# MINI-KUZAI PHASE 01 checkpoints

The source archive contained nine PyTorch checkpoints. They are deliberately excluded from normal Git through the `*.pt` rule in `.gitignore`.

Use this inventory to verify locally retained checkpoint files.

| Checkpoint | Approx. size | SHA-256 |
| --- | ---: | --- |
| `mini-kuzai.pt` | 16 KiB | `6e439903d386c9c5a823c1560c35332721372bfe4eca94214f1ee2d0c3803a56` |
| `mini-kuzai-eos.pt` | 16 KiB | `34c61f11e5530c70b81ba72e7f7f38da45e8610ded877c6e62b24b05f4fff85b` |
| `mini-kuzai-mha.pt` | 20 KiB | `67f204bfbedb2b928fb6ce2afc434549fc5b544d9864876d4e425ea57716b5ee` |
| `mini-kuzai-deep.pt` | 28 KiB | `eccf0fc8bb5af11a14bc78d04deb0c6aba0d35dd365bfc4012726f6079bba7a9` |
| `mini-kuzai-validation-best.pt` | 24 KiB | `a210b27110337775a5180b17bed0b54eae56e71ff683337278cb52c13206cd2e` |
| `mini-kuzai-best.pt` | 24 KiB | `7370acb8a46c994a59d401fac00ed9f9a738a04881cad17c6de2e3d927f1bf25` |
| `mini-kuzai-tvt.pt` | 24 KiB | `c2cfe18d862b1293108f323638ced98294d04054dfcae3b4a8a1e7c7e99345b3` |
| `mini-kuzai-batched.pt` | 24 KiB | `a781692528ec15d6536b6add6d1d241e813b91c493bbcc12086edb7b28adca42` |
| `mini-kuzai-final.pt` | 24 KiB | `ceee8ed3358af068224f056067d4bcae53f561765ae13340ee9084323c1d9a28` |

Verify a file with:

```bash
sha256sum mini-kuzai-final.pt
```

Expected Phase 01 final checkpoint hash:

```text
ceee8ed3358af068224f056067d4bcae53f561765ae13340ee9084323c1d9a28
```
