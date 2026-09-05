# GitHub Update Workflow

This file defines the repository synchronization rule for the Mini-Kuzai project.

## Implicit project task: `MAJ GITHUB`

GitHub synchronization is treated as an implicit maintenance task throughout Mini-Kuzai development.

A `MAJ GITHUB` should be performed whenever one of the following conditions is met:

- a sufficiently large development phase has been completed;
- a meaningful model, training, evaluation, or architecture milestone has been validated;
- several new experimental scripts have accumulated;
- project documentation has materially changed;
- a stable checkpoint or reproducible baseline has been established;
- the local source tree has diverged enough from the repository that delaying synchronization would make the project history harder to preserve;
- a development phase is explicitly closed or frozen.

## Procedure

When a synchronization point is reached, the working convention is:

1. Announce `MAJ GITHUB` in the project conversation.
2. Review the files produced since the previous synchronization point.
3. Keep generated, temporary, cache, virtual-environment, secret, and excluded binary files out of normal Git.
4. Preserve experimental history when it is technically useful.
5. Update the canonical source code and relevant technical documentation.
6. Update phase documentation and manifests when necessary.
7. Commit the changes directly to the Mini-Kuzai GitHub repository when GitHub access is available.
8. Verify that the repository branch contains the expected files after the update.

## Text style rule

Use the ASCII hyphen-minus character `-` for separators, ranges, headings, prose punctuation, and project documentation.

Do not use the Unicode em dash character in project files, generated documentation, commit-oriented text, or project conversations.

This rule applies to all current and future Mini-Kuzai phases unless explicitly changed later.

## Repository

```text
Kusanagi8200/Mini-Kuzai
```

## Principle

The user does not need to request repository synchronization after every individual development step. Synchronization should occur at meaningful project boundaries rather than after trivial changes.

The phrase `MAJ GITHUB` marks the synchronization operation when it is triggered.

This workflow applies to subsequent Mini-Kuzai phases unless it is explicitly changed later.
