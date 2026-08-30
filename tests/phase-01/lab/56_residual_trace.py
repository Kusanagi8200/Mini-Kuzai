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
id_to_token = checkpoint["id_to_token"]

PAD_ID = checkpoint["pad_token_id"]


model = MiniKuzaiPadding(
    vocab_size=len(vocabulary),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    num_heads=checkpoint["num_heads"],
    num_layers=checkpoint["num_layers"],
    max_sequence_length=checkpoint["max_sequence_length"],
    pad_token_id=PAD_ID
).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ==================================================
# Project an intermediate residual stream
# through final norm + LM head
# ==================================================

def inspect_logits(x, expected, stage):

    normalized = model.final_norm(x)

    logits = model.lm_head(
        normalized
    )[0, -1]

    probabilities = torch.softmax(
        logits,
        dim=-1
    )

    top_probs, top_ids = torch.topk(
        probabilities,
        k=5
    )

    print()
    print(f"===== {stage} =====")

    for probability, token_id in zip(
        top_probs,
        top_ids
    ):

        token = id_to_token[
            token_id.item()
        ]

        marker = ""

        if token == expected:
            marker = " <-- EXPECTED"

        print(
            f"{token:12s} "
            f"{probability.item() * 100:6.2f} %"
            f"{marker}"
        )


# ==================================================
# Trace one prompt
# ==================================================

def trace(prompt, expected):

    words = prompt.split()

    input_ids = torch.tensor(
        [[
            token_to_id[word]
            for word in words
        ]],
        dtype=torch.long,
        device=device
    )

    attention_mask = torch.ones_like(
        input_ids
    )

    sequence_length = input_ids.shape[1]

    positions = torch.arange(
        sequence_length,
        device=device
    )

    # ----------------------------------------------
    # Embeddings
    # ----------------------------------------------

    x = (
        model.token_embedding(input_ids)
        + model.position_embedding(positions)
    )

    print()
    print("========================================")
    print("PROMPT  :", prompt)
    print("EXPECTED:", expected)

    inspect_logits(
        x,
        expected,
        "EMBEDDINGS"
    )


    # ----------------------------------------------
    # Every Transformer block
    # ----------------------------------------------

    for block_index, block in enumerate(
        model.blocks,
        start=1
    ):

        # Attention residual update
        attention_output = block.attention(
            block.norm1(x),
            attention_mask
        )

        x = x + attention_output

        inspect_logits(
            x,
            expected,
            f"BLOCK {block_index} AFTER ATTENTION"
        )

        # MLP residual update
        mlp_output = block.mlp(
            block.norm2(x)
        )

        x = x + mlp_output

        inspect_logits(
            x,
            expected,
            f"BLOCK {block_index} AFTER MLP"
        )


    # ----------------------------------------------
    # Actual final prediction
    # ----------------------------------------------

    final_logits = model.lm_head(
        model.final_norm(x)
    )[0, -1]

    probabilities = torch.softmax(
        final_logits,
        dim=-1
    )

    predicted = id_to_token[
        torch.argmax(
            probabilities
        ).item()
    ]

    print()
    print("===== FINAL =====")
    print("Predicted:", predicted)
    print("Expected :", expected)


# ==================================================
# Frozen-model analysis
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== RESIDUAL STREAM / LOGIT TRACE =====")

print("Checkpoint: mini-kuzai-final.pt")
print("MODEL MODIFIED ON DISK: NO")


trace(
    "mini kuzai runs using",
    "linux"
)

trace(
    "a model can generate",
    "text"
)
