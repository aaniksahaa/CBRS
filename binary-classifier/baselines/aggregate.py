"""Collect result JSONs (old + new) into one table; emit Markdown, CSV and LaTeX rows for Table 3.

    python -m baselines.aggregate                       # new results only -> markdown + paper/tables/baselines_rows.tex
    python -m baselines.aggregate --include-paper       # also the existing Table 3 result files, for side-by-side
    python -m baselines.aggregate --avg weighted
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NEW_DIR = REPO_ROOT / "results" / "classifier-results-baselines" / "evaluation_results"
PAPER_DIR = REPO_ROOT / "results" / "classifier-results-with-time" / "evaluation_results"
TABLES_DIR = REPO_ROOT / "paper" / "tables"

PRETTY_MODEL = {
    "csebuetnlp/banglabert": "BanglaBERT", "csebuetnlp/banglishbert": "BanglishBERT",
    "google-bert/bert-base-multilingual-cased": "mBERT", "bert-base-multilingual-cased": "mBERT",
    "FacebookAI/xlm-roberta-base": "XLM-R-Base", "xlm-roberta-base": "XLM-R-Base",
    "FacebookAI/xlm-roberta-large": "XLM-R-Large",
    "google/muril-base-cased": "MuRIL", "ai4bharat/indic-bert": "IndicBERT",
    "ai4bharat/IndicBERTv2-MLM-only": "IndicBERTv2",
    "distilbert/distilbert-base-multilingual-cased": "DistilBERT", "distilbert-base-multilingual-cased": "DistilBERT",
    "google/mobilebert-uncased": "MobileBERT",
    "sentence-transformers/all-MiniLM-L6-v2": "MiniLM6", "sentence-transformers/all-MiniLM-L12-v2": "MiniLM12",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": "ParaMiniLM",
    "sentence-transformers/distiluse-base-multilingual-cased-v2": "DistilUse",
    "intfloat/multilingual-e5-small": "E5-Small", "sentence-transformers/LaBSE": "LaBSE",
    "jinaai/jina-embeddings-v2-small-en": "JinaEmb", "BAAI/bge-small-en-v1.5": "BGE",
}
PRETTY_VEC = {"tfidf": "TFIDF", "count": "Count", "word2vec": "W2V", "char_tfidf": "CharTFIDF",
              "word_char_tfidf": "Word+CharTFIDF", "fasttext": "fastText"}
PRETTY_CLF = {"logistic": "LogReg", "svm": "SVM", "random_forest": "RF", "naive_bayes": "NB", "bert": "Fine-tuned",
              "fasttext": "fastText", "logistic-weighted": "LogReg (weighted)"}


def load_rows(dirs, avg: str):
    rows = []
    for d, origin in dirs:
        for p in sorted(Path(d).glob("*.json")):
            if p.name.startswith("_") or p.name.startswith("bnet_classifier_all"):
                continue
            try:
                r = json.loads(p.read_text())
            except Exception:
                continue
            if "metrics" not in r or "accuracy" not in r:
                continue
            m = r["metrics"].get(f"{avg} avg", {})
            emb = r.get("embedding_model") or "N/A"
            vec = r.get("vectorizer", "")
            clf = r.get("model", "")
            extra = r.get("extra", {})
            if vec in ("bert-end-to-end",):
                group = PRETTY_MODEL.get(emb, emb)
                clf_label = "Fine-tuned"
                kind = "finetune"
            elif vec == "huggingface":
                group = PRETTY_MODEL.get(emb, emb)
                clf_label = PRETTY_CLF.get(clf, clf)
                kind = "embed"
            elif vec == "fasttext":
                group = "fastText" + (" (char n-gram)" if extra.get("fasttext_params", {}).get("maxn", 0) else " (word)")
                clf_label = "fastText"
                kind = "fasttext"
            else:
                group = PRETTY_VEC.get(vec, vec)
                clf_label = PRETTY_CLF.get(clf, clf)
                kind = "lexical"
            per_lang = extra.get("per_language", {})
            rows.append({
                "origin": origin, "file": p.name, "kind": kind, "group": group, "classifier": clf_label,
                "embedding_model": emb, "vectorizer": vec, "model": clf,
                "accuracy": r["accuracy"], "precision": m.get("precision"), "recall": m.get("recall"),
                "f1": m.get("f1-score"), "time_e7": r.get("avg_inference_time_seconds", 0) * 1e7,
                "acc_bn": per_lang.get("bn", {}).get("accuracy"), "acc_en": per_lang.get("en", {}).get("accuracy"),
                "acc_tbn": per_lang.get("tbn", {}).get("accuracy"),
                "n_params": extra.get("n_params"), "train_s": extra.get("train_seconds") or extra.get("fit_seconds"),
                "single_latency": (extra.get("inference") or {}).get("single_sample_latency_seconds"),
                "baseline": extra.get("baseline"),
            })
    return rows


def fmt(x, nd=2):
    return "" if x is None else f"{x:.{nd}f}"


def latex_rows(rows) -> str:
    """Rows formatted like tab:DLF: Embedding & Classifier & Acc & P & R & F1 & time.  Groups via multirow."""
    out = []
    groups = {}
    for r in rows:
        groups.setdefault(r["group"], []).append(r)
    for g, rs in groups.items():
        n = len(rs)
        for i, r in enumerate(rs):
            first = f"\\multirow{{{n}}}{{*}}{{{g}}}" if (i == 0 and n > 1) else (g if i == 0 else "")
            clf = r["classifier"] if r["kind"] != "finetune" else g
            out.append(f"{first} & {clf} & {fmt(r['accuracy'])} & {fmt(r['precision'])} & {fmt(r['recall'])} & "
                       f"{fmt(r['f1'])} & {r['time_e7']:.2f}\\\\")
        out.append("\\midrule")
    return "\n".join(out) + "\n"


TABLE_HEAD = r"""\begin{table}[h]
\centering
\caption{Comparative performance of filtering methods (existing rows plus the additional Bengali / multilingual baselines).}
\label{tab:DLF-full}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{@{}lcccccccc@{}}
\toprule
\textbf{Embedding} & \textbf{Classifier} & \textbf{Accuracy} & \textbf{Precision} & \textbf{Recall} & \textbf{F1-Score} & \makecell[l]{\textbf{Inference}\\\textbf{Time x e-07}\\\textbf{(Seconds)}} \\
\midrule
"""
TABLE_TAIL = r"""\bottomrule
\end{tabular}%
}
\end{table}
"""


def full_table(rows) -> str:
    """A complete, drop-in table (old + new rows) — for when you'd rather regenerate tab:DLF than paste rows."""
    return TABLE_HEAD + latex_rows(rows) + TABLE_TAIL


