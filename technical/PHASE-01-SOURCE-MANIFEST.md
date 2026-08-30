# MINI-KUZAI PHASE 01 source manifest

Source snapshot imported from the local Mini-Kuzai laboratory.

## Numbered experiments

```text
01_tokenizer.py
02_embeddings.py
03_positions.py
04_qkv.py
05_attention_scores.py
06_causal_attention.py
07_context_vectors.py
08_residual.py
09_mlp.py
10_transformer_block.py
11_mini_kuzai_model.py
12_one_training_step.py
13_train.py
14_generate.py
15_train_eos.py
16_generate_eos.py
17_inspect_predictions.py
18_sampling.py
19_temperature.py
20_parameters.py
21_multihead_shapes.py
22_multihead_attention.py
23_multihead_merge.py
24_test_mha_model.py
25_train_mha.py
26_compare_models.py
27_inspect_trained_heads.py
28_test_deep_model.py
29_train_deep.py
30_compare_depth.py
31_train_validation.py
32_clean_validation.py
33_true_validation.py
34_early_stopping.py
35_reproducibility.py
36_test_generalization.py
37_prefix_analysis.py
38_compositional_generalization.py
39_more_data.py
40_train_val_test.py
41_test_batch.py
42_test_padding.py
43_build_batch.py
44_dataloader.py
45_train_batches.py
46_test_batched_model.py
47_batch_lr_search.py
48_batch_lr_search_high.py
49_batch_lr_search_fine.py
50_train_final_batched.py
51_final_independent_test.py
52_blind_test.py
53_inspect_final_attention.py
54_head_ablation.py
55_component_ablation.py
56_residual_trace.py
57_logit_margin_trace.py
58_residual_geometry.py
59_layernorm_margin_decomposition.py
60_layernorm_internal_decomposition.py
61_beta_vocabulary_bias.py
62_beta_frequency_analysis.py
63_beta_frequency_regression.py
64_final_norm_ablation.py
65_confirm_beta_ablation.py
66_true_beta_confirmation.py
67_beta_additive_identity.py
```

Total numbered experiment scripts: **67**.

## Historical model modules

```text
mini_kuzai.py
mini_kuzai_mha.py
mini_kuzai_deep.py
mini_kuzai_batch.py
mini_kuzai_padding.py
```

## Corpus and original project note

```text
corpus.txt
README_ORIGINAL.txt
```

The complete historical snapshot is stored under `tests/phase-01/lab/`. Clean reusable model implementations are stored under `mini_kuzai/`.

Checkpoint binaries are documented separately in `technical/checkpoints/README.md` and excluded from Git.
