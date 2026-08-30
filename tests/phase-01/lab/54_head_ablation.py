import math
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
# Attention forward with optional head ablation
# ==================================================

def attention_with_ablation(
    attention,
    x,
    attention_mask,
    disabled_head=None
):

    batch_size, sequence_length, _ = x.shape

    Q = attention.q_proj(x)
    K = attention.k_proj(x)
    V = attention.v_proj(x)

    Q = Q.view(
        batch_size,
        sequence_length,
        attention.num_heads,
        attention.head_dim
    ).transpose(1, 2)

    K = K.view(
        batch_size,
        sequence_length,
        attention.num_heads,
        attention.head_dim
    ).transpose(1, 2)

    V = V.view(
        batch_size,
        sequence_length,
        attention.num_heads,
        attention.head_dim
    ).transpose(1, 2)

    scores = (
        Q @ K.transpose(-2, -1)
    ) / math.sqrt(attention.head_dim)

    causal_mask = torch.triu(
        torch.ones(
            sequence_length,
            sequence_length,
            dtype=torch.bool,
            device=x.device
        ),
        diagonal=1
    )

    scores = scores.masked_fill(
        causal_mask,
        float("-inf")
    )

    key_mask = attention_mask[
        :, None, None, :
    ].bool()

    scores = scores.masked_fill(
        ~key_mask,
        float("-inf")
    )

    weights = torch.softmax(
        scores,
        dim=-1
    )

    context = weights @ V

    # ----------------------------------------------
    # HEAD ABLATION
    # ----------------------------------------------

    if disabled_head is not None:

        context[
            :,
            disabled_head,
            :,
            :
        ] = 0.0

    context = (
        context
        .transpose(1, 2)
        .contiguous()
        .view(
            batch_size,
            sequence_length,
            attention.embedding_dim
        )
    )

    return attention.out_proj(context)


# ==================================================
# Manual forward
# ==================================================

def forward_with_ablation(
    input_ids,
    attention_mask,
    disabled_block=None,
    disabled_head=None
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

        normalized = block.norm1(x)

        head_to_disable = None

        if block_index == disabled_block:
            head_to_disable = disabled_head

        attention_output = attention_with_ablation(
            block.attention,
            normalized,
            attention_mask,
            head_to_disable
        )

        x = x + attention_output

        x = x + block.mlp(
            block.norm2(x)
        )

    x = model.final_norm(x)

    return model.lm_head(x)


# ==================================================
# Prediction
# ==================================================

def predict(
    prompt,
    disabled_block=None,
    disabled_head=None
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

        logits = forward_with_ablation(
            input_ids,
            attention_mask,
            disabled_block,
            disabled_head
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


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== ATTENTION HEAD ABLATION =====")
print("Checkpoint: mini-kuzai-final.pt")
print("MODEL MODIFIED ON DISK: NO")


for prompt in prompts:

    print()
    print("========================================")
    print("PROMPT:", prompt)

    experiments = [
        ("BASELINE", None, None),
        ("BLOCK 1 / HEAD 0 OFF", 0, 0),
        ("BLOCK 1 / HEAD 1 OFF", 0, 1),
        ("BLOCK 2 / HEAD 0 OFF", 1, 0),
        ("BLOCK 2 / HEAD 1 OFF", 1, 1),
    ]

    for name, block, head in experiments:

        results = predict(
            prompt,
            block,
            head
        )

        print()
        print(name)

        for token, probability in results:

            print(
                f"{token:12s} "
                f"{probability * 100:6.2f} %"
            )
