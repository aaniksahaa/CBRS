Latency benchmark ({"cpu": "x86_64", "python": "3.13.5", "n_test": 5166, "single_n": 500, "gpu": "NVIDIA GeForce RTX 3050 6GB Laptop GPU"})

| System | Device | Single msg median (ms) | p95 (ms) | Batch (µs/msg) |
|---|---|---|---|---|
| DLF Layer 1: word TF-IDF + weighted LogReg | cpu1 | 0.333 | 0.383 | 16.9 |
| TF-IDF + LogReg (paper row) | cpu1 | 0.211 | 0.269 | 17.1 |
| Count + LogReg (paper row) | cpu1 | 0.140 | 0.168 | 18.5 |
| Char n-gram TF-IDF + LogReg | cpu1 | 0.441 | 0.782 | 183.7 |
| fastText, char n-grams 2-5 | cpu1 | 0.074 | 0.150 | 75.5 |
| fastText, word only | cpu1 | 0.017 | 0.037 | 15.1 |
| banglabert_ft (fine-tuned) | gpu | 5.499 | 8.331 | 5986.7 |
| mbert_ft (fine-tuned) | gpu | 5.550 | 8.659 | 5988.8 |
| xlmr_base_ft (fine-tuned) | gpu | 5.609 | 8.624 | 5917.3 |
| muril_ft (fine-tuned) | gpu | 5.437 | 8.195 | 6018.3 |
| indicbert_ft (fine-tuned) | gpu | 5.624 | 8.700 | 6022.5 |
| distilbert_multilingual_ft (fine-tuned) | gpu | 3.027 | 4.621 | 3025.6 |
| paper_mobilebert_ft (fine-tuned) | gpu | 10.823 | 11.536 | 2558.8 |
| banglabert_ft (fine-tuned) | cpu16 | 36.535 | 352.548 | 66281.0 |
| distilbert_multilingual_ft (fine-tuned) | cpu16 | 23.055 | 268.612 | 33143.7 |
| DLF Layer 2 API call (gpt-4o-mini), per forwarded message | api | 1123.109 | 1530.841 | 513278.8 |
| DLF Layer 2 API call (gpt-5-mini), per forwarded message | api | 2256.198 | 3614.967 | 1079386.1 |
