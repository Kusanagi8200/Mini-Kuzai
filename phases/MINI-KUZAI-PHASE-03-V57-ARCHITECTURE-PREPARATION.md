# MINI-KUZAI PHASE 03 - V57 ARCHITECTURE PREPARATION

Status --> TOKEN BUDGET AND ARCHITECTURE CANDIDATE AUDIT

V57 begins after the V56 tokenizer freeze.

The purpose of this stage is to establish the real serialized token budget
before selecting the Phase 03 model scale.

## Conversation serialization v1

The canonical conversational representation is now frozen.

User turns begin with -->

USER -->

Mini-Kuzai turns begin with -->

MINI-KUZAI -->

Turns are separated by one blank line.

The tokenizer BOS token is added at the beginning of each complete
conversation and EOS is added at the end.

The role labels are ordinary tokenizer text rather than new special tokens.
This preserves the frozen V56 vocabulary.

## Populations measured

The V57 audit measures three distinct public populations.

Canonical TRAIN -->

107 conversations already admitted to the controlled TRAIN split.

V44 provisional SmolTalk -->

1139 public conversations retained only as a provisional candidate population.
They are not automatically approved for model training.

Full SmolTalk v0.4 reservoir -->

8000 public conversations used only as an upper-bound data reference.

VALIDATION, BLIND TEST and private conversation data remain excluded.

## Context candidates

V57 measures serialized conversation coverage at -->

1024
2048
4096

The automatic context recommendation is the smallest candidate covering at
least 95 percent of both canonical TRAIN and the V44 provisional population.

A recommendation is not yet a freeze.

## Architecture family under study

Decoder-only autoregressive Transformer.

Planned common properties -->

pre-norm
causal multi-head self-attention
GELU MLP
MLP expansion ratio 4
learned positional embeddings
tied token embedding and LM head
bias-free attention projections
biased MLP linear layers

Four initial scales are measured -->

micro --> d_model 128 / 4 heads / 4 layers
small --> d_model 192 / 6 heads / 6 layers
medium --> d_model 256 / 8 heads / 8 layers
large --> d_model 320 / 10 heads / 10 layers

Parameter counts are calculated against the recommended context length.

## Decision boundary

V57 does not yet freeze model scale.

The final architecture must be selected with knowledge of -->

serialized training token volume
context coverage
training-mixture decision
parameter-to-data ratio
RTX 5060 8 GB execution constraints

Training remains unauthorized.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
