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
10. `History Replay / Load Parity Snapshot`에서 핵심 설정이 저장되어 보이는지 확인한다.
11. saved portfolio replay가 해당 strategy override를 복원할 수 있는지 확인한다.
12. `Saved Portfolio Replay / Load Parity Snapshot`에서 compare context, weights, strategy overrides가 읽히는지 확인한다.
13. compile / import / synthetic smoke / DB-backed smoke를 실행한다.
14. phase docs, checklist, comprehensive analysis, doc index를 필요한 만큼 갱신한다.

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

현재 주요 구현 메모:

- `Equal Weight`는 단순 baseline 성격이 강하다.
- `GTAA`, `Risk Parity Trend`, `Dual Momentum`은 기존 ETF allocation family다.
- `Global Relative Strength`는 Phase 24에서 추가된 price-only ETF allocation family다.
- `Global Relative Strength`는 trailing return score로 상위 ETF를 고르고, trend filter를 통과하지 못한 슬롯은 cash proxy로 둔다.
- ETF family는 데이터 이력 부족이나 결측 ticker를 조용히 무시하지 않고 `excluded_tickers`, `malformed_price_rows`, warning metadata로 남겨야 한다.
- ETF family의 real-money / guardrail surface는 live approval이 아니라 실행 부담과 후보 검토 상태를 읽기 위한 진단 계층이다.

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

현재 주요 구현 메모:

- strict annual family는 `Quality`, `Value`, `Quality + Value`를 중심으로 운영된다.
- strict annual은 broad factor path보다 statement shadow / annual PIT snapshot path를 더 중요하게 본다.
- strict quarterly family는 Phase 23 이후 UI / payload / history / saved replay 계약이 보강됐지만, annual strict와 완전히 같은 real-money / guardrail parity를 가진 것은 아니다.
- factor strategy는 단순 수익률 table만이 아니라 selection history, interpretation summary, contract metadata를 함께 보존해야 한다.

## Strict Annual Contract 요약

strict annual family는 현재 여러 operator-facing contract를 가진다.
세부 UI 문구와 payload key는 `WEB_BACKTEST_UI_FLOW.md`와 `BACKTEST_RUNTIME_FLOW.md`를 같이 확인한다.

| Contract | 의미 | 결과에서 확인할 것 |
|---|---|---|
| `Universe Contract` | 어떤 후보군을 사용할지 정한다 | universe label, coverage, candidate count |
| `Benchmark Contract` | 단일 ticker benchmark 또는 candidate universe equal-weight 기준선 | benchmark label, benchmark coverage, spread diagnostics |
| `Rejected Slot Handling Contract` | trend filter로 일부 후보가 빠졌을 때 빈 슬롯을 어떻게 처리할지 정한다 | filled count, cash-retained events, rejected slot handling |
| `Weighting Contract` | 최종 선택 종목을 equal-weight로 둘지 rank-tapered로 둘지 정한다 | weighting mode, next weight |
| `Risk-Off Contract` | portfolio-wide risk-off 때 cash only인지 defensive sleeve preference인지 정한다 | risk-off reason, defensive sleeve activations |
| `Guardrails` | underperformance / drawdown 조건에서 포트폴리오를 보수적으로 전환한다 | trigger count, blocked count, policy status |

중요한 구분:

- `Rejected Slot Handling Contract`는 일부 종목만 trend filter에서 빠지는 상황을 다룬다.
- `Risk-Off Contract`는 market regime이나 guardrail 때문에 포트폴리오 전체를 쉬게 하는 상황을 다룬다.
- `Benchmark Contract = Candidate Universe Equal-Weight`는 선택 가능한 후보군을 단순 균등 보유한 기준선이며, 단일 `Benchmark Ticker`와 같은 의미가 아니다.
- contract는 대부분 on/off 토글이 아니라 실행 시 항상 저장되는 처리 규칙이다. 실제 영향은 관련 상황이 발생할 때만 나타난다.

## 제품 연결 체크리스트

새 strategy family는 core 함수만 추가되면 완료가 아니다.
제품 전략으로 보려면 아래 surface를 확인한다.

- Single Strategy에서 실행 가능
- Compare에서 선택 가능
- strategy-specific advanced inputs가 payload에 보존
- History record에 설정이 저장
- History Replay / Load Parity Snapshot에서 저장 상태가 읽힘
- `Load Into Form`으로 입력 복원
- `Run Again`으로 재실행
- Saved Portfolio replay에서 override 복원
- Saved Portfolio Replay / Load Parity Snapshot에서 weight와 override 저장 상태가 읽힘
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
