#!/usr/bin/env python3
"""Canonical Phase 03 conversation serialization."""

from __future__ import annotations


USER_HEADER = "USER:\n"
ASSISTANT_HEADER = "MINI-KUZAI:\n"
TURN_SEPARATOR = "\n\n"


def validate_messages(messages):
    if (
        not isinstance(messages, list)
        or not messages
        or len(messages) % 2
    ):
        raise ValueError(
            "Conversation must contain complete user/assistant pairs"
        )

    expected_roles = (
        ["user", "assistant"]
        * (len(messages) // 2)
    )

    roles = [
        message.get("role")
        if isinstance(message, dict)
        else None
        for message in messages
    ]

    if roles != expected_roles:
        raise ValueError(
            "Conversation roles must alternate user/assistant"
        )

    for message in messages:
        content = message.get("content")

        if (
            not isinstance(content, str)
            or not content.strip()
        ):
            raise ValueError(
                "Conversation content must be non-empty text"
            )


def serialize_messages(messages):
    validate_messages(messages)

    sections = []

    for message in messages:
        if message["role"] == "user":
            header = USER_HEADER
        else:
            header = ASSISTANT_HEADER

        sections.append(
            header + message["content"]
        )

    return TURN_SEPARATOR.join(
        sections
    )


def serialize_user_prompt(text):
    if (
        not isinstance(text, str)
        or not text.strip()
    ):
        raise ValueError(
            "User prompt must be non-empty text"
        )

    return (
        USER_HEADER
        + text
        + TURN_SEPARATOR
        + ASSISTANT_HEADER
    )
