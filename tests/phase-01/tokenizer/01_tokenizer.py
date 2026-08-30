corpus = """
hello i am mini kuzai
hello i am an artificial intelligence
mini kuzai runs on linux
mini kuzai learns from data
linux is a computer operating system
a model learns to predict words
a model uses tokens
tokens are represented by numbers
numbers are transformed into vectors
vectors pass through the transformer
the transformer uses the attention mechanism
attention connects related tokens
mini kuzai learns to predict the next token
mini kuzai can generate text
mini kuzai is a small language model
""".strip().splitlines()

words = []
for line in corpus:
    words.extend(line.split())

vocabulary = sorted(set(words))
token_to_id = {token: i for i, token in enumerate(vocabulary)}
id_to_token = {i: token for token, i in token_to_id.items()}

sentence = "mini kuzai runs on linux"
encoded = [token_to_id[token] for token in sentence.split()]
decoded = " ".join(id_to_token[i] for i in encoded)

print("Vocabulary size:", len(vocabulary))
print("Sentence       :", sentence)
print("IDs            :", encoded)
print("Decoded        :", decoded)
print("Round trip OK  :", decoded == sentence)
