# Training Process

Mini-Kuzai Phase 01 uses next-token prediction with teacher forcing.

For a sentence such as:

```text
mini kuzai runs on linux <eos>
```

the model receives:

```text
mini kuzai runs on linux
```

and learns to predict:

```text
kuzai runs on linux <eos>
```

## Core training loop

1. Build token IDs from the training text.
2. Create input and target sequences shifted by one token.
3. Batch variable-length sequences.
4. Pad shorter sequences with `<pad>`.
5. Build an attention mask so padding keys are ignored.
6. Run the Transformer forward pass.
7. Compute cross-entropy loss with padding ignored.
8. Backpropagate gradients.
9. Update parameters with AdamW.
10. Evaluate on a separate validation set.
11. Keep the best validation checkpoint.
12. Stop when validation no longer improves for the configured patience window.

## Phase 01 final configuration

```text
Embedding dimension : 8
Attention heads     : 2
Transformer blocks  : 2
MLP hidden dimension: 32
Batch size          : 4
Learning rate       : 0.04
Seed                : 42
Patience            : 30
Parameters          : 2368
Vocabulary          : 26
```

The learning rate was selected using the validation set only. Independent diagnostic and blind-test cases were kept separate from optimizer updates and early stopping whenever possible.
