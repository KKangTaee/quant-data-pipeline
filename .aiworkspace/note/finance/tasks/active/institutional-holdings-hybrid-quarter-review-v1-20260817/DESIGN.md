# Institutional Holdings Hybrid Quarter Review V1 Design

## Approved Product Decision

- Source strategy: EDGAR individual filing + SEC quarterly bulk dataset hybrid.
- Page-entry behavior: local-only due check. No automatic SEC/EDGAR request.
- Mutation boundary: availability discovery, download and DB update start only after an
  explicit user click.
- Performance: show both quarter-end-to-quarter-end and filing-date-to-next-filing-date.
- Product meaning: delayed reported-long-holdings research, not actual fund NAV or a trade signal.

## User Flow

```text
Institutional Holdings opens
  -> read local latest report period + current date
  -> calculate latest quarter whose official filing due date has passed
  -> local data current: show next expected check date, no primary refresh button
  -> local data behind: show "YYYY QN 업데이트 확인 및 갱신"
      -> explicit click
      -> discover a newer SEC bulk ZIP
          -> available: ingest/reconcile the full official dataset
          -> unavailable: inspect curated-manager EDGAR submissions
              -> ingest complete published manager filings
              -> keep missing/failed managers pending
      -> reload local freshness and manager portfolio
      -> open latest available quarter review
```

The existing manual URL/local ZIP form remains an advanced recovery path under Data
Operations. It is not the default product workflow.

## Local Due Decision

The page does not infer availability from a network call. A pure calendar helper receives:

- current local date
- stored latest `report_period`
- calendar quarter ends
- the Form 13F deadline: 45 calendar days after quarter-end, rolled to the next US business
  day when the date is a weekend or US federal holiday

It returns the latest due report period, the next due date, whether local data is behind and the
single target report period for the button. Before the due date, early individual filers do not
cause a primary update action. This intentionally favors a predictable low-frequency workflow.

## Hybrid Discovery And Collection

### Bulk-first discovery

After click, the server parses the official SEC Form 13F Data Sets page and selects the newest
dataset whose content can include the target report period. It never constructs a future ZIP URL
by guessing a filename. A dataset already recorded as collected remains safely replayable but
does not count as a new update.

### Individual fallback

When the target bulk dataset is not published, the job checks the curated watchlist CIKs through
SEC submissions data. It accepts public `13F-HR` and `13F-HR/A` filings for the target report
period and downloads the filing documents required to normalize cover, summary and information
table rows into the existing manager/filing/holding ledger shape.

Requests use a declared SEC User-Agent, bounded timeouts, fair-access pacing and per-manager
failure isolation. One unavailable manager does not roll back complete managers.

### Promotion and reconciliation

- Raw filing metadata and holdings are keyed by accession and information-table identity.
- A manager is promoted to a newer report period only after required filing metadata and holding
  rows commit successfully in one DB transaction.
- A repeated accession is idempotent.
- When the bulk dataset later appears, it UPSERTs the canonical official flattened rows and
  reconciles source coverage without deleting individual raw evidence.
- The refresh result reports `updated / already_current / not_filed / failed` manager counts.

## Amendment-Aware Effective Quarter

Raw filings remain immutable ledger evidence. The loader resolves an effective quarter for one
manager as follows:

1. Start from the accepted base `13F-HR` for `(cik, period_of_report)`.
2. A restatement amendment replaces the prior effective information table.
3. A new-holdings amendment adds its rows to the current effective table without dropping base
   holdings.
4. Unknown or contradictory amendment metadata fails closed: keep the last unambiguous effective
   quarter and expose an amendment warning.

Selected-manager portfolio and quarter-review paths use this resolver rather than assuming the
latest accession alone is a complete portfolio. Existing raw source links stay visible.

## Quarter Review Contract

A review transition is `previous effective quarter -> current effective quarter` for the same
manager.

### Position identity and change labels

Rows are aggregated by `(CUSIP, title_of_class, put_call, amount_type)` before comparison.
Share/principal amount determines the label:

- `NEW`: absent previously, present currently
- `ADD`: present in both and amount increased
- `KEEP`: present in both and amount unchanged
- `REDUCE`: present in both and amount decreased
- `DROP`: present previously, absent currently
- `NOT_COMPARABLE`: both rows exist but amount evidence is missing or inconsistent

