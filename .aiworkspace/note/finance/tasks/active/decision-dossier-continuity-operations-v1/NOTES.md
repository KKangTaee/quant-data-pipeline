# Decision Dossier Continuity Operations V1 Notes

Status: Complete
Created: 2026-05-29

## Notes

- This task did not add persistence. The new source contract is returned inside existing read model payloads.
- Continuity should not silently accept a manually supplied timeline if its source contract points to a different decision row.
- Decision Dossier can include a session timeline, but the markdown now labels whether that timeline contract is present and consistent.
- `_markdown_value()` now preserves `False` and `0` instead of rendering them as `-`, so read-only boundary tables do not hide disabled behavior.
