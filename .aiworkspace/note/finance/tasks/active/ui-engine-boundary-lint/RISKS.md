# UI Engine Boundary Lint Risks

## Open Risks

- If the script fails on all `app.web` imports today, it will block the current transitional architecture. Keep those as advisory first.
- Regex checks can have false positives; keep patterns narrow and report file/line.
- Staged artifact guard should not rewrite or remove files; it only reports and fails.

## Closed In This Slice

- The script passes on current service files while still surfacing transitional import debt.
- Generated / registry / saved artifact staging is guarded as a hard failure.
