# Runs

## 2026-07-23 Read-only inspection

- `git status --short`, `git log -6 --oneline`
  - unrelated registry/run-history/QA artifacts가 존재하므로 작업 파일만 선별한다.
- finance docs, NYSE collector/writer, symbol source, Ingestion registry/dispatcher/section을 확인했다.
- MySQL current master summary:
  - stock: 6,738 rows, lifecycle last snapshot 2026-05-31
  - ETF: 5,232 rows, lifecycle last snapshot 2026-05-31
- NYSE official current listing API read-only diff:
  - stock: current 6,770, DB missing 158, DB-only 126
  - ETF: current 5,537, DB missing 372, DB-only 67
- DB write는 수행하지 않았다.
