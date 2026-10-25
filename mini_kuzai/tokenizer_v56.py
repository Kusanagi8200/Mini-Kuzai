#!/usr/bin/env python3
"""Mini-Kuzai Phase 03 V56 tokenizer candidates.

Research implementation only.

Candidate families:

- byte_baseline
- byte_bpe_whitespace
- byte_bpe_unicode

All candidates are:

- UTF-8 lossless;
- deterministic;
- byte-fallback capable;
- free of external tokenizer dependencies.

No tokenizer is selected or frozen by this module.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence


SPECIAL_TOKENS = {
    "<pad>": 0,
    "<bos>": 1,
    "<eos>": 2,
}

SPECIAL_IDS = frozenset(SPECIAL_TOKENS.values())

BYTE_OFFSET = len(SPECIAL_TOKENS)
BYTE_COUNT = 256
BASE_VOCAB_SIZE = BYTE_OFFSET + BYTE_COUNT

PRETOKENIZER_WHITESPACE = "whitespace"
PRETOKENIZER_UNICODE = "unicode"

CANDIDATE_NAMES = (
    "byte_baseline",
    "byte_bpe_whitespace",
    "byte_bpe_unicode",
)


def _require_text(text: str) -> None:
    if not isinstance(text, str):
        raise TypeError("Tokenizer input must be str")


def _base_id(byte_value: int) -> int:
    return BYTE_OFFSET + byte_value


def _base_bytes(token_id: int) -> bytes:
    if not BYTE_OFFSET <= token_id < BASE_VOCAB_SIZE:
        raise ValueError(f"Not a base-byte token id: {token_id}")
    return bytes([token_id - BYTE_OFFSET])


def _split_text(text: str, mode: str) -> list[str]:
    _require_text(text)

    if not text:
        return []

    if mode == PRETOKENIZER_WHITESPACE:
        chunks = re.findall(
            r"\s+|[^\s]+",
            text,
            flags=re.UNICODE,
        )

    elif mode == PRETOKENIZER_UNICODE:
        chunks = re.findall(
            r"\s+|\w+|[^\w\s]+",
            text,
            flags=re.UNICODE,
        )

    else:
        raise ValueError(
            f"Unsupported pretokenizer mode: {mode}"
        )

    if "".join(chunks) != text:
        raise RuntimeError(
            "Pretokenizer failed lossless segmentation"
        )

    return chunks


def _bytes_to_base_ids(blob: bytes) -> tuple[int, ...]:
    return tuple(_base_id(value) for value in blob)


def _merge_sequence(
    sequence: Sequence[int],
    pair: tuple[int, int],
    new_id: int,
) -> tuple[int, ...]:
    if len(sequence) < 2:
        return tuple(sequence)

    left, right = pair
    output: list[int] = []

    index = 0

    while index < len(sequence):
        if (
            index + 1 < len(sequence)
            and sequence[index] == left
            and sequence[index + 1] == right
        ):
            output.append(new_id)
            index += 2
        else:
            output.append(sequence[index])
            index += 1

    return tuple(output)


@dataclass(frozen=True)
class MergeRule:
    left_id: int
    right_id: int
    new_id: int

    def to_dict(self) -> dict[str, int]:
        return {
            "left_id": self.left_id,
            "right_id": self.right_id,
            "new_id": self.new_id,
        }

    @classmethod
    def from_dict(cls, value: dict) -> "MergeRule":
        return cls(
            left_id=int(value["left_id"]),
            right_id=int(value["right_id"]),
            new_id=int(value["new_id"]),
        )


class ByteTokenizer:
    """Universal UTF-8 byte baseline."""

    family = "byte_baseline"
    byte_fallback = True
    external_dependencies = 0

    @property
    def vocab_size(self) -> int:
        return BASE_VOCAB_SIZE

    def encode(
        self,
        text: str,
        *,
        add_bos: bool = False,
        add_eos: bool = False,
    ) -> list[int]:
        _require_text(text)

        ids = [
            _base_id(value)
            for value in text.encode("utf-8")
        ]

        if add_bos:
            ids.insert(0, SPECIAL_TOKENS["<bos>"])

        if add_eos:
            ids.append(SPECIAL_TOKENS["<eos>"])

        return ids

    def decode(
        self,
        ids: Iterable[int],
        *,
        skip_special: bool = True,
    ) -> str:
        payload = bytearray()

        for token_id in ids:
            token_id = int(token_id)

            if token_id in SPECIAL_IDS:
                if skip_special:
                    continue

                raise ValueError(
                    "Special tokens cannot be converted "
                    "to source text"
                )

            payload.extend(_base_bytes(token_id))

        return bytes(payload).decode("utf-8")

    def to_dict(self) -> dict:
        return {
            "format_version": 1,
            "family": self.family,
            "special_tokens": dict(SPECIAL_TOKENS),
            "byte_offset": BYTE_OFFSET,
            "base_vocab_size": BASE_VOCAB_SIZE,
            "byte_fallback": True,
            "merges": [],
        }

    def fingerprint(self) -> str:
        payload = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()


class ByteBPETokenizer:
    """Deterministic byte-level BPE with fixed segmentation."""

    byte_fallback = True
    external_dependencies = 0

    def __init__(
        self,
        *,
        pretokenizer: str,
        merges: Sequence[MergeRule],
    ):
        if pretokenizer not in {
            PRETOKENIZER_WHITESPACE,
            PRETOKENIZER_UNICODE,
        }:
            raise ValueError(
                f"Unsupported pretokenizer: {pretokenizer}"
            )

        self.pretokenizer = pretokenizer
        self.merges = tuple(merges)

        self._token_bytes: dict[int, bytes] = {
            _base_id(value): bytes([value])
            for value in range(BYTE_COUNT)
        }

        seen_pairs: set[tuple[int, int]] = set()

        for index, merge in enumerate(self.merges):
            expected_new_id = BASE_VOCAB_SIZE + index

            if merge.new_id != expected_new_id:
                raise ValueError(
                    "Non-canonical BPE merge id sequence"
                )

            pair = (
                merge.left_id,
                merge.right_id,
            )

            if pair in seen_pairs:
                raise ValueError(
                    "Duplicate BPE merge pair"
                )

            if (
                merge.left_id not in self._token_bytes
                or merge.right_id not in self._token_bytes
            ):
                raise ValueError(
                    "BPE merge references unknown token"
                )

            self._token_bytes[merge.new_id] = (
                self._token_bytes[merge.left_id]
                + self._token_bytes[merge.right_id]
            )

            seen_pairs.add(pair)

    @property
    def family(self) -> str:
        return f"byte_bpe_{self.pretokenizer}"

    @property
    def vocab_size(self) -> int:
        return BASE_VOCAB_SIZE + len(self.merges)

    @classmethod
    def train(
        cls,
        texts: Iterable[str],
        *,
        target_vocab_size: int,
        pretokenizer: str,
        min_pair_frequency: int = 2,
    ) -> "ByteBPETokenizer":
        if target_vocab_size < BASE_VOCAB_SIZE:
            raise ValueError(
                "target_vocab_size cannot be smaller "
                "than the byte fallback vocabulary"
            )

        if min_pair_frequency < 1:
            raise ValueError(
                "min_pair_frequency must be >= 1"
            )

        sequence_counts: Counter[
            tuple[int, ...]
        ] = Counter()

        observed_text = False

        for text in texts:
            _require_text(text)
            observed_text = True

            for chunk in _split_text(
                text,
                pretokenizer,
            ):
                sequence = _bytes_to_base_ids(
                    chunk.encode("utf-8")
                )

                if sequence:
                    sequence_counts[sequence] += 1

        if not observed_text:
            raise ValueError(
                "Tokenizer training corpus is empty"
            )

        token_bytes: dict[int, bytes] = {
            _base_id(value): bytes([value])
            for value in range(BYTE_COUNT)
        }

        merges: list[MergeRule] = []

        while (
            BASE_VOCAB_SIZE + len(merges)
            < target_vocab_size
        ):
            pair_counts: Counter[
                tuple[int, int]
            ] = Counter()

            for sequence, sequence_frequency in (
                sequence_counts.items()
            ):
                for left, right in zip(
                    sequence,
                    sequence[1:],
                ):
                    pair_counts[(left, right)] += (
                        sequence_frequency
                    )

            if not pair_counts:
                break

            highest_frequency = max(
                pair_counts.values()
            )

            if highest_frequency < min_pair_frequency:
                break

            candidates = [
                pair
                for pair, frequency
                in pair_counts.items()
                if frequency == highest_frequency
            ]

            pair = min(
                candidates,
                key=lambda current: (
                    token_bytes[current[0]]
                    + token_bytes[current[1]],
                    current[0],
                    current[1],
                ),
            )

            new_id = (
                BASE_VOCAB_SIZE
                + len(merges)
            )

            rule = MergeRule(
                left_id=pair[0],
                right_id=pair[1],
                new_id=new_id,
            )

            merged_counts: Counter[
                tuple[int, ...]
            ] = Counter()

            for sequence, frequency in (
                sequence_counts.items()
            ):
                merged = _merge_sequence(
                    sequence,
                    pair,
                    new_id,
                )

                merged_counts[merged] += frequency

            sequence_counts = merged_counts

            token_bytes[new_id] = (
                token_bytes[pair[0]]
                + token_bytes[pair[1]]
            )

            merges.append(rule)

        return cls(
            pretokenizer=pretokenizer,
            merges=merges,
        )

    def _encode_chunk(
        self,
        chunk: str,
    ) -> tuple[int, ...]:
        sequence = _bytes_to_base_ids(
            chunk.encode("utf-8")
        )

        for merge in self.merges:
            sequence = _merge_sequence(
                sequence,
                (
                    merge.left_id,
                    merge.right_id,
                ),
                merge.new_id,
            )

        return sequence

    def encode(
        self,
        text: str,
        *,
        add_bos: bool = False,
        add_eos: bool = False,
    ) -> list[int]:
        _require_text(text)

        ids: list[int] = []

        for chunk in _split_text(
            text,
            self.pretokenizer,
        ):
            ids.extend(
                self._encode_chunk(chunk)
            )

        if add_bos:
            ids.insert(
                0,
                SPECIAL_TOKENS["<bos>"],
            )

        if add_eos:
            ids.append(
                SPECIAL_TOKENS["<eos>"]
            )

        return ids

    def decode(
        self,
        ids: Iterable[int],
        *,
        skip_special: bool = True,
    ) -> str:
        payload = bytearray()

        for token_id in ids:
            token_id = int(token_id)

            if token_id in SPECIAL_IDS:
                if skip_special:
                    continue

                raise ValueError(
                    "Special tokens cannot be converted "
                    "to source text"
                )

            token_bytes = self._token_bytes.get(
                token_id
            )

            if token_bytes is None:
                raise ValueError(
                    f"Unknown token id: {token_id}"
                )

            payload.extend(token_bytes)

        return bytes(payload).decode("utf-8")

    def to_dict(self) -> dict:
        return {
            "format_version": 1,
            "family": self.family,
            "pretokenizer": self.pretokenizer,
            "special_tokens": dict(SPECIAL_TOKENS),
            "byte_offset": BYTE_OFFSET,
            "base_vocab_size": BASE_VOCAB_SIZE,
            "vocab_size": self.vocab_size,
            "byte_fallback": True,
            "merges": [
                rule.to_dict()
                for rule in self.merges
            ],
        }

    @classmethod
    def from_dict(
        cls,
        value: dict,
    ) -> "ByteBPETokenizer":
        if value.get("format_version") != 1:
            raise ValueError(
                "Unsupported tokenizer format version"
            )

        if value.get("special_tokens") != SPECIAL_TOKENS:
            raise ValueError(
                "Unexpected special-token mapping"
            )

        if value.get("byte_offset") != BYTE_OFFSET:
            raise ValueError(
                "Unexpected byte offset"
            )

        merges = [
            MergeRule.from_dict(item)
            for item in value.get(
                "merges",
                [],
            )
        ]

        tokenizer = cls(
            pretokenizer=value["pretokenizer"],
            merges=merges,
        )

        if (
            value.get("vocab_size")
            != tokenizer.vocab_size
        ):
            raise ValueError(
                "Serialized vocabulary size mismatch"
            )

        return tokenizer

    def fingerprint(self) -> str:
        payload = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()


def build_candidate(
    name: str,
    *,
    texts: Iterable[str] | None = None,
    target_vocab_size: int = 320,
    min_pair_frequency: int = 2,
):
    if name == "byte_baseline":
        return ByteTokenizer()

    if texts is None:
        raise ValueError(
            "BPE candidates require training texts"
        )

    if name == "byte_bpe_whitespace":
        mode = PRETOKENIZER_WHITESPACE

    elif name == "byte_bpe_unicode":
        mode = PRETOKENIZER_UNICODE

    else:
        raise ValueError(
            f"Unknown V56 tokenizer candidate: {name}"
        )

    return ByteBPETokenizer.train(
        texts,
        target_vocab_size=target_vocab_size,
        pretokenizer=mode,
        min_pair_frequency=min_pair_frequency,
    )
