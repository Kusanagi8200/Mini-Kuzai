import statistics
import time

import torch

from mini_kuzai_padding import MiniKuzaiPadding


WARMUP_RUNS = 10
MEASURED_RUNS = 50
FIXED_NEW_TOKENS = 4

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

prompt = "mini kuzai"
initial_ids = torch.tensor(
    [[token_to_id[token] for token in prompt.split()]],
    dtype=torch.long,
    device=device
)


def generate_fixed():
    generated = initial_ids.clone()

    with torch.no_grad():
        for _ in range(FIXED_NEW_TOKENS):
            attention_mask = torch.ones_like(generated)
            logits = model(generated, attention_mask)
            next_token = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
            generated = torch.cat([generated, next_token], dim=1)

    return generated


def timed_generation():
    if device.type == "cuda":
        torch.cuda.synchronize()

    start = time.perf_counter()
    generated = generate_fixed()

    if device.type == "cuda":
        torch.cuda.synchronize()

    elapsed = time.perf_counter() - start
    return generated, elapsed


if device.type == "cuda":
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

cold_generated, cold_time = timed_generation()

for _ in range(WARMUP_RUNS):
    generate_fixed()

if device.type == "cuda":
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()

times = []
last_generated = None

for _ in range(MEASURED_RUNS):
    generated, elapsed = timed_generation()
    last_generated = generated
    times.append(elapsed)

mean_time = statistics.mean(times)
median_time = statistics.median(times)
min_time = min(times)
max_time = max(times)
std_time = statistics.stdev(times) if len(times) > 1 else 0.0

mean_tokens_per_second = FIXED_NEW_TOKENS / mean_time
median_tokens_per_second = FIXED_NEW_TOKENS / median_time

peak_memory = (
    torch.cuda.max_memory_allocated() / 1024**2
    if device.type == "cuda"
    else 0.0
)
allocated_memory = (
    torch.cuda.memory_allocated() / 1024**2
    if device.type == "cuda"
    else 0.0
)
reserved_memory = (
    torch.cuda.memory_reserved() / 1024**2
    if device.type == "cuda"
    else 0.0
)

decoded = " ".join(id_to_token[token_id] for token_id in last_generated[0].tolist())

print("##### SECTION RESULTS FOR ASSISTANT ######")
print()
print("===== MINI-KUZAI PHASE 02 =====")
print("===== STABILIZED BASELINE =====")
print()
print("Device                 :", device)
if device.type == "cuda":
    print("GPU                    :", torch.cuda.get_device_name(0))
print()
print("===== BENCHMARK CONFIG =====")
print("Prompt tokens          :", initial_ids.shape[1])
print("Fixed new tokens       :", FIXED_NEW_TOKENS)
print("Warmup runs            :", WARMUP_RUNS)
print("Measured runs          :", MEASURED_RUNS)
print("KV cache               : NO")
print()
print("===== COLD RUN =====")
print("Cold generation time   :", f"{cold_time:.6f} s")
print("Cold tokens / second   :", f"{FIXED_NEW_TOKENS / cold_time:.2f}")
print()
print("===== WARM PERFORMANCE =====")
print("Minimum time           :", f"{min_time:.6f} s")
print("Mean time              :", f"{mean_time:.6f} s")
print("Median time            :", f"{median_time:.6f} s")
print("Maximum time           :", f"{max_time:.6f} s")
print("Std deviation          :", f"{std_time:.6f} s")
print("Mean tokens / second   :", f"{mean_tokens_per_second:.2f}")
print("Median tokens / second :", f"{median_tokens_per_second:.2f}")
print()
print("===== GPU MEMORY AFTER WARMUP =====")
print("Allocated              :", f"{allocated_memory:.3f} MB")
print("Reserved               :", f"{reserved_memory:.3f} MB")
print("Peak allocated         :", f"{peak_memory:.3f} MB")
print()
print("===== COMPUTE OUTPUT =====")
print("Generated sequence     :", decoded)
print()
print("NOTE:")
print("EOS stopping is disabled only for this compute benchmark.")
print()
print("MODEL MODIFIED         : NO")
print("TRAINING               : NO")
