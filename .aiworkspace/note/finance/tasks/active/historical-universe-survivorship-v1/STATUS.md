# Status

## 2026-05-28

- Implementation complete.
- `nyse_symbol_lifecycle` schema / loader / Data Coverage Audit integration을 추가했다.
- requested period를 덮는 historical / delisting lifecycle evidence가 있을 때만 survivorship control PASS가 된다.
- current listing snapshot과 asset profile evidence만 있으면 REVIEW로 남긴다.
- 새 workflow JSONL, memo, preset, approval, order, auto rebalance는 추가하지 않았다.
