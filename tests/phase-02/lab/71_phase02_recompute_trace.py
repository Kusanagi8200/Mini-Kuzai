import torch

from mini_kuzai_padding import MiniKuzaiPadding


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PROMPT = "mini kuzai"
NEW_TOKENS = 4

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

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

input_ids = torch.tensor(
    [[token_to_id[token] for token in PROMPT.split()]],
    dtype=torch.long,
    device=device
)

generated = input_ids.clone()
block_traces = {index: [] for index in range(len(model.blocks))}
hooks = []

for block_index, block in enumerate(model.blocks):
    def make_hook(index):
        def hook(module, inputs, output):
            x = inputs[0]
            block_traces[index].append(int(x.shape[1]))
        return hook

    hooks.append(block.register_forward_hook(make_hook(block_index)))

step_input_lengths = []
generated_tokens = []

with torch.no_grad():
    for step in range(NEW_TOKENS):
        current_length = generated.shape[1]
        step_input_lengths.append(current_length)

        attention_mask = torch.ones_like(generated)
        logits = model(generated, attention_mask)
        next_token = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
        generated_tokens.append(next_token.item())
        generated = torch.cat([generated, next_token], dim=1)

for hook in hooks:
    hook.remove()

num_layers = len(model.blocks)
prompt_length = input_ids.shape[1]
no_cache_positions_per_layer = sum(step_input_lengths)
no_cache_block_positions = no_cache_positions_per_layer * num_layers

num_heads = checkpoint["num_heads"]
no_cache_attention_cells_per_head = sum(length * length for length in step_input_lengths)
no_cache_attention_cells = no_cache_attention_cells_per_head * num_heads * num_layers

cached_token_lengths = [prompt_length]
for _ in range(NEW_TOKENS - 1):
    cached_token_lengths.append(1)

cache_positions_per_layer = sum(cached_token_lengths)
cache_block_positions = cache_positions_per_layer * num_layers

cache_attention_cells_per_head = prompt_length * prompt_length
for step in range(1, NEW_TOKENS):
    key_length = prompt_length + step
    cache_attention_cells_per_head += key_length

cache_attention_cells = cache_attention_cells_per_head * num_heads * num_layers

position_reduction = (
    1.0 - cache_block_positions / no_cache_block_positions
) * 100.0
attention_reduction = (
    1.0 - cache_attention_cells / no_cache_attention_cells
) * 100.0

decoded = " ".join(id_to_token[token_id] for token_id in generated[0].tolist())

print("##### SECTION RESULTS FOR ASSISTANT ######")
print()
print("===== MINI-KUZAI PHASE 02 =====")
print("===== AUTOREGRESSIVE RECOMPUTE TRACE =====")
print()
print("Prompt                 :", PROMPT)
print("Prompt tokens          :", prompt_length)
print("Generated tokens       :", NEW_TOKENS)
print("Transformer blocks     :", num_layers)
print("Attention heads        :", num_heads)
print()
print("===== REAL NO-CACHE FORWARDS =====")
for step, length in enumerate(step_input_lengths, start=1):
    print(f"Decode step {step:<2d}         : {length} input tokens")
print()
print("===== BLOCK HOOK TRACE =====")
for block_index in range(num_layers):
    print(f"Block {block_index + 1} lengths        :", block_traces[block_index])
print()
print("===== TOKEN-POSITION WORK =====")
print("No cache / layer       :", no_cache_positions_per_layer)
print("No cache / all blocks  :", no_cache_block_positions)
print("Ideal cache / layer    :", cache_positions_per_layer)
print("Ideal cache / blocks   :", cache_block_positions)
print("Position reduction     :", f"{position_reduction:.2f}%")
print()
print("===== ATTENTION SCORE CELLS =====")
print("No cache / head        :", no_cache_attention_cells_per_head)
print("No cache total         :", no_cache_attention_cells)
print("Ideal cache / head     :", cache_attention_cells_per_head)
print("Ideal cache total      :", cache_attention_cells)
print("Attention reduction    :", f"{attention_reduction:.2f}%")
print()
print("===== OUTPUT =====")
print("Generated sequence     :", decoded)
print()
print("KV CACHE               : NO")
print("MODEL MODIFIED         : NO")
print("TRAINING               : NO")
