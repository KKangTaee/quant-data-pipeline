# Market Research Header System V1 Design

Status: Approved
Date: 2026-07-25

## 1. 문제 이해

현재 네 화면의 상단은 데이터 양뿐 아니라 구조 자체가 다르다.

- 경제사이클: 간결한 판단 제목과 우측 기준일
- 선물매크로: action row, 큰 판단 제목, 3개 상태 카드, 근거 칩
- 심리: action row, 독립 심리축 2개, 별도 meta row
- 일정: 판단 제목 카드와 다음 이벤트 카드가 서로 분리

통일 대상은 데이터 양이 아니라 사용자가 읽는 순서와 시각적 문법이다. 각 화면은 `화면 식별 -> 현재 판단 -> 설명 -> 핵심 사실 -> 보조 근거` 순서를 공유한다.

## 2. 선택된 방향

사용자는 `A. 공통 뼈대 + 가변 정보 슬롯`을 선택했다.

네 화면 모두 같은 shell, 타이포, 간격과 반응형 규칙을 사용한다. 다만 정보량에 따라 우측 사실 카드는 1~3개만 렌더링하고, action과 하단 meta도 데이터가 있을 때만 표시한다. 빈 슬롯이나 가짜 데이터를 만들지 않는다.

## 3. 공통 헤더 구조

```text
ResearchHeader
├── top row
│   ├── eyebrow
│   └── optional actions
├── content grid
│   ├── decision copy
│   │   ├── kicker
│   │   ├── title
│   │   ├── optional transition
│   │   ├── summary
│   │   └── optional detail
│   └── fact stack (1~3)
├── optional notice
└── optional meta chips
```

### 공통 시각 토큰

- 제목: desktop `34px`, mobile `28px`, 동일 weight와 letter spacing
- eyebrow: `10px`, uppercase, 동일 letter spacing
- shell: `21px` radius, `24px 26px` padding
- action: 동일 pill 형태와 최소 높이
- 사실 카드: 동일한 중립 배경, 외곽선, radius, 내부 여백
- 화면별 색상은 eyebrow, kicker, transition, 실제 상태값에만 제한한다.

## 4. 우측 사실 카드 상태 표현

초기 시안의 좌측 컬러 테두리는 사용하지 않는다.

- 모든 사실 카드는 동일한 중립 외곽선과 라운드를 사용한다.
- 상태를 전달해야 할 때만 값 앞에 `6px` 상태 점을 표시하고 값 텍스트에 제한적으로 의미 색상을 적용한다.
- 기준일, 관측 범위, 다음 이벤트처럼 상태가 아닌 사실 정보는 무채색으로 표시한다.
- 상태 색상만으로 의미를 전달하지 않고 기존 상태 문구를 항상 함께 표시한다.
- 상태 색상은 공통 component가 새로 판단하지 않는다. 각 화면의 기존 상태 매핑이 `neutral / info / positive / caution / negative` 중 하나를 명시적으로 전달한다.

## 5. 화면별 매핑

### 경제 사이클

- eyebrow: `U.S. ECONOMIC CYCLE`
- kicker: `현재 경기 위치`
- title: 기존 현재 dominant phase 문구
- facts:
  - 데이터 기준
  - 검증 상태 — 상태 점 사용
- meta:
  - 현재 / +1개월 / +2개월 관측 범위
  - 월중 추정이 있으면 해당 구분
- action은 만들지 않는다.

### 선물 매크로

- eyebrow: `FUTURES MACRO`
- actions: 기존 `일봉 갱신`, `다시 읽기`
- kicker: 기존 단기 방향 진단 문구
- title / transition / summary / 오늘의 재가격화: 기존 payload 의미 보존
- facts:
  - 관측 상태 — 상태 점 사용
  - 기준일
  - 관측 범위
- pending session notice와 기존 evidence chip을 공통 footer 슬롯으로 유지한다.

### 심리

- eyebrow: `MARKET PSYCHOLOGY · CROSS READ`
- actions: 기존 자료 action
- kicker / title / transition / summary / confidence note: 기존 payload 의미 보존
- facts:
  - CNN 시장 행동 — 상태 점 사용
  - AAII 투자자 설문 — 상태 점 사용
