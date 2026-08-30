import torch

from mini_kuzai_deep import MiniKuzaiDeep


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Load BEST checkpoint
# ==================================================

checkpoint = torch.load(
    "mini-kuzai-best.pt",
    map_location=device,
    weights_only=False
)

vocabulary = checkpoint["vocabulary"]
token_to_id = checkpoint["token_to_id"]
id_to_token = checkpoint["id_to_token"]

model = MiniKuzaiDeep(
    vocab_size=len(vocabulary),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    num_heads=checkpoint["num_heads"],
    num_layers=checkpoint["num_layers"],
    max_sequence_length=checkpoint["max_sequence_length"]
).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ==================================================
# Validation tests
# ==================================================

tests = [
    (
        "a language model runs on",
        "linux"
    ),
    (
        "mini kuzai can generate",
        "data"
    ),
    (
        "a model learns from",
        "data"
    ),
]


def inspect(prompt, expected, top_k=5):

    ids = torch.tensor(
        [
            token_to_id[word]
            for word in prompt.split()
        ],
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
        k=top_k
    )

    predicted_id = torch.argmax(
        probabilities
    ).item()

    predicted = id_to_token[predicted_id]

    expected_id = token_to_id[expected]

    expected_probability = probabilities[
        expected_id
    ].item()

    print()
    print("========================================")
    print("PROMPT   :", prompt)
    print("EXPECTED :", expected)
    print("PREDICTED:", predicted)

    print()
    print("TOP 5:")

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

    print()
    print(
        "Expected probability:",
        f"{expected_probability * 100:.2f} %"
    )

    print(
        "Correct top-1:",
        predicted == expected
    )


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== GENERALIZATION TEST =====")

print("Device              :", device)
print("Best training epoch :", checkpoint["best_epoch"])
print(
    "Best validation loss:",
    checkpoint["best_validation_loss"]
)

for prompt, expected in tests:
    inspect(prompt, expected)
