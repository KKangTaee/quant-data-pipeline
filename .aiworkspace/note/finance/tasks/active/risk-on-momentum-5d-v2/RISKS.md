# Risk-On Momentum 5D V2 Risks

## Open Risks

- Top1000 / Top2000 comparison and sensitivity suites can be expensive; UI controls should let the user keep the basic run simple.
- Ranking penalty is a market-wide score adjustment, so it may not change same-day cross-sectional ordering unless a future threshold uses the adjusted score.
- V2 quality warnings are research diagnostics, not Practical Validation pass/fail results.

## Closed / Managed

- Full comparison and sensitivity suite behavior is covered by focused service tests; Browser QA used a lighter UI run because a full interactive comparison run can be slower under headless Streamlit.
- MCP Browser and Computer Use were unavailable for this QA pass, so isolated Playwright Core with system Chrome was used as a fallback.
