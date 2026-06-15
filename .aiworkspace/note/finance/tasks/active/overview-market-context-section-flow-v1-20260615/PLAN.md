# Overview Market Context Section Flow V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the approved Market Context hybrid UI into clearer reading sections so the top dashboard stays focused and the brief / interpretation / reference material reads as separate flow.

**Architecture:** Keep the existing DB-backed cockpit read model. Refactor `app/web/overview_ui_components.py` so `.ov-macro-cockpit` contains only headline, tape, sector pressure, and event timeline; render brief, cues, historical analog, source confidence, and boundary note as sibling full-width reading sections.

**Tech Stack:** Python, Streamlit markdown HTML/CSS, existing `unittest` service-contract tests, Browser QA.

---

## 이걸 하는 이유?

The hybrid view improved the visual surface, but too much content still lives inside one large cockpit. The user now needs clearer section boundaries and stronger brief readability without adding new providers, diagnostics panels, or trading semantics.

## Scope

- In scope:
  - Add tests that prove Market Context is split into top dashboard plus reading-flow sections.
  - Keep sector pressure map and event timeline in the top dashboard.
  - Move market brief, interpretation cues, historical analog, source confidence, and boundary note outside `.ov-macro-cockpit`.
  - Improve section title hierarchy and market brief typography.
  - Run focused unit checks, compile, diff check, and Browser QA.
- Out of scope:
  - New data fields, providers, DB schema, registry / saved JSONL writes.
  - New interactive drill-in behavior.
  - Changing the meaning of market context, historical analog, validation, monitoring, or trading boundaries.

## Steps

- [x] Add RED contract tests for split cockpit / reading flow HTML and CSS classes.
- [x] Refactor renderer helpers into top cockpit body and reading-flow sections.
- [x] Apply section band CSS and improve market brief typography.
- [x] Run focused tests and py_compile.
- [x] Browser QA desktop and mobile; save generated screenshot.
- [x] Sync task / roadmap / root logs and commit source/docs/tests only.
