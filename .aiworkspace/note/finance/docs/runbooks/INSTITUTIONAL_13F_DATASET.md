# Institutional 13F Dataset Runbook

Status: Active
Last Verified: 2026-07-08

## Purpose

Use this runbook to load official SEC Form 13F quarterly data sets for `Workspace > Institutional Portfolios`.

## Source

- Official data page: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
- EDGAR API guidance: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- SEC data access guidance: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

The official page should be checked before each refresh. On 2026-07-08, the latest page entry was `2026 March April May 13F`.

## App Path

1. Open the Finance Streamlit app.
2. Go to `Workspace > Ingestion`.
3. Open `SEC Form 13F 데이터셋 수집`.
4. Confirm the official dataset URL or provide a local SEC ZIP path.
5. Set a descriptive dataset label, for example `2026 March April May 13F`.
6. Run the collection.
7. Open `Workspace > Institutional Portfolios`.

## Environment

Set a descriptive SEC user agent when downloading from SEC:

```bash
export SEC_USER_AGENT="quant-data-pipeline contact@example.com"
```

The collector can also load a local ZIP path. Prefer local ZIP for repeat QA so tests and UI checks do not repeatedly download large SEC files.

## Data Path

```text
SEC Form 13F ZIP
  -> finance/data/institutional_13f.py
  -> finance_meta.institutional_13f_manager
  -> finance_meta.institutional_13f_filing
  -> finance_meta.institutional_13f_holding
  -> finance_meta.institutional_13f_cusip_symbol_map
  -> finance/loaders/institutional_13f.py
  -> app/services/institutional_portfolios.py
  -> app/web/institutional_portfolios.py
```

## QA

```bash
git diff --check
.venv/bin/python tests/test_institutional_portfolios.py
.venv/bin/python -m py_compile finance/data/institutional_13f.py finance/loaders/institutional_13f.py app/services/institutional_portfolios.py app/web/institutional_portfolios.py
```

If UI changes are present, run Browser QA against `Workspace > Institutional Portfolios` and keep screenshots out of the commit.

## Caveats

- 13F is delayed reporting and can be filed up to 45 days after quarter end.
- Holdings are not live trading intent.
- 13F does not fully show shorts, cash, derivatives, hedge structure, non-reportable securities, or complete portfolio context.
- Amendments, confidential treatment, filer errors, and SEC extraction issues can change interpretation.
- CUSIP-symbol mapping is best-effort display metadata, not a complete security master.
