# Sources

Checked on 2026-06-30.

## Official / primary sources

- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- SEC accessing EDGAR data / fair access guidance: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- SEC accelerated filer / large accelerated filer definitions: https://www.sec.gov/resources-small-businesses/small-business-compliance-guides/accelerated-filer-large-accelerated-filer-definitions

## Libraries used by this project

- edgartools documentation: https://edgartools.readthedocs.io/
- edgartools GitHub: https://github.com/dgunning/edgartools
- yfinance documentation: https://ranaroussi.github.io/yfinance/
- yfinance GitHub: https://github.com/ranaroussi/yfinance
- yfinance PyPI: https://pypi.org/project/yfinance/

## Alternate provider references

- Financial Modeling Prep financial statement API docs: https://site.financialmodelingprep.com/developer/docs/stable/income-statement
- Polygon financials API docs: https://polygon.io/docs/rest/stocks/fundamentals/financials
- Alpha Vantage fundamentals docs: https://www.alphavantage.co/documentation/

## Local evidence

- `finance/data/fundamentals.py`
- `finance/data/financial_statements.py`
- `finance/data/factors.py`
- `finance/loaders/fundamentals.py`
- `finance/loaders/factors.py`
- `app/jobs/ingestion_jobs.py`
- `app/services/overview/why_it_moved.py`
- `app/runtime/backtest_strict.py`
- `app/web/backtest_common.py`
- `app/web/backtest_single_forms.py`
- `tests/test_service_contracts.py`

## Local DB checks

Queries were run against local MySQL `finance_fundamental` tables:

- `nyse_fundamentals`
- `nyse_fundamentals_statement`
- `nyse_financial_statement_values`

The current key finding is that broad yfinance tables have wider symbol count but shorter/staler history, while EDGAR statement shadow has longer PIT-friendly history for the current covered universe.
