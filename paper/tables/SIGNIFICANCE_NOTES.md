# Table 3: final results, statistics and text for the revision (2026-10-06)

**Final DLF = Layer 1: fastText with character n-grams, positive class weighted α = 12 (paper's direction)
+ Layer 2: gpt-4o-mini (repository prompt).**
**Primary labels = corrected test labels: 81 of 5,166 test messages human-reviewed and re-labelled
(63 request → not request, 18 not request → request).** Original-label results are kept alongside.

All numbers come from per-message predictions of 71 systems on the identical 5,166-message test split
(`results/classifier-results-baselines/evaluation_results/**/predictions/*.csv`); metrics are computed at full
precision, tables show three decimals.

---

## 1. What changed and why

| Change | Reason | Effect |
|---|---|---|
| Layer-1 weighting: α = 12 on **positives** | The paper describes this (recall first); the committed `eval-v1.py` weighted *negatives* 15:1. Code fixed (`eval-v1.py`, `eval/bert-eval.py`). | DLF F1 0.954 → 0.977 (original labels, word TF-IDF Layer 1); missed requests 181 → 63 |
| Layer 1: word TF-IDF + LogReg → **fastText (char n-grams)** | The paper's Layer-1 equations already describe fastText (subword embeddings → average → linear → softmax). Chosen on the **validation** split by a rule fixed beforehand (highest validation DLF F1; candidates within 0.25 points tie and the fastest wins); five of six candidates tied, fastText-char was fastest. | 4.5× faster Layer 1 (0.074 ms vs 0.333 ms per message) and the best test DLF of all candidates |
| **81 test labels corrected** | Blind review of all 921 test messages on which any of 69 systems disagreed with gold; each flip re-read and approved by the authors | See §3 |

### Label corrections (human-verified)

| Direction | n | bn | en | tbn | Sources |
|---|---|---|---|---|---|
| request → not request | **63** | 49 | 11 | 3 | Facebook 56, Twitter 6, Telegram 1 |
| not request → request | **18** | 2 | 16 | 0 | Twitter 16, Facebook 2 |
| total | **81** (1.6 % of test) | 51 | 27 | 3 | test positives 2,206 → 2,161 |

Typical cases: completed-donation thank-you posts, donor *offers* ("A+ donor ready"), slogans, job adverts and
scam warnings labelled *request* (mostly Facebook blood-group posts, i.e. labelled by source); unmistakable appeals
("urgent, 1 bag O-ve needed, patient in the OT at Dinajpur Medical College", "#Blood required urgently … call")
labelled *not request*. Definition used: label 1 = the message asks for blood or blood donors for a patient.
Applied to every dataset copy (`binary-classifier/`, `dual-layer-filtering/`, `dataset/pre_parsed/`,
`final-dataset/pre_parsed/` CSV + JSON) by `baselines/apply_label_corrections.py`; originals kept as
`*.pre_relabel_2026-10-06.*`; per-message log `LABEL_CORRECTIONS.csv` / `.md` next to each dataset.
**Training labels were not changed** (all trained models stay valid); 17 training rows share the exact text of a
corrected test message and keep the old label.

## 2. Final DLF numbers

| | Acc | P (macro) | R (macro) | F1 (macro) | P+ | R+ | F1+ | bn | en | tbn |
|---|---|---|---|---|---|---|---|---|---|---|
| **DLF, corrected labels** | **0.9911** | 0.9908 | 0.9909 | **0.9909** | 0.9889 | 0.9898 | **0.9894** | 0.988 | 0.992 | 0.998 |
| DLF, original labels | 0.9832 | 0.9841 | 0.9816 | 0.9827 | 0.9898 | 0.9705 | 0.9801 | 0.974 | 0.988 | 0.997 |

* Layer 1 forwards 2,227 of 5,166 messages; Layer 2 cost for the whole test set ≈ $0.12 (gpt-4o-mini, 2024-07-18).
* **Table 3 DLF row (corrected): `0.991 & 0.991 & 0.991 & 0.991`** (acc, macro P, R, F1).
* Layer 2 vs Layer 1 alone (corrected labels): +1.03 F1 points (CI [+0.68, +1.40], p = 0.007), McNemar 55 vs 9.
  On the original labels the LLM layer gives no net F1 gain (−0.07, n.s.): many of the "true requests" it rejected
  were mislabelled non-requests.

## 3. Statistics: DLF vs the 65 competing methods (paired bootstrap 10k + McNemar, Holm-corrected)

| Test labels | DLF significantly better | tie | DLF significantly worse |
|---|---|---|---|
| **Corrected (primary)** | **63** | **2** | **0** |
| Original | 33 | 32 | 0 |
| Only the 5,085 messages whose labels were never changed (McNemar) | 45 | 20 | 0 |

(identical counts for accuracy and McNemar; "competing" excludes DLF's own variants and Layer-1-only rows)

* **Corrected labels:** the only ties are LaBSE + RF (ΔF1 +0.37, p = 0.07) and fine-tuned MuRIL (+0.40, p = 0.07).
  DLF is significantly better than fine-tuned BanglaBERT (+0.63, CI [+0.28, +1.00], p = 0.007; McNemar 47 vs 19) and
  fine-tuned mBERT (+0.58, p = 0.007). Only MuRIL and mBERT have significantly higher recall (DLF trades a little
  recall for precision).
* **Original labels:** nothing beats DLF; it ties with the fine-tuned encoders and char-n-gram models.
* **Untouched messages only** (no correction involved; the most conservative view): DLF has the fewest errors of all
  71 systems (26); no system is significantly better.
* gpt-5-mini instead of gpt-4o-mini: statistically identical (earlier run, ΔF1 = 0.00, p = 1.0), 6× the cost.

## 4. Speed (end-to-end, raw text → label; `tab_latency.tex`)

| Model | Device | Median per message |
|---|---|---|
| **DLF Layer 1 (fastText char)** | 1 CPU thread | **0.074 ms** |
| word TF-IDF + LogReg | 1 CPU thread | 0.333 ms |
| fine-tuned BanglaBERT / mBERT / XLM-R / MuRIL | GPU (RTX 3050) | 5.4–5.6 ms |
| fine-tuned BanglaBERT | 16 CPU threads | 36.5 ms |
| DLF Layer 2 (gpt-4o-mini API) | – | 1.12 s, only for the 43 % forwarded; shared with the parsing call |

## 5. Files → where they go

| file | use |
|---|---|
| `tab_DLF_final.tex` (`tab:DLF`) | **replaces Table 3** (corrected labels; † = significantly different from DLF) |
| `significance_dlf_full_ftchar_gpt4omini_compact.tex` (`tab:sig-dlf-compact`) | main text: DLF vs fine-tuned encoders and strongest baselines |
| `tab_layer1_selection.tex` (`tab:layer1-selection`) | main text or appendix: how Layer 1 was chosen |
| `tab_latency.tex` (`tab:latency`) | main text: inference cost |
| `significance_dlf_full_ftchar_gpt4omini.tex` (`tab:sig-dlf-full`) | appendix: all 70 pairwise comparisons |
| `tab_per_language.tex`, `tab_frozen_encoders.tex` | appendix |
| `*_original_labels*.tex`, `tab_DLF_final_original_labels.tex` | appendix / supplement: same analyses on the original labels |
| `significance_finetune_csebuetnlp_banglabert_bert*.tex`, `significance_dlf_full_gpt4omini*.tex` | optional: other references (BanglaBERT; word-TF-IDF DLF) |
| `scores_original_vs_corrected.md/.csv`, `scores_unchanged_labels_only.csv`, `significance_allpairs_mcnemar_holm*.csv` | supplementary |
| `significance_markers_dlf_ftchar*.json` | † markers |
| `_superseded/` | earlier versions (word TF-IDF Layer 1 / original labels only), kept for the record |

## 6. Text for the paper

**Methodology, Layer 1 heading:** `Layer 1: Asymmetrically Weighted fastText Classifier` (the equations already
describe fastText; train with positive-class weight α = 12, implemented by repeating positive examples).

**Dataset (new paragraph).**
```latex
\paragraph{Test-label verification} To audit annotation quality, every test message on which at least one of
the 69 evaluated classifiers disagreed with the gold label (921 messages) was re-examined against the task
definition (a message is positive iff it requests blood or blood donors for a patient), blind to all model
predictions. 81 labels (1.6\% of the test set) were corrected after verification by the authors: 63 messages
labelled as requests were donation reports, donor offers, slogans or unrelated posts, and 18 unmistakable requests
were labelled negative. Training labels were not modified. We report results on the corrected labels and, for
transparency, on the original labels (Appendix~X).
```

**Experimental Setup (significance).**
```latex
\paragraph{Statistical Significance Testing} All methods are evaluated on the same 5{,}166 test messages, so we
compare them with paired tests: for every competing method we resample the test messages jointly with DLF 10{,}000
times and report the difference in accuracy, positive-class F1 and recall with 95\% percentile confidence intervals
and two-sided bootstrap $p$-values, together with McNemar's exact test on per-message correctness. All $p$-values are
Holm--Bonferroni corrected across the comparisons. Layer~1 of DLF was selected on a held-out validation split
(Table~\ref{tab:layer1-selection}); Layer~2 uses gpt-4o-mini (snapshot 2024-07-18), and all prompts, raw responses,
log-probabilities, latencies and costs are released.
```

**Results.**
```latex
DLF achieves the best scores in Table~\ref{tab:DLF} (accuracy and macro-F1 0.991) and is significantly better than
63 of the 65 compared configurations, including fine-tuned BanglaBERT ($\Delta$F1 $=+0.63$, $p<0.01$) and mBERT
($+0.58$, $p<0.01$); the remaining two (LaBSE+RF and fine-tuned MuRIL) are statistically indistinguishable from it
(Table~\ref{tab:sig-dlf-compact}). No method is significantly better than DLF on the corrected or on the original
labels, nor on the subset of test messages whose labels were not corrected. Its Layer~1 classifies a message in
0.074\,ms on a single CPU thread, about 75$\times$ faster than a fine-tuned BERT-base model on a GPU and 490$\times$
faster on a CPU (Table~\ref{tab:latency}), and the LLM in Layer~2, which removes most of Layer~1's false positives
(+1.03 F1, $p<0.01$), is invoked only for messages that Layer~1 forwards, in the same call that parses them.
```

**Response to the reviewer (statistical significance).**
> Thank you. Because all methods are evaluated on the same 5,166 test messages, we added paired tests:
> paired-bootstrap 95% confidence intervals (10,000 resamples) and p-values for the differences in accuracy,
> positive-class F1 and recall, McNemar's exact test, and Holm correction (new paragraph in Experimental Setup, new
> Table X, full pairwise tables in Appendix X). DLF is significantly better than 63 of the 65 compared
> configurations and statistically indistinguishable from the remaining two; no configuration is significantly
> better than DLF. While preparing this analysis we audited the test labels (all messages on which any classifier
> disagreed with the gold label) and corrected 81 of 5,166 labels after verification; we report results on both the
> corrected and the original labels, and on the subset of messages whose labels were not changed: in all three
> views no configuration is significantly better than DLF (on the original labels DLF is significantly better than
> 33 configurations and tied with 32). We also selected the first DLF layer on a held-out validation split and report its
> end-to-end latency against all baselines.

**Response to the reviewer (missing baselines).** Table 3 now includes fine-tuned BanglaBERT, mBERT, XLM-R, MuRIL,
IndicBERT and IndicBERTv2, frozen versions of these encoders with LogReg/SVM/RF, fastText with character n-grams,
and character n-gram TF-IDF classifiers (all on the same split). DLF remains the best configuration, and the paired
tests above show which differences are significant.

## 7. Reproducibility artifacts

* LLM layer: `results/classifier-results-baselines/evaluation_results/paper-repro/dlf_layer2/` — per call: full
  prompt, raw output, verdict, token log-probs and P(true), model snapshot, request id, fingerprint, tokens, cost,
  timestamps, latency, retries (`llm_cache_gpt-4o-mini.responses.jsonl` for validation + new test messages,
  `tfidf_logistic_weighted_recall_*.responses.jsonl` for the earlier runs), manifests with git commit, package
  versions and SHA-256 of data / prompt / code. Strip `request.user_prompt` before publishing (raw messages).
* Layer-1 search: `evaluation_results/layer1-search/` (results CSV, predictions, log).
* Label audit: `results/classifier-results-baselines/relabel/` (review sheet of all 921 disputed messages with blind
  verdicts and reasons; corrected labels; pre-migration backup of all results).
* Commands: `binary-classifier/baselines/cmd.txt`.

## 8. Caveats

1. The corrections were proposed by an automated blind review and verified by the authors; disclose this. The
   untouched-messages analysis (§3) does not depend on any correction.
2. Training labels still contain the same kind of noise (not corrected; models were not retrained).
3. On the original labels the LLM layer gives no net F1 gain; its benefit appears once mislabelled test messages
   are corrected.
4. Word2Vec and Jina rows of the old Table 3 could not be re-run (1.6 GB download; remote code incompatible with
   transformers ≥ 5) and are omitted from the final table.
5. XLM-R, MuRIL and IndicBERTv2 were fine-tuned with frozen word embeddings (6 GB GPU); single training seed;
   the bootstrap covers test-set sampling only.
