import torch

from mini_kuzai import MiniKuzai


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

checkpoint = torch.load(
    "mini-kuzai-eos.pt",
    map_location=device,
    weights_only=False
)

vocabulary = checkpoint["vocabulary"]
token_to_id = checkpoint["token_to_id"]
id_to_token = checkpoint["id_to_token"]
EOS = checkpoint["eos_token"]

model = MiniKuzai(
    vocab_size=len(vocabulary),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    max_sequence_length=checkpoint["max_sequence_length"]
).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ==================================================
# Inspect probability distribution
# ==================================================

def inspect_temperature(prompt, temperature):

    words = prompt.split()

    ids = torch.tensor(
        [token_to_id[word] for word in words],
        dtype=torch.long,
        device=device
    )

    with torch.no_grad():

        logits = model(ids)[-1]

        probabilities = torch.softmax(
            logits / temperature,
            dim=-1
        )

    top_probabilities, top_ids = torch.topk(
        probabilities,
        k=5
    )

    print(
        f"\nTemperature = {temperature}"
    )

    for probability, token_id in zip(
        top_probabilities,
        top_ids
    ):
        print(
            f"{id_to_token[token_id.item()]:12s} "
            f"{probability.item() * 100:6.2f} %"
        )


# ==================================================
# Generate
# ==================================================

def generate(prompt, temperature, max_new_tokens=12):

    words = prompt.split()

    with torch.no_grad():

        for _ in range(max_new_tokens):

            ids = torch.tensor(
                [token_to_id[word] for word in words],
                dtype=torch.long,
                device=device
            )

            logits = model(ids)[-1]

            probabilities = torch.softmax(
                logits / temperature,
                dim=-1
            )

            next_id = torch.multinomial(
                probabilities,
                num_samples=1
            ).item()

            next_token = id_to_token[next_id]

            if next_token == EOS:
                break

            words.append(next_token)

    return " ".join(words)


print("===== MINI-KUZAI TEMPERATURE =====")

print("\n===== NEXT TOKEN AFTER 'mini kuzai' =====")

for temperature in [0.3, 1.0, 1.5]:
    inspect_temperature(
        "mini kuzai",
        temperature
    )


print("\n===== GENERATIONS =====")

for temperature in [0.3, 1.0, 1.5]:

    print(
        f"\n--- TEMPERATURE {temperature} ---"
    )

    torch.manual_seed(42)

    for i in range(5):

        print(
            f"{i + 1}: "
            f"{generate('mini kuzai', temperature)}"
        )
