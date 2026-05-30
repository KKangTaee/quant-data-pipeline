# Backtest Real-Money Readiness Efficacy V1 Status

Status: Complete
Created: 2026-05-30

## Current State

- User approved refining the 1st-pass Real-Money indicators after reviewing whether they are actually useful.
- No indicator family needs deletion, but the calculation / display boundary should be tightened.
- Runtime `Execution Preview` now ignores legacy later-stage `shortlist_status`, `probation_status`, and `monitoring_status` fields.
- Candidate Readiness now scores `Promotion Decision`, `Execution Source Checks`, and `Validation Source Checks`.
- Turnover / cost display now shows estimation status and avoids presenting missing turnover evidence as a clean zero.
- Backtest split-period wording now reads as a simple first/back-half check, not formal OOS validation.

## Next

- User review in the Backtest UI should confirm the Real-Money panel answers only the 1차 question: "can this candidate be moved to the next validation step?"
