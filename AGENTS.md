# AGENTS.md

## Purpose
- This file defines how Markdown documentation should be structured and updated in GlobalPlace.
- Keep documentation practical, short, and production-minded.

## Section structure
- Use clear section headers with `##`.
- Use ordered sections `A, B, C, D, E` when listing interpretation logic.
- Keep sections short and focused.

## Style rules
- Be concise and operator-focused.
- Avoid long explanations and theory.
- Prefer bullet points over paragraphs.
- Use consistent naming such as `alerts`, `matches`, and `notifications`.

## Editing rules
- Do not append content blindly to the end of files.
- Insert new sections in logically correct positions.
- Preserve existing structure and formatting.
- Do not rewrite existing sections unless explicitly instructed.

## Product boundaries
- notifications are sent ONLY on explicit alert match
- no recommendations or "you may also like"
- no category expansion
- no view-based triggers
- no daily digests

Core principle:
- silence is better than irrelevant message

## Matcher constraints
- matcher must remain strict and deterministic
- no fuzzy matching
- no semantic matching
- no embeddings or AI-based matching
- no substring-based broad matching

## Change rules
- do NOT modify matcher logic without explicit instruction
- do NOT introduce new notification types
- preserve high signal / low noise behavior

## QA and Ops docs
- Keep documents minimal and practical.
- Focus on:
  - what to run
  - what to expect
  - how to interpret results

## Consistency
- Follow the same tone and structure across:
  - `ALERT_SCAN_OPS.md`
  - `QA_BASELINE_CHECKLIST.md`
  - `BATCH_QA_NOTE.md`

## Limits
- Do not introduce heavy documentation systems.
- Do not add unnecessary abstraction.
- Do not expand documents beyond practical use.
