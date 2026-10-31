```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 01 / 02
  STEP     : HISTORY-01
  STATUS   : PROJECT ORIGINS
========================================================================
```

**From curiosity to a small experimental AI**

Mini-Kuzai started with a simple question:

**What would happen if I tried to build a language model myself, from the very beginning, rather than using an existing pretrained model?**

The idea was not to compete with large commercial LLMs. It was to understand what actually happens inside a Transformer, from tokenization and attention mechanisms to learning, prediction, and text generation.

Mini-Kuzai is developed locally with Python, PyTorch, and NVIDIA CUDA as part of **THE KUZ NETWORK** laboratory.

### Phase 01 - Understanding the Transformer

The first phase was a hands-on exploration of the fundamental components of a language model.

Step by step, I built and tested token embeddings, positional information, self-attention, causal masking, residual connections, MLP layers, backpropagation, and autoregressive generation.

The work eventually produced a deliberately tiny model:

- 2 Transformer blocks
- 2 attention heads
- 2,368 parameters
- 67 preserved experimental scripts

The objective was to make every component observable and understandable.

### Phase 02 - Understanding Inference

The next phase explored token generation, repeated computation, performance measurement, and KV caching.

A KV-cache implementation was validated against the original frozen model, reproducing the same generated tokens without retraining its weights.

### Where this leads

These first experiments established the technical foundation for a more ambitious goal:

**Building Mini-Kuzai as a small conversational AI with her own evolving personality.**

Not just a model that predicts text, but a research project exploring how identity, curiosity, creativity, and conversational behavior might progressively emerge through learning.

That became the starting point for Phase 03.

**Project:** https://github.com/Kusanagi8200/Mini-Kuzai

**Phase 01:** https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/phases/MINI-KUZAI-PHASE-01.md

**Phase 02:** https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/phases/MINI-KUZAI-PHASE-02.md

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
