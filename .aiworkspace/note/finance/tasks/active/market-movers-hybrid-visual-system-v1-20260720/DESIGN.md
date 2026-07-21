# Market Movers Hybrid Visual System V1 Design

Status: Approved A-Option Specification
Last Updated: 2026-07-20

## 이걸 하는 이유?

현재 변동 종목 React one-shell은 ranking, sector/industry 확산, 선택 종목 조사를 같은 selected state로 연결했지만, 화면은 흰 직사각형·작은 타이포·native select·파랑/보라/청록 accent가 동시에 나타나는 운영 보드에 가깝다. 시장맥락과 선물매크로가 사용하는 큰 rounded surface, 낮은 채도의 blue-gray 계열, 해석 우선 hierarchy와 맞지 않아 Overview 안에서 별도 프로토타입처럼 보인다.

사용자가 승인한 A안은 선물매크로의 큰 통합 surface 안에 시장맥락의 읽는 흐름을 적용한다. 기능을 더 붙이는 작업이 아니라, 이미 구현된 흐름을 더 빠르게 읽고 같은 제품군으로 인식하게 만드는 시각 체계 개편이다.

## Approved Direction

`A안 — 통합 리포트형`을 사용한다.

- 선물매크로처럼 전체 workbench를 하나의 큰 rounded blue-gray surface로 감싼다.
- 시장맥락처럼 `현재 상태 → 무엇이 움직였는가 → 어디까지 퍼졌는가 → 선택 종목에서 무엇을 확인할까` 순서로 읽힌다.
- ranking과 breadth는 desktop에서 동시에 비교할 수 있도록 기존 `62/38` 비율을 유지한다.
- 선택 종목 조사는 같은 surface의 하단 evidence section으로 이어지며 별도 앱이나 drawer처럼 분리하지 않는다.

## Scope

### 포함

- `MarketMoversDecisionWorkbench`의 DOM hierarchy와 CSS visual system
- hero, trust, command band, market pulse, ranking/breadth, selected research, disclosure의 시각 재구성
- native select를 유지하되 segmented command card처럼 보이도록 일관된 custom styling 적용
- semantic positive/negative/warning/blocked 상태의 제한된 색상 사용
- desktop, tablet, 420px responsive hierarchy와 keyboard focus
- 기존 selected state, Streamlit event, payload schema를 그대로 사용하는 presentation-only 변경

### 제외

- `market_movers_decision_payload_v1` 계산 의미 변경
- sector/industry conditional outlook 또는 5D/20D/60D 수치
- 수집 job, raw rows, provider diagnostics를 첫 화면에 추가하는 작업
- ranking algorithm, financial factor 산식, DB schema 변경
- 시장맥락·선물매크로 화면 자체의 수정

## Visual Architecture

```text
Overview dark app background
  └─ Market Movers unified surface
       ├─ Hero + compact trust
       ├─ Command band
       ├─ Current market pulse
       ├─ Decision grid (ranking 62 / breadth 38)
       ├─ Selected company evidence
       │    ├─ quick identity / key facts
       │    └─ price | financial | events research
       └─ Method / source disclosure
```

### 1. Unified Surface

- outer radius: `20px`
- outer border: `1px solid #d8e4ea`
- surface background: `linear-gradient(145deg, #f8fbfd 0%, #f2f7f9 62%, #eef5f7 100%)`
- padding: desktop `28px`, tablet `22px`, mobile `16px`
- shadow: `0 18px 45px rgba(30, 56, 75, 0.07)`
- 기존 `4px teal top border`는 제거한다.

### 2. Color Contract

- ink: `#203c50`
- secondary ink: `#456377`
- muted: `#748793`
- faint line: `#d8e4ea`
- card line: `#cddde5`
- white card: `rgba(255, 255, 255, 0.88)`
- primary accent: muted blue `#397fb7`
- secondary accent: restrained teal `#2f7f73`
- positive: `#19765f`
- negative: `#b9554c`
- warning: `#9a6a22`

파랑은 선택과 정보 구조에, 청록은 trust/coverage에만 사용한다. 초록·빨강은 상승·하락 같은 실제 semantic state에만 사용하며 decorative top border나 section identity에는 쓰지 않는다. 보라는 제거한다.

### 3. Hero And Trust

- eyebrow `MARKET MOVERS`와 제목 `변동 종목`을 좌측에 둔다.
- 설명은 `움직임 → 확산 → 종목 확인`의 사용자 질문을 한 문장으로 제시한다.
- trust는 우측 compact chip + 기준일 한 줄로 표현하고 독립 카드로 키우지 않는다.
- `PARTIAL/BLOCKED`는 orange/red tint를 사용하되 ranking보다 시각적으로 앞서지 않는다.

### 4. Command Band

- coverage, period, ranking mode, top-N을 하나의 command band 안 네 구역으로 묶는다.
- 각 control은 label/value/chevron hierarchy를 가지며 outer band의 배경과 선으로 연결한다.
- native select 기능은 접근성과 기존 event 계약을 위해 보존한다.
- control focus는 `2px solid rgba(57, 127, 183, 0.35)`로 명확히 표시한다.
- mobile에서는 두 열 후 한 열로 내려가며 horizontal scroll을 만들지 않는다.

### 5. Current Market Pulse

hero와 decision grid 사이에 3~4개의 compact fact를 한 줄로 둔다.

- 선택 기간 / ranking 기준
- 상승·하락 또는 participation 요약
- leading sector 또는 industry
- coverage/trust 요약

