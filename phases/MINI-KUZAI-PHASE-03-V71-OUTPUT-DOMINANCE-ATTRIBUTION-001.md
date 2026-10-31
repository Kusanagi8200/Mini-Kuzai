# Mini-Kuzai Phase 03 - V71 Output Dominance Attribution 001

Date --> 2026-10-31

Status --> **RESEARCH PROTOCOL PUBLISHED / IMPLEMENTATION AND LOCAL GPU EXECUTION PENDING**

## Motivation and prior verified evidence

Frozen V62 remains at the mandatory cycle-2 review stop: 69 optimizer steps, 597982 exposed tokens and no further authorized training. All measurements are restricted to the existing 36 frozen VALIDATION conversations, with BLIND closed.

Validated GOGIT evidence -->

- [V67](../reports/assistant-results/history/PHASE03-SMOLTALK-V67-OUTPUT-CONCENTRATION-001.json) --> 4 distinct top-1 predicted IDs versus 606 distinct gold IDs, dominant prediction share 72.58%, on 9170 lexical targets
- [V68](../reports/assistant-results/history/PHASE03-SMOLTALK-V68-OUTPUT-HEAD-001.json) --> selected row norm 0.360, gold row norm 0.293, mean gold-logit deficit 1.174 for byte targets versus 3.466 for merged BPE targets
- [V69](../reports/assistant-results/history/PHASE03-SMOLTALK-V69-OUTPUT-NORM-COUNTERFACTUAL-001.json) --> FULL row-norm equalization raises predicted distinct IDs to 7 but increases validation CE to 5.048
- [V70](../reports/assistant-results/history/PHASE03-SMOLTALK-V70-PRECISION-CONTROL-001.json) --> original FP32 CE 4.732, 5 predicted IDs, top-token share 72.55%; the FULL FP32 control reproduces CE 5.048 and 7 distinct IDs

The V70 precision control isolates the BF16-versus-FP32 confound. It does **not** establish that large output-row norms are the main cause of low prediction diversity.

## Research question

What proportion of the frozen model's extreme next-token concentration is associated with output-row norm advantages versus directional alignment between captured hidden states and token embedding rows?

V71 must not rebrand the already completed V69 norm intervention as a new experiment. Its added contribution is **position-level attribution**, with all reported outputs aggregated and non-identifying.

## Planned read-only comparison

For each frozen next-token position, derive two FP32 projections from **the same captured V62 hidden state** -->

1. **ORIGINAL FP32** --> `z_i = h · W_i`, using the unchanged, tied output matrix
2. **NORM-NEUTRAL FP32** --> `z_i* = h · [W_i × (mean_nonzero_norm / max(norm_i, eps))]`, exactly replaying V69 FULL / V70 FULL semantics; zero-norm rows remain zero

The second projection is an angular/directional diagnostic under a common row-norm scale, **not** a newly trained output head. Compare original and norm-neutral argmax **at each position**; the already verified whole-set V70 statistics alone do not reveal which contexts switch.

Before analyzing attribution, explicitly demonstrate numerical agreement with V70 -->

| Reference metric | ORIGINAL FP32 | NORM-NEUTRAL FP32 |
| --- | ---: | ---: |
| Validation CE | 4.732 | 5.048 |
| Distinct argmax IDs | 5 | 7 |
| Dominant argmax share | 72.55% | 69.57% |
| Merged-BPE gold top-1 | 3.26% | 3.35% |
| Merged-BPE gold top-5 | 6.85% | 7.71% |
| Terminal EOS top-1 | 14/36 | 24/36 |

If any frozen reference fails, stop before GOGIT publication. Avoid relying solely on rounded CE when verifying data identities.

## Additional V71 measurements

All calculations are on frozen VALIDATION positions; results are aggregate integers only -->

- Number and share of positions whose top-1 token changes after norm neutralization
- Switch rate conditional on **true byte token** versus **true merged BPE token**; both denominators recorded and checked against frozen V67/V69 inventory
- Top-1 correctness changes: original-only correct, norm-neutral-only correct, correct in both, incorrect in both
- Original and norm-neutral winner-to-runner-up margin statistics, with deterministic tie handling
- Winner-versus-gold logit gap, separately for byte and merged BPE targets
- Average original row-norm advantage of selected token relative to the gold row, as a correlation measure, **not proof of causality**
- Hidden-state/output-row cosine alignment of original winner versus gold row, with zero-vector safeguards and explicit handling of special IDs
- Whether increased diversity comes from genuinely different winners across positions or only a changed small set of dominant tokens

The audit must define a stable and reviewed **maximum 30-field public numeric schema** before any GOGIT run. Do not publish raw IDs, token sequences, prompts, text, hidden vectors, weight rows, individual logits or per-position data. Do not invent numeric results before the fhc2 GPU run.

## Integrity and authorization boundaries

The future implementation must -->

1. Verify the exact stopped V62 run and immutable checkpoint, 69 optimizer steps, 597982 exposure tokens and the original tokenizer/architecture
2. Validate V67, V68, V69 and V70 immutable numeric GOGIT dependencies and source fingerprints
3. Build **only** the frozen 36-segment VALIDATION, and preserve the 9206 next-token / 9170 lexical-position inventory
4. Run `model.eval()` and `torch.inference_mode()`; perform no optimization, training, sampling or BLIND evaluation
5. Capture and release frozen output-head hidden states with a removable hook and compare the tied original weights for equality afterwards
6. Implement unit tests, deterministic numerical/tie rules, pinned Git source identity and fail-closed GOGIT publication
7. Keep all diagnostic branch decisions observational; no new training authorization, checkpoint replacement or architecture change follows automatically

AUTOPILOT integration is a separate reviewed implementation step. Its diagnostic-runner catalog and any future campaign must be pinned and bounded. **No V71 command, runner, AUTOPILOT campaign or GPU result is claimed as available by this protocol.**

## Interpretation gate

An increased number of different argmax IDs does not imply natural-language competence or improved conversation. A rise in BPE top-5 with worse CE also cannot independently justify deploying a modified output projection.

Following a verified V71 result, decide whether to investigate hidden-state anisotropy, training dynamics or a **new explicitly authorized** bounded optimization protocol. Preserve historical V62 checkpoint and BLIND separation throughout.

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
