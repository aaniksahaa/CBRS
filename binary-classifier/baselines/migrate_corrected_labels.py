"""Switch every saved per-message prediction file and result JSON to the corrected test labels (no retraining).

For each <dir>/predictions/<key>.csv: y_true := corrected label, the original label is kept as y_true_original.
For the matching <dir>/<key>.json: accuracy / metrics / extra.{macro_f1, weighted_f1, confusion_matrix,
per_language} are recomputed on the corrected labels; the original-label values are preserved under
extra.metrics_original_labels. Idempotent.

    cd binary-classifier && python -m baselines.migrate_corrected_labels
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .metrics import compute_metrics

REPO = Path(__file__).resolve().parents[2]
RES = REPO / "results/classifier-results-baselines/evaluation_results"
CORR = REPO / "results/classifier-results-baselines/relabel/test_labels_corrected.csv"
NOTE = "corrected test labels (2026-10-06): 81 of 5,166 human-verified corrections (63 request->not request, 18 not request->request)"


def main():
    C = pd.read_csv(CORR)
    orig, corr = C["label_original"].to_numpy(), C["label_corrected"].to_numpy()
    n_csv = n_json = 0
    for pdir in [RES / "predictions", RES / "paper-repro" / "predictions", RES / "layer1-search" / "predictions"]:
        if not pdir.exists():
            continue
        for f in sorted(pdir.glob("*.csv")):
            df = pd.read_csv(f)
            if len(df) != len(C):
                continue
            if "y_true_original" not in df:
                assert (df["y_true"].to_numpy() == orig).all(), f"{f}: y_true is not the original test labels"
                df.insert(df.columns.get_loc("y_true") + 1, "y_true_original", df["y_true"])
                df["y_true"] = corr
                df.to_csv(f, index=False)
                n_csv += 1
            j = pdir.parent / f"{f.stem}.json"
            if not j.exists():
                continue
            r = json.loads(j.read_text())
            ex = r.setdefault("extra", {})
            if "metrics_original_labels" in ex:
                continue
            m = compute_metrics(corr, df["y_pred"].to_numpy(), df["language"].to_numpy() if "language" in df else None)
            ex["metrics_original_labels"] = {"accuracy": r.get("accuracy"), "metrics": r.get("metrics"),
                                             "macro_f1": ex.get("macro_f1"), "weighted_f1": ex.get("weighted_f1"),
                                             "confusion_matrix": ex.get("confusion_matrix"), "per_language": ex.get("per_language")}
            r["accuracy"] = m["accuracy"]
            r["metrics"] = m["report"]
            ex.update(macro_f1=m["macro_f1"], weighted_f1=m["weighted_f1"], confusion_matrix=m["confusion_matrix"],
                      per_language=m.get("per_language", {}), labels=NOTE)
            j.write_text(json.dumps(r, indent=4, ensure_ascii=False))
            n_json += 1
    print(f"prediction files switched to corrected labels: {n_csv}; result JSONs recomputed: {n_json}")


if __name__ == "__main__":
    main()
