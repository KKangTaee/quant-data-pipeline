# Institutional Portfolios Manager Rail Visibility Design

Status: Approved
Date: 2026-07-18

## 이걸 하는 이유?

Context-First hero와 controls의 열 경계는 정렬됐지만, manager rail은 여전히 `flex + 고정 최소 너비 + overflow-x` 조합을 사용한다.
그 결과 rail 너비가 카드 너비의 정수 배가 아닐 때 다음 카드가 경계에서 반만 노출된다.
카드 내부의 investor alias와 SEC filer name도 `white-space: nowrap`과 `text-overflow: ellipsis`로 강제 축약돼, 의도된 가로 탐색보다 레이아웃이 잘린 것처럼 보인다.

이번 보완의 목적은 manager 전환 기능과 가로 탐색을 유지하면서, 모든 viewport에서 카드 단위와 카드 내용이 온전하게 읽히도록 만드는 것이다.

## Root Cause

- `.ip-manager-rail`은 가로 `flex`이고 `overflow-x: auto`다.
- compact card는 `min-width: 150px`지만 rail 너비와 visible card count 사이에 계약이 없다.
- 따라서 첫 화면에서 네 장 뒤의 다섯 번째 카드 일부가 남는 너비만큼 노출된다.
- 같은 DOM element의 뒤쪽 `.ip-manager-favorites` 규칙이 rail의 `margin-bottom: 12px`과 `padding-bottom: 8px`을 `0`과 `3px`으로 덮어써 native scrollbar가 카드에 붙어 보인다.
- `.ip-manager-tab strong, .ip-manager-tab span`은 모두 `overflow: hidden`, `text-overflow: ellipsis`, `white-space: nowrap`을 사용한다.
- 최근 hero layout follow-up은 hero / controls column alignment만 소유했고 manager rail의 카드 단위 노출 계약은 변경하지 않았다.

## Approaches Considered

### A. Complete-Card Horizontal Rail — Chosen

- rail을 정수 개 카드가 맞춰지는 horizontal grid로 바꾼다.
- desktop은 4개, tablet은 3개, mobile은 1개의 완전한 카드를 보여준다.
- 다음 manager는 horizontal scroll로 탐색하되 scroll이 카드 시작점에 맞춰진다.
- 카드 내부 alias, filer name, report period는 강제 한 줄 말줄임을 제거하고 자연스럽게 줄바꿈한다.
- 장점: compact manager switcher와 touch / trackpad / keyboard 탐색을 보존하면서 잘린 카드 인상을 제거한다.
- tradeoff: 첫 화면에 동시에 보이는 manager 수가 일부 줄고 카드 높이가 현재보다 커질 수 있다.

### B. Multi-Row Wrapped Manager Grid — Rejected

- 모든 manager를 여러 줄에 펼치면 잘림과 가로 스크롤은 사라진다.
- 검색 결과가 많을 때 hero 아래 높이가 크게 변하고 선택 기관 맥락이 아래로 밀린다.
- manager discovery를 첫 화면의 주인공으로 만들지 않는 Context-First 원칙과 맞지 않는다.

### C. Shrink Cards To Fit Five Or More — Rejected

- 카드와 글자를 축소하면 더 많은 manager를 동시에 볼 수 있다.
- 긴 filer name과 보고 분기 정보가 더 읽기 어려워지고 클릭 영역도 작아진다.
- 잘림의 원인을 해결하지 않고 밀도를 높이는 방식이므로 채택하지 않는다.

## Approved Layout Contract

### Card Count

- Desktop, `> 980px`: rail viewport에 정확히 4개 카드가 들어간다.
- Tablet, `721px–980px`: rail viewport에 정확히 3개 카드가 들어간다.
- Mobile, `<= 720px`: rail viewport에 정확히 1개 카드가 들어간다.
- gap을 제외한 rail 가용 폭을 visible card count로 나눠 각 카드 폭을 계산한다.
- 초기 위치와 스크롤 정착 위치에서 rail 경계에 걸친 부분 카드가 남지 않는다.

### Card Content

