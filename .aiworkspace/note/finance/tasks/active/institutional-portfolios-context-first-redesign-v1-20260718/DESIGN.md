# Institutional Portfolios Context-First Redesign V1 Design

Status: Proposed For User Review
Last Updated: 2026-07-18

## Agreed Product Intent

첫 화면의 주인공은 manager directory가 아니라 `선택 기관의 포트폴리오 맥락 이해`다.

사용자는 이 화면에서 다음 질문에 순서대로 답을 얻어야 한다.

1. 지금 어떤 기관과 어느 보고 분기를 보고 있는가.
2. 이 포트폴리오는 무엇에 집중되어 있고 자료는 얼마나 연결되어 있는가.
3. 이전 분기와 실제로 비교할 수 있는가.
4. 전체 보유 종목을 누락 없이 어떻게 찾는가.
5. 특정 종목의 가격 흐름과 다른 보유 기관을 어떻게 확인하는가.
6. 어떤 내용이 13F 지연 / mapping / 가격 coverage 한계에 의해 제한되는가.

이 화면은 delayed SEC Form 13F research context이며 추천, 현재 매수 / 매도 의도, live approval, broker action을 만들지 않는다.

## Approaches Considered

### A. Selected-Manager Context First — Chosen

- 선택 기관을 headline으로 두고 concentration, sector, mapping coverage, comparison readiness를 먼저 설명한다.
- manager search / favorites는 기관 전환 도구로 낮춘다.
- 전체 보유와 종목 분석은 context를 읽은 다음 이어지는 task flow로 둔다.
- 장점: Overview `시장 맥락`과 같은 결론-근거-세부 순서이며 사용자의 판단 부담이 가장 작다.
- tradeoff: 여러 기관을 한 화면에서 비교하는 기능은 첫 화면의 주인공이 아니다.

### B. Manager Explorer First — Rejected For Default

- 기관 목록과 검색 결과를 넓게 두고 선택 후 상세로 들어간다.
- 장점: manager discovery에는 유리하다.
- 단점: 현재 horizontal rail의 문제를 확대하고 선택 기관의 맥락이 다시 아래로 밀린다.

### C. Dense Comparison Dashboard — Parked

- 여러 기관의 concentration, sector, turnover를 동시에 비교한다.
- 장점: 비교 research에는 유용하다.
- 단점: multi-quarter history와 reliable mapping이 먼저 필요하고 현재 데이터 coverage로는 오해가 크다.

## Target User Flow

```text
Institutional Portfolios
  -> 기관 검색 / 즐겨찾기에서 manager 선택
  -> 선택 기관 context hero
  -> 포트폴리오 맥락
       -> allocation / concentration
       -> 실제 비교 가능한 경우에만 분기 변화
       -> sector / mapping coverage
       -> 참고: 보고 기준일 이후 단순 가정 성과
  -> 전체 보유 탐색
       -> 검색 / filter / sort / page
       -> mapped / unmapped row 모두 표시
  -> 종목 중심
       -> ticker / issuer / CUSIP 직접 검색
       -> 선택 기관 내 위치
       -> 저장 가격 chart
       -> 최신 filing 기준 보유 기관 list
  -> 자료 기준 / 13F 한계
```

## Visual And Information Architecture

### Page Header

- 기존 Streamlit page title과 긴 설명을 compact하게 줄인다.
- 상단은 Overview와 같은 dark shell / clear page title / short purpose copy를 유지한다.
- manager search는 page hero와 분리된 거대한 input이 아니라 manager switcher의 일부로 보인다.

### Manager Switcher

- 첫 상태에는 curated favorite managers만 compact하게 보여준다.
- 전체 manager는 검색으로 찾으며 결과 개수와 표시 범위를 공개한다.
- 긴 SEC filer name은 잘린 rail만 보여주지 않고 investor alias와 filer name을 함께 읽을 수 있게 한다.
- generic manager 24개를 default rail에 섞지 않는다.
- manager 선택은 payload rerun을 일으키지만 현재 page scroll과 선택 section을 가능한 범위에서 보존한다.

### Context Hero

Overview economic-cycle hero의 문법을 차용한다.

- eyebrow: `INSTITUTIONAL PORTFOLIO CONTEXT`.
- headline: 선택 manager 이름.
- summary: data-backed 한 문장 포트폴리오 맥락.
  - 상위 보유 집중도.
  - 가장 큰 mapped sector.
  - symbol mapping coverage.
  - 이전 분기 비교 가능 여부.
- summary는 위 필드의 deterministic formatter로 만들며 생성형 해석이나 임의 점수를 사용하지 않는다.
- basis block:
  - 보고 기준 분기.
  - 제출일.
  - 저장 snapshot 기준일.
  - SEC 원문.
