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


prompt = "mini kuzai"

generated_words = prompt.split()

max_new_tokens = 15


print("===== MINI-KUZAI EOS GENERATION =====")

print("\nPrompt:")
print(prompt)

with torch.no_grad():

    for step in range(max_new_tokens):

        ids = torch.tensor(
            [
                token_to_id[word]
                for word in generated_words
            ],
            dtype=torch.long,
            device=device
        )

        logits = model(ids)

        next_logits = logits[-1]

        probabilities = torch.softmax(
            next_logits,
            dim=-1
        )

        next_id = torch.argmax(
            probabilities
        ).item()

        next_token = id_to_token[next_id]

        probability = probabilities[
            next_id
        ].item()

        print(
            f"Step {step + 1:2d}: "
            f"{next_token:12s} "
            f"probability={probability:.4f}"
        )

        if next_token == EOS:
            print("\nEOS reached -> generation stopped")
            break

        generated_words.append(next_token)


print("\n===== RESULT =====")
print(" ".join(generated_words))
