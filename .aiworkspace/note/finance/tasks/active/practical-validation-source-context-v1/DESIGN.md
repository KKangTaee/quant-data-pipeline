# Design

## Direction

Use the existing Clean V2 source chain and add optional, append-compatible fields.

- `selection_history`: compact rows derived from source result payload when available
- component `selection_history`: compact rows per strategy component
- Practical Validation Step 1 renders:
  - strategy / construction brief
  - component strategy and target weight table
  - performance result table
  - selection / holdings history table when present

## Data Boundary

The new rows are compact UI evidence, not full raw holdings or provider responses.
Existing source rows without these fields remain valid.

## Display Rules

- Single strategy: show it as one component with 100% target weight.
- Weighted mix: show portfolio construction plus each component's strategy, role, and target weight.
- Selection history table is evidence from the original source snapshot; latest runtime replay remains separate Step 3 evidence.
