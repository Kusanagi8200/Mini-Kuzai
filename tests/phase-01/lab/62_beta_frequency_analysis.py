import math
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
# Count TRAINING TARGETS
#
# Example:
# mini kuzai runs on linux <eos>
#
# inputs :
# mini kuzai runs on linux
#
# targets:
# kuzai runs on linux <eos>
# ==================================================

target_counts = Counter()

for sentence in train_lines:

    tokens = sentence.split() + [EOS]

    targets = tokens[1:]

    target_counts.update(targets)


total_targets = sum(
    target_counts.values()
)


# ==================================================
# Beta -> LM-head vocabulary contribution
# ==================================================

with torch.no_grad():

    beta = model.final_norm.bias

    beta_logits = (
        model.lm_head.weight @ beta
    ).cpu()


# ==================================================
# Build vectors
# ==================================================

counts = torch.tensor(
    [
        float(target_counts[token])
        for token in vocabulary
    ],
    dtype=torch.float64
)

log_counts = torch.log1p(counts)

effects = beta_logits.to(
    dtype=torch.float64
)


# ==================================================
# Pearson correlations
# ==================================================

def pearson(x, y):

    x = x - x.mean()
    y = y - y.mean()

    return (
        torch.dot(x, y)
        /
        (
            torch.norm(x)
            * torch.norm(y)
        )
    ).item()


corr_count = pearson(
    counts,
    effects
)

corr_log_count = pearson(
    log_counts,
    effects
)


# ==================================================
# Display
# ==================================================

rows = []

for token in vocabulary:

    token_id = token_to_id[token]

    count = target_counts[token]

    frequency = (
        count / total_targets
        if total_targets
        else 0
    )

    beta_effect = beta_logits[
        token_id
    ].item()

    rows.append(
        (
            token,
            count,
            frequency,
            beta_effect
        )
    )


rows_by_frequency = sorted(
    rows,
    key=lambda x: (
        x[1],
        x[3]
    ),
    reverse=True
)


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== BETA vs TRAINING TARGET FREQUENCY =====")

print("Checkpoint       : mini-kuzai-final.pt")
print("MODEL MODIFIED   : NO")
print("Training lines   :", len(train_lines))
print("Training targets :", total_targets)

print()
print("===== CORRELATIONS =====")

print(
    "Pearson(count, beta)      :",
    f"{corr_count:+.4f}"
)

print(
    "Pearson(log1p(count), beta):",
    f"{corr_log_count:+.4f}"
)


print()
print("===== TOKENS BY TARGET FREQUENCY =====")

print(
    f"{'TOKEN':12s}"
    f"{'COUNT':>8s}"
    f"{'FREQ':>10s}"
    f"{'BETA':>10s}"
)

for token, count, frequency, beta_effect in rows_by_frequency:

    print(
        f"{token:12s}"
        f"{count:8d}"
        f"{frequency * 100:9.2f}%"
        f"{beta_effect:10.4f}"
    )


print()
print("===== SELECTED TOKENS =====")

for token in [
    "<eos>",
    "data",
    "linux",
    "text",
    "mini",
    "using",
]:

    count = target_counts[token]

    frequency = (
        count / total_targets
        if total_targets
        else 0
    )

    beta_effect = beta_logits[
        token_to_id[token]
    ].item()

    print(
        f"{token:12s}"
        f"targets={count:2d}  "
        f"freq={frequency * 100:6.2f}%  "
        f"beta={beta_effect:+.4f}"
    )
