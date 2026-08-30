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
# Manual forward with component ablation
# ==================================================

def forward_ablation(
    input_ids,
    attention_mask,
    disabled_block=None,
    disabled_component=None
):

    batch_size, sequence_length = input_ids.shape

    positions = torch.arange(
        sequence_length,
        device=device
    )

    x = (
        model.token_embedding(input_ids)
        + model.position_embedding(positions)
    )


    for block_index, block in enumerate(
        model.blocks
    ):

        # ------------------------------------------
        # ATTENTION
        # ------------------------------------------

        if (
            block_index == disabled_block
            and disabled_component == "attention"
        ):
            attention_output = torch.zeros_like(x)

        else:
            attention_output = block.attention(
                block.norm1(x),
                attention_mask
            )

        x = x + attention_output


        # ------------------------------------------
        # MLP
        # ------------------------------------------

        if (
            block_index == disabled_block
            and disabled_component == "mlp"
        ):
            mlp_output = torch.zeros_like(x)

        else:
            mlp_output = block.mlp(
                block.norm2(x)
            )

        x = x + mlp_output


    x = model.final_norm(x)

    return model.lm_head(x)


# ==================================================
# Prediction
# ==================================================

def predict(
    prompt,
    disabled_block=None,
    disabled_component=None
):

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

        logits = forward_ablation(
            input_ids,
            attention_mask,
            disabled_block,
            disabled_component
        )[0, -1]

        probabilities = torch.softmax(
            logits,
            dim=-1
        )

    top_probs, top_ids = torch.topk(
        probabilities,
        k=3
    )

    return [
        (
            id_to_token[token_id.item()],
            probability.item()
        )
        for probability, token_id
        in zip(top_probs, top_ids)
    ]


# ==================================================
# Experiments
# ==================================================

prompts = [
    "mini kuzai runs using",
    "a model can generate",
]


experiments = [
    ("BASELINE", None, None),

    ("BLOCK 1 ATTENTION OFF", 0, "attention"),
    ("BLOCK 1 MLP OFF",       0, "mlp"),

    ("BLOCK 2 ATTENTION OFF", 1, "attention"),
    ("BLOCK 2 MLP OFF",       1, "mlp"),
]


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== TRANSFORMER COMPONENT ABLATION =====")

print("Checkpoint: mini-kuzai-final.pt")
print("MODEL MODIFIED ON DISK: NO")


for prompt in prompts:

    print()
    print("========================================")
    print("PROMPT:", prompt)

    for name, block, component in experiments:

        results = predict(
            prompt,
            block,
            component
        )

        print()
        print(name)

        for token, probability in results:

            print(
                f"{token:12s} "
                f"{probability * 100:6.2f} %"
            )
