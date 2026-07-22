# Today Home React Workbench V2 Design

Status: Approved Visual Direction; Awaiting Written Spec Review
Last Updated: 2026-07-22

## Problem Diagnosis

V1의 [Today renderer](../../../../../../app/web/today_page.py)는 `overview_ui_css()`, `_today_css()`, `build_today_html()`을 합쳐 `st.markdown(..., unsafe_allow_html=True)`로 출력한다. 실제 경제사이클과 S&P 500은 각각 `economic_cycle_workbench`, `market_context_valuation` React/Vite component를 `streamlit.components.v1.declare_component`로 연결한다.

따라서 V1은 색상 변수 일부만 공유했을 뿐 다음 계약은 공유하지 않았다.

- component-local responsive layout과 frame height 갱신
- typed payload와 UI state 경계
- SVG axis/tooltip interaction
- 일관된 20px 전후 panel radius, hero surface, shadow depth, 내부 spacing
- React event를 통한 action handoff

## Confirmed Visual Direction

사용자는 `A. Market Context Workbench`를 선택했다.

읽기 순서는 유지한다.

```text
오늘의 시장 판단 hero
  -> 판단 근거 + 다음 일정
  -> 대표 포트폴리오 KPI + 성과곡선
  -> 다음 행동 3개
```

시각 문법은 경제사이클·S&P 500을 따른다.

- ink `#172536`, heading `#20364b`, muted `#64768a`
- line `#dbe4eb`, white surface, restrained blue-gray gradient
- hero radius 약 21~23px, panel radius 약 18~21px
- 낮은 shadow와 넓은 section gap
- desktop 2열, 760px 이하 1열
- 승인 시안의 모든 text role을 최초 A안보다 1px 확대

구현 typography token은 다음으로 고정한다.

- eyebrow / metadata: 10px
- axis / helper: 11px
- body / badge label: 12px
- evidence title: 13px
- section title / metric value: 15px
- portfolio title: 18px
- hero title: 26px

## Component Ownership

### New React Component

```text
app/web/streamlit_components/today_workbench/
  package.json
  package-lock.json
  vite.config.ts
  tsconfig.json
  index.html
  src/
    TodayWorkbench.tsx
    TodayPortfolioChart.tsx
    presentation.ts
    presentation.test.ts
    types.ts
    main.tsx
    style.css
  component_static/
```

- `TodayWorkbench.tsx`: section order와 action event 소유.
- `TodayPortfolioChart.tsx`: date-linear X scale, cumulative-return Y scale, responsive tick, hover/focus tooltip 소유.
- `presentation.ts`: 위험 라벨, chart series, ticks, tooltip placement의 pure functions 소유.
- `component_static/`: canonical Git 배포 산출물.

### Python Wrapper

`app/web/today_react_component.py`가 build availability와 `declare_component`를 소유한다.

`app/web/today_page.py`는 다음만 소유한다.

- persisted loader 호출
- Today read model 전달
- component event를 기존 Streamlit Page/query param으로 변환
- component build가 없거나 render가 불가능할 때 compact fallback 표시

기존 HTML renderer는 React primary 경로가 아니며 fallback 범위로 축소한다.

## Payload Contract

Today service는 UI가 추론하지 않도록 presentation-ready 의미를 제공한다. schema version은 호환 변경으로 갱신한다.

### Market Evidence

각 evidence row에 다음을 명시한다.

```text
signal_level: support | neutral | watch | limited
signal_label: 지지 신호 | 중립 신호 | 주의 신호 | 자료 제한/엇갈림
risk_label: 위험도 낮음 | 위험도 중간 | 위험도 높음 | 판단 제한
```

이 분류는 새로운 확률 점수나 매매 신호가 아니다. 기존 source의 status, provisional 여부, tone, 충돌 의미를 presentation category로 투영한다. React가 수치나 문장을 재해석하지 않는다.

분류 우선순위는 Python service가 다음처럼 소유한다.

1. source가 unavailable이면 `limited / 판단 제한`.
2. 경제 사이클은 canonical phase를 사용한다. `recovery/expansion`은 support, `slowdown/recession`은 watch, phase 불명은 neutral이다. publication이 partial이면 signal은 유지하되 별도 `data_quality_label=자료 제한`을 표시한다.
3. S&P 500은 multiple bucket을 사용한다. `VERY_HIGH/HIGH`는 watch, `MID/NEUTRAL`은 neutral, `LOW/VERY_LOW`는 support다. provisional EPS 여부는 별도 data-quality label로 표시한다.
4. Futures Macro와 Sentiment는 기존 canonical tone을 사용한다. positive/support는 support, warning/negative/danger/burden은 watch, neutral/mixed는 neutral이다. stale/missing/partial이면 별도 data-quality label을 표시한다.
5. source 의미가 충돌하거나 tone을 해석할 수 없으면 임의로 낮음/높음을 만들지 않고 `limited / 판단 제한`으로 둔다.

`signal_level`과 `risk_label`은 source별 화면 분류이며 Today 전체의 종합 위험 점수가 아니다. data readiness는 `data_quality_label`로 분리해 위험 의미와 섞지 않는다.

### Portfolio Curve

V1의 `{date, value}`만으로는 `value`의 의미와 좌표를 알 수 없다. V2 row는 다음을 제공한다.

