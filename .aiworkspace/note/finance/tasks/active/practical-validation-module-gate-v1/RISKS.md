# Practical Validation Module Gate V1 Risks

Status: Active
Created: 2026-05-30

## Risks

- Gate can become too strict and block all current candidates until replay is run.
- Module classification can hide useful detailed evidence if the UI removes old diagnostics too quickly.
- Strategy trait inference can be imperfect for future strategy families.

## Mitigation

- Keep detailed diagnostics visible.
- Make required vs conditional module reasoning explicit in rows.
- Add service tests for source traits and final review gate behavior.
- Do not add new persistence or live trading behavior.

## Remaining

- Trait inference is intentionally conservative and may need extra strategy key mappings as new non-ETF factor strategies enter Practical Validation.
- The first candidate still needs a user-triggered latest runtime replay before it can be saved and moved to Final Review.
