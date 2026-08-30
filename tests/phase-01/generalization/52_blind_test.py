import torch

from mini_kuzai import MiniKuzaiPadding


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

checkpoint = torch.load(
    "mini-kuzai-final.pt",
    map_location=device,
    weights_only=False,
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
    pad_token_id=PAD_ID,
).to(device)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

tests = [
    ("a language model runs using", "linux"),
    ("mini kuzai runs using", "linux"),
    ("a language model learns using", "data"),
    ("mini kuzai can learn using", "data"),
    ("a model can generate", "text"),
    ("linux is used by a", "model"),
]

correct = 0
top3 = 0

for prompt, expected in tests:
    input_ids = torch.tensor(
        [[token_to_id[word] for word in prompt.split()]],
        dtype=torch.long,
        device=device,
    )
    attention_mask = torch.ones_like(input_ids)

    with torch.no_grad():
        logits = model(input_ids, attention_mask)[0, -1]
        probabilities = torch.softmax(logits, dim=-1)

    sorted_probs, sorted_ids = torch.sort(probabilities, descending=True)
    predicted = id_to_token[sorted_ids[0].item()]
    expected_id = token_to_id[expected]
    rank = (
        (sorted_ids == expected_id)
        .nonzero(as_tuple=True)[0]
        .item()
        + 1
    )

    if predicted == expected:
        correct += 1
    if rank <= 3:
        top3 += 1

    print()
    print("PROMPT   :", prompt)
    print("EXPECTED :", expected)
    print("PREDICTED:", predicted)
    print("RANK     :", rank)
    print("EXPECTED PROBABILITY:", f"{probabilities[expected_id].item() * 100:.2f} %")

print()
print("Top-1:", f"{correct}/{len(tests)}")
print("Top-3:", f"{top3}/{len(tests)}")
