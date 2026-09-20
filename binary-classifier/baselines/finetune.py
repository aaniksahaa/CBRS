"""End-to-end fine-tuning of a Hugging Face encoder for binary blood-request detection."""
from __future__ import annotations

import gc
import logging
import shutil
import time
from pathlib import Path

import numpy as np
import torch

from .data import Split
from .metrics import Timer, build_result, env_info, save_result
from .registry import BaselineSpec
from .text_prep import prepare_texts

log = logging.getLogger(__name__)


def _pick_precision(pref: str) -> tuple[bool, bool]:
    """returns (fp16, bf16)"""
    if not torch.cuda.is_available() or pref == "fp32":
        return False, False
    if pref == "fp16":
        return True, False
    if pref == "bf16":
        return False, True
    # auto: bf16 is numerically safer when the GPU supports it (Ampere+)
    if torch.cuda.is_bf16_supported():
        return False, True
    return True, False


@torch.no_grad()
def _predict(model, tokenizer, texts: list[str], max_length: int, batch_size: int, device) -> tuple[np.ndarray, float]:
    """Batched prediction; returns (labels, wall seconds incl. tokenisation)."""
    model.eval()
    preds = []
    t0 = time.perf_counter()
    for i in range(0, len(texts), batch_size):
        enc = tokenizer(texts[i:i + batch_size], padding=True, truncation=True, max_length=max_length,
                        return_tensors="pt").to(device)
        logits = model(**enc).logits
        preds.append(logits.argmax(-1).cpu())
    if device.type == "cuda":
        torch.cuda.synchronize()
    return torch.cat(preds).numpy(), time.perf_counter() - t0


@torch.no_grad()
def _single_sample_latency(model, tokenizer, texts: list[str], max_length: int, device, n: int = 100) -> float:
    model.eval()
    texts = texts[:n]
    for t in texts[:5]:  # warm-up
        model(**tokenizer(t, truncation=True, max_length=max_length, return_tensors="pt").to(device))
    t0 = time.perf_counter()
    for t in texts:
        model(**tokenizer(t, truncation=True, max_length=max_length, return_tensors="pt").to(device))
    if device.type == "cuda":
        torch.cuda.synchronize()
    return (time.perf_counter() - t0) / len(texts)


