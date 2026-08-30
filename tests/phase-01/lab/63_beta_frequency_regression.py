from collections import Counter

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

EOS = checkpoint["eos_token"]


model = MiniKuzaiPadding(
    vocab_size=len(vocabulary),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    num_heads=checkpoint["num_heads"],
    num_layers=checkpoint["num_layers"],
    max_sequence_length=checkpoint["max_sequence_length"],
    pad_token_id=checkpoint["pad_token_id"]
).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ==================================================
# Count training targets
# ==================================================

target_counts = Counter()

for sentence in train_lines:

    tokens = sentence.split() + [EOS]

    target_counts.update(
        tokens[1:]
    )


# ==================================================
# Beta vocabulary effect
# ==================================================

with torch.no_grad():

    beta = model.final_norm.bias

    beta_effect = (
        model.lm_head.weight @ beta
    ).cpu().double()


counts = torch.tensor(
    [
        target_counts[token]
        for token in vocabulary
    ],
    dtype=torch.float64
)

x = torch.log1p(counts)
y = beta_effect


# ==================================================
# Linear regression
#
# y = slope * x + intercept
# ==================================================

X = torch.stack(
    [
        x,
        torch.ones_like(x)
    ],
    dim=1
)

solution = torch.linalg.lstsq(
    X,
    y
).solution

slope = solution[0]
intercept = solution[1]

predicted = (
    slope * x
    + intercept
)

residuals = (
    y - predicted
)


# ==================================================
# R²
# ==================================================

ss_res = torch.sum(
    (y - predicted) ** 2
)

ss_tot = torch.sum(
    (y - y.mean()) ** 2
)

r_squared = (
    1.0 - ss_res / ss_tot
).item()


# ==================================================
# Build table
# ==================================================

rows = []

for token in vocabulary:

    token_id = token_to_id[token]

    rows.append(
        (
            token,
            int(counts[token_id].item()),
            x[token_id].item(),
            y[token_id].item(),
            predicted[token_id].item(),
            residuals[token_id].item()
        )
    )


most_positive = sorted(
    rows,
    key=lambda row: row[5],
    reverse=True
)

most_negative = sorted(
    rows,
    key=lambda row: row[5]
)


# ==================================================
# Results
# ==================================================

print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== BETA FREQUENCY REGRESSION =====")

print("Checkpoint     : mini-kuzai-final.pt")
print("MODEL MODIFIED : NO")

print()
print("===== REGRESSION =====")

print(
    "Slope     :",
    f"{slope.item():+.6f}"
)

print(
    "Intercept :",
    f"{intercept.item():+.6f}"
)

print(
    "R²        :",
    f"{r_squared:.4f}"
)


print()
print("===== MOST ABOVE FREQUENCY EXPECTATION =====")

print(
    f"{'TOKEN':12s}"
    f"{'COUNT':>7s}"
    f"{'ACTUAL':>10s}"
    f"{'EXPECTED':>11s}"
    f"{'RESIDUAL':>11s}"
)

for row in most_positive[:10]:

    token, count, log_count, actual, expected, residual = row

    print(
        f"{token:12s}"
        f"{count:7d}"
        f"{actual:10.4f}"
        f"{expected:11.4f}"
        f"{residual:11.4f}"
    )


print()
print("===== MOST BELOW FREQUENCY EXPECTATION =====")

print(
    f"{'TOKEN':12s}"
    f"{'COUNT':>7s}"
    f"{'ACTUAL':>10s}"
    f"{'EXPECTED':>11s}"
    f"{'RESIDUAL':>11s}"
)

for row in most_negative[:10]:

    token, count, log_count, actual, expected, residual = row

    print(
        f"{token:12s}"
        f"{count:7d}"
        f"{actual:10.4f}"
        f"{expected:11.4f}"
        f"{residual:11.4f}"
    )


print()
print("===== SELECTED TOKENS =====")

selected = [
    "<eos>",
    "data",
    "linux",
    "text",
    "using",
    "mini",
]

for token in selected:

    token_id = token_to_id[token]

    print(
        f"{token:12s} "
        f"count={int(counts[token_id].item()):2d}  "
        f"actual={y[token_id].item():+7.4f}  "
        f"freq-model={predicted[token_id].item():+7.4f}  "
        f"residual={residuals[token_id].item():+7.4f}"
    )
