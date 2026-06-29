# Overview Market Context Macro Matrix V16 Plan

Status: Active
Date: 2026-06-21

## Why

V15 clarified the meaning of Macro sample counts, but the visible UI still reads as a prototype-like table with wide gaps, repeated labels, and long provider/detail text in the primary path. The user compared it with the cleaner `참고: 과거 유사 맥락` section and asked to improve the Macro section using the same visual language.

## Scope

- `app/web/overview_ui_components.py`
- `tests/test_service_contracts.py`
- task / durable docs after implementation

## Goals

1. Replace the visible Macro sample flow cards with a basis-bar style summary aligned with historical analog.
2. Replace the visible Macro result row table with a compact matrix: asset rows and `기본 / 조건 후 / 변화` columns.
3. Move verbose condition details out of the primary flow or compress them so they do not dominate the result section.
4. Keep current Macro backdrop as reference-only, but align its visual density with the rest of the section.

## Boundaries

- No calculation changes.
- No new Macro hard condition.
- No provider fetch, DB schema, loader, persistence, validation, monitoring, recommendation, or trade signal behavior.
