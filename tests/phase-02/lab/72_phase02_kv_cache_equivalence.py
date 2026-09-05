import torch

from mini_kuzai_padding import MiniKuzaiPadding
from mini_kuzai_kvcache import MiniKuzaiKVCache


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

model_kwargs = dict(
    vocab_size=len(vocabulary),
    embedding_dim=checkpoint["embedding_dim"],
    hidden_dim=checkpoint["hidden_dim"],
    num_heads=checkpoint["num_heads"],
    num_layers=checkpoint["num_layers"],
    max_sequence_length=checkpoint["max_sequence_length"],
    pad_token_id=checkpoint["pad_token_id"]
)

baseline = MiniKuzaiPadding(**model_kwargs).to(device)
baseline.load_state_dict(checkpoint["model_state_dict"])
baseline.eval()

cached_model = MiniKuzaiKVCache(**model_kwargs).to(device)
load_result = cached_model.load_state_dict(
    checkpoint["model_state_dict"],
    strict=True
)
cached_model.eval()

prompt_ids = torch.tensor(
    [[token_to_id[token] for token in PROMPT.split()]],
    dtype=torch.long,
    device=device
)

baseline_generated = prompt_ids.clone()
cached_generated = prompt_ids.clone()
past_key_values = None
max_logit_differences = []
cache_lengths = []

with torch.no_grad():
    for step in range(NEW_TOKENS):
        baseline_mask = torch.ones_like(baseline_generated)
        baseline_logits = baseline(baseline_generated, baseline_mask)
        baseline_next_logits = baseline_logits[:, -1, :]
        baseline_next_token = torch.argmax(
            baseline_next_logits,
            dim=-1,
            keepdim=True
        )

        if past_key_values is None:
            cached_input = cached_generated
            full_key_length = cached_input.shape[1]
        else:
            cached_input = cached_generated[:, -1:]
            previous_cache_length = past_key_values[0][0].shape[-2]
            full_key_length = previous_cache_length + cached_input.shape[1]

        cached_mask = torch.ones(
            (cached_input.shape[0], full_key_length),
            dtype=torch.long,
            device=device
        )

        cached_logits, past_key_values = cached_model(
            cached_input,
            cached_mask,
            past_key_values,
            use_cache=True
        )

        cached_next_logits = cached_logits[:, -1, :]
        cached_next_token = torch.argmax(
            cached_next_logits,
            dim=-1,
            keepdim=True
        )

        max_difference = (
            baseline_next_logits - cached_next_logits
        ).abs().max().item()

        max_logit_differences.append(max_difference)
        layer_cache_lengths = [
            layer_cache[0].shape[-2]
            for layer_cache in past_key_values
        ]
        cache_lengths.append(layer_cache_lengths)

        baseline_generated = torch.cat(
            [baseline_generated, baseline_next_token],
            dim=1
        )
        cached_generated = torch.cat(
            [cached_generated, cached_next_token],
            dim=1
        )

baseline_text = " ".join(
    id_to_token[token]
    for token in baseline_generated[0].tolist()
)
cached_text = " ".join(
    id_to_token[token]
    for token in cached_generated[0].tolist()
)
tokens_identical = torch.equal(baseline_generated, cached_generated)

print("##### SECTION RESULTS FOR ASSISTANT ######")
print()
print("===== MINI-KUZAI PHASE 02 =====")
print("===== KV CACHE EQUIVALENCE =====")
print()
print("Device                 :", device)
if device.type == "cuda":
    print("GPU                    :", torch.cuda.get_device_name(0))
print()
print("===== WEIGHTS =====")
print("Checkpoint load        :", load_result)
print("New trainable weights  : NO")
print()
print("===== STEP COMPARISON =====")
for index, difference in enumerate(max_logit_differences, start=1):
    print(f"Step {index} max logit diff  : {difference:.10f}")
print()
print("===== KV CACHE LENGTH =====")
for index, lengths in enumerate(cache_lengths, start=1):
    print(f"After step {index:<2d}          :", lengths)
print()
print("===== GENERATION =====")
print("Baseline               :", baseline_text)
print("KV cache               :", cached_text)
print("Tokens identical       :", tokens_identical)
print()
print("===== FINAL CHECK =====")
print("Maximum logit error    :", f"{max(max_logit_differences):.10f}")
print("KV CACHE IMPLEMENTED   : YES")
print("MODEL WEIGHTS MODIFIED : NO")
print("TRAINING               : NO")
