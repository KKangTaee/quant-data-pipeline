# Risks

Status: Active
Last Updated: 2026-06-07

## Residual Risks

- This pass does not physically move old task / phase folders, so file browsers will still show many folders under `active/`.
- Some old task / phase docs may still contain historical `Status: Active` text from their original execution window. The current-state source of truth is the active README and manifest, not every retained folder's old status line.
- A future physical migration needs link repair or redirect index checks before moving folders.
- `.note/` remains local / untracked and outside this cleanup.
