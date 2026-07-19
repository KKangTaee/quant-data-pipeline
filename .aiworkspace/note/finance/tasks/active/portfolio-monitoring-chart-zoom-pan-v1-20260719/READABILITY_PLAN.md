# Portfolio Monitoring Selected Chart Readability Follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 데스크톱의 종목·전략 목록과 선택 상세를 35:65로 재배분하고 선택 가격 차트의 X/Y축 라벨을 11px로 키워 차트 가독성을 높인다.

**Architecture:** 기존 React markup, data projection과 SVG viewBox는 유지하고 component-local CSS만 조정한다. Python static component contract가 열 비율, 축 타이포그래피와 900px 단일 열 경계를 고정하며, Vite production bundle을 재생성한다.

**Tech Stack:** React 18, TypeScript 5.7, SVG, CSS Grid, Python unittest static component contract, Vitest 4, Vite 6, Streamlit custom component

## Global Constraints

- 데스크톱 `pm-content-grid`는 종목·전략 목록 35%, 선택 상세 65%를 기본 비율로 사용한다.
- 목록 열은 `280px` 아래로 줄이지 않고 선택 상세 열은 남은 공간을 사용한다.
- 선택 가격 차트의 Y축 가격, `VOL`, X축 날짜는 SVG user-space 기준 `11px`, `font-weight: 700`을 사용한다.
- tooltip, 전체 Portfolio Monitoring 타이포그래피, React markup, data contract와 SVG viewBox는 변경하지 않는다.
- 기존 `@media (max-width: 900px)` 단일 열 전환과 420px controls-only 정책을 유지한다.
- 기존 wheel zoom, drag pan, line/candle viewport와 hover tooltip 동작을 변경하지 않는다.
- registry, saved JSONL, run history, `.superpowers/`와 generated QA PNG는 stage하지 않는다.

---

### Task 1: Desktop Layout And Axis Readability Contract

**Files:**
- Modify: `tests/test_portfolio_monitoring_component.py:70-103`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css:161-203`
- Rebuild: `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/`

**Interfaces:**
- Consumes: existing `.pm-content-grid`, `.pm-market-axis`, `.pm-market-date` and `@media (max-width: 900px)` selectors
- Produces: source/static bundle contract for `35:65`, minimum `280px` list width, 11px/700 axis labels and unchanged narrow-screen single column

- [x] **Step 1: Write the failing static component contract**

Insert this test after `test_market_chart_exposes_client_side_zoom_pan_controls` in `tests/test_portfolio_monitoring_component.py`:

```python
    def test_selected_chart_prioritizes_detail_width_and_readable_axes(self) -> None:
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertIn(
            ".pm-content-grid { display: grid; grid-template-columns: minmax(280px, .35fr) minmax(0, .65fr);",
            styles,
        )
        self.assertIn(
            ".pm-market-axis, .pm-market-date { fill: #63798a; font-size: 11px; font-weight: 700; }",
            styles,
        )
        self.assertRegex(
            styles,
            r"@media \(max-width: 900px\) \{[\s\S]*?\.pm-content-grid \{ grid-template-columns: 1fr; \}",
        )
```

- [x] **Step 2: Run the focused test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_component.PortfolioMonitoringComponentTests.test_selected_chart_prioritizes_detail_width_and_readable_axes -v
```

Expected: FAIL because the current stylesheet still contains `1.12fr/.88fr` and 9px axis labels.

- [x] **Step 3: Apply the minimum CSS implementation**

Replace the two existing rules in `src/style.css` with:

```css
.pm-content-grid { display: grid; grid-template-columns: minmax(280px, .35fr) minmax(0, .65fr); gap: 14px; }
```

```css
.pm-market-axis, .pm-market-date { fill: #63798a; font-size: 11px; font-weight: 700; }
```

Do not change `.pm-chart-tooltip`, `.pm-axis-label`, `.pm-axis-date`, SVG `width = 620`, SVG `height = 300`, or any React event handler.

