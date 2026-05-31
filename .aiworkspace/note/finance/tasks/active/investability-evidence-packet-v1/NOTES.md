# NOTES - Investability Evidence Packet V1

Status: Active
Last Updated: 2026-05-28

## Product Interpretation

This task strengthens decision quality without adding more workflow persistence.

User constraints to preserve:

- Avoid meaningless repeated JSONL saves.
- Avoid user memo storage features unless they are necessary decision evidence.
- Prefer free APIs for future data needs; if unavailable, use web crawling into DB.
- UI must not directly fetch provider / web data.

## Design Notes

- Treat critical missing evidence as a gate for selection, not as a cosmetic warning.
- Keep waiver out of V1 unless user explicitly approves detailed waiver workflow.
- Preserve hold / reject / re-review as valid outcomes when evidence is incomplete.
- V1 does not create a new JSONL registry. The packet is a compact snapshot inside the existing final decision row.
- `SELECT_FOR_PRACTICAL_PORTFOLIO` display copy now reads as `실전 검토 통과 후보` to reduce live-approval ambiguity.
