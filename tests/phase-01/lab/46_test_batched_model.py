import torch

from mini_kuzai_padding import MiniKuzaiPadding


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Load checkpoint
# ==================================================

checkpoint = torch.load(
    "mini-kuzai-batched.pt",
    map_location=device,
    weights_only=False
)

vocabulary = checkpoint["vocabulary"]
token_to_id = checkpoint["token_to_id"]
id_to_token = checkpoint["id_to_token"]

PAD_ID = checkpoint["pad_token_id"]


# ==================================================
# Model
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
# Independent tests
# ==================================================

tests = [
    ("a language model runs on", "linux"),
    ("a model runs on", "linux"),
    ("a model learns from", "data"),
]


def evaluate(prompt, expected):

    words = prompt.split()

    input_ids = torch.tensor(
        [[token_to_id[word] for word in words]],
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

    expected_probability = (
        probabilities[expected_id]
        .item()
    )

    return (
        predicted,
        expected_rank,
        expected_probability,
        sorted_probs,
        sorted_ids
    )


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== BATCHED MODEL GENERALIZATION =====")

print("Device      :", device)
print("Batch size  :", checkpoint["batch_size"])
print("Best epoch  :", checkpoint["best_epoch"])

print(
    "Best val    :",
    f'{checkpoint["best_validation_loss"]:.6f}'
)


for prompt, expected in tests:

    (
        predicted,
        rank,
        probability,
        sorted_probs,
        sorted_ids
    ) = evaluate(
        prompt,
        expected
    )

    print()
    print("========================================")
    print("PROMPT   :", prompt)
    print("EXPECTED :", expected)
    print("PREDICTED:", predicted)
    print("RANK     :", rank)

    print(
        "EXPECTED PROBABILITY:",
        f"{probability * 100:.2f} %"
    )

    print(
        "TOP-1 CORRECT:",
        predicted == expected
    )

    print()
    print("TOP 5:")

    for p, token_id in zip(
        sorted_probs[:5],
        sorted_ids[:5]
    ):

        token = id_to_token[
            token_id.item()
        ]

        marker = ""

        if token == expected:
            marker = " <-- EXPECTED"

        print(
            f"{token:12s} "
            f"{p.item() * 100:6.2f} %"
            f"{marker}"
        )
