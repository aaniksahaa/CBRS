# Statistical significance for Table 3 — FINAL (DLF = Layer 1 + gpt-4o-mini)

Generated 2026-10-06 by `binary-classifier/baselines/significance.py` from per-message predictions of
**69 systems on the identical 5,166-message test split** behind Table 3: DLF with gpt-4o-mini (the paper's
system), DLF with gpt-5-mini (ablation), the 35 new baseline rows, the paper's original rows re-run with the
repository code (TF-IDF, Count, 7 sentence-embedding models, DistilBERT, MobileBERT; Word2Vec and Jina not
re-runnable, see caveats) and the two DLF Layer-1-only variants. All metrics are computed at full precision;
two decimals appear only in LaTeX rows.

## 1. DLF results (re-run 2026-10-06, fully logged)

| System | Acc | P (macro) | R (macro) | F1 (macro) | P+ | R+ | F1+ | bn | en | tbn | LLM cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Layer 1 only (TF-IDF + LogReg, positives weighted 12:1) | 0.9710 | | | 0.9705 | 0.9446 | 0.9900 | 0.9668 | | | | – |
| **DLF = Layer 1 + gpt-4o-mini (paper)** | **0.9806** | **0.9810** | **0.9795** | **0.9802** | **0.9830** | **0.9714** | **0.9772** | 0.9706 | 0.9847 | 0.9969 | $0.126 |
| DLF = Layer 1 + gpt-5-mini (ablation) | 0.9806 | 0.9810 | 0.9794 | 0.9802 | 0.9835 | 0.9710 | 0.9772 | 0.9706 | 0.9847 | 0.9969 | $0.802 |

* Layer 1 forwards 2,312 of 5,166 test messages (45 %; real streams are far less positive-heavy).
  gpt-4o-mini **removes 91 of 128 false positives (71 %)** and **wrongly rejects 41 of 2,184 true positives
  (1.9 %)**; gpt-5-mini removes 92 and rejects 42. 0 API errors, 0 unparseable answers for both.
* Snapshots: `gpt-4o-mini-2024-07-18`, `gpt-5-mini-2025-08-07` (reasoning effort = API default; ~130
  hidden reasoning tokens per call, hence 6× the cost).
* **Table 3 DLF row:** `0.98 & 0.98 & 0.98 & 0.98` (acc, macro P, R, F1). The published
  `0.99 & 0.99 & 0.98 & 0.98` is not reproduced (it came from an unrecorded run; the committed `eval-v1.py`
  has the LLM branch disabled). Use the reproduced row — it has full artifacts and all tests refer to it.
* **Inference time:** the published DLF time (1.10 × 10⁻⁷ s) is Layer 1 alone. Including Layer 2 the average
  over all test messages is 0.51 s/message (mean API latency 1.15 s × 45 % forwarded). Report Layer 1 time
  and LLM latency separately and note that the amortised LLM cost scales with the forwarded fraction.

## 2. Procedure

Paired bootstrap (10,000 joint resamples of the 5,166 messages) → 95 % CI and two-sided p for
Δ = DLF − method in accuracy, positive-class F1, positive-class recall, macro F1; McNemar's exact test on
per-message correctness; Holm–Bonferroni over all 68 comparisons. Δ in percentage points.

## 3. Headline: DLF (gpt-4o-mini) vs the 68 other systems

| Holm-corrected test | DLF significantly better | tie | DLF significantly worse |
|---|---|---|---|
| ΔF1(+) bootstrap | **31** | **34** | **3** |
| Δaccuracy bootstrap | 31 | 34 | 3 |
| McNemar (correctness) | 31 | 34 | 3 |
| Δrecall(+) bootstrap | 25 | 33 | 10 |

Excluding DLF's own variants (two Layer-1-only versions: DLF better; gpt-5-mini DLF: tie), against the 65
competing methods **DLF wins 29, ties 33, loses 3**.

* **Loses (all by < 1 F1 point):** fine-tuned mBERT (−0.81, CI [−1.20, −0.44]), fine-tuned BanglaBERT
  (−0.76, [−1.17, −0.37]), word+char n-gram TF-IDF + SVM (−0.62, [−0.99, −0.26]).
* **Ties:** the other 6 fine-tuned encoders (XLM-R, IndicBERT, IndicBERTv2, MuRIL, DistilBERT, MobileBERT);
  LaBSE and E5 with every classifier; ParaMiniLM + SVM; all paper TF-IDF/Count LogReg/SVM/RF rows; char
  n-gram TF-IDF (LogReg/SVM/RF); word+char LogReg/RF; both fastText variants; 7 of 18 frozen-encoder rows.
