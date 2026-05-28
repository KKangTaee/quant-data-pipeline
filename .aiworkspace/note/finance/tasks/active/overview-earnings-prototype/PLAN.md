# Plan

## 이걸 하는 이유?

Overview Events 탭이 FOMC뿐 아니라 종목별 실적 발표 일정도 함께 보여주려면 무료 소스 기반 earnings collector가 필요하다. 다만 Coverage 1000/2000 전체를 매번 호출하면 느리고 차단 위험이 있으므로, 첫 prototype은 작은 심볼 묶음과 최근 Market Movers 심볼을 대상으로 DB 저장 흐름을 검증한다.

## Scope

- yfinance calendar field를 이용해 upcoming earnings event row를 만든다.
- 결과는 `finance_meta.market_event_calendar`에 `event_type=EARNINGS`로 UPSERT한다.
- 수집 대상은 수동 입력 또는 latest market movers top symbols로 제한한다.
- Ingestion 화면에 earnings prototype 버튼을 추가한다.
- Overview Events 탭에서 FOMC와 earnings를 함께 읽고, earnings refresh 버튼을 활성화한다.
- OpenBB 도입, paid API, Coverage 1000/2000 전체 earnings scan은 이번 task 범위 밖이다.

## Done Criteria

- collector는 missing / failed symbols를 job result에 드러낸다.
- service read model은 FOMC와 earnings event를 같이 표시할 수 있다.
- Ingestion과 Overview가 직접 remote fetch하지 않고 job wrapper를 호출한다.
- 관련 compile, service contract tests, DB smoke, browser smoke가 통과한다.
