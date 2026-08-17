# Runs

- RED: `.venv/bin/python -m pytest tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -k "separates_positive or popularity_model_ranks or source_caveats" -q` → expected 2 failures: sign-separated contributor list and missing `reported_value_label`.
- RED: `InstitutionalPortfolioReadModelTests::test_visual_workbench_payload_prioritizes_portfolio_chart_and_change_boards` → expected missing `source_caveats.title` failure.
- GREEN: `.venv/bin/python -m pytest tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -q` → 76 passed, 3 third-party `edgar` deprecation warnings, 4 subtests passed.
- Review: `git diff --check` → clean.