def run_finetune(spec: BaselineSpec, split: Split, out_dir: Path, cache_dir: Path, *,
                 device: str = "auto", keep_checkpoints: bool = False, save_model: Path | None = None,
                 seed: int = 42, overrides: dict | None = None) -> dict:
    from datasets import Dataset
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding,
                              Trainer, TrainingArguments, set_seed)

    ov = overrides or {}
    epochs = ov.get("epochs", spec.epochs)
    bs = ov.get("batch_size", spec.batch_size)
    max_length = ov.get("max_length", spec.max_length)
    lr = ov.get("lr", spec.lr)
    grad_accum = ov.get("grad_accum", spec.grad_accum)
    precision = ov.get("precision", spec.precision)

    set_seed(seed)
    dev = torch.device("cuda" if device == "auto" and torch.cuda.is_available() else ("cpu" if device == "auto" else device))
    fp16, bf16 = _pick_precision(precision) if dev.type == "cuda" else (False, False)

    assert split.val is not None, "finetune needs a validation split (val_fraction > 0)"
    tr_texts, normalised = prepare_texts(split.train["text"], spec.normalize_bangla)
    va_texts, _ = prepare_texts(split.val["text"], spec.normalize_bangla)
    te_texts, _ = prepare_texts(split.test["text"], spec.normalize_bangla)

    log.info("loading %s", spec.model_id)
    tokenizer = AutoTokenizer.from_pretrained(spec.model_id)
    model = AutoModelForSequenceClassification.from_pretrained(spec.model_id, num_labels=2)
    n_params = sum(p.numel() for p in model.parameters())
    freeze_mode = ov.get("freeze_embeddings", spec.freeze_embeddings)
    low_vram = dev.type == "cuda" and torch.cuda.get_device_properties(dev).total_memory < 10 * 2**30
    froze = freeze_mode == "always" or (freeze_mode == "low_vram" and low_vram)
    n_frozen = 0
    if froze:
        emb = model.get_input_embeddings()
        emb.weight.requires_grad_(False)
        n_frozen = emb.weight.numel()
        log.warning("freezing word-embedding matrix (%d of %d params) to fit the GPU; mode=%s",
                    n_frozen, n_params, freeze_mode)
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)

    def tok(batch):
        return tokenizer(batch["text"], truncation=True, max_length=max_length)

    ds_tr = Dataset.from_dict({"text": tr_texts, "label": split.train["label"].tolist()}).map(tok, batched=True, remove_columns=["text"])
    ds_va = Dataset.from_dict({"text": va_texts, "label": split.val["label"].tolist()}).map(tok, batched=True, remove_columns=["text"])

    ckpt_dir = cache_dir / "checkpoints" / spec.name
    if ckpt_dir.exists():
        shutil.rmtree(ckpt_dir)

    def compute_metrics(p):
        from sklearn.metrics import f1_score
        y = np.argmax(p.predictions, -1)
        return {"f1": f1_score(p.label_ids, y, average="macro"), "accuracy": float((y == p.label_ids).mean())}

    import math
    steps_per_epoch = math.ceil(len(ds_tr) / (bs * grad_accum))
    warmup_steps = int(spec.warmup_ratio * steps_per_epoch * epochs)  # warmup_ratio is deprecated in transformers 5.2
    args = TrainingArguments(
        output_dir=str(ckpt_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=bs,
        per_device_eval_batch_size=spec.eval_batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=lr,
        weight_decay=spec.weight_decay,
        warmup_steps=warmup_steps,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=50,
        fp16=fp16, bf16=bf16,
        seed=seed,
        report_to="none",
        dataloader_num_workers=2,
        use_cpu=(dev.type == "cpu"),
    )
    trainer = Trainer(model=model, args=args, train_dataset=ds_tr, eval_dataset=ds_va,
                      data_collator=DataCollatorWithPadding(tokenizer), processing_class=tokenizer,
                      compute_metrics=compute_metrics)
    log.info("training %s: epochs=%s bs=%s accum=%s lr=%s max_len=%s fp16=%s bf16=%s device=%s",
             spec.name, epochs, bs, grad_accum, lr, max_length, fp16, bf16, dev)
    with Timer() as t_train:
        train_out = trainer.train()
    val_metrics = trainer.evaluate()
    log.info("best-epoch val metrics: %s", {k: v for k, v in val_metrics.items() if "f1" in k or "acc" in k})

    model = trainer.model.to(dev)
    y_pred, infer_secs = _predict(model, tokenizer, te_texts, max_length, spec.eval_batch_size, dev)
    y_true = split.test["label"].to_numpy()
    single = _single_sample_latency(model, tokenizer, te_texts, max_length, dev)

    result = build_result(
        vectorizer="bert-end-to-end", model="bert", embedding_model=spec.model_id,
        y_true=y_true, y_pred=y_pred, avg_inference_time_seconds=infer_secs / len(y_true),
        languages=split.test["language"].to_numpy(),
        extra={
            "baseline": spec.name, "description": spec.description, "kind": "finetune",
            "n_params": int(n_params), "n_trainable_params": int(n_trainable),
            "embeddings_frozen": bool(froze), "n_frozen_params": int(n_frozen), "train_seconds": t_train.elapsed, "train_loss": float(train_out.training_loss),
            "val_macro_f1_best": float(val_metrics.get("eval_f1", float("nan"))),
            "hparams": {"epochs": epochs, "batch_size": bs, "grad_accum": grad_accum, "lr": lr,
                        "max_length": max_length, "weight_decay": spec.weight_decay,
                        "warmup_ratio": spec.warmup_ratio, "val_fraction": spec.val_fraction,
                        "fp16": fp16, "bf16": bf16, "seed": seed, "freeze_embeddings": freeze_mode},
            "bangla_normalised": normalised,
            "inference": {"batch_size": spec.eval_batch_size, "device": str(dev),
                          "single_sample_latency_seconds": single, "total_test_seconds": infer_secs},
            "env": env_info(), "data": split.data_path, "matches_paper_split": split.matches_paper_split,
        })
    path = save_result(result, out_dir, spec.result_key)
    log.info("saved %s  acc=%.4f macroF1=%.4f  infer=%.2e s/sample", path, result["accuracy"],
             result["extra"]["macro_f1"], result["avg_inference_time_seconds"])

    if save_model:
        save_model = Path(save_model) / spec.name
        trainer.save_model(str(save_model))
        tokenizer.save_pretrained(str(save_model))
        log.info("model saved to %s", save_model)
    if not keep_checkpoints and ckpt_dir.exists():
        shutil.rmtree(ckpt_dir, ignore_errors=True)
    del trainer, model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return result
