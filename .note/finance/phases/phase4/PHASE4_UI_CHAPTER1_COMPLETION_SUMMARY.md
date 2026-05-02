# Phase 4 UI Chapter 1 Completion Summary

## 목적
이 문서는 Phase 4의 첫 UI 실행 챕터가 어디까지 완료되었는지 요약한다.

이 챕터의 중심 목표는
`DB-backed price-only 전략을 웹 UI에서 실행하고, 비교하고, 다시 읽을 수 있게 만드는 것`이었다.

## 완료된 범위

### 1. 메인 앱 구조
- 메인 Streamlit 앱 하나를 유지
- `Ingestion` / `Backtest` 탭 구조 확정
- 내부 코드는 탭별/관심사별로 분리

### 2. 공개 전략 실행 경로
- `Equal Weight`
- `GTAA`
- `Risk Parity Trend`
- `Dual Momentum`

위 4개 price-only 전략이 모두 DB-backed runtime wrapper를 통해 UI에서 실행 가능하다.

### 3. 단일 전략 결과 화면
- KPI metric row
- summary table
- equity curve
- result table
- execution meta
- balance / period extremes

### 4. 다중 전략 비교
- 최대 4개 전략 비교
- equity / drawdown / total-return overlay
- focused strategy drilldown
- strategy highlights table

### 5. 가중 포트폴리오 빌더
- compare 결과를 바탕으로 weighted portfolio 생성
- contribution amount / share 시각화
- weighted result용 extremes / markers

### 6. Backtest History
- persistent JSONL history 저장
- run kind filter
- 검색
- recorded date range filter
- metric sort
- drilldown
- single-strategy `Run Again`
- single-strategy `Load Into Form`
- form prefill

## 아직 intentionally 남겨둔 것
- compare / weighted rerun
- factor / fundamental strategy UI
- strict PIT snapshot 기반 전략 runtime
- 전체 `?` help icon 스타일 통일

## 결론
- Phase 4 첫 UI 챕터는 실질적으로 완료 상태로 본다.
- 다음 챕터의 자연스러운 시작점은
  `factor / fundamental 전략 진입 준비`
  다.
