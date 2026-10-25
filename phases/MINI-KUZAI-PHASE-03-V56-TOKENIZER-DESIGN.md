# MINI-KUZAI PHASE 03 - V56 TOKENIZER DESIGN

Status: TOKENIZER CANDIDATES IMPLEMENTED

## Purpose

V56 starts tokenizer design after successful global closure of the controlled
TRAIN / VALIDATION / BLIND corpus.

The purpose of this workstream is to compare tokenizer strategies and
vocabulary sizes before freezing any final vocabulary.

No model architecture or training authorization is implied by V56.

## Prerequisite

V55 GLOBAL BLIND CLOSURE
PHASE03-SMOLTALK-V55-BLIND-CLOSURE-001
STATUS: COMPLETE

## Tokenizer-learning boundary

Tokenizer vocabulary construction may use:

Canonical Phase 03 TRAIN corpus : 107 records / 29 groups
Public SmolTalk v0.4 reservoir  : 8000 records

The following material is excluded from tokenizer learning:

VALIDATION corpus               : EXCLUDED
BLIND TEST corpus               : EXCLUDED
Private conversation corpus     : EXCLUDED

VALIDATION and BLIND text remain evaluation-only material.

Private conversational material remains outside the public workflow and is not
part of the V56 tokenizer design corpus.

## Phase 01 baseline

Phase 01 used a deliberately simple word-level tokenizer.

That tokenizer was appropriate for the educational Phase 01 laboratory but is
not assumed to be suitable for Phase 03.

V56 will compare subword-capable strategies rather than extending the frozen
Phase 01 vocabulary mechanically.

## V56 sequence

V56.1 tokenizer source-boundary audit
-> V56.2 tokenizer candidate implementation
-> V56.3 candidate vocabulary-size benchmark
-> V56.4 sequence-length / coverage / parameter-cost comparison
-> V56.5 tokenizer selection
-> V56.6 vocabulary freeze

Vocabulary freeze is not authorized until the comparison stages are complete.

## Current authorization state

TOKENIZER FINALIZED       : NO
VOCABULARY FROZEN         : NO
ARCHITECTURE SELECTED     : NO
TRAINING MIX FINALIZED    : NO
TRAINING AUTHORIZED       : NO

## V56.2 implemented candidates

Three deterministic tokenizer families are now available for benchmarking.

1. byte_baseline

Pure UTF-8 byte tokenizer.

Base vocabulary:

259 tokens total

- 3 special tokens
- 256 byte tokens

This candidate provides the universal lossless baseline.

2. byte_bpe_whitespace

Deterministic byte-level BPE.

BPE merges are learned inside whitespace-delimited chunks.

It retains complete byte fallback and therefore cannot produce an unknown
character or unknown word.

3. byte_bpe_unicode

Deterministic byte-level BPE.

Pretokenization separates Unicode words, punctuation and whitespace before
learning byte-level merges.

It also retains complete byte fallback.

## V56.2 invariants

All three candidate families must remain:

- lossless for valid Python Unicode strings;
- deterministic for identical corpus and parameters;
- serializable;
- independent of external tokenizer libraries;
- capable of representing arbitrary UTF-8 text without an UNK token.

The BPE implementations are research candidates.

Their efficiency and vocabulary sizes have not yet been selected.

No benchmark result from V56.2 constitutes tokenizer selection.

## Next gate

V56.3 will train and measure candidate vocabulary configurations against the
authorized tokenizer-learning corpus.

The comparison must measure at least:

- resulting vocabulary size;
- token count;
- compression relative to byte baseline;
- average tokens per message;
- high-percentile sequence lengths;
- round-trip integrity;
- estimated embedding/output parameter cost.

VALIDATION, BLIND TEST and private conversation material remain excluded from
tokenizer learning.
