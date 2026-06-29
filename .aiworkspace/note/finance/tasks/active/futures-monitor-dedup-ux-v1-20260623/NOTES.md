# Futures Monitor Dedup UX V1 Notes

## Decisions

- This is a UX ownership cleanup, not a new data feature.
- Diagnostics and raw provider information remain available, but should not compete with the default reading path.
- The command center owns page-level status; chart cards own symbol-level status.
- Macro hero owns the scenario; support strips own confidence / validation facts.
- Provider run `rows_written` / latest candle timestamp now stay in `진단 / Provider 근거` instead of command center or Live Chart defaults.
- Live Chart keeps the stale warning and symbol state chips because they point to chart usability, not provider job diagnostics.
- Macro confidence support values use short labels such as `낮음`, `보통`, `높음` to avoid repeating the card title.