- investor alias, SEC filer name, latest report period를 계속 표시한다.
- 기존 강제 `nowrap + ellipsis` 계약은 제거한다.
- filer name과 report period는 카드 내부에서 자연스럽게 줄바꿈한다.
- 긴 토큰도 카드 폭을 밀지 않도록 `overflow-wrap` 경계를 둔다.
- 모든 카드의 높이는 같은 rail row 안에서 동일하게 늘어나며 내용이 카드 밖으로 넘치지 않는다.
- active / pending / disabled 시각 상태와 접근성 label은 그대로 보존한다.

### Scrolling And Discoverability

- horizontal scroll 자체는 유지한다.
- CSS scroll snap을 카드 시작점에 적용해 touch / trackpad scroll이 부분 카드 위치에 멈추지 않게 한다.
- native scrollbar는 탐색 가능성을 위해 유지하되 카드와 붙어 보이지 않도록 기존 하단 여백을 정돈한다.
- 현재 React의 `managerRailRef`와 scroll position 보존 동작은 변경하지 않는다.

## Components And Boundaries

### Presentation Owner

- `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
  - manager rail을 complete-card grid로 전환한다.
  - responsive visible-card count, card sizing, scroll snap, text wrapping을 소유한다.

### Existing Markup

- `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`
  - 현재 `tablist -> button` 구조와 manager selection event를 유지한다.
  - CSS만으로 전체 이름과 기간을 읽을 수 있으면 DOM 구조를 변경하지 않는다.

### Runtime Artifact

- `app/web/streamlit_components/institutional_portfolios_workbench/component_static/`
  - Vite production build 결과를 갱신하고 tracked index가 새 CSS asset을 참조하는지 확인한다.

### Regression Contract

- `tests/test_institutional_portfolios.py`
  - source CSS와 tracked runtime CSS가 동일한 complete-card / wrapping 계약을 포함하는지 보호한다.
  - 기존 hero / freshness / no-80-row-cut 계약을 함께 보존한다.

## Data Flow And Error Handling

- manager payload, 검색 결과 개수, 선택 CIK, pending action, refresh action은 변경하지 않는다.
- manager search 0건, pending selection, disabled state, payload rerun 동작은 기존 계약을 그대로 사용한다.
- 이번 변경은 presentation-only이므로 새 API, DB read, event type, fallback state를 만들지 않는다.
- 콘텐츠가 길어도 rail 바깥 page overflow를 만들지 않고 카드 내부에서 줄바꿈한다.

## Validation Contract

### Automated

- 먼저 기존 CSS 계약에서 부분 카드와 강제 말줄임을 재현하는 failing regression을 만든다.
- source CSS exact selector에 대해 complete-card grid, responsive count, snap, wrapping 계약을 검증한다.
- tracked `component_static/index.html`이 참조하는 CSS asset에도 같은 marker가 있는지 확인한다.
- focused institutional portfolio tests, Vitest, TypeScript typecheck, Vite production build, `git diff --check`를 실행한다.

### Browser QA

- 사용자가 제공한 화면과 같은 desktop 폭에서 첫 rail 위치에 완전한 카드 4개만 보이는지 확인한다.
- tablet 폭에서 완전한 카드 3개, `420px`에서 완전한 카드 1개를 확인한다.
- visible card intersection과 rail 경계를 측정해 부분 카드가 없는지 확인한다.
- Berkshire / Pershing / Appaloosa처럼 긴 filer name이 말줄임 없이 카드 안에서 줄바꿈되는지 확인한다.
- 가로 스크롤 후 정착 위치가 카드 시작점과 일치하고 manager 선택이 계속 동작하는지 확인한다.
- page / iframe horizontal overflow와 browser console error가 없는지 확인한다.
- 최종 QA screenshot 1장을 generated artifact로 남기되 commit하지 않는다.

## Out Of Scope

- manager 검색 / 정렬 / selection event 의미 변경.
- favorite manager 구성이나 검색 결과 제한 변경.
- previous / next arrow button 추가.
- manager comparison surface 추가.
- hero, freshness, holdings explorer, security chart, DB / provider / ingestion 변경.

## Completion Condition

- desktop / tablet / mobile에서 rail 경계에 부분 카드가 보이지 않는다.
- 카드 내부 manager 정보가 강제 한 줄 말줄임 없이 읽힌다.
- 스크롤과 manager selection이 유지된다.
- focused regression, frontend build, tracked runtime verification, actual Browser QA가 통과한다.
