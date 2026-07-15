# Institutional Portfolios Workspace V1 Notes

## Decisions

- Page label: `Institutional Portfolios`.
- Sub-mode label for ticker/CUSIP reverse lookup: `Institutional Interest`.
- Primary source: SEC Form 13F official data sets.
- Third-party sources: UX benchmark and external reference only.
- Source caveat copy must avoid current-action wording.
- Navigation decision remained `Workspace > Institutional Portfolios`; `Operations` was rejected because it implies user portfolio monitoring / action queue semantics.
- Reverse lookup weight must be calculated against each manager's latest total 13F reported portfolio, not only against matching search rows.

## Durable Caveats

- Form 13F is a delayed quarterly disclosure and may be filed up to 45 days after quarter end.
- 13F does not show short positions, full derivatives, cash, bonds, hedging structures, or real-time intent.
- Confidential treatment, amendments, and source extraction issues can change what is visible.
- CUSIP-symbol mapping is partial unless a separate mapping source is verified.
