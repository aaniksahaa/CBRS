"""Apply the human-verified test-label corrections to every copy of the classification dataset.

The corrections (results/classifier-results-baselines/relabel/test_labels_corrected.csv) re-adjudicate 81 of the
5,166 test messages of the paper split (63 request -> not request, 18 not request -> request). They were proposed by
a blind review of every test message on which at least one of 69 classifiers disagreed with the original label
(text only; no predictions, labels or sources shown), each proposed flip was re-read, and all 81 were approved by
the authors on 2026-10-06. TRAINING rows are not changed (17 training rows share the exact text of a corrected test
message and keep their original label), so every trained model stays valid.

    cd binary-classifier && python -m baselines.apply_label_corrections            # --dry-run to only verify

Each target file is backed up as <name>.pre_relabel_2026-10-06<ext> (only once) and a LABEL_CORRECTIONS.csv/.md
log is written next to it. Row identity is verified before any change; the script refuses to write on any mismatch
and is idempotent (re-running on corrected files changes nothing).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
CORR = REPO / "results/classifier-results-baselines/relabel/test_labels_corrected.csv"
REVIEW = REPO / "results/classifier-results-baselines/relabel/review_sheet_disputed_921.csv"
TAG = "pre_relabel_2026-10-06"
CSV_TARGETS = ["binary-classifier/pre_parsed_dataset.csv", "binary-classifier/dual-layer-filtering/pre_parsed_dataset.csv",
               "dataset/pre_parsed/pre_parsed_dataset.csv", "final-dataset/pre_parsed/pre_parsed_dataset.csv"]
JSON_TARGETS = ["dataset/pre_parsed/pre_parsed_merged.json", "final-dataset/pre_parsed/pre_parsed_merged.json"]


def norm(t: str) -> str:
    """Comparable text across the raw and the contact-anonymised copies (drop digits / placeholders / spaces)."""
    t = re.sub(r"[\dX]", "", str(t))  # the anonymiser replaces (Bengali or ASCII) phone digits with X; applied to both sides
    t = re.sub(r"<[^>]{1,20}>|\[[^\]]{1,20}\]", "", t)
    return re.sub(r"\s+", "", t)


def csv_writer(p: Path, df: pd.DataFrame):
    """Return kwargs for DataFrame.to_csv that reproduce the file byte-for-byte (line endings differ between copies)."""
    import io
    orig = p.read_bytes()
    for lt in ("\n", "\r\n"):
        buf = io.StringIO()
        df.to_csv(buf, index=False, lineterminator=lt)
        if buf.getvalue().encode("utf-8") == orig:
            return {"lineterminator": lt}
    raise SystemExit(f"{p}: cannot reproduce the original bytes with pandas; refusing to rewrite it")


def json_dump(p: Path, data) -> bytes:
    """Serialise like the original file (indent 2, raw Unicode, LF or CRLF); verified on the unmodified data first."""
    orig = p.read_bytes()
    base = json.loads(orig.decode("utf-8"))
    for nl in ("\n", "\r\n"):
        for trail in ("", nl):
            if (json.dumps(base, ensure_ascii=False, indent=2).replace("\n", nl) + trail).encode("utf-8") == orig:
                return (json.dumps(data, ensure_ascii=False, indent=2).replace("\n", nl) + trail).encode("utf-8")
    raise SystemExit(f"{p}: cannot reproduce the original bytes; refusing to rewrite it")


def backup(p: Path) -> Path:
    b = p.with_name(f"{p.stem}.{TAG}{p.suffix}")
    if not b.exists():
        shutil.copy2(p, b)
    return b


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    C = pd.read_csv(CORR)
    ch = C[C["changed"]].copy()
    assert "csv_row" in ch, "test_labels_corrected.csv lacks csv_row"
    reasons = {}
    if REVIEW.exists():
        R = pd.read_csv(REVIEW)
        reasons = dict(zip(R["idx"], R["blind_reason"]))
    raw = pd.read_csv(REPO / CSV_TARGETS[0])
    raw_text = {int(r): str(raw.at[int(r), "text"]) for r in ch["csv_row"]}

    log = ch[["idx", "csv_row", "label_original", "label_corrected", "message_sha256"]].rename(columns={"idx": "test_position"})
    log["direction"] = log["label_original"].map({1: "request -> not request", 0: "not request -> request"})
    log["reason"] = log["test_position"].map(reasons)
    log["verified_by"] = "authors (human review), 2026-10-06"

    for rel in CSV_TARGETS:
        p = REPO / rel
        df = pd.read_csv(p)
        assert len(df) == len(raw), f"{rel}: row count differs"
        for r in ch["csv_row"]:
            r = int(r)
            assert norm(df.at[r, "text"]) == norm(raw_text[r]), f"{rel}: row {r} is not the same message"
        cur = df.loc[ch["csv_row"], "label"].to_numpy()
        todo = (cur != ch["label_corrected"].to_numpy()).sum()
        already = (cur == ch["label_corrected"].to_numpy()).all()
        assert already or (cur == ch["label_original"].to_numpy()).all(), f"{rel}: labels are neither original nor corrected"
        print(f"{rel}: {todo} labels to change{' (already corrected)' if already else ''}")
        fmt = csv_writer(p, df)  # verified byte-exact before any change
        if not args.dry_run and todo:
            backup(p)
            df.loc[ch["csv_row"].to_numpy(), "label"] = ch["label_corrected"].to_numpy()
            df.to_csv(p, index=False, **fmt)
        if not args.dry_run:
            log.to_csv(p.parent / "LABEL_CORRECTIONS.csv", index=False)

    for rel in JSON_TARGETS:
        p = REPO / rel
        data = json.loads(p.read_bytes().decode("utf-8"))
        json_dump(p, data)  # verified byte-exact before any change
        assert len(data) == len(raw), f"{rel}: item count differs"
        todo = 0
        for r, new in zip(ch["csv_row"].astype(int), ch["label_corrected"].astype(int)):
            assert norm(data[r]["text"]) == norm(raw_text[r]), f"{rel}: item {r} is not the same message"
            if bool(data[r]["is_blood_donation_request"]) != bool(new):
                todo += 1
                data[r]["is_blood_donation_request"] = bool(new)
                data[r].setdefault("metadata", {})["label_corrected_2026_10_06"] = True
        print(f"{rel}: {todo} labels to change")
        if not args.dry_run and todo:
            out = json_dump(p, data)
            backup(p)
            p.write_bytes(out)
        if not args.dry_run:
            log.to_csv(p.parent / "LABEL_CORRECTIONS.csv", index=False)

    if not args.dry_run:
        md = (f"# Test-label corrections (2026-10-06)\n\n"
              f"81 of the 5,166 messages in the paper's classification test split were re-labelled after human review:\n"
              f"**63 request -> not request** and **18 not request -> request** (test positives 2,206 -> 2,161).\n\n"
              f"Procedure: every test message on which at least one of 69 classifiers disagreed with the original label (921)\n"
              f"was re-read blind (text only, no labels or predictions) against a fixed definition (label 1 = the message asks\n"
              f"for blood or blood donors for a patient). Each proposed flip was re-read and all 81 were verified and approved\n"
              f"by the authors. Training rows were not changed (17 training rows share the exact text of a corrected test message).\n"
              f"Per-message log: LABEL_CORRECTIONS.csv (row index, test position, old/new label, reason). Originals: *.{TAG}.*\n")
        for d in {(REPO / t).parent for t in CSV_TARGETS + JSON_TARGETS}:
            (d / "LABEL_CORRECTIONS.md").write_text(md)
    print("dry run - nothing written" if args.dry_run else "done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
