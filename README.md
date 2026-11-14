#### **`Mini-Kuzai - LLM`**

#### **`BUILD A LANGUAGE MODEL FROM SCRATCH, TRAIN IT LOCALLY AND INSPECT WHAT HAPPENS INSIDE A TRANSFORMER.`**

[![GITHUB](https://img.shields.io/badge/GITHUB-555555?style=flat-square&logo=github&logoColor=white)](https://github.com/Kusanagi8200/Mini-Kuzai)&#8202;![MINI-KUZAI](https://img.shields.io/badge/MINI--KUZAI-FFFFFF?style=flat-square)&#8202;![PYTHON](https://img.shields.io/badge/PYTHON-2EA043?style=flat-square)&#8202;![PYTORCH](https://img.shields.io/badge/PYTORCH-2EA043?style=flat-square)&#8202;![CUDA](https://img.shields.io/badge/CUDA-2EA043?style=flat-square)&#8202;![TRANSFORMER](https://img.shields.io/badge/TRANSFORMER-2EA043?style=flat-square)&#8202;![FROM SCRATCH](https://img.shields.io/badge/FROM%20SCRATCH-555555?style=flat-square)&#8202;![PHASE 03](https://img.shields.io/badge/PHASE%2003-D73A49?style=flat-square)

---

![Mini-Kuzai project illustration](Mini-Kuzai-Project.png)

## Project overview

**Mini-Kuzai** is an experimental autoregressive language model developed **from scratch** with Python and PyTorch and inspected locally with NVIDIA CUDA.

It is not built from pretrained weights and is not presented as a production chatbot. The project is a controlled research laboratory for understanding model behavior, training dynamics, representation geometry, token-frequency effects and conversational-model design.

The current trained state remains on the **V62 run lineage**, but V81 explicitly resumed the frozen cycle-2 checkpoint and completed the remaining authorized initial-window budget. The continuation is now closed and no further optimizer step is authorized.

## Current checkpoint - 2026-11-14

| Component | Verified state |
| --- | --- |
| Phase | **Phase 03** |
| Model | Decoder-only Transformer, 1,184,512 parameters |
| Tokenizer | Byte-BPE, 1,024-token vocabulary |
| Controlled corpus | 107 TRAIN / 36 VALIDATION / 36 BLIND conversations |
| Training inventory | 345 segments |
| Training lineage | **V62 run resumed under V81** |
| Final optimizer steps | **136** |
| Final exposure tokens | **1,181,302** |
| Best validation loss | **4.030447** |
| V81 unused exposure budget | **362 tokens** |
| Latest scientific step | **V81 CLOSED** |
| Training authorization | **0 / NOT AUTHORIZED** |
| BLIND access | **CLOSED** |
| V81 semantic claim | **0 / NONE** |
| V81 media flow | **CLOSED / TRI-CHANNEL VERIFIED** |
| Next step | **V82 protocol frozen / START-DEV-FLOW required** |

## Development phases

| Phase | Purpose | Documentation |
| --- | --- | --- |
| **01 - Transformer fundamentals** | Tokenization, attention, MLP, LayerNorm, training, ablations and interpretability | [Phase 01](phases/MINI-KUZAI-PHASE-01.md) |
| **02 - Inference** | Autoregressive decoding and KV-cache experiments | [Phase 02](phases/MINI-KUZAI-PHASE-02.md) |
| **03 - Conversational Mini-Kuzai** | Identity, curated corpus, Byte-BPE, controlled training and diagnostic evaluation | [Phase 03](phases/MINI-KUZAI-PHASE-03.md) |

Historical detailed chronology remains available in [README-DETAILED-20261031T192526Z.md](README-DETAILED-20261031T192526Z.md).

## Phase 03 research path

| Steps | Focus |
| --- | --- |
| **V48-V55** | Semantic review, controlled corpus construction, VALIDATION closure and BLIND freeze |
| **V56-V58** | Byte-BPE tokenizer and 1.18M-parameter architecture |
| **V59-V62** | Training mix, bounded training, EOS objectives and boundary-margin control |
| **V63-V70** | Generation robustness, EOS behavior, token-frequency diagnostics, output concentration and precision control |
| **V71-V74** | Output dominance, hidden-state anisotropy, PC1 attribution and frequency-prior control |
| **V75** | TRAIN-fitted PC1 geometry transfers to VALIDATION with 99.95% absolute cosine alignment |
| **V76** | TRAIN lexical frequency explains 7.75% of centered PC1 output-profile energy; residual retains 92.25% |
| **V77** | Reverse-history control changes only 5/9,170 residual top-1 predictions |
| **V78** | Identical-input rebatching produces continuous numerical noise but 0/9,170 discrete prediction changes |
| **V79** | Same-path batch-32 control reproduces the exact five context-order prediction/sign changes |
| **V80** | Decision-boundary proximity control shows the five V79 changes are not confined to the frozen 1e-3 near-zero band |
| **V81** | Explicitly authorized bounded continuation of the frozen V62 run lineage to the remaining initial-window exposure limit; final state closed at 136 steps / 1,181,302 tokens |

## V81 verified result

V81 resumed the frozen V62 cycle-2 checkpoint under an explicit bounded continuation authorization. The frozen V62 trainer and objective were reused unchanged with `--resume`; no tokenizer, architecture, corpus, stream-weight or scheduler change was introduced.

Verified closure -->

- starting optimizer steps --> **69**
- starting exposure tokens --> **597,982**
- final optimizer steps --> **136**
- final exposure tokens --> **1,181,302**
- maximum authorized exposure --> **1,181,664**
- unused exposure budget --> **362 tokens**
- stop reason --> **MAX_EXPOSURE_TOKENS**
- best validation loss --> **4.030447**
- baseline best validation loss --> **4.732514**
- best-loss improvement --> **14.83%**
- BLIND access --> **0**
- further training authorized --> **0**
- semantic validation complete --> **0**
- semantic claim --> **0**

The continuation stopped because the next segment would have exceeded the frozen exposure ceiling. The absence of a cycle-4 checkpoint is therefore expected and is not a failed milestone.

Primary evidence -->

- [V81 readiness protocol](phases/MINI-KUZAI-PHASE-03-V81-V62-CONTINUATION-READINESS-001.md)
- [V81 final scientific GOGIT](reports/assistant-results/history/PHASE03-SMOLTALK-V81-FINAL-CLOSURE-001.json)
- [V81 FINAL receipt](automation/dev-flow/receipts/V81-final.json)
- [Discussion #13](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/13)

## DEV-FLOW publication system

Mini-Kuzai separates scientific authority from communication publication.

```text
scientific protocol
      |
      v
validated execution
      |
      v
GOGIT PASS
      |
      v
FINAL-DEV-FLOW
      |
      +--> GitHub Discussion FINAL
      +--> committed FINAL receipt
      |
      v
downstream communication sinks
```

For V81 -->

- GitHub FINAL --> **PUBLISHED**, Discussion #13
- LinkedIn FINAL text publication --> **PUBLISHED through KUZ-DIN**
- YouTube FINAL Short --> **PUBLIC**
- YouTube video ID --> `EAMRSevA2zk`
- LinkedIn native media post --> `urn:li:ugcPost:7527349657677594624`
- GitHub media fallback --> Discussion #13 comment #19612381
- cross-channel media receipt --> `Mini-Kuzai_YOUTUBE/automation/publication-receipts/V81-final.json`

A downstream communication failure never invalidates the underlying scientific result.

## Cross-channel media flow - validated before V81

`FLOW-PRESENTATION-001` is a **non-scientific integration test** used to validate the extended publication path before V81.

Verified media -->

- duration --> **60 seconds**
- narration window --> **5 s to 55 s**
- media SHA256 --> `c34b3dc19788e6770e4edb9dffc2331df2438b23c6663858b7d5299ad5731034`

Verified publication -->

- YouTube --> **PUBLIC**, video ID `vhQmddUuMcg`
- LinkedIn --> **native video PUBLISHED**, post URN `urn:li:ugcPost:7526340708715327488`
- GitHub --> [Discussion #12](https://github.com/Kusanagi8200/Mini-Kuzai/discussions/12)
- GitHub media mode --> verified public YouTube link fallback

The test proves the media primitives required for V81 publication. It is **not V81 scientific evidence**.

## V81+ publication orchestration

Automatic cross-channel orchestration is now installed and active for future genuine V81+ FINAL receipts -->

```text
V81 scientific GOGIT PASS
  -> GitHub FINAL
  -> FINAL receipt
  -> automatic media brief
  -> 60-second audited MP4
  -> YouTube public
  -> LinkedIn native video
  -> GitHub media publication
  -> committed cross-channel media receipt
  -> V81 media flow closed
```

The media engineering prerequisite is complete and V81 has exercised the genuine production path end to end. The V82 read-only post-continuation replication protocol is now frozen and its START publication source is prepared. No V82 execution has occurred. The next boundary is explicit `START-DEV-FLOW V82`.

## Safety boundary

Current frozen rules -->

- the latest trained state is the closed V81 continuation on the V62 run lineage
- no further optimizer step is authorized
- no further checkpoint mutation is authorized
- BLIND remains closed
- publication authorization is never training authorization
- media generation is never scientific evidence
- historical reports, receipts and frozen datasets remain immutable evidence

## Repository map

| Area | Purpose |
| --- | --- |
| [phases/](phases/) | Scientific protocols and phase documentation |
| [mini_kuzai/](mini_kuzai/) | Model and training implementation |
| [data/phase-03/](data/phase-03/) | Controlled public corpus artifacts and manifests |
| [reviews/](reviews/) | Semantic and dataset review evidence |
| [tests/](tests/) | Regression and scientific-control tests |
| [tools/](tools/) | Diagnostics, GOGIT and DEV-FLOW tooling |
| [automation/dev-flow/](automation/dev-flow/) | Explicit START / FINAL requests and receipts |
| [reports/assistant-results/history/](reports/assistant-results/history/) | Immutable GOGIT reports |
| [docs/discussions/](docs/discussions/) | GitHub Discussion publication history |
| [PROJECT-WORKFLOW-POLICY.md](PROJECT-WORKFLOW-POLICY.md) | Current execution and publication policy |
| [MAJ-THEKUZNETWORK.md](MAJ-THEKUZNETWORK.md) | Cross-repository THE KUZ NETWORK maintenance command |
| [docs/DEV-FLOW-REPRISE-2026-11-01.md](docs/DEV-FLOW-REPRISE-2026-11-01.md) | Detailed operational checkpoint |

## Related repositories

- Mini-Kuzai YouTube pipeline --> [Kusanagi8200/Mini-Kuzai_YOUTUBE](https://github.com/Kusanagi8200/Mini-Kuzai_YOUTUBE)
- LinkedIn bridge --> [Kusanagi8200/KUZ-DIN](https://github.com/Kusanagi8200/KUZ-DIN)
- public project website --> [Kusanagi8200/KUZAI.ORG-VS2](https://github.com/Kusanagi8200/KUZAI.ORG-VS2)
- local KUZAI application --> [Kusanagi8200/KUZAI-CHAT](https://github.com/Kusanagi8200/KUZAI-CHAT)

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
