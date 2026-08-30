import torch


PAD = "<pad>"
EOS = "<eos>"

sentences = [
    "mini kuzai runs on linux",
    "a model uses data",
    "linux is a system",
]

words = set()
for sentence in sentences:
    words.update(sentence.split())

vocabulary = [PAD, EOS] + sorted(words)
token_to_id = {token: i for i, token in enumerate(vocabulary)}
id_to_token = {i: token for token, i in token_to_id.items()}

PAD_ID = token_to_id[PAD]

encoded = []
for sentence in sentences:
    tokens = sentence.split() + [EOS]
    encoded.append(torch.tensor([token_to_id[t] for t in tokens]))

max_length = max(len(ids) - 1 for ids in encoded)
batch_size = len(encoded)

input_ids = torch.full((batch_size, max_length), PAD_ID, dtype=torch.long)
targets = torch.full((batch_size, max_length), PAD_ID, dtype=torch.long)
attention_mask = torch.zeros((batch_size, max_length), dtype=torch.long)

for row, ids in enumerate(encoded):
    inputs = ids[:-1]
    outputs = ids[1:]
    length = len(inputs)

    input_ids[row, :length] = inputs
    targets[row, :length] = outputs
    attention_mask[row, :length] = 1

print("Vocabulary:", vocabulary)
print("Input IDs:")
print(input_ids)
print("Targets:")
print(targets)
print("Attention mask:")
print(attention_mask)
