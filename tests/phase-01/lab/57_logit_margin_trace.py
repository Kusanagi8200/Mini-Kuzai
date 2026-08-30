import torch

from mini_kuzai_padding import MiniKuzaiPadding


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

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


def get_logits(x):

    return model.lm_head(
        model.final_norm(x)
    )[0, -1]


def trace(prompt, expected, competitor):

    words = prompt.split()

    input_ids = torch.tensor(
        [[token_to_id[word] for word in words]],
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

    stages = []


    def record(name):

        logits = get_logits(x)

        expected_logit = logits[
            expected_id
        ].item()

        competitor_logit = logits[
            competitor_id
        ].item()

        margin = (
            expected_logit
            - competitor_logit
        )

        stages.append(
            (
                name,
                expected_logit,
                competitor_logit,
                margin
            )
        )


    record("EMBEDDINGS")


    for block_index, block in enumerate(
        model.blocks,
        start=1
    ):

        attention_output = block.attention(
            block.norm1(x),
            attention_mask
        )

        x = x + attention_output

        record(
            f"BLOCK {block_index} ATTENTION"
        )


        mlp_output = block.mlp(
            block.norm2(x)
        )

        x = x + mlp_output

        record(
            f"BLOCK {block_index} MLP"
        )


    print()
    print("========================================")
    print("PROMPT     :", prompt)
    print("EXPECTED   :", expected)
    print("COMPETITOR :", competitor)

    print()
    print(
        f"{'STAGE':24s} "
        f"{'EXPECTED':>10s} "
        f"{'COMPETITOR':>12s} "
        f"{'MARGIN':>10s} "
        f"{'DELTA':>10s}"
    )

    previous_margin = None

    for (
        stage,
        expected_logit,
        competitor_logit,
        margin
    ) in stages:

        if previous_margin is None:
            delta_text = "-"
        else:
            delta = margin - previous_margin
            delta_text = f"{delta:+.4f}"

        print(
            f"{stage:24s} "
            f"{expected_logit:10.4f} "
            f"{competitor_logit:12.4f} "
            f"{margin:10.4f} "
            f"{delta_text:>10s}"
        )

        previous_margin = margin


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== LOGIT MARGIN TRACE =====")
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
