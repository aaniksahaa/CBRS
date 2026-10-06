"""Score every system on the original and on the corrected test labels, from saved per-message predictions.

    cd binary-classifier && python -m baselines.rescore      # -> paper/tables/scores_original_vs_corrected.{csv,md}
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from .aggregate import NEW_DIR, TABLES_DIR
from .significance import load_systems

LABELS = NEW_DIR.parents[0] / "relabel" / "test_labels_corrected.csv"


def score(y, p):
    return {"acc": accuracy_score(y, p), "p_pos": precision_score(y, p), "r_pos": recall_score(y, p),
            "f1_pos": f1_score(y, p), "macro_f1": f1_score(y, p, average="macro")}


def main():
    dirs = [(NEW_DIR, "new"), (NEW_DIR / "paper-repro", "paper-repro")]
    systems = load_systems(dirs, None, None)
    lab = pd.read_csv(LABELS)
    corr, orig = lab["label_corrected"].to_numpy(), lab["label_original"].to_numpy()
    rows = []
    for k, s in systems.items():
        o, c = score(orig, s["y_pred"]), score(corr, s["y_pred"])
        rows.append({"system": s["label"], "key": k, **{f"orig_{m}": v for m, v in o.items()},
                     **{f"corr_{m}": v for m, v in c.items()}})
    df = pd.DataFrame(rows)
    df["orig_rank_f1"] = df["orig_f1_pos"].rank(ascending=False, method="min").astype(int)
    df["corr_rank_f1"] = df["corr_f1_pos"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("corr_f1_pos", ascending=False)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES_DIR / "scores_original_vs_corrected.csv", index=False)
    md = ["| Rank (corr.) | System | Acc orig | Acc corr | F1+ orig | F1+ corr | Macro-F1 orig | Macro-F1 corr | Rank (orig.) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        md.append(f"| {r.corr_rank_f1} | {r.system} | {r.orig_acc:.4f} | {r.corr_acc:.4f} | {r.orig_f1_pos:.4f} | "
                  f"{r.corr_f1_pos:.4f} | {r.orig_macro_f1:.4f} | {r.corr_macro_f1:.4f} | {r.orig_rank_f1} |")
    (TABLES_DIR / "scores_original_vs_corrected.md").write_text(
        f"Scores of {len(df)} systems on the 5,166 test messages; corrected labels = {LABELS.name} "
        f"({int((corr != orig).sum())} human-verified label corrections: 63 request->not request, 18 not request->request).\n\n" + "\n".join(md) + "\n")
    print("\n".join(md[:2] + md[2:14]))
    print(f"... {len(df)} systems -> {TABLES_DIR / 'scores_original_vs_corrected.md'}")


if __name__ == "__main__":
    main()
