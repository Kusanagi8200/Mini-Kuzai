"""Pairwise boundary-margin objective for Mini-Kuzai V62.

The base next-token cross-entropy is preserved exactly.

Sparse auxiliary hinge losses operate directly on logits:
- terminal boundary: EOS must beat the best non-EOS competitor by margin;
- intermediate assistant boundary: the true continuation token must beat EOS
  by margin.

The two hinge terms have the same local derivative magnitude when active.
A separate intermediate weight can compensate for the frozen TRAIN inventory
ratio between terminal and intermediate boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class MarginLossResult:
    total: torch.Tensor
    base_ce: torch.Tensor
    terminal_extra: torch.Tensor
    intermediate_extra: torch.Tensor
    valid_tokens: int
    terminal_positions: int
    intermediate_positions: int
    terminal_active: int
    intermediate_active: int


def boundary_margin_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
    *,
    terminal_mask: torch.Tensor,
    intermediate_mask: torch.Tensor,
    eos_id: int = 2,
    pad_id: int = 0,
    margin: float,
    terminal_weight: float,
    intermediate_weight: float,
) -> MarginLossResult:
    """Return the V62 pairwise boundary-margin objective."""

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
    if margin <= 0:
        raise ValueError("margin must be positive")
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
    flat_terminal = terminal_mask.reshape(-1)
    flat_intermediate = intermediate_mask.reshape(-1)

    base_ce = F.cross_entropy(
        flat_logits,
        flat_targets,
        ignore_index=pad_id,
        reduction="mean",
    )
    denominator = base_ce.new_tensor(float(valid_tokens))
    zero = base_ce.new_zeros(())

    terminal_active = 0
    if bool(flat_terminal.any().item()):
        selected = flat_logits[flat_terminal]
        eos_logits = selected[:, eos_id]
        non_eos = selected.clone()
        non_eos[:, eos_id] = -torch.inf
        competitor_logits = torch.max(non_eos, dim=-1).values
        violations = F.relu(
            float(margin) - (eos_logits - competitor_logits)
        )
        terminal_active = int((violations > 0).sum().item())
        terminal_extra = (
            violations.sum()
            * float(terminal_weight)
            / denominator
        )
    else:
        terminal_extra = zero

    intermediate_active = 0
    if bool(flat_intermediate.any().item()):
        selected = flat_logits[flat_intermediate]
        selected_targets = flat_targets[flat_intermediate]
        rows = torch.arange(
            selected.shape[0],
            device=selected.device,
        )
        true_logits = selected[rows, selected_targets]
        eos_logits = selected[:, eos_id]
        violations = F.relu(
            float(margin) - (true_logits - eos_logits)
        )
        intermediate_active = int((violations > 0).sum().item())
        intermediate_extra = (
            violations.sum()
            * float(intermediate_weight)
            / denominator
        )
    else:
        intermediate_extra = zero

    total = base_ce + terminal_extra + intermediate_extra

    return MarginLossResult(
        total=total,
        base_ce=base_ce,
        terminal_extra=terminal_extra,
        intermediate_extra=intermediate_extra,
        valid_tokens=valid_tokens,
        terminal_positions=int(flat_terminal.sum().item()),
        intermediate_positions=int(flat_intermediate.sum().item()),
        terminal_active=terminal_active,
        intermediate_active=intermediate_active,
    )
