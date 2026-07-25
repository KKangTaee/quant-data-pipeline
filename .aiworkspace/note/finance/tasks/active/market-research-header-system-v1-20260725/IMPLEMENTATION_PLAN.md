# Market Research Header System V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 경제사이클·선물매크로·심리·일정의 상단 헤더를 하나의 공통 React 표시 계약으로 통일하되 기존 계산, payload 의미와 Python action dispatch는 보존한다.

**Architecture:** `app/web/streamlit_components/market_research_header/`에 Streamlit과 데이터 계층을 모르는 공통 `ResearchHeader`를 만든다. 네 독립 Vite workbench는 기존 payload를 공통 props로 매핑하는 얇은 adapter만 소유하며, optional facts/actions/notice/meta가 없으면 영역과 여백을 함께 생략한다.

**Tech Stack:** React 18, TypeScript, CSS, Vite 6, Streamlit component lib, pytest source-contract regression tests, in-app Browser QA

## Global Constraints

- 제목은 desktop `34px`, mobile `28px`; eyebrow는 `10px`; shell은 `21px` radius와 `24px 26px` padding을 사용한다.
- 사실 카드의 좌측 컬러 테두리는 사용하지 않는다.
- 상태는 기존 화면이 전달한 tone과 `6px` 점, 상태 문구로 함께 표시한다. 기준일·범위·다음 이벤트는 무채색이다.
- facts/actions/meta/notice가 비어 있으면 빈 슬롯이나 가짜 데이터를 만들지 않는다.
- 계산, scoring, validation, payload schema, provider fetch, DB, loader와 Python dispatch id는 변경하지 않는다.
- 기존 사용자 변경, registry, run history, `.superpowers/`, QA 이미지에는 손대거나 stage하지 않는다.
- 각 Vite package의 canonical `component_static/`을 재빌드하고 generated hash 변경을 함께 commit한다.

---

### Task 1: 공통 ResearchHeader 계약과 스타일

**Files:**
- Create: `app/web/streamlit_components/market_research_header/ResearchHeader.tsx`
- Create: `app/web/streamlit_components/market_research_header/style.css`
- Create: `tests/test_market_research_header_system.py`

**Interfaces:**
- Consumes: React `ReactNode`; 화면별 기존 string/action callback
- Produces:
  - `ResearchHeaderTone = "neutral" | "info" | "positive" | "caution" | "negative"`
  - `ResearchHeaderVariant = "cycle" | "futures" | "sentiment" | "events"`
  - `ResearchHeaderFact`, `ResearchHeaderAction`, `ResearchHeaderMeta`
  - `ResearchHeader(props: ResearchHeaderProps)`

- [ ] **Step 1: 공통 계약의 실패 테스트 작성**

```python
from pathlib import Path

ROOT = Path("app/web/streamlit_components")
SHARED = ROOT / "market_research_header"


def test_shared_research_header_exposes_only_display_contract() -> None:
    source = (SHARED / "ResearchHeader.tsx").read_text(encoding="utf-8")

    for token in (
        'export type ResearchHeaderTone =',
        'export type ResearchHeaderFact =',
        'export type ResearchHeaderAction =',
        'export type ResearchHeaderMeta =',
        'function ResearchHeader(',
        'className="research-header__facts"',
        'className="research-header__state-dot"',
        "facts.length > 0",
        "actions.length > 0",
        "meta.length > 0",
    ):
        assert token in source
    for forbidden in ("Streamlit", "fetch(", "axios", "load_", "provider"):
        assert forbidden not in source


def test_shared_research_header_css_uses_neutral_fact_boxes_and_responsive_tokens() -> None:
    css = (SHARED / "style.css").read_text(encoding="utf-8")

    fact_rule = css[css.index(".research-header__fact {") :]
    fact_rule = fact_rule[: fact_rule.index("}")]
    assert "border-left" not in fact_rule
    assert "border: 1px solid" in fact_rule
    assert "border-radius:" in fact_rule
    assert "width: 6px" in css
    assert "height: 6px" in css
    assert "font-size: 34px" in css
    assert "@media (max-width: 760px)" in css
    assert "@media (max-width: 480px)" in css
    assert "font-size: 28px" in css
```

