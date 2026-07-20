# Reference Center React V1 Notes

## Decisions

- Reference value is retained; only the two-page Guides / Glossary split is removed.
- Search-first Hybrid A is the selected layout.
- User-facing content is curated; `GLOSSARY.md` is not auto-rendered.
- Legacy / developer terms are excluded from app search, not hidden behind an advanced filter.
- Reference stays read-only and does not become an operational diagnostic or log surface.
- Search/filter/detail state remains inside React; Python handles validated navigation intent only.

## Current Evidence

- Existing Reference has task cards, journeys, playbooks, shared concepts, and markdown glossary search.
- Existing tests validate shape but do not prevent product-name/content drift.
- Current product requires Institutional Portfolios, Futures Macro, Economic Cycle/current Overview, and Portfolio Monitoring naming.
- Existing Reference-specific UI has no React component and retains stale/legacy copy.
