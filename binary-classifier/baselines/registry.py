"""Baseline registry.  ADD A NEW BASELINE = ADD ONE ENTRY HERE.

kind:
  "finetune"  - end-to-end fine-tuning of a HF encoder + classification head (GPU).
  "embed"     - frozen HF encoder -> pooled sentence vector -> sklearn classifiers
                (mirrors the Embedding x Classifier rows of Table 3).
  "lexical"   - sklearn vectorizer (e.g. char n-gram TF-IDF) x sklearn classifiers (CPU).
  "fasttext"  - fastText supervised classifier with (sub)word n-grams (CPU).

`tags` are used by `run.py --tags ...` to select groups.  Rough VRAM/time notes
are for max_length=128 on a 6 GB RTX 3050 (this host); scale accordingly.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BaselineSpec:
    name: str
    kind: str
    description: str
    model_id: str | None = None           # HF hub id (finetune / embed)
    tags: tuple[str, ...] = ()
    # --- fine-tuning hyper-parameters (kind == "finetune")
    max_length: int = 128                 # 75% of messages are < 195 chars; 128 tokens is plenty
    batch_size: int = 32
    eval_batch_size: int = 64
    lr: float = 2e-5
    epochs: int = 3
    weight_decay: float = 0.01
    warmup_ratio: float = 0.06
    val_fraction: float = 0.1             # carved from TRAIN, used for best-epoch selection
    precision: str = "auto"               # auto|fp32|fp16|bf16
    grad_accum: int = 1
    normalize_bangla: bool = False        # apply csebuetnlp `normalizer` (BanglaBERT authors' recommendation)
    freeze_embeddings: str = "never"      # never | low_vram | always : freeze the word-embedding matrix
                                          # (large-vocab models: fp32 AdamW states for a 250k x 768 matrix alone
                                          #  need ~2.3 GB; "low_vram" freezes only when the GPU has < 10 GB)
    # --- frozen-embedding options (kind == "embed")
    pooling: str = "mean"                 # mean | cls
    classifiers: tuple[str, ...] = ("logistic", "svm", "random_forest")
    # --- lexical options (kind == "lexical")
    vectorizer: str | None = None         # key into lexical.VECTORIZERS
    # --- fastText options (kind == "fasttext")
    fasttext_params: dict = field(default_factory=dict)
    notes: str = ""

    @property
    def result_key(self) -> str:
        """File stem of the JSON written for this baseline (embed/lexical add _<classifier>)."""
        if self.kind == "finetune":
            return f"finetune_{self.model_id}_bert".replace("/", "_")
        if self.kind == "embed":
            return f"huggingface_{self.model_id}".replace("/", "_")
        if self.kind == "lexical":
            return f"{self.vectorizer}"
        if self.kind == "fasttext":
            return self.name
        raise ValueError(self.kind)


_B: list[BaselineSpec] = [
    # ------------------------------------------------------------------ fine-tuned encoders
    BaselineSpec("banglabert_ft", "finetune",
                 "BanglaBERT (ELECTRA-base discriminator pre-trained on Bangla; Bhattacharjee et al. 2022)",
                 model_id="csebuetnlp/banglabert", tags=("ft", "core", "bengali"),
                 normalize_bangla=True,
                 notes="~110M params. Authors recommend their `normalizer` package before tokenizing."),
    BaselineSpec("mbert_ft", "finetune",
                 "Multilingual BERT base cased (Devlin et al. 2019)",
                 model_id="google-bert/bert-base-multilingual-cased", tags=("ft", "core"),
                 notes="~178M params."),
    BaselineSpec("xlmr_base_ft", "finetune",
                 "XLM-RoBERTa base (Conneau et al. 2020)",
                 model_id="FacebookAI/xlm-roberta-base", tags=("ft", "core"),
                 batch_size=16, grad_accum=2, freeze_embeddings="low_vram",
                 notes="~278M params, 192M of them in the 250k-vocab embedding matrix -> frozen on < 10 GB GPUs."),
    BaselineSpec("muril_ft", "finetune",
                 "MuRIL base cased (Khanuja et al. 2021) - Indian languages incl. Bengali + transliteration",
                 model_id="google/muril-base-cased", tags=("ft", "core", "bengali"),
                 batch_size=16, grad_accum=2, freeze_embeddings="low_vram",
                 notes="~237M params. Pre-trained on transliterated data too, relevant for tbn."),
    BaselineSpec("indicbertv2_ft", "finetune",
                 "IndicBERT v2 (MLM-only, AI4Bharat; Doddapaneni et al. 2023)",
                 model_id="ai4bharat/IndicBERTv2-MLM-only", tags=("ft", "core"),
                 batch_size=16, grad_accum=2, freeze_embeddings="low_vram",
                 notes="~278M params (250k vocab, frozen on < 10 GB GPUs). Open repo (v1 is gated)."),
    BaselineSpec("indicbert_ft", "finetune",
                 "IndicBERT v1 (ALBERT, AI4Bharat; Kakwani et al. 2020)",
                 model_id="ai4bharat/indic-bert", tags=("ft", "gated"),
                 lr=3e-5,
                 notes="~33M params (ALBERT). GATED repo: request access on the HF page, then `hf auth login`."),
    # optional extras (not required by the reviewer, but cheap and relevant)
    BaselineSpec("banglishbert_ft", "finetune",
                 "BanglishBERT (ELECTRA pre-trained on Bangla + English + code-mixed; csebuetnlp)",
                 model_id="csebuetnlp/banglishbert", tags=("ft", "extra", "bengali"),
                 normalize_bangla=True),
    BaselineSpec("xlmr_large_ft", "finetune",
                 "XLM-RoBERTa large", model_id="FacebookAI/xlm-roberta-large", tags=("ft", "large"),
                 batch_size=8, grad_accum=4, lr=1e-5, freeze_embeddings="low_vram",
                 notes="~560M params - needs >= 12 GB VRAM even with frozen embeddings; skip on the 6 GB laptop GPU."),
    BaselineSpec("distilbert_multilingual_ft", "finetune",
                 "DistilBERT multilingual cased - sanity re-run of an existing Table 3 row",
                 model_id="distilbert/distilbert-base-multilingual-cased", tags=("ft", "sanity"),
                 notes="Paper row: acc 0.985. Use to check the harness reproduces existing numbers."),
    # ------------------------------------------------------------------ frozen encoders x sklearn
    BaselineSpec("banglabert_emb", "embed", "BanglaBERT frozen mean-pooled embeddings",
                 model_id="csebuetnlp/banglabert", tags=("emb", "core", "bengali"), normalize_bangla=True),
    BaselineSpec("mbert_emb", "embed", "mBERT frozen mean-pooled embeddings",
                 model_id="google-bert/bert-base-multilingual-cased", tags=("emb", "core")),
    BaselineSpec("xlmr_base_emb", "embed", "XLM-R base frozen mean-pooled embeddings",
                 model_id="FacebookAI/xlm-roberta-base", tags=("emb", "core")),
    BaselineSpec("muril_emb", "embed", "MuRIL frozen mean-pooled embeddings",
                 model_id="google/muril-base-cased", tags=("emb", "core", "bengali")),
    BaselineSpec("indicbertv2_emb", "embed", "IndicBERT v2 frozen mean-pooled embeddings",
                 model_id="ai4bharat/IndicBERTv2-MLM-only", tags=("emb", "core")),
    BaselineSpec("indicbert_emb", "embed", "IndicBERT v1 frozen mean-pooled embeddings (gated repo)",
                 model_id="ai4bharat/indic-bert", tags=("emb", "gated")),
    # ------------------------------------------------------------------ lexical / fastText (CPU)
    BaselineSpec("char_tfidf", "lexical",
                 "Character n-gram (2-5, char_wb) TF-IDF x {LogReg, SVM, RF, NB}",
                 vectorizer="char_tfidf", tags=("lex", "core"),
                 classifiers=("logistic", "svm", "random_forest", "naive_bayes")),
    BaselineSpec("word_char_tfidf", "lexical",
                 "Word (1-2) + character (2-5) TF-IDF union x {LogReg, SVM, RF, NB}",
                 vectorizer="word_char_tfidf", tags=("lex", "extra"),
                 classifiers=("logistic", "svm", "random_forest", "naive_bayes")),
    BaselineSpec("fasttext_char", "fasttext",
                 "fastText supervised with character n-grams (minn=2, maxn=5) + word bigrams",
                 tags=("fasttext", "core"),
                 fasttext_params=dict(dim=100, epoch=25, lr=1.0, wordNgrams=2, minn=2, maxn=5, minCount=1)),
    BaselineSpec("fasttext_word", "fasttext",
                 "fastText supervised, word-level only (maxn=0) - ablation for the char n-gram effect",
                 tags=("fasttext", "extra"),
                 fasttext_params=dict(dim=100, epoch=25, lr=1.0, wordNgrams=2, minn=0, maxn=0, minCount=1)),
]

BASELINES: dict[str, BaselineSpec] = {b.name: b for b in _B}


def select(names: list[str] | None = None, tags: list[str] | None = None, all_: bool = False) -> list[BaselineSpec]:
    if all_:
        return list(_B)
    chosen: list[BaselineSpec] = []
    for b in _B:
        if names and b.name in names:
            chosen.append(b)
        elif tags and any(t in b.tags for t in tags):
            chosen.append(b)
    unknown = set(names or []) - set(BASELINES)
    if unknown:
        raise SystemExit(f"Unknown baseline(s): {sorted(unknown)}. Use --list.")
    return chosen
