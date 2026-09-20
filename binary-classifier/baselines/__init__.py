"""Pluggable baseline harness for the CBRS blood-request binary classifier.

Adding a baseline = one entry in `registry.py`.  Every baseline is evaluated on
the *identical* 80/20 split used for the numbers already in the paper
(`shuffle(random_state=42)` + `train_test_split(test_size=0.2, random_state=42)`),
and writes a JSON file with the same schema as `results/classifier-results-with-time/`.
"""
