# Runs

## 2026-07-12 Analysis

- latest GRS Practical Validation JSONL row를 read-only로 확인했다.
- `load_price_freshness_summary`로 SPY / QQQ / GLD / IEF / TLT / BIL / AOR latest date를 확인했다.
- `get_global_relative_strength_from_db(...)`를 read-only로 재실행해 actual result end가 `2026-05-29`임을 재현했다.
- 2026년 6월 ticker별 last row가 BIL `2026-06-26`, 나머지 risky ticker `2026-06-30`임을 확인했다.
- Final Review Level2 disposition을 read-only로 만들어 latest replay `-6`, data coverage `-6` 고정 impact를 확인했다.
- code / registry / saved / run history write는 수행하지 않았다.

## 2026-07-12 Planning Baseline

- `.venv/bin/python -m pytest ...`: `.venv`에 pytest가 없어 `No module named pytest`로 종료했다. dependency는 추가하지 않았다.
- `.venv/bin/python -m unittest tests.test_global_relative_strength_strategy tests.test_gtaa_strategy tests.test_service_contracts.DataCoverageAuditContractTests tests.test_service_contracts.PracticalValidationReplayServiceContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`: 75 tests, `OK`.
- recent commit, module/audit/trace/score/replay/GRS data flow를 read-only로 역추적해 DESIGN.md의 root cause를 재확인했다.
- `PLAN.md`는 function signature, RED/GREEN command, Browser QA, distinct commit scope 기준으로 self-review했다.
