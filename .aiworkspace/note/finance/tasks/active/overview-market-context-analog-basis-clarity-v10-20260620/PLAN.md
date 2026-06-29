# Overview Market Context Analog Basis Clarity V10

Status: Active
Started: 2026-06-20

## 이걸 하는 이유?

`Workspace > Overview > Market Context`의 `참고: 과거 유사 맥락`에서 사용자가 기준일을 바꿔도 계산 기준일이 `2026-05-29`처럼 고정되어 보인다. 실제로는 선택일이 서비스에 전달되지만, sector ETF / SPY / comparison asset 공통 daily price coverage가 더 오래된 날짜에서 끊기면 계산이 그 날짜로 내려간다. 현재 UI는 이 차이를 설명하지 않아 사용자가 선택 기준일이 무시된 것으로 이해한다.

Macro 조건 포함 비교도 broad sample을 GLD / futures 조건으로 좁히는 구조인데, 사용 조건 / preview / 제외 조건이 개발자 용어로 나열되어 처음 읽는 사용자가 표본이 어떻게 바뀌었는지 파악하기 어렵다.

## Scope

- Historical analog service model에 요청 기준일, 실제 계산 기준일, 자료 최종일, fallback 이유를 명시한다.
- 선택 기준일이 실제 계산 기준일과 다를 때 UI에서 이를 숨기지 않고 설명한다.
- `참고: 과거 유사 맥락`의 기준 / 패턴 / 표본 / 한계 정보를 사용자 흐름 중심으로 재배치한다.
- `Macro 조건 포함 비교`에서 broad sample → GLD 조건 → futures 조건 funnel을 명확히 보여준다.
- FRED / Events / Sentiment는 hard condition이 아니라 preview / annotation / deferred로 유지한다.

## Out Of Scope

- 새 provider / DB schema / loader / persistence path 추가
- UI render 중 direct provider / FRED fetch
- registry / saved JSONL write
- Backtest / Practical Validation / Final Review / Operations core logic 연결
- trading action, prediction guarantee, recommendation, validation gate, monitoring signal
- full PIT sector universe / historical sector membership storage

## Done When

- 선택 기준일이 6/18이고 common price matrix가 5/29까지만 있을 때, UI가 요청일과 실제 계산일 차이를 명확히 표시한다.
- 선택일이 적용 가능한 경우에는 실제 계산 기준일이 선택일과 일치한다.
- Macro 조건 포함 비교는 broad sample을 숨기지 않고 sample reduction과 조건 역할을 사용자 언어로 설명한다.
- Focused service contract tests, compile checks, Browser QA가 완료된다.
