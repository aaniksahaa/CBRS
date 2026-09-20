# Baseline harness for the blood-request classifier

Adds the standard Bengali / multilingual text-classification baselines that were missing from
Table 3 (`tab:DLF` in `paper/main_arr.tex`): **BanglaBERT, mBERT, XLM-R, IndicBERT, MuRIL,
fastText with character n-grams**, plus a character n-gram TF-IDF baseline. Each model is
evaluated two ways, mirroring the two kinds of rows already in the table:

* **fine-tuned end-to-end** (`*_ft`, like the DistilBERT / MobileBERT rows), and
* **frozen encoder → sentence embedding → LogReg / SVM / RF** (`*_emb`, like the LaBSE / E5 rows).

Nothing existing is touched: results go to a *new* directory
`results/classifier-results-baselines/evaluation_results/` and the paper table is only extended
via a generated snippet `paper/tables/baselines_rows.tex` that you paste (or `\input`) yourself.

## Comparability guarantees

* **Identical test set.** `data.py` reproduces the paper split byte-for-byte
  (`shuffle(random_state=42)` → `train_test_split(test_size=0.2, random_state=42)`; 20,664 train /
  5,166 test; the loader asserts the fingerprint and warns if a different CSV is used).
* **Same classifiers & hyper-parameters** as `models.py` for the embedding rows
  (`LogisticRegression(C=1)`, `SVC(kernel='linear', probability=True)`, `RF(100)`).
* **Same JSON schema** as `results/classifier-results-with-time/` (`vectorizer, model,
  embedding_model, accuracy, avg_inference_time_seconds, metrics`) so old and new files aggregate
  together. An `extra` block adds per-language accuracy (bn / en / tbn), confusion matrix,
  parameter count, train time, single-message latency, hyper-parameters and environment.
* **No test-set peeking for fine-tuning.** Best epoch is picked on a 10 % validation slice carved
  *from the training portion* (the old `bert-eval.py` used the test set as `eval_dataset`).
* Precision / recall are reported from `classification_report(y_true, y_pred)`. Note the old
  sklearn pipeline called `classification_report(y_pred, y_true)` (arguments swapped), which
  swaps precision and recall; at two decimals this rarely changes anything, but be aware of it if
  you regenerate the old rows.

## Verified on this laptop (RTX 3050 6 GB, 2026-09-21)

* The `distilbert_multilingual_ft` sanity re-run reproduces the paper's DistilBERT row
  (0.9849 vs 0.9851 accuracy), so new and old rows are comparable.
* **Large-vocabulary models (XLM-R, MuRIL, IndicBERTv2; 250k-token embedding matrices) do not
  fit fp32 AdamW on 6 GB**, so their `freeze_embeddings="low_vram"` setting freezes the word
  embedding matrix on GPUs < 10 GB (recorded in the JSON as `extra.embeddings_frozen`). On a
  ≥ 10 GB GPU they are fine-tuned fully; force either way with `--freeze-embeddings never|always`.
* Inference times of the new fine-tuned rows are ~10x lower than the old DistilBERT/MobileBERT
  rows because the harness uses dynamic padding at 128 tokens instead of fixed 512-token padding;
  compare fine-tuned rows with each other, not with the two old ones.
* `ai4bharat/indic-bert` (v1) is a gated repo: request access on its page, then `hf auth login`.
* Downloads: `HF_HUB_DISABLE_XET=1` is set automatically (Xet stalled on a slow link).

## Quick start

```bash
cd binary-classifier
pip install -r baselines/requirements.txt          # torch / transformers / sklearn / fasttext / normalizer

python -m baselines.run --list                     # what is registered
python -m baselines.run --tags core --dry-run      # plan
python -m baselines.run --tags core --prefetch     # download weights only (≈4 GB), good on a fast link
python -m baselines.run --tags lex fasttext        # CPU rows, a few minutes
python -m baselines.run --tags emb                 # frozen embeddings + sklearn, GPU, minutes per model
python -m baselines.run --tags ft                  # fine-tuning, GPU, ~10-25 min per model on a 6 GB 3050
python -m baselines.run --baseline banglabert_ft --epochs 5 --lr 3e-5   # per-run overrides
python -m baselines.run --baseline mbert_ft --limit 512                 # 1-minute smoke test (-> out/smoke/)
python -m baselines.aggregate --include-paper      # markdown table + paper/tables/baselines_rows.tex + csv

# unattended, resumable, everything the reviewer asked for:
nohup bash baselines/run_all.sh > baselines_run_all.log 2>&1 &
```

Useful flags: `--device cuda:1`, `--out DIR`, `--cache-dir DIR` (checkpoints / cached embeddings,
default `~/.cache/cbrs-baselines`, override with `CBRS_BASELINE_CACHE`), `--save-model DIR`,
`--force`, `--classifiers logistic` (skip the slow SVM), `--precision bf16|fp16|fp32`,
`--batch-size`, `--grad-accum`, `--max-length`, `--seed`.

Each baseline runs in its own subprocess; per-baseline logs are in `<out>/logs/<name>.log` and a
run ledger in `<out>/_manifest.jsonl`. Already-finished baselines are skipped, so you can re-launch
the same command after an interruption or spread baselines across machines and just copy the
JSON files into one directory.

## Running on a remote GPU box

```bash
rsync -a binary-classifier/ user@gpu:~/cbrs/binary-classifier/      # code + pre_parsed_dataset.csv (8 MB)
ssh user@gpu 'cd ~/cbrs/binary-classifier && pip install -r baselines/requirements.txt && \
              nohup bash baselines/run_all.sh > run_all.log 2>&1 &'
# ... later
rsync -a user@gpu:~/cbrs/results/classifier-results-baselines/ results/classifier-results-baselines/
python -m baselines.aggregate --include-paper
```

With ≥ 12 GB VRAM also run `--tags large` (XLM-R large) and `--tags extra`
(BanglishBERT, word-only fastText ablation, word+char TF-IDF) and, after `hf auth login` with access
granted on the model page, `--tags gated` (IndicBERT v1, ALBERT); with lots of VRAM you
can raise `--batch-size 64 --grad-accum 1`.

## Adding a baseline

One entry in `registry.py`:

```python
BaselineSpec("bangla_bert_base_ft", "finetune", "sagorsarker/bangla-bert-base",
             model_id="sagorsarker/bangla-bert-base", tags=("ft", "extra", "bengali"))
```

`kind` is one of `finetune | embed | lexical | fasttext`; the runner, result naming, aggregation
and LaTeX row come for free. For a new *kind* of method, add a `run_<kind>` function and one
branch in `run.py::run_one`.

## Files

| file | role |
|---|---|
| `data.py` | paper-identical split (+ optional validation slice from train) |
| `registry.py` | **the list of baselines** and their hyper-parameters |
| `finetune.py` | HF `Trainer` fine-tuning, dynamic padding, bf16/fp16, best-epoch on val |
| `embed.py` | frozen encoder mean/CLS pooling → cached `.npz` → sklearn classifiers |
| `lexical.py` | char / word TF-IDF × sklearn, fastText supervised |
| `metrics.py` | metrics + JSON writer in the paper's schema |
| `run.py` | CLI / orchestration / prefetch / smoke test |
| `aggregate.py` | markdown + CSV + LaTeX rows for `tab:DLF` |
| `run_all.sh` | unattended end-to-end run |
| `cmd.txt` | copy/paste cheat-sheet of every command |
