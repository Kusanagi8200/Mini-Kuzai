import torch

from mini_kuzai import MiniKuzai


checkpoint = torch.load(
    "mini-kuzai-eos.pt",
    map_location="cpu",
    weights_only=False
)

model = MiniKuzai(
    vocab_size=len(checkpoint["vocabulary"]),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    max_sequence_length=checkpoint["max_sequence_length"]
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)


print("===== MINI-KUZAI PARAMETERS =====")

total = 0

for name, parameter in model.named_parameters():

    count = parameter.numel()
    total += count

    print(
        f"{name:45s} "
        f"{str(list(parameter.shape)):15s} "
        f"{count:5d}"
    )


print("\n===== TOTAL =====")
print(total)


print("\n===== EXAMPLE WEIGHTS =====")

print("\nToken embedding for 'mini':")

mini_id = checkpoint["token_to_id"]["mini"]

print(
    model.token_embedding
    .weight[mini_id]
    .detach()
)

print("\nQ projection first row:")

print(
    model.transformer
    .attention
    .q_proj
    .weight[0]
    .detach()
)

print("\nLM head row for token 'learns':")

learns_id = checkpoint["token_to_id"]["learns"]

print(
    model.lm_head
    .weight[learns_id]
    .detach()
)
