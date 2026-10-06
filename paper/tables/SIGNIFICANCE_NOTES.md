# Statistical significance for Table 3 — what was done, what it shows, what to paste

Generated 2026-10-01 by `binary-classifier/baselines/significance.py` from per-message predictions of
**67 systems on the identical 5,166-message test split** (the one behind Table 3): the 35 new baseline rows,
the paper's original rows re-run with the repository code (TF-IDF, Count, 8 sentence-embedding models,
DistilBERT, MobileBERT; Word2Vec and Jina excluded, see caveats) and two DLF layer-1 variants.

## Procedure (what the paper should say)

* **Paired bootstrap.** All systems are evaluated on the same messages, so for a reference R and a
  method S we resample the 5,166 test messages *jointly* 10,000 times and compute the distribution of
  Δ = metric(R) − metric(S) for accuracy, positive-class F1, positive-class recall and macro F1
  → 95 % percentile CI and a two-sided bootstrap p-value.
* **McNemar's exact test** on per-message correctness (b = messages only R gets right, c = only S).
* **Holm–Bonferroni** correction over the 66 comparisons of each family.
* Reported as Δ in percentage points with CI; `*` p<0.05, `**` p<0.01, `***` p<0.001.
* Reference systems: (1) **DLF layer 1 as described in the paper** (TF-IDF + LogReg, positives weighted
  12:1) — the DLF component that can be reproduced without API keys; (2) **BanglaBERT fine-tuned** — the
  strongest single model; (3) **plain TF-IDF + LogReg** — the cheapest competitive model.

## Headline results

| Reference | sig. better than ref | sig. worse | not distinguishable |
|---|---|---|---|
| DLF layer 1 (recall-weighted), F1(+) | 25 | 7 | 34 |
| BanglaBERT fine-tuned, F1(+) | 0 | 57 | 9 |
| TF-IDF + LogReg, F1(+) | 17 | 23 | 26 |

* **The top of Table 3 is a statistical tie.** Against BanglaBERT (0.987), the other five fine-tuned
  encoders (mBERT, XLM-R, IndicBERT, DistilBERT, MuRIL) and the four character-n-gram SVM/RF rows are
  *not* significantly different (all |ΔF1| ≤ 0.3 pts, Holm p ≥ 0.5). Everything else (57 systems) is
  significantly worse. Nothing beats BanglaBERT.
* **DLF layer 1 matches the best encoders on recall, not on F1.** On positive-class recall the
  recall-weighted layer 1 (0.990) is statistically tied with mBERT, BanglaBERT and XLM-R (ΔRecall CIs
  include 0) and significantly *higher* than every cheaper model. Its F1 (0.967) is significantly below
  the 25 strongest systems (ΔF1 ≈ 1.1–1.9 pts) because of false positives — exactly the errors the
  LLM second layer is designed to remove.
* **The layer 1 shipped in the repository is weighted the wrong way round.** `eval-v1.py` uses
  class_weight {0:15, 1:1} (negatives up-weighted): recall(+) 0.919, precision(+) 0.993. The paper text
  (Sec. Methodology) describes the opposite. The recall-weighted variant has +7.1 pts recall
  (CI [+6.1, +8.2], p = 0.002) and +1.25 pts F1 over the as-coded one. Use the recall-weighted one; fix
  the code.
* **Character n-grams beat word n-grams significantly:** CharTFIDF+LogReg vs TFIDF+LogReg ΔF1 = +0.55
  pts (p < 0.05); fastText char vs word also significant.
* All-pairs: of the 2,211 pairs, 1,129 McNemar comparisons are significant after Holm correction
  (`significance_allpairs_mcnemar_holm.csv`).

## Files → where they go

| file | use |
|---|---|
| `significance_tfidf_logistic_weighted_recall_compact.tex` (`tab:significance-compact`, 20 rows) | **main text or first appendix table**: every fine-tuned encoder + the strongest cheap rows vs DLF layer 1 |
| `significance_tfidf_logistic_weighted_recall.tex` (`tab:significance`, 66 rows) | appendix: full pairwise table vs DLF layer 1 |
| `significance_finetune_csebuetnlp_banglabert_bert.tex` | appendix: full pairwise table vs the best model (shows the tie at the top) |
| `significance_tfidf_logistic.tex` | optional: vs plain TF-IDF + LogReg |
| `significance_allpairs_mcnemar_holm.csv` | supplementary material (67×67 Holm-corrected McNemar p-values) |
| `significance_markers.json` / `*_compact.json` | which Table 3 rows get a † marker |

Before pasting: rename the duplicate `\label{tab:significance}` if you include more than one full table,
and shorten the auto-generated captions as you like.

## Text to add

