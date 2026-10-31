#!/usr/bin/env python3
"""Private local V63 generation and human semantic review.

Never publishes raw prompts, generations, token IDs or review annotations.
Only the separate vetted GOGIT audit may publish numeric aggregates.
No training and no BLIND TEST access.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mini_kuzai import phase03_v62_trainer as T

PRIVATE = Path("/root/Mini-Kuzai/runs/v63-semantic-generation-review-001")
SAMPLES = PRIVATE / "samples-private.json"
REVIEWS = PRIVATE / "ratings-private.json"
SEEDS = (6301, 6303, 6305, 6308)
N_PROMPTS = 6
MAX_NEW = 96
SAMPLE_COUNT = len(SEEDS) * N_PROMPTS
SCHEMA = "v63-human-review-001"
CRITERIA = ("relevance", "coherence", "cognition", "persona")
OPTIONAL = frozenset(("cognition", "persona"))


def canonical_json(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha(value) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def safe_dir() -> None:
    PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    if PRIVATE.is_symlink() or not PRIVATE.is_dir():
        raise RuntimeError("Unsafe private review directory")
    os.chmod(PRIVATE, 0o700)


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or unsafe private JSON: {path.name}")
    if path.stat().st_mode & 0o077:
        raise RuntimeError(f"Private JSON is accessible by other users: {path.name}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Review JSON must be an object")
    return data


def atomic_private(path: Path, data: dict) -> None:
    safe_dir()
    if path.exists():
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("Unsafe existing private review file")
        backups = PRIVATE / "backups"
        backups.mkdir(exist_ok=True, mode=0o700)
        if backups.is_symlink() or not backups.is_dir():
            raise RuntimeError("Unsafe private review backup directory")
        os.chmod(backups, 0o700)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        copy = backups / f"{path.name}.{stamp}.bak"
        shutil.copy2(path, copy)
        os.chmod(copy, 0o600)
    fd, temporary = tempfile.mkstemp(prefix=".atomic-", dir=PRIVATE)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical_json(data) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_ablation_helper():
    path = (
        REPO / "tools" / "public-audits"
        / "phase03_v63_decoding_robustness_001.py"
    )
    spec = importlib.util.spec_from_file_location("v63_review_robustness", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("V63 robustness helper unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_screen(text: str) -> str:
    return "".join(
        ch if ch.isprintable() or ch in "\n\t" else f"\\u{ord(ch):04x}"
        for ch in text
    )


def check_samples(samples: dict) -> list[dict]:
    if (
        samples.get("schema") != SCHEMA
        or samples.get("seeds") != list(SEEDS)
        or samples.get("decoder") != "TOPP"
        or samples.get("max_new") != MAX_NEW
    ):
        raise RuntimeError("Samples do not match the frozen V63 review protocol")
    entries = samples.get("entries")
    if not isinstance(entries, list) or len(entries) != SAMPLE_COUNT:
        raise RuntimeError("Private review sample count mismatch")
    if samples.get("digest") != sha({
        key: samples[key] for key in ("schema", "seeds", "decoder", "max_new", "entries")
    }):
        raise RuntimeError("Private samples digest mismatch")
    expected = [(s, p) for s in SEEDS for p in range(N_PROMPTS)]
    for index, (entry, (seed, slot)) in enumerate(zip(entries, expected), 1):
        if (
            not isinstance(entry, dict)
            or entry.get("id") != f"S{index:03d}"
            or entry.get("seed") != seed
            or entry.get("slot") != slot
            or not isinstance(entry.get("prompt"), str)
            or not isinstance(entry.get("output"), str)
            or not isinstance(entry.get("tokens"), list)
            or not 0 < len(entry["tokens"]) <= MAX_NEW
            or not isinstance(entry.get("utf8_valid"), bool)
            or not isinstance(entry.get("eos"), bool)
            or not isinstance(entry.get("role_leak"), bool)
            or entry["eos"] != (entry["tokens"][-1] == T.EOS_ID)
        ):
            raise RuntimeError(f"Invalid private review sample: S{index:03d}")
    return entries


def check_rating(rating: dict) -> bool:
    if not isinstance(rating, dict) or rating.get("human_confirmed") is not True:
        return False
    if set(rating) != set(CRITERIA) | {"human_confirmed"}:
        return False
    for field in CRITERIA:
        score = rating[field]
        if type(score) is not int or score not in (0, 1, 2, 3):
            return False
        if score == 3 and field not in OPTIONAL:
            return False
    return True


def load_review_state(samples: dict) -> dict:
    if not REVIEWS.exists():
        return {"schema": SCHEMA, "samples_digest": samples["digest"], "ratings": {}}
    state = read_json(REVIEWS)
    if (
        state.get("schema") != SCHEMA
        or state.get("samples_digest") != samples["digest"]
        or not isinstance(state.get("ratings"), dict)
        or set(state) != {"schema", "samples_digest", "ratings"}
    ):
        raise RuntimeError("Private ratings file does not match the samples")
    ids = {entry["id"] for entry in samples["entries"]}
    if not set(state["ratings"]).issubset(ids):
        raise RuntimeError("Unexpected rated sample identifier")
    if not all(check_rating(x) for x in state["ratings"].values()):
        raise RuntimeError("Invalid human ratings record")
    return state


def completed_review():
    samples = read_json(SAMPLES)
    entries = check_samples(samples)
    state = load_review_state(samples)
    if len(state["ratings"]) != SAMPLE_COUNT:
        raise RuntimeError("Human semantic review incomplete; GOGIT is blocked")
    return entries, state["ratings"]


def generate():
    safe_dir()
    if SAMPLES.exists():
        samples = read_json(SAMPLES)
        check_samples(samples)
        print("SAMPLES: PRIVATE_ALREADY_PREPARED")
        return
    helper = load_ablation_helper()
    model, tokenizer, device, prompts = helper.read_model_and_prompts()
    if len(prompts) != N_PROMPTS:
        raise RuntimeError("Frozen V63 prompt count changed")
    full = [list(prompt) for _ in SEEDS for prompt in prompts]
    lengths = [len(prompt) for _ in SEEDS for prompt in prompts]
    complete = [False] * len(full)
    rng = [
        torch.Generator(device="cuda").manual_seed(seed) for seed in SEEDS
    ]
    with torch.inference_mode():
        for _ in range(MAX_NEW):
            active = [i for i in range(len(full)) if not complete[i]]
            if not active:
                break
            inputs = helper.pad_right([full[i] for i in active], device)
            ends = torch.as_tensor(
                [len(full[i]) - 1 for i in active],
                dtype=torch.long, device=device,
            )
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits = model(inputs)[
                    torch.arange(len(active), device=device), ends
                ].float()
            tokens = [None] * len(active)
            for seed_index in range(len(SEEDS)):
                positions = [
                    j for j, absolute in enumerate(active)
                    if absolute // N_PROMPTS == seed_index
                ]
                if positions:
                    drawn = helper.sample_logits(
                        logits[positions], "TOPP", rng[seed_index]
                    ).tolist()
                    for position, token in zip(positions, drawn):
                        tokens[position] = int(token)
            if any(token is None for token in tokens):
                raise RuntimeError("Incomplete GPU sample batch")
            for j, absolute in enumerate(active):
                full[absolute].append(tokens[j])
                if tokens[j] == T.EOS_ID:
                    complete[absolute] = True

    entries = []
    for index, entire in enumerate(full):
        slot = index % N_PROMPTS
        output_ids = entire[lengths[index]:]
        if not 0 < len(output_ids) <= MAX_NEW:
            raise RuntimeError("Invalid frozen sample length")
        output, valid = T._decode_generated_probe_text(tokenizer, output_ids)
        entries.append({
            "id": f"S{index + 1:03d}",
            "seed": SEEDS[index // N_PROMPTS],
            "slot": slot,
            "prompt": tokenizer.decode(prompts[slot]),
            "output": output,
            "tokens": output_ids,
            "eos": bool(output_ids[-1] == T.EOS_ID),
            "utf8_valid": bool(valid),
            "role_leak": bool(
                "USER:\n" in output or "MINI-KUZAI:\n" in output
            ),
        })
    base = {
        "schema": SCHEMA, "seeds": list(SEEDS),
        "decoder": "TOPP", "max_new": MAX_NEW, "entries": entries,
    }
    base["digest"] = sha(base)
    check_samples(base)
    atomic_private(SAMPLES, base)
    print(f"SAMPLES: PRIVATE_READY ({len(entries)}); raw text remains outside Git")


def review():
    samples = read_json(SAMPLES)
    entries = check_samples(samples)
    state = load_review_state(samples)
    print("REVIEW: LOCAL HUMAN SCORING - 0=insufficient, 1=partial, 2=adequate")
    print("Cognition/persona may use '-' if the prompt does not test the criterion.")
    print("This is single-turn evaluation, not a multi-turn continuity review.")
    confirmation = input("Type CONFIRMER to start subjective human evaluation: ").strip()
    if confirmation != "CONFIRMER":
        print("REVIEW: PAUSED, no automatic scores assigned")
        return False
    for entry in entries:
        if entry["id"] in state["ratings"]:
            continue
        print(f"\n--- {entry['id']} / {SAMPLE_COUNT} ---")
        print(f"PROMPT:\n{safe_screen(entry['prompt'])}")
        print(f"RESPONSE:\n{safe_screen(entry['output'])}")
        print(f"EOS={int(entry['eos'])} UTF8_VALID={int(entry['utf8_valid'])}")
        while True:
            raw = input(
                "Ratings relevance coherence cognition persona "
                "(0/1/2; '-' only cognition/persona), or q: "
            ).strip()
            if raw.lower() == "q":
                print("REVIEW: PAUSED with all previous ratings saved privately")
                return False
            parts = raw.split()
            if len(parts) != len(CRITERIA):
                print("Invalid number of ratings")
                continue
            try:
                scores = [
                    3 if token == "-" else int(token)
                    for token in parts
                ]
            except ValueError:
                print("Ratings must be 0, 1, 2 or '-'")
                continue
            result = dict(zip(CRITERIA, scores))
            result["human_confirmed"] = True
            if check_rating(result):
                state["ratings"][entry["id"]] = result
                atomic_private(REVIEWS, state)
                break
            print("Invalid rating: relevance/coherence cannot be N/A")
    print(f"REVIEW: COMPLETE ({SAMPLE_COUNT}/{SAMPLE_COUNT})")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("prepare", "review", "check", "all")
    )
    args = parser.parse_args()
    if args.action in ("prepare", "all"):
        generate()
    if args.action in ("review", "all"):
        if not review():
            return 2
    if args.action in ("check", "all"):
        entries, ratings = completed_review()
        print(f"HUMAN_RATINGS: COMPLETE ({len(ratings)}/{len(entries)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
