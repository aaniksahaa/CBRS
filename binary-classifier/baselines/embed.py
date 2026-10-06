"""Frozen HF encoder -> pooled embedding -> sklearn classifiers (Embedding x Classifier rows)."""
from __future__ import annotations

import gc
import hashlib
import logging
import time
from pathlib import Path

import numpy as np
import torch

from .data import Split
from .lexical import MODELS
from .metrics import Timer, build_result, env_info, positive_scores, save_predictions, save_result
from .registry import BaselineSpec
from .text_prep import prepare_texts

log = logging.getLogger(__name__)


def _shim_transformers_onnx():
    import sys, types
    try:
        import transformers.onnx  # noqa: F401
    except Exception:
        import transformers
        stub = types.ModuleType("transformers.onnx")
        stub.OnnxConfig = type("OnnxConfig", (), {})
        sys.modules["transformers.onnx"] = stub
        transformers.onnx = stub
    # helpers dropped from transformers.pytorch_utils in v5 but imported by old remote code (jina-bert)
    import transformers.pytorch_utils as pu
    if not hasattr(pu, "find_pruneable_heads_and_indices"):
        def find_pruneable_heads_and_indices(heads, n_heads, head_size, already_pruned_heads):
            mask = torch.ones(n_heads, head_size)
            heads = set(heads) - already_pruned_heads
            for head in heads:
                head = head - sum(1 if h < head else 0 for h in already_pruned_heads)
                mask[head] = 0
            mask = mask.view(-1).contiguous().eq(1)
            index = torch.arange(len(mask))[mask].long()
            return heads, index
        pu.find_pruneable_heads_and_indices = find_pruneable_heads_and_indices
    if not hasattr(pu, "apply_chunking_to_forward"):
        def apply_chunking_to_forward(forward_fn, chunk_size, chunk_dim, *input_tensors):
            if chunk_size > 0:
                chunks = [t.chunk(t.shape[chunk_dim] // chunk_size, dim=chunk_dim) for t in input_tensors]
                return torch.cat([forward_fn(*c) for c in zip(*chunks)], dim=chunk_dim)
            return forward_fn(*input_tensors)
        pu.apply_chunking_to_forward = apply_chunking_to_forward


@torch.no_grad()
def encode(model, tokenizer, texts: list[str], *, pooling: str, max_length: int, batch_size: int, device,
           normalize: bool = True, desc: str = "") -> tuple[np.ndarray, float]:
    """Returns (embeddings [n, d], wall seconds).  Length-sorted batching for speed."""
    from tqdm import tqdm
    model.eval()
    order = np.argsort([len(t) for t in texts])
    out = np.zeros((len(texts), model.config.hidden_size), dtype=np.float32)
    t0 = time.perf_counter()
    for i in tqdm(range(0, len(texts), batch_size), desc=desc or "encode", leave=False):
        idx = order[i:i + batch_size]
        enc = tokenizer([texts[j] for j in idx], padding=True, truncation=True, max_length=max_length,
                        return_tensors="pt").to(device)
        h = model(**enc).last_hidden_state
        if pooling == "cls":
            v = h[:, 0]
        else:
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            v = (h * m).sum(1) / m.sum(1).clamp(min=1e-6)
        if normalize:
            v = torch.nn.functional.normalize(v, dim=-1)
        out[idx] = v.float().cpu().numpy()
    if device.type == "cuda":
        torch.cuda.synchronize()
    return out, time.perf_counter() - t0


def run_embed(spec: BaselineSpec, split: Split, out_dir: Path, cache_dir: Path, *, device: str = "auto",
              classifiers: tuple[str, ...] | None = None, force: bool = False, overrides: dict | None = None) -> dict:
    from transformers import AutoModel, AutoTokenizer

    ov = overrides or {}
    max_length = ov.get("max_length", spec.max_length)
    dev = torch.device("cuda" if device == "auto" and torch.cuda.is_available() else ("cpu" if device == "auto" else device))
    clfs = classifiers or spec.classifiers

    tr_texts, normalised = prepare_texts(split.train["text"], spec.normalize_bangla)
    te_texts, _ = prepare_texts(split.test["text"], spec.normalize_bangla)

    fp = hashlib.md5(f"{spec.model_id}|{spec.pooling}|{max_length}|{len(tr_texts)}|{len(te_texts)}|{split.data_path}|st={spec.sentence_transformer}".encode()).hexdigest()[:10]
    emb_cache = cache_dir / "embeddings" / f"{spec.name}_{fp}.npz"
    if emb_cache.exists() and not force:
        z = np.load(emb_cache)
        X_tr, X_te, enc_secs = z["X_tr"], z["X_te"], float(z["enc_secs"])
        log.info("loaded cached embeddings %s", emb_cache)
    elif spec.sentence_transformer:
        _shim_transformers_onnx()  # jinaai remote code imports transformers.onnx (removed in transformers 5)
        from sentence_transformers import SentenceTransformer
        log.info("loading %s (sentence-transformers)", spec.model_id)
        st = SentenceTransformer(spec.model_id, device=str(dev), trust_remote_code=True)
        st.max_seq_length = min(st.max_seq_length or max_length, max_length)
        t0 = time.perf_counter()
        X_tr = st.encode(tr_texts, batch_size=spec.eval_batch_size, normalize_embeddings=True, show_progress_bar=True)
        t0 = time.perf_counter()
        X_te = st.encode(te_texts, batch_size=spec.eval_batch_size, normalize_embeddings=True, show_progress_bar=True)
        enc_secs = time.perf_counter() - t0
        emb_cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez(emb_cache, X_tr=X_tr, X_te=X_te, enc_secs=enc_secs)
        del st
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    else:
        log.info("loading %s", spec.model_id)
        tokenizer = AutoTokenizer.from_pretrained(spec.model_id)
        model = AutoModel.from_pretrained(spec.model_id, torch_dtype=torch.float16 if dev.type == "cuda" else torch.float32).to(dev)
        X_tr, _ = encode(model, tokenizer, tr_texts, pooling=spec.pooling, max_length=max_length,
                         batch_size=spec.eval_batch_size, device=dev, desc=f"{spec.name} train")
        X_te, enc_secs = encode(model, tokenizer, te_texts, pooling=spec.pooling, max_length=max_length,
                                batch_size=spec.eval_batch_size, device=dev, desc=f"{spec.name} test")
        emb_cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez(emb_cache, X_tr=X_tr, X_te=X_te, enc_secs=enc_secs)
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    y_tr = split.train["label"].to_numpy()
    y_te = split.test["label"].to_numpy()
    results = {}
    for clf_name in clfs:
        if clf_name == "naive_bayes":
            log.warning("skipping naive_bayes on dense embeddings (MultinomialNB needs non-negative features)")
            continue
        key = f"{spec.result_key}_{clf_name}"
        clf = MODELS[clf_name]()
        with Timer() as t_fit:
            clf.fit(X_tr, y_tr)
        t0 = time.perf_counter()
        y_pred = clf.predict(X_te)
        infer = time.perf_counter() - t0
        save_predictions(out_dir, key, y_true=y_te, y_pred=y_pred, scores=positive_scores(clf, X_te),
                         languages=split.test["language"].to_numpy())
        result = build_result(
            vectorizer="huggingface", model=clf_name, embedding_model=spec.model_id,
            y_true=y_te, y_pred=y_pred, avg_inference_time_seconds=infer / len(y_te),
            languages=split.test["language"].to_numpy(),
            extra={"baseline": spec.name, "description": spec.description, "kind": "embed",
                   "pooling": "sentence-transformers" if spec.sentence_transformer else spec.pooling,
                   "max_length": max_length, "normalised_embeddings": True,
                   "bangla_normalised": normalised, "fit_seconds": t_fit.elapsed,
                   "encode_test_seconds_total": enc_secs, "encode_seconds_per_sample": enc_secs / len(y_te),
                   "note": "avg_inference_time_seconds = classifier predict only (as in Table 3); "
                           "encoder cost is in encode_seconds_per_sample",
                   "env": env_info(), "data": split.data_path, "matches_paper_split": split.matches_paper_split})
        path = save_result(result, out_dir, key)
        log.info("saved %s  acc=%.4f macroF1=%.4f", path, result["accuracy"], result["extra"]["macro_f1"])
        results[key] = result
    return results