def markdown(rows, per_lang: bool) -> str:
    hdr = "| Group | Classifier | Acc | P | R | F1 | time ×1e-7 s |"
    sep = "|---|---|---|---|---|---|---|"
    if per_lang:
        hdr += " bn | en | tbn | train s |"
        sep += "---|---|---|---|"
    lines = [hdr, sep]
    for r in rows:
        line = f"| {r['group']} | {r['classifier']} | {fmt(r['accuracy'],4)} | {fmt(r['precision'],4)} | {fmt(r['recall'],4)} | {fmt(r['f1'],4)} | {r['time_e7']:.2f} |"
        if per_lang:
            line += f" {fmt(r['acc_bn'],3)} | {fmt(r['acc_en'],3)} | {fmt(r['acc_tbn'],3)} | {fmt(r['train_s'],0)} |"
        lines.append(line)
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--new-dir", default=str(NEW_DIR))
    ap.add_argument("--paper-dir", default=str(PAPER_DIR))
    ap.add_argument("--include-paper", action="store_true", help="also load the existing Table 3 JSONs")
    ap.add_argument("--avg", choices=["macro", "weighted"], default="macro")
    ap.add_argument("--sort", choices=["file", "accuracy", "f1"], default="file")
    ap.add_argument("--tables-dir", default=str(TABLES_DIR))
    args = ap.parse_args(argv)

    dirs = [(args.new_dir, "new")]
    if args.include_paper:
        dirs.append((args.paper_dir, "paper"))
    rows = load_rows(dirs, args.avg)
    if not rows:
        print(f"no result JSONs found in {[d for d, _ in dirs]}")
        return 1
    if args.sort != "file":
        rows.sort(key=lambda r: -(r[args.sort] or 0))

    print(markdown(rows, per_lang=True))
    tdir = Path(args.tables_dir)
    tdir.mkdir(parents=True, exist_ok=True)
    new_rows = [r for r in rows if r["origin"] == "new"]
    (tdir / "baselines_rows.tex").write_text(
        "% AUTO-GENERATED by binary-classifier/baselines/aggregate.py -- extra baseline rows for tab:DLF\n"
        f"% metrics = {args.avg} avg precision/recall/F1 from classification_report(y_true, y_pred); time = s/sample x 1e7\n"
        + latex_rows(new_rows))
    if args.include_paper:
        (tdir / "baselines_table_full.tex").write_text(
            "% AUTO-GENERATED by binary-classifier/baselines/aggregate.py -- full table, old + new rows\n" + full_table(rows))
    with open(tdir / "baselines_all.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {tdir / 'baselines_rows.tex'} ({len(new_rows)} rows) and {tdir / 'baselines_all.csv'} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