**Experimental Setup → new paragraph "Statistical significance".**
```latex
\paragraph{Statistical Significance Testing}
All filtering methods in Table~\ref{tab:DLF} are evaluated on the same 5{,}166 test messages, so we
compare them with paired tests. For a reference system $R$ and a competing method $S$ we resample the
test messages jointly 10{,}000 times and report the difference $\Delta = m(R)-m(S)$ in accuracy,
positive-class F1 and positive-class recall with 95\% percentile confidence intervals and two-sided
bootstrap $p$-values; we additionally apply McNemar's exact test to per-message correctness. All
$p$-values are Holm--Bonferroni corrected across the 66 comparisons of a reference. We use three
references: DLF Layer~1 (the TF-IDF/weighted-LogReg filter), the strongest single model (fine-tuned
BanglaBERT) and the cheapest competitive model (TF-IDF + LogReg). Table~\ref{tab:significance-compact}
reports the main comparisons; the complete pairwise tables are in Appendix~X.
```

**Table 3 caption, add:** `$\dagger$ marks methods whose positive-class F1 differs significantly from
DLF Layer~1 after Holm correction ($p<0.05$); see Table~\ref{tab:significance-compact}.` (The
markers are listed in `significance_markers_compact.json`; in practice: † on every fine-tuned encoder,
every CharTFIDF / Word+CharTFIDF row except NB, both fastText rows, TFIDF+SVM/RF, Count+LogReg/RF,
LaBSE, E5+SVM, IndicBERTv2+SVM and the frozen-encoder rows that are significantly *worse*.)

**Results paragraph (after the Table 3 discussion).**
```latex
Paired tests (Table~\ref{tab:significance-compact}) show that the top of Table~\ref{tab:DLF} is a
statistical tie: the six fine-tuned encoders and the character $n$-gram SVM/RF models are
indistinguishable from the best model, fine-tuned BanglaBERT ($|\Delta F1| \le 0.3$ points, Holm
$p \ge 0.5$), whereas all other configurations are significantly worse. DLF Layer~1 attains the same
positive-class recall as the best fine-tuned encoders (0.990; $\Delta$ not significant) at four
orders of magnitude lower inference cost, while its lower precision---the false positives that Layer~2
removes---makes its F1 significantly lower ($\Delta F1 = 1.1$--$1.9$ points). Character $n$-grams
significantly outperform word $n$-grams for both TF-IDF ($\Delta F1=+0.55$, $p<0.05$) and fastText.
```

**Response to the reviewer.**
> We agree that point estimates alone do not establish whether the differences in Table 3 are meaningful.
> Since every method is evaluated on the same 5,166 test messages, we added paired comparisons: paired
> bootstrap confidence intervals (10,000 resamples) and p-values for Δaccuracy, ΔF1 and Δrecall, McNemar's
> exact test on per-message correctness, and Holm correction across all comparisons (new paragraph in
> Experimental Setup; Table X in the main text; complete pairwise tables and the full 67×67 McNemar matrix in
> Appendix X / supplementary material). The analysis shows that (i) the strongest configurations
> (fine-tuned BanglaBERT, mBERT, XLM-R, IndicBERT, MuRIL, DistilBERT and character n-gram SVM/RF) are
> statistically indistinguishable from each other, (ii) all remaining configurations are significantly
> worse than the best model, and (iii) DLF Layer 1 matches the best encoders on positive-class recall
> while being significantly lower in F1 owing to false positives, which motivates the second layer. We have
> revised the text accordingly and no longer claim that DLF "outperforms" the other classifiers in accuracy.

## Caveats (state them or be ready for them)

1. **The full DLF (Layer 1 + LLM Layer 2) is not in these tests.** Its predictions need ~2,300 GPT-4o-mini
   calls (`python -m baselines.dlf_layer2`, resumable; under one dollar). Once run, `significance.py`
   uses it as the default reference automatically. The paper's DLF row (0.99/0.99/0.98/0.98) cannot be
   reproduced from the repository without that layer, and the Layer-1 classification report in the
   paper (support 525) comes from a different, smaller test set than Table 3.
2. The reproduced paper rows differ from the published ones by ≤ 0.6 pts (e.g. TFIDF+LogReg 0.9768 vs
   0.9774; MiniLM6 0.966 vs 0.97; MobileBERT 0.982 vs 0.980 — only with fp32 and lr 5e-5, bf16 gave
   0.963). Word2Vec (1.6 GB download) and Jina (remote code incompatible with transformers ≥ 5) were not
   re-run; their Table 3 rows stay as published but have no significance entry.
3. Fine-tuned rows are single-seed; the bootstrap captures test-set sampling variance only, not
   training-seed variance. With 5,166 messages, one message = 0.02 pts; differences < ~0.3 pts are never
   significant here.
4. XLM-R, MuRIL and IndicBERTv2 were fine-tuned with frozen word embeddings (6 GB GPU).
