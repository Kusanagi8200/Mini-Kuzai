import torch

from mini_kuzai import MiniKuzai
from mini_kuzai_mha import MiniKuzaiMHA


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Load checkpoints
# ==================================================

mono_ckpt = torch.load(
    "mini-kuzai-eos.pt",
    map_location=device,
    weights_only=False
)

mha_ckpt = torch.load(
    "mini-kuzai-mha.pt",
    map_location=device,
    weights_only=False
)


# ==================================================
# Verify vocabulary compatibility
# ==================================================

assert mono_ckpt["vocabulary"] == mha_ckpt["vocabulary"]

vocabulary = mono_ckpt["vocabulary"]
token_to_id = mono_ckpt["token_to_id"]
id_to_token = mono_ckpt["id_to_token"]
EOS = mono_ckpt["eos_token"]


# ==================================================
# Recreate models
# ==================================================

mono = MiniKuzai(
    vocab_size=len(vocabulary),
    embedding_dim=mono_ckpt["embedding_dim"],
    hidden_dim=mono_ckpt["hidden_dim"],
    max_sequence_length=mono_ckpt["max_sequence_length"]
).to(device)

mono.load_state_dict(
    mono_ckpt["model_state_dict"]
)

mono.eval()


mha = MiniKuzaiMHA(
    vocab_size=len(vocabulary),
    embedding_dim=mha_ckpt["embedding_dim"],
    hidden_dim=mha_ckpt["hidden_dim"],
    num_heads=mha_ckpt["num_heads"],
    max_sequence_length=mha_ckpt["max_sequence_length"]
).to(device)

mha.load_state_dict(
    mha_ckpt["model_state_dict"]
)

mha.eval()


# ==================================================
# Prediction inspection
# ==================================================

def get_top_predictions(model, prompt, k=5):

    ids = torch.tensor(
        [token_to_id[word] for word in prompt.split()],
        dtype=torch.long,
        device=device
    )

    with torch.no_grad():
        logits = model(ids)[-1]

        probabilities = torch.softmax(
            logits,
            dim=-1
        )

    top_probs, top_ids = torch.topk(
        probabilities,
        k=k
    )

    return [
        (
            id_to_token[token_id.item()],
            probability.item()
        )
        for probability, token_id
        in zip(top_probs, top_ids)
    ]


# ==================================================
# Greedy generation
# ==================================================

def generate(model, prompt, max_new_tokens=15):

    words = prompt.split()

    with torch.no_grad():

        for _ in range(max_new_tokens):

            ids = torch.tensor(
                [token_to_id[word] for word in words],
                dtype=torch.long,
                device=device
            )

            logits = model(ids)[-1]

            next_id = torch.argmax(
                logits
            ).item()

            next_token = id_to_token[next_id]

            if next_token == EOS:
                break

            words.append(next_token)

    return " ".join(words)


# ==================================================
# Results
# ==================================================

prompts = [
    "mini kuzai",
    "mini kuzai learns from",
    "mini kuzai runs on"
]

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== MONO vs MULTI-HEAD =====")
print("Device:", device)

for prompt in prompts:

    print()
    print("========================================")
    print("PROMPT:", prompt)

    print()
    print("MONO-HEAD TOP 5")

    for token, probability in get_top_predictions(
        mono,
        prompt
    ):
        print(
            f"{token:14s} "
            f"{probability * 100:6.2f} %"
        )

    print()
    print("MULTI-HEAD TOP 5")

    for token, probability in get_top_predictions(
        mha,
        prompt
    ):
        print(
            f"{token:14s} "
            f"{probability * 100:6.2f} %"
        )


print()
print("===== GREEDY GENERATION =====")

print()
print("MONO:")
print(generate(mono, "mini kuzai"))

print()
print("MULTI:")
print(generate(mha, "mini kuzai"))
