# Market Research React Navigation V1 Design

Status: Approved
Last Updated: 2026-07-22

## User-Approved Direction

사용자는 `RESEARCH WORKSPACE + Market Research 제목 + 설명 + 1차 family + 2차 view` 전체를 하나의 React component로 전환하는 A안을 승인했다.

## Architecture

`app/web/overview/navigation.py`는 계속 canonical state owner다. query, widget/session compatibility, legacy slug normalization, renderer dispatch는 Python에 남긴다. 새 wrapper `app/web/overview/market_research_navigation_react_component.py`는 static bundle availability와 component declaration만 소유한다.

React source는 `app/web/streamlit_components/market_research_navigation/`에 둔다. component는 전달받은 payload만 렌더링하고 클릭 시 작은 event envelope만 반환한다. provider fetch, DB read/write, route 계산은 하지 않는다.

```text
Python current_view
  -> navigation payload { active_view, active_family, families, views }
  -> MarketResearchNavigation React
  -> { event: { id: "select_view", view, nonce } }
  -> Python allowlist validation
  -> session state + overview_tab query
  -> selected renderer only
```

## Python Contract

Payload schema version은 `market_research_navigation_v1`이다.

```python
{
    "schema_version": "market_research_navigation_v1",
    "eyebrow": "RESEARCH WORKSPACE",
    "title": "Market Research",
    "description": "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.",
    "active_family": "market-environment",
    "active_view": "economic-cycle",
    "families": [
        {
            "id": "market-environment",
            "label": "시장 환경",
            "description": "경제·매크로·심리·일정",
            "views": [
                {"id": "economic-cycle", "label": "경제 사이클"},
                {"id": "futures-macro", "label": "선물 매크로"},
                {"id": "sentiment", "label": "심리"},
                {"id": "events", "label": "일정"},
            ],
        },
        {
            "id": "index-valuation",
            "label": "지수 가치평가",
            "description": "대표지수 멀티플과 실적",
            "views": [{"id": "sp500", "label": "S&P 500"}],
        },
        {
            "id": "stock-research",
            "label": "종목 리서치",
            "description": "변동 종목과 개별 기업",
            "views": [
                {"id": "market-movers", "label": "변동 종목"},
                {"id": "us-stock", "label": "개별 종목"},
            ],
        },
    ],
}
```

React event는 `{ "event": { "id": "select_view", "view": <canonical>, "nonce": <number> } }`다. Python은 event id와 `MARKET_RESEARCH_VIEW_OPTIONS` allowlist를 모두 검증한다. 잘못된 event는 current view를 유지한다.

현재 선택된 family를 다시 누르면 event를 보내지 않는다. 다른 family를 누르면 Python과 동일한 family default view를 event로 보낸다. URL에는 view slug만 저장하므로 기존 deep link 형식은 바뀌지 않는다.

## Visual Design

상단은 iframe 안의 하나의 투명 React surface로 렌더링한다.

- Header: 작은 uppercase eyebrow, 큰 page title, 한 줄 description
- Family rail: 세 개의 equal-purpose item. label과 짧은 목적 설명을 함께 표시한다.
- Selected family: blue-gray background, stronger label, 하단/좌측 indicator와 `aria-pressed=true`
- Local view rail: 선택 family 이름을 반복하지 않고 해당 family의 view만 compact chips로 표시한다.
- Desktop: content-width family rail과 view chips, 과도한 full-width button appearance 금지
- 760px: family 설명을 유지하되 간격 축소
- 420px: family 3열, view 2열. family 목적 설명은 screen-reader text로 유지하되 시각적으로 숨겨 label 밀도를 확보한다. horizontal scroll과 clipping은 금지한다.
- Motion: hover/focus transition 140~180ms, `prefers-reduced-motion`에서는 제거
- Theme: destructive red 금지. blue-gray neutral palette와 명암/weight/indicator를 함께 사용한다.

## Accessibility

- title은 실제 `<h1>`이다.
- family group은 `aria-label="리서치 목적"`, family button은 `aria-pressed`를 가진다.
- view group은 `aria-label="세부 리서치"`, active view는 `aria-current="page"`를 가진다.
- 모든 control은 native `<button type="button">`이고 `:focus-visible` outline을 제공한다.
- color만으로 selected state를 표현하지 않는다.

## Frame And Fallback

React root는 `ResizeObserver`와 `Streamlit.setFrameHeight()`로 높이를 맞춘다. payload/width 변경 시 즉시, animation frame, short timeout에서 높이를 다시 전달한다.

static bundle의 `index.html`이 없으면 `page.py`가 현재 semantic HTML header를, `_render_market_research_selector`가 현재 Streamlit family/view controls를 fallback으로 렌더링한다. component가 반환한 값이 dict가 아니거나 event가 invalid여도 current view를 유지한다. fallback은 배포 안전장치이며 primary presentation이 아니다.

## File Ownership

- Create `app/web/overview/market_research_navigation_react_component.py`: component availability/declaration/render wrapper
- Create `app/web/streamlit_components/market_research_navigation/`: React/Vite source, tests, canonical `component_static`
- Modify `app/web/overview/navigation.py`: payload builder, event resolver, React-first selector with fallback
- Modify `app/web/overview/page.py`: React bundle이 있을 때 Streamlit header를 생략하고, bundle이 없을 때만 현재 semantic HTML header를 fallback으로 렌더링
- Modify `tests/test_market_research_navigation.py`: payload/event/fallback/page shell contracts

## Testing

- Python: payload completeness, active family/view normalization, valid/invalid event resolution, React-first/fallback routing, legacy query/session preservation
- React/Vitest: header semantics, family selection event, view selection event, `aria-pressed`, `aria-current`, missing payload state
- Static: typecheck, test, production build, committed `component_static`
- Browser: all three families, all seven views, URL updates, module lazy render, 1280/760/420 overflow, keyboard focus, frame height, console errors

## Tradeoffs

- 별도 iframe/component bundle이 하나 늘지만 page/module 결합을 만들지 않고 독립 배포·fallback이 가능하다.
- Python rerun을 통해 view를 전환하므로 React 내부 SPA 전환보다 짧은 rerender가 있지만, canonical URL/session state와 기존 renderer 계약을 보존하는 이점이 더 크다.
- Streamlit fallback을 유지하므로 CSS 계약을 완전히 삭제하지는 않지만 primary visual 품질은 native widget DOM에서 분리된다.
