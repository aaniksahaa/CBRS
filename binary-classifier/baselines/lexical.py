"""CPU baselines: sklearn vectorizers x classifiers, and fastText."""
from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion
from sklearn.svm import SVC

from .data import Split
from .metrics import Timer, build_result, env_info, save_result
from .registry import BaselineSpec

log = logging.getLogger(__name__)

# Identical to binary-classifier/models.py so new rows are comparable to the old ones.
MODELS = {
    "logistic": lambda: LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", max_iter=10000),
    "svm": lambda: SVC(kernel="linear", probability=True),
    "random_forest": lambda: RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    "naive_bayes": lambda: MultinomialNB(),
}

VECTORIZERS = {
    "char_tfidf": lambda: TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=200_000,
                                          sublinear_tf=True, min_df=2),
    "word_char_tfidf": lambda: FeatureUnion([
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), max_features=50_000, sublinear_tf=True, min_df=2)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=200_000, sublinear_tf=True, min_df=2)),
    ]),
}


def run_lexical(spec: BaselineSpec, split: Split, out_dir: Path, classifiers=None) -> dict:
    vec = VECTORIZERS[spec.vectorizer]()
    with Timer() as t_vec:
        X_tr = vec.fit_transform(split.train["text"])
        X_te = vec.transform(split.test["text"])
    log.info("%s: %d features (%.1fs)", spec.vectorizer, X_tr.shape[1], t_vec.elapsed)
    y_tr = split.train["label"].to_numpy()
    y_te = split.test["label"].to_numpy()
    results = {}
    for clf_name in classifiers or spec.classifiers:
        key = f"{spec.result_key}_{clf_name}"
        clf = MODELS[clf_name]()
        with Timer() as t_fit:
            clf.fit(X_tr, y_tr)
        t0 = time.perf_counter()
        y_pred = clf.predict(X_te)
        infer = time.perf_counter() - t0
        result = build_result(
            vectorizer=spec.vectorizer, model=clf_name, embedding_model=None,
            y_true=y_te, y_pred=y_pred, avg_inference_time_seconds=infer / len(y_te),
            languages=split.test["language"].to_numpy(),
            extra={"baseline": spec.name, "description": spec.description, "kind": "lexical",
                   "n_features": int(X_tr.shape[1]), "vectorize_seconds": t_vec.elapsed, "fit_seconds": t_fit.elapsed,
                   "env": env_info(), "data": split.data_path, "matches_paper_split": split.matches_paper_split})
        path = save_result(result, out_dir, key)
        log.info("saved %s  acc=%.4f macroF1=%.4f fit=%.1fs", path, result["accuracy"], result["extra"]["macro_f1"], t_fit.elapsed)
        results[key] = result
    return results


def _ft_line(text: str, label: int | None = None) -> str:
    text = " ".join(str(text).split())  # fastText is line-oriented
    return (f"__label__{label} {text}" if label is not None else text)


def run_fasttext(spec: BaselineSpec, split: Split, out_dir: Path, cache_dir: Path, seed: int = 42) -> dict:
    try:
        import fasttext
    except ImportError as e:
        raise SystemExit("fastText not installed: pip install fasttext-wheel  (or: pip install fasttext)") from e
    work = cache_dir / "fasttext"
    work.mkdir(parents=True, exist_ok=True)
    train_file = work / f"{spec.name}_train.txt"
    train_file.write_text("\n".join(_ft_line(t, l) for t, l in zip(split.train["text"], split.train["label"])) + "\n",
                          encoding="utf-8")
    params = dict(spec.fasttext_params)
    params.setdefault("thread", 4)
    params.setdefault("seed", seed)
    params["verbose"] = 0
    with Timer() as t_fit:
        model = fasttext.train_supervised(input=str(train_file), **params)
    te_texts = [_ft_line(t) for t in split.test["text"]]
    t0 = time.perf_counter()
    labels, _ = model.predict(te_texts)
    infer = time.perf_counter() - t0
    y_pred = np.array([int(l[0].replace("__label__", "")) for l in labels])
    y_te = split.test["label"].to_numpy()
    result = build_result(
        vectorizer="fasttext", model="fasttext", embedding_model=None,
        y_true=y_te, y_pred=y_pred, avg_inference_time_seconds=infer / len(y_te),
        languages=split.test["language"].to_numpy(),
        extra={"baseline": spec.name, "description": spec.description, "kind": "fasttext",
               "fasttext_params": params, "fit_seconds": t_fit.elapsed,
               "n_words": len(model.get_words()), "env": env_info(), "data": split.data_path,
               "matches_paper_split": split.matches_paper_split})
    path = save_result(result, out_dir, spec.result_key)
    log.info("saved %s  acc=%.4f macroF1=%.4f fit=%.1fs", path, result["accuracy"], result["extra"]["macro_f1"], t_fit.elapsed)
    train_file.unlink(missing_ok=True)
    return {spec.result_key: result}
