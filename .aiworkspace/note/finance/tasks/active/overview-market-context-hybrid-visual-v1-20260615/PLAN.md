# Overview Market Context Hybrid Visual V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved A+C hybrid Market Context UI: tape summary plus sector pressure map and event timeline, using existing DB-backed read models only.

**Architecture:** `app/services/overview_market_intelligence.py` adds lightweight cockpit fields by reusing `build_overview_breadth_heatmap_summary()` and `build_overview_macro_week_lane()`. `app/web/overview_ui_components.py` renders the new fields as a cardless visual cockpit while keeping historical analog, source confidence, and context-only boundary copy.

**Tech Stack:** Python, Streamlit markdown HTML/CSS, existing service contract unittest coverage, Browser QA.

---

## Why

The user approved a hybrid of option 1 and option 3 from the benchmark screen: a dense finance-terminal tape for quick reading and a visual heatmap/timeline board for market pressure. The current row-only version is better than cards but still visually weaker than the desired direction.

## Scope

- In scope:
  - Add cockpit `sector_pressure` and `event_timeline` fields from existing snapshots.
  - Render tape, sector pressure map, event timeline, and evidence rows.
  - Keep source confidence / historical analog / boundary copy.
  - Add focused contract tests and Browser QA.
- Out of scope:
  - New provider, DB schema, registry/saved JSONL write.
  - Direct UI provider fetch.
  - Trading signal / validation gate / monitoring signal.
  - Full interactive drill-in or custom dashboard editor.

## Steps

- [x] Add RED service/UI contract tests for hybrid fields and classes.
- [x] Implement service model fields by reusing existing helper functions.
- [x] Implement CSS/HTML helpers for hybrid tape, sector pressure map, timeline, and evidence rows.
- [x] Run focused tests and py_compile.
- [x] Browser QA desktop/mobile viewport and save screenshot as generated artifact.
- [x] Sync docs/research/task records and commit only source/docs/tests.
