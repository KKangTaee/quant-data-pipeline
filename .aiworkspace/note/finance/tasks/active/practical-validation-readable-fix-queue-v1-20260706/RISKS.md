# Risks

- Do not hide raw status entirely; keep it as technical context so debugging remains possible.
- Do not change gate thresholds or persistence semantics while improving copy.

## Closeout

- Raw statuses remain visible as `기술 기준` tags, while first-read copy uses user-facing labels.
- Gate thresholds, replay execution, provider collection, registry / saved JSONL, Final Review persistence, live approval, order, and auto rebalance boundaries were not changed.
