import math
import torch

from mini_kuzai_padding import MiniKuzaiPadding


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Frozen model
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
# Attention extraction
# ==================================================

def get_attention_weights(attention, x, attention_mask):

    batch_size, sequence_length, _ = x.shape

    Q = attention.q_proj(x)
    K = attention.k_proj(x)
    V = attention.v_proj(x)

    Q = Q.view(
        batch_size,
        sequence_length,
        attention.num_heads,
        attention.head_dim
    ).transpose(1, 2)

    K = K.view(
        batch_size,
        sequence_length,
        attention.num_heads,
        attention.head_dim
    ).transpose(1, 2)

    scores = (
        Q @ K.transpose(-2, -1)
    ) / math.sqrt(attention.head_dim)

    causal_mask = torch.triu(
        torch.ones(
            sequence_length,
            sequence_length,
            dtype=torch.bool,
            device=x.device
        ),
        diagonal=1
    )

    scores = scores.masked_fill(
        causal_mask,
        float("-inf")
    )

    key_mask = attention_mask[
        :, None, None, :
    ].bool()

    scores = scores.masked_fill(
        ~key_mask,
        float("-inf")
    )

    return torch.softmax(
        scores,
        dim=-1
    )


# ==================================================
# Inspect one prompt
# ==================================================

def inspect(prompt, expected):

    words = prompt.split()

    input_ids = torch.tensor(
        [[token_to_id[word] for word in words]],
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

    x = (
        model.token_embedding(input_ids)
        + model.position_embedding(positions)
    )

    print()
    print("========================================")
    print("PROMPT  :", prompt)
    print("EXPECTED:", expected)

    # ----------------------------------------------
    # Inspect every Transformer block
    # ----------------------------------------------

    for block_index, block in enumerate(
        model.blocks,
        start=1
    ):

        normalized = block.norm1(x)

        weights = get_attention_weights(
            block.attention,
            normalized,
            attention_mask
        )

        print()
        print(
            f"===== BLOCK {block_index} / LAST TOKEN ====="
        )

        for head in range(
            block.attention.num_heads
        ):

            print()
            print(f"HEAD {head}")

            last_token_weights = weights[
                0,
                head,
                -1
            ]

            for word, probability in zip(
                words,
                last_token_weights
            ):

                print(
                    f"{words[-1]} -> "
                    f"{word:10s} "
                    f"{probability.item() * 100:6.2f} %"
                )

        # Real forward through this block
        x = block(
            x,
            attention_mask
        )


    # ----------------------------------------------
    # Final prediction
    # ----------------------------------------------

    x = model.final_norm(x)
    logits = model.lm_head(x)[0, -1]

    probabilities = torch.softmax(
        logits,
        dim=-1
    )

    top_probs, top_ids = torch.topk(
        probabilities,
        k=5
    )

    print()
    print("===== FINAL PREDICTION =====")

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
# Frozen-model analysis only
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== FROZEN MODEL ATTENTION ANALYSIS =====")

print("Checkpoint: mini-kuzai-final.pt")
print("MODEL MODIFIED: NO")


inspect(
    "mini kuzai runs using",
    "linux"
)

inspect(
    "a model can generate",
    "text"
)
