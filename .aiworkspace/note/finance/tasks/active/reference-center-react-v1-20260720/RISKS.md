# Reference Center React V1 Risks

## Open Risks

- Curated content can still drift unless current surface and forbidden legacy term contracts are enforced in tests.
- Streamlit cross-page deep-link behavior may require stable page-target/session handoff instead of arbitrary URL navigation.
- Removing both old pages before contextual links migrate could leave broken Reference entry points.
- A client-local search index should remain small enough that initial payload and render cost stay negligible.
- Current product copy uses mixed Korean/English terms; alias coverage must preserve findability without exposing internal vocabulary.
- The first implementation pass may reveal owner-page placement differences for contextual help; placement must stay after each surface purpose/title and must not alter workflow behavior.

## Mitigations

- Land catalog and referential-integrity tests before UI migration.
- Keep one migration window where old implementation remains importable but is no longer primary navigation.
- Validate destination allowlist and every contextual help item ID.
- Run actual desktop/900/420 Browser QA before deleting the old renderer.
- Keep each roadmap checkpoint independently verifiable so legacy removal cannot mask a failed migration.
