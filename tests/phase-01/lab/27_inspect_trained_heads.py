import math
import torch

from mini_kuzai_mha import MiniKuzaiMHA


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

checkpoint = torch.load(
    "mini-kuzai-mha.pt",
    map_location=device,
    weights_only=False
)

vocabulary = checkpoint["vocabulary"]
token_to_id = checkpoint["token_to_id"]

model = MiniKuzaiMHA(
    vocab_size=len(vocabulary),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    num_heads=checkpoint["num_heads"],
    max_sequence_length=checkpoint["max_sequence_length"]
).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ==================================================
# Prompt
# ==================================================

prompt = "mini kuzai learns from data"
words = prompt.split()

token_ids = torch.tensor(
    [token_to_id[word] for word in words],
    dtype=torch.long,
    device=device
)

sequence_length = len(words)


# ==================================================
# Reproduce input to attention
# ==================================================

positions = torch.arange(
    sequence_length,
    device=device
)

x = (
    model.token_embedding(token_ids)
    + model.position_embedding(positions)
)

# Pre-LayerNorm, same as TransformerBlock
x_norm = model.transformer.norm1(x)

attention = model.transformer.attention

num_heads = attention.num_heads
head_dim = attention.head_dim


# ==================================================
# Q / K / V using TRAINED weights
# ==================================================

Q = attention.q_proj(x_norm)
K = attention.k_proj(x_norm)
V = attention.v_proj(x_norm)

Q = Q.view(
    sequence_length,
    num_heads,
    head_dim
).transpose(0, 1)

K = K.view(
    sequence_length,
    num_heads,
    head_dim
).transpose(0, 1)

V = V.view(
    sequence_length,
    num_heads,
    head_dim
).transpose(0, 1)


# ==================================================
# Attention
# ==================================================

scores = (
    Q @ K.transpose(-2, -1)
) / math.sqrt(head_dim)

mask = torch.triu(
    torch.ones(
        sequence_length,
        sequence_length,
        dtype=torch.bool,
        device=device
    ),
    diagonal=1
)

scores = scores.masked_fill(
    mask,
    float("-inf")
)

weights = torch.softmax(
    scores,
    dim=-1
)


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== TRAINED MULTI-HEAD ATTENTION =====")

print("Prompt    :", prompt)
print("Tokens    :", words)
print("Heads     :", num_heads)
print("Head dim  :", head_dim)
print("Shape     :", weights.shape)

for head in range(num_heads):

    print()
    print(f"===== HEAD {head} =====")

    matrix = weights[head]

    header = "            " + " ".join(
        f"{word:>9s}"
        for word in words
    )

    print(header)

    for row_index, word in enumerate(words):

        values = " ".join(
            f"{value.item():9.4f}"
            for value in matrix[row_index]
        )

        print(
            f"{word:10s}  {values}"
        )


print()
print("===== LAST TOKEN: data =====")

for head in range(num_heads):

    print()
    print(f"HEAD {head}")

    for word, probability in zip(
        words,
        weights[head, -1]
    ):

        print(
            f"data -> {word:8s} "
            f"{probability.item() * 100:6.2f} %"
        )
