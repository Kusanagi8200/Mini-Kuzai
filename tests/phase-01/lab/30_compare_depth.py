import torch

from mini_kuzai import MiniKuzai
from mini_kuzai_mha import MiniKuzaiMHA
from mini_kuzai_deep import MiniKuzaiDeep


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Checkpoints
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

deep_ckpt = torch.load(
    "mini-kuzai-deep.pt",
    map_location=device,
    weights_only=False
)


vocabulary = mono_ckpt["vocabulary"]
token_to_id = mono_ckpt["token_to_id"]
id_to_token = mono_ckpt["id_to_token"]
EOS = mono_ckpt["eos_token"]


assert vocabulary == mha_ckpt["vocabulary"]
assert vocabulary == deep_ckpt["vocabulary"]


# ==================================================
# Models
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


deep = MiniKuzaiDeep(
    vocab_size=len(vocabulary),
    embedding_dim=deep_ckpt["embedding_dim"],
    hidden_dim=deep_ckpt["hidden_dim"],
    num_heads=deep_ckpt["num_heads"],
    num_layers=deep_ckpt["num_layers"],
    max_sequence_length=deep_ckpt["max_sequence_length"]
).to(device)

deep.load_state_dict(
    deep_ckpt["model_state_dict"]
)

deep.eval()


# ==================================================
# Helpers
# ==================================================

def parameter_count(model):
    return sum(
        p.numel()
        for p in model.parameters()
    )


def top_predictions(model, prompt, k=4):

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

            token = id_to_token[next_id]

            if token == EOS:
                break

            words.append(token)

    return " ".join(words)


# ==================================================
# Deep training history
# ==================================================

deep_history = deep_ckpt["loss_history"]

best_deep_loss = min(deep_history)
best_deep_epoch = deep_history.index(
    best_deep_loss
) + 1


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== ARCHITECTURE COMPARISON =====")

print(
    "Mono / 1 block :",
    parameter_count(mono),
    "parameters"
)

print(
    "MHA / 1 block  :",
    parameter_count(mha),
    "parameters"
)

print(
    "MHA / 2 blocks :",
    parameter_count(deep),
    "parameters"
)

print()
print("===== DEEP TRAINING HISTORY =====")

print(
    "Best epoch:",
    best_deep_epoch
)

print(
    "Best loss :",
    f"{best_deep_loss:.6f}"
)

print(
    "Final loss:",
    f"{deep_history[-1]:.6f}"
)


prompts = [
    "mini kuzai",
    "mini kuzai learns from",
    "mini kuzai runs on"
]


models = [
    ("MONO-1", mono),
    ("MHA-1", mha),
    ("MHA-2", deep)
]


for prompt in prompts:

    print()
    print("========================================")
    print("PROMPT:", prompt)

    for name, model in models:

        print()
        print(name)

        for token, probability in top_predictions(
            model,
            prompt
        ):

            print(
                f"{token:14s} "
                f"{probability * 100:6.2f} %"
            )


print()
print("===== GREEDY GENERATION =====")

for name, model in models:

    print()
    print(
        f"{name}:",
        generate(model, "mini kuzai")
    )
