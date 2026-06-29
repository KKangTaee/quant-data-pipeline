# Notes

Status: Active
Last Updated: 2026-06-29

## Design Notes

- Board rendering is intentionally UI-only and reads existing snapshot rows. It does not add provider calls or persistence.
- Top tape and list rows are not recommendations; boundary copy remains context-only.
- Sector mode can reuse the same board model by falling back from `Symbol` to `Group` / `Sector`.
