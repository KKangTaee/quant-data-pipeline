# Futures Macro Observation Copy V3 Runs

Last Updated: 2026-08-17

| 검증 | 결과 |
|---|---|
| TDD RED | 신규 문장 계약 3건이 기존 축약형 출력 때문에 예상대로 실패 |
| TDD GREEN | 신규 문장 계약 3건 통과 |
| Short-horizon 전체 | 23 passed, 기존 edgar deprecation warning 3건 |
| Futures Macro 회귀 | short-horizon + refresh + integration 46 passed |
| Production build | Vite 180 modules, exit 0 |
| Browser QA desktop | 실제 저장 데이터의 1D·5D·20D 두 문장과 중복 eyebrow 0건 확인 |
| Browser QA 420px | outer 420/420, iframe·component 377/377 client/scroll width |
| Browser console | warning/error 0건 |
| QA screenshot | `futures-macro-observation-copy-v3-qa.png`; generated artifact라 commit 제외 |
| 광범위 공통 계약 | 894 passed, 19 unrelated failures, 41 subtests passed; 이번 변경 파일 밖의 기존 contract drift |

## Common Contract Gap

`tests/test_service_contracts.py` 전체 실행은 기존 Backtest, sentiment, AAII, legacy Futures
thermometer와 이전 refresh contract에서 19건 실패했다. 이번 변경은 observation narrative와
React copy만 수정하며, 직접 관련 회귀 46건은 별도로 통과했다.