- summary는 현재 거래 의도나 추천을 표현하지 않는다.

### Navigation

기존 2단 IA 의미는 유지하되 Overview의 얇은 underline tab 문법으로 단순화한다.

- 상위: `기관 포트폴리오 | 종목 중심`.
- 기관 포트폴리오 하위: `포트폴리오 맥락 | 전체 보유`.
- 종목 중심 하위: `종목 상세 | 기관 보유 랭킹`.
- manager switcher, primary tab, secondary tab이 모두 강한 card/button으로 경쟁하지 않게 visual weight를 단계별로 낮춘다.

### Portfolio Context Reading Order

1. `포트폴리오 구성`
   - allocation donut은 유지한다.
   - top holdings list와 top 5 concentration을 함께 보여준다.
   - `Other`가 몇 종목 / 몇 %인지 공개한다.
2. `분기 보고 변화`
   - previous comparable filing이 있을 때만 신규 / 증가 / 감소 / 미보고를 보여준다.
   - previous filing이 없으면 변화 수치 전체를 숨기고 `비교할 이전 분기가 저장되어 있지 않음` state만 보여준다.
3. `노출과 자료 연결 범위`
   - sector exposure.
   - mapped holding count / total count.
   - mapped reported-value weight.
   - unresolved / ambiguous count.
4. `참고: 보고 기준일 이후 단순 가정 성과`
   - current top-level headline에서 supporting section으로 낮춘다.
   - return 숫자와 `계산 가능 평가액 비중`을 항상 같은 문장 / header에서 읽게 한다.
   - 실제 현재 보유, manager actual performance, 추천으로 표현하지 않는다.

## Complete Holdings Explorer Contract

### No Silent Truncation

- `rows.slice(0, 80)` 같은 display-only hard cut을 제거한다.
- V1은 현재 payload가 이미 전달하는 모든 prepared holding row를 유지하고 React client-side search / filter / pagination에 사용한다.
- DOM performance를 위해 기본 50개 page를 사용한다.
- 항상 `1–50 / 993` 같은 visible range와 total count를 보여준다.
- page size는 50으로 고정해 먼저 검증하고, 별도 page-size 선택 control은 추가하지 않는다.

### Search / Filter / Sort

- search targets: ticker, issuer name, CUSIP.
- filters:
  - 전체.
  - ticker 연결됨.
  - ticker 미연결 / mapping 확인 필요.
  - sector.
- sort:
  - portfolio weight descending — default.
  - reported value descending.
  - issuer name ascending.
- search / filter / sort / page 전환은 client-side state로 처리하며 Streamlit rerun을 만들지 않는다.

### Row Semantics

- mapped row: ticker, issuer, weight, value, sector, mapping state.
- unmapped row: issuer와 CUSIP을 primary identity로 유지하고 `ticker 연결 전` badge를 표시한다.
- unmapped는 13F holding 부재가 아니며 row를 숨기지 않는다.
- mapped row click은 종목 상세로 이동한다.
- unmapped row click은 chart가 없는 identity detail을 열고, 가격 수집 action 대신 mapping limitation을 설명한다.

## Security-Centric Flow

- React primary surface 안에 ticker / issuer / CUSIP 직접 검색을 둔다.
- 입력 중 자동 provider / DB query를 반복하지 않는다. Enter 또는 명시 검색 action으로 event를 보낸다.
- 검색 결과는 latest stored filings 기준 holder list와 선택 기관 내 portfolio position을 분리한다.
- 현재 custom line / candle chart, daily / weekly / monthly, volume / navigator는 유지한다.
- chart empty state는 다음을 구분한다.
  - ticker mapping 없음.
  - mapping ambiguous.
  - ticker는 있으나 저장 가격 없음.
  - 저장 가격 ready.
- `기관 보유 랭킹`은 lazy load를 유지하되 직접 검색의 대체재로 사용하지 않는다.

## Read-Model And Payload Contract

React payload는 `institutional_portfolios_workbench_v2`로 명시적으로 올린다.

### New / Strengthened Fields

- `context_summary`
  - `headline`.
  - `summary`.
  - `top5_weight_pct` / label.
  - `largest_sector` / weight label.
  - `comparison_state`.
- `coverage`
  - `holding_count_total`.
  - `holding_count_mapped`.
  - `holding_count_unmapped`.
  - `holding_count_ambiguous`.
  - `mapped_weight_pct` / label.
  - `performance_covered_weight_pct` / label.
- `holdings_explorer`
  - full logical row set.
  - supported filters / sort metadata.
  - default page size.
- `security_search`
  - current query.
  - state.
  - explicit submit event contract.

### Change Board Correctness