- [ ] **Step 2: 테스트가 파일 부재로 실패하는지 확인**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_header_system.py -q
```

Expected: FAIL because `market_research_header/ResearchHeader.tsx` and `style.css` do not exist.

- [ ] **Step 3: 공통 타입과 렌더러 구현**

`ResearchHeader.tsx`의 공개 계약은 아래 이름과 역할을 그대로 사용한다.

```tsx
import type { ReactNode } from "react";
import "./style.css";

export type ResearchHeaderTone =
  | "neutral"
  | "info"
  | "positive"
  | "caution"
  | "negative";

export type ResearchHeaderVariant =
  | "cycle"
  | "futures"
  | "sentiment"
  | "events";

export type ResearchHeaderFact = {
  id: string;
  label: string;
  value: ReactNode;
  tone?: ResearchHeaderTone;
  showIndicator?: boolean;
};

export type ResearchHeaderAction = {
  id: string;
  label: string;
  kind: "primary" | "secondary";
  title?: string;
  disabled?: boolean;
  onClick: () => void;
};

export type ResearchHeaderMeta = {
  id: string;
  label: ReactNode;
};

type ResearchHeaderProps = {
  titleId: string;
  variant: ResearchHeaderVariant;
  eyebrow: string;
  kicker: string;
  title: ReactNode;
  transition?: ReactNode;
  summary: ReactNode;
  detail?: ReactNode;
  facts?: ResearchHeaderFact[];
  actions?: ResearchHeaderAction[];
  actionFeedback?: ReactNode;
  notice?: ReactNode;
  meta?: ResearchHeaderMeta[];
};

function ResearchHeader({
  titleId,
  variant,
  eyebrow,
  kicker,
  title,
  transition,
  summary,
  detail,
  facts = [],
  actions = [],
  actionFeedback,
  notice,
  meta = [],
}: ResearchHeaderProps) {
  return (
    <section
      className={`research-header research-header--${variant}`}
      aria-labelledby={titleId}
    >
      <div className="research-header__top">
        <span className="research-header__eyebrow">{eyebrow}</span>
        {actions.length > 0 ? (
          <div className="research-header__action-area">
            <div className="research-header__actions">
              {actions.map((action) => (
                <button
                  className={`research-header__action research-header__action--${action.kind}`}
                  disabled={action.disabled}
                  key={action.id}
                  onClick={action.onClick}
                  title={action.title}
                  type="button"
                >
                  {action.label}
                </button>
              ))}
            </div>
            {actionFeedback ? (
              <span className="research-header__action-feedback">{actionFeedback}</span>
            ) : null}
          </div>
        ) : null}
      </div>
      <div className="research-header__grid">
        <div className="research-header__copy">
          <span className="research-header__kicker">{kicker}</span>
          <h2 id={titleId}>{title}</h2>
          {transition ? <strong className="research-header__transition">{transition}</strong> : null}
          <p className="research-header__summary">{summary}</p>
          {detail ? <small className="research-header__detail">{detail}</small> : null}
        </div>
        {facts.length > 0 ? (
          <aside className="research-header__facts">
            {facts.map((fact) => {
              const tone = fact.tone || "neutral";
              return (
                <div className="research-header__fact" key={fact.id}>
                  <span>{fact.label}</span>
                  <strong className={`research-header__fact-value research-header__fact-value--${tone}`}>
                    {fact.showIndicator ? <i className="research-header__state-dot" /> : null}
                    {fact.value}
                  </strong>
                </div>
              );
            })}
          </aside>
        ) : null}
      </div>
      {notice ? <div className="research-header__notice">{notice}</div> : null}
      {meta.length > 0 ? (
        <div className="research-header__meta">
          {meta.map((item) => <span key={item.id}>{item.label}</span>)}
        </div>
      ) : null}
    </section>
  );
}

