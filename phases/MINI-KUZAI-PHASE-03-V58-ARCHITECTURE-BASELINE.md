# MINI-KUZAI PHASE 03 - V58 ARCHITECTURE BASELINE

Status: EXPERIMENTAL BASELINE FROZEN

V58 establishes a reproducible experimental architecture baseline for the
first Phase 03 model experiments.

It does not authorize model training and it is not an irreversible final
architecture decision.

## Baseline architecture

Decoder-only autoregressive Transformer.

- vocabulary: 1024
- context length: 2048
- d_model: 128
- attention heads: 4
- head dimension: 32
- transformer layers: 4
- MLP dimension: 512
- activation: GELU
- normalization: pre-LayerNorm
- learned positional embeddings
- tied token embedding and LM head
- bias-free attention projections
- biased MLP linear layers
- dropout: 0
- right padding
- parameters: 1,184,512

## Why context 2048

The canonical controlled TRAIN corpus is fully covered at context 2048.

The longer public SmolTalk candidate population is not fully covered without
segmentation. V58 therefore treats segmentation only as a feasibility
calculation.

The actual training-data segmentation implementation is not frozen here.

In particular, the final implementation must preserve conversational
structure and role information and must avoid treating arbitrary token
windowing as an already validated training policy.

Using context 4096 would cover the current public reservoir without
segmentation but would approximately quadruple the attention matrix cost
relative to context 2048.

## Why the micro baseline

The final Phase 03 training mixture is not yet frozen.

The currently available unique public-data envelope does not justify
committing permanently to one of the larger candidate architectures.

The micro configuration is therefore frozen only as the first reproducible
experimental baseline.

A later corpus expansion or training-mixture decision may justify a new
architecture version.

## GPU validation

The V58 implementation and CUDA smoke test pass on the local NVIDIA GeForce
RTX 5060 Laptop GPU.

The current CUDA environment is operational with PyTorch CUDA support and
BF16 capability.

## Decision boundary

V58 freezes:

- the experimental micro architecture baseline
- context length 2048 for that baseline
- the implementation used for reproducible model experiments

V58 does not freeze:

- the final training mixture
- the final public-data selection
- the final conversation segmentation implementation
- an irreversible final model scale

Model training remains NOT AUTHORIZED and NOT STARTED.
