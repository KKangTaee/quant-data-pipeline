# Economic Cycle Evidence Role-Aware Copy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Economic Cycle Evidence 행을 현재 수준과 전망 영향에 맞는 상태·색상·한 줄 해석으로 표시해 `강화=좋음` 오해를 제거한다.

**Architecture:** 기존 Python payload의 `factor`, `direction`, `value`, source 계약은 유지한다. React의 pure presentation helper가 factor 역할과 direction을 역할별 상태, tone, 설명으로 변환하고 Evidence renderer와 CSS는 그 결과만 표시한다.

**Tech Stack:** React 18, TypeScript, CSS, Streamlit custom component, pytest source-contract tests, Vite

## Global Constraints

- factor 계산, `±0.15` 임계값, 모델 확률, 국면 좌표, source와 payload 값은 변경하지 않는다.
- 기존 Evidence 패널과 두 그룹 구조를 유지한다.
- 좌측 강조선, 새 hover panel, 원시 지표 목록, 외부 수집을 추가하지 않는다.
- 역할별 상태 문구와 한 줄 해석을 항상 함께 표시한다.
- 모바일 420px에서 수평 overflow 없이 factor, badge, source, 설명을 읽을 수 있어야 한다.

---

### Task 1: 역할별 Evidence presentation 계약

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py:230-270`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx:32-40,215-220,517-530,980-990`

**Interfaces:**
- Consumes: `Evidence.factor`, `Evidence.direction`, `Evidence.source_date`, `Evidence.source_basis`
- Produces: `resolveEvidencePresentation(item: Evidence): EvidencePresentation`
- Produces: `EvidencePresentation = { statusLabel: string; tone: EvidenceTone; description: string }`

- [ ] **Step 1: 실패하는 source contract 추가**

기존 component source contract에 다음 token과 제거 조건을 추가한다.

```python
for token in (
    "현재 수준과 전망 영향을 구분해 표시",
    'financial_leading_score: "금융·선행 여건"',
    'statusLabel: "기준 이상"',
    'statusLabel: "기준 이하"',
    'statusLabel: "기준 부근"',
    'statusLabel: "전망 지원"',
    'statusLabel: "전망 부담"',
    'statusLabel: "부담 완화"',
    'statusLabel: "영향 중립"',
    "자기 과거 기준보다 낮아 현재 경기 위치를 낮추는 근거입니다",
    "향후 1·2개월 경기 전망을 지지하는 방향입니다",
    "향후 1·2개월 경기 전망에 부담을 주는 방향입니다",
):
    assert token in source
assert "강화 · 약화 · 중립" not in source
```

- [ ] **Step 2: RED 확인**

Run: `uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py::test_cycle_component_source_contract_covers_full_reading_flow -q`

Expected: 새 token이 없어 FAIL.

- [ ] **Step 3: presentation type과 helper 구현**

```tsx
type EvidenceTone = "positive-level" | "weak-level" | "support" | "burden" | "neutral";
type EvidencePresentation = { statusLabel: string; tone: EvidenceTone; description: string };

function resolveEvidencePresentation(item: Evidence): EvidencePresentation {
  const direction = item.direction;
  if (item.factor === "activity_score" || item.factor === "labor_income_score") {
    const subject = item.factor === "activity_score" ? "생산·소비 관련 지표" : "고용·소득 관련 지표";
    if (direction === "강화") return { statusLabel: "기준 이상", tone: "positive-level", description: `${subject}의 종합점수가 자기 과거 기준보다 높아 현재 경기 위치를 지지하는 근거입니다.` };
    if (direction === "약화") return { statusLabel: "기준 이하", tone: "weak-level", description: `${subject}의 종합점수가 자기 과거 기준보다 낮아 현재 경기 위치를 낮추는 근거입니다.` };
    return { statusLabel: "기준 부근", tone: "neutral", description: `${subject}의 종합점수가 자기 과거 기준 부근으로 현재 경기 위치에 중립적인 근거입니다.` };
  }
  if (item.factor === "financial_leading_score") {
    if (direction === "강화") return { statusLabel: "전망 지원", tone: "support", description: "금리차·신용스프레드·금융여건·선행지표 조합이 향후 1·2개월 경기 전망을 지지하는 방향입니다." };
    if (direction === "약화") return { statusLabel: "전망 부담", tone: "burden", description: "금리차·신용스프레드·금융여건·선행지표 조합이 향후 1·2개월 경기 전망을 제약하는 방향입니다." };
  }
  if (item.factor === "inflation_policy_score") {
    if (direction === "강화") return { statusLabel: "전망 부담", tone: "burden", description: "근원물가·기대인플레이션·정책금리 조합의 압력이 높아 향후 1·2개월 경기 전망에 부담을 주는 방향입니다." };
    if (direction === "약화") return { statusLabel: "부담 완화", tone: "support", description: "근원물가·기대인플레이션·정책금리 조합의 압력이 낮아 향후 1·2개월 경기 전망의 부담이 완화된 상태입니다." };
  }
  return { statusLabel: "영향 중립", tone: "neutral", description: "현재 종합점수는 자기 과거 기준 부근으로 전망에 미치는 영향이 중립적입니다." };
}
```

`FACTOR_LABEL.financial_leading_score`는 `금융·선행 여건`, Evidence 상단 small copy는 `현재 수준과 전망 영향을 구분해 표시`로 바꾼다.

- [ ] **Step 4: EvidenceGroup 렌더링 변경**

