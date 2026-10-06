"""Apples-to-apples inference latency: raw text in -> label out, same machine, same test messages.

Table 3's times are not comparable across rows: the sklearn rows time only `clf.predict` on pre-computed
features, the fine-tuned rows time the whole pipeline. This benchmark times every system end-to-end:

  * single  : one message at a time (streaming / bot scenario), median and p95 over N messages
  * batch   : all 5,166 test messages in one call (offline scenario), seconds per message
  * CPU rows are forced to 1 thread so they are comparable; GPU rows use the local GPU.

    cd binary-classifier && python -m baselines.latency            # writes paper/tables/latency_benchmark.{csv,md}
    python -m baselines.latency --single-n 300 --skip-gpu
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import time
from pathlib import Path

import numpy as np

from .data import load_split

REPO = Path(__file__).resolve().parents[2]
MODELS_DIR = Path(os.environ.get("CBRS_BASELINE_CACHE", Path.home() / ".cache" / "cbrs-baselines")) / "models"
LLM_ARTIFACTS = REPO / "results/classifier-results-baselines/evaluation_results/paper-repro/dlf_layer2"


def one_thread():
    for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[v] = "1"


def bench(predict_one, predict_batch, texts, single_n):
    for t in texts[:20]:  # warm-up
        predict_one(t)
    lat = []
    for t in texts[:single_n]:
        t0 = time.perf_counter()
        predict_one(t)
        lat.append(time.perf_counter() - t0)
    t0 = time.perf_counter()
    predict_batch(texts)
    batch = (time.perf_counter() - t0) / len(texts)
    return {"single_median_s": statistics.median(lat), "single_p95_s": float(np.percentile(lat, 95)),
            "batch_s_per_msg": batch}


def sklearn_system(vec, clf, Xtr, ytr):
    vec_ = vec()
    clf_ = clf()
    clf_.fit(vec_.fit_transform(Xtr), ytr)
    return (lambda t: clf_.predict(vec_.transform([t]))), (lambda ts: clf_.predict(vec_.transform(ts)))


def fasttext_system(split, params, workdir, pos_weight=1):
    import fasttext
    workdir.mkdir(parents=True, exist_ok=True)
    f = workdir / "lat_train.txt"
    lines = []
    for t, l in zip(split.train["text"], split.train["label"]):
        line = f"__label__{l} {' '.join(str(t).split())}"
        lines += [line] * (pos_weight if l == 1 else 1)
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    m = fasttext.train_supervised(input=str(f), thread=1, seed=42, verbose=0, **params)
    clean = lambda t: " ".join(str(t).split())
    # single-string predict() is broken under NumPy 2 (np.array(copy=False)); a one-element list is equivalent
    return (lambda t: m.predict([clean(t)])), (lambda ts: m.predict([clean(t) for t in ts]))


def hf_system(path, device, max_length=128, batch_size=64):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSequenceClassification.from_pretrained(path).to(device).eval()
    dev = torch.device(device)

    @torch.no_grad()
    def one(t):
        out = model(**tok(t, truncation=True, max_length=max_length, return_tensors="pt").to(dev)).logits.argmax(-1)
        if dev.type == "cuda":
            torch.cuda.synchronize()
        return out

    @torch.no_grad()
    def many(ts):
        for i in range(0, len(ts), batch_size):
            model(**tok(ts[i:i + batch_size], padding=True, truncation=True, max_length=max_length,
                        return_tensors="pt").to(dev)).logits.argmax(-1)
        if dev.type == "cuda":
            torch.cuda.synchronize()
    return one, many, model


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--single-n", type=int, default=500, help="messages timed one at a time")
    ap.add_argument("--skip-gpu", action="store_true")
    ap.add_argument("--with-svm", action="store_true", help="also retrain + time the char n-gram SVM (~6 min)")
    ap.add_argument("--cpu-bert", nargs="*", default=["banglabert_ft", "distilbert_multilingual_ft"],
                    help="fine-tuned models also timed on CPU (1 thread is very slow; these use all cores)")
    ap.add_argument("--out", default=str(REPO / "paper" / "tables" / "latency_benchmark"))
    args = ap.parse_args(argv)
    one_thread()

    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC

    split = load_split()
    Xtr, ytr = split.train["text"].tolist(), split.train["label"].to_numpy()
    texts = split.test["text"].tolist()
    rows = []

    def add(name, group, device, res, note=""):
        rows.append({"system": name, "group": group, "device": device, **res, "note": note})
        print(f"{name:52s} {device:5s} single median {res['single_median_s']*1e3:9.3f} ms  "
              f"p95 {res['single_p95_s']*1e3:9.3f} ms  batch {res['batch_s_per_msg']*1e6:10.1f} us/msg", flush=True)

    word = lambda: TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    char = lambda: TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=200_000, sublinear_tf=True, min_df=2)
    lr = lambda: LogisticRegression(C=1.0, max_iter=10000)
    lrw = lambda: LogisticRegression(class_weight={0: 1.0, 1: 12.0}, C=1.0, max_iter=10000)

    o, b = sklearn_system(word, lrw, Xtr, ytr); add("DLF Layer 1: word TF-IDF + weighted LogReg", "layer1", "cpu1", bench(o, b, texts, args.single_n))
    o, b = sklearn_system(word, lr, Xtr, ytr); add("TF-IDF + LogReg (paper row)", "lexical", "cpu1", bench(o, b, texts, args.single_n))
    o, b = sklearn_system(lambda: CountVectorizer(max_features=5000, ngram_range=(1, 2)), lr, Xtr, ytr)
    add("Count + LogReg (paper row)", "lexical", "cpu1", bench(o, b, texts, args.single_n))
    o, b = sklearn_system(char, lr, Xtr, ytr); add("Char n-gram TF-IDF + LogReg", "lexical", "cpu1", bench(o, b, texts, args.single_n))
    if args.with_svm:  # ~6 min to retrain; not needed for the DLF-vs-encoder question
        o, b = sklearn_system(char, lambda: SVC(kernel="linear"), Xtr, ytr)
        add("Char n-gram TF-IDF + SVM", "lexical", "cpu1", bench(o, b, texts, min(args.single_n, 200)))
    wd = MODELS_DIR.parent / "latency"
    o, b = fasttext_system(split, dict(dim=100, epoch=25, lr=1.0, wordNgrams=2, minn=2, maxn=5, minCount=1), wd)
    add("fastText, char n-grams 2-5", "fasttext", "cpu1", bench(o, b, texts, args.single_n))
    o, b = fasttext_system(split, dict(dim=100, epoch=25, lr=1.0, wordNgrams=2, minn=0, maxn=0, minCount=1), wd)
    add("fastText, word only", "fasttext", "cpu1", bench(o, b, texts, args.single_n))

    import torch
    if not args.skip_gpu and torch.cuda.is_available():
        for name in ["banglabert_ft", "mbert_ft", "xlmr_base_ft", "muril_ft", "indicbert_ft", "distilbert_multilingual_ft",
                     "paper_mobilebert_ft"]:
            p = MODELS_DIR / name
            if not p.exists():
                continue
            one, many, model = hf_system(str(p), "cuda")
            add(f"{name} (fine-tuned)", "finetuned", "gpu", bench(one, many, texts, min(args.single_n, 300)),
                note=torch.cuda.get_device_name(0))
            del model
            torch.cuda.empty_cache()
    torch.set_num_threads(os.cpu_count() or 1)
    for name in args.cpu_bert:
        p = MODELS_DIR / name
        if p.exists():
            one, many, model = hf_system(str(p), "cpu")
            add(f"{name} (fine-tuned)", "finetuned", f"cpu{os.cpu_count()}", bench(one, many, texts[:1000], 100),
                note="batch timed on first 1,000 messages")
            del model

    # LLM layer: measured latencies from the logged API calls (not re-run here)
    for m in ("gpt-4o-mini", "gpt-5-mini"):
        f = LLM_ARTIFACTS / f"tfidf_logistic_weighted_recall_{m}.calls.csv"
        if f.exists():
            import pandas as pd
            lat = pd.read_csv(f)["latency_s"].dropna()
            frac = len(lat) / len(texts)
            rows.append({"system": f"DLF Layer 2 API call ({m}), per forwarded message", "group": "llm", "device": "api",
                         "single_median_s": float(lat.median()), "single_p95_s": float(lat.quantile(0.95)),
                         "batch_s_per_msg": float(lat.mean() * frac),
                         "note": f"logged latencies of {len(lat)} calls; batch = mean x forwarded fraction {frac:.3f}, sequential"})
            print(f"{'LLM ' + m:52s} api   single median {lat.median()*1e3:9.1f} ms", flush=True)

    import pandas as pd
    df = pd.DataFrame(rows)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out.with_suffix(".csv"), index=False)
    meta = {"cpu": platform.processor() or platform.machine(), "python": platform.python_version(),
            "n_test": len(texts), "single_n": args.single_n,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
    md = ["| System | Device | Single msg median (ms) | p95 (ms) | Batch (µs/msg) |", "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['system']} | {r['device']} | {r['single_median_s']*1e3:.3f} | {r['single_p95_s']*1e3:.3f} | "
                  f"{r['batch_s_per_msg']*1e6:.1f} |")
    out.with_suffix(".md").write_text(f"Latency benchmark ({json.dumps(meta)})\n\n" + "\n".join(md) + "\n")
    print(f"\nwrote {out.with_suffix('.csv')} and .md")


if __name__ == "__main__":
    raise SystemExit(main())
