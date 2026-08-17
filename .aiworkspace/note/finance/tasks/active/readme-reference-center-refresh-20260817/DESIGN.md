# Design

## Current Source

- README is the public first-entry product map and should not track transient task state or worktree-specific QA ports.
- Reference Center source of truth is `app/services/reference_center.py`; React renders the catalog payload and Python validates navigation intents.
- Current Market Research route remains `/overview` with internal `overview` destination key, but visible product language is `Market Research`.

## Implementation Direction

- Keep README aligned with Product Direction: 7 top-level surfaces, no live trading / broker / auto rebalance promise, Data Operations as evidence foundation.
- Make README explicitly name Market Research 3-family / 8-view structure.
- Keep Reference Center destination keys stable while adding missing current Market Research views as searchable catalog items.
- Strengthen tests by adding new Reference item ids to the required catalog set.
