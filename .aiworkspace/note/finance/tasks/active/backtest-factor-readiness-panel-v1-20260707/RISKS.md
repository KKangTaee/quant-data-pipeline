# Backtest Factor Readiness Panel V1 Risks

## Risks

- Existing untracked QA artifacts and run history should remain unstaged.
- Browser QA screenshot `backtest-factor-readiness-panel-v1-qa.png` is a generated artifact and should remain unstaged unless explicitly requested.
- Portfolio Mix Builder wiring is covered by code contract tests. Browser QA directly verified the shared component in Single Strategy; Portfolio Mix radio interaction was unstable in browser automation.