* **Wins:** all MiniLM6, MiniLM12, DistilUSE and BGE rows, ParaMiniLM + LogReg/RF (14 of 21 sentence-
  embedding rows); 11 of 18 frozen-encoder rows; all four Naive-Bayes rows; Layer 1 alone (F1 +1.04,
  CI [+0.54, +1.54], p = 0.007).
* **Recall** is DLF's cost: 9 competing methods (the fine-tuned encoders except MobileBERT, char-n-gram SVMs)
  have significantly higher positive-class recall (by 1.0–1.6 pts); Layer 2 trades 1.9 pts recall for
  +3.8 pts precision.
* **gpt-5-mini gives no gain:** DLF-gpt-5-mini vs DLF-gpt-4o-mini Δ = 0.00 (CI [−0.22, +0.22]), McNemar 12/12,
  p = 1.0. Against the others it wins 31, ties 33, loses 4 (XLM-R crosses the threshold, p = 0.014, vs
  p = 0.058 for gpt-4o-mini — boundary noise).

## 4. Why no LLM can make DLF beat the best encoders on these labels

The two LLMs make the *same* errors (88 of 100 shared), and most of them look like **gold-label errors**:
* 36 messages labelled *request* that both LLMs reject are mostly not requests: thank-you posts
  ("brother X donated B+ blood, please pray"), donation-awareness slogans, a hospital job advert, a scam
  warning, a missing-person post — almost all Facebook, suggesting group-level rather than content labels.
