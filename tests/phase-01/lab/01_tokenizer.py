# Mini-Kuzai - Step 01
# Simple word-level tokenizer

with open("corpus.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split the corpus into words
tokens = text.split()

# Build the vocabulary
vocabulary = sorted(set(tokens))

# Create mappings
token_to_id = {token: i for i, token in enumerate(vocabulary)}
id_to_token = {i: token for token, i in token_to_id.items()}

print("===== MINI-KUZAI TOKENIZER =====")
print("Total tokens in corpus :", len(tokens))
print("Vocabulary size        :", len(vocabulary))

print("\n===== VOCABULARY =====")
for token, token_id in token_to_id.items():
    print(f"{token_id:3d} -> {token}")

# Test encoding
sentence = "mini kuzai runs on linux"
encoded = [token_to_id[word] for word in sentence.split()]

print("\n===== ENCODING TEST =====")
print("Text :", sentence)
print("IDs  :", encoded)

# Test decoding
decoded = " ".join(id_to_token[token_id] for token_id in encoded)

print("\n===== DECODING TEST =====")
print("IDs  :", encoded)
print("Text :", decoded)
