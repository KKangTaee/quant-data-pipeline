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

## 2026-07-12 Implementation And QA

- 1차 focused closure / Practical Validation / Final Review regression: 98 tests, `OK`.
- 2차 actionability / Gate / runtime regression: 177 tests, `OK`; 760px Practical Validation Browser QA에서 current-session replay guard와 horizontal overflow 없음 확인.
- 3차 focused GRS / GTAA / ETF runtime / replay / coverage / closure regression: 121 tests, `OK`.
- 실제 DB GRS fixture: 119 rows, latest `2026-06-26`, `Row Kind=valuation`, `Rebalancing=False`, `Raw Selected Ticker=[]`, valuation row 1개.
- 실제 weighted source replay: status `PASS`, requested common end `2026-06-26`, GRS actual end `2026-06-26`, GRS last signal `2026-05-29`.
- 4차 closure / Final Review read model / runtime regression: 168 tests, `OK`; React Vite production build와 target py_compile 통과.
- Browser QA: stale selector가 이전 report를 숨기고 재확인을 요구함, report에 `선정 전 미해결 항목 0`, `인수한 한계와 최종 판단 항목`, 기존 route/reason 표시, `세부 설명 준비 안 됨` 미노출, 760px overflow 없음.
- QA screenshot: `qa-final-review-evidence-closure-final-760.png` generated artifact로 남기고 commit하지 않음.
- closeout fresh focused suite: 계획에 명시한 8개 module/class, 126 tests, `OK`.

## 2026-07-12 Follow-up UX Correction

- RED: 새 workspace / source contract 2개가 `final_review_limit_count` 부재와 기존 `_render_evidence_closure_groups` 잔존으로 실패했다.
- GREEN: 같은 2개 test가 통과했다.
- focused regression: `tests.test_backtest_evidence_closure` + `PracticalValidationServiceContractTests`, 45 tests, `OK`.
- Practical Validation fix queue Vite production build, target `py_compile`, `git diff --check` 통과.
- Browser QA: current GRS replay 후 Flow 3 accepted-limit root count 5, immediate/development blocker 0, Flow 4 old closure path 없음, `· 미정` 없음, 760px document `clientWidth=760 / scrollWidth=760`, console error 0.
- QA screenshot: `qa-practical-validation-closure-summary-760.png` generated artifact로 남기고 commit하지 않는다.
