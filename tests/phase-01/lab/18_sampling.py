import torch

from mini_kuzai import MiniKuzai

torch.manual_seed(42)

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


def generate(prompt, max_new_tokens=12):

    words = prompt.split()

    with torch.no_grad():

        for _ in range(max_new_tokens):

            ids = torch.tensor(
                [token_to_id[word] for word in words],
                dtype=torch.long,
                device=device
            )

            logits = model(ids)
            probabilities = torch.softmax(
                logits[-1],
                dim=-1
            )

            # Sampling instead of argmax
            next_id = torch.multinomial(
                probabilities,
                num_samples=1
            ).item()

            next_token = id_to_token[next_id]

            if next_token == EOS:
                break

            words.append(next_token)

    return " ".join(words)


print("===== MINI-KUZAI SAMPLING =====")

for i in range(10):
    print(f"{i + 1:2d}: {generate('mini kuzai')}")
