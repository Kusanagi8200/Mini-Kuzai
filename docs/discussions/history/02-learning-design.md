```text
========================================================================
  MINI-KUZAI  //  FROM SCRATCH AI RESEARCH
========================================================================
  PROJECT  : THE KUZ NETWORK
  PHASE    : 03
  STEP     : HISTORY-02
  STATUS   : LEARNING DESIGN
========================================================================
```

**Phase 03 - Designing the model, the character, and the learning environment**

After building the first Transformer and exploring its inference mechanisms, Mini-Kuzai entered a new stage.

The objective was no longer simply to make a small model generate text.

It was to investigate whether a language model trained from scratch could progressively develop a **recognizable conversational identity**.

### Who is Mini-Kuzai supposed to become?

Mini-Kuzai is designed as a curious, creative, independent character originating from THE KUZ NETWORK laboratory.

Her intended behavioral characteristics include curiosity, critical thinking, imagination, intellectual independence, expressing uncertainty, reasoned disagreement, and the ability to revise an opinion when confronted with convincing evidence.

These are research objectives, not abilities already demonstrated by the model.

### Building the learning material

A significant part of Phase 03 was dedicated to designing, reviewing, and separating conversational data.

The controlled corpus was divided into:

- **107 TRAIN conversations** for learning
- **36 VALIDATION conversations** for evaluation during development
- **36 BLIND TEST conversations** reserved for future independent evaluation

The project also investigated external conversational datasets, including SmolTalk, with an emphasis on relevance, provenance, behavioral quality, and preventing leakage between evaluation groups.

The goal was not simply to accumulate as much training data as possible, but to understand what kind of examples might help develop the intended character.

### A new model architecture

The project then introduced a new Byte-BPE tokenizer and a larger Transformer architecture:

- Vocabulary of 1,024 tokens
- 1,184,512 model parameters
- 345 prepared training segments
- Local GPU execution

Unlike the original tiny educational Transformer, this architecture was intended to support controlled conversational learning experiments.

**The important distinction:** Mini-Kuzai still starts without pretrained language-model weights.

At this stage, the architecture, learning data, and evaluation protocols were prepared. The next challenge was to determine what the model would actually learn.

**Project and development history:** https://github.com/Kusanagi8200/Mini-Kuzai

**Phase 03:** https://github.com/Kusanagi8200/Mini-Kuzai/blob/main/phases/MINI-KUZAI-PHASE-03.md

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
