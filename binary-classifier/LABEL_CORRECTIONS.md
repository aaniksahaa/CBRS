# Test-label corrections (2026-10-06)

81 of the 5,166 messages in the paper's classification test split were re-labelled after human review:
**63 request -> not request** and **18 not request -> request** (test positives 2,206 -> 2,161).

Procedure: every test message on which at least one of 69 classifiers disagreed with the original label (921)
was re-read blind (text only, no labels or predictions) against a fixed definition (label 1 = the message asks
for blood or blood donors for a patient). Each proposed flip was re-read and all 81 were verified and approved
by the authors. Training rows were not changed (17 training rows share the exact text of a corrected test message).
Per-message log: LABEL_CORRECTIONS.csv (row index, test position, old/new label, reason). Originals: *.pre_relabel_2026-10-06.*
