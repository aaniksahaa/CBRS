"""DLF layer 2: re-check layer-1 positives with an LLM and write full-DLF predictions.

    cd binary-classifier
    # key in dual-layer-filtering/.env (git-ignored) as OPENAI_API_KEY=...; llmclient.py loads it
    python -m baselines.dlf_layer2 --limit 5                 # dry run: 5 calls, prints cost/latency estimate
    python -m baselines.dlf_layer2                           # full run (resumable), then:
    python -m baselines.significance                         # full DLF becomes the default reference

Only messages that layer 1 predicts positive are sent to the LLM (that is the point of DLF); a "false"
verdict flips them to negative, anything else (true / unparseable / API failure) keeps the layer-1
decision, exactly as dual-layer-filtering/eval-v1.py does. The prompt, system prompt and client
(dual-layer-filtering/llmclient.py) are the repository's, unchanged.

Reproducibility artifacts, all under <out>/paper-repro/dlf_layer2/:
  <run>.responses.jsonl   one JSON record per call: full request (system + user prompt, model, params),
                          full raw output, parsed JSON, verdict, P(true)/P(false) from token log-probs,
                          exact model snapshot, request id, system fingerprint, finish reason, token
                          usage details, cost, UTC timestamps, latency, every retry attempt and error,
                          message/prompt SHA-256, gold label and layer-1 score.
  <run>.calls.csv         flat per-call summary of the above (no prompt text).
  <run>.manifest.json     command line, git commit + dirty flag, package versions, SHA-256 of the dataset,
                          layer-1 predictions, prompt template, client and this script, request settings,
                          start/end time, totals (calls, tokens, cost, failures, snapshots, fingerprints).
  <run>.log               full run log.
Request settings beyond the original client: a fixed `seed` (OpenAI best-effort determinism) and
`logprobs`/`top_logprobs`; neither changes the model's output distribution. Temperature is NOT set,
as in the original client, so the API default applies (recorded in every record).
NOTE: the user prompts contain the raw messages (phone numbers etc. from pre_parsed_dataset.csv);
drop the `request.user_prompt` field before publishing (the SHA-256 hashes remain for verification).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import platform
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .data import DEFAULT_DATA, load_split
from .metrics import build_result, env_info, save_predictions, save_result
from .run import DEFAULT_OUT

log = logging.getLogger("dlf_layer2")
DLF_DIR = Path(__file__).resolve().parents[1] / "dual-layer-filtering"
REPO = Path(__file__).resolve().parents[2]
SYSTEM_PROMPT = "You are a helpful assistant."  # llmclient.get_response default, used by eval-v1.py
# USD per 1M tokens (standard tier), used when llmclient.py has no price for the model; reasoning tokens are
# billed as output tokens and are included in completion_tokens.
PRICES = {"gpt-4o-mini": (0.15, 0.60), "gpt-5-mini": (0.25, 2.00), "gpt-5-nano": (0.05, 0.40),
          "gpt-5": (1.25, 10.00), "gpt-4.1-mini": (0.40, 1.60), "gpt-4o": (2.50, 10.00)}


def is_reasoning_model(model: str) -> bool:
    return model.startswith(("gpt-5", "o1", "o3", "o4"))


def get_prompt(message: str) -> str:
    """Verbatim copy of get_prompt() in dual-layer-filtering/eval-v1.py (that file runs code on import)."""
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


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(p: Path) -> str | None:
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except Exception:
        return None


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def git_info() -> dict:
    def g(*a):
        try:
            return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            return None
    return {"commit": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty_files": len((g("status", "--porcelain") or "").splitlines())}


def pkg_versions() -> dict:
    from importlib.metadata import PackageNotFoundError, version
    out = {"python": platform.python_version()}
    for p in ("openai", "langchain-openai", "langchain-core", "httpx", "numpy", "pandas", "scikit-learn"):
        try:
            out[p] = version(p)
        except PackageNotFoundError:
            out[p] = None
    return out


# ----------------------------------------------------------------------------- capture layer
_TL = threading.local()


def install_recorder(llmclient_module, seed: int | None, logprobs: bool, top_logprobs: int, reasoning_effort: str | None = None):
    """Replace llmclient's ChatOpenAI with a subclass that (a) adds seed/logprobs to the request and
    (b) records every invoke attempt and the full AIMessage in thread-local storage.
    llmclient.py itself is not modified."""
    Base = llmclient_module.ChatOpenAI

    class RecordingChatOpenAI(Base):  # type: ignore[misc, valid-type]
        def __init__(self, **kw):
            if seed is not None:
                kw.setdefault("seed", seed)
            if logprobs:
                kw.setdefault("logprobs", True)
                kw.setdefault("top_logprobs", top_logprobs)
            if reasoning_effort:
                kw.setdefault("reasoning_effort", reasoning_effort)
            super().__init__(**kw)

        def invoke(self, *a, **kw):
            att = {"t_start_utc": now_utc()}
            t0 = time.perf_counter()
            try:
                msg = super().invoke(*a, **kw)
                att.update(ok=True, latency_s=time.perf_counter() - t0)
                _TL.last = msg
                _TL.request_params = {"model": self.model_name, "temperature": self.temperature, "seed": self.seed,
                                      "logprobs": self.logprobs, "top_logprobs": self.top_logprobs,
                                      "max_tokens": getattr(self, "max_tokens", None), "n": getattr(self, "n", None),
                                      "reasoning_effort": getattr(self, "reasoning_effort", None)}
                return msg
            except Exception as e:
                att.update(ok=False, latency_s=time.perf_counter() - t0, error=f"{type(e).__name__}: {str(e)[:500]}")
                raise
            finally:
                _TL.attempts.append(att)

    llmclient_module.ChatOpenAI = RecordingChatOpenAI


def verdict_probs(logprobs_content) -> dict | None:
    """P(true) / P(false) at the first token that decides the boolean, from top_logprobs."""
    if not logprobs_content:
        return None
    for tok in logprobs_content:
        t = (tok.get("token") or "").strip().lower()
        if t in ("true", "false"):
            # sum the probability mass of all variants (" true", "true", "\ttrue", ...) among the top alternatives
            mass: dict[str, float] = {}
            alts = tok.get("top_logprobs") or [{"token": tok.get("token"), "logprob": tok.get("logprob")}]
            for a in alts:
                k = (a.get("token") or "").strip().lower()
                mass[k] = mass.get(k, 0.0) + math.exp(a.get("logprob", -1e9))
            return {"p_true": mass.get("true", 0.0), "p_false": mass.get("false", 0.0),
                    "chosen_token": tok.get("token"), "chosen_logprob": tok.get("logprob"),
                    "top_alternatives": [(a.get("token"), a.get("logprob")) for a in alts]}
    return None


def to_jsonable(x):
    try:
        json.dumps(x)
        return x
    except TypeError:
        if isinstance(x, dict):
            return {str(k): to_jsonable(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [to_jsonable(v) for v in x]
        if hasattr(x, "model_dump"):
            return to_jsonable(x.model_dump())
        return str(x)


def call_one(client, i: int, text: str, meta: dict) -> dict:
    prompt = get_prompt(text)
    _TL.attempts, _TL.last, _TL.request_params = [], None, None
    rec = {"idx": int(i), **{k: v for k, v in meta.items() if not k.startswith("_")}, "message_sha256": sha256_text(text), "prompt_sha256": sha256_text(prompt),
           "started_utc": now_utc()}
    t0 = time.perf_counter()
    try:
        resp = client.get_response(prompt)  # the repository client: retries, key rotation, cost, JSON parsing
        msg = _TL.last
        md = to_jsonable(getattr(msg, "response_metadata", {}) or {})
        usage = to_jsonable(getattr(msg, "usage_metadata", {}) or {})
        lp = (md.get("logprobs") or {}).get("content") if isinstance(md.get("logprobs"), dict) else None
        parsed = resp.get("parsed_json")
        v = parsed.get("is_blood_donation_request") if isinstance(parsed, dict) else None
        rec.update({
            "verdict": None if v is None else bool(v),
            "parse_ok": isinstance(parsed, dict) and "is_blood_donation_request" in parsed,
            "request": {"system_prompt": SYSTEM_PROMPT, "user_prompt": prompt, **(_TL.request_params or {})},
            "response": {"output_text": resp.get("output_text"), "parsed_json": parsed,
                         "openai_id": md.get("id"), "langchain_run_id": getattr(msg, "id", None),
                         "model_snapshot": md.get("model_name"),
                         "system_fingerprint": md.get("system_fingerprint"), "finish_reason": md.get("finish_reason"),
                         "service_tier": md.get("service_tier"), "token_usage": md.get("token_usage"),
                         "usage_metadata": usage, "logprobs": lp},
            "verdict_probs": verdict_probs(lp),
            "input_tokens": resp.get("input_tokens"), "output_tokens": resp.get("output_tokens"),
            "reasoning_tokens": ((md.get("token_usage") or {}).get("completion_tokens_details") or {}).get("reasoning_tokens"),
            "cost_usd_llmclient": resp.get("total_cost"), "latency_s": resp.get("inference_time"),
        })
        price = PRICES.get(meta.get("_model", ""))
        rec["price_per_1m_usd"] = price
        rec["cost_usd"] = (resp.get("total_cost") or 0) if not price else \
            (resp.get("input_tokens", 0) * price[0] + resp.get("output_tokens", 0) * price[1]) / 1e6
    except Exception as e:  # keep the layer-1 decision on failure, as eval-v1.py does
        rec.update({"verdict": None, "parse_ok": False, "error": f"{type(e).__name__}: {str(e)[:1000]}",
                    "request": {"system_prompt": SYSTEM_PROMPT, "user_prompt": prompt, **(_TL.request_params or {})}})
    rec["attempts"] = list(_TL.attempts)
    rec["n_attempts"] = len(_TL.attempts)
    rec["wall_s"] = time.perf_counter() - t0
    rec["finished_utc"] = now_utc()
    return rec


# ----------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layer1", default="tfidf_logistic_weighted_recall", help="prediction key under <out>/paper-repro/predictions/")
    ap.add_argument("--model", default="gpt-4o-mini", help="model name known to dual-layer-filtering/llmclient.py")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--data", default=None)
    ap.add_argument("--limit", type=int, default=None, help="dry run: only the first N layer-1 positives, no predictions written")
    ap.add_argument("--workers", type=int, default=4, help="concurrent requests (gpt-4o-mini limits are far higher)")
    ap.add_argument("--seed", type=int, default=42, help="OpenAI best-effort determinism; -1 to omit")
    ap.add_argument("--no-logprobs", action="store_true")
    ap.add_argument("--top-logprobs", type=int, default=5)
    ap.add_argument("--retry-failed", action="store_true", help="re-query records that ended in an API error")
    ap.add_argument("--reasoning-effort", default=None, choices=["minimal", "low", "medium", "high"],
                    help="reasoning models only; default = API default (medium for gpt-5-mini)")
    args = ap.parse_args(argv)

    out_dir = Path(args.out) / "paper-repro"
    art_dir = out_dir / "dlf_layer2"
    art_dir.mkdir(parents=True, exist_ok=True)
    run = f"{args.layer1}_{args.model}".replace("/", "_")
    paths = {k: art_dir / f"{run}.{k}" for k in ("responses.jsonl", "calls.csv", "manifest.json", "log")}

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S",
                        handlers=[logging.StreamHandler(), logging.FileHandler(paths["log"], encoding="utf-8")])
    for noisy in ("httpx", "httpcore", "openai", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    sys.path.insert(0, str(DLF_DIR))
    import llmclient  # noqa: E402  the repository's client; load_dotenv() reads dual-layer-filtering/.env
    seed = None if args.seed is not None and args.seed < 0 else args.seed
    if is_reasoning_model(args.model) and not args.no_logprobs:
        log.info("%s is a reasoning model: the API does not return log-probs, disabling them", args.model)
        args.no_logprobs = True
    install_recorder(llmclient, seed, not args.no_logprobs, args.top_logprobs, args.reasoning_effort)

    l1_path = out_dir / "predictions" / f"{args.layer1}.csv"
    if not l1_path.exists():
        raise SystemExit(f"{l1_path} not found - run `python -m baselines.run --tags dlf` first")
    l1 = pd.read_csv(l1_path)
    split = load_split(args.data or DEFAULT_DATA)
    assert len(split.test) == len(l1) and np.array_equal(split.test["label"].to_numpy(), l1["y_true"].to_numpy()), \
        "layer-1 predictions are not on this test split"
    texts = split.test["text"].tolist()
    langs = split.test["language"].tolist()

    done: dict[int, dict] = {}
    if paths["responses.jsonl"].exists():
        for line in paths["responses.jsonl"].read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["idx"]] = r  # later lines (retries) supersede earlier ones
    pos_idx = l1.index[l1["y_pred"] == 1].tolist()
    todo = [i for i in pos_idx if i not in done or (args.retry_failed and "error" in done[i])]
    if args.limit:
        todo = todo[: args.limit]

    manifest = json.loads(paths["manifest.json"].read_text()) if paths["manifest.json"].exists() else {}
    manifest.setdefault("runs", [])
    manifest.update({
        "description": "DLF layer 2 (LLM re-check of layer-1 positives) on the paper's Table 3 test split",
        "layer1": args.layer1, "model_requested": args.model, "system_prompt": SYSTEM_PROMPT,
        "prompt_template": get_prompt("{MESSAGE}"), "prompt_template_sha256": sha256_text(get_prompt("{MESSAGE}")),
        "request_settings": {"seed": seed, "logprobs": not args.no_logprobs, "top_logprobs": args.top_logprobs,
                             "temperature": "not set (API default), as in llmclient.py",
                             "reasoning_effort": args.reasoning_effort or ("API default" if is_reasoning_model(args.model) else None)},
        "prices_usd_per_1m": PRICES.get(args.model),
        "decision_rule": "verdict false -> negative; true/unparseable/error -> keep layer-1 positive (eval-v1.py)",
        "sha256": {"dataset_csv": sha256_file(Path(split.data_path)), "layer1_predictions_csv": sha256_file(l1_path),
                   "llmclient_py": sha256_file(DLF_DIR / "llmclient.py"), "eval_v1_py": sha256_file(DLF_DIR / "eval-v1.py"),
                   "this_script": sha256_file(Path(__file__))},
        "data": {"path": split.data_path, "n_test": len(texts), "matches_paper_split": split.matches_paper_split,
                 "n_layer1_positives": len(pos_idx)},
        "git": git_info(), "packages": pkg_versions(), "env": env_info(),
    })
    run_rec = {"started_utc": now_utc(), "argv": sys.argv, "n_to_query": len(todo), "n_cached": len(done),
               "dry_run": bool(args.limit)}
    manifest["runs"].append(run_rec)
    paths["manifest.json"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    log.info("layer-1 positives: %d, cached: %d, to query: %d, workers: %d, seed: %s, logprobs: %s",
             len(pos_idx), len(done), len(todo), args.workers, seed, not args.no_logprobs)

    client = llmclient.LLMClient()
    client.set_model(args.model)
    lock = threading.Lock()
    t_start = time.perf_counter()
    n_new = 0
    with open(paths["responses.jsonl"], "a", encoding="utf-8") as f, \
            ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(call_one, client, i, texts[i],
                            {"_model": args.model, "y_true": int(l1.at[i, "y_true"]), "language": langs[i],
                             "layer1_score": float(l1.at[i, "score"]) if "score" in l1 else None}): i for i in todo}
        for fut in as_completed(futs):
            rec = fut.result()
            with lock:
                done[rec["idx"]] = rec
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                n_new += 1
            if n_new % 100 == 0 or n_new == len(todo):
                spent = sum((r.get("cost_usd") or 0) for r in done.values())
                el = time.perf_counter() - t_start
                log.info("%d/%d queried  cost so far $%.4f  %.1f calls/s  ETA %.0fs", n_new, len(todo), spent,
                         n_new / el, (len(todo) - n_new) / max(n_new / el, 1e-9))

    recs = [done[i] for i in pos_idx if i in done]
    flat = pd.DataFrame([{
        "idx": r["idx"], "y_true": r.get("y_true"), "language": r.get("language"), "layer1_score": r.get("layer1_score"),
        "verdict": r.get("verdict"), "parse_ok": r.get("parse_ok"),
        "p_true": (r.get("verdict_probs") or {}).get("p_true"), "p_false": (r.get("verdict_probs") or {}).get("p_false"),
        "input_tokens": r.get("input_tokens"), "output_tokens": r.get("output_tokens"),
        "reasoning_tokens": r.get("reasoning_tokens"), "cost_usd": r.get("cost_usd"),
        "latency_s": r.get("latency_s"), "n_attempts": r.get("n_attempts"),
        "model_snapshot": (r.get("response") or {}).get("model_snapshot"),
        "system_fingerprint": (r.get("response") or {}).get("system_fingerprint"),
        "finish_reason": (r.get("response") or {}).get("finish_reason"), "openai_id": (r.get("response") or {}).get("openai_id"),
        "error": r.get("error"), "message_sha256": r.get("message_sha256"), "started_utc": r.get("started_utc"),
    } for r in recs]).sort_values("idx")
    flat.to_csv(paths["calls.csv"], index=False)

    totals = {"n_calls_recorded": len(recs), "n_layer1_positives": len(pos_idx),
              "cost_usd": float(flat["cost_usd"].fillna(0).sum()),
              "input_tokens": int(flat["input_tokens"].fillna(0).sum()), "output_tokens": int(flat["output_tokens"].fillna(0).sum()),
              "reasoning_tokens": int(pd.to_numeric(flat["reasoning_tokens"], errors="coerce").fillna(0).sum()),
              "n_errors": int(flat["error"].notna().sum()), "n_unparsed": int((~flat["parse_ok"].fillna(False).astype(bool)).sum()),
              "n_verdict_false": int((flat["verdict"] == False).sum()),  # noqa: E712
              "model_snapshots": sorted(set(flat["model_snapshot"].dropna())),
              "system_fingerprints": sorted(set(flat["system_fingerprint"].dropna())),
              "mean_latency_s": float(flat["latency_s"].dropna().mean()) if flat["latency_s"].notna().any() else None,
              "llm_seconds_total": float(flat["latency_s"].fillna(0).sum())}
    run_rec.update(finished_utc=now_utc(), n_queried=n_new, wall_s=time.perf_counter() - t_start)
    manifest["totals"] = totals
    paths["manifest.json"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    log.info("totals: %s", json.dumps({k: v for k, v in totals.items() if k != "system_fingerprints"}))

    if args.limit:
        per = totals["cost_usd"] / max(1, len(recs))
        log.info("DRY RUN: %d calls recorded, $%.6f/call -> projected $%.3f for all %d positives; "
                 "mean latency %.2fs -> ~%.0f min with %d workers. No predictions written.",
                 len(recs), per, per * len(pos_idx), len(pos_idx), totals["mean_latency_s"] or 0,
                 (totals["mean_latency_s"] or 0) * len(pos_idx) / max(1, args.workers) / 60, args.workers)
        return 0
    if len(recs) < len(pos_idx):
        log.warning("only %d of %d positives have a record; missing ones keep the layer-1 decision", len(recs), len(pos_idx))

    y_true = l1["y_true"].to_numpy()
    y_pred = l1["y_pred"].to_numpy().copy()
    for r in recs:
        if r.get("verdict") is False:
            y_pred[r["idx"]] = 0
    sent_true = flat[flat["y_true"] == 1]
    sent_false = flat[flat["y_true"] == 0]
    layer2_confusion = {"true_positives_sent": int(len(sent_true)),
                        "true_positives_wrongly_rejected": int((sent_true["verdict"] == False).sum()),  # noqa: E712
                        "false_positives_sent": int(len(sent_false)),
                        "false_positives_removed": int((sent_false["verdict"] == False).sum())}  # noqa: E712
    key = f"dlf_full_{run}"
    p_true = np.full(len(y_true), np.nan)
    for r in recs:
        vp = r.get("verdict_probs")
        if vp:
            p_true[r["idx"]] = vp["p_true"]
    save_predictions(out_dir, key, y_true=y_true, y_pred=y_pred, scores=p_true, languages=split.test["language"].to_numpy())
    l1_secs = json.load(open(out_dir / f"{args.layer1}.json"))["avg_inference_time_seconds"] * len(y_true)
    result = build_result(vectorizer="tfidf", model="dlf", embedding_model=args.model, y_true=y_true, y_pred=y_pred,
                          avg_inference_time_seconds=(l1_secs + totals["llm_seconds_total"]) / len(y_true),
                          languages=split.test["language"].to_numpy(),
                          extra={"baseline": key, "kind": "dlf", "layer1": args.layer1, "llm": args.model,
                                 "layer2_confusion": layer2_confusion, "llm_totals": totals,
                                 "note": "score column in the prediction CSV = LLM P(true) for layer-1 positives, NaN otherwise; "
                                         "avg_inference_time = (layer-1 time + sequential LLM latency) / all test messages",
                                 "artifacts": {k: str(v) for k, v in paths.items()}, "env": env_info(), "data": split.data_path})
    save_result(result, out_dir, key)
    log.info("DLF full: acc=%.4f P+=%.4f R+=%.4f F1+=%.4f macroF1=%.4f | layer 2: %s -> %s",
             result["accuracy"], result["metrics"]["1"]["precision"], result["metrics"]["1"]["recall"],
             result["metrics"]["1"]["f1-score"], result["extra"]["macro_f1"], layer2_confusion, key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
