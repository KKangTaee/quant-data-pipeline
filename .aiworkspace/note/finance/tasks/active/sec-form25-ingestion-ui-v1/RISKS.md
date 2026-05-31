# SEC Form 25 Ingestion UI V1 Risks

- Existing ingestion job framework records operational run history when users execute jobs. This task must not add a separate registry or memo store.
- Form 25 evidence can still be partial because old tickers may be absent from SEC ticker mapping.
- UI wording must not imply live approval, trading readiness, or complete survivorship control.
