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
# NEW confirmatory cases
#
# Defined after the NO-BETA hypothesis.
# Do not tune variants from these results.
# ==================================================

tests = [
    ("language model can generate", "text"),
    ("mini kuzai can generate", "text"),
    ("language model learns from", "data"),
    ("mini kuzai learns using", "data"),
    ("model runs using", "linux"),
    ("mini kuzai uses", "linux"),
    ("data is used by", "a"),
    ("linux can run", "a"),
]


# ==================================================
# Leakage / vocabulary checks
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


# ==================================================
# Final residual BEFORE final_norm
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
# Frozen variants
# ==================================================

def decode_variant(x, variant):

    norm = model.final_norm

    shape = (
        checkpoint["embedding_dim"],
    )

    gamma = norm.weight
    beta = norm.bias

    ones = torch.ones_like(gamma)
    zeros = torch.zeros_like(beta)


    if variant == "BASELINE":

        return norm(x)


    if variant == "NO BETA":

        return F.layer_norm(
            x,
            shape,
            weight=gamma,
            bias=zeros,
            eps=norm.eps
        )


    if variant == "NO AFFINE":

        return F.layer_norm(
            x,
            shape,
            weight=ones,
            bias=zeros,
            eps=norm.eps
        )


    if variant == "RAW NO NORM":

        return x


    raise ValueError(variant)


# ==================================================
# Evaluate
# ==================================================

def evaluate(prompt, expected, variant):

    x = final_residual(prompt)

    decoded = decode_variant(
        x,
        variant
    )

    logits = model.lm_head(
        decoded
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

    expected_probability = probabilities[
        expected_id
    ].item()

    return (
        predicted,
        rank,
        expected_probability
    )


# ==================================================
# Run
# ==================================================

variants = [
    "BASELINE",
    "NO BETA",
    "NO AFFINE",
    "RAW NO NORM",
]


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== CONFIRMATORY FINAL-NORM ABLATION =====")

print("Checkpoint       : mini-kuzai-final.pt")
print("MODEL MODIFIED   : NO")
print("Training         : NO")
print("Cases            :", len(tests))

print()
print("Unknown tokens   :", len(unknown_tokens))
print("Prefix leakage   :", len(leaked_prefixes))

if unknown_tokens:
    print("UNKNOWN:", unknown_tokens)

if leaked_prefixes:
    print("LEAKED:", leaked_prefixes)


summary = {
    variant: {
        "top1": 0,
        "top3": 0,
        "prob_sum": 0.0
    }
    for variant in variants
}


for prompt, expected in tests:

    print()
    print("========================================")
    print("PROMPT   :", prompt)
    print("EXPECTED :", expected)

    print()

    print(
        f"{'VARIANT':14s}"
        f"{'PREDICTED':12s}"
        f"{'EXP PROB':>10s}"
        f"{'RANK':>7s}"
    )


    for variant in variants:

        predicted, rank, probability = evaluate(
            prompt,
            expected,
            variant
        )

        if predicted == expected:
            summary[variant]["top1"] += 1

        if rank <= 3:
            summary[variant]["top3"] += 1

        summary[variant][
            "prob_sum"
        ] += probability


        print(
            f"{variant:14s}"
            f"{predicted:12s}"
            f"{probability * 100:9.2f}%"
            f"{rank:7d}"
        )


print()
print("===== SUMMARY =====")

print()

print(
    f"{'VARIANT':14s}"
    f"{'TOP1':>9s}"
    f"{'TOP3':>9s}"
    f"{'AVG EXP':>12s}"
)


for variant in variants:

    top1 = summary[variant]["top1"]
    top3 = summary[variant]["top3"]

    average_probability = (
        summary[variant]["prob_sum"]
        / len(tests)
    )

    print(
        f"{variant:14s}"
        f"{top1:4d}/{len(tests)}"
        f"{top3:6d}/{len(tests)}"
        f"{average_probability * 100:11.2f}%"
    )


print()
print("VARIANTS TUNED FROM THIS SET: NO")
