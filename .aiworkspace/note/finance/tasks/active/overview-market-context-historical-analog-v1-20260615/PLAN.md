# Overview Market Context Historical Analog V1 Plan

## 이걸 하는 이유?

`Overview > Market Context`는 현재 시장 브리프를 읽기 쉬워졌지만, 사용자는 현재 leadership sector와 비슷했던 과거 맥락에서 주요 자산이 이후 어떻게 움직였는지도 참고하고 싶다.
이번 4차는 미래 예측이나 매수/매도 신호가 아니라, `Sector Leadership -> Sector ETF Proxy -> Historical Analog` 흐름의 context-only MVP를 만든다.

## 전체 흐름

- 1차 완료: Market Context를 가이드/카드 중심 구조에서 시장 브리프 흐름으로 재배치했다.
- 2차 완료: 보조 갱신 후 상단 Market Context가 최신 snapshot을 다시 읽도록 cache/rerun UX를 보정했다.
- 3차 완료: CPI/Event coverage, recent + upcoming event read model, Macro Calendar 신뢰도, Data Health 전면화 완화를 개선했다.
- 4차 현재: 현재 leadership sector를 sector ETF proxy에 연결하고, DB 가격 coverage가 충분한 proxy에 한해 과거 유사 맥락 이후 5D/20D/60D 주요 자산 흐름을 작게 보여준다.
- 후속: sector ETF coverage 확장, macro/futures/event regime 조건 추가, CPI/FOMC 전후 analog 확장, sample quality / PIT / survivorship 보강.

## 4차 Scope

- GICS sector -> 대표 sector ETF map을 Streamlit-free helper로 둔다.
- `finance_price.nyse_price_history`에 sector ETF와 benchmark ETF coverage가 있는지 점검한다.
- 현재 Market Context leadership sector 또는 top group을 sector ETF proxy로 resolve한다.
- coverage가 부족하면 분석을 억지로 만들지 않고 `INSUFFICIENT_DATA` 또는 `REVIEW` 상태와 이유를 반환한다.
- coverage가 충분하면 sector ETF의 최근 5D/20D SPY 대비 상대강도와 유사했던 과거 anchor를 찾는다.
- anchor 이후 5D/20D/60D forward return을 주요 자산별로 요약한다.
- Market Context 화면에 `과거 유사 맥락 참고` 섹션을 compact table / inline summary로 추가한다.
- 모든 문구는 context-only로 유지하고 예측, 추천, 매수/매도, 신호, validation gate처럼 보이지 않게 한다.

## Out Of Scope

- Consumer Defensive/XLP 전용 하드코딩.
- 머신러닝 모델, 예측 점수, 매수/매도 신호.
- Backtest strategy, Practical Validation gate, Final Review decision, Operations monitoring signal 연결.
- DB schema 변경, 새 provider 추가, registry/saved JSONL write.
- full sector universe historical PIT 보정.
- generated artifact staging.

## TDD Plan

1. sector ETF map helper 테스트를 먼저 작성한다.
2. price coverage helper가 시작일, 종료일, row 수, coverage 상태를 요약하는지 테스트한다.
3. leadership sector -> ETF proxy resolve 테스트를 작성한다.
4. coverage 부족 시 `INSUFFICIENT_DATA` 또는 `REVIEW`를 반환하는 테스트를 작성한다.
5. relative strength anchor와 forward return 계산이 anchor 이후 데이터만 쓰는지 테스트한다.
6. UI/read model 문구가 예측/추천/신호 언어를 만들지 않는지 테스트한다.
7. RED 확인 후 최소 구현으로 GREEN을 만든다.

## Completion Conditions

- Sector Leadership -> Sector ETF Proxy -> Historical Analog 구조가 generic map 기반으로 동작한다.
- local DB coverage 점검 결과와 부족 상태가 task 기록과 UI/read model에 명확히 남는다.
- 현재 leadership sector와 proxy ETF가 표시된다.
- 5D/20D/60D 주요 자산 forward return 요약이 context-only로 표시된다.
- focused tests 또는 환경 제약 시 대체 검증, py_compile, diff check, Streamlit Browser QA가 수행된다.
- coherent commit을 만든다.
