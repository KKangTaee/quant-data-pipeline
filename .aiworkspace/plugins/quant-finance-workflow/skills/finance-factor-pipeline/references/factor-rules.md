# Factor Pipeline Rules

## Primary Code Areas

- `finance/data/fundamentals.py`
- `finance/data/factors.py`
- `finance/data/financial_statements.py`
- `finance/data/data.py`
- `finance/data/db/schema.py`

## Factor Classification

Classify each factor first:

- valuation: `per`, `pbr`, `psr`, `ev_ebit`
- profitability / quality: `gpa`, `roe`, `roa`
- safety / balance sheet strength: `current_ratio`, `debt_ratio`
- growth: `op_income_growth`, `asset_growth`, `shares_growth`
- custom accounting or event-driven: detailed statement labels or filing behavior

This classification informs source fields, timing sensitivity, denominator risk, and docs interpretation.

## Source Field Rules

State which fields are:

1. direct provider fields
2. normalized fields
3. fallback-computed fields
4. inferred fields

If a factor depends on inferred fields, treat that as a meaningful modeling assumption.

## Timing Rules

Always state whether the factor is keyed by accounting period end, filing date, or acceptance timestamp.

Current project reality:

- `fundamentals.py` is mostly `period_end` oriented.
- `financial_statements.py` captures filing-related fields.
- `factors.py` currently attaches market price by `period_end` as-of matching.
- `nyse_fundamentals` is the broad coverage summary layer.
- `nyse_factors` is the broad research derived layer.
- detailed statement tables remain the long-term raw truth.

If the factor is not filing-date safe, describe it as period-end based, research-oriented, and potentially exposed to look-ahead bias if used naively.

## Market Price Attachment

- Define whether close, adjusted close, or another field is used.
- Define the matching rule: exact date, previous available trading date, or another justified rule.
- Avoid forward fill unless explicitly justified.
- Current pattern: `period_end` matched to the most recent prior trading date using as-of logic.

## Formula And Storage

- Keep formulas readable and close to financial meaning.
- Use safe division helpers for denominator-sensitive ratios.
- Preserve `None`/missing when inputs are missing or invalid.
- For growth factors, state the lag rule clearly.
- Keep raw source tables and derived factor tables separate.
- Add schema entries in `schema.py`.
- Use stable uniqueness keys.

Current roles:

- `nyse_factors` stores attached base fields plus derived factors.
- `nyse_fundamentals` stores selected normalized summary fields plus derivation/source metadata.

Do not turn `nyse_fundamentals` into a raw dump or describe `nyse_factors` as strict PIT if the build path is still broad research oriented.

## Data Quality Checks

Check whether:

- denominator can be zero or negative
- source field can be structurally missing
- provider labels can drift
- accounting definitions differ across issuers

For detailed statement factors, confirm label selection, label normalization, generalizability, and fallback order.

## Downstream Use

Before finalizing, state whether the factor is for storage, ranking, screening/exclusion, or time-series strategy input. Reliability requirements differ by use case.

## Done Condition

- Business meaning is explicit.
- Source and fallback fields are explicit.
- Timing basis is explicit.
- Market price attachment rule is explicit.
- Schema and storage meaning are aligned.
- `nyse_fundamentals` / `nyse_factors` roles remain explicit when touched.
- Full backfill vs code hardening is separated when relevant.
- Data and architecture docs reflect updated factor behavior when meaning changed.
