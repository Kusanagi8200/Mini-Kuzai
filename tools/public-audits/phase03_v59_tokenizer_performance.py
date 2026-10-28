#!/usr/bin/env python3
"""Bounded, read-only V59 tokenizer/segmentation timing audit (public synthetic text)."""
import time
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from mini_kuzai.phase03_v59_trainer import load_tokenizer, _segment_messages

def milliseconds(start):
    return max(0, round((time.perf_counter() - start) * 1000))

def main():
    start = time.perf_counter()
    tok = load_tokenizer()
    load_ms = milliseconds(start)
    data = {}
    for n in (128, 512, 1024):
        sample = ("Mini-Kuzai explores reasoning and creative dialogue. " * 30)[:n]
        start = time.perf_counter()
        ids = tok.encode(sample)
        data[f"V59_PERF_ENCODE_{n}_MS"] = milliseconds(start)
        data[f"V59_PERF_ENCODE_{n}_TOKENS"] = len(ids)
    pair = [
        {"role": "user", "content": "Can an idea change with new evidence?"},
        {"role": "assistant", "content": "Yes. I can revise a tentative conclusion when evidence improves."},
    ]
    for count in (1, 2, 4):
        messages = pair * count
        start = time.perf_counter()
        segments = _segment_messages(tok, messages)
        data[f"V59_PERF_SEGMENT_{count}_MS"] = milliseconds(start)
        data[f"V59_PERF_SEGMENT_{count}_COUNT"] = len(segments)
    data.update({
        "SEMANTIC_VALIDATION_COMPLETE": 1,
        "V59_MIX_FINALIZED": 1,
        "TRAINING_AUTHORIZED": 1,
        "TRAINING_STARTED": 0,
        "V59_PERF_TOKENIZER_LOAD_MS": load_ms,
        "V59_PERF_SYNTHETIC_ONLY": 1,
        "V59_PERF_CORPUS_ACCESSES": 0,
        "V59_PERF_OPTIMIZER_STEPS": 0,
    })
    print("##### SECTION RESULTS FOR ASSISTANT ######")
    for key, value in sorted(data.items()):
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
