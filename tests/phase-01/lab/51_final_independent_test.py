import torch

from mini_kuzai_padding import MiniKuzaiPadding


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Frozen final checkpoint
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


# ==================================================
# Recreate frozen model
# ==================================================

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
# Independent TEST
#
# These cases were NOT used for:
# - gradient updates
# - early stopping
# - learning-rate selection
# ==================================================

tests = [
    ("a language model runs on", "linux"),
    ("a model runs on", "linux"),
    ("a model learns from", "data"),
]


# ==================================================
# Evaluation
# ==================================================

def evaluate(prompt, expected):

    input_ids = torch.tensor(
        [[
            token_to_id[word]
            for word in prompt.split()
        ]],
        dtype=torch.long,
        device=device
    )

    attention_mask = torch.ones_like(
        input_ids
    )

    with torch.no_grad():

        logits = model(
            input_ids,
            attention_mask
        )[0, -1]

        probabilities = torch.softmax(
            logits,
            dim=-1
        )

    sorted_probs, sorted_ids = torch.sort(
        probabilities,
        descending=True
    )

    predicted_id = sorted_ids[0].item()
    predicted = id_to_token[predicted_id]

    expected_id = token_to_id[expected]

    expected_rank = (
        (sorted_ids == expected_id)
        .nonzero(as_tuple=True)[0]
        .item()
        + 1
    )

    expected_probability = probabilities[
        expected_id
    ].item()

    return {
        "predicted": predicted,
        "expected_rank": expected_rank,
        "expected_probability": expected_probability,
        "sorted_probs": sorted_probs,
        "sorted_ids": sorted_ids
    }


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== FINAL INDEPENDENT TEST =====")

print("Device          :", device)
print("Checkpoint      : mini-kuzai-final.pt")

print()
print("Model parameters:", sum(
    p.numel()
    for p in model.parameters()
))

print("Batch size      :", checkpoint["batch_size"])
print("Learning rate   :", checkpoint["learning_rate"])
print("Best epoch      :", checkpoint["best_epoch"])

print(
    "Validation loss :",
    f'{checkpoint["best_validation_loss"]:.6f}'
)


correct = 0


for prompt, expected in tests:

    result = evaluate(
        prompt,
        expected
    )

    is_correct = (
        result["predicted"] == expected
    )

    if is_correct:
        correct += 1

    print()
    print("========================================")
    print("PROMPT   :", prompt)
    print("EXPECTED :", expected)

    print(
        "PREDICTED:",
        result["predicted"]
    )

    print(
        "RANK     :",
        result["expected_rank"]
    )

    print(
        "EXPECTED PROBABILITY:",
        f'{result["expected_probability"] * 100:.2f} %'
    )

    print(
        "TOP-1 CORRECT:",
        is_correct
    )

    print()
    print("TOP 5:")

    for probability, token_id in zip(
        result["sorted_probs"][:5],
        result["sorted_ids"][:5]
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
print("===== FINAL SCORE =====")

print(
    "Correct top-1:",
    f"{correct}/{len(tests)}"
)

print(
    "Accuracy     :",
    f"{correct / len(tests) * 100:.2f} %"
)
