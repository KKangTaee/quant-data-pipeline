# Risks

- Final Review currently has a large `page.py` renderer, so UI refactor and semantic read-model changes can easily tangle unless split by section.
- Existing tests protect gate/checklist behavior, but not investment-review narrative quality.
- Non-select outcomes are now durable judgment records, but old saved rows do not have v3 handoff flags. Read models keep legacy compatibility, so future cleanup must not rewrite JSONL without explicit request.
- Final Review still lacks the analyst-style narrative / score layer that explains strengths, weaknesses, market fit, expected ranges, and benchmark rationale in one human-readable review.
- Weakness-improvement comparison can become a new strategy/proposal generator if not kept read-only and session-scoped in the first version.
