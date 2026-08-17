# Risks

- No open implementation blocker.
- At 360px, the family and view rails retain desktop styling and wrap without page-level horizontal overflow.
- Existing deep links remain protected by the focused normalization and renderer tests; `economic-cycle` is retained as the 경기 국면 compatibility slug.
- Repository-wide `tests/test_service_contracts.py` is not fully green: 18 pre-existing failures remain in unchanged, out-of-scope sentiment, Final Review, Practical Validation, Futures Macro and AAII contracts. The changed `OverviewAutomationContractTests` class passes all 201 tests.
