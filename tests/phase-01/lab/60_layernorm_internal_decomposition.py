import torch

from mini_kuzai_padding import MiniKuzaiPadding


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Frozen checkpoint
# ==================================================

checkpoint = torch.load(
    "mini-kuzai-final.pt",
    map_location=device,
    weights_only=False
)

vocabulary = checkpoint["vocabulary"]
token_to_id = checkpoint["token_to_id"]

model = MiniKuzaiPadding(
    vocab_size=len(vocabulary),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    num_heads=checkpoint["num_heads"],
    num_layers=checkpoint["num_layers"],
    max_sequence_length=checkpoint["max_sequence_length"],
    pad_token_id=checkpoint["pad_token_id"]
).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ==================================================
# LM-head margin
# ==================================================

def margin(vector, expected_id, competitor_id):

    logits = model.lm_head(vector)

    return (
        logits[expected_id]
        - logits[competitor_id]
    ).item()


# ==================================================
# Get final residual stream BEFORE final_norm
# ==================================================

def final_residual(prompt):

    input_ids = torch.tensor(
        [[
            token_to_id[word]
            for word in prompt.split()
        ]],
        dtype=torch.long,
        device=device
    )

    attention_mask = torch.ones_like(input_ids)

    positions = torch.arange(
        input_ids.shape[1],
        device=device
    )

    x = (
        model.token_embedding(input_ids)
        + model.position_embedding(positions)
    )

    for block in model.blocks:

        x = x + block.attention(
            block.norm1(x),
            attention_mask
        )

        x = x + block.mlp(
            block.norm2(x)
        )

    return x[0, -1]


# ==================================================
# LayerNorm decomposition
# ==================================================

def trace(prompt, expected, competitor):

    x = final_residual(prompt)

    expected_id = token_to_id[expected]
    competitor_id = token_to_id[competitor]

    layernorm = model.final_norm

    gamma = layernorm.weight
    beta = layernorm.bias
    eps = layernorm.eps


    # PyTorch LayerNorm uses population variance
    # (unbiased=False).

    mean = x.mean()

    variance = x.var(
        unbiased=False
    )

    std = torch.sqrt(
        variance + eps
    )


    # ----------------------------------------------
    # Stage 1: raw residual
    # ----------------------------------------------

    raw = x


    # ----------------------------------------------
    # Stage 2: standardized
    #
    # (x - mean) / std
    # ----------------------------------------------

    standardized = (
        x - mean
    ) / std


    # ----------------------------------------------
    # Stage 3: learned gamma
    # ----------------------------------------------

    gamma_applied = (
        standardized * gamma
    )


    # ----------------------------------------------
    # Stage 4: learned beta
    # ----------------------------------------------

    full_manual = (
        gamma_applied + beta
    )


    # Real PyTorch LayerNorm for verification

    full_pytorch = layernorm(x)


    raw_margin = margin(
        raw,
        expected_id,
        competitor_id
    )

    standardized_margin = margin(
        standardized,
        expected_id,
        competitor_id
    )

    gamma_margin = margin(
        gamma_applied,
        expected_id,
        competitor_id
    )

    final_margin = margin(
        full_manual,
        expected_id,
        competitor_id
    )


    print()
    print("========================================")
    print("PROMPT     :", prompt)
    print("EXPECTED   :", expected)
    print("COMPETITOR :", competitor)

    print()
    print("RESIDUAL MEAN:", f"{mean.item():+.6f}")
    print("RESIDUAL STD :", f"{std.item():.6f}")

    print()
    print(
        f"{'STAGE':24s}"
        f"{'MARGIN':>12s}"
        f"{'CHANGE':>12s}"
    )


    stages = [
        ("RAW RESIDUAL", raw_margin),
        (
            "CENTER + SCALE",
            standardized_margin
        ),
        (
            "LEARNED GAMMA",
            gamma_margin
        ),
        (
            "LEARNED BETA",
            final_margin
        ),
    ]


    previous = None

    for name, value in stages:

        if previous is None:
            change = "-"
        else:
            change = f"{value - previous:+.4f}"

        print(
            f"{name:24s}"
            f"{value:12.4f}"
            f"{change:>12s}"
        )

        previous = value


    print()
    print(
        "MANUAL == PYTORCH:",
        torch.allclose(
            full_manual,
            full_pytorch,
            atol=1e-6
        )
    )


    # ----------------------------------------------
    # Direct beta contribution
    # ----------------------------------------------

    decision_direction = (
        model.lm_head.weight[expected_id]
        - model.lm_head.weight[competitor_id]
    )

    beta_contribution = torch.dot(
        beta,
        decision_direction
    ).item()

    print(
        "BETA DIRECT CONTRIBUTION:",
        f"{beta_contribution:+.4f}"
    )


# ==================================================
# Run
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== FINAL LAYERNORM INTERNAL DECOMPOSITION =====")

print("Checkpoint: mini-kuzai-final.pt")
print("MODEL MODIFIED ON DISK: NO")


with torch.no_grad():

    trace(
        "mini kuzai runs using",
        "linux",
        "data"
    )

    trace(
        "a model can generate",
        "text",
        "<eos>"
    )
