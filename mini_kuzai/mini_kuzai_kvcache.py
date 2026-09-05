import math

import torch
import torch.nn as nn


class MultiHeadAttention(nn.Module):

    def __init__(self, embedding_dim, num_heads):
        super().__init__()

        assert embedding_dim % num_heads == 0

        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.head_dim = embedding_dim // num_heads

        self.q_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.k_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.v_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.out_proj = nn.Linear(embedding_dim, embedding_dim, bias=False)

    def forward(
        self,
        x,
        attention_mask=None,
        past_key_value=None,
        use_cache=False
    ):
        batch_size, sequence_length, _ = x.shape

        Q = self.q_proj(x)
        K_new = self.k_proj(x)
        V_new = self.v_proj(x)

        Q = Q.view(batch_size, sequence_length, self.num_heads, self.head_dim).transpose(1, 2)
        K_new = K_new.view(batch_size, sequence_length, self.num_heads, self.head_dim).transpose(1, 2)
        V_new = V_new.view(batch_size, sequence_length, self.num_heads, self.head_dim).transpose(1, 2)

        if past_key_value is None:
            past_length = 0
            K = K_new
            V = V_new
        else:
            K_past, V_past = past_key_value
            past_length = K_past.shape[-2]
            K = torch.cat([K_past, K_new], dim=-2)
            V = torch.cat([V_past, V_new], dim=-2)

        key_length = K.shape[-2]

        scores = (Q @ K.transpose(-2, -1)) / math.sqrt(self.head_dim)

        query_positions = past_length + torch.arange(sequence_length, device=x.device)
        key_positions = torch.arange(key_length, device=x.device)

        causal_mask = key_positions[None, :] > query_positions[:, None]
        causal_mask = causal_mask[None, None, :, :]

        scores = scores.masked_fill(causal_mask, float("-inf"))

        if attention_mask is not None:
            if attention_mask.shape[1] != key_length:
                raise ValueError(
                    "attention_mask length "
                    f"{attention_mask.shape[1]} "
                    "does not match cached key "
                    f"length {key_length}"
                )

            key_mask = attention_mask[:, None, None, :].bool()
            scores = scores.masked_fill(~key_mask, float("-inf"))

        weights = torch.softmax(scores, dim=-1)
        context = weights @ V

        context = (
            context.transpose(1, 2)
            .contiguous()
            .view(batch_size, sequence_length, self.embedding_dim)
        )

        output = self.out_proj(context)

        present_key_value = None
        if use_cache:
            present_key_value = (K, V)

        return output, present_key_value


class MLP(nn.Module):

    def __init__(self, embedding_dim, hidden_dim):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, embedding_dim)
        )

    def forward(self, x):
        return self.network(x)


class TransformerBlock(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, num_heads):
        super().__init__()

        self.norm1 = nn.LayerNorm(embedding_dim)
        self.attention = MultiHeadAttention(embedding_dim, num_heads)
        self.norm2 = nn.LayerNorm(embedding_dim)
        self.mlp = MLP(embedding_dim, hidden_dim)

    def forward(
        self,
        x,
        attention_mask=None,
        past_key_value=None,
        use_cache=False
    ):
        attention_output, present = self.attention(
            self.norm1(x),
            attention_mask,
            past_key_value,
            use_cache
        )

        x = x + attention_output
        x = x + self.mlp(self.norm2(x))

        return x, present


class MiniKuzaiKVCache(nn.Module):

    def __init__(
        self,
        vocab_size,
        embedding_dim=8,
        hidden_dim=32,
        num_heads=2,
        num_layers=2,
        max_sequence_length=32,
        pad_token_id=0
    ):
        super().__init__()

        self.pad_token_id = pad_token_id

        self.token_embedding = nn.Embedding(
            vocab_size,
            embedding_dim,
            padding_idx=pad_token_id
        )

        self.position_embedding = nn.Embedding(
            max_sequence_length,
            embedding_dim
        )

        self.blocks = nn.ModuleList([
            TransformerBlock(embedding_dim, hidden_dim, num_heads)
            for _ in range(num_layers)
        ])

        self.final_norm = nn.LayerNorm(embedding_dim)
        self.lm_head = nn.Linear(embedding_dim, vocab_size, bias=False)

    def forward(
        self,
        token_ids,
        attention_mask=None,
        past_key_values=None,
        use_cache=False
    ):
        batch_size, sequence_length = token_ids.shape

        if past_key_values is None:
            past_key_values = [None for _ in self.blocks]
            past_length = 0
        else:
            if len(past_key_values) != len(self.blocks):
                raise ValueError("Incorrect number of layer KV caches")

            first_cache = past_key_values[0]
            if first_cache is None:
                past_length = 0
            else:
                past_length = first_cache[0].shape[-2]

        positions = torch.arange(
            past_length,
            past_length + sequence_length,
            device=token_ids.device
        )

        if positions[-1].item() >= self.position_embedding.num_embeddings:
            raise ValueError("Sequence exceeds max_sequence_length")

        x = self.token_embedding(token_ids) + self.position_embedding(positions)

        new_key_values = []

        for block, layer_cache in zip(self.blocks, past_key_values):
            x, present = block(
                x,
                attention_mask,
                layer_cache,
                use_cache
            )

            if use_cache:
                new_key_values.append(present)

        x = self.final_norm(x)
        logits = self.lm_head(x)

        if use_cache:
            return logits, new_key_values

        return logits
