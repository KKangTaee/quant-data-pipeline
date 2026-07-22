# Final Review Liquidity Evidence Copy V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This workspace executes inline because subagent dispatch is not enabled.

**Goal:** Level3 유동성 근거 카드에서 내부 enum을 숨기고 사용자가 현재 근거 상태와 통과 기준을 바로 이해하게 한다.

**Architecture:** `backtest_realism_audit.py`의 stable `proof_status`와 Gate 계약은 유지한다. `backtest_final_review_decision_brief.py`에 presentation-only 상태 매핑을 두고 raw enum은 `measured_value`, 사용자 문구는 `display_value`와 `threshold_or_comparator`로 분리한다. React는 전달된 read model을 그대로 표시한다.

**Tech Stack:** Python 3.12, unittest/pytest, Streamlit Final Review Decision Brief, React display-only component.

## Global Constraints

- 유동성 판정 기준, Gate, `proof_status` 생성 규칙을 변경하지 않는다.
- registry / saved JSONL / run history / generated screenshot을 stage하지 않는다.
- raw internal enum은 `measured_value`에 보존한다.
- 알 수 없는 신규 상태도 first-read에 raw enum을 노출하지 않는다.
- 카드 제목은 `유동성·운용 가능성 근거`, 기준은 `공식 제공처의 최신 유동성 근거 확보`로 표시한다.

---

### Task 1: Liquidity Evidence Presentation Adapter

**Files:**
- Modify: `tests/test_backtest_final_review_decision_brief.py`
- Modify: `app/services/backtest_final_review_decision_brief.py`

**Interfaces:**
- Produces: `_LIQUIDITY_CAPACITY_STATUS_LABELS: dict[str, str]`
- Produces: `_liquidity_capacity_status_label(proof_status: str) -> str`
- Preserves: `execution_observation["measured_value"] == proof_status`
- Changes display only: `title`, `interpretation`, `display_value`, `threshold_or_comparator`

- [x] **Step 1: Write the failing status mapping test**

```python
def test_liquidity_capacity_status_labels_cover_internal_contract(self) -> None:
    from app.services import backtest_final_review_decision_brief as service

    expected = {
        "official_fresh_capacity_evidence": "공식 제공처의 최신 유동성 근거 확보",
        "weak_source_or_proxy_liquidity_evidence": "공식 자료가 부족하거나 일부 대체 지표를 사용함",
        "partial_liquidity_coverage": "일부 구성요소의 유동성만 확인됨",
        "stale_or_unknown_provider_snapshot": "유동성 자료의 최신성 확인 필요",
        "provider_operability_review": "유동성 근거 추가 검토 필요",
        "missing_provider_operability": "유동성 근거가 아직 없음",
        "blocked_provider_operability": "가격 또는 제공처 문제로 유동성 확인 불가",
        "legacy_provider_pass_without_capacity_contract": "이전 형식 자료로 세부 유동성 근거 확인 필요",
        "incomplete_liquidity_capacity_evidence": "유동성 근거가 불완전함",
    }
    for status, label in expected.items():
        with self.subTest(status=status):
            self.assertEqual(service._liquidity_capacity_status_label(status), label)
    self.assertEqual(
        service._liquidity_capacity_status_label("future_internal_status"),
        "유동성 근거 상태 확인 필요",
    )
```

- [x] **Step 2: Write the failing Decision Brief display contract test**

```python
def test_liquidity_observation_uses_user_copy_and_preserves_raw_status(self) -> None:
    with patch(
        "app.services.backtest_final_review_decision_brief.build_liquidity_capacity_contract",
        return_value={"proof_status": "weak_source_or_proxy_liquidity_evidence"},
    ):
        brief = self._build(self._grs_inputs())

    observation = next(
        row
        for row in brief["behavior_board"]["execution_observations"]
        if row["observation_id"] == "liquidity-capacity"
    )
    self.assertEqual(observation["title"], "유동성·운용 가능성 근거")
    self.assertEqual(
        observation["measured_value"],
        "weak_source_or_proxy_liquidity_evidence",
    )
    self.assertEqual(
        observation["display_value"],
        "공식 자료가 부족하거나 일부 대체 지표를 사용함",
    )
    self.assertEqual(
        observation["threshold_or_comparator"],
        "공식 제공처의 최신 유동성 근거 확보",
    )
```

