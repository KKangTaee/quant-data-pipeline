# Final Review Decision Desk Card Layout V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Final Review Decision Desk의 6개 KPI를 3x2로 읽히게 하고, `오늘 먼저 볼 후보` 카드를 후보 / 이유 / 추천 근거 / 다음 행동 중심으로 구조화한다.

**Architecture:** 기존 Python read model과 Streamlit HTML helper 경계를 유지한다. Decision Desk는 React로 전환하지 않고, `page.py`가 표시 모델을 만들고 `components.py`가 구조화된 HTML/CSS를 렌더링한다.

**Tech Stack:** Python, Streamlit, custom HTML/CSS helper, service contract tests.

---

## 이걸 하는 이유?

현재 Decision Desk는 KPI grid가 화면 폭에 따라 4+2처럼 흐르고, `오늘 먼저 볼 후보` 카드가 긴 문장 하나로 후보명 / 이유 / 추천 근거 / 다음 행동을 이어 붙인다. 사용자는 Final Review 첫 화면에서 어떤 후보를 먼저 볼지와 왜 추천되는지를 빠르게 스캔해야 한다.

## Scope

- 6개 KPI를 desktop 3x2, tablet 2x3, mobile 1열로 표시한다.
- `오늘 먼저 볼 후보` 카드를 구조화된 field / badge 형태로 렌더링한다.
- 기존 Decision Desk shadow는 유지한다.
- React investment report, gate 계산, registry / saved write, Portfolio Monitoring 저장 경계는 변경하지 않는다.

## Steps

- [x] **Step 1: Write failing tests**
  - Add tests requiring structured `featured_candidate` fields and 3-column KPI grid CSS.
- [x] **Step 2: Verify RED**
  - Run the focused tests and confirm the missing fields / CSS fail.
- [x] **Step 3: Implement read model and render helper**
  - Add `featured_candidate` to `_build_final_review_decision_desk_model()`.
  - Extend `render_fr_command_center()` to render structured candidate fields and chips.
  - Set `.fr-kpi-grid` to 3 columns on desktop with responsive fallbacks.
- [x] **Step 4: QA**
  - Run focused service contract tests, py_compile, diff check, and Browser QA.
- [x] **Step 5: Commit**
  - Commit only code/tests/task docs. Leave run history and screenshots untracked.
