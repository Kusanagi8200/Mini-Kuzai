import torch
import torch.nn.functional as F

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
# Prompts already inspected earlier in the lab
# ==================================================

previous_prompts = {
    "a language model runs on",
    "mini kuzai can generate",
    "a model learns from",

    "a language model runs using",
    "mini kuzai runs using",
    "a language model learns using",
    "mini kuzai can learn using",
    "a model can generate",
    "linux is used by a",

    "language model can generate",
    "language model learns from",
    "mini kuzai learns using",
    "model runs using",
    "mini kuzai uses",
    "data is used by",
    "linux can run",
}


# ==================================================
# NEW confirmatory cases
#
# Defined only now.
# ==================================================

tests = [
    ("language model runs using", "linux"),
    ("language model runs on", "linux"),
    ("language model can learn from", "data"),
    ("a model learns using", "data"),
    ("linux learns from", "data"),
    ("linux uses data", "<eos>"),
    ("mini kuzai uses data", "<eos>"),
    ("a language model uses linux", "<eos>"),
]


# ==================================================
# Checks
# ==================================================

reference_lines = (
    train_lines
    + validation_lines
)


def contained_in_reference(prompt):

    prompt_words = prompt.split()
    n = len(prompt_words)

    for line in reference_lines:

        words = line.split()

        for i in range(
            len(words) - n + 1
        ):

            if words[i:i+n] == prompt_words:
                return True

    return False


unknown_tokens = sorted({
    token
    for prompt, expected in tests
    for token in prompt.split() + [expected]
    if token not in token_to_id
})


reference_leakage = [
    prompt
    for prompt, _ in tests
    if contained_in_reference(prompt)
]


previously_used = [
    prompt
    for prompt, _ in tests
    if prompt in previous_prompts
]


duplicate_tests = (
    len({
        prompt
        for prompt, _ in tests
    })
    != len(tests)
)


# ==================================================
# Final residual
# ==================================================

def final_residual(prompt):

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

    positions = torch.arange(
        input_ids.shape[1],
        device=device
    )

    x = (
        model.token_embedding(input_ids)
        + model.position_embedding(positions)
    )

    for block in model.blocks:

        x = x + block.attention(
            block.norm1(x),
            attention_mask
        )

        x = x + block.mlp(
            block.norm2(x)
        )

    return x


# ==================================================
# Decode variants
# ==================================================

def decode(x, variant):

    norm = model.final_norm

    if variant == "BASELINE":
        return norm(x)

    if variant == "NO BETA":

        return F.layer_norm(
            x,
            (checkpoint["embedding_dim"],),
            weight=norm.weight,
            bias=torch.zeros_like(norm.bias),
            eps=norm.eps
        )

    raise ValueError(variant)


# ==================================================
# Evaluate
# ==================================================

def evaluate(prompt, expected, variant):

    x = final_residual(prompt)

    logits = model.lm_head(
        decode(x, variant)
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

    rank = (
        (sorted_ids == expected_id)
        .nonzero(as_tuple=True)[0]
        .item()
        + 1
    )

    probability = probabilities[
        expected_id
    ].item()

    return (
        predicted,
        rank,
        probability
    )


# ==================================================
# Print checks BEFORE evaluation
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== TRUE BETA CONFIRMATION =====")

print("Checkpoint        : mini-kuzai-final.pt")
print("MODEL MODIFIED    : NO")
print("Training          : NO")
print("Cases             :", len(tests))

print()
print("Unknown tokens    :", len(unknown_tokens))
print("Reference leakage :", len(reference_leakage))
print("Previously used   :", len(previously_used))
print("Duplicate tests   :", duplicate_tests)


if unknown_tokens:
    print("UNKNOWN:", unknown_tokens)

if reference_leakage:
    print("LEAKED:", reference_leakage)

if previously_used:
    print("OLD:", previously_used)


# Hard stop if the test is contaminated.

if (
    unknown_tokens
    or reference_leakage
    or previously_used
    or duplicate_tests
):
    raise RuntimeError(
        "Confirmation set failed independence checks."
    )


# ==================================================
# Actual confirmation
# ==================================================

variants = [
    "BASELINE",
    "NO BETA",
]


summary = {
    variant: {
        "top1": 0,
        "top3": 0,
        "probability": 0.0
    }
    for variant in variants
}


for prompt, expected in tests:

    print()
    print("========================================")
    print("PROMPT   :", prompt)
    print("EXPECTED :", expected)

    print()

    for variant in variants:

        predicted, rank, probability = evaluate(
            prompt,
            expected,
            variant
        )

        correct = (
            predicted == expected
        )

        if correct:
            summary[variant]["top1"] += 1

        if rank <= 3:
            summary[variant]["top3"] += 1

        summary[variant][
            "probability"
        ] += probability


        print(
            f"{variant:10s} "
            f"pred={predicted:10s} "
            f"expected_prob={probability * 100:6.2f}% "
            f"rank={rank:2d} "
            f"top1={correct}"
        )


print()
print("===== CONFIRMATION SUMMARY =====")

print()

for variant in variants:

    top1 = summary[
        variant
    ]["top1"]

    top3 = summary[
        variant
    ]["top3"]

    avg_probability = (
        summary[
            variant
        ]["probability"]
        / len(tests)
    )

    print(
        f"{variant:10s} "
        f"TOP1={top1}/{len(tests)}  "
        f"TOP3={top3}/{len(tests)}  "
        f"AVG_EXPECTED={avg_probability * 100:.2f}%"
    )


print()
print("VARIANT SELECTION CHANGED: NO")
print("MODEL MODIFIED           : NO")
