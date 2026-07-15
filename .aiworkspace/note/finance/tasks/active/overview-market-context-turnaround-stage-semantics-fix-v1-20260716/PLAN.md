# Overview Market Context Turnaround Stage Semantics Fix V1 Plan

Last Updated: 2026-07-16

## 이걸 하는 이유?

AAPL처럼 이미 EPS·PER·영업이익이 양수인 기업이 전환분석에서 `EPS 양전`, `PER READY`, `영업손실 축소`를 미확인으로 보여 사용자가 적자 또는 분석 실패로 오해할 수 있다. 실제로는 EPS 단위 누락 버그와 전환 신호/현재 상태를 같은 체크 표현으로 표시한 UX 의미 문제가 겹쳐 있다.

## Goal

6개 전환 요소의 직관적인 구조는 유지하면서 저장 EPS를 정확히 읽고, `전환 신호`, `이미 양수`, `PER 적용 가능`, `개선폭 미달`, `근거 부족`을 서로 구분한다.

## Roadmap

1. EPS loader 단위와 milestone evidence 계약을 TDD로 보정한다.
2. 6개 rail 문구·상태·headline을 사용자 의미에 맞게 개선한다.
3. Actual AAPL, desktop/420px Browser QA, focused/full regression, 문서 정렬을 완료한다.

## Scope

- `USD per share` diluted EPS read boundary
- AAPL과 적자/전환기업을 함께 보존하는 independent milestone semantics
- selected-stock 전환분석 rail과 status/headline copy
- tests, production build, actual/Browser QA

## Out Of Scope

- milestone threshold 자체 변경
- universe-wide ranking/screener
- provider 자동 수집, DB schema, 새 table
- run/job/row 진단 panel

## Stop Condition

AAPL에서 TTM EPS `7.90`, `PER_READY`, `PER 적용 가능`이 일치하고, 이미 흑자인 기업의 EPS/영업 상태가 실패처럼 보이지 않으며, 기존 RIVN/LCID/PLTR 전환 신호 계약과 PER/S&P 화면이 회귀하지 않는다.
