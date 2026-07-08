# Development Guidelines

Status: Active
Last Updated: 2026-06-29 KST

## Operating Principle

이번 Backtest 개선은 "가이드 추가"가 아니다.
개발 세션은 화면의 기본 흐름을 줄이고, 사용자가 실제로 해야 할 일을 더 빨리 끝내게 만드는 방향으로 진행한다.

금지:

- 새 guide expander 추가
- Reference help를 Backtest Analysis에 다시 노출
- 새 evidence/workbench panel을 기본 화면에 추가
- Data Trust / readiness 경고를 숨김
- Practical Validation / Final Review / Monitoring 경계를 암묵적으로 변경

## Phase 1 Implementation Guideline

Title: Backtest Analysis Default Surface Cleanup

Goal:

- Backtest first viewport를 manual이 아니라 workbench로 만든다.
- `Backtest 사용 안내`와 `Reference help`를 제거한다.
- `Backtest Analysis -> Practical Validation -> Final Review` 흐름은 유지한다.

Likely files:

- `app/web/pages/backtest.py`
- `app/web/backtest_analysis.py`
- `app/web/backtest_ui_components.py` only if a reusable compact header is needed
- tests only if existing tests assert old Reference/help behavior

Detailed steps:

1. Read `PROJECT_MAP.md`, `BACKTEST_UI_FLOW.md`, and this research bundle.
2. Confirm current render path:
   - `render_backtest_tab`
   - `_render_backtest_panel_selector`
   - `render_backtest_analysis_workspace`
   - `_render_backtest_analysis_research_reference_board`
3. Remove the top `Backtest 사용 안내` expander.
4. Replace it with a compact stage/action header:
   - Stage: `1 Backtest Analysis`, `2 Practical Validation`, `3 Final Review`
   - Current purpose: `후보 source 만들기`
   - Next action: selected active panel based message
5. Remove `render_reference_contextual_help("backtest_analysis")` from Backtest Analysis.
6. Remove or hide `_render_backtest_analysis_research_reference_board` from the default render path.
7. Do not delete service files in 1차 unless tests prove they are unused and user approved physical cleanup.
8. Browser QA `/backtest` first viewport.

Acceptance criteria:

- No `Backtest 사용 안내` block in first viewport.
- No `Reference help - Backtest > Backtest Analysis` in Backtest Analysis.
- No visible `전략 개발 참고` section in the default Backtest Analysis path.
- User can still switch `Backtest Analysis`, `Practical Validation`, `Final Review`.
- Single Strategy and Portfolio Mix Builder still render.
- No registry/saved/run_history/generated artifacts are staged.

Verification:

- `git status --short`
- `git diff --check`
- `.venv/bin/python -m py_compile app/web/pages/backtest.py app/web/backtest_analysis.py`
- relevant focused tests if any Reference/help tests fail
- Browser QA at `http://localhost:8525/backtest`

## Phase 2 Implementation Guideline

Title: Latest Backtest Run Summary-First Redesign

Goal:

- Remove repetitive A/B/C/D guide cards and convert result display into summary-first artifact.
- Preserve data warnings and details in a compact, action-linked way.

Likely files:

- `app/web/backtest_result_display.py`
- `app/services/backtest_result_read_model.py`
- tests for result read model or helper

Detailed steps:

1. Build a Streamlit-free helper that returns:
   - strategy name/key
   - requested vs actual period
   - top performance metrics
   - data state
   - handoff state
   - top warning reason
2. Replace `_render_latest_run_orientation` with a compact `Run Overview`.
3. Keep Data Trust detail but move long details into disclosure.
4. Keep tabs but reorganize:
   - Overview / Performance
   - Selection or Holdings when applicable
   - Policy / Assumptions when applicable
   - Raw Result / Meta
5. Do not remove raw data access.
6. Browser QA with at least one existing or newly run result.

Acceptance criteria:

- Latest Run starts with result summary and next action, not a reading guide.
- Data Trust warning is visible but not repeated in multiple blocks.
- Raw meta and result table remain accessible.
- Quarterly/Risk-On caveats remain visible when relevant.

## Phase 3 Implementation Guideline

Title: Validation Handoff Eligibility Policy

Goal:

- Replace pseudo-score readiness with action eligibility.

Policy:

- Hard block only when Practical Validation cannot consume the source:
  - no result bundle
  - no result rows / curve
  - unsupported strategy lane
  - missing source/replay contract
- Review but allow when:
  - data freshness warning
  - promotion hold/caution
  - provider/liquidity/benchmark caveat
  - warnings that Practical Validation is meant to inspect

Likely files:

