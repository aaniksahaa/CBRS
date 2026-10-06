"""DLF layer 2: re-check layer-1 positives with an LLM and write full-DLF predictions (needs API keys).

    cd binary-classifier
    export OPENAI_API_KEY=...            # whatever dual-layer-filtering/llmclient.py expects for the chosen model
    python -m baselines.dlf_layer2 --layer1 tfidf_logistic_weighted_recall --model gpt-4o-mini
    python -m baselines.significance    # the dlf_full_* predictions become the default reference

Resumable: every LLM response is appended to <cache>/dlf_layer2/<layer1>_<model>.jsonl and reused on re-run.
Messages predicted negative by layer 1 are never sent to the LLM (that is the point of DLF).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .data import DEFAULT_DATA, load_split
from .metrics import build_result, env_info, save_predictions, save_result
from .run import DEFAULT_CACHE, DEFAULT_OUT

log = logging.getLogger("dlf_layer2")
DLF_DIR = Path(__file__).resolve().parents[1] / "dual-layer-filtering"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layer1", default="tfidf_logistic_weighted_recall", help="prediction key under <out>/paper-repro/predictions/")
    ap.add_argument("--model", default="gpt-4o-mini", help="model name known to dual-layer-filtering/llmclient.py")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--data", default=None)
    ap.add_argument("--limit", type=int, default=None, help="only the first N positives (cost check)")
    ap.add_argument("--sleep", type=float, default=0.0, help="seconds between calls (rate limits)")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S")

    sys.path.insert(0, str(DLF_DIR))
    from llmclient import LLMClient  # noqa: E402  (the repo's client; reads API keys from env)
    # eval-v1.py runs code at import; we only need its prompt, re-implemented verbatim:
    def get_prompt(message: str) -> str:
        message = message.replace('"', '\\"')
        sample_true = {"is_blood_donation_request": True}
        sample_false = {"is_blood_donation_request": False}
        return f"""
    You are an expert in text classification for emergency blood donation requests. Analyze the following text to determine if it is explicitly related to a request for blood donation or an emergency need for blood. The text may be in English, Bengali, or a mix of both. Return your response in JSON format with a single key 'is_blood_donation_request' and a boolean value (true if related to blood donation/emergency, false otherwise). Ensure your analysis is precise and academically sound.
    Samples:
    Input Text: Emergency O+ blood needed. Please help.
    Response:
    ```json
    {json.dumps(sample_true)}
    ```
    Input Text: Blood donation is a great virtue.
    Response:
    ```json
    {json.dumps(sample_false)}
    ```
    Text: "{message}"
    Reminders:
    - Do not include any sort of greetings/fillers etc in the response.
    - Output only the correct JSON properly understanding the meaning of the English / Bengali / Transliterated Bengali Text
    """

    out_dir = Path(args.out) / "paper-repro"
    l1_path = out_dir / "predictions" / f"{args.layer1}.csv"
    if not l1_path.exists():
        raise SystemExit(f"{l1_path} not found - run `python -m baselines.run --tags dlf` first")
    l1 = pd.read_csv(l1_path)
    split = load_split(args.data or DEFAULT_DATA)
    assert len(split.test) == len(l1) and np.array_equal(split.test["label"].to_numpy(), l1["y_true"].to_numpy())
    texts = split.test["text"].tolist()

    cache = Path(args.cache_dir) / "dlf_layer2" / f"{args.layer1}_{args.model}.jsonl"
    cache.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if cache.exists():
        for line in cache.read_text().splitlines():
            r = json.loads(line)
            done[r["idx"]] = r
    pos_idx = l1.index[l1["y_pred"] == 1].tolist()
    todo = [i for i in pos_idx if i not in done]
    if args.limit:
        todo = todo[: args.limit]
    log.info("layer-1 positives: %d, cached: %d, to query: %d", len(pos_idx), len(done), len(todo))

    client = LLMClient()
    client.set_model(args.model)
    t_total = 0.0
    with open(cache, "a") as f:
        for n, i in enumerate(todo, 1):
            t0 = time.perf_counter()
            try:
                resp = client.get_response(get_prompt(texts[i]))
                parsed = resp.get("parsed_json") or {}
                verdict = parsed.get("is_blood_donation_request", None)
                rec = {"idx": int(i), "verdict": None if verdict is None else bool(verdict),
                       "raw": resp.get("output_text", "")[:500], "cost": resp.get("total_cost"),
                       "tokens": resp.get("total_tokens"), "secs": time.perf_counter() - t0}
            except Exception as e:  # keep the layer-1 decision on failure, as eval-v1.py does
                rec = {"idx": int(i), "verdict": None, "error": str(e)[:300], "secs": time.perf_counter() - t0}
            t_total += rec["secs"]
            done[i] = rec
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            if n % 50 == 0:
                log.info("%d/%d queried (%.1fs/call)", n, len(todo), t_total / n)
            if args.sleep:
                time.sleep(args.sleep)

    y_pred = l1["y_pred"].to_numpy().copy()
    n_flipped = 0
    for i in pos_idx:
        v = done.get(i, {}).get("verdict")
        if v is False:
            y_pred[i] = 0
            n_flipped += 1
    y_true = l1["y_true"].to_numpy()
    key = f"dlf_full_{args.layer1}_{args.model}".replace("/", "_")
    save_predictions(out_dir, key, y_true=y_true, y_pred=y_pred, languages=split.test["language"].to_numpy())
    l1_secs = json.load(open(out_dir / f"{args.layer1}.json"))["avg_inference_time_seconds"] * len(y_true)
    result = build_result(vectorizer="tfidf", model="dlf", embedding_model=args.model, y_true=y_true, y_pred=y_pred,
                          avg_inference_time_seconds=(l1_secs + t_total) / len(y_true),
                          languages=split.test["language"].to_numpy(),
                          extra={"baseline": key, "kind": "dlf", "layer1": args.layer1, "llm": args.model,
                                 "n_layer1_positives": len(pos_idx), "n_llm_calls": len(done), "n_flipped_to_negative": n_flipped,
                                 "n_llm_failures": sum(1 for r in done.values() if r.get("verdict") is None),
                                 "llm_cost_total": float(sum((r.get("cost") or 0) for r in done.values())),
                                 "llm_seconds_total": t_total, "env": env_info(), "data": split.data_path})
    save_result(result, out_dir, key)
    log.info("DLF full: acc=%.4f macroF1=%.4f recall+=%.4f (%d of %d positives flipped)  -> %s",
             result["accuracy"], result["extra"]["macro_f1"], result["metrics"]["1"]["recall"], n_flipped, len(pos_idx), key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
