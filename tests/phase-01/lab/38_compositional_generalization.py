import torch

from mini_kuzai_deep import MiniKuzaiDeep


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==================================================
# Original training data
# ==================================================

train_lines = [
    "mini kuzai runs on linux",
    "mini kuzai learns from data",
    "mini kuzai can generate text",
    "mini kuzai is a language model",
    "a language model learns from data",
    "a language model can generate text",
    "linux runs a model",
    "data helps a model learn",
    "mini kuzai uses a model",
    "a model uses data",
    "a model uses linux",
    "text uses data",
]


# ==================================================
# Controlled unseen prefixes
# ==================================================

tests = [
    ("a language model runs on", "linux"),
    ("a model runs on", "linux"),
    ("a model learns from", "data"),
]


# ==================================================
# Load best checkpoint
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
# Exact prefix detection
# ==================================================

def prefix_seen(prefix):

    prefix_words = prefix.split()

    for line in train_lines:

        words = line.split()

        n = len(prefix_words)

        for i in range(len(words) - n + 1):

            if words[i:i+n] == prefix_words:
                return True

    return False


# ==================================================
# Evaluate
# ==================================================

def evaluate(prompt, expected):

    ids = torch.tensor(
        [token_to_id[w] for w in prompt.split()],
        dtype=torch.long,
        device=device
    )

    with torch.no_grad():

        logits = model(ids)[-1]

        probabilities = torch.softmax(
            logits,
            dim=-1
        )

    sorted_probs, sorted_ids = torch.sort(
        probabilities,
        descending=True
    )

    expected_id = token_to_id[expected]

    expected_position = (
        sorted_ids == expected_id
    ).nonzero(as_tuple=True)[0].item()

    expected_rank = expected_position + 1

    predicted_id = sorted_ids[0].item()
    predicted = id_to_token[predicted_id]

    print()
    print("========================================")
    print("PROMPT       :", prompt)
    print("PREFIX SEEN  :", prefix_seen(prompt))
    print("EXPECTED     :", expected)
    print("PREDICTED    :", predicted)
    print("EXPECTED RANK:", expected_rank)

    print()
    print("TOP 5")

    for probability, token_id in zip(
        sorted_probs[:5],
        sorted_ids[:5]
    ):

        token = id_to_token[token_id.item()]

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
        "Correct top-1:",
        predicted == expected
    )

    print(
        "Expected in top-3:",
        expected_rank <= 3
    )


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== COMPOSITIONAL GENERALIZATION =====")

print("Device:", device)

for prompt, expected in tests:
    evaluate(prompt, expected)