export default ResearchHeader;
```

- [ ] **Step 4: 승인된 공통 CSS 토큰 구현**

`style.css`에는 다음 selector와 값을 명시적으로 둔다.

```css
.research-header {
  --research-accent: #397da8;
  padding: 24px 26px;
  border: 1px solid #d9e5e8;
  border-radius: 21px;
  background:
    radial-gradient(circle at 91% 12%, rgb(79 143 199 / 15%), transparent 33%),
    radial-gradient(circle at 10% 100%, rgb(57 164 127 / 7%), transparent 28%),
    linear-gradient(135deg, #fbfcfd, #f3f8f6);
  box-shadow: 0 14px 34px rgb(30 56 75 / 7%);
}

.research-header--sentiment { --research-accent: #8a5d3b; }
.research-header--events { --research-accent: #0f766e; }
.research-header__top,
.research-header__actions,
.research-header__fact-value,
.research-header__meta { display: flex; }
.research-header__top { align-items: center; justify-content: space-between; gap: 16px; min-height: 31px; }
.research-header__grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(165px, .22fr); align-items: end; gap: 24px; margin-top: 15px; }
.research-header__eyebrow { color: var(--research-accent); font-size: 10px; font-weight: 900; letter-spacing: .11em; text-transform: uppercase; }
.research-header h2 { margin: 6px 0 0; color: #172536; font-size: 34px; font-weight: 900; letter-spacing: -.045em; line-height: 1.07; }
.research-header__fact { display: grid; gap: 4px; padding: 10px 11px; border: 1px solid rgb(185 201 213 / 82%); border-radius: 10px; background: rgb(255 255 255 / 76%); }
.research-header__state-dot { width: 6px; height: 6px; flex: 0 0 6px; border-radius: 50%; background: currentColor; }

@media (max-width: 760px) {
  .research-header__grid { grid-template-columns: 1fr; }
  .research-header__facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 480px) {
  .research-header { padding: 20px 18px; }
  .research-header__top { align-items: flex-start; flex-wrap: wrap; }
  .research-header h2 { font-size: 28px; }
  .research-header__facts { grid-template-columns: 1fr; }
}
```

같은 파일에서 action, kicker, transition, summary, detail, notice, meta의 spacing과 `neutral/info/positive/caution/negative` 색상을 완성한다. 사실 카드 selector에는 `border-left`를 넣지 않는다.

- [ ] **Step 5: 공통 계약 테스트 통과 확인**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_header_system.py -q
```

Expected: 2 tests PASS.

- [ ] **Step 6: Task 1 커밋**

```bash
git add tests/test_market_research_header_system.py \
  app/web/streamlit_components/market_research_header
git commit -m "Market Research 공통 헤더 계약 추가"
```

---

### Task 2: 경제사이클과 선물매크로 adapter 전환

**Files:**
- Modify: `tests/test_market_research_header_system.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx:1194`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css:24`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx:1`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css:25`

**Interfaces:**
- Consumes: Task 1의 `ResearchHeader`, `ResearchHeaderFact`, `ResearchHeaderMeta`, `ResearchHeaderTone`
- Produces: 경제사이클과 선물매크로의 기존 payload를 공통 표시 props로 변환하는 adapter

- [ ] **Step 1: 두 화면 adapter 실패 테스트 추가**

```python
def test_cycle_and_futures_use_shared_header_without_left_status_border() -> None:
    cycle = (ROOT / "economic_cycle_workbench/src/EconomicCycleWorkbench.tsx").read_text(encoding="utf-8")
    futures = (ROOT / "futures_macro_workbench/src/MacroContextSection.tsx").read_text(encoding="utf-8")

    for source in (cycle, futures):
        assert 'from "../../market_research_header/ResearchHeader"' in source
        assert "<ResearchHeader" in source

    assert 'variant="cycle"' in cycle
    assert 'label: "데이터 기준"' in cycle
    assert 'label: "검증 상태"' in cycle
    assert "showIndicator: true" in cycle

    assert 'variant="futures"' in futures
    assert 'label: "관측 상태"' in futures
    assert 'label: "기준일"' in futures
    assert 'label: "관측 범위"' in futures
    assert "hasPendingSession" in futures
    assert "hero.evidence.slice(0, 3)" in futures
    assert "pendingActionId === action.id" in futures
```

- [ ] **Step 2: 새 테스트 실패 확인**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_market_research_header_system.py \
  tests/test_market_context_economic_cycle.py \
  tests/test_overview_futures_macro_short_horizon.py -q
```

Expected: new shared-header assertions FAIL; existing domain tests remain PASS.

- [ ] **Step 3: 경제사이클 헤더 adapter 구현**

`EconomicCycleWorkbench.tsx`에서 legacy `<header className="cycle-hero">`를 제거하고 아래 mapping을 `ResearchHeader`에 전달한다.

```tsx
const estimateTone: ResearchHeaderTone =
  currentState === "VERIFIED"
    ? "positive"
    : currentState === "PROVISIONAL"
      ? "caution"
      : "neutral";

const cycleFacts: ResearchHeaderFact[] = [
  { id: "as-of", label: "데이터 기준", value: payload.as_of_date || "-" },
  {
    id: "estimate",
    label: "검증 상태",
    value: ESTIMATE_LABEL[currentState],
    tone: estimateTone,
    showIndicator: true,
  },
];

const cycleMeta: ResearchHeaderMeta[] = [
  { id: "horizons", label: "현재 · +1개월 · +2개월" },
  ...(payload.intramonth
    ? [{ id: "intramonth", label: "월중 추정 별도 표시" }]
    : []),
];

<ResearchHeader
  eyebrow="U.S. ECONOMIC CYCLE"
  facts={cycleFacts}
  kicker="현재 경기 위치"
  meta={cycleMeta}
  summary={payload.headline?.summary || "저장된 경제사이클 결과를 확인합니다."}
  title={`${payload.headline?.phase_label || "판단 불가"} ${current?.dominant_phase ? "우세" : ""}`.trim()}
  titleId="cycle-hero-title"
  variant="cycle"
/>;
```

legacy `.cycle-hero`, `.hero-basis`, `.hero-status` CSS는 삭제하고 본문 section CSS는 변경하지 않는다.

- [ ] **Step 4: 선물매크로 헤더 adapter 구현**

`MacroContextSection.tsx`에서 기존 pending session 판정과 action callback을 유지하며 공통 props를 만든다.

```tsx
const observationTone: ResearchHeaderTone =
  hero.observation_status === "OBSERVED"
    ? "info"
    : hero.observation_status === "PARTIAL"
      ? "caution"
      : "neutral";

const facts: ResearchHeaderFact[] = [
  {
    id: "observation",
    label: "관측 상태",
    value: OBSERVATION_LABEL[hero.observation_status],
    tone: observationTone,
    showIndicator: true,
  },
  { id: "as-of", label: "기준일", value: hero.as_of_date || "-" },
  { id: "coverage", label: "관측 범위", value: hero.coverage_label || "-" },
];

const actions: ResearchHeaderAction[] = command.actions.map((action) => ({
  id: action.id,
  label: pendingActionId === action.id ? "요청 중" : action.label,
  kind: action.kind,
  title: action.detail,
  disabled: pendingActionId === action.id,
  onClick: () => onAction(action),
}));

const notice = hasPendingSession ? (
  <>
    <strong>{sessionEvidence.pending_session} 데이터는 완료 전이라 현재 위치와 전망에서 제외했습니다.</strong>
    <span>화면은 마지막 완료 세션 {sessionEvidence.latest_final_session || hero.as_of_date} 기준입니다.</span>
  </>
) : undefined;

<ResearchHeader
  actions={actions}
  detail={hero.today_summary ? <>오늘의 재가격화 · {hero.today_summary}</> : undefined}
  eyebrow="FUTURES MACRO"
  facts={facts}
  kicker={hero.kicker}
  meta={hero.evidence.slice(0, 3).map((label, index) => ({ id: `evidence-${index}`, label }))}
  notice={notice}
  summary={hero.summary}
  title={hero.title}
  titleId="fm-hero-title"
  transition={hero.transition_label}
  variant="futures"
/>;
```

legacy `.fm-workbench__hero*`, `.fm-workbench__command-row`, `.fm-workbench__session-notice` 중 공통 헤더에서 대체된 규칙만 삭제한다. 나머지 `fm-workbench` section 스타일은 보존한다.

- [ ] **Step 5: 관련 회귀 테스트 통과 확인**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_market_research_header_system.py \
  tests/test_market_context_economic_cycle.py \
  tests/test_overview_futures_macro_short_horizon.py \
  tests/test_service_contracts.py -q
```

Expected: PASS. `test_service_contracts.py`에서 legacy hero class를 직접 요구하는 assertion이 발견되면 동일 테스트 안에서 `ResearchHeader`와 shared import assertion으로 교체하고 의미·action assertions는 유지한다.

- [ ] **Step 6: Task 2 커밋**

```bash
git add tests/test_market_research_header_system.py \
  tests/test_service_contracts.py \
  app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx \
  app/web/streamlit_components/economic_cycle_workbench/src/style.css \
  app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx \
  app/web/streamlit_components/futures_macro_workbench/src/style.css
git commit -m "경제사이클과 선물매크로 헤더 통일"
```

---

### Task 3: 심리와 일정 adapter 전환

**Files:**
- Modify: `tests/test_market_research_header_system.py`
- Modify: `tests/test_service_contracts.py:8507`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentHero.tsx:1`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css:30`
- Modify: `app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx:670`
- Modify: `app/web/streamlit_components/events_workbench/src/style.css:19`

**Interfaces:**
- Consumes: Task 1의 공통 header types와 Task 2에서 검증된 adapter pattern
- Produces: 심리와 일정의 공통 header props mapping; 기존 본문과 event command panel 보존

- [ ] **Step 1: 심리·일정 adapter 실패 테스트 추가**

```python
def test_sentiment_and_events_use_shared_header_with_existing_payload_values() -> None:
    sentiment = (ROOT / "sentiment_workbench/src/SentimentHero.tsx").read_text(encoding="utf-8")
    events = (ROOT / "events_workbench/src/EventsWorkbench.tsx").read_text(encoding="utf-8")

    for source in (sentiment, events):
        assert 'from "../../market_research_header/ResearchHeader"' in source
        assert "<ResearchHeader" in source

    assert 'variant="sentiment"' in sentiment
    assert "payload.axes.market_behavior.tone" in sentiment
    assert "payload.axes.investor_survey.tone" in sentiment
    assert "pendingActionLabel" in sentiment
    assert "합성점수 없음" in sentiment
    assert "매수·매도 신호 아님" in sentiment

    assert 'variant="events"' in events
    assert 'label: "다음 이벤트"' in events
    assert "brief.next_event" in events
    assert "counts.today" in events
    assert "counts.this_week" in events
    assert "counts.next_30d" in events
    assert "freshness.stale_estimate_count" in events
    assert "showIndicator" not in events[events.index("const eventFacts") : events.index("<ResearchHeader")]
```

- [ ] **Step 2: 새 테스트 실패 확인**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_market_research_header_system.py \
  tests/test_service_contracts.py -q
```

Expected: shared-header assertions FAIL before adapter changes.

- [ ] **Step 3: 심리 tone mapping과 공통 헤더 구현**

`SentimentHero.tsx`에 service의 기존 tone 문자열을 표시 enum으로만 정규화하는 local helper를 둔다.

```tsx
function sentimentTone(value: string): ResearchHeaderTone {
  if (value === "positive") return "positive";
  if (value === "warning") return "caution";
  if (value === "danger") return "negative";
  return value === "primary" ? "info" : "neutral";
}
```

facts/actions/meta를 기존 payload에서 직접 구성한다.

```tsx
const facts: ResearchHeaderFact[] = [
  {
    id: "cnn",
    label: "CNN 시장 행동",
    value: payload.axes.market_behavior.direction_label,
    tone: sentimentTone(payload.axes.market_behavior.tone),
    showIndicator: true,
  },
  {
    id: "aaii",
    label: "AAII 투자자 설문",
    value: payload.axes.investor_survey.direction_label,
    tone: sentimentTone(payload.axes.investor_survey.tone),
    showIndicator: true,
  },
];

const actions: ResearchHeaderAction[] = payload.command.actions.map((action) => ({
  id: action.id,
  label: action.label,
  kind: action.kind,
  title: action.detail,
  onClick: () => onAction(action),
}));

<ResearchHeader
  actionFeedback={pendingActionLabel ? <>요청 전송 · {pendingActionLabel}</> : undefined}
  actions={actions}
  detail={payload.cross_read.confidence_note}
  eyebrow="MARKET PSYCHOLOGY · CROSS READ"
  facts={facts}
  kicker={payload.cross_read.status}
  meta={[
    { id: "cnn-date", label: <>CNN {payload.axes.market_behavior.latest_date || "-"}</> },
    { id: "aaii-date", label: <>AAII {payload.axes.investor_survey.latest_date || "-"}</> },
    { id: "no-score", label: "합성점수 없음" },
    { id: "no-trade", label: "매수·매도 신호 아님" },
    ...(payload.freshness.stale_count > 0
      ? [{ id: "stale", label: <>stale {payload.freshness.stale_count} · 상세 근거 확인</> }]
      : []),
  ]}
  summary={payload.cross_read.meaning}
  title={payload.summary.headline}
  titleId="sentiment-hero-title"
  transition={payload.summary.phase_label}
  variant="sentiment"
/>;
```

legacy hero/command/side/meta CSS만 제거하고 source box, history, outlook, watch CSS는 유지한다.

- [ ] **Step 4: 일정의 분리된 두 카드 hero를 공통 shell로 통합**

`EventsWorkbench.tsx`에서 기존 `brief`, `counts`, `freshness` 값을 사용한다.

```tsx
const eventFacts: ResearchHeaderFact[] = [
  {
    id: "next-event",
    label: "다음 이벤트",
    value: brief.next_event
      ? `${brief.next_event.date} · ${brief.next_event.title}`
      : "예정 없음",
  },
];

const eventMeta: ResearchHeaderMeta[] = [
  { id: "today", label: <>오늘 {counts.today}건</> },
  { id: "week", label: <>이번 주 {counts.this_week}건</> },
  { id: "next-30d", label: <>30일 내 {counts.next_30d}건</> },
  { id: "stale", label: <>오래된 추정 {freshness.stale_estimate_count}건</> },
];

<ResearchHeader
  eyebrow="MARKET EVENTS"
  facts={eventFacts}
  kicker="다가오는 시장 이벤트 브리프"
  meta={eventMeta}
  summary={brief.boundary_note}
  title={brief.title || "다가오는 시장 이벤트 브리프"}
  titleId="events-hero-title"
  variant="events"
/>;
```

기존 `.events-workbench__hero-copy`와 `.events-workbench__next-card`만 제거한다. 바로 아래 6개 count tile, command, filter, rail, trust, calendar, evidence는 markup과 동작을 유지한다.

- [ ] **Step 5: stale source assertions를 공통 계약 기준으로 갱신**

`tests/test_service_contracts.py`에서 다음 legacy assertion만 교체한다.

- `sentiment-workbench__command-row`, `sentiment-workbench__hero-side`, `sentiment-workbench__hero-meta`, `.sentiment-workbench__hero`
  - `ResearchHeader`, `payload.command.actions.map`, 두 axis payload, `actionFeedback`, shared import assertion으로 교체
- `.events-workbench__hero`
  - `ResearchHeader`, `brief.next_event`, 기존 count / command / filter / calendar assertion으로 교체

source ordering, payload schema, Streamlit dispatch, current evidence, chart, outlook, calendar와 trust assertions는 삭제하지 않는다.

- [ ] **Step 6: 네 화면 source-contract 회귀 통과 확인**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_market_research_header_system.py \
  tests/test_market_context_economic_cycle.py \
  tests/test_overview_futures_macro_short_horizon.py \
  tests/test_service_contracts.py -q
```

Expected: PASS.

- [ ] **Step 7: Task 3 커밋**

```bash
git add tests/test_market_research_header_system.py \
  tests/test_service_contracts.py \
  app/web/streamlit_components/sentiment_workbench/src/SentimentHero.tsx \
  app/web/streamlit_components/sentiment_workbench/src/style.css \
  app/web/streamlit_components/events_workbench/src/EventsWorkbench.tsx \
  app/web/streamlit_components/events_workbench/src/style.css
git commit -m "심리와 일정 헤더 통일"
```

---

### Task 4: 네 Vite bundle과 static distribution 검증

**Files:**
- Modify: `tests/test_market_research_header_system.py`
- Rebuild: `app/web/streamlit_components/economic_cycle_workbench/component_static/`
- Rebuild: `app/web/streamlit_components/futures_macro_workbench/component_static/`
- Rebuild: `app/web/streamlit_components/sentiment_workbench/component_static/`
- Rebuild: `app/web/streamlit_components/events_workbench/component_static/`

**Interfaces:**
- Consumes: Task 1~3의 shared source imports
- Produces: 각 독립 Streamlit wrapper가 읽는 canonical static bundle

- [ ] **Step 1: 네 static entry의 상대 asset 계약 테스트 추가**

```python
import re

WORKBENCHES = (
    "economic_cycle_workbench",
    "futures_macro_workbench",
    "sentiment_workbench",
    "events_workbench",
)


def test_market_research_header_workbench_static_entries_reference_existing_assets() -> None:
    for name in WORKBENCHES:
        static_root = ROOT / name / "component_static"
        entry = static_root / "index.html"
        assert entry.is_file(), name
        source = entry.read_text(encoding="utf-8")
        assert 'src="/assets/' not in source
        assert 'href="/assets/' not in source
        references = re.findall(r'(?:src|href)="\./([^"?#]+)', source)
        assert references, name
        for reference in references:
            assert (static_root / reference).is_file(), f"{name}: {reference}"
```

- [ ] **Step 2: source 변경 후 build 전 계약 상태 확인**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_header_system.py -q
```

Expected: source tests PASS. Static asset test may still PASS against old bundles, but does not yet prove shared header inclusion.

- [ ] **Step 3: 네 package를 각각 빌드**

Run:

```bash
npm run build --prefix app/web/streamlit_components/economic_cycle_workbench
npm run build --prefix app/web/streamlit_components/futures_macro_workbench
npm run build --prefix app/web/streamlit_components/sentiment_workbench
npm run build --prefix app/web/streamlit_components/events_workbench
```

Expected: each Vite command exits `0`; new `component_static/index.html` references existing relative hashed CSS/JS assets.

- [ ] **Step 4: build output과 전체 회귀 검증**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_market_research_header_system.py \
  tests/test_market_context_economic_cycle.py \
  tests/test_overview_futures_macro_short_horizon.py \
  tests/test_service_contracts.py -q
git diff --check
```

Expected: PASS; whitespace error 없음.

- [ ] **Step 5: Task 4 커밋**

```bash
git add tests/test_market_research_header_system.py \
  app/web/streamlit_components/economic_cycle_workbench/component_static \
  app/web/streamlit_components/futures_macro_workbench/component_static \
  app/web/streamlit_components/sentiment_workbench/component_static \
  app/web/streamlit_components/events_workbench/component_static
git commit -m "Market Research 공통 헤더 정적 빌드 갱신"
```

---

### Task 5: 실제 Browser QA와 문서 closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-header-system-v1-20260725/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-header-system-v1-20260725/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-header-system-v1-20260725/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-header-system-v1-20260725/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate but do not commit: `market-research-header-system-v1-qa.png`

**Interfaces:**
- Consumes: Task 4의 canonical bundles와 running Streamlit app
- Produces: `3/3차` closeout evidence, durable ownership note와 한 장의 user-facing QA screenshot

- [ ] **Step 1: 구현 후 최종 자동 회귀 실행**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_market_research_header_system.py \
  tests/test_market_context_economic_cycle.py \
  tests/test_overview_futures_macro_short_horizon.py \
  tests/test_service_contracts.py -q
git diff --check
git status --short
```

Expected: tests PASS; implementation files만 intended diff로 남고 기존 registry/research/run-history/QA artifact는 분리되어 있다.

- [ ] **Step 2: Browser skill로 네 화면 desktop QA**

브라우저에서 `http://localhost:8501/overview?overview_tab=<view>`의 실제 Market Research navigation을 사용해 `경제 사이클`, `선물 매크로`, `심리`, `일정`을 각각 연다.

각 화면 1280px에서 확인한다.

- 제목 `34px`과 동일한 시작 위계
- facts 1~3개가 동일한 중립 박스
- 컬러 좌측 테두리 없음
- 상태 점이 상태 문구 옆에만 존재
- 경제사이클/일정에 빈 action 영역 없음
- 선물매크로/심리 action이 기존 Python event를 유지
- 일정의 count grid와 command panel이 헤더 아래 그대로 존재
- console error와 수평 overflow 없음

- [ ] **Step 3: 760px와 420px 반응형 QA**

각 화면에서 760px와 420px viewport를 확인한다.

- 760px: copy 위, facts 아래 1~2열
- 420px: title `28px`, facts 1열, top/actions wrap
- 긴 심리 headline과 선물매크로 action label이 잘리지 않음
- pending notice와 meta chip 자연 wrap
- 페이지와 component iframe 수평 overflow 없음

- [ ] **Step 4: 최종 QA 스크린샷 저장**

가장 정보량이 많은 선물매크로 desktop 또는 네 화면 비교가 가능한 상태를 `market-research-header-system-v1-qa.png`로 저장한다. 이는 generated artifact이므로 stage하지 않는다.

- [ ] **Step 5: finance-doc-sync로 closeout 문서 정렬**

문서에는 다음 결론을 남긴다.

- shared source owner: `app/web/streamlit_components/market_research_header/`
- consumers: 경제사이클, 선물매크로, 심리, 일정 workbench
- data / payload / dispatch boundary unchanged
- roadmap `3/3차` 완료와 실제 QA viewport
- 남은 실제 검증 공백이 있으면 `RISKS.md`에 유지하고 완료로 과장하지 않음

- [ ] **Step 6: closeout 검증**

Run:

```bash
git diff --check
git status --short
```

Expected: 문서 whitespace error 없음; generated screenshot과 기존 사용자 artifact는 untracked/unstaged 상태.

- [ ] **Step 7: Task 5 커밋**

```bash
git add \
  .aiworkspace/note/finance/tasks/active/market-research-header-system-v1-20260725 \
  .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "Market Research 헤더 통일 QA와 문서 정렬"
```

Do not add `market-research-header-system-v1-qa.png`, `.superpowers/`, registry JSONL, research bundle, or run history.
