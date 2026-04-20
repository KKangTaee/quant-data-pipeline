# Strategy Implementation Flow

## 목적

이 문서는 새 strategy family를 finance 제품에 추가할 때 어떤 파일과 문서를 갱신해야 하는지 설명한다.
Phase 24의 `Global Relative Strength` 추가 이후, 새 전략 확장을 반복 가능하게 만들기 위한 기준이다.

## 현재 strategy 계층

| 계층 | 대표 파일 | 역할 |
|---|---|---|
| core simulation | `finance/strategy.py` | 실제 전략 로직 |
| preprocessing | `finance/transform.py` | MA, return, date alignment, snapshot shaping |
| orchestration | `finance/engine.py` | price strategy chaining |
| DB-backed sample/runtime helper | `finance/sample.py` | 수동 smoke와 reusable helper |
| web runtime adapter | `app/web/runtime/backtest.py` | UI payload를 실행 가능한 runtime으로 변환 |
| web UI | `app/web/pages/backtest.py` | form, compare, history, saved replay |

## 새 전략 추가 순서

1. 전략 성격을 먼저 분류한다.
2. 필요한 데이터가 현재 DB / loader로 가능한지 확인한다.
3. core strategy를 `finance/strategy.py` 또는 적절한 strategy module에 추가한다.
4. 필요한 transform helper가 있으면 `finance/transform.py`에 재사용 가능한 함수로 둔다.
5. DB-backed runtime helper를 `finance/sample.py` 또는 runtime adapter에서 재사용 가능하게 만든다.
6. `app/web/runtime/backtest.py`에 `run_*_backtest_from_db(...)` wrapper를 추가한다.
7. `app/web/pages/backtest.py`의 single strategy catalog와 form에 연결한다.
8. compare strategy catalog와 strategy-specific override를 연결한다.
9. history payload, `Load Into Form`, `Run Again` 복원을 확인한다.
10. saved portfolio replay가 해당 strategy override를 복원할 수 있는지 확인한다.
11. compile / import / synthetic smoke / DB-backed smoke를 실행한다.
12. phase docs, checklist, comprehensive analysis, doc index를 필요한 만큼 갱신한다.

## 전략 유형별 기준

### Price-only ETF 전략

예:

- `GTAA`
- `Risk Parity Trend`
- `Dual Momentum`
- `Global Relative Strength`

주요 계약:

- price history
- moving average / relative return warmup
- date alignment
- cash fallback
- optional real-money / guardrail / pre-live surface

### Factor / fundamental 전략

예:

- `Quality Snapshot`
- `Value Snapshot`
- `Quality + Value Snapshot`

주요 계약:

- universe contract
- rebalance date
- statement snapshot / factor snapshot
- point-in-time handling
- candidate coverage
- selection history / interpretation
- real-money contract / guardrail / promotion semantics

## 제품 연결 체크리스트

새 strategy family는 core 함수만 추가되면 완료가 아니다.
제품 전략으로 보려면 아래 surface를 확인한다.

- Single Strategy에서 실행 가능
- Compare에서 선택 가능
- strategy-specific advanced inputs가 payload에 보존
- History record에 설정이 저장
- `Load Into Form`으로 입력 복원
- `Run Again`으로 재실행
- Saved Portfolio replay에서 override 복원
- result warning / metadata가 사용자에게 보임
- checklist가 실제 UI 위치를 기준으로 작성됨

## 문서 갱신 기준

새 전략을 추가하면 최소한 아래를 검토한다.

- active phase plan / TODO / checklist
- `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- `FINANCE_DOC_INDEX.md`
- `code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md`
- strategy hub 또는 backtest report index
- `WORK_PROGRESS.md`
- 중요한 설계 판단이 있으면 `QUESTION_AND_ANALYSIS_LOG.md`

## 하지 말아야 할 것

- 성과가 좋아 보인다는 이유만으로 새 전략을 live-ready로 표현하지 않는다.
- research note의 매력도를 구현 가능성과 혼동하지 않는다.
- core strategy만 추가하고 compare/history/saved replay 계약을 누락하지 않는다.
- point-in-time, survivorship, stale price risk를 warning 없이 숨기지 않는다.
