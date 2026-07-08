# Risks

- Company filer deadlines vary by filer status; the UI treats actual EDGAR filing ledger evidence as stronger than simple deadline prediction.
- If the filing ledger is empty or stale, the UI should show 확인 필요 / 확인 불가 rather than implying the statement was definitely filed.
- Prediction-only checks tolerate nearby fiscal quarter dates because some companies report fiscal quarter ends a few days away from simple month-offset estimates.
