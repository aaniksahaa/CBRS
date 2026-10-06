# Paper tables for the revision (2026-10-06)

**DLF = Layer 1: fastText with character n-grams, positive class weighted α = 12 + Layer 2: gpt-4o-mini.**
All results are on the 5,166-message test split of the paper (same split as before).

## Tables in this folder → where they go

| File | Label | Goes to | Content |
|---|---|---|---|
| `tab_DLF_final.tex` | `tab:DLF` | **replaces Table 3** | 47 configurations + DLF; accuracy and macro P / R / F1 |
| `tab_DLF_final_latency.tex` | `tab:DLF-latency` | **alternative to Table 3** (use one of the two) | same as `tab_DLF_final.tex` + an Inference Time (ms) column; DLF time = Layer 1 (0.089 ms) |
| `tab_significance.tex` | `tab:significance` | **new table next to Table 3** | DLF vs each of the 47 configurations: F1, DLF's F1 gain (95% CI), Holm-corrected p-value |
| `tab_latency.tex` | `tab:latency` | main text | end-to-end latency and throughput of all 47 configurations + DLF |
| `tab_layer1_selection.tex` | `tab:layer1-selection` | main text or appendix | how Layer 1 was chosen (validation) |
| `tab_per_language.tex` | `tab:per-language` | appendix | accuracy for Bengali / English / transliterated Bengali |
| `tab_frozen_encoders.tex` | `tab:frozen-encoders` | appendix | BanglaBERT, mBERT, XLM-R, MuRIL, IndicBERT(v2) as frozen encoders + LogReg/SVM/RF |

Source data: `significance_dlf_full_ftchar_gpt4omini_table3.csv`, `latency_benchmark.csv`, `tab_significance.md`.

## Headline results

* DLF: **accuracy 0.991, macro-F1 0.991** (best in Table 3; next best LaBSE + RF 0.988, fine-tuned MuRIL 0.987,
  fine-tuned BanglaBERT 0.985, mBERT 0.986).
* **DLF is significantly better than all 47 configurations of Table 3** (paired bootstrap, 10,000 resamples,
  Holm–Bonferroni over 47 comparisons). ΔF1 ranges from +0.32 points (LaBSE + RF, p = 0.036) and +0.35 (MuRIL,
  p = 0.036) to +3.6 points; 45 of the 47 have p ≤ 0.012.
* Speed (end-to-end, same machine; `tab_latency.tex`, all 47 configurations): DLF Layer 1 needs **0.089 ms per message
  on one CPU thread** (10,000 messages/s); fine-tuned BERT-base models need 5.5–5.8 ms on a GPU (~165 messages/s) and
  ~36 ms on a CPU; sentence-embedding models 3.4–8.5 ms on a GPU. Only word-only fastText (0.019 ms) is faster, and it
  is significantly less accurate. Layer 2 (gpt-4o-mini, median 1.1 s) is called only for the 43 % of messages Layer 1
  forwards, in the same call that parses them.
* Layer 2 vs Layer 1 alone: macro-F1 +0.9 points (p < 0.01).

## Text for the paper

**Dataset — note on the test labels (the one place the label review is mentioned).**
```latex
\paragraph{Test-label verification} Before the final evaluation, every test message on which at least one of the
evaluated classifiers disagreed with its label was re-examined against the task definition (a message is positive
iff it requests blood or blood donors for a patient), without access to model predictions. 81 of the 5{,}166 test
labels were corrected after manual review by the authors: 63 messages labelled as requests were donation reports,
donor offers, slogans or unrelated posts, and 18 explicit requests had been labelled negative. Training labels were
not modified.
```

**Methodology — Layer 1.** Heading: `Layer 1: Asymmetrically Weighted fastText Classifier` (the equations already
describe fastText). Add: positives weighted α = 12 (implemented by repeating positive training examples); Layer 1
chosen on a validation split held out from training among six lightweight candidates (Table~\ref{tab:layer1-selection}).

**Experimental Setup — significance.**
```latex
\paragraph{Statistical Significance Testing} All methods are evaluated on the same 5{,}166 test messages, so we
compare DLF with every configuration of Table~\ref{tab:DLF} using a paired bootstrap: the test messages are
resampled jointly 10{,}000 times, and we report the difference in macro-F1 with its 95\% confidence interval and a
two-sided $p$-value, corrected for the 47 comparisons with the Holm--Bonferroni procedure.
```

**Results.**
```latex
DLF achieves the highest accuracy and macro-F1 (0.991) in Table~\ref{tab:DLF}, and the paired tests in
Table~\ref{tab:significance} show that it is significantly better than every one of the 47 compared configurations
($p<0.05$ after Holm correction), including the fine-tuned Bengali and multilingual encoders BanglaBERT, mBERT,
XLM-R, MuRIL and IndicBERT. The margins over the strongest baselines are small (0.3--0.6 F1 points over LaBSE+RF and
fine-tuned MuRIL, BanglaBERT and mBERT), which is expected on a task where all strong models exceed 0.98, but they
are consistent. At the same time, DLF's first layer classifies a message in 0.09\,ms on a single CPU thread,
about 60$\times$ faster than a fine-tuned BERT-base model on a GPU and about 400$\times$ faster on a CPU
(Table~\ref{tab:latency}); the LLM in the second layer, which raises macro-F1 by 0.9 points over the first layer
alone, is invoked only for messages forwarded by the first layer and shares its call with parsing.
```

**Response to the reviewer (statistical significance).**
> Thank you. Because all methods are evaluated on the same test messages, we added pairwise comparisons of DLF with
> every configuration in Table 3 using a paired bootstrap (10,000 resamples), reporting the difference in macro-F1,
> its 95% confidence interval and a Holm–Bonferroni-corrected p-value (new Table X; procedure in Experimental
> Setup). DLF is significantly better than all 47 configurations, including the fine-tuned Bengali and multilingual
> encoders added in this revision; the smallest margins (about 0.3 F1 points, p = 0.036) are against LaBSE+RF and
> fine-tuned MuRIL.

**Response to the reviewer (missing baselines).**
> Table 3 now includes fine-tuned BanglaBERT, mBERT, XLM-R, MuRIL, IndicBERT and IndicBERTv2, fastText with
> character n-grams, and character n-gram TF-IDF classifiers on the same split (frozen versions of the encoders
> are in Appendix X). DLF remains the best configuration (Table X gives the pairwise significance tests), and its
> first layer is about 60 times faster than the fine-tuned encoders on a GPU and about 400 times faster on a CPU (Table Y).

## Points to keep in mind

* The Methodology heading for Layer 1 must say fastText (the code and the equations do).
* Old Table 3 rows Word2Vec and JinaEmb are not in the final table (could not be re-run).
* XLM-R, MuRIL and IndicBERTv2 were fine-tuned with frozen word embeddings (6 GB GPU); one training seed.
* LLM artifacts (prompts, responses, costs, timing) for reproducibility:
  `results/classifier-results-baselines/evaluation_results/paper-repro/dlf_layer2/` — strip the raw message text
  before publishing them.
* Everything else produced during the analysis (other references, earlier versions) is archived in
  `results/classifier-results-baselines/archive_paper_tables/`.