- [x] **Step 3: Run the two tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest -q \
  tests/test_backtest_final_review_decision_brief.py::FinalReviewDecisionBriefContractTests::test_liquidity_capacity_status_labels_cover_internal_contract \
  tests/test_backtest_final_review_decision_brief.py::FinalReviewDecisionBriefContractTests::test_liquidity_observation_uses_user_copy_and_preserves_raw_status
```

Expected: FAIL because the label helper does not exist and the current observation exposes raw enum text.

- [x] **Step 4: Implement the minimal presentation mapping**

```python
_LIQUIDITY_CAPACITY_STATUS_LABELS = {
    "official_fresh_capacity_evidence": "공식 제공처의 최신 유동성 근거 확보",
    "weak_source_or_proxy_liquidity_evidence": "공식 자료가 부족하거나 일부 대체 지표를 사용함",
    "partial_liquidity_coverage": "일부 구성요소의 유동성만 확인됨",
    "stale_or_unknown_provider_snapshot": "유동성 자료의 최신성 확인 필요",
    "provider_operability_review": "유동성 근거 추가 검토 필요",
    "missing_provider_operability": "유동성 근거가 아직 없음",
    "blocked_provider_operability": "가격 또는 제공처 문제로 유동성 확인 불가",
    "legacy_provider_pass_without_capacity_contract": "이전 형식 자료로 세부 유동성 근거 확인 필요",
    "incomplete_liquidity_capacity_evidence": "유동성 근거가 불완전함",
}


def _liquidity_capacity_status_label(proof_status: str) -> str:
    """Translate a stable audit identity into first-read Final Review copy."""

    return _LIQUIDITY_CAPACITY_STATUS_LABELS.get(
        str(proof_status or "").strip(),
        "유동성 근거 상태 확인 필요",
    )
```

Use the helper only for `display_value`. Keep `measured_value=liquidity_status`, set the title to `유동성·운용 가능성 근거`, interpretation to `공식 제공처의 유동성 자료 범위와 최신성을 확인합니다.`, and comparator to the mapped official/fresh label.

- [x] **Step 5: Run focused GREEN tests**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_backtest_final_review_decision_brief.py
```

Expected: all Final Review Decision Brief contract tests pass.

---

### Task 2: Regression, Browser QA, Documentation And Commit

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/final-review-liquidity-evidence-copy-v1-20260722/*.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create generated artifact only: `final-review-liquidity-evidence-copy-v1-qa.png`

**Interfaces:**
- Consumes: verified Decision Brief display contract
- Produces: actual Level3 visual evidence and durable closeout record

- [x] **Step 1: Run linked Final Review regression and compile checks**

Run:

```bash
.venv/bin/python -m pytest -q \
  tests/test_backtest_final_review_decision_brief.py \
  tests/test_final_review_market_context_visual_contract.py
.venv/bin/python -m pytest -q \
  tests/test_backtest_refactor_boundaries.py -k final_review
.venv/bin/python -m py_compile app/services/backtest_final_review_decision_brief.py
git diff --check
```

Expected: linked Final Review tests, compile, and diff checks pass.

- [x] **Step 2: Run actual Browser QA**

Open the current Level3 candidate that reproduces the card and verify:

- title is `유동성·운용 가능성 근거`
- display value contains no underscore enum
- comparator is `공식 제공처의 최신 유동성 근거 확보`
- desktop and 760px cards do not overflow
- application console error count is zero; framework initialization warnings are recorded separately

- [x] **Step 3: Capture QA evidence and remove temporary artifacts**

Keep `final-review-liquidity-evidence-copy-v1-qa.png` uncommitted. Stop any temporary server and remove temporary diagnostic files.

- [x] **Step 4: Synchronize durable docs**

Record the presentation adapter boundary and `2/2차` completion. Do not describe this as a Gate or provider behavior change.

- [x] **Step 5: Review and commit only owned files**

Run `git status --short`, `git diff --check`, and inspect the staged diff. Exclude registries, saved JSONL, run history, screenshots, and unrelated user files.

Commit message:

```text
개선: Final Review 유동성 근거 문구 정리
```
