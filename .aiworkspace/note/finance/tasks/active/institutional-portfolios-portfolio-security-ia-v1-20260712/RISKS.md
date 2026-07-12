# Institutional Portfolios Portfolio / Security IA V1 Risks

## Remaining Risks

- This task only clarifies IA. It does not add true multi-quarter holding duration metrics. If the product needs `몇 분기 연속 보유` / `최초 확인 분기`, that should be a separate data/read-model task.
- `interest` remains an internal event / payload name for backend compatibility, while user-facing UI now says `종목 상세`. A later internal refactor can rename the event boundary if it becomes confusing for maintainers.
