DLF (fastText L1 + gpt-4o-mini) vs the 47 configurations of Table 3. Win/loss = paired-bootstrap F1+ difference significant significant (Holm over 47). Δ = DLF − method, percentage points.

| Family | # | Strongest config | F1+ | ΔF1+ [95% CI] (corrected) | p | W/T/L corrected | ΔF1+ original | W/T/L original |
|---|---|---|---|---|---|---|---|---|
| Word TF-IDF | 4 | TF-IDF + RF | 0.9818 | +0.76 [+0.40, +1.13] | 0.005 | 4/0/0 | +0.20 (p=1.000) | 2/2/0 |
| Count | 4 | Count + RF | 0.9816 | +0.78 [+0.43, +1.14] | 0.005 | 4/0/0 | +0.17 (p=1.000) | 1/3/0 |
| Char TF-IDF | 4 | Char TF-IDF + LogReg | 0.9841 | +0.52 [+0.20, +0.86] | 0.008 | 4/0/0 | +0.19 (p=1.000) | 1/3/0 |
| Word+Char TF-IDF | 4 | W+C TF-IDF + SVM | 0.9844 | +0.50 [+0.18, +0.83] | 0.008 | 4/0/0 | -0.33 (p=0.823) | 1/3/0 |
| fastText | 2 | char $n$-grams | 0.9805 | +0.88 [+0.55, +1.22] | 0.005 | 2/0/0 | +0.00 (p=1.000) | 0/2/0 |
| Sentence embeddings$^{a}$ | 21 | LaBSE + RF | 0.9856 | +0.37 [+0.06, +0.70] | 0.036 | 21/0/0 | +0.28 (p=1.000) | 15/6/0 |
| Fine-tuned BanglaBERT | 1 | BanglaBERT | 0.9831 | +0.63 [+0.28, +1.00] | 0.005 | 1/0/0 | -0.47 (p=0.216) | 0/1/0 |
| Fine-tuned mBERT | 1 | mBERT | 0.9835 | +0.58 [+0.24, +0.95] | 0.005 | 1/0/0 | -0.52 (p=0.095) | 0/1/0 |
| Fine-tuned XLM-R | 1 | XLM-R | 0.9806 | +0.87 [+0.49, +1.28] | 0.005 | 1/0/0 | -0.37 (p=1.000) | 0/1/0 |
| Fine-tuned MuRIL | 1 | MuRIL | 0.9854 | +0.40 [+0.05, +0.76] | 0.036 | 1/0/0 | -0.20 (p=1.000) | 0/1/0 |
| Fine-tuned IndicBERT | 1 | IndicBERT | 0.9815 | +0.79 [+0.43, +1.17] | 0.005 | 1/0/0 | -0.27 (p=1.000) | 0/1/0 |
| Fine-tuned IndicBERTv2 | 1 | IndicBERTv2 | 0.9817 | +0.76 [+0.40, +1.13] | 0.005 | 1/0/0 | -0.02 (p=1.000) | 0/1/0 |
| Fine-tuned DistilBERT | 1 | DistilBERT | 0.9833 | +0.61 [+0.25, +0.96] | 0.005 | 1/0/0 | -0.22 (p=1.000) | 0/1/0 |
| Fine-tuned MobileBERT | 1 | MobileBERT | 0.9814 | +0.80 [+0.44, +1.17] | 0.005 | 1/0/0 | +0.15 (p=1.000) | 0/1/0 |
| **All configurations** | 47 | | | | | **47/0/0** | | **20/27/0** |