- [x] **Step 4: Run focused and full source tests and confirm GREEN**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_component -v
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -v
```

Expected: focused component module 12 tests PASS and full Portfolio Monitoring suite 102 tests PASS.

- [x] **Step 5: Run React regression and typecheck**

Run:

```bash
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test
npm run typecheck
```

Expected: Vitest 24 tests PASS and TypeScript typecheck exits 0.

- [x] **Step 6: Rebuild the production component**

Run:

```bash
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm run build
```

Expected: Vite build exits 0, `component_static/index.html` references existing hashed CSS/JS assets, and no source map or QA PNG is created.

- [x] **Step 7: Verify the implementation diff and commit**

Run:

```bash
git diff --check
git status --short
git add tests/test_portfolio_monitoring_component.py \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css \
  app/web/streamlit_components/portfolio_monitoring_workbench/component_static
git diff --cached --check
git diff --cached --name-only
git commit -m "포트폴리오 선택 차트 가독성 개선"
```

Expected: staged files contain only the Python contract, source CSS and rebuilt component assets; `.superpowers/`, registries, saved data, run history and PNG files are excluded.

---

### Task 2: Responsive Browser QA And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/RISKS.md`
- Modify when QA closes: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify when QA closes: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify when QA closes: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: rebuilt production component at `Operations > Portfolio Monitoring`
- Produces: evidence that 35:65 desktop layout, 11px axes, zoom/pan and narrow-screen overflow contracts hold in the actual rendered app

- [ ] **Step 1: Perform desktop Browser QA**

Open `Operations > Portfolio Monitoring`, select a direct stock/ETF with a READY chart, and verify:

1. 종목·전략 목록은 약 35%, 선택 상세는 약 65%를 차지한다.
2. 목록의 종목명, 현재 가치와 기여 손익은 잘리거나 겹치지 않는다.
3. Y축 가격, `VOL`, X축 날짜를 별도 확대 없이 읽을 수 있다.
4. wheel zoom, horizontal drag, `− / + / 전체 보기`, line/candle 전환과 tooltip이 그대로 동작한다.
5. 차트 카드와 페이지 전체에 horizontal overflow가 없다.

- [ ] **Step 2: Perform 900px and 420px Browser QA**

At `900×900`, verify `.pm-content-grid` is one column with the list above the detail. At `420×900`, verify:

1. axis/date labels remain inside the chart shell;
2. range and zoom/mode controls wrap without overlap;
3. vertical page scroll remains available over the chart;
4. `document.documentElement.scrollWidth === document.documentElement.clientWidth`.

Save one desktop line-mode screenshot with the wider detail chart and readable axes as `portfolio-monitoring-chart-readability-qa.png`. Treat it as generated and do not stage it.

If in-app Browser security policy blocks the local URL, do not use alternate automation. Record the exact policy block in `RUNS.md` and keep Browser QA plus the 3/3 closeout status pending.

- [x] **Step 3: Synchronize task and root handoff status**

If Browser QA passes, record:

```markdown
- Current: 선택 차트 35:65 desktop layout, 11px axis readability, zoom/pan과 responsive Browser QA 완료
- Roadmap: 3/3차 완료
- Next: 없음. 목록 collapse와 전체 너비 세로 배치는 별도 승인 범위다.
```

If Browser QA is blocked, record:

```markdown
- Current: 선택 차트 35:65 desktop layout과 11px axis 구현 및 자동 회귀 완료, 실제 Browser interaction QA 대기
- Roadmap: 2/3차 완료, 3차 Browser QA 미완료
- Next: 정책상 허용된 in-app Browser에서 desktop/900px/420px layout·interaction·overflow 확인
```

Document actual test counts, viewport sizes, overflow outcome and screenshot path only when observed. Do not claim Browser QA from static tests.

- [x] **Step 4: Re-run final verification after documentation changes**

Run:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -v
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test
npm run typecheck
npm run build
cd ../../../..
git diff --check
git status --short
```

Expected: Python 102 tests PASS, Vitest 24 tests PASS, typecheck/build/diff-check PASS. Git status contains only intended docs/code/build changes plus pre-existing untracked generated artifacts.

- [x] **Step 5: Stage only closeout records and commit**

Run:

```bash
git add .aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719 \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git diff --cached --name-only
git commit -m "포트폴리오 차트 가독성 검증 기록"
```

Expected: staged names exclude `.aiworkspace/note/finance/registries/`, `.aiworkspace/note/finance/saved/`, run history, `.superpowers/` and all PNG files.
