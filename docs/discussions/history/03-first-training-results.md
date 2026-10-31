```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : HISTORY-03
  STATUS   : V60-V73 RESEARCH REVIEW
========================================================================
```

**Phase 03 - From V60 to V73**

After preparing the architecture and training material, Mini-Kuzai reached its first controlled training experiments.

The objective was to observe how a small language model begins learning from conversational examples and, more importantly, how to identify what is working and what is not.

### The first training milestone

The V60-V62 experiments explored training initialization, learning objectives, conversation boundaries, and end-of-sequence behavior.

The V62 run stopped at a mandatory evaluation checkpoint after:

- 69 optimizer steps
- 597,982 exposed training tokens
- 2 completed training cycles

The checkpoint was frozen for further investigation.

### An unexpected result

Subsequent diagnostics revealed a significant limitation.

On 9,170 lexical validation positions, the original model repeatedly selected only a handful of different tokens as its most likely predictions.

In other words, the model had learned measurable prediction patterns, but its outputs remained extremely concentrated.

This raised a new question:

**Was the problem caused by the output layer, or did it originate deeper inside the model's learned representations?**

### Looking inside the model

Between V63 and V73, the project investigated token frequency, output logits, embedding norms, numerical precision, and the geometry of internal hidden states.

Two important findings emerged.

**V72 - Hidden-state anisotropy**

The first principal component accounted for 82.88% of the centered hidden-state variance, indicating a strongly concentrated internal representation.

**V73 - Principal-component experiments**

Removing this dominant direction increased the number of distinct predicted tokens from 15 to 522, but reduced top-1 accuracy from 30.88% to 12.26% in the mean-centered comparison.

Greater output diversity did not mean better predictions.

The dominant direction appears to carry substantial predictive information, even while the model's predictions remain highly repetitive.

### Where Mini-Kuzai stands today

The project has produced a functioning experimental Transformer, a frozen conversational training checkpoint, and a reproducible diagnostic framework.

However, **Mini-Kuzai has not yet demonstrated the conversational abilities or coherent personality originally envisioned**.

That distinction matters.

The next investigations will focus on understanding prediction bias, training-data distributions, and the learning objective before considering another training experiment.

The V62 checkpoint remains frozen, and the reserved BLIND TEST has not been opened for these diagnostics.

This is what makes the project interesting to me: discovering not only how a language model learns, but also why it sometimes fails to learn what we expected.

**Project:** https://github.com/Kusanagi8200/Mini-Kuzai

**Latest verified diagnostic (V73):** https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/reports/assistant-results/history/PHASE03-SMOLTALK-V73-PRINCIPAL-AXIS-ATTRIBUTION-001.json

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
