# Plan

## 이걸 하는 이유?

Market Movers daily refresh에서 반복적으로 남는 `missing quote row` 티커는 단순 재수집만으로 해결되지 않는 경우가 있다. 1차 목표는 자동 제외나 강한 상장폐지 판정이 아니라, 무료 source와 내부 DB evidence를 조합해 사용자가 다음 조치를 판단할 수 있는 원인 후보를 보여주는 것이다.

## Scope

- Market Movers `Coverage Diagnostics`의 missing 티커를 대상으로 수동 quote gap diagnosis를 실행한다.
- 외부 source는 기존 Yahoo / yfinance와 내부 DB evidence만 사용한다.
- 1차에서는 SEC / Nasdaq official symbol directory, 자동 fallback 가격 반영, 자동 universe 제외는 제외한다.

## Steps

1. Missing quote 대상 조회 / 진단 service 추가.
2. Ingestion-style job wrapper 추가.
3. Overview UI 버튼과 결과 테이블 연결.
4. Focused service contract tests 추가.
5. Browser smoke와 문서 closeout.
