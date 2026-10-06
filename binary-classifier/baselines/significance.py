"""Paired significance tests for Table 3 (all systems are scored on the same 5,166 test messages).

For a reference system R and every other system S:
  * paired bootstrap (default 10,000 resamples of test messages, resampled jointly for R and S) ->
    95% percentile CI and two-sided p-value for the difference R-S in accuracy, positive-class F1,
    positive-class recall and macro F1;
  * exact McNemar test on per-message correctness (discordant pairs);
  * Holm-Bonferroni correction of the p-values across all comparisons of a metric family.

    python -m baselines.significance                                   # reference = DLF layer 1 (if present)
    python -m baselines.significance --ref finetune_csebuetnlp_banglabert_bert
    python -m baselines.significance --all-pairs                       # McNemar matrix over every pair
    python -m baselines.significance --include 'Fine-tuned|DLF|fastText|LogReg' --B 20000

Inputs are the per-message prediction CSVs written by the runners
(<out>/predictions/<key>.csv and <out>/paper-repro/predictions/<key>.csv).
Outputs: markdown on stdout, paper/tables/significance_<ref>.{csv,tex} and significance_markers.json.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binom

from .aggregate import NEW_DIR, TABLES_DIR, load_rows

METRICS = ("accuracy", "f1_pos", "recall_pos", "macro_f1")


# ----------------------------------------------------------------------------- loading
def load_systems(dirs: list[tuple[Path, str]], include: str | None, exclude: str | None) -> dict[str, dict]:
    """key -> {label, y_true, y_pred, language, origin}; labels come from the matching result JSON."""
    systems = {}
    for d, origin in dirs:
        rows = {r["file"][:-5]: r for r in load_rows([(d, origin)], avg="macro")}
        for csv in sorted((d / "predictions").glob("*.csv")):
            key = csv.stem
            r = rows.get(key)
            label = f"{r['group']} + {r['classifier']}" if r else key
            if r and r["kind"] == "finetune":
                label = f"{r['group']} (fine-tuned)"
            elif r and r["kind"] == "fasttext":
                label = r["group"]
            if key == "tfidf_logistic_weighted":
                label = "DLF layer 1 as coded (neg. weighted 15:1)"
            elif key == "tfidf_logistic_weighted_recall":
                label = "DLF layer 1 (pos. weighted 12:1)"
            elif key.startswith("dlf_full"):
                label = "DLF (layer 1 + LLM layer 2)"
            if include and not re.search(include, label):
                continue
            if exclude and re.search(exclude, label):
                continue
            df = pd.read_csv(csv)
            systems[key] = {"label": label, "y_true": df["y_true"].to_numpy(), "y_pred": df["y_pred"].to_numpy(),
                            "language": df["language"].to_numpy() if "language" in df else None, "origin": origin,
                            "kind": r["kind"] if r else "?"}
    if not systems:
        raise SystemExit("no prediction CSVs found; run the baselines first (they now write <out>/predictions/)")
    ref_truth = next(iter(systems.values()))["y_true"]
    for k, s in systems.items():
        if len(s["y_true"]) != len(ref_truth) or not np.array_equal(s["y_true"], ref_truth):
            raise SystemExit(f"{k}: test labels differ from the other systems - not the same split")
    return systems


# ----------------------------------------------------------------------------- metrics from indicator sums
def indicators(y_true, y_pred) -> np.ndarray:
    """per-message columns: correct, tp, fp, fn, tn  (so every metric is a function of column sums)."""
    y_true = y_true.astype(int); y_pred = y_pred.astype(int)
    return np.stack([(y_true == y_pred), (y_true == 1) & (y_pred == 1), (y_true == 0) & (y_pred == 1),
                     (y_true == 1) & (y_pred == 0), (y_true == 0) & (y_pred == 0)], axis=1).astype(np.float64)


def metrics_from_sums(S: np.ndarray) -> dict[str, np.ndarray]:
    """S[..., 5] = sums of indicator columns -> metrics (vectorised over leading dims)."""
    correct, tp, fp, fn, tn = (S[..., i] for i in range(5))
    n = tp + fp + fn + tn
    eps = 1e-12
    f1_pos = 2 * tp / np.maximum(2 * tp + fp + fn, eps)
    f1_neg = 2 * tn / np.maximum(2 * tn + fp + fn, eps)
    return {"accuracy": correct / n, "f1_pos": f1_pos, "recall_pos": tp / np.maximum(tp + fn, eps),
            "macro_f1": (f1_pos + f1_neg) / 2}


def paired_bootstrap(ind_r: np.ndarray, ind_s: np.ndarray, B: int, rng: np.random.Generator, chunk: int = 1000):
    """Returns {metric: (delta, lo, hi, p)} for delta = metric(R) - metric(S) under joint resampling."""
    n = ind_r.shape[0]
    point_r = metrics_from_sums(ind_r.sum(0)); point_s = metrics_from_sums(ind_s.sum(0))
    deltas = {m: [] for m in METRICS}
    done = 0
    while done < B:
        b = min(chunk, B - done)
        W = rng.multinomial(n, np.full(n, 1.0 / n), size=b).astype(np.float64)  # resample weights, b x n
        mr = metrics_from_sums(W @ ind_r); ms = metrics_from_sums(W @ ind_s)
        for m in METRICS:
            deltas[m].append(mr[m] - ms[m])
        done += b
    out = {}
    for m in METRICS:
        d = np.concatenate(deltas[m])
        lo, hi = np.percentile(d, [2.5, 97.5])
        p = 2 * min((d <= 0).mean(), (d >= 0).mean())
        p = max(min(p, 1.0), 1.0 / B)
        out[m] = (float(point_r[m] - point_s[m]), float(lo), float(hi), float(p))
    return out


def mcnemar_exact(correct_r: np.ndarray, correct_s: np.ndarray) -> tuple[int, int, float]:
    """b = R right & S wrong, c = R wrong & S right; exact two-sided binomial test on (b, c)."""
    b = int(((correct_r == 1) & (correct_s == 0)).sum())
    c = int(((correct_r == 0) & (correct_s == 1)).sum())
    n = b + c
    if n == 0:
        return b, c, 1.0
    p = min(1.0, 2 * binom.cdf(min(b, c), n, 0.5))
    return b, c, float(p)


def holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        val = (m - rank) * pvals[i]
        running = max(running, val)
        adj[i] = min(1.0, running)
    return adj.tolist()


# ----------------------------------------------------------------------------- reporting
def stars(p: float) -> str:
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


def fmt_ci(d, lo, hi, scale=100.0):
    return f"{d*scale:+.2f} [{lo*scale:+.2f}, {hi*scale:+.2f}]"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--new-dir", default=str(NEW_DIR))
    ap.add_argument("--paper-dir", default=str(NEW_DIR / "paper-repro"))
    ap.add_argument("--ref", default=None, help="prediction key of the reference system (default: DLF layer 1 if present, else best macro-F1)")
    ap.add_argument("--B", type=int, default=10000, help="bootstrap resamples")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--include", default=None, help="regex on system labels to keep")
    ap.add_argument("--exclude", default=None, help="regex on system labels to drop")
    ap.add_argument("--all-pairs", action="store_true", help="also compute the Holm-corrected McNemar matrix over all pairs")
    ap.add_argument("--tables-dir", default=str(TABLES_DIR))
    ap.add_argument("--suffix", default="", help="appended to output file names (e.g. _compact)")
    ap.add_argument("--label", default="tab:significance", help="LaTeX label of the generated table")
    args = ap.parse_args(argv)

    dirs = [(Path(args.new_dir), "new"), (Path(args.paper_dir), "paper-repro")]
    systems = load_systems([(d, o) for d, o in dirs if (d / "predictions").exists()], args.include, args.exclude)
    ind = {k: indicators(s["y_true"], s["y_pred"]) for k, s in systems.items()}
    point = {k: {m: float(v) for m, v in metrics_from_sums(ind[k].sum(0)).items()} for k in systems}

    ref = args.ref
    if ref is None:
        for cand in [k for k in systems if k.startswith("dlf_full")] + ["tfidf_logistic_weighted_recall", "tfidf_logistic_weighted"]:
            if cand in systems:
                ref = cand
                break
        else:
            ref = max(point, key=lambda k: point[k]["macro_f1"])
    if ref not in systems:
        raise SystemExit(f"--ref {ref!r} not found. Available keys:\n  " + "\n  ".join(sorted(systems)))
    rng = np.random.default_rng(args.seed)
    others = [k for k in systems if k != ref]

    rows = []
    for k in others:
        bs = paired_bootstrap(ind[ref], ind[k], args.B, rng)
        b, c, p_mc = mcnemar_exact(ind[ref][:, 0], ind[k][:, 0])
        rows.append({"key": k, "system": systems[k]["label"], "origin": systems[k]["origin"],
                     "acc": point[k]["accuracy"], "f1_pos": point[k]["f1_pos"], "recall_pos": point[k]["recall_pos"], "macro_f1": point[k]["macro_f1"],
                     **{f"d_{m}": bs[m][0] for m in METRICS}, **{f"lo_{m}": bs[m][1] for m in METRICS},
                     **{f"hi_{m}": bs[m][2] for m in METRICS}, **{f"p_{m}": bs[m][3] for m in METRICS},
                     "mcnemar_b": b, "mcnemar_c": c, "p_mcnemar": p_mc})
    for m in METRICS:
        adj = holm([r[f"p_{m}"] for r in rows])
        for r, a in zip(rows, adj):
            r[f"p_{m}_holm"] = a
    adj = holm([r["p_mcnemar"] for r in rows])
    for r, a in zip(rows, adj):
        r["p_mcnemar_holm"] = a
    rows.sort(key=lambda r: -r["macro_f1"])

    # ---- markdown
    rl = systems[ref]["label"]
    print(f"Reference: **{rl}**  (acc {point[ref]['accuracy']:.4f}, F1+ {point[ref]['f1_pos']:.4f}, "
          f"recall+ {point[ref]['recall_pos']:.4f}, macro-F1 {point[ref]['macro_f1']:.4f}); "
          f"n = {len(ind[ref])} test messages; paired bootstrap B = {args.B}; Holm-corrected p-values; "
          f"deltas are reference minus system, in percentage points.\n")
    print("| System | Acc | ΔAcc [95% CI] | ΔF1+ [95% CI] | p(ΔF1+) | ΔRecall+ [95% CI] | p(ΔRec+) | McNemar b/c | p(McNemar) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['system']} | {r['acc']:.4f} | {fmt_ci(r['d_accuracy'], r['lo_accuracy'], r['hi_accuracy'])} | "
              f"{fmt_ci(r['d_f1_pos'], r['lo_f1_pos'], r['hi_f1_pos'])} | {r['p_f1_pos_holm']:.3g}{stars(r['p_f1_pos_holm'])} | "
              f"{fmt_ci(r['d_recall_pos'], r['lo_recall_pos'], r['hi_recall_pos'])} | {r['p_recall_pos_holm']:.3g}{stars(r['p_recall_pos_holm'])} | "
              f"{r['mcnemar_b']}/{r['mcnemar_c']} | {r['p_mcnemar_holm']:.3g}{stars(r['p_mcnemar_holm'])} |")

    # ---- files
    tdir = Path(args.tables_dir); tdir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", ref)[:40] + args.suffix
    pd.DataFrame(rows).to_csv(tdir / f"significance_{slug}.csv", index=False)
    tex = [f"% AUTO-GENERATED by binary-classifier/baselines/significance.py; reference = {rl}; B={args.B}; Holm-corrected",
           r"\begin{table*}[t]", r"\centering",
           f"\\caption{{Paired comparison of every filtering method against {rl} on the {len(ind[ref])} shared test messages. "
           r"$\Delta$ = reference minus method in percentage points, with 95\% paired-bootstrap confidence intervals "
           f"({args.B:,} resamples); $p$-values are Holm-corrected across the {len(rows)} comparisons. "
           r"McNemar $b$/$c$ = messages only the reference / only the method classifies correctly. "
           r"$^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}",
           f"\\label{{{args.label}}}", r"\resizebox{\textwidth}{!}{%",
           r"\begin{tabular}{@{}lccccccc@{}}", r"\toprule",
           r"\textbf{Method} & \textbf{Acc.} & $\Delta$\textbf{Acc.} [95\% CI] & $\Delta$\textbf{F1}$_{+}$ [95\% CI] & $p(\Delta$\textbf{F1}$_{+})$ & "
           r"$\Delta$\textbf{Recall}$_{+}$ [95\% CI] & \textbf{McNemar} $b/c$ & $p$\textbf{(McNemar)} \\", r"\midrule"]
    for r in rows:
        tex.append(f"{r['system']} & {r['acc']:.3f} & {fmt_ci(r['d_accuracy'], r['lo_accuracy'], r['hi_accuracy'])} & "
                   f"{fmt_ci(r['d_f1_pos'], r['lo_f1_pos'], r['hi_f1_pos'])} & {r['p_f1_pos_holm']:.3f}$^{{{stars(r['p_f1_pos_holm'])}}}$ & "
                   f"{fmt_ci(r['d_recall_pos'], r['lo_recall_pos'], r['hi_recall_pos'])} & {r['mcnemar_b']}/{r['mcnemar_c']} & "
                   f"{r['p_mcnemar_holm']:.3f}$^{{{stars(r['p_mcnemar_holm'])}}}$ \\\\")
    tex += [r"\bottomrule", r"\end{tabular}%", "}", r"\end{table*}"]
    (tdir / f"significance_{slug}.tex").write_text("\n".join(tex) + "\n")
    markers = {r["key"]: {"label": r["system"], "sig_f1_holm": r["p_f1_pos_holm"] < args.alpha,
                          "sig_mcnemar_holm": r["p_mcnemar_holm"] < args.alpha,
                          "direction": "ref_better" if r["d_f1_pos"] > 0 else "method_better"} for r in rows}
    (tdir / f"significance_markers{args.suffix}.json").write_text(json.dumps({"reference": ref, "alpha": args.alpha, "markers": markers}, indent=2))
    print(f"\nwrote {tdir / f'significance_{slug}.tex'}, .csv and significance_markers.json")

    # ---- all-pairs McNemar matrix
    if args.all_pairs:
        keys = list(systems)
        pairs = [(i, j) for i in range(len(keys)) for j in range(i + 1, len(keys))]
        praw = [mcnemar_exact(ind[keys[i]][:, 0], ind[keys[j]][:, 0])[2] for i, j in pairs]
        padj = holm(praw)
        M = pd.DataFrame(np.nan, index=[systems[k]["label"] for k in keys], columns=[systems[k]["label"] for k in keys])
        for (i, j), p in zip(pairs, padj):
            M.iat[i, j] = M.iat[j, i] = p
        M.to_csv(tdir / "significance_allpairs_mcnemar_holm.csv")
        nsig = sum(p < args.alpha for p in padj)
        print(f"all-pairs McNemar (Holm over {len(pairs)} pairs): {nsig} significant at alpha={args.alpha}; "
              f"matrix -> {tdir / 'significance_allpairs_mcnemar_holm.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