Reported market value alone never changes a position label because price movement is not a trade.
Options remain separate identities and are excluded from common-stock price proxy returns.

### Performance windows

Both windows use the previous quarter's reported-value weights:

1. `quarter_holdings_proxy`: previous quarter-end close to current quarter-end close.
2. `public_follow_proxy`: previous filing-date close to current filing-date close.

For each mapped common-stock holding, the price helper selects the first stored close on or after
the start date and the last stored close on or before the end date. It returns symbol return,
starting reported weight and contribution.

Missing price/identifier weight is not assigned a zero return. The UI displays the return of the
covered sleeve and its reported-value coverage separately:

- `READY`: coverage >= 80%
- `LIMITED`: 50% <= coverage < 80%
- `NOT_AVAILABLE`: coverage < 50% or a required boundary date is absent

The result is explicitly named a reported-long-holdings proxy. It excludes intra-quarter trades,
cash, shorts, many derivatives, fees and hedge structure.

## UI Contract

The healthy React path remains the complete visible surface. Streamlit owns route, service calls,
explicit command execution and fallback.

### Freshness action

- Current: `최신 보고 분기 반영 완료` and `다음 확인 예정 YYYY-MM-DD`; no primary button.
- Due: `YYYY년 N분기 업데이트 확인 및 갱신` primary button.
- Partial: `N/M개 기관 반영 · 미제출/실패 기관 다시 확인` with the same explicit action.
- No new filing after click: preserve current data and show the checked target/report timestamp.
- Failure: preserve current data and provide a bounded retry; raw exception text stays in details.

### Quarter Review destination

Add `분기 리뷰` to the existing studio destinations. The default transition is the latest pair
with two effective quarters. The view contains:

- manager and transition selector
- the two independent performance cards and coverage states
- change-count summary for `NEW / ADD / KEEP / REDUCE / DROP`
- contribution leaders and detractors
- filterable position-change table with previous/current amount, weight and return evidence
- source/caveat disclosure

If only one effective quarter exists, the view explains that one more filing is required instead
of rendering all current positions as `NEW`.

## Error And Partial-State Rules

- Network discovery failure never blocks viewing stored holdings.
- A 403/429 response is surfaced as retryable SEC access failure and does not promote freshness.
- Malformed/empty information tables do not create an empty latest portfolio.
- Per-manager failures remain visible and retryable without undoing successful managers.
- Bulk reconciliation failure leaves prior individual evidence readable.
- Missing prices or ambiguous identifiers reduce coverage; they do not become flat returns.
- `13F-NT` or combination-report references without a complete owned information table are shown
  as unavailable rather than fabricated holdings.

## Ownership

- `finance/data/institutional_13f.py`: bulk discovery/normalization and common persistence helpers
- focused new module under `finance/data/`: individual EDGAR filing discovery/parser
- `finance/data/db/schema.py`: only fields/tables required for persistent source/effective state
- `finance/loaders/institutional_13f.py`: effective-quarter and historical transition reads
- focused service module under `app/services/`: due decision and quarter-review calculation
- `app/services/institutional_portfolios.py`: workbench composition
- `app/jobs/ingestion_jobs.py`: explicit hybrid refresh orchestration
- `app/web/institutional_portfolios.py`: command/event boundary
- Institutional React workbench: freshness action and quarter-review presentation

Exact file creation and function signatures are deferred to the implementation plan after this
design is approved as a written spec.

## Verification Contract

- Parser fixtures: SEC bulk listing, submissions JSON, base filing, restatement, additive amendment,
  missing/invalid information table and 13F-NT.
- Pure tests: due-date decision, transition labels, two price windows, coverage thresholds.
- Persistence tests: idempotent accession, per-manager transaction, no incomplete promotion,
  bulk-after-individual reconciliation.
- Service/UI tests: current/due/partial/error states, no page-entry network request, explicit event,
  one-quarter unavailable review and latest transition payload.
- Actual QA: bounded SEC smoke with declared User-Agent, actual MySQL replay, desktop/tablet/mobile
  Browser QA and one final screenshot.
