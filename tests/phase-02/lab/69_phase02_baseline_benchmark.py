import time

import torch

from mini_kuzai_padding import MiniKuzaiPadding


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def gpu_memory_mb():
    if device.type != "cuda":
        return 0.0
    return torch.cuda.memory_allocated() / 1024**2


def gpu_reserved_mb():
    if device.type != "cuda":
        return 0.0
    return torch.cuda.memory_reserved() / 1024**2


if device.type == "cuda":
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

memory_before = gpu_memory_mb()
reserved_before = gpu_reserved_mb()

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

memory_after_model = gpu_memory_mb()
reserved_after_model = gpu_reserved_mb()

parameter_count = sum(p.numel() for p in model.parameters())
parameter_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
parameter_kb = parameter_bytes / 1024

prompt = "mini kuzai"
input_ids = torch.tensor(
    [[token_to_id[token] for token in prompt.split()]],
    dtype=torch.long,
    device=device
)

generated = input_ids.clone()
max_new_tokens = 10

if device.type == "cuda":
    torch.cuda.synchronize()

start = time.perf_counter()

with torch.no_grad():
    for _ in range(max_new_tokens):
        attention_mask = torch.ones_like(generated)
        logits = model(generated, attention_mask)
        next_token = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
        generated = torch.cat([generated, next_token], dim=1)

        if next_token.item() == checkpoint["eos_token_id"]:
            break

if device.type == "cuda":
    torch.cuda.synchronize()

end = time.perf_counter()
elapsed = end - start
new_token_count = generated.shape[1] - input_ids.shape[1]
tokens_per_second = new_token_count / elapsed if elapsed > 0 else 0.0

peak_memory = (
    torch.cuda.max_memory_allocated() / 1024**2
    if device.type == "cuda"
    else 0.0
)

decoded_tokens = [id_to_token[token_id] for token_id in generated[0].tolist()]
decoded_text = " ".join(decoded_tokens)

print("##### SECTION RESULTS FOR ASSISTANT ######")
print()
print("===== MINI-KUZAI PHASE 02 =====")
print("===== BASELINE BENCHMARK =====")
print()
print("Device                 :", device)
if device.type == "cuda":
    print("GPU                    :", torch.cuda.get_device_name(0))
print()
print("===== MODEL =====")
print("Transformer blocks     :", checkpoint["num_layers"])
print("Attention heads        :", checkpoint["num_heads"])
print("Embedding dimension    :", checkpoint["embedding_dim"])
print("Hidden dimension       :", checkpoint["hidden_dim"])
print("Vocabulary             :", len(vocabulary))
print("Parameters             :", parameter_count)
print("Parameter storage      :", f"{parameter_kb:.2f} KB")
print()
print("===== GPU MEMORY =====")
print("Allocated before model :", f"{memory_before:.3f} MB")
print("Allocated after model  :", f"{memory_after_model:.3f} MB")
print("Reserved after model   :", f"{reserved_after_model:.3f} MB")
print("Peak allocated         :", f"{peak_memory:.3f} MB")
print()
print("===== GENERATION =====")
print("Prompt                 :", prompt)
print("Generated              :", decoded_text)
print("New tokens             :", new_token_count)
print("Generation time        :", f"{elapsed:.6f} s")
print("Tokens / second        :", f"{tokens_per_second:.2f}")
print()
print("KV CACHE               : NO")
print("MODEL MODIFIED         : NO")
print("TRAINING               : NO")
