# Final Review Saved Decision Review V1 Design

## Current State

`_render_saved_final_review_decisions` currently displays saved rows, a selectbox, status panel, badges, component table, dossier export, optional packet, and raw JSON. This is useful but still reads like an implementation inspector.

## Implementation Direction

- Add `build_saved_final_review_decision_review(rows)` in the Streamlit-free evidence read model.
- Keep raw Final Decision V2 row as source of truth.
- Sort review rows newest first using `updated_at` / `created_at` string order.
- Derive:
  - total records
  - selected count
  - hold count
  - reject count
  - re-review count
  - dashboard eligible selected count
  - latest decision id / label / updated timestamp
- UI:
  - status cards
  - latest decision notice
  - route family filter
  - review ledger table
  - selected detail tabs: Summary, Dossier, Evidence Packet, Raw JSON

## Non-Goals

- No persistence schema change.
- No new JSONL registry.
- No automatic report file write.
- No validation rerun.
- No broker approval, order, account sync, or auto rebalance.
