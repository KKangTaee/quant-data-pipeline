# Institutional Holdings Content-First UI V1 Design

Status: Approved Design — Written Spec Review
Last Updated: 2026-08-17

## Approved Direction

사용자가 시각 비교에서 A안 `Content-first 하이브리드`를 선택했다. Market Research의
수평 탐색 구조와 Today의 `요약 -> 다음 확인` reading order를 결합한다. 기관 목록과
목적지 navigation을 한 dark sidebar에 유지하지 않는다.

## Current Problem And Root Cause

### Manager selection regression

1. `manager_search` event가 `institutional_portfolios_manager_search`를 유지한다.
2. 다른 manager를 누르면 `select_manager` event가 selected CIK만 바꾼다.
3. 다음 Streamlit rerun에서 `search_active=True`인 `_resolve_selected_manager()`가 새
   selected CIK을 query match로 인정하지 않고 기존 검색 결과의 첫 manager를 다시
   선택한다.
4. React의 manager pending action은 요청한 CIK을 payload에서 확인하지 못해 일정 시간
   다른 manager button을 비활성화한다.

따라서 click event 자체가 없는 문제가 아니라, server-side selection normalization이
사용자가 방금 선택한 CIK을 덮어쓰는 상태 충돌이다.

### Visual and structural mismatch

- manager search, manager list, five destinations, refresh state가 하나의 left rail에서
  경쟁한다.
- selected manager는 full-height `inset box-shadow`로 표시되어 row 높이에 따라 긴
  세로선이 된다.
- 다른 Research surface와 달리 page title, selected subject, freshness와 primary
  navigation이 content hierarchy 위에 드러나지 않는다.
- 모바일은 같은 과밀 rail을 drawer로 옮겨 desktop hierarchy 문제를 그대로 유지한다.

## User Flow

```text
Institutional Holdings 진입
  -> page title + selected manager + report period + freshness 확인
  -> 필요하면 manager selector를 열고 이름/기관명으로 검색
      -> manager 선택
      -> 검색 query와 picker를 닫고 selected CIK을 단일 current context로 승격
      -> 기존 본문을 유지한 채 선택 영역에 pending 표시
      -> 새 payload 수신 후 header와 body를 함께 교체
  -> horizontal research tab에서 목적지 선택
  -> 첫 화면은 핵심 요약 -> 보고 근거 -> 다음 확인 -> 상세 근거 순서로 읽음
  -> 로컬 due 상태일 때만 explicit refresh action 실행
```

## Information Architecture

### 1. Page Header

- eyebrow: `RESEARCH / INSTITUTIONAL HOLDINGS`
- title: `기관 보유 분석`
- scope note: `지연 공시 기반 리서치`
- right context: latest report period와 local freshness state

Header는 제품 위치와 데이터 시점을 설명한다. raw job count나 ingestion row는 첫 화면에
두지 않는다.

### 2. Manager Control Bar

- 현재 investor alias와 SEC filer name을 한 control에 표시한다.
- `기관 변경`을 열면 검색 input과 manager result list가 나타난다.
- 선택 후 query를 비우고 picker를 닫는다.
- report period, filing date와 SEC source는 같은 context bar의 compact evidence로 둔다.
- refresh action은 기존 local due contract가 `due` 또는 `partial`일 때만 표시한다.

### 3. Research Destination Tabs

- `포트폴리오 맥락`
- `분기 리뷰`
- `전체 보유`
- `종목 상세`
- `기관 보유 랭킹`

Desktop은 한 행, 좁은 viewport는 horizontal scroll을 사용한다. active tab은 text contrast,
subtle tint와 짧은 bottom underline으로 표시한다. left inset line과 full pill outline은
사용하지 않는다.

### 4. Content Canvas

기존 view body와 계산 결과는 보존하되 기본 `포트폴리오 맥락` 순서를 아래처럼 정렬한다.

1. selected manager context summary
2. concentration / holding count / mapping coverage 핵심 metric
3. report basis와 SEC source
4. `다음 확인` action — quarter review readiness에 따라 분기 리뷰 또는 holdings 탐색
5. allocation, reported changes, sector와 price proxy detailed evidence

`다음 확인`은 navigation shortcut이며 추천·승인·매매 신호가 아니다.

## Component Boundaries

### React presentation

- `InstitutionalStudioShell.tsx`
  - content-first page header, manager control slot, destination tabs와 responsive canvas를
    소유한다.
  - left rail, mobile drawer와 scrim 계약을 제거한다.
- `InstitutionalPortfoliosWorkbench.tsx`
  - manager picker interaction, active view, pending/error state와 existing view bodies를
    연결한다.
  - manager drag-scroll suppression은 vertical rail 제거와 함께 삭제한다.
  - 한 파일의 변경이 과도해지면 manager picker와 destination tabs를 각각 목적이
    분명한 local component로 추출하되 payload contract는 바꾸지 않는다.
- `style.css`
  - shared light surface tokens, control bar, horizontal tabs, active state와 responsive
    layout을 소유한다.
- tracked `component_static/`
  - 검증된 production build 결과만 갱신한다.

### Streamlit command boundary

