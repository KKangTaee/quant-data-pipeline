# Market Research Top Navigation Visual Polish V1 Design

Status: Approved Direction; Written Spec Review Pending
Last Updated: 2026-07-22

## Confirmed Direction

- 기존 `시장 환경 | 지수 가치평가 | 종목 리서치`와 7개 canonical view는 바꾸지 않는다.
- core navigation은 상단 compact research rail로 유지한다.
- 좌측 drawer는 관심종목, 최근 조회, 저장 리서치 같은 보조 도구가 늘어날 때 검토하고 현재 core navigation에는 사용하지 않는다.
- 긴 화면의 재접근 문제는 actual QA 후 sticky rail 필요성을 판단한다.

## Current Visual Diagnosis

현재 `app/web/overview/navigation.py`는 primary `st.segmented_control(width="stretch")`과 secondary `st.pills(width="stretch")`를 사용한다.

- 두 selector가 모두 outline button group이라 family와 view가 같은 level로 보인다.
- desktop에서 3개/4개 control이 전체 폭을 채워 내부 여백이 과도하다.
- segmented group에 CSS gap이 들어가면서 양 끝만 둥글고 내부 segment는 각진 형태가 노출된다.
- primary red selected surface가 module workbench의 blue-gray 계열과 충돌한다.
- secondary active state와 현재 path가 약해 `시장 환경 / 경제 사이클`을 빠르게 읽기 어렵다.
- header와 first module 사이에서 navigation이 큰 독립 form처럼 떠 있다.

## Target Page Shell

```text
RESEARCH WORKSPACE
Market Research
Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.

시장 환경    지수 가치평가    종목 리서치
──────────────────────────────────────

선택한 리서치  시장 환경
[경제 사이클]  선물 매크로  심리  일정

시장 환경 / 경제 사이클
Economic Cycle module body
```

page-global session, freshness, Reference, run/job/row 정보는 추가하지 않는다.

## Header Contract

- page header는 keyed Streamlit container가 소유해 CSS scope를 다른 page와 분리한다.
- eyebrow는 `RESEARCH WORKSPACE`, title은 `Market Research`다.
- description은 `Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다.`로 짧게 유지한다.
- 현재보다 title 이후와 navigation 전 vertical gap을 줄이되 Streamlit global heading style은 변경하지 않는다.
- header 전체는 full-width card나 bordered surface로 감싸지 않는다.

## Primary Family Rail

- 3개 family는 desktop에서 content-width horizontal rail로 표시한다.
- full-width equal box와 개별 outline border를 사용하지 않는다.
- selected family는 진한 text, medium weight와 rail position indicator 또는 quiet selected surface로 구분한다.
- red outline/fill은 사용하지 않는다. 경고·손실 의미의 red와 navigation state를 분리한다.
- hover/focus/selected 상태는 color 하나에만 의존하지 않는다.
- control은 기존 Streamlit widget을 유지해 keyboard/accessibility와 session behavior를 보존한다.

## Secondary Local Navigation

- secondary view는 primary rail 아래의 bounded local navigation surface에 둔다.
- surface는 `선택한 리서치`와 현재 family label을 먼저 보여 family/view 관계를 설명한다.
- view control은 content width로 배치하고 선택 view만 quiet filled surface와 weight로 강조한다.
- `지수 가치평가`는 view가 하나여도 local surface 안에서 `S&P 500` 현재 위치를 표시한다. family 전환 때 surface 높이가 크게 튀지 않아야 한다.
- local navigation과 module body 사이에는 현재 path와 module 시작점이 자연스럽게 이어지는 compact gap만 둔다.

## Responsive Contract

### Desktop

- primary family: content-width row
- local navigation: family label lane + view control lane
- secondary buttons: intrinsic width, unnecessary stretch 없음

### 760px

- primary family는 한 줄 유지가 기본이며 공간이 부족하면 natural wrap을 허용한다.
- local navigation label/view lane은 필요 시 세로로 쌓인다.

### 420px

- primary family는 3 equal columns로 유지한다.
- secondary view는 2-column grid로 배치한다.
- `지수 가치평가` 단일 view는 한 칸만 어색하게 남기지 않고 사용 가능한 폭 안에서 명확한 current item으로 표시한다.
- horizontal scroll, clipping, fixed viewport width를 사용하지 않는다.

## State And Data Boundary

다음 기존 contract는 수정하지 않는다.

- canonical view 및 legacy slug normalization
- URL query > widget > session precedence
- family -> default view mapping
- Today deep link와 `/overview` continuity
- selected view lazy renderer
- Market Movers -> U.S. Stock selected-symbol handoff

visual wrapper와 CSS가 state source를 새로 만들지 않는다.

## File Ownership

| Area | Owner |
| --- | --- |
| header copy, keyed wrapper, render order | `app/web/overview/page.py` |
| primary/secondary widget structure와 scoped CSS | `app/web/overview/navigation.py` |
| pure navigation/state contract regression | `tests/test_market_research_navigation.py` |
| broader structural compatibility | `tests/test_service_contracts.py` |

module renderer와 React workbench file은 이 task에서 수정하지 않는다.

## Verification Contract

### Automated

- 3 families / 7 views / legacy normalization 기존 tests 유지
- selector가 full-width primary/secondary box contract로 되돌아가지 않는 structural test
- local family label과 single-view S&P state contract
- Today CTA와 Market Movers handoff regression
- `py_compile`, `git diff --check`

### Browser QA

- actual `/overview` default Economic Cycle
- desktop, 760px, 420px header/nav hierarchy
- all three family selected states
- market environment 4 views, index 1 view, stock 2 views
- module start와 nav 사이 excessive whitespace/overlap 없음
- horizontal overflow 0, keyboard focus visible, console warning/error 0
- final screenshot 1장; generated artifact는 commit하지 않음

## Tradeoffs

- 상단 rail은 현재 기능 수에 가장 직접적이지만 화면을 아래로 스크롤한 뒤에는 보이지 않는다. 먼저 실제 QA하고 sticky 필요가 확인될 때만 후속으로 연다.
- 좌측 drawer는 persistent access를 줄 수 있지만 core navigation을 숨기고 추가 click과 overlay를 만든다. 현재 3-family/7-view에는 복잡도 대비 이점이 작다.
- Streamlit native widget을 유지하면 state/accessibility 위험이 작지만 custom React navigation만큼 geometry 제어가 자유롭지 않다. scoped CSS는 widget DOM contract를 focused test와 Browser QA로 보호한다.

## Approval Boundary

이 문서는 사용자가 승인한 compact top rail과 drawer 제외 방향을 구현 가능한 시각 contract로 고정한다. written spec 확인 후에만 implementation plan을 작성하고 code work를 시작한다.
