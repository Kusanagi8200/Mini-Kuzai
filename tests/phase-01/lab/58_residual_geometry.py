import torch
import torch.nn.functional as F

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
# Exact decoded margin
# ==================================================

def decoded_margin(x, expected_id, competitor_id):

    logits = model.lm_head(
        model.final_norm(x)
    )[0, -1]

    return (
        logits[expected_id]
        - logits[competitor_id]
    ).item()


# ==================================================
# Trace geometry
# ==================================================

def trace(prompt, expected, competitor):

    words = prompt.split()

    input_ids = torch.tensor(
        [[token_to_id[word] for word in words]],
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

    expected_id = token_to_id[expected]
    competitor_id = token_to_id[competitor]


    # ------------------------------------------------
    # LM-head decision direction
    #
    # logit(expected) - logit(competitor)
    # corresponds to projection onto:
    #
    # W_expected - W_competitor
    # ------------------------------------------------

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
        f"{'RES NORM':>11s}"
        f"{'UPD NORM':>11s}"
        f"{'RATIO':>10s}"
        f"{'COSINE':>10s}"
        f"{'MARGIN Δ':>12s}"
    )


    def analyse_component(name, before, update):

        before_last = before[0, -1]
        update_last = update[0, -1]

        residual_norm = torch.norm(
            before_last
        ).item()

        update_norm = torch.norm(
            update_last
        ).item()

        ratio = (
            update_norm / residual_norm
            if residual_norm > 0
            else 0.0
        )

        cosine = F.cosine_similarity(
            update_last.unsqueeze(0),
            decision_direction.unsqueeze(0)
        ).item()

        margin_before = decoded_margin(
            before,
            expected_id,
            competitor_id
        )

        after = before + update

        margin_after = decoded_margin(
            after,
            expected_id,
            competitor_id
        )

        margin_delta = (
            margin_after - margin_before
        )

        print(
            f"{name:22s}"
            f"{residual_norm:11.4f}"
            f"{update_norm:11.4f}"
            f"{ratio:10.4f}"
            f"{cosine:10.4f}"
            f"{margin_delta:12.4f}"
        )

        return after


    for block_index, block in enumerate(
        model.blocks,
        start=1
    ):

        # ------------------------------------------
        # Attention update
        # ------------------------------------------

        attention_output = block.attention(
            block.norm1(x),
            attention_mask
        )

        x = analyse_component(
            f"BLOCK {block_index} ATTENTION",
            x,
            attention_output
        )


        # ------------------------------------------
        # MLP update
        # ------------------------------------------

        mlp_output = block.mlp(
            block.norm2(x)
        )

        x = analyse_component(
            f"BLOCK {block_index} MLP",
            x,
            mlp_output
        )


    final_margin = decoded_margin(
        x,
        expected_id,
        competitor_id
    )

    print()
    print(
        "FINAL MARGIN:",
        f"{final_margin:+.4f}"
    )


# ==================================================
# Run
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== RESIDUAL UPDATE GEOMETRY =====")
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