- `app/web/institutional_portfolios.py`
  - `select_manager` event를 받을 때 selected CIK을 저장하기 전에 manager search query를
    비운다.
  - interest/security transient state reset은 기존 동작을 유지한다.
  - provider fetch나 DB write를 manager selection에 추가하지 않는다.

### Existing service/data boundary

- workbench payload schema와 manager rail item fields는 가능한 한 유지한다.
- SEC collector, loaders, quarter review calculation과 database schema는 변경하지 않는다.
- presentation-only rename이 필요하면 Python authority와 React presentation 경계를
  유지한다.

## State And Data Flow

### Manager selection

```text
React select_manager(cik)
  -> pending target만 표시, current body 유지
  -> Streamlit clears manager search + stores selected CIK + rerun
  -> loader reads selected portfolio
  -> payload selected_cik / hero / body가 같은 CIK으로 반환
  -> React acknowledges target and clears pending
```

- query가 존재해도 explicit manager selection이 우선한다.
- selection success 뒤 picker input에는 빈 query와 selected manager label이 보인다.
- 요청한 CIK의 portfolio load가 실패하면 이전 body를 보존하고 picker 아래에 bounded
  retry guidance를 표시한다.

### Destination selection

- existing local `StudioView` state를 사용한다.
- tab change는 DB load나 Streamlit rerun을 요구하지 않는다.
- manager 변경 뒤 active destination은 유지한다. 새 manager에 해당 view evidence가
  없으면 그 view의 기존 explicit empty state를 표시한다.

### Refresh

- page entry는 local due calculation만 수행한다.
- SEC/EDGAR access와 mutation은 기존 explicit refresh button 이후에만 시작한다.
- refresh pending과 failure는 manager selection pending과 별도 state로 유지한다.

## Pending, Empty And Error Behavior

- manager loading은 picker/control bar에만 표시하고 destination tabs 전체를 막지 않는다.
- stale current portfolio는 새 payload가 올 때까지 읽을 수 있다.
- manager search 0건은 current selection과 body를 바꾸지 않는다.
- manager load failure는 current content를 보존하고 picker 아래 concise message를 둔다.
- refresh failure는 refresh control에 남기고 portfolio exploration을 막지 않는다.
- raw exception, row count와 job detail은 default first-read에 노출하지 않는다.

## Responsive And Accessibility Contract

- `> 980px`: header, manager control, tabs와 canvas가 full-width content column을 사용한다.
- `721px–980px`: manager evidence가 자연스럽게 wrap되고 tabs는 horizontal scroll을
  허용한다.
- `<= 720px`: manager control은 vertical stack, touch target은 최소 44px을 유지한다.
- 별도 sidebar drawer, scrim 또는 full-page manager overlay를 만들지 않는다.
- manager control은 combobox/listbox 또는 동등한 semantic button/search/list contract를
  사용한다.
- tabs는 keyboard focus와 `aria-selected`를 제공한다.
- selected manager는 color만이 아니라 text/check marker로도 구분한다.
- page와 iframe에 horizontal overflow를 만들지 않는다. tabs의 내부 overflow만 허용한다.

## Approaches Considered

### A. Content-first hybrid — Chosen

Research product hierarchy와 responsive reading order가 가장 자연스럽고, manager rail의
과밀과 선택 indicator 문제를 구조적으로 제거한다.

### B. Manager list + detail split

manager comparison에는 유리하지만 persistent sidebar와 mobile drawer가 필요해 첫 화면
과밀과 다른 Research surface 불일치가 일부 남는다.

### C. Existing studio rail restyle

변경 위험은 작지만 navigation ownership과 manager selection hierarchy가 그대로라 사용자
요청인 구조적 일치에 도달하지 못한다.

## Verification Contract

### Automated

- Python regression: active search가 있는 상태의 `select_manager` event가 search를 비우고
  requested CIK을 유지한다.
- selection resolver regression: explicit selected manager가 다음 render에서 query match로
  덮이지 않는다.
- React tests: manager selector pending acknowledgment, empty search, sequential selection과
  destination tab state.
- source/runtime contract: left studio rail active line과 drawer selectors가 제거되고,
  horizontal tab active marker와 content-first shell selector가 존재한다.
- focused institutional Python suite, Vitest, TypeScript typecheck, Vite production build와
  `git diff --check`를 통과한다.

### Browser QA

- desktop에서 Bill Ackman 선택 후 David Tepper, Warren Buffett로 연속 전환한다.
- 검색어가 선택 후 비워지고 header/body/active manager가 같은 CIK임을 확인한다.
- five destination tabs와 quarter review action을 확인한다.
- local current와 due refresh state가 기존 explicit-click 의미를 유지하는지 확인한다.
- 900px와 420px에서 manager control, horizontally scrollable tabs, no page overflow와
  최소 touch target을 확인한다.
- 최종 QA screenshot 1장을 generated artifact로 남기고 commit하지 않는다.

## Documentation Closeout

- 화면 흐름이 구현과 함께 바뀌므로
  `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md` 갱신을 검토한다.
- product promise, data meaning과 code ownership이 바뀌지 않으면
  `PRODUCT_DIRECTION.md`, `PROJECT_MAP.md`는 변경하지 않는다.
- 실행 결과와 검증은 이 task의 `STATUS.md`, `RUNS.md`, `RISKS.md`가 소유한다.
