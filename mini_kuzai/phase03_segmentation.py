#!/usr/bin/env python3
"""Turn-aware Phase 03 conversation segmentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


CONTEXT_LENGTH = 2048
SPECIAL_TOKEN_COUNT = 2


class OversizedPairError(ValueError):
    """Raised when one complete user/assistant pair cannot fit the context."""

    def __init__(
        self,
        *,
        pair_index: int,
        token_count: int,
        context_length: int,
    ):
        self.pair_index = pair_index
        self.token_count = token_count
        self.context_length = context_length
        super().__init__(
            "Conversation pair {} requires {} tokens, context is {}".format(
                pair_index,
                token_count,
                context_length,
            )
        )


@dataclass(frozen=True)
class ConversationSegment:
    segment_index: int
    pair_start: int
    pair_end: int
    messages: tuple[dict, ...]
    token_count: int


def _copy_messages(messages):
    return tuple(
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in messages
    )


def _token_count(
    messages,
    *,
    serialize_messages: Callable,
    count_text: Callable[[str], int],
    special_token_count: int,
) -> int:
    return (
        count_text(
            serialize_messages(messages)
        )
        + special_token_count
    )


def pair_token_counts(
    messages,
    *,
    serialize_messages: Callable,
    validate_messages: Callable,
    count_text: Callable[[str], int],
    special_token_count: int = SPECIAL_TOKEN_COUNT,
) -> list[int]:
    validate_messages(messages)

    return [
        _token_count(
            messages[index:index + 2],
            serialize_messages=serialize_messages,
            count_text=count_text,
            special_token_count=special_token_count,
        )
        for index in range(0, len(messages), 2)
    ]


def segment_messages(
    messages,
    *,
    serialize_messages: Callable,
    validate_messages: Callable,
    count_text: Callable[[str], int],
    context_length: int = CONTEXT_LENGTH,
    special_token_count: int = SPECIAL_TOKEN_COUNT,
) -> list[ConversationSegment]:
    """Greedily pack complete user/assistant pairs into context-safe segments."""

    if context_length <= special_token_count:
        raise ValueError(
            "Context length must exceed special-token overhead"
        )

    validate_messages(messages)

    segments: list[ConversationSegment] = []
    current: list[dict] = []
    pair_start = 0
    current_token_count = 0
    pair_count = len(messages) // 2

    for pair_index in range(pair_count):
        pair = messages[
            pair_index * 2:
            pair_index * 2 + 2
        ]

        pair_tokens = _token_count(
            pair,
            serialize_messages=serialize_messages,
            count_text=count_text,
            special_token_count=special_token_count,
        )

        if pair_tokens > context_length:
            raise OversizedPairError(
                pair_index=pair_index,
                token_count=pair_tokens,
                context_length=context_length,
            )

        candidate = [
            *current,
            *pair,
        ]

        candidate_tokens = (
            _token_count(
                candidate,
                serialize_messages=serialize_messages,
                count_text=count_text,
                special_token_count=special_token_count,
            )
            if current else pair_tokens
        )

        if (
            current
            and candidate_tokens > context_length
        ):
            current_tokens = current_token_count

            segments.append(
                ConversationSegment(
                    segment_index=len(segments),
                    pair_start=pair_start,
                    pair_end=pair_index,
                    messages=_copy_messages(current),
                    token_count=current_tokens,
                )
            )

            current = list(pair)
            current_token_count = pair_tokens
            pair_start = pair_index
        else:
            current = candidate
            current_token_count = candidate_tokens

    if current:
        current_tokens = current_token_count

        segments.append(
            ConversationSegment(
                segment_index=len(segments),
                pair_start=pair_start,
                pair_end=pair_count,
                messages=_copy_messages(current),
                token_count=current_tokens,
            )
        )

    flattened = [
        message
        for segment in segments
        for message in segment.messages
    ]

    expected = [
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in messages
    ]

    if flattened != expected:
        raise RuntimeError(
            "Segmentation changed or reordered conversation messages"
        )

    if any(
        segment.token_count > context_length
        for segment in segments
    ):
        raise RuntimeError(
            "Segmentation produced an over-context segment"
        )

    return segments
