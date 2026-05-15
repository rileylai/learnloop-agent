# 12 GitHub Collaboration Rules

## Purpose
This document defines safe and consistent GitHub workflow rules for this repository.

## Status
Draft

This document will be expanded in later steps.

What belongs here:
- Branch naming rules.
- Commit message rules.
- Push and PR safety checks.

## Branch Naming
- Use lowercase branch names.
- Use clear prefixes by intent.
- Recommended patterns:
- `docs/<short-topic>`
- `feat/<short-topic>`
- `fix/<short-topic>`
- `chore/<short-topic>`

Examples:
- `docs/harness-foundation-v1`
- `feat/notion-incremental-sync`
- `fix/reindex-stale-chunks`

## Commit Message Convention
- Format: `<type>: <short summary>`
- Keep summaries short and specific.
- Use English.

Allowed commit types:
- `feat`
- `fix`
- `docs`
- `chore`
- `refactor`
- `test`
- `ci`
- `build`
- `perf`

Examples:
- `docs: define notion ownership and sync model`
- `chore: initialize repository scaffold`

## Push Safety Rules
- Always run `git status` before commit.
- Review staged files with `git diff --staged`.
- Never commit secrets, API keys, or private Notion content.
- Do not use destructive commands like `git reset --hard` on shared work.
- Prefer `git push -u origin <branch>` for first push of a branch.

## PR Guidance
- Keep each PR focused on one change set.
- Link design decisions and updated docs in PR description.
- Include verification notes for safety rules and acceptance checks.
