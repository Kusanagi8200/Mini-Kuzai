# Mini-Kuzai V53 repaired derivative candidates

Status: **public-source research derivatives only - NOT TRAIN.**

This directory contains newly authored repair candidates derived from already published public SmolTalk review cases. Original V51/V52 case pages remain immutable.

## Safety and lineage rules

Every derivative:

- has a new derivative identifier;
- retains the original public SmolTalk content SHA-256 and review-case path;
- labels source-normalized user text separately from newly authored assistant rewrites;
- records its repair type and rationale;
- sets `training_approved`, `dataset_split_assigned`, and `semantic_validation_complete` to `false`;
- requires an independent derivative review before any dataset admission.

`SOURCE_TEXT_NORMALIZED` means the public-source wording is preserved while Markdown/HTML presentation entities from the review page are decoded into plain text. It does not claim byte identity with the Markdown file.

## Current candidates

| Derivative | Source case | Repair |
| --- | --- | --- |
| [V53-DERIV-001-V52-025](V53-DERIV-001-V52-025.json) | [V52-025](../../smoltalk-v52/cases/025-4bd411ceb95b9b3c.md) | numeric correction + uncertainty calibration |
| [V53-DERIV-002-V51-013](V53-DERIV-002-V51-013.json) | [V51-013](../../smoltalk-v51/cases/013-566e0b8c4ed792cc.md) | wording + occupancy-constraint cleanup |

Derivative records created: **2**.
TRAIN approved: **0**.
