"""Choose DLF Layer 1: fastest + most accurate, selected on VALIDATION, evaluated once on test.

Candidates (all with the paper's recall-first weighting, alpha = 12 on positives):
  word_tfidf_lr      word 1-2-gram TF-IDF (5k) + LogReg, class_weight {0:1, 1:12}   (current DLF Layer 1)
  count_lr           word 1-2-gram counts (5k) + LogReg, class_weight {0:1, 1:12}
  char_tfidf_lr      char_wb 2-5-gram TF-IDF (200k) + LogReg, class_weight {0:1, 1:12}
  word_char_tfidf_lr word + char TF-IDF union + LogReg, class_weight {0:1, 1:12}
  fasttext_char      fastText, subwords 2-5 + word bigrams; positives repeated 12x (= loss weight 12)
  fasttext_word      fastText, words + bigrams only;   positives repeated 12x
fastText matches the Layer-1 architecture written in the paper (subword embeddings -> average -> linear -> softmax).

Protocol
  1. Split: the paper's test split is untouched; 10% of the paper's train split (stratified, seed 42 - the same
     slice used for fine-tuning model selection) is the validation set.
  2. Each candidate is trained on the remaining 90% and predicts validation; Layer 2 (gpt-4o-mini, the repository
     prompt) re-checks every validation message the candidate forwards -> validation DLF metrics.
  3. Selection rule (fixed before looking at test): highest validation DLF F1 on the request class; any candidate
     within 0.25 F1 points of the best counts as tied and the one with the lowest single-message latency wins.
  4. Every candidate is retrained on the full paper train split (as all other Table 3 baselines) and evaluated on
     test once; the chosen one becomes the paper's DLF, the others are reported as an ablation.
LLM verdicts are cached by message SHA-256 (+ model + prompt), so a message is never sent twice; the existing
2,312 logged test calls are reused. All new calls carry the full reproducibility record of dlf_layer2.py.

    cd binary-classifier && python -m baselines.layer1_search            # --dry-run to see how many calls are needed
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import FeatureUnion

from .data import load_split
from .dlf_layer2 import DLF_DIR, call_one, get_prompt, install_recorder, now_utc, sha256_text
from .metrics import build_result, env_info, save_predictions, save_result
from .run import DEFAULT_OUT

log = logging.getLogger("layer1_search")
ALPHA = 12
TIE_PTS = 0.25
CANDIDATES = ["word_tfidf_lr", "count_lr", "char_tfidf_lr", "word_char_tfidf_lr", "fasttext_char", "fasttext_word"]
LATENCY_NAME = {  # rows of paper/tables/latency_benchmark.csv (inference cost does not depend on the class weight)
    "word_tfidf_lr": "DLF Layer 1: word TF-IDF + weighted LogReg", "count_lr": "Count + LogReg (paper row)",
    "char_tfidf_lr": "Char n-gram TF-IDF + LogReg", "word_char_tfidf_lr": None,
    "fasttext_char": "fastText, char n-grams 2-5", "fasttext_word": "fastText, word only"}


def lr():
    return LogisticRegression(class_weight={0: 1.0, 1: float(ALPHA)}, C=1.0, penalty="l2", solver="lbfgs", max_iter=10000)


def word_tfidf():
    return TfidfVectorizer(max_features=5000, ngram_range=(1, 2))


def char_tfidf():
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=200_000, sublinear_tf=True, min_df=2)


def fit_predict(name: str, Xtr, ytr, Xte, workdir: Path):
    """Returns (pred, score) for Xte."""
    if name.startswith("fasttext"):
        import fasttext
        params = dict(dim=100, epoch=25, lr=1.0, wordNgrams=2, minCount=1, thread=1, seed=42, verbose=0,
                      **({"minn": 2, "maxn": 5} if name == "fasttext_char" else {"minn": 0, "maxn": 0}))
        workdir.mkdir(parents=True, exist_ok=True)
        f = workdir / f"{name}_train.txt"
        clean = lambda t: " ".join(str(t).split())
        lines = []
        for t, l in zip(Xtr, ytr):
            lines += [f"__label__{int(l)} {clean(t)}"] * (ALPHA if l == 1 else 1)
        f.write_text("\n".join(lines) + "\n", encoding="utf-8")
        m = fasttext.train_supervised(input=str(f), **params)
        labs, probs = m.predict([clean(t) for t in Xte], k=2)
        score = np.array([dict(zip(l, p)).get("__label__1", 0.0) for l, p in zip(labs, probs)])
        pred = np.array([int(l[0].replace("__label__", "")) for l in labs])
        return pred, score
    vec = {"word_tfidf_lr": word_tfidf, "count_lr": lambda: CountVectorizer(max_features=5000, ngram_range=(1, 2)),
           "char_tfidf_lr": char_tfidf,
           "word_char_tfidf_lr": lambda: FeatureUnion([("w", word_tfidf()), ("c", char_tfidf())])}[name]()
    clf = lr().fit(vec.fit_transform(Xtr), ytr)
    Z = vec.transform(Xte)
    return clf.predict(Z), clf.predict_proba(Z)[:, 1]


def metrics(y, p) -> dict:
    return {"acc": accuracy_score(y, p), "p_pos": precision_score(y, p, zero_division=0),
            "r_pos": recall_score(y, p), "f1_pos": f1_score(y, p), "macro_f1": f1_score(y, p, average="macro")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="train candidates and count needed LLM calls, query nothing")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)

    out = Path(args.out)
    sdir = out / "layer1-search"
    art = out / "paper-repro" / "dlf_layer2"
    sdir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S",
                        handlers=[logging.StreamHandler(), logging.FileHandler(sdir / "layer1_search.log", encoding="utf-8")])
    for noisy in ("httpx", "httpcore", "openai", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    sp = load_split(val_fraction=0.1, seed=42)
    full = load_split()  # same test split; full paper train split
    assert np.array_equal(sp.test["label"].to_numpy(), full.test["label"].to_numpy())
    splits = {"val": sp.val, "test": full.test}

    # ---------------------------------------------------------------- layer-1 predictions
    l1 = {}
    for name in CANDIDATES:
        t0 = time.perf_counter()
        pv, sv = fit_predict(name, sp.train["text"].tolist(), sp.train["label"].to_numpy(), sp.val["text"].tolist(), sdir / "tmp")
        pt, st = fit_predict(name, full.train["text"].tolist(), full.train["label"].to_numpy(), full.test["text"].tolist(), sdir / "tmp")
        l1[name] = {"val": (pv, sv), "test": (pt, st)}
        log.info("%-20s layer-1 val R+=%.4f fwd=%d | test R+=%.4f fwd=%d  (%.0fs)", name,
                 recall_score(sp.val["label"], pv), pv.sum(), recall_score(full.test["label"], pt), pt.sum(), time.perf_counter() - t0)
    ref = pd.read_csv(out / "paper-repro" / "predictions" / "tfidf_logistic_weighted_recall.csv")
    same = np.array_equal(ref["y_pred"].to_numpy(), l1["word_tfidf_lr"]["test"][0])
    log.info("consistency: word_tfidf_lr test predictions identical to the existing DLF Layer 1: %s", same)

    # ---------------------------------------------------------------- LLM cache keyed by message hash
    prompt_sha = sha256_text(get_prompt("{MESSAGE}"))
    cache_path = art / f"llm_cache_{args.model}.responses.jsonl"
    cache: dict[str, dict] = {}
    for f in [art / f"tfidf_logistic_weighted_recall_{args.model}.responses.jsonl", cache_path]:
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    if r.get("verdict") is not None or "error" not in r:
                        cache[r["message_sha256"]] = r
    need = {}
    for sname, df in splits.items():
        texts = df["text"].tolist()
        fwd = np.zeros(len(df), bool)
        for name in CANDIDATES:
            fwd |= l1[name][sname][0] == 1
        for i in np.nonzero(fwd)[0]:
            h = sha256_text(texts[i])
            if h not in cache and h not in need:
                need[h] = (sname, int(i), texts[i], int(df["label"].iloc[i]), str(df["language"].iloc[i]))
    log.info("LLM verdicts cached: %d; new calls needed (union over candidates, val + test): %d", len(cache), len(need))
    if args.dry_run:
        return 0

    if need:
        sys.path.insert(0, str(DLF_DIR))
        import llmclient
        install_recorder(llmclient, 42, True, 5)
        client = llmclient.LLMClient()
        client.set_model(args.model)
        lock = threading.Lock()
        with open(cache_path, "a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = [pool.submit(call_one, client, i, text, {"_model": args.model, "split": s, "y_true": y, "language": lang})
                    for h, (s, i, text, y, lang) in need.items()]
            for n, fut in enumerate(as_completed(futs), 1):
                rec = fut.result()
                rec["prompt_template_sha256"] = prompt_sha
                with lock:
                    cache[rec["message_sha256"]] = rec
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fh.flush()
                if n % 100 == 0 or n == len(need):
                    log.info("%d/%d new LLM calls, cost so far $%.4f", n, len(need),
                             sum((r.get("cost_usd") or 0) for r in cache.values() if r.get("split")))

    # ---------------------------------------------------------------- DLF per candidate
    lat = {}
    lat_csv = Path(__file__).resolve().parents[2] / "paper" / "tables" / "latency_benchmark.csv"
    if lat_csv.exists():
        L = pd.read_csv(lat_csv).set_index("system")
        lat = {k: (float(L.at[v, "single_median_s"]) if v in L.index else None) for k, v in LATENCY_NAME.items()}
    rows, dlf_test = [], {}
    for name in CANDIDATES:
        row = {"candidate": name, "single_msg_latency_ms": None if lat.get(name) is None else lat[name] * 1e3}
        for sname, df in splits.items():
            y = df["label"].to_numpy()
            p1 = l1[name][sname][0]
            pd_ = p1.copy()
            texts = df["text"].tolist()
            n_missing = 0
            for i in np.nonzero(p1 == 1)[0]:
                r = cache.get(sha256_text(texts[i]))
                if r is None:
                    n_missing += 1
                elif r.get("verdict") is False:
                    pd_[i] = 0
            m1, md = metrics(y, p1), metrics(y, pd_)
            row.update({f"{sname}_l1_{k}": v for k, v in m1.items()})
            row.update({f"{sname}_dlf_{k}": v for k, v in md.items()})
            row[f"{sname}_forwarded"] = int(p1.sum())
            row[f"{sname}_missing_llm"] = n_missing
            if sname == "test":
                dlf_test[name] = pd_
        rows.append(row)
    res = pd.DataFrame(rows)
    best = res["val_dlf_f1_pos"].max()
    tied = res[res["val_dlf_f1_pos"] >= best - TIE_PTS / 100]
    chosen = tied.sort_values("single_msg_latency_ms", na_position="last").iloc[0]["candidate"]
    res["chosen"] = res["candidate"] == chosen
    res["tied_with_best_on_val"] = res["candidate"].isin(tied["candidate"])
    res.to_csv(sdir / "layer1_search_results.csv", index=False)
    log.info("selection: best val DLF F1+ %.4f; tied (within %.2f pts): %s; chosen (fastest of tied): %s",
             best, TIE_PTS, list(tied["candidate"]), chosen)

    # ---------------------------------------------------------------- save test predictions + results
    y = full.test["label"].to_numpy()
    langs = full.test["language"].to_numpy()
    for name in CANDIDATES:
        p1, s1 = l1[name]["test"]
        for key, pred, score, kind in [(f"l1w12_{name}", p1, s1, "layer1"), (f"dlf_full_l1w12_{name}_{args.model}", dlf_test[name], None, "dlf")]:
            save_predictions(sdir, key, y_true=y, y_pred=pred, scores=score, languages=langs)
            r = build_result(vectorizer=name, model=kind, embedding_model=args.model if kind == "dlf" else None,
                             y_true=y, y_pred=pred, avg_inference_time_seconds=lat.get(name) or 0.0, languages=langs,
                             extra={"baseline": key, "kind": kind, "alpha_pos": ALPHA, "chosen": name == chosen,
                                    "selection": "validation DLF F1+ (tie 0.25 pts -> fastest)", "env": env_info()})
            save_result(r, sdir, key)
    # the chosen DLF joins the comparison set used by significance.py (unless it is the existing Layer 1)
    if chosen != "word_tfidf_lr":
        key = f"dlf_full_l1w12_{chosen}_{args.model}"
        save_predictions(out / "paper-repro", key, y_true=y, y_pred=dlf_test[chosen], languages=langs)
        save_result(json.load(open(sdir / f"{key}.json")), out / "paper-repro", key)
        key1 = f"l1w12_{chosen}"
        save_predictions(out / "paper-repro", key1, y_true=y, y_pred=l1[chosen]["test"][0], scores=l1[chosen]["test"][1], languages=langs)
        save_result(json.load(open(sdir / f"{key1}.json")), out / "paper-repro", key1)
    show = ["candidate", "single_msg_latency_ms", "val_l1_r_pos", "val_forwarded", "val_dlf_f1_pos", "val_dlf_acc",
            "test_l1_r_pos", "test_forwarded", "test_dlf_acc", "test_dlf_f1_pos", "test_dlf_macro_f1", "chosen"]
    print(res[show].to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
