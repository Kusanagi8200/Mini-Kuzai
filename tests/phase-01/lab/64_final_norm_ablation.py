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
# Diagnostic set
#
# Already observed previously.
# This is NOT a blind test anymore.
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
# Final residual stream BEFORE final_norm
# ==================================================

def get_final_residual(prompt):

    words = prompt.split()

    input_ids = torch.tensor(
        [[
            token_to_id[word]
            for word in words
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
# Different final-normalization variants
# ==================================================

def normalize_variant(x, variant):

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


    if variant == "NO GAMMA":

        return F.layer_norm(
            x,
            shape,
            weight=ones,
            bias=beta,
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


    raise ValueError(
        f"Unknown variant: {variant}"
    )


# ==================================================
# Prediction
# ==================================================

def evaluate(prompt, expected, variant):

    x = get_final_residual(prompt)

    decoded = normalize_variant(
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

    predicted_id = sorted_ids[
        0
    ].item()

    predicted = id_to_token[
        predicted_id
    ]

    expected_id = token_to_id[
        expected
    ]

    expected_probability = probabilities[
        expected_id
    ].item()

    rank = (
        (sorted_ids == expected_id)
        .nonzero(as_tuple=True)[0]
        .item()
        + 1
    )

    return (
        predicted,
        expected_probability,
        rank
    )


# ==================================================
# Run experiments
# ==================================================

variants = [
    "BASELINE",
    "NO BETA",
    "NO GAMMA",
    "NO AFFINE",
    "RAW NO NORM",
]


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== FINAL LAYERNORM ABLATION =====")

print("Checkpoint      : mini-kuzai-final.pt")
print("MODEL ON DISK   : UNCHANGED")
print("Diagnostic cases:", len(tests))

print()


summary = {
    variant: {
        "correct": 0,
        "top3": 0
    }
    for variant in variants
}


for prompt, expected in tests:

    print("========================================")
    print("PROMPT   :", prompt)
    print("EXPECTED :", expected)

    print()

    print(
        f"{'VARIANT':14s}"
        f"{'PREDICTED':12s}"
        f"{'EXP PROB':>10s}"
        f"{'RANK':>7s}"
        f"{'TOP1':>8s}"
    )


    for variant in variants:

        predicted, probability, rank = evaluate(
            prompt,
            expected,
            variant
        )

        correct = (
            predicted == expected
        )

        if correct:
            summary[variant]["correct"] += 1

        if rank <= 3:
            summary[variant]["top3"] += 1


        print(
            f"{variant:14s}"
            f"{predicted:12s}"
            f"{probability * 100:9.2f}%"
            f"{rank:7d}"
            f"{str(correct):>8s}"
        )

    print()


# ==================================================
# Summary
# ==================================================

print("===== SUMMARY =====")

print()

print(
    f"{'VARIANT':14s}"
    f"{'TOP-1':>10s}"
    f"{'TOP-3':>10s}"
)

for variant in variants:

    correct = summary[
        variant
    ]["correct"]

    top3 = summary[
        variant
    ]["top3"]

    print(
        f"{variant:14s}"
        f"{correct:4d}/6"
        f"{top3:7d}/6"
    )


print()
print("TRAINING PERFORMED : NO")
print("WEIGHTS MODIFIED   : NO")
