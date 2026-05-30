# Plan

## 이걸 하는 이유?

Overview Events는 4차까지 FOMC와 earnings 중심의 캘린더가 됐다. 다음 단계에서는 사용자가 처음 요청했던 "미국 증시에 영향이 큰 주요 행사" 범위를 넓혀 CPI, PPI, 고용지표, GDP 같은 공식 macro release 일정을 같은 calendar surface에서 볼 수 있게 한다.

## Scope

- 기존 `finance_meta.market_event_calendar`를 사용한다.
- BLS 공식 release schedule에서 CPI, PPI, Employment Situation 일정을 파싱한다.
- BEA 공식 release schedule에서 national GDP 일정을 파싱한다.
- Ingestion과 Overview Events에 `Macro Calendar` refresh entry point를 추가한다.
- Overview Events에서 Macro filter와 Data Health 상태를 표시한다.
- 새 자동 refresh / scheduler는 이번 task 범위에서 제외한다.

## Done Criteria

- Macro events는 `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`, `MACRO_GDP`로 저장된다.
- Event rows는 `source_type=official`, `validation_status=official`로 저장된다.
- Overview Events에서 `Macro` 필터와 refresh button으로 확인할 수 있다.
- Data Health에 Macro Calendar target이 추가된다.
- service contract tests와 UI boundary check가 통과한다.
