# Storage Governance Audit V1 Status

Status: Complete
Last Updated: 2026-05-28

## Completed

- Audited JSONL and artifact write points across `app/runtime`, `app/jobs`, `app/services`, `app/web`, and repo helper scripts.
- Classified each storage surface as main workflow registry, explicit saved setup, optional monitoring log, legacy compatibility, local runtime artifact, or DB-only evidence.
- Added durable storage governance policy under `docs/data`.
- Updated registry / saved / run history docs to reflect the current source-of-truth boundary.
- Updated Investability Decision Foundation phase task board and roadmap.

## Decision

No runtime registry was rewritten and no new JSONL file was added.

The main investability flow remains:

```text
PORTFOLIO_SELECTION_SOURCES
  -> PRACTICAL_VALIDATION_RESULTS
    -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2
      -> Selected Portfolio Dashboard
```

## Next

Proceed to `data-provenance-coverage-v1` before adding look-through exposure board, monitoring timeline, or decision dossier work.