- `comparison_available=False`이면 user-facing change groups는 빈 목록 또는 unpublished 상태여야 한다.
- 이전 분기 없는 최신 holding을 `신규 보고`로 사용자에게 노출하지 않는다.
- 내부 compatibility 계산이 row를 `reported_new`로 만들더라도 UI payload gate가 이를 차단한다.

### Coverage Semantics

- mapping coverage와 price performance coverage를 같은 값으로 취급하지 않는다.
- count coverage는 `몇 종목을 ticker로 연결했는가`를 말한다.
- value coverage는 `전체 보고 평가액 중 ticker 연결 비중`을 말한다.
- performance coverage는 `보고 기준일 이후 가격 계산에 포함된 평가액 비중`을 말한다.

## Streamlit / Event Boundary

- `app/web/institutional_portfolios.py`는 manager search / selection, explicit security search, lazy popularity, explicit price collection event만 처리한다.
- render 중 SEC / provider 직접 fetch를 추가하지 않는다.
- manager selection / security selection / price collection event id를 구분한다.
- React local search/filter/page state는 Streamlit session state에 저장하지 않는다.
- SEC 13F refresh expander는 secondary action으로 유지하며 context hero 안에 run/job result panel을 추가하지 않는다.

## Empty And Error States

- DB empty: preview임을 명확히 표시하되 current holdings처럼 보이지 않는다.
- manager not found: query와 결과 0을 보여주고 default manager로 조용히 이동하지 않는다.
- previous filing missing: comparison unavailable state.
- all holdings unmapped: allocation은 issuer/CUSIP로 유지하고 sector/chart limitation을 별도로 설명한다.
- price missing: mapping 문제와 구분하고 explicit selected-symbol price collection만 허용한다.
- large manager: total, visible range, current filters를 항상 표시한다.

## Responsive Contract

- desktop: context hero 2-column, portfolio context section 2-column where comparison is meaningful.
- 420px:
  - hero 1-column.
  - manager switcher search first, favorite managers horizontal scroll.
  - primary / secondary tabs wrap하지 않고 horizontal scroll 또는 compact fit.
  - holdings filter와 row는 1-column reading order.
  - ticker / issuer / weight는 유지하고 value / sector는 secondary line으로 내린다.
- page-level horizontal overflow는 허용하지 않는다.

## File Ownership

- `app/services/institutional_portfolios.py`
  - context summary, coverage, comparison gate, v2 payload.
- `app/web/institutional_portfolios.py`
  - Streamlit shell and explicit event state.
- `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`
  - target IA, holdings explorer state, security search, visual render.
- `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
  - Overview-aligned tokens, responsive layout.
- `tests/test_institutional_portfolios.py`
  - service, source contract, event, no-truncation regression.
- `finance/loaders/institutional_13f.py`
  - no first-slice change expected. Only change if implementation proves loader metadata is insufficient.

## Validation Contract

### Focused Tests

- Bridgewater-like 993 holding fixture가 payload full logical rows를 유지한다.
- React source에 `rows.slice(0, 80)` hard cut이 없다.
- default page `1–50 / 993`, search / filter / sort 결과 total이 정확하다.
- previous filing 없음이면 change counts / items를 user-facing으로 publish하지 않는다.
- count mapping coverage, value mapping coverage, performance coverage가 분리된다.
- primary React surface에 explicit security search가 존재한다.
- unmapped row는 숨겨지지 않고 price action이 비활성이다.
- existing manager select / drilldown / popularity / price collection event contracts를 보존한다.

### Commands / QA

- `tests.test_institutional_portfolios` focused suite.
- touched Python `py_compile`.
- Institutional Portfolios React `npm run build`.
- `git diff --check`.
- UI / engine boundary check.
- actual DB smoke:
  - Berkshire: mixed mapped / unmapped, high value coverage.
  - Bridgewater: 993 logical holdings, pagination / search / low coverage.
  - Duquesne: mapping coverage가 낮아도 issuer / CUSIP 전체 탐색 가능.
- Browser QA:
  - desktop.
  - 420px.
  - manager switch, all holdings page, direct security search, mapped chart, unmapped detail.
  - screenshot 1장 이상은 generated artifact로 남기고 commit하지 않는다.

## Tradeoffs And Deferred Decisions

- pagination을 사용해 993개 row를 한 번에 DOM에 넣지 않는다.
- manager comparison은 선택 기관 맥락을 약화시키므로 이번 default flow에서 제외한다.
- 실제 quarter-over-quarter 분석을 살리려면 historical SEC quarter 저장이 필요하지만, 이번 UI implementation이 자동 backfill을 실행하지 않는다.
- mapping quality를 UI copy만으로 해결하지 않는다. unresolved는 visible evidence로 남기며 security master 도입은 별도 data task다.
- 그래프는 현재 강점이므로 chart library 교체보다 context와 discoverability를 먼저 개선한다.