```tsx
{rows.length ? rows.map((item, index) => {
  const presentation = resolveEvidencePresentation(item);
  return (
    <article key={`${item.factor}-${index}`} tabIndex={0}>
      <div className="evidence-row-heading">
        <strong>{FACTOR_LABEL[item.factor] || item.series_id || item.factor}</strong>
        <span className={`evidence-status evidence-tone-${presentation.tone}`}>{presentation.statusLabel}</span>
      </div>
      <small>{formatMonth(item.source_date)} · {item.source_basis || "PIT 기준"}</small>
      <p className="evidence-description">{presentation.description}</p>
    </article>
  );
}) : <p className="empty-copy">표시할 근거가 아직 없습니다.</p>}
```

- [ ] **Step 5: GREEN 확인**

Run: `uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py::test_cycle_component_source_contract_covers_full_reading_flow -q`

Expected: `1 passed`.

- [ ] **Step 6: Task 1 커밋**

```bash
git add tests/test_market_context_economic_cycle.py app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx
git commit -m "경제사이클 근거 역할별 문구 적용"
```

---

### Task 2: Evidence tone과 반응형 카드

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css:162-170, mobile media queries`

**Interfaces:**
- Consumes: Task 1의 `evidence-tone-*` class
- Produces: desktop/mobile Evidence row layout과 의미별 badge tone

- [ ] **Step 1: 실패하는 CSS contract 추가**

```python
def test_cycle_component_evidence_role_styles_are_present() -> None:
    source = Path("app/web/streamlit_components/economic_cycle_workbench/src/style.css").read_text()
    for token in (
        ".evidence-row-heading", ".evidence-description",
        ".evidence-tone-positive-level", ".evidence-tone-weak-level",
        ".evidence-tone-support", ".evidence-tone-burden", ".evidence-tone-neutral",
    ):
        assert token in source
```

- [ ] **Step 2: RED 확인**

Run: `uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py::test_cycle_component_evidence_role_styles_are_present -q`

Expected: 새 class가 없어 FAIL.

- [ ] **Step 3: 카드 layout과 badge tone 구현**

```css
.evidence-list article { display: grid; gap: 4px; padding: 10px; border: 1px solid #e5ebef; border-radius: 10px; background: #fff; outline: none; }
.evidence-row-heading { display: flex; align-items: center; justify-content: space-between; gap: 10px; min-width: 0; }
.evidence-row-heading strong { min-width: 0; overflow: hidden; color: #304b60; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.evidence-list small { color: #81909b; font-size: 9px; }
.evidence-description { margin-top: 3px; color: #657987; font-size: 9px; line-height: 1.5; }
.evidence-status { flex: 0 0 auto; min-width: 52px; padding: 5px 7px; border-radius: 7px; font-size: 9px; font-weight: 900; text-align: center; white-space: nowrap; }
.evidence-tone-positive-level, .evidence-tone-support { color: #1d6d5d; background: #e7f4ef; }
.evidence-tone-weak-level { color: #a55749; background: #fbeeea; }
.evidence-tone-burden { color: #8b641f; background: #fff1d2; }
.evidence-tone-neutral { color: #687985; background: #edf1f3; }
```

420px media query에는 heading과 설명의 줄바꿈 규칙을 추가한다.

```css
.evidence-row-heading { align-items: flex-start; }
.evidence-row-heading strong { white-space: normal; overflow-wrap: anywhere; }
.evidence-description { overflow-wrap: anywhere; }
```

- [ ] **Step 4: focused tests와 build 실행**

```bash
uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
```

Expected: tests PASS, Vite build exit 0.

- [ ] **Step 5: Task 2 커밋**

```bash
git add tests/test_market_context_economic_cycle.py app/web/streamlit_components/economic_cycle_workbench/src/style.css app/web/streamlit_components/economic_cycle_workbench/component_static
git commit -m "경제사이클 근거 카드 해석 UI 정리"
```

---

### Task 3: 회귀·Browser QA·문서 closeout

**Files:**
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generated only: `/tmp/codex-browser-qa/economic-cycle-evidence-role-copy-desktop.png`
- Generated only: `/tmp/codex-browser-qa/economic-cycle-evidence-role-copy-mobile.png`

**Interfaces:**
- Consumes: built Economic Cycle component and stored payload
- Produces: verified desktop/mobile flow and durable handoff summary

- [ ] **Step 1: fresh regression과 build 실행**

```bash
uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py tests/test_economic_cycle_service.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
git diff --check
```

Expected: all tests PASS, build exit 0, diff check output 없음.

- [ ] **Step 2: Browser QA 수행**

`Workspace > Overview > 시장맥락 > 경제 사이클`에서 상단 안내, 네 역할별 badge, 한 줄 설명, source 기준월을 확인한다. Desktop과 420px에서 horizontal overflow 0, console error 0을 확인한다.

- [ ] **Step 3: screenshot 저장**

두 screenshot을 `/tmp/codex-browser-qa/`에 저장하고 stage하지 않는다.

- [ ] **Step 4: Finance handoff log 정렬**

```markdown
## 2026-07-19 - 경제사이클 판단 근거 역할별 문구 완료

- 실물 factor는 과거 기준 대비 수준, 전망 factor는 전망 지원·부담으로 분리했다.
- 각 Evidence 행에 factor 역할과 방향을 설명하는 한 줄 해석을 추가했다.
- 모델 점수·임계값·확률·payload는 변경하지 않았다.
- focused tests, React build, desktop/mobile Browser QA를 완료했다.
```

- [ ] **Step 5: closeout 커밋**

```bash
git diff --check
git status --short
git add .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "경제사이클 판단 근거 문구 QA 마무리"
```
