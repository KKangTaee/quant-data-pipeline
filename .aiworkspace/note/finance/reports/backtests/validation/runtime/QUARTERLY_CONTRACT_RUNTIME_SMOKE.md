# Quarterly Contract Runtime Smoke

## 이 문서는 무엇인가

quarterly strict family에 연결한 `Portfolio Handling & Defensive Rules`가
실제 DB-backed runtime에서도 깨지지 않는지 확인한 개발 검증 report다.

여기서 중요한 것은 성과가 좋은 전략을 찾는 것이 아니다.
사용자가 quarterly 전략을 실행했을 때, UI에서 고른 portfolio handling contract가 runtime까지 전달되고,
결과 기록에도 다시 남는지를 확인하는 것이다.

## 검증 목적

이번 smoke validation은 아래 질문에 답하기 위한 것이다.

- quarterly 3개 family가 실제 DB-backed 경로에서 실행되는가?
- non-default contract 값을 넣어도 runtime이 에러 없이 처리하는가?
- 실행 결과의 `meta`에 contract 값이 남아서 history / load-into-form 복원에 쓸 수 있는가?
- 이 결과가 투자 분석이 아니라 제품 기능 검증으로 문서화되어 있는가?

## 실행 조건

| 항목 | 값 |
|---|---|
| 검증일 | 2026-04-19 |
| 실행 목적 | 개발 검증 smoke run |
| 전략 family | Quality / Value / Quality + Value strict quarterly prototype |
| Tickers | AAPL, MSFT, GOOG |
| 기간 | 2021-01-01 ~ 2024-12-31 |
| Top N | 2 |
| Trend Filter | Enabled, 200-day |
| Weighting Contract | Rank-Tapered |
| Rejected Slot Handling Contract | Fill Then Retain Unfilled Slots As Cash |
| Risk-Off Contract | Defensive Sleeve Preference |
| Defensive Sleeve Tickers | SPY, TLT |
| Market Regime | Enabled, SPY 200-day |

## 결과 요약

| 전략 | Rows | End Balance | Contract Meta 확인 |
|---|---:|---:|---|
| Quality Snapshot (Strict Quarterly Prototype) | 48 | 21,058.90 | 통과 |
| Value Snapshot (Strict Quarterly Prototype) | 48 | 18,271.10 | 통과 |
| Quality + Value Snapshot (Strict Quarterly Prototype) | 48 | 18,271.10 | 통과 |

## 확인한 contract meta

세 전략 모두 결과 `meta`에 아래 값이 남는 것을 확인했다.

| Meta Key | 확인 값 |
|---|---|
| `weighting_mode` | `rank_tapered` |
| `rejected_slot_handling_mode` | `fill_then_retain_cash` |
| `rejected_slot_fill_enabled` | `True` |
| `partial_cash_retention_enabled` | `True` |
| `risk_off_mode` | `defensive_sleeve_preference` |
| `defensive_tickers` | `SPY`, `TLT` |

## 검증 중 발견한 문제와 수정

첫 smoke run에서 계산은 성공했지만,
result bundle의 `meta`에 `weighting_mode`, `rejected_slot_handling_mode`,
`rejected_slot_fill_enabled`, `partial_cash_retention_enabled`가 빠져 있었다.

이 상태라면 UI에서 contract를 골라도 history / load-into-form 복원에서 일부 값이 사라질 수 있다.

수정 내용:

- 공통 `build_backtest_result_bundle()`에서 portfolio handling contract 관련 meta를 보존하도록 수정했다.
- 수정 후 quarterly 3개 family를 다시 실행했고, 세 전략 모두 contract meta 보존을 확인했다.

## 해석

이번 결과는 quarterly 전략이 투자 후보로 충분하다는 뜻이 아니다.

이번 결과가 의미하는 것은 더 좁다.

- quarterly strict 3개 family는 DB-backed runtime에서 portfolio handling contract를 받을 수 있다.
- non-default contract 조합에서도 기본 실행 경로가 깨지지 않았다.
- 결과 meta에 contract 값이 남기 때문에 history / load-into-form 복원 검증으로 이어갈 수 있다.

## 남은 확인

- Streamlit UI에서 quarterly `Portfolio Handling & Defensive Rules`가 자연스럽게 보이는지 확인한다.
- `Backtest > History > Load Into Form`에서 quarterly contract 값이 실제 form에 복원되는지 수동 확인한다.
- saved replay가 quarterly contract 값을 유지하는지 UI 레벨에서 확인한다.

## 한 줄 정리

Quarterly strict family는 실제 DB-backed smoke run 기준으로 portfolio handling contract 전달과 meta 보존까지 통과했으며,
남은 검증은 UI 수동 흐름 확인이다.
