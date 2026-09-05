# MINI-KUZAI PHASE 02

Phase 02 focuses on inference engineering, performance measurement, KV caching, GPU profiling, and controlled inference experiments while preserving the frozen Phase 01 baseline.

## Current milestone

The Phase 02 milestone establishes a reproducible no-cache benchmark and implements a functionally equivalent KV cache without modifying or retraining the Phase 01 weights.

### Step 69 - baseline benchmark

Reference model:

```text
Transformer blocks   : 2
Attention heads      : 2
Embedding dimension  : 8
Hidden dimension     : 32
Vocabulary           : 26
Parameters           : 2368
Parameter storage    : 9.25 KB
```

First cold generation measurement:

```text
Prompt               : mini kuzai
Generated            : mini kuzai uses a model <eos>
New tokens           : 4
Generation time      : 0.300817 s
Tokens / second      : 13.30
KV cache             : NO
```

This cold result was not accepted as the stable performance baseline because CUDA/PyTorch initialization dominated the measurement.

### Step 70 - stabilized no-cache benchmark

Protocol:

```text
Prompt tokens        : 2
Fixed new tokens     : 4
Warmup runs          : 10
Measured runs        : 50
KV cache             : NO
```

Validated warm results:

```text
Mean time            : 0.002237 s
Median time          : 0.002233 s
Std deviation        : 0.000019 s
Mean tokens / second : 1788.42
Median tokens/second : 1791.22
```

This is the Phase 02 no-cache reference for the four-token decode benchmark.

### Step 71 - autoregressive recomputation trace

For four generated tokens, the original model recomputes sequence lengths:

```text
2, 3, 4, 5
```

Measured work:

```text
No cache positions / layer      : 14
Ideal cache positions / layer   : 5
Position reduction              : 64.29%

No cache attention cells / head : 54
Ideal cache cells / head        : 16
Attention reduction             : 70.37%
```

### Step 72 - KV cache equivalence

A new Phase 02 implementation, `MiniKuzaiKVCache`, reuses cached key/value tensors for prior tokens and processes only the new token after prompt prefill.

The original Phase 01 checkpoint loads with `strict=True` and no additional trainable weights.

Validated equivalence:

```text
Step 1 max logit diff : 0.0000000000
Step 2 max logit diff : 0.0000007153
Step 3 max logit diff : 0.0000009537
Step 4 max logit diff : 0.0000009537

Cache lengths:
[2, 2]
[3, 3]
[4, 4]
[5, 5]

Baseline generation  : mini kuzai uses a model <eos>
KV-cache generation  : mini kuzai uses a model <eos>
Tokens identical     : True
Maximum logit error  : 0.0000009537
```

The remaining numerical difference is at float32 rounding scale and does not alter token decisions in this test.

## Phase 02 status

```text
PHASE 01 checkpoint preserved : YES
KV cache implemented          : YES
Weight changes                : NO
Retraining                    : NO
Functional equivalence        : VALIDATED
Performance comparison        : DEFERRED
```

The controlled no-cache versus KV-cache performance comparison remains available as a later engineering experiment, but it is not required before continuing the project.

The project now continues with MINI-KUZAI PHASE 03, focused on training, identity, personality, laboratory-specific knowledge, and chatbot behavior.
