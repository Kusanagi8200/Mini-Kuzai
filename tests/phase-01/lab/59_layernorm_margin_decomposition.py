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
# Margin functions
# ==================================================

def raw_margin(
    x,
    expected_id,
    competitor_id
):

    logits = model.lm_head(
        x
    )[0, -1]

    return (
        logits[expected_id]
        - logits[competitor_id]
    ).item()


def normalized_margin(
    x,
    expected_id,
    competitor_id
):

    logits = model.lm_head(
        model.final_norm(x)
    )[0, -1]

    return (
        logits[expected_id]
        - logits[competitor_id]
    ).item()


# ==================================================
# Trace
# ==================================================

def trace(
    prompt,
    expected,
    competitor
):

    input_ids = torch.tensor(
        [[
            token_to_id[word]
            for word in prompt.split()
        ]],
        dtype=torch.long,
        device=device
    )

    attention_mask = torch.ones_like(
        input_ids
    )

    positions = torch.arange(
        input_ids.shape[1],
        device=device
    )

    x = (
        model.token_embedding(input_ids)
        + model.position_embedding(positions)
    )

    expected_id = token_to_id[expected]
    competitor_id = token_to_id[competitor]

    decision_direction = (
        model.lm_head.weight[expected_id]
        - model.lm_head.weight[competitor_id]
    )


    print()
    print("========================================")
    print("PROMPT     :", prompt)
    print("EXPECTED   :", expected)
    print("COMPETITOR :", competitor)

    print()
    print(
        f"{'COMPONENT':22s}"
        f"{'DOT PRODUCT':>14s}"
        f"{'RAW DELTA':>12s}"
        f"{'NORM DELTA':>13s}"
    )


    def apply_update(
        name,
        before,
        update
    ):

        before_raw = raw_margin(
            before,
            expected_id,
            competitor_id
        )

        before_normalized = normalized_margin(
            before,
            expected_id,
            competitor_id
        )

        after = before + update

        after_raw = raw_margin(
            after,
            expected_id,
            competitor_id
        )

        after_normalized = normalized_margin(
            after,
            expected_id,
            competitor_id
        )

        raw_delta = (
            after_raw
            - before_raw
        )

        normalized_delta = (
            after_normalized
            - before_normalized
        )

        # Direct linear projection of the last-token
        # update onto the LM-head decision direction.
        dot_product = torch.dot(
            update[0, -1],
            decision_direction
        ).item()

        print(
            f"{name:22s}"
            f"{dot_product:14.4f}"
            f"{raw_delta:12.4f}"
            f"{normalized_delta:13.4f}"
        )

        return after


    for block_index, block in enumerate(
        model.blocks,
        start=1
    ):

        attention_output = block.attention(
            block.norm1(x),
            attention_mask
        )

        x = apply_update(
            f"BLOCK {block_index} ATTENTION",
            x,
            attention_output
        )


        mlp_output = block.mlp(
            block.norm2(x)
        )

        x = apply_update(
            f"BLOCK {block_index} MLP",
            x,
            mlp_output
        )


    print()

    print(
        "FINAL RAW MARGIN       :",
        f"{raw_margin(x, expected_id, competitor_id):+.4f}"
    )

    print(
        "FINAL NORMALIZED MARGIN:",
        f"{normalized_margin(x, expected_id, competitor_id):+.4f}"
    )


# ==================================================
# Run
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== LAYERNORM / LOGIT DECOMPOSITION =====")
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
