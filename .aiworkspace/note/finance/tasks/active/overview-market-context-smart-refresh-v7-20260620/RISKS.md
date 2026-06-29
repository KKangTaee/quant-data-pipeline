# Risks

## Watch

- Smart refresh must not skip a genuinely stale source due to overly narrow mapping.
- Events estimate caveats should not appear as actionable refresh requirements unless collection status is missing, stale, failed, or partial.
- Full refresh fallback must remain available for broad repair.
- Raw job rows should stay available, but not become the primary user-facing result.
