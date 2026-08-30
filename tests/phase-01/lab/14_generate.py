import torch

from mini_kuzai import MiniKuzai


# ==================================================
# Device
# ==================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Load checkpoint
# ==================================================

checkpoint = torch.load(
    "mini-kuzai.pt",
    map_location=device,
    weights_only=False
)

vocabulary = checkpoint["vocabulary"]
token_to_id = checkpoint["token_to_id"]
id_to_token = checkpoint["id_to_token"]


# ==================================================
# Recreate model
# ==================================================

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
# Generation
# ==================================================

prompt = "mini kuzai"

generated_words = prompt.split()

max_new_tokens = 8


print("===== MINI-KUZAI GENERATION =====")

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

        # Only the final position predicts
        # the next token.
        next_token_logits = logits[-1]

        probabilities = torch.softmax(
            next_token_logits,
            dim=-1
        )

        # Deterministic generation:
        # choose highest probability.
        next_token_id = torch.argmax(
            probabilities
        ).item()

        next_word = id_to_token[next_token_id]

        probability = probabilities[
            next_token_id
        ].item()

        print(
            f"Step {step + 1}: "
            f"{next_word:12s} "
            f"probability={probability:.4f}"
        )

        generated_words.append(next_word)


print("\n===== RESULT =====")
print(" ".join(generated_words))