새 payload 필드를 만들지 않고 ranking/group/trust의 기존 값으로 구성한다. 값이 없으면 해당 cell을 숨기고 빈 placeholder를 만들지 않는다.

### 6. Decision Grid

- desktop `min-width: 900px` 이상에서 ranking `1.62fr`, breadth `1fr`을 유지한다.
- 두 영역은 별도 컬러 top border 대신 같은 white glass card와 동일한 radius/border를 사용한다.
- 선택된 ranking row는 연한 blue background + 좌측 3px blue rail로 표현한다.
- 수익률/변동 값만 positive/negative semantic color를 사용한다.
- breadth의 sector/industry 및 day/week/month controls는 작은 segmented pills로 유지한다.
- selected group과 Top 3 bellwether는 같은 breadth card 안의 evidence 흐름으로 읽힌다.

### 7. Selected Company Evidence

- quick research strip은 decision grid 직후 full-width white card로 둔다.
- symbol/name, 선택 ranking 근거, 핵심 상태, `상세 조사` affordance를 한 줄 hierarchy로 표현한다.
- expanded research는 별도 border-heavy block이 아니라 quick strip과 같은 card family의 하위 section으로 연결한다.
- `가격·모멘텀 | 재무 | 뉴스·공시` tab은 Overview primary navigation과 같은 muted text + active blue underline pattern을 사용한다.
- 재무의 `분기/연간`, `재무 영역`, `factor` 세 control group은 현재 승인 구조를 그대로 유지한다.
- chart/readout은 desktop `70/30`, mobile stack을 유지하며 chart 높이는 데이터 points와 무관하게 안정적으로 고정한다.

### 8. Disclosure And Diagnostics

- method/source는 surface 하단의 disclosure로 둔다.
- raw missing rows, job status, provider detail은 기본 접힘 상태에서만 접근한다.
- `Complete/Partial/Blocked`의 사용자 의미와 다음 행동은 상단 trust와 local empty state에서 설명한다.
- BLOCKED이면 ranking을 정상 결과처럼 꾸미지 않고 원인과 가능한 행동을 같은 surface 안에 표시한다.

## Interaction Contract

- coverage/period/ranking/top-N 변경은 기존 bounded Streamlit event를 보낸다.
- ranking row 선택은 quick research와 expanded research의 symbol을 함께 바꾼다.
- sector/industry, group period, group, research tab, financial controls는 React local state를 유지한다.
- visual refactor는 event name, payload schema version, Python session-state key를 변경하지 않는다.
- focus-visible, button/row aria semantics, disabled factor 표현을 보존한다.

## Responsive Contract

- `>= 900px`: 62/38 decision grid, 4-column command band, quick research horizontal.
- `600px–899px`: single-column decision grid, 2-column command band, research chart/readout stack 허용.
- `< 600px`: one-column command band, compact hero/trust stack, row secondary facts 축약, all controls wrap without overflow.
- minimum QA widths: actual component desktop width, `693px`, `420px`, `353px`.
- 모든 QA width에서 `scrollWidth == clientWidth`를 만족해야 한다.

## Error And Empty States

- empty ranking: 현재 조건과 다음 가능한 action을 한 개의 local empty card로 표시한다.
- empty group: ranking은 유지하고 breadth card 안에서만 empty state를 표시한다.
- missing financial factor: chart 영역에 이유를 표시하고 factor button은 disabled한다.
- schema mismatch: 기존 React empty state를 유지하며 시각 변경 코드가 Python fallback을 재구성하지 않는다.
- unknown tone: neutral blue-gray로 fallback한다.

## Testing Strategy

### Contract Tests

- source contract로 unified surface, hero, command band, market pulse, decision grid, selected evidence class 구조를 고정한다.
- 기존 event strings와 payload schema가 변경되지 않았음을 검증한다.
- purple accent 및 teal top border가 decision shell에서 제거됐음을 검증한다.
- 900px/600px responsive breakpoint와 focus-visible rule을 검증한다.

### Build And Regression

- Market Movers focused Python/service tests
- React TypeScript/Vite production build
- `git diff --check`
- 기존 one-shell selection/financial contract regression

### Browser QA

- desktop: visual parity, 62/38 balance, ranking selection, sector→industry, daily→monthly, research/financial interaction
- 420px: hero/control stack, ranking row readability, breadth and research overflow
- console error 0건 확인
- 최종 QA screenshot 1장을 생성하되 commit하지 않는다.

## Acceptance Criteria

1. 첫 화면이 흰 admin board가 아니라 시장맥락·선물매크로와 같은 Overview report family로 인식된다.
2. `무엇이 움직였는가 → 어디까지 퍼졌는가 → 선택 종목에서 무엇을 확인할까`가 한 surface 안에서 시각적으로 이어진다.
3. ranking과 breadth의 동시 비교 및 selected-state interaction은 현재와 동일하게 작동한다.
4. 파랑/청록/semantic green-red 이외의 competing accent가 없다.
5. desktop/693px/420px/353px에서 horizontal overflow가 없다.
6. payload, data loader, ranking/financial 계산 로직은 변경하지 않는다.

## Roadmap Position

- 기존 Market Movers 기능 roadmap: `4/5차` 유지
- 이번 시각 통일 task: `1/3차` 설계 확정
- 다음 2차: TDD 기반 React DOM/CSS 적용과 production build
- 다음 3차: actual browser interaction·responsive QA와 문서 closeout
- 별도 남은 기능 5차: conditional outlook/OOS publication gate; 이번 task에서 수행하지 않는다.
