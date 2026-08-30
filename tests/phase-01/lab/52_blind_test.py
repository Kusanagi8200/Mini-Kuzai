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

train_lines = checkpoint["train_lines"]
validation_lines = checkpoint["validation_lines"]

PAD_ID = checkpoint["pad_token_id"]


# ==================================================
# Frozen model
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
# NEW BLIND TEST
#
# Defined only after model configuration was frozen.
# Do not tune the model from these results.
# ==================================================

tests = [
    ("a language model runs using", "linux"),
    ("mini kuzai runs using", "linux"),
    ("a language model learns using", "data"),
    ("mini kuzai can learn using", "data"),
    ("a model can generate", "text"),
    ("linux is used by a", "model"),
]


# ==================================================
# Leakage checks
# ==================================================

reference_lines = (
    train_lines
    + validation_lines
)


def prefix_seen(prefix):

    prefix_words = prefix.split()
    n = len(prefix_words)

    for line in reference_lines:

        words = line.split()

        for i in range(
            len(words) - n + 1
        ):

            if words[i:i+n] == prefix_words:
                return True

    return False


unknown_tokens = sorted({
    word
    for prompt, expected in tests
    for word in prompt.split() + [expected]
    if word not in token_to_id
})


leaked_prefixes = [
    prompt
    for prompt, _ in tests
    if prefix_seen(prompt)
]


if unknown_tokens:
    raise RuntimeError(
        f"Unknown tokens: {unknown_tokens}"
    )

if leaked_prefixes:
    raise RuntimeError(
        f"Prefix leakage: {leaked_prefixes}"
    )


# ==================================================
# Prediction
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

    expected_id = token_to_id[
        expected
    ]

    predicted = id_to_token[
        sorted_ids[0].item()
    ]

    expected_rank = (
        (sorted_ids == expected_id)
        .nonzero(as_tuple=True)[0]
        .item()
        + 1
    )

    expected_probability = probabilities[
        expected_id
    ].item()

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
print("===== BLIND GENERALIZATION TEST =====")

print("Checkpoint      : mini-kuzai-final.pt")
print("Device          :", device)
print("Test cases      :", len(tests))

print()
print("Unknown tokens  :", len(unknown_tokens))
print("Prefix leakage  :", len(leaked_prefixes))

correct = 0
top3 = 0


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

    if predicted == expected:
        correct += 1

    if rank <= 3:
        top3 += 1

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
    print("TOP 3:")

    for p, token_id in zip(
        sorted_probs[:3],
        sorted_ids[:3]
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


print()
print("===== BLIND SCORE =====")

print(
    "Top-1:",
    f"{correct}/{len(tests)}",
    f"({correct / len(tests) * 100:.2f} %)"
)

print(
    "Top-3:",
    f"{top3}/{len(tests)}",
    f"({top3 / len(tests) * 100:.2f} %)"
)

print()
print("MODEL MODIFIED: NO")
