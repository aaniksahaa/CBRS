"""Metric computation + result JSON in the same schema as the existing results."""
from __future__ import annotations

import json
import os
import platform
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score


def compute_metrics(y_true, y_pred, languages=None) -> dict:
    """classification_report(y_true, y_pred) (correct orientation) + per-language breakdown."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    report = classification_report(y_true, y_pred, digits=8, output_dict=True, zero_division=0)
    out = {"report": report,
           "accuracy": float(accuracy_score(y_true, y_pred)),
           "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
           "weighted_f1": float(f1_score(y_true, y_pred, average="weighted")),
           "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()}
    if languages is not None:
        languages = np.asarray(languages)
        per_lang = {}
        for lang in sorted(set(languages.tolist())):
            m = languages == lang
            if m.sum() == 0:
                continue
            per_lang[str(lang)] = {
                "n": int(m.sum()),
                "accuracy": float(accuracy_score(y_true[m], y_pred[m])),
                "macro_f1": float(f1_score(y_true[m], y_pred[m], average="macro", zero_division=0)),
                "positive_recall": float(((y_pred[m] == 1) & (y_true[m] == 1)).sum() / max(1, (y_true[m] == 1).sum())),
            }
        out["per_language"] = per_lang
    return out


def build_result(*, vectorizer: str, model: str, embedding_model: str | None, y_true, y_pred,
                 avg_inference_time_seconds: float, languages=None, extra: dict | None = None) -> dict:
    """Same top-level keys as results/classifier-results-with-time/*.json, plus `extra`."""
    m = compute_metrics(y_true, y_pred, languages)
    result = {
        "vectorizer": vectorizer,
        "model": model,
        "embedding_model": embedding_model if embedding_model else "N/A",
        "accuracy": m["accuracy"],
        "avg_inference_time_seconds": float(avg_inference_time_seconds),
        "metrics": m["report"],
        "extra": {
            "macro_f1": m["macro_f1"],
            "weighted_f1": m["weighted_f1"],
            "confusion_matrix": m["confusion_matrix"],
            "per_language": m.get("per_language", {}),
            "n_test": int(len(np.asarray(y_true))),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "host": platform.node(),
            "python": platform.python_version(),
            **(extra or {}),
        },
    }
    return result


def save_result(result: dict, out_dir: str | Path, key: str) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / (f"{key}.json".replace("/", "_"))
    with open(path, "w") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    return path


def result_exists(out_dir: str | Path, key: str) -> bool:
    return (Path(out_dir) / (f"{key}.json".replace("/", "_"))).exists()


class Timer:
    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *a):
        self.elapsed = time.perf_counter() - self.t0


def env_info() -> dict:
    info = {"cuda": False}
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda"] = torch.cuda.is_available()
        if info["cuda"]:
            info["gpu"] = torch.cuda.get_device_name(0)
            info["gpu_mem_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1)
    except Exception:  # torch not installed for lexical-only runs
        pass
    try:
        import transformers
        info["transformers"] = transformers.__version__
    except Exception:
        pass
    info["cpu_count"] = os.cpu_count()
    return info
