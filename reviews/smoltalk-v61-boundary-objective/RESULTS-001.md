# Mini-Kuzai V61 - boundary-aware EOS objective

Status --> **OBJECTIVE DEFINED / PREFLIGHT PASSED / TRAINING NOT AUTHORIZED**

## Controlled change from V60

- architecture --> unchanged
- initialization --> unchanged
- tokenizer --> unchanged
- corpus and stream weighting --> unchanged
- serializer and segmentation --> unchanged
- base next-token cross-entropy --> unchanged
- only experimental variable --> boundary-aware EOS objective

## Boundary objective

- terminal assistant boundary --> extra EOS cross-entropy
- intermediate assistant boundary --> explicit EOS suppression
- ordinary token positions --> unchanged
- auxiliary normalization --> global non-pad token count
- selected boundary weight --> **16.0**
- effective local gradient multiplier --> **17x**
- added loss ratio on frozen VALIDATION --> **4.63%**

## Selection gate

- candidates --> **4 / 8 / 16 / 32**
- maximum allowed auxiliary loss ratio --> **5.00%**
- minimum boundary gradient multiplier --> **9x**

## Hardware preflight

- CUDA/BF16 --> **PASS**
- peak reserved VRAM --> **746 MiB**
- peak reserved ratio --> **9.68%**

TRAINING_AUTHORIZED --> **0**
TRAINING_STARTED --> **0**
BLIND TEST --> **CLOSED**

---

##### **`THE KUZ NETWORK - KUSANAGI8200 - @2026`**
