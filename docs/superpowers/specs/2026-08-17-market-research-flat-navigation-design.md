# Market Research Flat Navigation Design

Status: Approved
Date: 2026-08-17

## Follow-up Approval

같은 날 승인된 후속 변경이 초기 모바일 one-line/swipe 계약을 대체한다. 모바일도
desktop과 같은 family underline·view pill 스타일을 유지하고, 좁은 폭에서는 자연스럽게
줄바꿈한다. 별도 mobile-only nowrap, horizontal swipe와 강제 active-tab scroll은 사용하지 않는다.

## 이걸 하는 이유?

현재 `시장 환경 > 경제 사이클 > 경기 국면 | 물가·정책 경로`만 다른 Market Research 화면보다 한 단계 깊다. 사용자는 경기와 물가·정책이라는 서로 다른 질문을 확인하려는데, `경제 사이클`이라는 중간 분류를 한 번 더 통과해야 한다. 모바일에서는 하위 화면이 2열 큰 버튼으로 바뀌어 탐색이 본문보다 더 많은 공간을 차지한다.

이번 변경은 경기 국면과 물가·정책을 다른 시장 환경 화면과 같은 깊이로 올리고, 모바일 탐색도 desktop과 같은 compact rail로 유지해 사용자가 본문에 더 빨리 도달하게 한다.

## Approved Information Architecture

```text
Market Research
  시장 환경
    경기 국면
    물가·정책
    선물 매크로
    심리
    일정
  지수 가치평가
    S&P 500
  종목 리서치
    변동 종목
    개별 종목
```

- 사용자에게 보이는 `경제 사이클` navigation label은 `경기 국면`으로 바꾼다.
- `물가·정책`을 canonical Market Research view로 추가한다.
- 기존 `economic-cycle` slug, loader, service, payload schema는 경기 국면의 호환 식별자로 유지한다.
- `inflation-policy` slug는 같은 DB-backed transport를 사용하지만 처음부터 물가·정책 본문을 연다.
- 경제사이클 workbench 내부의 `경기 국면 | 물가·정책 경로` 중복 탭은 제거한다.

## Visual Contract

### Desktop and Tablet

- page header는 기존 `RESEARCH WORKSPACE / Market Research / description`을 유지한다.
- family는 배경 없는 editorial text rail과 선택 underline을 사용한다.
- view는 content-width compact rail로 표시하고 선택 view만 quiet filled state로 강조한다.
- 별도 card, drawer, diagnostic panel은 추가하지 않는다.

### Mobile

- family rail은 desktop과 같은 editorial text·underline 스타일을 유지한다.
- view rail은 2열 grid나 full-width button을 사용하지 않는다.
- view는 desktop과 같은 compact pill, padding과 gap을 사용한다.
- 좁은 폭에서는 family와 view rail이 자연스럽게 줄바꿈하며 horizontal swipe를 만들지 않는다.
- page와 rail은 viewport보다 넓어지지 않는다.
- tab rail은 sticky/fixed가 아니며 본문을 덮지 않는다.

## Runtime And State Contract

```text
overview_tab=economic-cycle
  -> render_economic_cycle(selected_view="cycle")
  -> economic-cycle component args.selected_view="cycle"
  -> 경기 국면 본문

overview_tab=inflation-policy
  -> render_economic_cycle(selected_view="inflation")
  -> economic-cycle component args.selected_view="inflation"
  -> 물가·정책 본문
```

- Python이 canonical URL/session state와 selected renderer를 계속 소유한다.
- React navigation은 payload를 표시하고 `select_view` event만 반환한다.
- economic-cycle React component는 전달받은 `selected_view`만 렌더링하며 별도 local selection state를 만들지 않는다.
- invalid selected view는 `cycle`로 정규화한다.
- 물가·정책 payload가 없으면 기존 제한/empty 표현을 사용하며 경기 국면으로 자동 이동하지 않는다.
- provider fetch, DB write, refresh semantics, inflation-policy command contract는 변경하지 않는다.

## Fallback Contract

- React navigation bundle이 없을 때 Streamlit fallback도 다섯 시장 환경 view를 노출한다.
- fallback의 모바일 view control 역시 2열 stretch grid를 사용하지 않는다.
- economic-cycle component bundle이 없을 때 Python fallback은 canonical view에 따라 경기 국면 또는 물가·정책 본문 하나만 렌더링한다.

## Files

- `app/web/overview/navigation.py`: canonical `inflation-policy` view, labels, family mapping, fallback mobile rail
- `app/web/overview/page.py`: 경기 국면과 물가·정책 renderer dispatch
- `app/web/overview/market_context_helpers.py`: selected analysis view normalization and fallback routing
- `app/web/overview/economic_cycle_react_component.py`: selected view bridge argument
- `app/web/streamlit_components/market_research_navigation/`: five-view navigation payload fixtures and desktop-parity responsive CSS
- `app/web/streamlit_components/economic_cycle_workbench/`: controlled selected view and duplicate inner navigation removal
- focused Python/React tests and production bundles

## Verification

- Python navigation mapping, payload, event, renderer dispatch and bridge tests
- Market Research React navigation tests with five market-environment views
- Economic Cycle React tests proving cycle and inflation views open directly without an inner tablist
- TypeScript typecheck, Vitest, Vite production builds
- Python focused tests, `py_compile`, `git diff --check`
- Browser QA at desktop, 736px and 360px: selected state, desktop-parity wrapping, horizontal overflow boundary, both direct routes, zero console errors

## Non-goals

- 경기/물가 계산, 확률, 데이터 수집, 검증 기준 변경
- module body redesign
- sticky navigation or drawer
- global freshness/run/job/status panel
- route migration away from `/overview`
