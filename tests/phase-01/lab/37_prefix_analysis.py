from collections import Counter


train_lines = [
    "mini kuzai runs on linux",
    "mini kuzai learns from data",
    "mini kuzai can generate text",
    "mini kuzai is a language model",
    "a language model learns from data",
    "a language model can generate text",
    "linux runs a model",
    "data helps a model learn",
    "mini kuzai uses a model",
    "a model uses data",
    "a model uses linux",
    "text uses data",
]

EOS = "<eos>"

tests = [
    "a language model runs on",
    "mini kuzai can generate",
    "a model learns from",
]


def next_token_counts(prefix):

    prefix_words = prefix.split()
    counts = Counter()

    for line in train_lines:

        words = line.split() + [EOS]

        n = len(prefix_words)

        for i in range(len(words) - n):

            if words[i:i+n] == prefix_words:

                counts[
                    words[i+n]
                ] += 1

    return counts


print("##### SECTION RESULTS FOR ASSISTANT ######")

print()
print("===== TRAIN PREFIX ANALYSIS =====")

for prefix in tests:

    counts = next_token_counts(prefix)

    print()
    print("========================================")
    print("PREFIX:", prefix)

    if counts:

        print("Seen exactly in training: YES")

        for token, count in counts.items():
            print(
                f"Next token: {token:10s} "
                f"count={count}"
            )

    else:

        print("Seen exactly in training: NO")


print()
print("===== TRAIN SENTENCES =====")

for line in train_lines:
    print("-", line)
