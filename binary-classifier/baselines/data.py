"""Dataset loading that reproduces the paper's exact train/test split."""
from __future__ import annotations

import hashlib
import warnings
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

# The CSV the paper's classifier numbers were computed on.
DEFAULT_DATA = Path(__file__).resolve().parents[1] / "pre_parsed_dataset.csv"

SPLIT_SEED = 42
TEST_SIZE = 0.2
# Sanity fingerprint of the paper split (label counts of the 5,166-row test set).
EXPECTED_TEST_LABEL_COUNTS = {0: 2960, 1: 2206}
EXPECTED_TEST_INDEX_MD5 = "40630e29c4ef04420bbaa55a2865e7e3"


@dataclass
class Split:
    train: pd.DataFrame  # columns: text, label, language, source
    val: pd.DataFrame | None
    test: pd.DataFrame
    data_path: str
    matches_paper_split: bool

    def describe(self) -> str:
        s = f"data={self.data_path}\n"
        s += f"train={len(self.train)}  val={0 if self.val is None else len(self.val)}  test={len(self.test)}\n"
        s += f"test label counts={self.test['label'].value_counts().to_dict()}  "
        s += f"test languages={self.test['language'].value_counts().to_dict()}\n"
        s += f"matches_paper_split={self.matches_paper_split}"
        return s


def load_split(data_path: str | Path = DEFAULT_DATA, val_fraction: float = 0.0, seed: int = SPLIT_SEED) -> Split:
    """Load the CSV and split it exactly like `models.py` / `eval/bert-eval.py`.

    `val_fraction` (0..1) optionally carves a stratified validation set *out of
    the training portion* (used for model selection in fine-tuning) so that the
    test set stays byte-identical to the one behind the paper's Table 3.
    """
    data_path = Path(data_path)
    df = pd.read_csv(data_path)
    for col in ("language", "source"):
        if col not in df.columns:
            df[col] = "unknown"
    df["text"] = df["text"].astype(str)
    df = shuffle(df, random_state=SPLIT_SEED)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=TEST_SIZE, random_state=SPLIT_SEED
    )
    train = df.loc[X_train.index, ["text", "label", "language", "source"]].copy()
    test = df.loc[X_test.index, ["text", "label", "language", "source"]].copy()

    idx_md5 = hashlib.md5("|".join(map(str, X_test.index)).encode()).hexdigest()
    counts = test["label"].value_counts().to_dict()
    matches = counts == EXPECTED_TEST_LABEL_COUNTS and idx_md5 == EXPECTED_TEST_INDEX_MD5
    if not matches:
        warnings.warn(
            f"Test split does not match the paper split (label counts {counts}, index md5 {idx_md5}). "
            "Results will not be directly comparable to Table 3 unless you use the original CSV."
        )

    val = None
    if val_fraction and val_fraction > 0:
        train, val = train_test_split(
            train, test_size=val_fraction, random_state=seed, stratify=train["label"]
        )
    return Split(train=train.reset_index(drop=True),
                 val=None if val is None else val.reset_index(drop=True),
                 test=test.reset_index(drop=True),
                 data_path=str(data_path), matches_paper_split=bool(matches))
