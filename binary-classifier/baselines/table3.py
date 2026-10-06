"""Final Table 3 (tab:DLF) on the corrected test labels, with significance markers vs DLF.

    cd binary-classifier && python -m baselines.table3            # -> paper/tables/tab_DLF_final.tex (+ _original_labels)

Metrics are macro averages (precision, recall, F1) and accuracy, three decimals. Significance is in a separate table
(baselines/sigtable.py). Inference time is reported separately (tab:latency) because the old
time column mixed classifier-only and end-to-end timings.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RES = REPO / "results/classifier-results-baselines/evaluation_results"
T = REPO / "paper/tables"
DLF_KEY = "dlf_full_l1w12_fasttext_char_gpt-4o-mini"

GROUPS = [  # (group label, [(json path relative to RES, classifier label)])
    ("TF-IDF", [(f"paper-repro/tfidf_{c}", n) for c, n in [("logistic", "LogReg"), ("svm", "SVM"), ("random_forest", "RF"), ("naive_bayes", "NB")]]),
    ("Count", [(f"paper-repro/count_{c}", n) for c, n in [("logistic", "LogReg"), ("svm", "SVM"), ("random_forest", "RF"), ("naive_bayes", "NB")]]),
    ("Char TF-IDF", [(f"char_tfidf_{c}", n) for c, n in [("logistic", "LogReg"), ("svm", "SVM"), ("random_forest", "RF"), ("naive_bayes", "NB")]]),
    ("Word+Char TF-IDF", [(f"word_char_tfidf_{c}", n) for c, n in [("logistic", "LogReg"), ("svm", "SVM"), ("random_forest", "RF"), ("naive_bayes", "NB")]]),
    ("fastText", [("fasttext_char", "char $n$-grams"), ("fasttext_word", "words")]),
] + [
    (name, [(f"paper-repro/huggingface_{mid.replace('/', '_')}_{c}", n) for c, n in [("logistic", "LogReg"), ("svm", "SVM"), ("random_forest", "RF")]])
    for name, mid in [("MiniLM6", "sentence-transformers/all-MiniLM-L6-v2"), ("MiniLM12", "sentence-transformers/all-MiniLM-L12-v2"),
                      ("ParaMiniLM", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
                      ("DistilUse", "sentence-transformers/distiluse-base-multilingual-cased-v2"),
                      ("E5-Small", "intfloat/multilingual-e5-small"), ("LaBSE", "sentence-transformers/LaBSE"),
                      ("BGE", "BAAI/bge-small-en-v1.5")]
] + [
    ("Fine-tuned", [("finetune_csebuetnlp_banglabert_bert", "BanglaBERT"), ("finetune_google-bert_bert-base-multilingual-cased_bert", "mBERT"),
                    ("finetune_FacebookAI_xlm-roberta-base_bert", "XLM-R"), ("finetune_google_muril-base-cased_bert", "MuRIL"),
                    ("finetune_ai4bharat_indic-bert_bert", "IndicBERT"), ("finetune_ai4bharat_IndicBERTv2-MLM-only_bert", "IndicBERTv2"),
                    ("finetune_distilbert_distilbert-base-multilingual-cased_bert", "DistilBERT"),
                    ("paper-repro/finetune_google_mobilebert-uncased_bert", "MobileBERT")]),
]


def row_metrics(r: dict, original: bool):
    if original:
        o = r["extra"]["metrics_original_labels"]
        acc, m = o["accuracy"], o["metrics"]
    else:
        acc, m = r["accuracy"], r["metrics"]
    ma = m["macro avg"]
    return acc, ma["precision"], ma["recall"], ma["f1-score"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--original-labels", action="store_true")
    args = ap.parse_args(argv)
    suf = "_original_labels" if args.original_labels else ""
    dlf = json.loads((RES / "paper-repro" / f"{DLF_KEY}.json").read_text())
    rows, best = [], 0.0
    for g, items in GROUPS:
        for path, lab in items:
            f = RES / f"{path}.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            rows.append((g, lab, *row_metrics(r, args.original_labels)))
    d = row_metrics(dlf, args.original_labels)
    fmt = lambda x: f"{x:.3f}"
    lines = [r"\begin{table}[h]", r"\centering",
             r"\caption{Comparative performance of filtering methods on the 5{,}166-message test split. "
             r"Macro-averaged precision, recall and F1. DLF = fastText Layer~1 ($\alpha=12$) + gpt-4o-mini Layer~2. "
             r"Pairwise significance tests in Table~\ref{tab:significance}; inference latency in Table~\ref{tab:latency}.}",
             r"\label{tab:DLF" + ("-original-labels" if args.original_labels else "") + "}",
             r"\resizebox{\columnwidth}{!}{%", r"\begin{tabular}{@{}llcccc@{}}", r"\toprule",
             r"\textbf{Embedding} & \textbf{Classifier} & \textbf{Accuracy} & \textbf{Precision} & \textbf{Recall} & \textbf{F1-Score} \\",
             r"\midrule"]
    groups = {}
    for g, *rest in rows:
        groups.setdefault(g, []).append(rest)
    for g, rs in groups.items():
        for i, (lab, acc, p, rc, f1) in enumerate(rs):
            first = (rf"\multirow{{{len(rs)}}}{{*}}{{{g}}}" if len(rs) > 1 else g) if i == 0 else ""
            lines.append(f"{first} & {lab} & {fmt(acc)} & {fmt(p)} & {fmt(rc)} & {fmt(f1)} \\\\")
        lines.append(r"\midrule")
    lines.append(rf"\textbf{{DLF}} & \textbf{{fastText + gpt-4o-mini}} & \textbf{{{fmt(d[0])}}} & \textbf{{{fmt(d[1])}}} & "
                 rf"\textbf{{{fmt(d[2])}}} & \textbf{{{fmt(d[3])}}} \\")
    lines += [r"\bottomrule", r"\end{tabular}%", "}", r"\end{table}"]
    out = T / f"tab_DLF_final{suf}.tex"
    out.write_text("% AUTO-GENERATED by binary-classifier/baselines/table3.py\n" + "\n".join(lines) + "\n")
    allf1 = sorted([(r[5], r[1]) for r in rows] + [(d[3], "DLF")], reverse=True)
    print(f"wrote {out} ({len(rows)} rows + DLF); top macro-F1: " + ", ".join(f"{n} {v:.4f}" for v, n in allf1[:5]))


if __name__ == "__main__":
    main()
