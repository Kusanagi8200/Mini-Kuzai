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
# Beta -> vocabulary projection
# ==================================================

beta = model.final_norm.bias

W = model.lm_head.weight


with torch.no_grad():

    # Contribution caused ONLY by LayerNorm beta.
    beta_logits = W @ beta

    # Keep LM-head bias separate if the implementation
    # happens to contain one.
    lm_head_bias = model.lm_head.bias


# ==================================================
# Helper
# ==================================================

def value(token):
    return beta_logits[
        token_to_id[token]
    ].item()


# ==================================================
# Pairwise contributions
# ==================================================

linux_data = (
    value("linux")
    - value("data")
)

text_eos = (
    value("text")
    - value("<eos>")
)


# ==================================================
# Ranking
# ==================================================

sorted_values, sorted_ids = torch.sort(
    beta_logits,
    descending=True
)


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== FINAL LAYERNORM BETA VOCABULARY EFFECT =====")

print("Checkpoint: mini-kuzai-final.pt")
print("MODEL MODIFIED ON DISK: NO")

print()
print("Vocabulary :", len(vocabulary))

print(
    "LM head bias:",
    "YES" if lm_head_bias is not None else "NO"
)

print()
print("===== KNOWN PAIRS =====")

print(
    "beta(linux) - beta(data) :",
    f"{linux_data:+.4f}"
)

print(
    "expected from Step 65    :",
    "-1.1111"
)

print()

print(
    "beta(text) - beta(<eos>):",
    f"{text_eos:+.4f}"
)

print(
    "expected from Step 65    :",
    "-1.8335"
)


print()
print("===== MOST FAVOURED BY BETA =====")

for score, token_id in zip(
    sorted_values[:10],
    sorted_ids[:10]
):

    token = id_to_token[
        token_id.item()
    ]

    print(
        f"{token:12s} "
        f"{score.item():+8.4f}"
    )


print()
print("===== MOST PENALISED BY BETA =====")

for score, token_id in zip(
    sorted_values[-10:].flip(0),
    sorted_ids[-10:].flip(0)
):

    token = id_to_token[
        token_id.item()
    ]

    print(
        f"{token:12s} "
        f"{score.item():+8.4f}"
    )


print()
print("===== SELECTED TOKENS =====")

for token in [
    "linux",
    "data",
    "text",
    "<eos>",
    "model",
    "a",
]:

    print(
        f"{token:12s} "
        f"{value(token):+8.4f}"
    )
