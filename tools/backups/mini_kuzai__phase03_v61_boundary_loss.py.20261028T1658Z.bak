"""Boundary-aware EOS objective for Mini-Kuzai V61.

The base next-token cross-entropy is preserved exactly.

Two sparse auxiliary terms are added:
- terminal assistant boundary: extra EOS cross-entropy;
- intermediate assistant boundary: extra EOS suppression.

All auxiliary sums are normalized by the same non-pad token count as the base
cross-entropy. Therefore a boundary weight W means that the local gradient at
that boundary is approximately (1 + W) times the baseline contribution while
the global objective remains dominated by ordinary language-model tokens.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class BoundaryLossResult:
    total: torch.Tensor
    base_ce: torch.Tensor
    terminal_extra: torch.Tensor
    intermediate_extra: torch.Tensor
    valid_tokens: int
    terminal_positions: int
    intermediate_positions: int


def boundary_aware_eos_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
    *,
    terminal_mask: torch.Tensor,
    intermediate_mask: torch.Tensor,
    eos_id: int = 2,
    pad_id: int = 0,
    terminal_weight: float,
    intermediate_weight: float,
) -> BoundaryLossResult:
    """Return V61 boundary-aware next-token loss.

    Shapes:
      logits: [..., vocab]
      targets: [...]
      terminal_mask: bool [...]
      intermediate_mask: bool [...]

    terminal_mask positions must target EOS.
    intermediate_mask positions must target a non-EOS token.
    Masks must be disjoint and must not select PAD targets.
    """

    if logits.ndim < 2:
        raise ValueError("logits must have at least 2 dimensions")
    if logits.shape[:-1] != targets.shape:
        raise ValueError("logits/targets shape mismatch")
    if terminal_mask.shape != targets.shape:
        raise ValueError("terminal mask shape mismatch")
    if intermediate_mask.shape != targets.shape:
        raise ValueError("intermediate mask shape mismatch")
    if terminal_mask.dtype is not torch.bool:
        raise TypeError("terminal_mask must be boolean")
    if intermediate_mask.dtype is not torch.bool:
        raise TypeError("intermediate_mask must be boolean")
    if terminal_weight < 0 or intermediate_weight < 0:
        raise ValueError("boundary weights must be non-negative")
    if eos_id < 0 or eos_id >= logits.shape[-1]:
        raise ValueError("EOS id outside vocabulary")

    valid = targets != pad_id
    if bool((terminal_mask & intermediate_mask).any().item()):
        raise ValueError("boundary masks must be disjoint")
    if bool((terminal_mask & ~valid).any().item()):
        raise ValueError("terminal boundary cannot target PAD")
    if bool((intermediate_mask & ~valid).any().item()):
        raise ValueError("intermediate boundary cannot target PAD")
    if bool((terminal_mask & (targets != eos_id)).any().item()):
        raise ValueError("terminal boundary must target EOS")
    if bool((intermediate_mask & (targets == eos_id)).any().item()):
        raise ValueError("intermediate boundary cannot target EOS")

    valid_tokens = int(valid.sum().item())
    if valid_tokens <= 0:
        raise ValueError("loss has no valid target token")

    flat_logits = logits.reshape(-1, logits.shape[-1])
    flat_targets = targets.reshape(-1)
    flat_valid = valid.reshape(-1)
    flat_terminal = terminal_mask.reshape(-1)
    flat_intermediate = intermediate_mask.reshape(-1)

    per_token_ce = F.cross_entropy(
        flat_logits,
        flat_targets,
        ignore_index=pad_id,
        reduction="none",
    )
    denominator = per_token_ce.new_tensor(float(valid_tokens))
    base_ce = per_token_ce[flat_valid].sum() / denominator

    zero = base_ce.new_zeros(())

    if bool(flat_terminal.any().item()):
        terminal_ce_sum = per_token_ce[flat_terminal].sum()
        terminal_extra = (
            terminal_ce_sum
            * float(terminal_weight)
            / denominator
        )
    else:
        terminal_extra = zero

    if bool(flat_intermediate.any().item()):
        selected = flat_logits[flat_intermediate]
        eos_logits = selected[:, eos_id]

        # -log(1 - P(EOS)) in a numerically stable logit form:
        # softplus(eos_logit - logsumexp(non_eos_logits)).
        non_eos = selected.clone()
        non_eos[:, eos_id] = -torch.inf
        other_lse = torch.logsumexp(non_eos, dim=-1)
        suppression_sum = F.softplus(
            eos_logits - other_lse
        ).sum()
        intermediate_extra = (
            suppression_sum
            * float(intermediate_weight)
            / denominator
        )
    else:
        intermediate_extra = zero

    total = base_ce + terminal_extra + intermediate_extra

    return BoundaryLossResult(
        total=total,
        base_ce=base_ce,
        terminal_extra=terminal_extra,
        intermediate_extra=intermediate_extra,
        valid_tokens=valid_tokens,
        terminal_positions=int(flat_terminal.sum().item()),
        intermediate_positions=int(
            flat_intermediate.sum().item()
        ),
    )
