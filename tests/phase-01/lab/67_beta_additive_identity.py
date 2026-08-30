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
# Get residual stream before final LayerNorm
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
# Baseline vs NO-BETA logits
# ==================================================

def get_logit_delta(prompt):

    x = final_residual(prompt)

    norm = model.final_norm

    baseline = norm(x)

    no_beta = F.layer_norm(
        x,
        (checkpoint["embedding_dim"],),
        weight=norm.weight,
        bias=torch.zeros_like(norm.bias),
        eps=norm.eps
    )

    baseline_logits = model.lm_head(
        baseline
    )[0, -1]

    no_beta_logits = model.lm_head(
        no_beta
    )[0, -1]

    return (
        baseline_logits
        - no_beta_logits
    )


# ==================================================
# Theoretical beta contribution
# ==================================================

with torch.no_grad():

    theoretical_delta = (
        model.lm_head.weight
        @ model.final_norm.bias
    )


# ==================================================
# Several unrelated prompts
# ==================================================

prompts = [
    "language model runs using",
    "a model learns using",
    "linux uses data",
    "a model can generate",
]


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== BETA ADDITIVE LOGIT IDENTITY =====")

print("Checkpoint     : mini-kuzai-final.pt")
print("MODEL MODIFIED : NO")

print()

all_deltas = []


with torch.no_grad():

    for prompt in prompts:

        delta = get_logit_delta(
            prompt
        )

        all_deltas.append(
            delta
        )

        max_error = torch.max(
            torch.abs(
                delta
                - theoretical_delta
            )
        ).item()

        print(
            f"PROMPT: {prompt}"
        )

        print(
            "max |measured - W@beta|:",
            f"{max_error:.10f}"
        )

        print()


# ==================================================
# Compare prompt-to-prompt deltas
# ==================================================

print("===== PROMPT INVARIANCE =====")

reference = all_deltas[0]

for index in range(
    1,
    len(all_deltas)
):

    difference = torch.max(
        torch.abs(
            reference
            - all_deltas[index]
        )
    ).item()

    print(
        f"prompt 1 vs prompt {index + 1}:",
        f"{difference:.10f}"
    )


# ==================================================
# Vocabulary effects
# ==================================================

print()
print("===== SELECTED TOKEN OFFSETS =====")

for token in [
    "<eos>",
    "data",
    "linux",
    "text",
    "model",
    "using",
]:

    token_id = token_to_id[token]

    print(
        f"{token:12s} "
        f"{theoretical_delta[token_id].item():+8.4f}"
    )


# ==================================================
# Important pairwise offsets
# ==================================================

print()
print("===== PAIRWISE CONSTANT OFFSETS =====")

linux_data = (
    theoretical_delta[
        token_to_id["linux"]
    ]
    -
    theoretical_delta[
        token_to_id["data"]
    ]
)

text_eos = (
    theoretical_delta[
        token_to_id["text"]
    ]
    -
    theoretical_delta[
        token_to_id["<eos>"]
    ]
)

print(
    "linux - data :",
    f"{linux_data.item():+.4f}"
)

print(
    "text - <eos>:",
    f"{text_eos.item():+.4f}"
)


print()
print("EXPECTED:")
print("linux - data  ~= -1.1111")
print("text - <eos> ~= -1.8335")
