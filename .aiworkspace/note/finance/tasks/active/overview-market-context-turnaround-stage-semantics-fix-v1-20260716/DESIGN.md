# Overview Market Context Turnaround Stage Semantics Fix V1 Design

Last Updated: 2026-07-16
Status: Approved direction, written spec review

## Problem

AAPL actual DB에서 PER 분석은 READY, current P/E는 `39.324x`, current TTM EPS는 `7.90`이다. 그러나 전환분석은 `CASH_FLOW_TURN` headline과 매출/GP·OCF·FCF 세 항목만 체크한다.

원인은 두 가지다.

1. `finance/loaders/us_stock_turnaround.py`의 duration unit filter에 실제 DB EPS 단위 `USD per share`가 없어 turnaround EPS rows가 query 단계에서 모두 빠진다.
2. `EPS 양전`은 recent quarterly EPS가 먼저 양수지만 TTM EPS는 아직 0 이하인 early-turn contract다. 이미 TTM EPS가 양수인 회사에는 NOT_MET이 맞지만 UI가 이를 실패처럼 표시한다. `영업손실 축소`도 실제 계약은 적자 여부가 아니라 영업이익률 개선 속도다.

## Actual AAPL Evidence

- PER status: `READY`
- current P/E: `39.324051096469546`
- PER current TTM EPS: `7.90`
- latest TTM revenue YoY: `+10.071%`
- latest TTM operating margin: `32.384%`
- recent operating-margin YoY deltas: `+0.592`, `+0.461`, `+0.629%p`
- latest TTM OCF: `$135.472B`
- latest TTM FCF: `$123.324B`
- raw diluted EPS row: `2.84`, `us-gaap:EarningsPerShareDiluted`, `USD per share`, period end `2025-12-27`
- current turnaround TTM EPS before fix: `null`
- read-only hypothesis test with `USD per share` allowed: turnaround TTM EPS `7.90`, headline `PER_READY`, PER_CANDIDATE/PER_READY `MET`

## Considered Approaches

### A. Data-unit fix only

EPS/PER READY는 복구하지만 `EPS 양전`과 `영업손실 축소`의 의미 혼동은 남는다. 제품 질문을 절반만 해결하므로 채택하지 않는다.

### B. Data fix plus semantic display states — selected

기존 independent milestone 계산과 6요소 rail을 유지한다. EPS 단위를 보정하고 UI-local `ESTABLISHED` 상태로 이미 양수인 회사를 전환 실패와 구분한다. 문구를 실제 계산 의미에 맞춘다.

### C. Backend milestone taxonomy 전면 재작성

각 metric을 transition/current/acceleration/readiness state machine으로 바꾸면 가장 정교하지만 payload·tests·downstream 범위가 커지고 현재 6요소 컨셉을 불필요하게 흔든다. V1 범위를 넘으므로 채택하지 않는다.

## Authoritative Data Design

- `_DURATION_UNITS`에 `USD per share`를 추가한다.
- source table, schema, collector, UPSERT는 변경하지 않는다.
- PER와 turnaround 모두 저장 `nyse_financial_statement_values`의 diluted EPS를 읽는다.
- `OPERATING_IMPROVEMENT` evidence에 latest operating margin, latest YoY delta, recent +1.0%p count를 추가한다. 판정 threshold는 바꾸지 않는다.
- existing milestone status `MET/NOT_MET/UNKNOWN`과 headline priority는 보존한다.

## Authoritative UI Design

6개 rail은 다음 의미로 표시한다.

| Slot | Default label | Positive/established behavior |
|---|---|---|
| 1 | 매출 성장 / GP 개선 | revenue direction 또는 GP margin +1.0%p evidence면 `확인` |
| 2 | 영업 수익성 개선 | threshold MET면 `개선 확인`; current margin > 0이나 threshold 미달이면 `흑자 · 개선폭 미달` |
| 3 | OCF 양수 지속 | 최근 2개 TTM OCF가 양수면 `확인` |
| 4 | FCF 양수 | current TTM FCF가 양수면 `확인` |
| 5 | EPS 양전 신호 | EARNINGS_TURN MET면 `전환 확인`; TTM EPS가 이미 양수면 label `TTM EPS 양수`, display state `ESTABLISHED`, detail `이미 양수` |
| 6 | PER 적용 가능 | PER_READY MET면 `적용 가능` |

- `ESTABLISHED`는 UI-local display state이며 backend milestone status를 바꾸지 않는다.
- `READY` badge는 `분석 가능`으로 번역한다. 이는 6개 모두 통과가 아니라 분석 근거 충족을 뜻한다.
- headline은 raw enum 대신 `PER 적용 가능`, `PER 후보`, `EPS 양전 신호`, `현금흐름 전환`, `영업 개선`, `손실 기준`의 사용자 문구로 표시한다.
- UNKNOWN/PARTIAL은 `근거 부족`, true NOT_MET은 `아직 미확인`, profitable-but-below-threshold는 neutral `흑자 · 개선폭 미달`로 구분한다.
- rail은 단계 funnel이 아니며 앞 단계를 자동 통과시키지 않는다.

## AAPL Expected Result

- headline: `PER 적용 가능`
- 매출 성장 / GP 개선: 확인
- 영업 수익성 개선: 흑자 · 개선폭 미달
- OCF 양수 지속: 확인
- FCF 양수: 확인
- TTM EPS 양수: 이미 양수
- PER 적용 가능: 적용 가능

PER 상대가치의 `상대적 고평가` 판정은 별도 valuation position이며 위 operating/readiness state를 변경하지 않는다.

## Error And Edge Cases

- EPS raw row가 실제 없으면 `근거 부족`이며 0 또는 적자로 추정하지 않는다.
- quarterly EPS 양전, TTM EPS <= 0이면 `EPS 양전 신호`만 확인하고 PER는 적용하지 않는다.
- TTM EPS > 0이나 PER history가 부족하면 `TTM EPS 양수`는 established, `PER 적용 가능`은 미확인으로 분리한다.
- 현재 영업이익률이 양수지만 acceleration threshold 미달이면 실패색 대신 neutral established context를 사용한다.
- negative-margin 회사도 동일 +1.0%p 개선 threshold를 사용하며 자동 pass하지 않는다.

## Files

- `finance/loaders/us_stock_turnaround.py`
- `finance/data/us_stock_turnaround.py`
- `app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx`
- `app/web/streamlit_components/market_context_valuation/src/style.css`
- `tests/test_us_stock_turnaround.py`
- `tests/test_market_context_valuation.py`

## Verification Contract

- loader query-spy RED/GREEN for `USD per share`
- milestone evidence RED/GREEN without threshold change
- React source-contract RED/GREEN for new labels, established state, Korean headline/status
- focused turnaround/PER/Market Context tests
- target `py_compile`, Vite production build
- actual AAPL model equality between PER and turnaround TTM EPS
- AAPL and one negative-EPS transition company desktop/420px Browser QA
- no horizontal overflow, duplicate CTA, provider call on selector switch, or console error