- source date와 `합성점수 없음`, `매수·매도 신호 아님`은 meta chip으로 유지한다.

### 일정

- eyebrow: `MARKET EVENTS`
- kicker / title / summary: 기존 brief 정보를 사용한다.
- fact:
  - 다음 이벤트 날짜와 제목 — 상태가 아니므로 무채색
- 오늘 / 이번 주 / 30일 내 / 오래된 추정처럼 기존 payload가 이미 제공하는 count 중 상단 판단에 필요한 compact 값만 meta chip에 투영한다.
- 기존 상세 count grid, 갱신 command, filter, rail, calendar, trust, evidence 영역은 유지한다.

## 6. 구현 경계

공통 source는 다음처럼 React 표시 계층 안에 둔다.

```text
app/web/streamlit_components/
  market_research_header/
    ResearchHeader.tsx
    style.css
```

각 workbench는 기존 payload를 `ResearchHeader` props로 매핑하는 얇은 화면별 adapter를 유지한다.

- `economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- `futures_macro_workbench/src/MacroContextSection.tsx`
- `sentiment_workbench/src/SentimentHero.tsx`
- `events_workbench/src/EventsWorkbench.tsx`

공통 component는 Streamlit API, DB, loader, provider를 알지 않는다. action callback과 표시할 React data만 입력받는다. 화면별 서비스와 Python dispatch 경계는 변경하지 않는다.

공통 props 경계는 다음 역할만 가진다.

- 식별 / 판단: `eyebrow`, `kicker`, `title`, 선택적 `transition`, `summary`, `detail`
- 사실: `label`, `value`, 선택적 기존 상태 `tone`
- 동작: `label`, `kind`, `disabled`, 기존 callback
- 보조: `meta`, 선택적 `notice`

`facts`, `actions`, `meta`, `notice`가 비어 있으면 해당 영역과 여백을 함께 렌더링하지 않는다.

## 7. 반응형 규칙

- desktop: 판단 copy와 facts를 2열로 표시한다.
- `760px` 이하: content grid를 1열로 전환하고 facts를 제목 아래로 내린다.
- mobile:
  - 제목은 `28px`
  - facts는 제목 아래 1~2열로 배치
  - actions는 우측에서 자연스럽게 wrap
  - meta chip은 여러 줄로 wrap
- `480px` 이하: facts를 한 열로 바꾸고 action label이 잘리지 않도록 top row도 wrap한다.
- 어떤 너비에서도 빈 사실 카드, 수평 스크롤, 잘린 action label을 만들지 않는다.

## 8. 데이터·오류 처리

- payload가 제공하지 않은 선택 슬롯은 렌더링하지 않는다.
- 제공된 필수 값이 비어 있으면 기존 화면의 `-` 또는 기존 fallback 문구를 보존한다.
- action pending / disabled 상태와 Python dispatch id는 현재 계약을 그대로 사용한다.
- 상태 색상은 접근성 보조 표현이며, 상태 텍스트를 대체하지 않는다.
- 공통 헤더 오류가 데이터 계산이나 provider fetch로 이어지는 새 경로를 만들지 않는다.

## 9. 검증

### 자동 검증

- 네 component의 TypeScript / Vite build
- 관련 Python payload projection 테스트
- 기존 action id와 dispatch 회귀 테스트
- static distribution 파일 갱신 확인
- `git diff --check`

### 실제 Browser QA

- 화면: 경제사이클, 선물매크로, 심리, 일정
- 너비: 1280px, 760px, 420px
- 확인 항목:
  - 동일 제목 크기와 시작 위치
  - facts 1~3개 가변 배치
  - 상태 점과 중립 사실 정보 구분
  - action wrap / disabled 상태
  - pending notice와 meta chip wrap
  - 수평 overflow 및 console error 없음

## 10. 완료 기준

- 네 화면의 헤더가 같은 정보 순서와 시각 토큰을 사용한다.
- 화면별 데이터 양과 기존 의미는 유지된다.
- 좌측 컬러 테두리가 없고 상태값 내부 점 표현이 적용된다.
- 기존 갱신 action과 Python dispatch가 동작한다.
- 1280px, 760px, 420px actual Browser QA와 최소 1장의 최종 QA 스크린샷을 남긴다.