```text
date
unit_value
total_value
cumulative_return
```

chart metadata는 다음을 제공한다.

```text
interval: daily
price_basis: stored_close
aggregation: none
intraday: false
observation_count
start_date
end_date
```

최근 60개 저장 관측이라는 기존 범위는 유지한다. 주봉으로 재집계하거나 장중 데이터를 합성하지 않는다. synthetic point를 추가하지 않는다.

### Recent Return

현재 `day_return`은 최신 두 unit-value 관측의 변화다. UI에서는 `오늘`이라고 부르지 않는다.

```text
latest_observation_return
return_from_date
return_to_date
```

표시는 `최근 거래일 수익률`과 `MM.DD → MM.DD`로 한다. 두 관측이 없으면 0%를 만들지 않고 `계산 자료 부족`으로 표시한다.

## Evidence Risk Presentation

판단 근거 카드의 좌측 색상선은 제거한다. 모든 카드는 같은 neutral border와 surface를 사용한다.

- 카드 상단: source label + explicit signal pill
- 카드 본문: 현재 결론 + 근거 설명
- 카드 하단: risk label + as-of date
- 색상은 라벨을 보조할 뿐 단독 의미로 사용하지 않는다.

기본 color mapping:

- support: green text / pale green background
- neutral: blue-gray text / pale blue background
- watch: amber text / pale amber background
- limited: muted violet-gray text / pale violet-gray background

## Portfolio Chart Design

### Meaning

그래프 제목은 `일별 종가 기반 누적 수익률`이다. subtitle은 `입출금 영향을 조정한 포트폴리오 단위가치의 변화`라고 설명한다.

header chip은 다음 세 개다.

- `주기 · 일별`
- `최근 N관측`
- `장중 아님`

footer에는 `주봉 변환 없음 · 장중 데이터 없음`을 명시한다.

### X Axis

- 실제 ISO date를 epoch time으로 변환한 date-linear scale을 사용한다.
- desktop 최대 5개, narrow 최대 3개 tick을 표시한다.
- tick label은 `MM.DD`, range는 footer에 `YYYY.MM.DD–YYYY.MM.DD`로 표시한다.
- 누락 날짜를 synthetic observation으로 채우지 않는다.

### Y Axis

- `cumulative_return = unit_value - 1`을 percent scale로 표시한다.
- 데이터 범위 기반 padding을 적용하되 0%가 의미 있는 범위에 있으면 zero baseline을 표시한다.
- tick은 사람이 읽기 좋은 간격으로 생성하고 단위 `%`를 축 제목에 명시한다.
- 투자금 입출금으로 왜곡될 수 있는 total value를 primary line으로 사용하지 않는다.

### Tooltip And Accessibility

hover와 keyboard focus에서 다음을 표시한다.

- exact date
- cumulative return
- total portfolio value
- `저장 종가 기준`

SVG `aria-label`은 전체 기간과 일별 종가 기반임을 포함한다. 색상과 hover에만 의존하지 않고 point focus와 `<title>` fallback을 둔다.

## Navigation Events

React action은 다음 event만 반환한다.

```text
open_market_research
open_stock_research
open_portfolio_monitoring
```

Python page가 기존 Page object와 query param 계약을 이용해 이동한다. React에 URL 문자열을 중복 저장하지 않는다.

## Error And Fallback

- 일부 source 실패: 해당 evidence만 limited로 표시하고 나머지 section 유지.
- curve 2개 미만: chart 대신 `성과 추이를 표시할 관측치가 부족합니다`와 metadata 표시.
- total value 일부 없음: line은 cumulative return으로 유지하고 tooltip 평가액만 `자료 없음`.
- component build 없음: compact fallback과 `상세 화면을 불러오지 못했습니다` 안내를 표시하되 provider fetch나 write를 실행하지 않음.
- render 중 portfolio group 생성, registry write, monitoring log write를 하지 않음.

## Verification Contract

### RED/GREEN Automated

- Python: chart metadata, row meaning, latest-observation return date contract
- Python: signal/risk label projection and partial/unavailable semantics
- Python: component availability, event routing, explicit fallback
- Frontend: date-linear coordinate, responsive ticks, percent axis ticks, tooltip payload
- Frontend: evidence label mapping and no left-border presentation class
- Frontend: typecheck, Vitest, Vite build
- Regression: Today read-only and existing navigation/reference contracts

### Browser QA

- actual root `/`에서 React iframe/component가 primary renderer인지 확인
- desktop, 760px, 420px layout과 horizontal overflow 확인
- text scale, risk labels, graph axis labels, chips, tooltip, keyboard focus 확인
- `최근 거래일 수익률`의 from/to date와 basis date 확인
- 세 action route와 browser console 확인
- 최종 QA screenshot 한 장 생성하되 generated artifact로 커밋하지 않음

## Tradeoffs

- 별도 component bundle이 하나 늘지만 기존 시장맥락과 동일한 ownership과 QA 경계를 얻는다.
- 누적 수익률을 primary line으로 사용하므로 KPI의 현재 평가액과 선의 Y값이 다른 단위다. chart title, axis, tooltip에서 두 단위를 명확히 분리한다.
- date-linear X축은 휴장일과 데이터 gap을 실제 시간 간격으로 보인다. synthetic point를 만들지 않는 대신 관측 간격이 고르지 않을 수 있다.
