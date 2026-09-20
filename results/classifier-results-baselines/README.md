# Additional baselines for Table 3 (tab:DLF)

Produced 2026-09-21 with `binary-classifier/baselines/` on the paper's exact test split
(`binary-classifier/pre_parsed_dataset.csv`, shuffle rs=42, 80/20 split rs=42, 5,166 test messages:
2,042 bn / 2,488 en / 636 tbn). Metrics: accuracy and macro-averaged P/R/F1 from
`classification_report(y_true, y_pred)`. Per-language columns are accuracy on that slice.
Hardware: RTX 3050 Laptop 6 GB, bf16, seed 42. Full per-run details (confusion matrix, hyper-parameters,
parameter counts, single-message latency, environment) are in `evaluation_results/*.json`;
the run ledger is `evaluation_results/_manifest.jsonl`; logs are in `evaluation_results/logs/`.

## Fine-tuned encoders (3 epochs, lr 2e-5, max 128 tokens, best epoch on a 10% val slice of train)

| Model | Params | Acc | F1 (macro) | bn | en | tbn | Note |
|---|---|---|---|---|---|---|---|
| **BanglaBERT** (csebuetnlp/banglabert) | 110M | **0.987** | **0.987** | 0.982 | 0.988 | 0.998 | full fine-tune, csebuetnlp normaliser |
| mBERT (bert-base-multilingual-cased) | 178M | 0.987 | 0.986 | 0.978 | 0.991 | 0.997 | full fine-tune |
| IndicBERT v1 (ai4bharat/indic-bert, ALBERT) | 33M | 0.985 | 0.985 | 0.978 | 0.988 | 0.998 | full fine-tune, gated repo |
| XLM-R base | 278M | 0.985 | 0.985 | 0.977 | 0.988 | 0.998 | word embeddings frozen (6 GB GPU) |
| DistilBERT multilingual (sanity re-run) | 135M | 0.985 | 0.985 | 0.975 | 0.990 | 0.997 | paper row: 0.985 -> harness reproduces it |
| MuRIL base | 237M | 0.985 | 0.984 | 0.976 | 0.988 | 0.998 | word embeddings frozen (6 GB GPU) |
| IndicBERT v2 (IndicBERTv2-MLM-only) | 278M | 0.983 | 0.983 | 0.975 | 0.987 | 0.995 | word embeddings frozen (6 GB GPU) |

## Lexical / fastText (CPU)

| Model | Acc | F1 (macro) | bn | en | tbn | Inference s/msg |
|---|---|---|---|---|---|---|
| Char n-gram (2-5) TF-IDF + SVM | 0.985 | 0.985 | 0.977 | 0.989 | 0.997 | 2.9e-3 |
| Char n-gram TF-IDF + RF | 0.985 | 0.984 | 0.976 | 0.990 | 0.994 | 4.2e-5 |
| Char n-gram TF-IDF + LogReg | 0.981 | 0.981 | 0.974 | 0.985 | 0.992 | 2.3e-6 |
| Word+char TF-IDF + SVM | 0.986 | 0.986 | 0.976 | 0.991 | 0.997 | 3.8e-3 |
| fastText, char n-grams (minn 2, maxn 5, word bigrams) | 0.982 | 0.982 | 0.973 | 0.987 | 0.994 | 7.5e-5 |
| fastText, word only (ablation) | 0.981 | 0.981 | 0.972 | 0.986 | 0.991 | 1.4e-5 |
| *(paper)* word TF-IDF + LogReg | 0.977 | 0.977 | | | | 1.3e-7 |

## Frozen encoder -> mean-pooled embedding -> classifier (same protocol as the LaBSE / E5 rows)

Best classifier per encoder: IndicBERT v2 + SVM 0.980, mBERT + SVM 0.978, MuRIL + RF 0.978,
XLM-R + RF 0.977, BanglaBERT + RF 0.972, IndicBERT v1 + SVM 0.972. All are below the paper's
LaBSE / E5 rows (0.98) and well below fine-tuning; raw MLM/ELECTRA encoders are not sentence
encoders. Full rows are in `../../paper/tables/baselines_all.csv`.

## What this says

* Every reasonable model, from a 3-second char-TF-IDF LogReg to a fully fine-tuned BanglaBERT,
  lands between 0.981 and 0.987 accuracy. The task is saturated at the message level, as the
  reviewer suspected; the new rows make that explicit instead of leaving it implied.
* The best new model (BanglaBERT, 0.987) beats the paper's DistilBERT row by 0.2 points and the
  word-TF-IDF LogReg row by 1.0 point, at ~4 orders of magnitude higher per-message cost.
* Bengali is the hardest slice for every model (0.972-0.982) while transliterated Bengali is the
  easiest (0.99+), which is worth a sentence in the analysis.
* Character n-grams are the cheap win for this data: char TF-IDF + LogReg (0.981) > word TF-IDF +
  LogReg (0.977), and fastText char n-grams > fastText word-only.

## Caveats to state in the paper

* XLM-R, MuRIL and IndicBERT v2 have 250k-token vocabularies; their word-embedding matrices were
  frozen during fine-tuning to fit a 6 GB GPU (`extra.embeddings_frozen = true` in the JSON).
  Re-run with `--freeze-embeddings never` on a >= 10 GB GPU for full fine-tuning.
* Fine-tuned rows use dynamic padding at 128 tokens; the old DistilBERT/MobileBERT rows used fixed
  512-token padding, so their inference times are ~10x higher for the same model class.
* Single seed (42). With 5,166 test messages, one message = 0.02 points; differences under ~0.3
  points are within noise.

## Reproduce / extend

```bash
cd binary-classifier
python -m baselines.run --tags core          # everything above except gated/extra
python -m baselines.aggregate --include-paper
```
See `binary-classifier/baselines/cmd.txt` for every command.
