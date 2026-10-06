"""End-to-end inference latency of every Table-3 configuration (+ DLF), paper-ready.

Protocol (identical for all rows): raw message text -> predicted label, on one machine.
  * Latency    : median wall time to classify ONE message, over the first N test messages (after warm-up).
  * Throughput : messages per second when all 5,166 test messages are classified in one call (batch 64 for neural models).
  * Devices    : lexical / fastText models on ONE CPU thread; neural encoders (sentence embeddings, fine-tuned models)
                 on the GPU (their CPU numbers for BanglaBERT/DistilBERT are in latency_benchmark.csv).
Models are trained exactly as for Table 3 (sentence-embedding classifiers are refit on the cached training
embeddings; fine-tuned models are loaded from disk). Training time is never included.

    cd binary-classifier && python -u -m baselines.latency_table3        # ~30 min; -> paper/tables/latency_table3.csv
    python -m baselines.latency_table3 --table-only                       # rebuild tab_latency.tex from the CSV
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import platform
import statistics
import time
from pathlib import Path

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .data import load_split
from .table3 import GROUPS

REPO = Path(__file__).resolve().parents[2]
T = REPO / "paper" / "tables"
CACHE = Path(os.environ.get("CBRS_BASELINE_CACHE", Path.home() / ".cache" / "cbrs-baselines"))
OUT_CSV = T / "latency_table3.csv"
LLM_DIR = REPO / "results/classifier-results-baselines/evaluation_results/paper-repro/dlf_layer2"

SENT = {"MiniLM6": ("sentence-transformers/all-MiniLM-L6-v2", "paper_minilm6"),
        "MiniLM12": ("sentence-transformers/all-MiniLM-L12-v2", "paper_minilm12"),
        "ParaMiniLM": ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "paper_paraminilm"),
        "DistilUse": ("sentence-transformers/distiluse-base-multilingual-cased-v2", "paper_distiluse"),
        "E5-Small": ("intfloat/multilingual-e5-small", "paper_e5small"),
        "LaBSE": ("sentence-transformers/LaBSE", "paper_labse"),
        "BGE": ("BAAI/bge-small-en-v1.5", "paper_bge")}
FT = {"BanglaBERT": "banglabert_ft", "mBERT": "mbert_ft", "XLM-R": "xlmr_base_ft", "MuRIL": "muril_ft",
      "IndicBERT": "indicbert_ft", "IndicBERTv2": "indicbertv2_ft", "DistilBERT": "distilbert_multilingual_ft",
      "MobileBERT": "paper_mobilebert_ft"}
CLF_OF = {"LogReg": "logistic", "SVM": "svm", "RF": "random_forest", "NB": "naive_bayes"}


def clf_factory(name):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.svm import SVC
    return {"logistic": lambda: LogisticRegression(C=1.0, max_iter=10000),
            "svm": lambda: SVC(kernel="linear"),  # probability calibration only affects training time
            "random_forest": lambda: RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            "naive_bayes": lambda: MultinomialNB()}[name]()


def bench(one, many, texts, n_single):
    for t in texts[:20]:
        one(t)
    lat = []
    for t in texts[:n_single]:
        t0 = time.perf_counter()
        one(t)
        lat.append(time.perf_counter() - t0)
    t0 = time.perf_counter()
    many(texts)
    total = time.perf_counter() - t0
    return {"latency_ms": statistics.median(lat) * 1e3, "latency_p95_ms": float(np.percentile(lat, 95)) * 1e3,
            "throughput_msg_s": len(texts) / total}


def vectorizer(family):
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.pipeline import FeatureUnion
    word = lambda: TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    char = lambda: TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=200_000, sublinear_tf=True, min_df=2)
    return {"TF-IDF": word, "Count": lambda: CountVectorizer(max_features=5000, ngram_range=(1, 2)), "Char TF-IDF": char,
            "Word+Char TF-IDF": lambda: FeatureUnion([("w", word()), ("c", char())])}[family]()


def fasttext_model(split, char: bool, pos_weight: int = 1):
    import fasttext
    work = CACHE / "latency"
    work.mkdir(parents=True, exist_ok=True)
    f = work / f"ft_{'char' if char else 'word'}_w{pos_weight}.txt"
    clean = lambda t: " ".join(str(t).split())
    lines = []
    for t, l in zip(split.train["text"], split.train["label"]):
        lines += [f"__label__{int(l)} {clean(t)}"] * (pos_weight if l == 1 else 1)
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    m = fasttext.train_supervised(input=str(f), dim=100, epoch=25, lr=1.0, wordNgrams=2, minCount=1, thread=1, seed=42,
                                  verbose=0, **({"minn": 2, "maxn": 5} if char else {"minn": 0, "maxn": 0}))
    return (lambda t: m.predict([clean(t)])), (lambda ts: m.predict([clean(t) for t in ts]))


def run(n_single: int):
    import torch
    split = load_split()
    Xtr, ytr = split.train["text"].tolist(), split.train["label"].to_numpy()
    texts = split.test["text"].tolist()
    rows = []
    done = set()
    if OUT_CSV.exists():  # resumable
        prev = pd.read_csv(OUT_CSV)
        rows = prev.to_dict("records")
        done = set(zip(prev.group, prev.classifier))

    def add(group, clf, device, res, note=""):
        rows.append({"group": group, "classifier": clf, "device": device, **res, "note": note})
        pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
        print(f"{group:18s} {clf:24s} {device:4s} latency {res['latency_ms']:9.3f} ms  throughput {res['throughput_msg_s']:10.1f} msg/s", flush=True)

    gpu = torch.cuda.is_available()
    for g, items in GROUPS:
        labels = [lab for _, lab in items]
        if g in ("TF-IDF", "Count", "Char TF-IDF", "Word+Char TF-IDF"):
            if all((g, l) in done for l in labels):
                continue
            with threadpool_limits(1):
                vec = vectorizer(g)
                Ztr = vec.fit_transform(Xtr)
                for lab in labels:
                    if (g, lab) in done:
                        continue
                    clf = clf_factory(CLF_OF[lab]).fit(Ztr, ytr)
                    if hasattr(clf, "n_jobs"):
                        clf.n_jobs = 1
                    add(g, lab, "CPU", bench(lambda t: clf.predict(vec.transform([t])), lambda ts: clf.predict(vec.transform(ts)),
                                             texts, n_single if lab != "SVM" else min(n_single, 200)))
        elif g == "fastText":
            with threadpool_limits(1):
                for lab, char in (("char $n$-grams", True), ("words", False)):
                    if (g, lab) not in done:
                        one, many = fasttext_model(split, char)
                        add(g, lab, "CPU", bench(one, many, texts, n_single))
        elif g in SENT:
            if all((g, l) in done for l in labels):
                continue
            from sentence_transformers import SentenceTransformer
            from .embed import _shim_transformers_onnx
            _shim_transformers_onnx()
            mid, cache_name = SENT[g]
            npz = sorted(glob.glob(str(CACHE / "embeddings" / f"{cache_name}_*.npz")))
            assert npz, f"no cached embeddings for {g}"
            Etr = np.load(npz[0])["X_tr"]
            assert len(Etr) == len(ytr), f"{g}: cached train embeddings do not match the train split"
            st = SentenceTransformer(mid, device="cuda" if gpu else "cpu")
            st.max_seq_length = min(st.max_seq_length or 512, 512)
            for lab in labels:
                if (g, lab) in done:
                    continue
                with threadpool_limits(1):
                    clf = clf_factory(CLF_OF[lab]).fit(Etr, ytr)
                if hasattr(clf, "n_jobs"):
                    clf.n_jobs = 1
                enc1 = lambda t: st.encode([t], normalize_embeddings=True, show_progress_bar=False)
                encn = lambda ts: st.encode(ts, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
                add(g, lab, "GPU" if gpu else "CPU", bench(lambda t: clf.predict(enc1(t)), lambda ts: clf.predict(encn(ts)),
                                                           texts, n_single), note="encoder on GPU, classifier on CPU")
            del st
            torch.cuda.empty_cache()
        elif g == "Fine-tuned":
            from .latency import hf_system
            for lab in labels:
                if (g, lab) in done:
                    continue
                one, many, model = hf_system(str(CACHE / "models" / FT[lab]), "cuda" if gpu else "cpu")
                add(g, lab, "GPU" if gpu else "CPU", bench(one, many, texts, n_single))
                del model
                torch.cuda.empty_cache()

    # DLF: Layer 1 (fastText char, positives x12) + Layer 2 (logged gpt-4o-mini calls)
    if ("DLF", "Layer 1") not in done:
        with threadpool_limits(1):
            one, many = fasttext_model(split, True, pos_weight=12)
            add("DLF", "Layer 1", "CPU", bench(one, many, texts, n_single))
    recs = []
    for f in [LLM_DIR / "tfidf_logistic_weighted_recall_gpt-4o-mini.responses.jsonl", LLM_DIR / "llm_cache_gpt-4o-mini.responses.jsonl"]:
        recs += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    lat = np.array([r["latency_s"] for r in recs if r.get("latency_s")])
    fwd = pd.read_csv(REPO / "results/classifier-results-baselines/evaluation_results/paper-repro/predictions/l1w12_fasttext_char.csv")["y_pred"].mean()
    l1 = [r for r in rows if r["group"] == "DLF" and r["classifier"] == "Layer 1"][0]
    rows = [r for r in rows if not (r["group"] == "DLF" and r["classifier"] != "Layer 1")]
    rows.append({"group": "DLF", "classifier": "Layer 2 (per forwarded message)", "device": "API",
                 "latency_ms": float(np.median(lat)) * 1e3, "latency_p95_ms": float(np.percentile(lat, 95)) * 1e3,
                 "throughput_msg_s": np.nan, "note": f"gpt-4o-mini, {len(lat)} logged calls; one sequential request"})
    rows.append({"group": "DLF", "classifier": "End-to-end (expected per message)", "device": "CPU+API",
                 "latency_ms": l1["latency_ms"] + fwd * float(np.mean(lat)) * 1e3, "latency_p95_ms": np.nan,
                 "throughput_msg_s": np.nan,
                 "note": f"Layer 1 + {fwd:.3f} (forwarded fraction) x mean Layer-2 latency; the Layer-2 call also parses the message"})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    meta = {"cpu": platform.processor() or platform.machine(), "gpu": torch.cuda.get_device_name(0) if gpu else None,
            "n_single": n_single, "n_test": len(texts), "forwarded_fraction": float(fwd)}
    (T / "latency_table3.meta.json").write_text(json.dumps(meta, indent=2))


def table():
    df = pd.read_csv(OUT_CSV)
    meta = json.loads((T / "latency_table3.meta.json").read_text())
    fmt_lat = lambda v: f"{v:.3f}" if v < 10 else (f"{v:.1f}" if v < 1000 else f"{v:,.0f}".replace(",", "{,}"))
    fmt_thr = lambda v: "--" if pd.isna(v) else (f"{v:,.0f}".replace(",", "{,}"))
    L = [r"\begin{table}[h]", r"\centering",
         r"\caption{End-to-end inference cost of every configuration of Table~\ref{tab:DLF} (raw message $\to$ label, "
         r"same machine). \emph{Latency}: median time to classify a single message; \emph{Throughput}: messages per second "
         r"when the 5{,}166 test messages are classified in one batch. Lexical and fastText models run on one CPU thread "
         r"(Intel i5-13450HX); sentence encoders and fine-tuned models on an RTX~3050 (6\,GB) GPU. DLF Layer~2 is a "
         r"gpt-4o-mini API call made only for the " + f"{meta['forwarded_fraction']*100:.0f}" + r"\% of messages forwarded by "
         r"Layer~1; the same call also produces the structured parse, which every pipeline needs for a detected request.}",
         r"\label{tab:latency}", r"\resizebox{\columnwidth}{!}{%", r"\begin{tabular}{@{}llcrr@{}}", r"\toprule",
         r"\textbf{Embedding} & \textbf{Classifier} & \textbf{Device} & \makecell[r]{\textbf{Latency}\\\textbf{(ms/msg)}} & "
         r"\makecell[r]{\textbf{Throughput}\\\textbf{(msg/s)}} \\", r"\midrule"]
    for g, items in GROUPS + [("DLF", [(None, "Layer 1"), (None, "Layer 2 (per forwarded message)"),
                                         (None, "End-to-end (expected per message)")])]:
        sub = [df[(df.group == g) & (df.classifier == lab)] for _, lab in items]
        sub = [s.iloc[0] for s in sub if len(s)]
        for i, r in enumerate(sub):
            first = (rf"\multirow{{{len(sub)}}}{{*}}{{{'\\textbf{DLF}' if g == 'DLF' else g}}}" if len(sub) > 1 else g) if i == 0 else ""
            lab = {"Layer 1": "Layer 1 (fastText)", "Layer 2 (per forwarded message)": "Layer 2 (gpt-4o-mini)$^{a}$",
                   "End-to-end (expected per message)": "Layer 1 + Layer 2$^{b}$"}.get(r.classifier, r.classifier)
            L.append(f"{first} & {lab} & {r.device} & {fmt_lat(r.latency_ms)} & {fmt_thr(r.throughput_msg_s)} \\\\")
        if sub:
            L.append(r"\midrule")
    L[-1] = r"\bottomrule"
    L += [r"\end{tabular}%", "}",
          r"\par\smallskip\footnotesize $^{a}$per forwarded message (median of logged API calls). "
          r"$^{b}$expected per incoming message: Layer~1 + forwarded fraction $\times$ mean Layer-2 latency.",
          r"\end{table}"]
    (T / "tab_latency.tex").write_text("% AUTO-GENERATED by binary-classifier/baselines/latency_table3.py\n" + "\n".join(L) + "\n")
    print(f"wrote {T / 'tab_latency.tex'} ({len(df)} rows)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--single-n", type=int, default=300)
    ap.add_argument("--table-only", action="store_true")
    args = ap.parse_args(argv)
    if not args.table_only:
        run(args.single_n)
    table()


if __name__ == "__main__":
    raise SystemExit(main())
