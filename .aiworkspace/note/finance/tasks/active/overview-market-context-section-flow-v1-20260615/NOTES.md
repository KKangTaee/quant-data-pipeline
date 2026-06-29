# Overview Market Context Section Flow V1 Notes

## Intake Notes

- Worktree: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`.
- Branch: `codex/sub-dev`.
- Prior commit: `1ab5be2c Overview 시장맥락 하이브리드 시각화 적용`.
- Existing local/generated artifacts include `.DS_Store`, `.superpowers/`, and prior QA PNGs; do not stage them.

## Design Notes

- The user's complaint is not that the top hybrid dashboard is wrong; it is that the lower explanatory/reference material is still buried inside the same large surface.
- The implementation should separate hierarchy first, then typography. No new data or diagnostic workflow is needed.
- `_macro_cockpit_body_html()` now returns only the top dashboard body: tape + sector pressure + event timeline.
- `_macro_context_cockpit_html()` assembles the top cockpit plus sibling `.ov-macro-reading-flow`.
- Reading sections intentionally use full-width bands with left accents rather than nested cards.