- `app/web/backtest_result_display.py`
- `app/services/backtest_result_read_model.py` or new service
- possible tests

Acceptance criteria:

- UI uses three states:
  - `검증으로 보낼 수 있음`
  - `보낼 수 있지만 확인 필요`
  - `아직 보낼 수 없음`
- The copy does not say recommendation / approval / live ready.
- Detailed criteria are in disclosure.
- Practical Validation still owns the real evidence gate.

## Phase 4 Implementation Guideline

Title: Strategy Maturity Chips

Goal:

- Replace strategy maturity panels with compact labels.

Suggested labels:

- `후보 source`
- `근거 보강 필요`
- `Research lane`
- `Prototype`
- `Baseline / sleeve`

Likely mapping:

- Strict Annual Quality / Value / Quality+Value: `후보 source`
- GTAA: `후보 source / tactical sleeve`
- Equal Weight: `Baseline / sleeve`
- GRS / Risk Parity / Dual Momentum: `근거 보강 필요`
- Risk-On Momentum 5D: `Research lane`
- Strict Quarterly variants: `Prototype`

Acceptance criteria:

- Label appears near strategy selection/result overview.
- No full maturity table in default Backtest Analysis.
- Labels are tested in a Streamlit-free helper.

## Phase 5 Implementation Guideline

Title: Portfolio Mix Builder Commercial Workbench

Goal:

- Make mix creation feel like a model portfolio lab.

Suggested layout:

1. Components selected / executed
2. Weight assignment
3. Mix result summary
4. Handoff status
5. Details / raw tables

Do not:

- redesign Practical Validation in this phase
- rewrite saved setup JSONL
- add new optimizer
- add broker/live trading semantics

## New Implementation Session Request Template

Use this after the user approves a phase.

```text
이 요청은 개발 진행 승인이다.

워크트리: /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
브랜치: codex/backtest-dev

먼저 아래 문서를 읽어줘.
- AGENTS.md
- .aiworkspace/note/finance/docs/INDEX.md
- .aiworkspace/note/finance/docs/ROADMAP.md
- .aiworkspace/note/finance/docs/PROJECT_MAP.md
- .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md
- .aiworkspace/note/finance/researches/active/2026-06-backtest-analysis-commercial-ux/RECOMMENDATION.md
- .aiworkspace/note/finance/researches/active/2026-06-backtest-analysis-commercial-ux/DEVELOPMENT_GUIDELINES.md

이번 차수: 1차 Backtest Analysis Default Surface Cleanup만 진행한다.

목표:
- Backtest 상단의 `Backtest 사용 안내` expander를 제거하고, compact stage/action header로 대체한다.
- Backtest Analysis에서 `Reference help - Backtest > Backtest Analysis`를 제거한다.
- 기본 Backtest Analysis 화면에서 `전략 개발 참고` / strategy development reference panels가 보이지 않게 한다.
- Backtest Analysis -> Practical Validation -> Final Review 흐름은 유지한다.
- Single Strategy와 Portfolio Mix Builder 기본 실행 흐름은 유지한다.

이번 차수에서 하지 말 것:
- Latest Backtest Run redesign은 하지 않는다.
- Practical Validation / Final Review / Operations / Monitoring behavior는 바꾸지 않는다.
- registry / saved JSONL / run_history / generated artifact를 rewrite하거나 stage하지 않는다.
- provider / FRED / yfinance를 UI render 중 직접 fetch하지 않는다.
- 새 guide expander, 새 evidence panel, 새 workbench panel을 추가하지 않는다.
- live approval, broker order, account sync, auto rebalance 의미를 추가하지 않는다.

주요 파일:
- app/web/pages/backtest.py
- app/web/backtest_analysis.py
- 필요하면 app/web/backtest_ui_components.py

검증:
- git status --short
- git diff --check
- .venv/bin/python -m py_compile app/web/pages/backtest.py app/web/backtest_analysis.py
- 가능한 경우 관련 focused tests
- .venv/bin/streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
- Browser QA: http://localhost:8525/backtest 에서 첫 viewport, Backtest Analysis, Single Strategy / Portfolio Mix Builder 전환 확인
- QA 스크린샷 1장 최종 응답에 첨부

커밋:
- 구현과 검증이 끝나면 coherent commit을 만든다.
- commit message는 한국어로 작성한다.
- screenshot/generated artifact, run_history, registry/saved JSONL은 명시 없이는 stage하지 않는다.

최종 응답:
- 전체 roadmap 중 1차 완료 여부
- 핵심 변경 내용
- 변경한 파일
- 실행한 검증
- Browser QA 결과와 스크린샷
- 남은 리스크
- 다음 차수
- 커밋 해시
```