* 30 messages labelled *not a request* that both LLMs accept include unmistakable requests ("urgent, 1 bag
  O-ve blood needed, patient in the OT at Dinajpur Medical College"; "#Blood required urgently … contact").
* Fine-tuned BanglaBERT is right on 28 of the 36 and 14 of the 30, i.e. it has learnt the labelling quirks.

If the paper should claim DLF is best, the defensible route is a **blind re-annotation** of every test
message on which *any* of the 69 systems disagrees with the gold label (annotators blind to predictions),
applied to all systems, then re-running `python -m baselines.significance`. Re-labelling only DLF's errors
would bias the comparison and must not be done.

## 5. Files → where they go

| file | use |
|---|---|
| `significance_dlf_full_gpt4omini_compact.tex` (22 rows) | **main text**: DLF vs every fine-tuned encoder + strongest cheap rows (Holm over all 68) |
| `significance_dlf_full_gpt4omini.tex` (68 rows) | appendix: complete pairwise table vs DLF |
| `significance_dlf_full_gpt5mini.tex` / `_compact.tex` | appendix (optional): LLM ablation |
| `significance_finetune_csebuetnlp_banglabert_bert.tex`, `significance_tfidf_logistic.tex`, `significance_tfidf_logistic_weighted_recall.tex` | appendix (optional): other references |
| `significance_allpairs_mcnemar_holm.csv` | supplementary (all-pairs Holm-corrected McNemar p-values) |
| `significance_markers.json` | Table 3 † markers (significant vs DLF-gpt-4o-mini) |
| `results/.../paper-repro/dlf_layer2/` | LLM reproducibility artifacts (§8) |
| `_superseded/` | earlier versions of these tables, kept for the record |

## 6. Text to add

**Experimental Setup.**
```latex
\paragraph{Statistical Significance Testing}
All filtering methods in Table~\ref{tab:DLF} are evaluated on the same 5{,}166 test messages, so we compare
them with paired tests. For each competing method we resample the test messages jointly with DLF 10{,}000
times and report the difference in accuracy, positive-class F1 and positive-class recall with 95\%
percentile confidence intervals and two-sided bootstrap $p$-values; we also apply McNemar's exact test to
per-message correctness. $p$-values are Holm--Bonferroni corrected across all comparisons. Layer~2 of DLF
uses gpt-4o-mini (snapshot 2024-07-18); prompts, raw responses, token log-probabilities, latencies and costs
are released with the code.
```

**Table 3 caption.** `DLF is statistically indistinguishable from most strong configurations and within one
F1 point of the best fine-tuned encoders; $\dagger$ marks methods whose positive-class F1 differs
significantly from DLF after Holm correction ($p<0.05$; Table~\ref{tab:significance-compact-gpt-4o-mini}).`

**Results.**
```latex
Paired tests (Table~\ref{tab:significance-compact-gpt-4o-mini}; full results in Appendix~X) show that DLF
significantly outperforms 29 of the 65 competing configurations and is statistically indistinguishable from
33 others, including fine-tuned XLM-R, MuRIL, IndicBERT, DistilBERT and MobileBERT, character $n$-gram and
fastText classifiers, and LaBSE and E5 embeddings. Only fine-tuned mBERT, fine-tuned BanglaBERT and a
word+character $n$-gram SVM are significantly better, each by less than one F1 point. The LLM layer removes
71\% of Layer~1's false positives while rejecting 1.9\% of true requests, raising F1 from 0.967 to 0.977
($p<0.01$). Replacing gpt-4o-mini with the reasoning model gpt-5-mini changes neither the predictions
materially nor any conclusion ($\Delta F1 = 0.00$, $p=1.0$) at six times the cost.
```

## 7. Response to the reviewer

> Thank you for this suggestion. Because every method in Table 3 is evaluated on the same 5,166 test messages,
> we added paired statistical comparisons: paired-bootstrap 95% confidence intervals (10,000 resamples) and
> p-values for the differences in accuracy, positive-class F1 and recall, McNemar's exact test on per-message
> correctness, and Holm correction for multiple comparisons (new paragraph in Experimental Setup; new Table X;
> complete pairwise tables in Appendix X). DLF significantly outperforms 29 of the 65 compared configurations
> and is statistically indistinguishable from 33 others, including several fine-tuned multilingual and Bengali
> encoders; fine-tuned mBERT, BanglaBERT and a character n-gram SVM are significantly better by less than one
> F1 point. We have revised Table 3 and its caption accordingly and no longer claim that DLF outperforms all
> classifiers; we retain the claim that DLF reaches comparable accuracy while invoking the LLM only for
> messages pre-selected by an inexpensive first layer. We also show that a newer reasoning LLM (gpt-5-mini)
> yields statistically identical results. To ensure reproducibility we re-ran the complete pipeline and release
> all prompts, raw LLM responses, log-probabilities, costs and per-message predictions.

## 8. Reproducibility artifacts (LLM layer)

`results/classifier-results-baselines/evaluation_results/paper-repro/dlf_layer2/`, per model
(`tfidf_logistic_weighted_recall_<model>.*`):
* `.responses.jsonl` — one record per call: full system + user prompt, request settings (model, seed 42,
  logprobs for gpt-4o-mini, temperature = API default as in `llmclient.py`), raw output, parsed JSON, verdict,
  P(true)/P(false) (gpt-4o-mini), OpenAI request id, model snapshot, system fingerprint, finish reason,
  token usage incl. reasoning tokens, cost, UTC timestamps, latency, retry attempts, SHA-256 of message and
  prompt, gold label, Layer-1 score.
* `.calls.csv` flat per-call table; `.manifest.json` git commit, package versions, SHA-256 of dataset /
  Layer-1 predictions / prompt / client / script, totals; `.log` run log; `stdout_*.txt` raw console output.
* `_dryrun_2026-10-06/`, `_superseded_v0_sparse_records/` — dry runs, kept for completeness.
* **Before publishing:** prompts contain the raw, non-anonymised messages; strip `request.user_prompt`
  (hashes remain) or regenerate from the anonymised dataset.
* Re-run: `cd binary-classifier && python -m baselines.dlf_layer2 [--model gpt-5-mini]` (resumes), then
  `python -m baselines.significance --ref dlf_full_tfidf_logistic_weighted_recall_gpt-4o-mini`.

## 9. Caveats

1. **Layer-1 weighting:** committed `eval-v1.py` up-weights the *negative* class 15:1 (recall 0.919), the
   opposite of the paper's text. DLF here uses Layer 1 as described (positives 12:1, recall 0.990). Fix the code.
2. The published DLF row (0.99) and the 525-message Layer-1 report come from earlier unrecorded runs on a
   different evaluation set; the reproduced numbers replace them.
3. Reproduced paper rows differ from published ones by ≤ 0.6 pts; Word2Vec and Jina keep published numbers
   without tests (download size / remote code incompatible with transformers ≥ 5).
4. Single training seed for fine-tuned models; the bootstrap covers test-set sampling only. LLM sampling uses
   the API default temperature with a fixed seed (best-effort determinism; several backend fingerprints seen).
5. XLM-R, MuRIL and IndicBERTv2 were fine-tuned with frozen word embeddings (6 GB GPU).
