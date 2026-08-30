import torch

from mini_kuzai import MiniKuzai


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

checkpoint = torch.load(
    "mini-kuzai-eos.pt",
    map_location=device,
    weights_only=False
)

vocabulary = checkpoint["vocabulary"]
token_to_id = checkpoint["token_to_id"]
id_to_token = checkpoint["id_to_token"]

model = MiniKuzai(
    vocab_size=len(vocabulary),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    max_sequence_length=checkpoint["max_sequence_length"]
).to(device)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


def inspect(prompt, top_k=10):

    words = prompt.split()

    ids = torch.tensor(
        [token_to_id[word] for word in words],
        dtype=torch.long,
        device=device
    )

    with torch.no_grad():

        logits = model(ids)

        probabilities = torch.softmax(
            logits[-1],
            dim=-1
        )

    top_probabilities, top_ids = torch.topk(
        probabilities,
        k=top_k
    )

    print("\nPrompt:")
    print(prompt)

    print("\nPossible next tokens:")

    for probability, token_id in zip(
        top_probabilities,
        top_ids
    ):

        token = id_to_token[token_id.item()]

        print(
            f"{token:14s} "
            f"{probability.item() * 100:6.2f} %"
        )

    print(
        "\nTop-10 probability total:",
        f"{top_probabilities.sum().item() * 100:.2f} %"
    )


print("===== MINI-KUZAI PREDICTION INSPECTION =====")

inspect("mini kuzai")

inspect("mini kuzai learns from")

inspect("mini kuzai learns from data")
