# Practical Validation Level2 Decision Workspace V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task in the current `codex/backtest-dev` worktree. Every behavior change uses `superpowers:test-driven-development`; completion claims use `superpowers:verification-before-completion`. This task does not authorize a new worktree or subagent dispatch.

**Goal:** Practical Validation Level2를 질문 중심의 4단계 one-shell workspace로 바꾸고, 검증된 사실·측정된 주의·지금 해결할 일·개발 필요·Final Review handoff를 root issue 기준으로 구분한다.

**Architecture:** Python이 audit / closure / applicability / handler registry를 소비해 `practical_validation_decision_workspace_v1` read model을 만들고 source, profile, replay, Gate, action, save를 계속 소유한다. 새 React component는 Final Review와 같은 visual token으로 read model을 표시하고 intent만 반환한다. 기존 workspace / Fix Queue / Data Action Board는 migration compatibility에 남기되 active first-read render에서는 제거한다. React build가 없거나 payload를 표시할 수 없으면 새 Python fallback이 동일한 4단계 순서와 동일 count를 표시한다.

**Tech Stack:** Python 3.12, pandas, Streamlit, `unittest`, React 18, TypeScript 5, Vite 5, append-only JSONL runtime helpers.

## Global Constraints

- worktree는 `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev`, branch는 `codex/backtest-dev`를 유지한다.
- active task는 `.aiworkspace/note/finance/tasks/active/practical-validation-level2-decision-workspace-v1-20260716/`만 사용한다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`과 `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`은 사용자 실행 결과다. rewrite / delete / stage / commit하지 않는다.
- saved JSONL, 기존 registry row, generated QA screenshot, `.superpowers/`, run artifact를 commit하지 않는다.
- historical universe / delisting provider, DB schema, strategy runtime 재설계는 범위 밖이다.
- Final Review에서 provider fetch, replay, ingestion을 실행하지 않는다.
- live approval, broker order, account sync, auto rebalance 의미를 추가하지 않는다.
- React는 분류, root dedup, applicability, Gate, handler existence, replay, persistence를 계산하지 않는다.
- current-session replay guard와 save-and-move guard를 유지한다.
- visible user flow는 `후보와 기준 확인 -> 최신 재검증 -> 결과 해석과 해결 구분 -> 저장 / Final Review 이동` 4단계다.
- `검증 기준 상세`는 독립 flow가 아니라 Step 3 disclosure다.

---

### Task 1: Validation Truth / Root Actionability Contract

**Files:**
- Create: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `app/services/backtest_construction_risk_audit.py`
- Modify: `app/services/backtest_evidence_closure.py`
- Modify: `app/services/backtest_practical_validation.py`
- Modify: `app/web/backtest_practical_validation/page.py`

**Interfaces:**
- Consumes: `build_construction_risk_audit(validation: dict[str, Any]) -> dict[str, Any]`
- Consumes: `build_evidence_closure_contract(validation: dict[str, Any]) -> dict[str, Any]`
- Produces: closure summary fields `resolve_now_count`, `engineering_required_count`, `accepted_limit_count`, `final_decision_count`, `monitoring_transfer_count`
- Produces: registered action id `run_practical_validation_provider_gap_collection`
- Produces: callable Python handler `_execute_practical_validation_provider_gap_collection(...)`
- Preserves: existing `run_practical_validation_replay` handler contract

- [ ] **Step 1: Add failing truth-contract tests**

Create `tests/test_backtest_practical_validation_decision_workspace.py` with:

```python
from __future__ import annotations

import unittest
from importlib import import_module


class PracticalValidationTruthContractTests(unittest.TestCase):
    def test_single_component_weight_is_not_mix_concentration(self) -> None:
        from app.services.backtest_construction_risk_audit import (
            build_construction_risk_audit,
        )

        audit = build_construction_risk_audit(
            {
                "metrics": {
                    "active_components": 1,
                    "weight_total": 100.0,
                    "max_weight": 100.0,
                },
                "validation_profile": {
                    "thresholds": {"max_weight_review": 75.0},
                },
            }
        )
        row = next(
            row
            for row in audit["rows"]
            if row["Criteria"] == "Component weight concentration"
        )

        self.assertEqual(row["Status"], "NOT_APPLICABLE")
        self.assertTrue(row["Ready"])
        self.assertIn("단일 component", row["Current"])
        self.assertNotIn("Final Review 근거에 남깁니다", row["Next Action"])

    def test_pre_final_enrichment_is_resolve_now_only_with_registered_handler(
        self,
    ) -> None:
        from app.services.backtest_evidence_closure import (
            build_evidence_closure_contract,
        )

        contract = build_evidence_closure_contract(
            {
                "validation_id": "validation-action",
                "selection_source_id": "source-action",
                "validation_modules": [
                    {
                        "module_id": "pre_final_data_enrichment",
                        "label": "승격 전 필수 데이터 보강",
                        "status": "NEEDS_INPUT",
                        "requirement": "REQUIRED",
                        "review_role": "final_readiness_blocker",
                        "action_id": "run_practical_validation_provider_gap_collection",
                        "gate_effect": "Blocks Final Review",
                    }
                ],
            }
        )

        issue = contract["issues"][0]
        self.assertEqual(issue["resolution_class"], "resolve_now")
        self.assertTrue(issue["actionable_now"])
        self.assertEqual(
            issue["action_id"],
            "run_practical_validation_provider_gap_collection",
        )
        self.assertEqual(contract["summary"]["resolve_now_count"], 1)
        self.assertEqual(contract["summary"]["unresolved_actionable_count"], 1)

    def test_closure_summary_separates_handoff_classes(self) -> None:
        from app.services.backtest_evidence_closure import (
            build_evidence_closure_contract,
        )

        modules = [
            {
                "module_id": module_id,
                "label": module_id,
                "status": "REVIEW",
                "requirement": "REQUIRED",
                "review_role": "pv_practical_caution",
            }
            for module_id in (
                "validation_efficacy",
                "construction_risk",
                "backtest_realism",
                "stress_robustness",
                "provider_investability",
                "source_integrity",
            )
        ]
        modules.append(
            {
                "module_id": "tax_account_scope",
                "label": "Tax / Account Scope",
                "status": "REVIEW",
                "requirement": "REFERENCE",
                "review_role": "final_decision_input",
            }
        )

        summary = build_evidence_closure_contract(
            {
                "validation_id": "validation-grs-current",
                "selection_source_id": "source-grs-current",
                "validation_modules": modules,
            }
        )["summary"]

        self.assertEqual(summary["accepted_limit_count"], 6)
        self.assertEqual(summary["final_decision_count"], 1)
        self.assertEqual(summary["resolve_now_count"], 0)
        self.assertEqual(summary["critical_engineering_count"], 0)

    def test_registered_provider_action_resolves_to_callable_python_handler(
        self,
    ) -> None:
        from app.services.backtest_evidence_closure import (
            ACTION_HANDLER_CONTRACTS,
        )

        contract = ACTION_HANDLER_CONTRACTS[
            "run_practical_validation_provider_gap_collection"
        ]
        module_name, function_name = str(contract["handler"]).split(":", 1)
        handler = getattr(import_module(module_name), function_name)

        self.assertTrue(callable(handler))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_backtest_practical_validation_decision_workspace.PracticalValidationTruthContractTests
```

Expected:

- single-component assertion fails because the row is `REVIEW`
- enrichment assertion fails because provider collection handler is not registered and the generic issue is not `resolve_now`
- summary assertion fails because resolution-class counts do not exist
- callable-handler assertion fails because the provider action contract and execution function do not exist

- [ ] **Step 3: Make single-component construction applicability explicit**

In `app/services/backtest_construction_risk_audit.py`:

```python
_STATUS_RANK = {
    "PASS": 0,
    "NOT_APPLICABLE": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}
```

Update `_row(...)`:

```python
def _row(
    *,
    criteria: str,
    status: str,
    current: Any,
    evidence: Any,
    next_action: str,
    meaning: str,
    source_strength: str,
) -> dict[str, Any]:
    normalized = status if status in _STATUS_RANK else _status(status, default="REVIEW")
    return {
        "Criteria": criteria,
        "Status": normalized,
        "Ready": normalized in {"PASS", "NOT_APPLICABLE"},
        "Current": _safe_text(current),
        "Evidence": _safe_text(evidence),
        "Source Strength": source_strength,
        "Next Action": next_action,
        "Meaning": meaning,
    }
```

Update the first branch of `_component_weight_row(...)`:

```python
    if active_components <= 0:
        status = "BLOCKED"
        current = "active component 없음"
        next_action = "Backtest Analysis에서 active component가 있는 source를 다시 선택합니다."
    elif active_components == 1 and abs(weight_total - 100.0) <= 0.01:
        status = "NOT_APPLICABLE"
        current = "단일 component 100.0% / mix concentration 비적용"
        next_action = "단일 전략의 underlying holdings 집중은 별도 look-through 근거에서 확인합니다."
    elif abs(weight_total - 100.0) > 0.01:
        status = "BLOCKED"
        current = f"max {max_weight:.1f}% / total {weight_total:.1f}% / components {active_components}"
        next_action = "target weight 합계를 100%로 맞춘 뒤 다시 검증합니다."
    elif max_weight > review_line:
        status = "REVIEW"
        current = f"max {max_weight:.1f}% / total {weight_total:.1f}% / components {active_components}"
        next_action = "최대 component 비중이 profile 기준을 넘는 이유를 Final Review 근거에 남깁니다."
    else:
        status = "PASS"
        current = f"max {max_weight:.1f}% / total {weight_total:.1f}% / components {active_components}"
        next_action = "추가 조치 없음"
```

Use `current=current` in the returned row.

- [ ] **Step 4: Register the real provider action and attach it to the blocker**

In `app/services/backtest_evidence_closure.py`:

```python
ACTION_HANDLER_CONTRACTS = {
    "run_practical_validation_replay": {
        "owner_stage": "practical_validation",
        "handler": "app.web.backtest_practical_validation.page:_render_actual_replay_panel",
    },
    "run_practical_validation_provider_gap_collection": {
        "owner_stage": "practical_validation",
        "handler": "app.web.backtest_practical_validation.page:_execute_practical_validation_provider_gap_collection",
    },
}
```

The replay handler path remains unchanged in Task 1. Task 3 changes it only after
`_execute_practical_validation_replay(...)` exists.

In `app/web/backtest_practical_validation/page.py`, add this execution boundary
immediately after `_complete_provider_gap_collection(...)`:

```python
def _execute_practical_validation_provider_gap_collection(
    validation_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Run the registered provider-gap action and invalidate stale replay proof."""

    results = list(run_provider_gap_collection(validation_result) or [])
    _complete_provider_gap_collection(
        validation_result,
        results,
        origin="decision_workspace",
    )
    return results
```

In `app/services/backtest_practical_validation.py`, add these fields to the `pre_final_data_enrichment` blocker built by `_apply_pre_final_enrichment_gate(...)`:

```python
        "action_id": "run_practical_validation_provider_gap_collection",
        "actionable_now": True,
        "completion_criteria": (
            "필수 데이터 보강 실행 후 current-session replay를 다시 실행하고 "
            "새 validation을 저장합니다."
        ),
```

In `app/services/backtest_evidence_closure.py`, extend `_base_issue(...)` with
`measurement: dict[str, Any] | None = None` and persist `"measurement":
dict(measurement or {})`. In `_generic_module_issue(...)`, pass
`measurement=dict(module.get("measurement") or {})`. This preserves structured
observation / comparator data for the Task 2 `measured_caution` projection; prose
must not be parsed into a measurement.

In `_generic_module_issue(...)`, handle `final_readiness_blocker` before the existing monitoring / final-decision branches:

```python
    action_id = str(module.get("action_id") or "").strip() or None
    if role == "final_readiness_blocker":
        if has_action_handler(action_id):
            resolution_class = "resolve_now"
            owner_stage = "practical_validation"
            criticality = "critical"
            gate_effect = "block_final_review"
        else:
            resolution_class = "engineering_required"
            owner_stage = "development"
            criticality = "critical"
            gate_effect = "block_final_review"
            action_id = None
    elif role == "monitoring_followup":
        resolution_class = "monitoring_transfer"
        owner_stage = "final_review"
        criticality = "noncritical"
        gate_effect = "final_review_closure"
    elif role == "final_decision_input":
        resolution_class = "final_decision"
        owner_stage = "final_review"
        criticality = "noncritical"
        gate_effect = "final_review_closure"
    else:
        resolution_class = "accepted_limit"
        owner_stage = "final_review"
        criticality = "noncritical"
        gate_effect = "final_review_closure"
```

Pass these values to `_base_issue(...)`:

```python
        actionable_now=resolution_class == "resolve_now",
        action_id=action_id,
        criticality=criticality,
        gate_effect=gate_effect,
        terminal_state=(
            "deferred"
            if resolution_class == "engineering_required"
            else "open"
        ),
```

- [ ] **Step 5: Add resolution-class counts to closure summary**

Replace `_closure_summary(...)` in `app/services/backtest_evidence_closure.py` with:

```python
def _closure_summary(issues: list[dict[str, Any]]) -> dict[str, int]:
    resolution_counts = {
        resolution_class: sum(
            1
            for issue in issues
            if issue.get("resolution_class") == resolution_class
        )
        for resolution_class in (
            "resolve_now",
            "engineering_required",
            "accepted_limit",
            "final_decision",
            "monitoring_transfer",
        )
    }
    unresolved_actionable_count = sum(
        1
        for issue in issues
        if issue.get("actionable_now") and issue.get("terminal_state") == "open"
    )
    critical_engineering_count = sum(
        1
        for issue in issues
        if issue.get("resolution_class") == "engineering_required"
        and issue.get("criticality") == "critical"
        and issue.get("terminal_state")
        not in {"resolved", "accepted", "monitoring_transferred"}
    )
    missing_contract_count = sum(
        1
        for issue in issues
        if str(issue.get("root_issue_id") or "").startswith("missing_contract:")
    )
    return {
        "total": len(issues),
        "unresolved_actionable_count": unresolved_actionable_count,
        "critical_engineering_count": critical_engineering_count,
        "missing_contract_count": missing_contract_count,
        "resolve_now_count": resolution_counts["resolve_now"],
        "engineering_required_count": resolution_counts["engineering_required"],
        "accepted_limit_count": resolution_counts["accepted_limit"],
        "final_decision_count": resolution_counts["final_decision"],
        "monitoring_transfer_count": resolution_counts["monitoring_transfer"],
    }
```

- [ ] **Step 6: Run GREEN and focused regression**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_practical_validation_decision_workspace.PracticalValidationTruthContractTests \
  tests.test_backtest_evidence_closure \
  tests.test_service_contracts.PracticalValidationServiceContractTests
```

Expected: all tests pass.

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/backtest_construction_risk_audit.py \
  app/services/backtest_evidence_closure.py \
  app/services/backtest_practical_validation.py \
  app/web/backtest_practical_validation/page.py
git diff --check
```

Expected: both commands succeed with no output from `git diff --check`.

- [ ] **Step 7: Commit 1차**

```bash
git add \
  app/services/backtest_construction_risk_audit.py \
  app/services/backtest_evidence_closure.py \
  app/services/backtest_practical_validation.py \
  app/web/backtest_practical_validation/page.py \
  tests/test_backtest_practical_validation_decision_workspace.py
git commit -m "Practical Validation 검증 의미 계약 보정"
```

---

### Task 2: Level2 Decision Workspace Read Model

**Files:**
- Create: `app/services/backtest_practical_validation_decision_workspace.py`
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `app/services/backtest_practical_validation.py`
- Modify: `app/services/backtest_practical_validation_workspace.py`

**Interfaces:**
- Produces: `build_practical_validation_decision_workspace(...) -> dict[str, Any]`
- Produces schema: `practical_validation_decision_workspace_v1`
- Produces top-level identity: `selection_source_id`, `validation_result_id`
- Consumes: `evidence_closure`, `practical_validation_workspace`, `VALIDATION_PROFILE_OPTIONS`, current replay result
- Preserves: `practical_validation_workspace` compatibility field

- [ ] **Step 1: Add failing state-machine and GRS projection tests**

Append to `tests/test_backtest_practical_validation_decision_workspace.py`:

```python
class PracticalValidationDecisionWorkspaceTests(unittest.TestCase):
    def _source(self) -> dict[str, object]:
        return {
            "selection_source_id": "source-grs-current",
            "title": "GRS Macro Top 3",
            "source_type": "single_strategy",
            "period": {"actual_start": "2016-01-29", "actual_end": "2026-07-15"},
        }

    def _validation(self) -> dict[str, object]:
        accepted = [
            {
                "root_issue_id": root_id,
                "title": title,
                "resolution_class": "accepted_limit",
                "criticality": "noncritical",
                "terminal_state": "open",
                "actionable_now": False,
                "derived_checks": [root_id],
            }
            for root_id, title in (
                ("historical_universe_coverage", "과거 universe와 상장폐지 반영 범위"),
                ("validation_method_strength", "Validation Method Strength"),
                ("construction_risk", "Construction Risk"),
                ("backtest_realism", "Backtest Realism"),
                ("stress_robustness", "Stress / Robustness"),
                ("provider_investability", "Provider Investability"),
            )
        ]
        final_decision = {
            "root_issue_id": "tax_account_scope",
            "title": "세금 / 계좌 적용 범위",
            "resolution_class": "final_decision",
            "criticality": "noncritical",
            "terminal_state": "open",
            "actionable_now": False,
            "derived_checks": ["tax_account_scope"],
        }
        return {
            "validation_id": "validation-grs-current",
            "selection_source_id": "source-grs-current",
            "validation_route": "READY_FOR_FINAL_REVIEW",
            "final_review_gate": {
                "route": "READY_WITH_REVIEW",
                "can_save_and_move": True,
                "blocking_modules": [],
                "review_modules": [],
            },
            "evidence_closure": {
                "issues": [*accepted, final_decision],
                "summary": {
                    "total": 7,
                    "unresolved_actionable_count": 0,
                    "critical_engineering_count": 0,
                    "missing_contract_count": 0,
                    "resolve_now_count": 0,
                    "engineering_required_count": 0,
                    "accepted_limit_count": 6,
                    "final_decision_count": 1,
                    "monitoring_transfer_count": 0,
                },
                "current_final_review_eligible": True,
            },
            "practical_validation_workspace": {
                "visible_criteria_detail_groups": [
                    {
                        "group_id": "source_replay",
                        "display_label": "Source & Replay",
                        "purpose": "같은 후보를 최신 데이터로 재현했는가?",
                        "criteria_cards": [
                            {
                                "label": "Latest Runtime Replay",
                                "status": "PASS",
                                "checked_evidence": "requested / actual period 일치",
                            }
                        ],
                    }
                ],
                "next_stage_action": {
                    "primary_action": {
                        "id": "save_and_move",
                        "label": "저장하고 Final Review로 이동",
                        "enabled": True,
                    },
                    "secondary_action": {
                        "id": "save_audit_only",
                        "label": "검증 결과 저장",
                        "enabled": True,
                    },
                },
            },
        }

    def test_ready_with_handoff_separates_limits_and_final_decision(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=self._validation(),
            source_options=[self._source()],
        )

        self.assertEqual(model["state"], "ready_with_handoff")
        self.assertEqual(model["validation_result_id"], "validation-grs-current")
        self.assertEqual(model["summary"]["resolve_now_count"], 0)
        self.assertEqual(model["summary"]["engineering_blocker_count"], 0)
        self.assertEqual(model["summary"]["accepted_limit_count"], 6)
        self.assertEqual(model["summary"]["final_decision_count"], 1)
        self.assertEqual(model["resolution_lanes"]["resolve_now"], [])
        self.assertEqual(len(model["resolution_lanes"]["final_review_handoff"]), 7)
        self.assertIn("Final Review로 이동할 수 있습니다", model["verdict"]["headline"])

    def test_source_required_disables_replay_and_save(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        model = build_practical_validation_decision_workspace(
            source={},
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result=None,
            validation_result=None,
            source_options=[],
        )

        self.assertEqual(model["state"], "source_required")
        self.assertFalse(model["actions"]["run_replay"]["enabled"])
        self.assertFalse(model["actions"]["save_audit_only"]["enabled"])
        self.assertFalse(model["actions"]["save_and_move"]["enabled"])

    def test_replay_required_hides_result_and_save_actions(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result=None,
            validation_result=None,
            source_options=[self._source()],
        )

        self.assertEqual(model["state"], "replay_required")
        self.assertEqual(model["verified_findings"], [])
        self.assertFalse(model["actions"]["save_and_move"]["enabled"])
        self.assertTrue(model["actions"]["run_replay"]["enabled"])

    def test_action_lane_contains_only_registered_current_actions(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"] = {
            "issues": [
                {
                    "root_issue_id": "pre_final_data_enrichment",
                    "title": "필수 provider 근거 보강",
                    "resolution_class": "resolve_now",
                    "criticality": "critical",
                    "terminal_state": "open",
                    "actionable_now": True,
                    "action_id": "run_practical_validation_provider_gap_collection",
                    "completion_criteria": "수집 후 replay와 새 validation 저장",
                },
                {
                    "root_issue_id": "unknown-action",
                    "title": "미구현 action",
                    "resolution_class": "engineering_required",
                    "criticality": "critical",
                    "terminal_state": "deferred",
                    "actionable_now": False,
                    "action_id": None,
                },
            ],
            "summary": {
                "unresolved_actionable_count": 1,
                "critical_engineering_count": 1,
                "missing_contract_count": 0,
                "resolve_now_count": 1,
                "engineering_required_count": 1,
                "accepted_limit_count": 0,
                "final_decision_count": 0,
                "monitoring_transfer_count": 0,
            },
        }
        validation["final_review_gate"]["can_save_and_move"] = False

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        self.assertEqual(model["state"], "resolution_required")
        self.assertEqual(
            [row["root_issue_id"] for row in model["resolution_lanes"]["resolve_now"]],
            ["pre_final_data_enrichment"],
        )
        self.assertEqual(
            [row["root_issue_id"] for row in model["resolution_lanes"]["engineering_required"]],
            ["unknown-action"],
        )
        self.assertFalse(model["actions"]["save_and_move"]["enabled"])

    def test_explicit_measurement_is_one_caution_not_a_duplicate_handoff(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"] = {
            "issues": [
                {
                    "root_issue_id": "provider_liquidity_pressure",
                    "title": "유동성 여유",
                    "resolution_class": "accepted_limit",
                    "criticality": "noncritical",
                    "terminal_state": "open",
                    "actionable_now": False,
                    "measurement": {
                        "observed": 42.0,
                        "threshold": 30.0,
                        "unit": "%",
                        "as_of": "2026-07-15",
                    },
                }
            ],
            "summary": {
                "unresolved_actionable_count": 0,
                "critical_engineering_count": 0,
                "missing_contract_count": 0,
                "accepted_limit_count": 1,
            },
        }

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        self.assertEqual(model["summary"]["measured_caution_count"], 1)
        self.assertEqual(model["summary"]["accepted_limit_count"], 0)
        self.assertEqual(
            [row["root_issue_id"] for row in model["measured_cautions"]],
            ["provider_liquidity_pressure"],
        )
        self.assertEqual(model["resolution_lanes"]["final_review_handoff"], [])

    def test_method_strength_separates_computed_passes_from_remaining_review(
        self,
    ) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["validation_efficacy_audit"] = {
            "rows": [
                {
                    "Criteria": "Walk-forward temporal validation",
                    "Status": "REVIEW",
                    "Current": "REVIEW / windows=103",
                    "Evidence": "worst excess -4.46%",
                    "Next Action": "negative window 원인을 확인합니다.",
                },
                {
                    "Criteria": "OOS holdout validation",
                    "Status": "PASS",
                    "Current": "PASS / in=64 / out=63",
                    "Evidence": "out excess 144.32%",
                },
                {
                    "Criteria": "Regime split validation",
                    "Status": "PASS",
                    "Current": "PASS / buckets=3 / months=126",
                    "Evidence": "worst excess 19.88%",
                },
            ]
        }

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        verified_titles = {row["title"] for row in model["verified_findings"]}
        method_issue = next(
            row
            for row in model["resolution_lanes"]["final_review_handoff"]
            if row["root_issue_id"] == "validation_method_strength"
        )
        self.assertIn("OOS holdout validation", verified_titles)
        self.assertIn("Regime split validation", verified_titles)
        self.assertIn("windows=103", method_issue["observed"])
        self.assertNotIn("근거 없음", method_issue["observed"])
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_backtest_practical_validation_decision_workspace.PracticalValidationDecisionWorkspaceTests
```

Expected: import error because `app.services.backtest_practical_validation_decision_workspace` does not exist.

- [ ] **Step 3: Create the pure Decision Workspace service**

Create `app/services/backtest_practical_validation_decision_workspace.py`:

```python
from __future__ import annotations

from typing import Any

from app.services.backtest_evidence_closure import has_action_handler
from app.services.backtest_practical_validation_source import (
    VALIDATION_PROFILE_OPTIONS,
)


PRACTICAL_VALIDATION_DECISION_WORKSPACE_SCHEMA_VERSION = (
    "practical_validation_decision_workspace_v1"
)

_ROOT_AUDIT_KEYS = {
    "validation_method_strength": "validation_efficacy_audit",
    "construction_risk": "construction_risk_audit",
    "backtest_realism": "backtest_realism_audit",
    "risk_contribution": "risk_contribution_audit",
    "component_role_weight": "component_role_weight_audit",
    "provider_investability": "data_coverage_audit",
    "historical_universe_coverage": "data_coverage_audit",
}

_ROOT_AUDIT_CRITERIA = {
    "provider_investability": {"Provider snapshot freshness"},
    "historical_universe_coverage": {
        "Universe / listing evidence",
        "Survivorship / delisting control",
    },
}

_AUDIT_LABELS = {
    "validation_efficacy_audit": "검증 방법론 강도",
    "construction_risk_audit": "포트폴리오 구성 근거",
    "backtest_realism_audit": "실전 운용 현실성",
    "risk_contribution_audit": "위험 기여",
    "component_role_weight_audit": "구성 역할과 비중",
    "data_coverage_audit": "데이터 범위와 최신성",
}


def _dict_rows(value: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in list(value or []) if isinstance(row, dict)]


def _audit_rows(
    validation_result: dict[str, Any],
    audit_key: str,
) -> list[dict[str, Any]]:
    return _dict_rows(dict(validation_result.get(audit_key) or {}).get("rows"))


def _technical_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "row_id": str(
            row.get("module_id")
            or row.get("Criteria")
            or row.get("label")
            or row.get("display_label")
            or "row"
        ),
        "title": str(
            row.get("Criteria")
            or row.get("display_label")
            or row.get("label")
            or "검증 항목"
        ),
        "status": str(row.get("Status") or row.get("status") or "NOT_RUN"),
        "detail": str(
            row.get("Evidence")
            or row.get("checked_evidence")
            or row.get("Current")
            or row.get("current_problem")
            or "-"
        ),
    }


def _source_option(row: dict[str, Any], selected_id: str) -> dict[str, Any]:
    source_id = str(row.get("selection_source_id") or "").strip()
    return {
        "selection_source_id": source_id,
        "title": str(
            row.get("source_title")
            or row.get("title")
            or row.get("strategy_name")
            or source_id
            or "후보"
        ),
        "source_type": str(row.get("source_type") or "selection_source"),
        "selected": source_id == selected_id,
        "eligible": True,
    }


def _profile_model(profile: dict[str, Any]) -> dict[str, Any]:
    current_id = str(profile.get("profile_id") or "balanced_core")
    return {
        "profile_id": current_id,
        "profile_label": str(
            profile.get("profile_label")
            or dict(VALIDATION_PROFILE_OPTIONS.get(current_id) or {}).get("label")
            or current_id
        ),
        "options": [
            {
                "profile_id": profile_id,
                "label": str(config.get("label") or profile_id),
                "description": str(config.get("description") or ""),
                "selected": profile_id == current_id,
            }
            for profile_id, config in VALIDATION_PROFILE_OPTIONS.items()
        ],
        "advanced_control_owner": "streamlit_disclosure",
    }


def _issue_model(
    issue: dict[str, Any],
    validation_result: dict[str, Any],
) -> dict[str, Any]:
    resolution_class = str(
        issue.get("resolution_class") or "engineering_required"
    )
    measurement = dict(issue.get("measurement") or {})
    observed = measurement.get("observed")
    comparator = (
        measurement.get("threshold")
        if measurement.get("threshold") is not None
        else measurement.get("comparator")
    )
    measured_caution = (
        resolution_class
        not in {"resolve_now", "engineering_required"}
        and observed is not None
        and comparator is not None
    )
    action_id = str(issue.get("action_id") or "").strip() or None
    terminal_state = str(issue.get("terminal_state") or "open")
    actionable = (
        resolution_class == "resolve_now"
        and terminal_state == "open"
        and has_action_handler(action_id)
    )
    if resolution_class == "resolve_now" and not actionable:
        resolution_class = "engineering_required"
        terminal_state = "deferred"
        action_id = None
    root_issue_id = str(issue.get("root_issue_id") or "")
    audit_key = _ROOT_AUDIT_KEYS.get(root_issue_id)
    evidence_rows = _audit_rows(validation_result, audit_key) if audit_key else []
    criteria_filter = _ROOT_AUDIT_CRITERIA.get(root_issue_id)
    if criteria_filter:
        evidence_rows = [
            row
            for row in evidence_rows
            if str(row.get("Criteria") or "") in criteria_filter
        ]
    observed_rows = [
        f"{row.get('Criteria')}: {row.get('Current') or row.get('Evidence')}"
        for row in evidence_rows
        if row.get("Criteria") and (row.get("Current") or row.get("Evidence"))
    ]
    remaining_rows = [
        str(row.get("Next Action") or "")
        for row in evidence_rows
        if str(row.get("Status") or "").upper() not in {"PASS", "READY", "NOT_APPLICABLE"}
        and str(row.get("Next Action") or "").strip()
    ]
    return {
        "root_issue_id": str(issue.get("root_issue_id") or ""),
        "title": str(issue.get("title") or issue.get("root_issue_id") or "검증 항목"),
        "finding_kind": "measured_caution" if measured_caution else resolution_class,
        "resolution_class": resolution_class,
        "observed": " / ".join(observed_rows) or str(issue.get("observed") or ""),
        "expected": " / ".join(dict.fromkeys(remaining_rows))
        or str(issue.get("expected") or ""),
        "cause": str(issue.get("cause") or ""),
        "criticality": str(issue.get("criticality") or "noncritical"),
        "terminal_state": terminal_state,
        "actionable_now": actionable,
        "action_id": action_id if actionable else None,
        "action_label": str(issue.get("action_label") or ""),
        "completion_criteria": str(issue.get("completion_criteria") or ""),
        "derived_checks": list(issue.get("derived_checks") or []),
        "measurement": measurement,
    }


def _verified_findings(validation_result: dict[str, Any]) -> list[dict[str, Any]]:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for audit_key, audit_label in _AUDIT_LABELS.items():
        for row in _audit_rows(validation_result, audit_key):
            status = str(row.get("Status") or "").upper()
            if status not in {"PASS", "READY"}:
                continue
            stable_id = f"{audit_key}:{row.get('Criteria')}"
            if stable_id in seen:
                continue
            seen.add(stable_id)
            findings.append(
                {
                    "finding_id": stable_id,
                    "finding_kind": "verified",
                    "title": str(row.get("Criteria") or audit_label),
                    "detail": str(
                        row.get("Evidence")
                        or row.get("Current")
                        or "기준을 충족했습니다."
                    ),
                    "category_id": audit_key,
                }
            )
    for group in _dict_rows(
        workspace.get("visible_criteria_detail_groups")
        or workspace.get("criteria_detail_groups")
    ):
        group_id = str(group.get("group_id") or group.get("label") or "")
        for card in _dict_rows(group.get("criteria_cards")):
            status = str(card.get("status") or "").upper()
            if status not in {"PASS", "READY"}:
                continue
            stable_id = f"{group_id}:{card.get('label') or card.get('display_label')}"
            if stable_id in seen:
                continue
            seen.add(stable_id)
            findings.append(
                {
                    "finding_id": stable_id,
                    "finding_kind": "verified",
                    "title": str(
                        card.get("display_label")
                        or card.get("label")
                        or "검증 통과"
                    ),
                    "detail": str(
                        card.get("checked_evidence")
                        or card.get("evidence")
                        or card.get("explanation")
                        or "기준을 충족했습니다."
                    ),
                    "category_id": group_id,
                }
            )
    return findings


def _category_disclosures(
    validation_result: dict[str, Any],
) -> list[dict[str, Any]]:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    groups = _dict_rows(
        workspace.get("visible_criteria_detail_groups")
        or workspace.get("criteria_detail_groups")
    )
    disclosures = [
        {
            "category_id": str(group.get("group_id") or group.get("label") or ""),
            "title": str(
                group.get("display_label")
                or group.get("label")
                or "검증 카테고리"
            ),
            "question": str(group.get("purpose") or ""),
            "outcome": str(
                group.get("display_status")
                or group.get("status")
                or "NOT_RUN"
            ),
            "verified_items": list(group.get("passed_criteria") or []),
            "root_issue_ids": [],
            "technical_rows": [
                _technical_row(row)
                for row in _dict_rows(group.get("criteria_cards"))
            ],
        }
        for group in groups
    ]
    known_ids = {row["category_id"] for row in disclosures}
    for audit_key, audit_label in _AUDIT_LABELS.items():
        rows = _audit_rows(validation_result, audit_key)
        if not rows or audit_key in known_ids:
            continue
        disclosures.append(
            {
                "category_id": audit_key,
                "title": audit_label,
                "question": "실제 계산된 row와 남은 REVIEW 근거를 함께 확인합니다.",
                "outcome": str(
                    dict(validation_result.get(audit_key) or {}).get(
                        "overall_status"
                    )
                    or "NOT_RUN"
                ),
                "verified_items": [
                    str(row.get("Criteria") or "")
                    for row in rows
                    if str(row.get("Status") or "").upper()
                    in {"PASS", "READY"}
                ],
                "root_issue_ids": [
                    root_issue_id
                    for root_issue_id, mapped_key in _ROOT_AUDIT_KEYS.items()
                    if mapped_key == audit_key
                ],
                "technical_rows": [_technical_row(row) for row in rows],
            }
        )
    return disclosures


def _summary(
    *,
    verified_count: int,
    issues: list[dict[str, Any]],
    closure_summary: dict[str, Any],
) -> dict[str, int]:
    finding_counts = {
        finding_kind: sum(
            1
            for issue in issues
            if issue.get("finding_kind") == finding_kind
        )
        for finding_kind in (
            "measured_caution",
            "resolve_now",
            "accepted_limit",
            "final_decision",
            "monitoring_transfer",
        )
    }
    engineering_blocker_count = sum(
        1
        for issue in issues
        if issue.get("resolution_class") == "engineering_required"
        and issue.get("criticality") == "critical"
        and issue.get("terminal_state")
        not in {"resolved", "accepted", "monitoring_transferred"}
    )
    return {
        "verified_count": verified_count,
        "measured_caution_count": finding_counts["measured_caution"],
        "resolve_now_count": finding_counts["resolve_now"],
        "engineering_blocker_count": engineering_blocker_count,
        "accepted_limit_count": finding_counts["accepted_limit"],
        "final_decision_count": finding_counts["final_decision"],
        "monitoring_transfer_count": finding_counts["monitoring_transfer"],
        "missing_contract_count": int(
            closure_summary.get("missing_contract_count") or 0
        ),
    }


def _state(
    *,
    has_source: bool,
    replay_result: dict[str, Any] | None,
    validation_result: dict[str, Any] | None,
    summary: dict[str, int],
) -> str:
    if not has_source:
        return "source_required"
    if not replay_result:
        return "replay_required"
    if not validation_result:
        return "replay_required"
    if (
        summary["resolve_now_count"]
        or summary["engineering_blocker_count"]
        or summary["missing_contract_count"]
    ):
        return "resolution_required"
    if (
        summary["accepted_limit_count"]
        or summary["final_decision_count"]
        or summary["monitoring_transfer_count"]
    ):
        return "ready_with_handoff"
    return "ready"


def _verdict(state: str, summary: dict[str, int]) -> dict[str, str]:
    if state == "source_required":
        return {
            "tone": "neutral",
            "label": "후보 필요",
            "headline": "먼저 검증할 포트폴리오 후보를 선택하세요.",
            "detail": "Backtest Analysis에서 후보를 보내면 검증 기준과 replay 경로가 열립니다.",
        }
    if state == "replay_required":
        return {
            "tone": "neutral",
            "label": "재검증 필요",
            "headline": "최신 데이터 기준 재검증을 실행하세요.",
            "detail": "현재 세션 replay가 완료돼야 검증 결론과 저장 경로가 열립니다.",
        }
    if state == "resolution_required":
        return {
            "tone": "danger",
            "label": "이동 보류",
            "headline": "Final Review 전에 해결하거나 개발해야 할 항목이 있습니다.",
            "detail": (
                f"지금 해결 {summary['resolve_now_count']}건 · "
                f"개발 차단 {summary['engineering_blocker_count']}건"
            ),
        }
    if state == "ready_with_handoff":
        return {
            "tone": "warning",
            "label": "이동 가능",
            "headline": "Final Review로 이동할 수 있습니다.",
            "detail": (
                f"인수할 한계 {summary['accepted_limit_count']}건 · "
                f"최종 판단 {summary['final_decision_count']}건 · "
                f"Monitoring 이관 {summary['monitoring_transfer_count']}건을 전달합니다."
            ),
        }
    return {
        "tone": "positive",
        "label": "검증 완료",
        "headline": "추가 해결 항목 없이 Final Review로 이동할 수 있습니다.",
        "detail": "현재 검증 기준과 replay 결과가 이동 조건을 충족합니다.",
    }


def build_practical_validation_decision_workspace(
    *,
    source: dict[str, Any],
    validation_profile: dict[str, Any],
    replay_result: dict[str, Any] | None,
    validation_result: dict[str, Any] | None,
    source_options: list[dict[str, Any]],
) -> dict[str, Any]:
    selected_source_id = str(source.get("selection_source_id") or "")
    validation = dict(validation_result or {})
    closure = dict(validation.get("evidence_closure") or {})
    issues = [
        _issue_model(row, validation)
        for row in _dict_rows(closure.get("issues"))
    ]
    verified = _verified_findings(validation)
    measured_cautions = [
        issue for issue in issues if issue["finding_kind"] == "measured_caution"
    ]
    summary = _summary(
        verified_count=len(verified),
        issues=issues,
        closure_summary=dict(closure.get("summary") or {}),
    )
    state = _state(
        has_source=bool(selected_source_id),
        replay_result=replay_result,
        validation_result=validation_result,
        summary=summary,
    )
    resolve_now = [
        issue
        for issue in issues
        if issue["finding_kind"] == "resolve_now" and issue["actionable_now"]
    ]
    engineering_required = [
        issue
        for issue in issues
        if issue["finding_kind"] == "engineering_required"
    ]
    final_review_handoff = [
        issue
        for issue in issues
        if issue["finding_kind"] != "measured_caution"
        and issue["resolution_class"]
        in {"accepted_limit", "final_decision", "monitoring_transfer"}
    ]
    legacy_actions = dict(
        dict(validation.get("practical_validation_workspace") or {}).get(
            "next_stage_action"
        )
        or {}
    )
    primary = dict(legacy_actions.get("primary_action") or {})
    secondary = dict(legacy_actions.get("secondary_action") or {})
    can_move = state in {"ready", "ready_with_handoff"} and bool(
        dict(validation.get("final_review_gate") or {}).get("can_save_and_move")
    )
    return {
        "schema_version": PRACTICAL_VALIDATION_DECISION_WORKSPACE_SCHEMA_VERSION,
        "selection_source_id": selected_source_id,
        "validation_result_id": str(validation.get("validation_id") or ""),
        "state": state,
        "header": {
            "question": "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?",
            "detail": "후보와 기준을 확인하고 최신 데이터로 재검증한 뒤, 해결할 일과 넘길 판단을 구분합니다.",
        },
        "candidate_selector": {
            "selected_source_id": selected_source_id,
            "options": [
                _source_option(row, selected_source_id)
                for row in source_options
            ],
        },
        "candidate": {
            "selection_source_id": selected_source_id,
            "title": str(
                source.get("source_title")
                or source.get("title")
                or selected_source_id
                or "후보"
            ),
            "source_type": str(source.get("source_type") or "selection_source"),
            "as_of": str(
                dict(source.get("period") or {}).get("actual_end")
                or validation.get("created_at")
                or ""
            ),
        },
        "profile": _profile_model(validation_profile),
        "replay": {
            "status": str(dict(replay_result or {}).get("status") or "NOT_RUN"),
            "replay_id": str(dict(replay_result or {}).get("replay_id") or ""),
            "completed": bool(replay_result),
        },
        "verdict": _verdict(state, summary),
        "summary": summary,
        "verified_findings": verified,
        "measured_cautions": measured_cautions,
        "resolution_lanes": {
            "resolve_now": resolve_now,
            "engineering_required": engineering_required,
            "final_review_handoff": final_review_handoff,
        },
        "category_disclosures": _category_disclosures(validation),
        "actions": {
            "run_replay": {
                "id": "run_replay",
                "label": "최신 데이터 기준 재검증",
                "enabled": bool(selected_source_id),
            },
            "save_audit_only": {
                "id": "save_audit_only",
                "label": str(secondary.get("label") or "검증 결과 저장"),
                "enabled": bool(secondary.get("enabled", True)) and bool(validation_result),
            },
            "save_and_move": {
                "id": "save_and_move",
                "label": str(primary.get("label") or "저장하고 Final Review로 이동"),
                "enabled": can_move,
            },
        },
        "boundaries": {
            "react_executes_validation": False,
            "react_executes_collection": False,
            "react_executes_storage": False,
            "python_validates_intent": True,
        },
    }


__all__ = [
    "PRACTICAL_VALIDATION_DECISION_WORKSPACE_SCHEMA_VERSION",
    "build_practical_validation_decision_workspace",
]
```

- [ ] **Step 4: Attach the new read model without removing compatibility**

In `app/services/backtest_practical_validation.py`, import the builder:

```python
from app.services.backtest_practical_validation_decision_workspace import (
    build_practical_validation_decision_workspace,
)
```

Do not build the page-specific model inside `build_practical_validation_result(...)`, because source options and current-session replay state belong to the web orchestration. Export the builder through `__all__`:

```python
    "build_practical_validation_decision_workspace",
```

In `app/services/backtest_practical_validation_workspace.py`, replace the accepted-limit-only count initialization with closure summary consumption:

```python
    closure_summary = dict(closure.get("summary") or {})
    final_review_limit_count = int(
        closure_summary.get("accepted_limit_count")
        or len(final_review_limit_root_issue_ids)
    )
    final_review_decision_count = int(
        closure_summary.get("final_decision_count") or 0
    )
```

Add `final_review_decision_count` to the returned `summary`.

- [ ] **Step 5: Run GREEN and regression**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_practical_validation_decision_workspace \
  tests.test_backtest_evidence_closure \
  tests.test_service_contracts.PracticalValidationServiceContractTests \
  tests.test_service_contracts.PracticalValidationReplayServiceContractTests
```

Expected: all tests pass.

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/backtest_evidence_closure.py \
  app/services/backtest_practical_validation_decision_workspace.py \
  app/services/backtest_practical_validation.py \
  app/services/backtest_practical_validation_workspace.py
git diff --check
```

Expected: all commands succeed.

- [ ] **Step 6: Commit 2차**

```bash
git add \
  app/services/backtest_practical_validation_decision_workspace.py \
  app/services/backtest_practical_validation.py \
  app/services/backtest_practical_validation_workspace.py \
  tests/test_backtest_practical_validation_decision_workspace.py
git commit -m "Practical Validation 판단 워크스페이스 모델 도입"
```

---

### Task 3: One-Shell React UI / Python Intent Integration

**Files:**
- Create: `app/web/components/practical_validation_decision_workspace/__init__.py`
- Create: `app/web/components/practical_validation_decision_workspace/component.py`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/package.json`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/package-lock.json`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/tsconfig.json`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/vite.config.ts`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/index.html`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/src/index.tsx`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/src/types.ts`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- Create: `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- Create: `tests/test_practical_validation_market_context_visual_contract.py`
- Modify: `app/services/backtest_evidence_closure.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`

**Interfaces:**
- Produces: `render_practical_validation_decision_workspace(workspace, key) -> dict[str, Any] | None`
- React intents: `select_source`, `select_profile_preset`, `run_replay`, `run_resolution_action`, `save_audit_only`, `save_and_move`
- Python handlers:
  - `_execute_practical_validation_replay(...)`
  - `_execute_practical_validation_provider_gap_collection(...)` from Task 1
  - `_consume_practical_validation_decision_workspace_intent(...)`
- Preserves: `_consume_practical_validation_next_stage_action(...)` for save semantics
- Provides: Streamlit fallback from the same Python read model

- [ ] **Step 1: Add failing boundary and visual-contract tests**

In `tests/test_backtest_refactor_boundaries.py`, replace the old square-surface tests with:

```python
    def test_practical_validation_page_uses_one_decision_workspace(self) -> None:
        page_source = (
            PROJECT_ROOT / "app/web/backtest_practical_validation/page.py"
        ).read_text()
        render_body = page_source.split(
            "def render_practical_validation_workspace", 1
        )[1]

        self.assertIn(
            "render_practical_validation_decision_workspace(",
            render_body,
        )
        self.assertIn(
            "build_practical_validation_decision_workspace(",
            render_body,
        )
        self.assertNotIn(
            "render_practical_validation_workspace_overview(",
            render_body,
        )
        self.assertNotIn("_render_data_action_board(validation_result)", render_body)
        self.assertNotIn(
            "_render_final_review_data_enrichment_handoff(source)",
            render_body,
        )
        self.assertNotIn(
            "_render_practical_validation_recovery_progress(",
            render_body,
        )
        self.assertNotIn('title="검증 기준 상세"', render_body)
        self.assertIn("고급 설정과 원본 근거", render_body)
        self.assertIn(
            "render_practical_validation_decision_workspace_fallback(",
            render_body,
        )

    def test_practical_validation_react_is_intent_only(self) -> None:
        source = (
            PROJECT_ROOT
            / "app/web/components/practical_validation_decision_workspace/frontend/src/"
            "PracticalValidationDecisionWorkspace.tsx"
        ).read_text()

        for action in (
            "select_source",
            "select_profile_preset",
            "run_replay",
            "run_resolution_action",
            "save_audit_only",
            "save_and_move",
        ):
            self.assertIn(action, source)
        for forbidden in (
            "fetch(",
            "resolution_class ===",
            "can_save_and_move =",
            "run_provider_gap_collection(",
            "save_practical_validation_result(",
        ):
            self.assertNotIn(forbidden, source)
```

Create `tests/test_practical_validation_market_context_visual_contract.py`:

```python
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(
    "app/web/components/practical_validation_decision_workspace/frontend/src"
)
WORKSPACE = ROOT / "PracticalValidationDecisionWorkspace.tsx"
STYLE = ROOT / "style.css"
FINAL_REVIEW_STYLE = Path(
    "app/web/components/final_review_investment_report/frontend/src/style.css"
)


class PracticalValidationMarketContextVisualContractTests(unittest.TestCase):
    def test_workspace_uses_question_first_four_step_order(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn(
            "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?",
            source,
        )
        for label in (
            "1. 후보와 검증 기준",
            "2. 최신 데이터 기준 재검증",
            "3. 결과 해석과 해결 구분",
            "4. 저장하고 Final Review로 이동",
        ):
            self.assertIn(label, source)
        self.assertLess(source.index("1. 후보와 검증 기준"), source.index("2. 최신 데이터 기준 재검증"))
        self.assertLess(source.index("2. 최신 데이터 기준 재검증"), source.index("3. 결과 해석과 해결 구분"))
        self.assertLess(source.index("3. 결과 해석과 해결 구분"), source.index("4. 저장하고 Final Review로 이동"))

    def test_style_uses_final_review_visual_tokens(self) -> None:
        style = STYLE.read_text(encoding="utf-8")
        reference = FINAL_REVIEW_STYLE.read_text(encoding="utf-8")
        for token in (
            "#152033",
            "#647589",
            "#dae4ee",
            "border-radius: 20px",
            "border-radius: 17px",
            "border-radius: 14px",
            "0 10px 30px rgba(33, 53, 72, .055)",
        ):
            self.assertIn(token, reference)
            self.assertIn(token, style)
        self.assertNotIn("border-radius: 0", style)

    def test_zero_action_lane_is_not_rendered(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn("resolveNow.length > 0", source)
        self.assertIn("engineeringRequired.length > 0", source)
        self.assertIn("상세 검증 근거", source)
        self.assertNotIn("현재 표시할 항목이 없습니다.", source)

    def test_760_layout_collapses_to_one_column(self) -> None:
        style = STYLE.read_text(encoding="utf-8")
        responsive = style.split("@media (max-width: 760px)", 1)[1]

        self.assertIn("grid-template-columns: 1fr;", responsive)
        self.assertIn("overflow-wrap: anywhere;", style)

    def test_dynamic_content_updates_streamlit_frame_height(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn("new ResizeObserver", source)
        self.assertIn("Streamlit.setFrameHeight()", source)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_refactor_boundaries \
  tests.test_practical_validation_market_context_visual_contract
```

Expected: failures because the new component and active render path do not exist and the old square tests still describe the current UI.

- [ ] **Step 3: Create the Python component wrapper**

Create `app/web/components/practical_validation_decision_workspace/component.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "practical_validation_decision_workspace"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(
        _COMPONENT_NAME,
        path=str(_FRONTEND_BUILD_DIR),
    )
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_practical_validation_decision_workspace_available() -> bool:
    return _component is not None


def render_practical_validation_decision_workspace(
    *,
    workspace: dict[str, Any],
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render the Python-owned Level2 projection and return presentation intent."""

    if _component is None:
        return None
    value = _component(
        workspace=workspace,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
```

Create `app/web/components/practical_validation_decision_workspace/__init__.py`:

```python
from .component import (
    is_practical_validation_decision_workspace_available,
    render_practical_validation_decision_workspace,
)

__all__ = [
    "is_practical_validation_decision_workspace_available",
    "render_practical_validation_decision_workspace",
]
```

- [ ] **Step 4: Create the React payload and intent types**

Create `frontend/src/types.ts`:

```typescript
export type Tone = "positive" | "warning" | "danger" | "neutral"

export type WorkspaceIntent =
  | { action: "select_source"; intent_id: string; selection_source_id: string; validation_result_id: string }
  | { action: "select_profile_preset"; intent_id: string; selection_source_id: string; validation_result_id: string; profile_id: string }
  | { action: "run_replay"; intent_id: string; selection_source_id: string; validation_result_id: string }
  | {
      action: "run_resolution_action"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
      root_issue_id: string
      action_id: string
    }
  | { action: "save_audit_only"; intent_id: string; selection_source_id: string; validation_result_id: string }
  | { action: "save_and_move"; intent_id: string; selection_source_id: string; validation_result_id: string }

export type Issue = {
  root_issue_id: string
  title: string
  finding_kind: string
  resolution_class: string
  observed: string
  expected: string
  cause: string
  criticality: string
  terminal_state: string
  actionable_now: boolean
  action_id?: string | null
  action_label: string
  completion_criteria: string
  derived_checks: string[]
  measurement: Record<string, unknown>
}

export type DecisionWorkspace = {
  schema_version: string
  selection_source_id: string
  validation_result_id: string
  state: string
  header: { question: string; detail: string }
  candidate_selector: {
    selected_source_id: string
    options: Array<{
      selection_source_id: string
      title: string
      source_type: string
      selected: boolean
      eligible: boolean
    }>
  }
  candidate: {
    selection_source_id: string
    title: string
    source_type: string
    as_of: string
  }
  profile: {
    profile_id: string
    profile_label: string
    options: Array<{
      profile_id: string
      label: string
      description: string
      selected: boolean
    }>
  }
  replay: { status: string; replay_id: string; completed: boolean }
  verdict: { tone: Tone; label: string; headline: string; detail: string }
  summary: Record<string, number>
  verified_findings: Array<{
    finding_id: string
    finding_kind: "verified"
    title: string
    detail: string
    category_id: string
  }>
  measured_cautions: Issue[]
  resolution_lanes: {
    resolve_now: Issue[]
    engineering_required: Issue[]
    final_review_handoff: Issue[]
  }
  category_disclosures: Array<{
    category_id: string
    title: string
    question: string
    outcome: string
    verified_items: string[]
    root_issue_ids: string[]
    technical_rows: Array<{
      row_id: string
      title: string
      status: string
      detail: string
    }>
  }>
  actions: {
    run_replay: { id: string; label: string; enabled: boolean }
    save_audit_only: { id: string; label: string; enabled: boolean }
    save_and_move: { id: string; label: string; enabled: boolean }
  }
}
```

- [ ] **Step 5: Implement the four-step React workspace**

Create `frontend/src/PracticalValidationDecisionWorkspace.tsx` with these exact behavior boundaries:

```tsx
import React, { useEffect } from "react"
import { Streamlit } from "streamlit-component-lib"
import { DecisionWorkspace, Issue, WorkspaceIntent } from "./types"

const intentId = (prefix: string) =>
  `${prefix}-${globalThis.crypto?.randomUUID?.() ?? Date.now()}`

const emit = (intent: WorkspaceIntent) => Streamlit.setComponentValue(intent)

function StepTitle({ step, title, detail }: { step: string; title: string; detail: string }) {
  return (
    <header className="pv2-step-title">
      <span>{step}</span>
      <div><h2>{title}</h2><p>{detail}</p></div>
    </header>
  )
}

function IssueCard({
  issue,
  workspace,
}: {
  issue: Issue
  workspace: DecisionWorkspace
}) {
  return (
    <article className="pv2-issue-card">
      <div><strong>{issue.title}</strong><span>{issue.action_label}</span></div>
      {issue.observed && <p>{issue.observed}</p>}
      {issue.completion_criteria && <small>{issue.completion_criteria}</small>}
      {issue.actionable_now && issue.action_id && (
        <button
          type="button"
          onClick={() =>
            emit({
              action: "run_resolution_action",
              intent_id: intentId("resolution"),
              selection_source_id: workspace.candidate.selection_source_id,
              validation_result_id: workspace.validation_result_id,
              root_issue_id: issue.root_issue_id,
              action_id: issue.action_id!,
            })
          }
        >
          {issue.action_label || "지금 해결"}
        </button>
      )}
    </article>
  )
}

export function PracticalValidationDecisionWorkspace({
  workspace,
}: {
  workspace: DecisionWorkspace
}) {
  useEffect(() => {
    const resize = () => Streamlit.setFrameHeight()
    resize()
    const observer = new ResizeObserver(resize)
    observer.observe(document.body)
    return () => observer.disconnect()
  }, [])

  const resolveNow = workspace.resolution_lanes.resolve_now ?? []
  const engineeringRequired = workspace.resolution_lanes.engineering_required ?? []
  const handoff = workspace.resolution_lanes.final_review_handoff ?? []
  const measuredCautions = workspace.measured_cautions ?? []
  const visibleVerified = workspace.verified_findings.slice(0, 8)
  const validationResultId = workspace.validation_result_id

  return (
    <main className="pv2-workspace">
      <header className="pv2-header">
        <div>
          <p className="pv2-kicker">Practical Validation Decision Workspace</p>
          <h1>{workspace.header.question || "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?"}</h1>
          <p>{workspace.header.detail}</p>
        </div>
        <aside><strong>{workspace.candidate.title}</strong><span>{workspace.candidate.as_of || "기준일 미측정"}</span></aside>
      </header>

      <section className="pv2-step">
        <StepTitle step="1. 후보와 검증 기준" title="무엇을 어떤 기준으로 검증하는가" detail="후보와 판정 기준을 먼저 고정합니다." />
        <div className="pv2-choice-grid">
          {workspace.candidate_selector.options.map((option) => (
            <button
              type="button"
              className={option.selected ? "is-selected" : ""}
              disabled={!option.eligible}
              key={option.selection_source_id}
              onClick={() => emit({
                action: "select_source",
                intent_id: intentId("source"),
                selection_source_id: option.selection_source_id,
                validation_result_id: workspace.validation_result_id,
              })}
            >
              <strong>{option.title}</strong><span>{option.source_type}</span>
            </button>
          ))}
        </div>
        <div className="pv2-profile-grid">
          {workspace.profile.options.map((option) => (
            <button
              type="button"
              className={option.selected ? "is-selected" : ""}
              key={option.profile_id}
              onClick={() => emit({
                action: "select_profile_preset",
                intent_id: intentId("profile"),
                selection_source_id: workspace.candidate.selection_source_id,
                validation_result_id: workspace.validation_result_id,
                profile_id: option.profile_id,
              })}
            >
              <strong>{option.label}</strong><span>{option.description}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="pv2-step">
        <StepTitle step="2. 최신 데이터 기준 재검증" title="현재 저장 데이터로 다시 재현하는가" detail="현재 세션 replay가 완료되어야 결과와 저장 경로가 열립니다." />
        <div className="pv2-replay">
          <div><span>현재 상태</span><strong>{workspace.replay.status}</strong><small>{workspace.replay.replay_id || "아직 실행하지 않음"}</small></div>
          <button
            type="button"
            disabled={!workspace.actions.run_replay.enabled}
            onClick={() => emit({
              action: "run_replay",
              intent_id: intentId("replay"),
              selection_source_id: workspace.candidate.selection_source_id,
              validation_result_id: workspace.validation_result_id,
            })}
          >
            {workspace.actions.run_replay.label}
          </button>
        </div>
      </section>

      <section className={`pv2-verdict pv2-tone-${workspace.verdict.tone}`}>
        <span>{workspace.verdict.label}</span>
        <h2>{workspace.verdict.headline}</h2>
        <p>{workspace.verdict.detail}</p>
        <dl>
          <div><dt>검증됨</dt><dd>{workspace.summary.verified_count ?? 0}</dd></div>
          <div><dt>측정 주의</dt><dd>{workspace.summary.measured_caution_count ?? 0}</dd></div>
          <div><dt>지금 해결</dt><dd>{workspace.summary.resolve_now_count ?? 0}</dd></div>
          <div><dt>개발 차단</dt><dd>{workspace.summary.engineering_blocker_count ?? 0}</dd></div>
          <div><dt>인수할 한계</dt><dd>{workspace.summary.accepted_limit_count ?? 0}</dd></div>
          <div><dt>최종 판단</dt><dd>{workspace.summary.final_decision_count ?? 0}</dd></div>
          <div><dt>Monitoring</dt><dd>{workspace.summary.monitoring_transfer_count ?? 0}</dd></div>
        </dl>
      </section>

      <section className="pv2-step">
        <StepTitle step="3. 결과 해석과 해결 구분" title="검증된 내용과 남은 판단을 구분합니다" detail="해결할 수 있는 일과 Final Review로 넘길 항목을 섞지 않습니다." />
        {visibleVerified.length > 0 && (
          <div className="pv2-lane"><h3>검증된 내용</h3><div className="pv2-card-grid">
            {visibleVerified.map((item) => (
              <article key={item.finding_id}><strong>{item.title}</strong><p>{item.detail}</p></article>
            ))}
          </div>
          {workspace.verified_findings.length > visibleVerified.length && (
            <p>나머지 {workspace.verified_findings.length - visibleVerified.length}개 통과 근거는 상세 검증 근거에서 확인할 수 있습니다.</p>
          )}</div>
        )}
        {measuredCautions.length > 0 && (
          <div className="pv2-lane"><h3>주의해서 볼 결과</h3><div className="pv2-card-grid">
            {measuredCautions.map((issue) => <IssueCard issue={issue} workspace={workspace} key={issue.root_issue_id} />)}
          </div></div>
        )}
        {resolveNow.length > 0 && (
          <div className="pv2-lane"><h3>지금 해야 할 일</h3><div className="pv2-card-grid">
            {resolveNow.map((issue) => <IssueCard issue={issue} workspace={workspace} key={issue.root_issue_id} />)}
          </div></div>
        )}
        {engineeringRequired.length > 0 && (
          <div className="pv2-lane"><h3>개발 후 재검토</h3><div className="pv2-card-grid">
            {engineeringRequired.map((issue) => <IssueCard issue={issue} workspace={workspace} key={issue.root_issue_id} />)}
          </div></div>
        )}
        {handoff.length > 0 && (
          <div className="pv2-lane"><h3>Final Review로 넘길 것</h3><div className="pv2-card-grid">
            {handoff.map((issue) => <IssueCard issue={issue} workspace={workspace} key={issue.root_issue_id} />)}
          </div></div>
        )}
        <details className="pv2-disclosure"><summary>상세 검증 근거</summary>
          {workspace.category_disclosures.map((group) => (
            <article key={group.category_id}>
              <strong>{group.title}</strong><span>{group.outcome}</span><p>{group.question}</p>
              <ul>
                {group.technical_rows.map((row) => (
                  <li key={`${group.category_id}-${row.row_id}`}>
                    <b>{row.title}</b><span>{row.status}</span><p>{row.detail}</p>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </details>
      </section>

      <section className="pv2-step pv2-final-action">
        <StepTitle step="4. 저장하고 Final Review로 이동" title="현재 검증 결과를 기록하고 다음 판단으로 이동합니다" detail="이동은 최종 승인이나 주문 실행이 아닙니다." />
        <div>
          <button
            type="button"
            disabled={!workspace.actions.save_audit_only.enabled}
            onClick={() => emit({
              action: "save_audit_only",
              intent_id: intentId("audit"),
              selection_source_id: workspace.candidate.selection_source_id,
              validation_result_id: validationResultId,
            })}
          >
            {workspace.actions.save_audit_only.label}
          </button>
          <button
            type="button"
            disabled={!workspace.actions.save_and_move.enabled}
            onClick={() => emit({
              action: "save_and_move",
              intent_id: intentId("move"),
              selection_source_id: workspace.candidate.selection_source_id,
              validation_result_id: validationResultId,
            })}
          >
            {workspace.actions.save_and_move.label}
          </button>
        </div>
      </section>
    </main>
  )
}
```

- [ ] **Step 6: Create the Streamlit connection entrypoint**

Create `frontend/src/index.tsx`:

```tsx
import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { PracticalValidationDecisionWorkspace } from "./PracticalValidationDecisionWorkspace"
import { DecisionWorkspace } from "./types"
import "./style.css"

type StreamlitArgs = { workspace?: DecisionWorkspace }

function Connected({ args }: { args: StreamlitArgs }) {
  React.useEffect(() => {
    Streamlit.setFrameHeight()
  }, [args])
  if (!args.workspace) {
    return <div className="pv2-empty">Practical Validation workspace payload를 읽을 수 없습니다.</div>
  }
  return <PracticalValidationDecisionWorkspace workspace={args.workspace} />
}

const Component = withStreamlitConnection(Connected)
createRoot(document.getElementById("root")!).render(<Component />)
```

Use the same dependency versions as the existing Practical Validation component package, keep Vite `base: "./"`, and generate `package-lock.json` with `npm install`.

- [ ] **Step 7: Implement the Level3-compatible visual contract**

Create `frontend/src/style.css` with these required base tokens and responsive rules:

```css
:root {
  color: #152033;
  background: transparent;
  font-family: Inter, Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --pv2-ink: #152033;
  --pv2-muted: #647589;
  --pv2-line: #dae4ee;
  --pv2-line-soft: #e8edf3;
  --pv2-paper: #ffffff;
  --pv2-wash: #f7fafc;
  --pv2-blue: #284e69;
  --pv2-positive: #17695e;
  --pv2-warning: #a24d19;
  --pv2-danger: #a13f3f;
  --pv2-shadow: 0 10px 30px rgba(33, 53, 72, .055);
}

* { box-sizing: border-box; }
html, body, #root { width: 100%; min-width: 0; margin: 0; background: transparent; }
button { font: inherit; }

.pv2-workspace {
  display: grid;
  gap: 18px;
  width: 100%;
  min-width: 0;
  padding: 4px 2px 18px;
  color: var(--pv2-ink);
}

.pv2-header {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(260px, .72fr);
  gap: 24px;
  padding: 22px 24px;
  border: 1px solid var(--pv2-line);
  border-radius: 20px;
  background: linear-gradient(135deg, #f8fbff 0%, #f1f7f7 100%);
}

.pv2-header h1,
.pv2-step h2,
.pv2-verdict h2 {
  margin: 0;
  overflow-wrap: anywhere;
}

.pv2-header > aside,
.pv2-replay,
.pv2-final-action > div,
.pv2-disclosure {
  padding: 14px;
  border: 1px solid var(--pv2-line);
  border-radius: 14px;
  background: rgba(255, 255, 255, .82);
}

.pv2-step,
.pv2-verdict {
  padding: 22px 24px;
  border: 1px solid var(--pv2-line);
  border-radius: 17px;
  background: var(--pv2-paper);
  box-shadow: var(--pv2-shadow);
}

.pv2-step-title {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.pv2-choice-grid,
.pv2-profile-grid,
.pv2-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.pv2-replay {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  margin-top: 14px;
}

.pv2-final-action > div {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}

.pv2-choice-grid button,
.pv2-profile-grid button,
.pv2-replay button,
.pv2-final-action button,
.pv2-issue-card button {
  min-width: 0;
  padding: 11px 13px;
  border: 1px solid var(--pv2-line);
  border-radius: 14px;
  color: var(--pv2-ink);
  background: #fff;
  cursor: pointer;
}

.pv2-choice-grid button.is-selected,
.pv2-profile-grid button.is-selected {
  border-color: #6f91a7;
  background: #eef5f8;
  box-shadow: inset 0 0 0 1px #6f91a7;
}

.pv2-verdict dl {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.pv2-lane + .pv2-lane { margin-top: 18px; }

.pv2-card-grid article,
.pv2-issue-card {
  min-width: 0;
  padding: 14px;
  border: 1px solid var(--pv2-line-soft);
  border-radius: 14px;
  background: var(--pv2-wash);
  overflow-wrap: anywhere;
}

.pv2-disclosure article {
  padding: 14px 0;
  border-top: 1px solid var(--pv2-line-soft);
}

.pv2-disclosure ul {
  display: grid;
  gap: 8px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.pv2-disclosure li {
  min-width: 0;
  padding: 10px 12px;
  border-radius: 14px;
  background: var(--pv2-wash);
  overflow-wrap: anywhere;
}

.pv2-tone-positive { background: linear-gradient(135deg, #eef8f4 0%, #f8fbf9 100%); }
.pv2-tone-warning { background: linear-gradient(135deg, #fff6ef 0%, #fffbf8 100%); }
.pv2-tone-danger { background: linear-gradient(135deg, #fff2f1 0%, #fffafa 100%); }
.pv2-tone-neutral { background: linear-gradient(135deg, #f6f9fb 0%, #fbfcfd 100%); }

button:disabled { cursor: not-allowed; opacity: .48; }

@media (max-width: 760px) {
  .pv2-header,
  .pv2-step-title,
  .pv2-replay,
  .pv2-verdict dl,
  .pv2-choice-grid,
  .pv2-profile-grid,
  .pv2-card-grid {
    grid-template-columns: 1fr;
  }

  .pv2-final-action > div {
    display: grid;
    grid-template-columns: 1fr;
  }

  .pv2-final-action button {
    width: 100%;
  }

  .pv2-header,
  .pv2-step,
  .pv2-verdict {
    padding: 18px;
  }
}
```

- [ ] **Step 8: Extract Python execution handlers and consume intents**

In `app/web/backtest_practical_validation/page.py`, add:

```python
def _execute_practical_validation_replay(
    source: dict[str, Any],
    *,
    mode: str = RECHECK_MODE_EXTEND_TO_LATEST,
) -> dict[str, Any]:
    replay_result = run_practical_validation_actual_replay(source, mode=mode)
    st.session_state[_replay_state_key(source, mode)] = replay_result
    return dict(replay_result or {})
```

Make `_render_actual_replay_panel(...)` call `_execute_practical_validation_replay(...)` so fallback and React use the same execution boundary.

In `app/services/backtest_evidence_closure.py`, now that the replay execution
boundary exists, change only the replay registry handler to:

```python
"handler": "app.web.backtest_practical_validation.page:_execute_practical_validation_replay"
```

Keep the provider execution boundary created and contract-tested in Task 1.

Add a nonce guard and intent consumer:

```python
def _consume_practical_validation_decision_workspace_intent(
    intent: dict[str, Any] | None,
    *,
    sources: list[dict[str, Any]],
    source: dict[str, Any],
    validation_result: dict[str, Any] | None,
    replay_result: dict[str, Any] | None,
) -> None:
    if not isinstance(intent, dict):
        return
    action = str(intent.get("action") or "").strip()
    intent_id = str(intent.get("intent_id") or "").strip()
    if not action or not intent_id:
        return
    consumed_key = "practical_validation_workspace_last_intent_id"
    if st.session_state.get(consumed_key) == intent_id:
        return
    st.session_state[consumed_key] = intent_id

    current_source_id = str(source.get("selection_source_id") or "")
    intent_source_id = str(intent.get("selection_source_id") or "")
    source_by_id = {
        str(row.get("selection_source_id") or ""): row
        for row in sources
    }
    if action == "select_source":
        if intent_source_id not in source_by_id:
            st.session_state["backtest_practical_validation_notice"] = "현재 후보 목록에 없는 source intent를 무시했습니다."
            st.rerun()
        st.session_state["practical_validation_selected_source_id"] = intent_source_id
        _clear_practical_validation_replay_state()
        st.rerun()

    if intent_source_id != current_source_id:
        st.session_state["backtest_practical_validation_notice"] = "후보가 바뀌어 이전 화면 action을 실행하지 않았습니다."
        st.rerun()

    if action == "select_profile_preset":
        profile_id = str(intent.get("profile_id") or "")
        if profile_id not in VALIDATION_PROFILE_OPTIONS:
            st.session_state["backtest_practical_validation_notice"] = "지원하지 않는 검증 프로필입니다."
            st.rerun()
        st.session_state["practical_validation_profile_id"] = profile_id
        _clear_practical_validation_replay_state(current_source_id)
        st.rerun()

    if action == "run_replay":
        _execute_practical_validation_replay(source)
        st.session_state["backtest_practical_validation_notice"] = "최신 데이터 기준 재검증을 완료했습니다."
        st.rerun()

    if action == "run_resolution_action":
        if not validation_result:
            st.session_state["backtest_practical_validation_notice"] = "현재 검증 결과가 없어 action을 실행하지 않았습니다."
            st.rerun()
        validation_id = str(validation_result.get("validation_id") or "")
        if str(intent.get("validation_result_id") or "") != validation_id:
            st.session_state["backtest_practical_validation_notice"] = "검증 결과가 바뀌어 이전 action을 실행하지 않았습니다."
            st.rerun()
        closure = dict(validation_result.get("evidence_closure") or {})
        issue = next(
            (
                dict(row)
                for row in list(closure.get("issues") or [])
                if str(dict(row).get("root_issue_id") or "")
                == str(intent.get("root_issue_id") or "")
            ),
            {},
        )
        action_id = str(intent.get("action_id") or "")
        if (
            not issue
            or not issue.get("actionable_now")
            or str(issue.get("action_id") or "") != action_id
            or not has_action_handler(action_id)
        ):
            st.session_state["backtest_practical_validation_notice"] = "현재 실행 가능한 해결 action이 아닙니다."
            st.rerun()
        if action_id == "run_practical_validation_provider_gap_collection":
            _execute_practical_validation_provider_gap_collection(validation_result)
            st.rerun()
        if action_id == "run_practical_validation_replay":
            _execute_practical_validation_replay(source)
            st.rerun()

    if action in {"save_audit_only", "save_and_move"}:
        validation_id = str(dict(validation_result or {}).get("validation_id") or "")
        if (
            not validation_id
            or str(intent.get("validation_result_id") or "") != validation_id
        ):
            st.session_state["backtest_practical_validation_notice"] = "검증 결과가 바뀌어 이전 저장 action을 실행하지 않았습니다."
            st.rerun()
        _consume_practical_validation_next_stage_action(
            {
                "action": action,
                "source": "practical_validation_decision_workspace",
                "nonce": intent_id,
            },
            source=source,
            validation_result=dict(validation_result or {}),
            replay_result=replay_result,
        )
```

Allow `"practical_validation_decision_workspace"` in `_consume_practical_validation_next_stage_action(...)` event-source validation.

- [ ] **Step 9: Replace the active page render with one shell**

In `app/web/backtest_practical_validation/workspace_panel.py`, add
`render_practical_validation_decision_workspace_fallback(workspace)`. It must
consume only the new Python read model and return the same intent shapes as React.
Render, in order:

1. question / candidate / as-of header
2. source and preset choices
3. replay state and replay button
4. verdict plus the same seven summary counts
5. non-empty verified, measured caution, resolve-now, engineering, handoff lanes
6. collapsed `상세 검증 근거`
7. audit save and save-and-move buttons

Use the read model's precomputed `finding_kind`, `actionable_now`, action ids, and
enabled flags. Do not read raw module statuses or recalculate the Gate. Do not
render an empty action lane. Match React's first-read density by showing at most
eight verified cards and leaving the full list in `상세 검증 근거`.

In `render_practical_validation_workspace()`:

1. Keep source loading and protected notice handling.
2. Resolve selected source from `practical_validation_selected_source_id`; use the first source when missing. If no source exists, use `source={}` and render the read model's `source_required` state instead of returning to a separate legacy empty screen.
3. Build the current profile from `practical_validation_profile_id` plus existing answer session keys without rendering the old form first.
4. Read the default latest replay state.
5. Build `validation_result` only when current-session replay exists.
6. Build the new decision workspace model for both replay-required and result-ready states.
7. Render the new component once.
8. Consume its intent.
9. Keep normalized category evidence inside React's `상세 검증 근거`; put custom profile questions, advanced replay mode, full source snapshot, and raw JSON under one secondary `st.expander("고급 설정과 원본 근거", expanded=False)`.

The active path must contain:

```python
workspace_model = build_practical_validation_decision_workspace(
    source=source,
    validation_profile=validation_profile,
    replay_result=replay_result,
    validation_result=validation_result,
    source_options=selectable_sources,
)
if is_practical_validation_decision_workspace_available():
    intent = render_practical_validation_decision_workspace(
        workspace=workspace_model,
        key=f"practical-validation-decision-workspace-{selected_source_id}",
    )
else:
    intent = render_practical_validation_decision_workspace_fallback(
        workspace_model
    )
_consume_practical_validation_decision_workspace_intent(
    intent,
    sources=selectable_sources,
    source=source,
    validation_result=validation_result,
    replay_result=replay_result,
)
```

Do not call these in the active path:

```python
render_practical_validation_workspace_overview(...)
_render_data_action_board(...)
_render_final_review_data_enrichment_handoff(...)
_render_practical_validation_recovery_progress(...)
```

Keep the old functions, `practical_validation_fix_queue`, and
`practical_validation_data_action_board` as compatibility code; do not delete
them in this task. Recovery is represented by the new replay-required state and
resolution lane instead of another first-read panel.

- [ ] **Step 10: Run React build and GREEN tests**

Run:

```bash
cd app/web/components/practical_validation_decision_workspace/frontend
npm install
npm run build
```

Expected: Vite production build succeeds and creates `frontend/build/index.html`.

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_practical_validation_decision_workspace \
  tests.test_practical_validation_market_context_visual_contract \
  tests.test_backtest_refactor_boundaries \
  tests.test_backtest_evidence_closure
```

Expected: all tests pass.

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/backtest_practical_validation_decision_workspace.py \
  app/web/backtest_practical_validation/page.py \
  app/web/backtest_practical_validation/workspace_panel.py \
  app/web/components/practical_validation_decision_workspace/component.py
git diff --check
```

Expected: all commands succeed.

- [ ] **Step 11: Commit 3차**

```bash
git add \
  app/services/backtest_evidence_closure.py \
  app/web/components/practical_validation_decision_workspace \
  app/web/backtest_practical_validation/page.py \
  app/web/backtest_practical_validation/workspace_panel.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_backtest_practical_validation_decision_workspace.py \
  tests/test_practical_validation_market_context_visual_contract.py
git commit -m "Practical Validation Level2 원셸 UI 전환"
```

---

### Task 4: Runtime QA / Documentation / Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-level2-decision-workspace-v1-20260716/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-level2-decision-workspace-v1-20260716/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-level2-decision-workspace-v1-20260716/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-level2-decision-workspace-v1-20260716/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Documentation canonical flow: four visible steps plus Step 3 disclosure
- Completion evidence: focused tests, production build, py_compile, diff check, Browser QA
- Commit policy: protected JSONL and generated screenshots remain unstaged

- [ ] **Step 1: Run the current GRS read-only projection probe**

Use the runtime loader and new builder without appending:

```bash
.venv/bin/python - <<'PY'
from app.runtime import load_portfolio_selection_sources, load_practical_validation_results
from app.services.backtest_practical_validation_decision_workspace import (
    build_practical_validation_decision_workspace,
)
from app.services.backtest_practical_validation_source import build_validation_profile

sources = load_portfolio_selection_sources(limit=100)
validations = load_practical_validation_results(limit=100)
validation = next(
    row
    for row in reversed(validations)
    if row.get("selection_source_id")
    and row.get("evidence_closure")
    and row.get("final_review_gate", {}).get("can_save_and_move")
)
source = next(
    row
    for row in sources
    if row.get("selection_source_id") == validation.get("selection_source_id")
)
model = build_practical_validation_decision_workspace(
    source=source,
    validation_profile=build_validation_profile("balanced_core", {}),
    replay_result={"status": "PASS", "replay_id": "read-only-probe"},
    validation_result=validation,
    source_options=[source],
)
print(
    model["state"],
    model["summary"]["resolve_now_count"],
    model["summary"]["engineering_blocker_count"],
    model["summary"]["accepted_limit_count"],
    model["summary"]["final_decision_count"],
)
PY
```

Expected for the current eligible GRS-shaped row:

```text
ready_with_handoff 0 0 6 1
```

If the current user registry contains a newer different candidate, record the actual counts in `RUNS.md`; do not rewrite the row to force these numbers.

- [ ] **Step 2: Run fresh focused completion tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_practical_validation_decision_workspace \
  tests.test_practical_validation_market_context_visual_contract \
  tests.test_backtest_evidence_closure \
  tests.test_backtest_refactor_boundaries \
  tests.test_service_contracts.PracticalValidationServiceContractTests \
  tests.test_service_contracts.PracticalValidationReplayServiceContractTests
```

Expected: all tests pass. Record the exact test count and elapsed time in `RUNS.md`.

- [ ] **Step 3: Run build, compile, and diff verification**

Run:

```bash
cd app/web/components/practical_validation_decision_workspace/frontend
npm run build
```

Run from repository root:

```bash
.venv/bin/python -m py_compile \
  app/services/backtest_construction_risk_audit.py \
  app/services/backtest_evidence_closure.py \
  app/services/backtest_practical_validation.py \
  app/services/backtest_practical_validation_decision_workspace.py \
  app/services/backtest_practical_validation_workspace.py \
  app/web/backtest_practical_validation/page.py \
  app/web/backtest_practical_validation/workspace_panel.py \
  app/web/components/practical_validation_decision_workspace/component.py
git diff --check
```

Expected: production build and py_compile succeed; `git diff --check` prints nothing.

- [ ] **Step 4: Restart the Streamlit process before Browser QA**

The current app may run with `--fileWatcherType none`. Read the current terminal/process command, stop only the process serving this worktree, and restart it with the same environment and port.

Do not run provider collection, audit save, or Final Review save merely to create
QA data. If no current-session replay exists after restart, one replay is allowed
because it is the required product transition being tested; record any generated
run-history artifact and keep it unstaged. Do not rewrite or delete existing JSONL
rows and do not run DB ingestion.

- [ ] **Step 5: Execute desktop Browser QA**

At `http://localhost:8505/backtest`, verify:

1. Practical Validation opens one question-first workspace instead of separate square Flow containers.
2. source options and profile presets appear inside Step 1.
3. Step 2 explains current replay state and exposes one replay intent.
4. current eligible result says `Final Review로 이동할 수 있습니다`.
5. summary separates `검증됨`, `측정 주의`, `지금 해결`, `개발 차단`, `인수할 한계`, `최종 판단`, `Monitoring`.
6. zero resolve-now items do not render an empty data-action board.
7. `Final Review로 넘길 것` contains accepted limits and final-decision input without `미정` as a primary label.
8. normalized category rows are collapsed under `상세 검증 근거`, while advanced settings and raw evidence stay under `고급 설정과 원본 근거`.
9. no horizontal overflow or clipped long evidence text.
10. browser console has no component error.

- [ ] **Step 6: Execute 760px Browser QA**

Verify at 760px:

1. header, source/profile choices, replay, verdict metrics, finding lanes, final actions are one column.
2. buttons remain fully visible.
3. root issue titles and long source text wrap.
4. outer document `scrollWidth == clientWidth`.
5. component document `scrollWidth == clientWidth`.

Capture one screenshot such as `qa-practical-validation-level2-decision-workspace-760.png`. Keep it untracked and do not stage it.

- [ ] **Step 7: Synchronize durable docs**

Update the canonical wording to:

```text
Practical Validation visible flow:
1. 후보와 검증 기준 확인
2. 최신 데이터 기준 재검증
3. 결과 해석과 해결 구분
4. 저장하고 Final Review로 이동

상세 검증 근거는 Step 3 disclosure이며 별도 Flow 5가 아니다.
```

Document:

- new service owner `app/services/backtest_practical_validation_decision_workspace.py`
- new React owner `app/web/components/practical_validation_decision_workspace/`
- old Fix Queue / Data Action Board are compatibility-only, not active first-read
- Python owns finding / applicability / Gate / action / replay / save
- current eligible result requires unresolved actionable / critical engineering / missing contract 0
- accepted limit / final decision / monitoring transfer are Final Review handoff, not Level2 repair queue

- [ ] **Step 8: Close the active task records**

Set `STATUS.md` to:

```markdown
Status: Completed
Last Updated: 2026-07-16

## 전체 Roadmap

- [x] 1차 Validation Truth / Finding Contract
- [x] 2차 Level2 Decision Workspace Read Model
- [x] 3차 One-Shell UI / Intent Integration
- [x] 4차 QA / Docs / Closeout

## Next Action

남은 위험은 dynamic historical universe의 PIT membership / delisting provider이며 별도 승인 전까지 critical blocker로 유지한다.
```

Record:

- each commit hash
- exact test count
- Vite module count
- py_compile targets
- desktop / 760 QA scope
- registry / run history exclusion
- any residual legacy component removal decision

Move the active pointers in INDEX / ROADMAP / task README / STATUS_MANIFEST back to `none` only after all four implementation commits and fresh verification pass.

- [ ] **Step 9: Verify staged scope and commit 4차**

Stage only code tests and durable docs from this task:

```bash
git add \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/tasks/active/README.md \
  .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md \
  .aiworkspace/note/finance/tasks/active/practical-validation-level2-decision-workspace-v1-20260716 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git diff --cached --name-only
```

Confirm the staged name list does not include:

```text
.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl
.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl
*.png
.superpowers/
```

Commit:

```bash
git commit -m "Practical Validation Level2 QA와 문서 동기화"
```

## Completion Gate

Do not claim completion until all are freshly true:

- 1차~4차 distinct Korean commits exist.
- focused service / closure / boundary / visual tests pass.
- React production build passes.
- target py_compile passes.
- `git diff --check` passes.
- desktop and 760px Browser QA pass.
- current eligible result has no unresolved actionable, critical engineering, or missing contract.
- zero-action result has no empty action board.
- protected registry / run history / saved JSONL / generated screenshots remain unstaged.

---

## Approved Correction Execution

2026-07-16 실화면 확인 후 승인된 correction이다. 아래 Task 5~9가 기존
Browser-QA-only closeout을 대체한다. 각 task는 RED 확인, 최소 GREEN 구현,
focused regression, 한국어 commit 순서로 실행한다.

### Task 5: Level2-Owned Caution And Evidence-State Contract

**Files:**
- Modify: `app/services/backtest_evidence_closure.py`
- Modify: `app/services/backtest_practical_validation_modules.py`
- Modify: `app/services/backtest_practical_validation_decision_workspace.py`
- Modify: `tests/test_backtest_evidence_closure.py`
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`

**Interfaces:**
- Produces closure class `validated_caution`
- Produces module field `evidence_state`
- Produces summary field `validated_caution_count`
- Preserves explicit static-universe `accepted_limit`
- Blocks missing required validation as `engineering_required`

- [x] Add a RED test proving a `pv_practical_caution` module with
  `evidence_state=computed` becomes `validated_caution`, owner
  `practical_validation`, terminal `resolved`.
- [x] Add a RED test proving the same role with `evidence_state=missing`
  becomes critical `engineering_required`.
- [x] Change the current six-default-accepted-limit GRS fixture so Level2
  cautions no longer appear in `final_review_handoff`.
- [x] Add explicit module evidence-state projection from audit / diagnostic
  status without parsing prose into fabricated measurements.
- [x] Run focused closure / workspace / service regressions and py_compile.
- [x] Commit: `Practical Validation Level2 주의 종결 계약 보정`.

### Task 6: Candidate/Policy Separation And Fragment Revalidation

**Files:**
- Modify: `app/services/backtest_practical_validation_decision_workspace.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/types.ts`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: relevant `tests/test_service_contracts.py`

**Interfaces:**
- Produces human source labels from `source_kind`
- Produces separate candidate summary and validation-policy model
- Produces fragment rerun boundary for selection / replay / resolution
- Preserves app rerun for Final Review navigation

- [x] Add RED boundary tests for `1A. 검증할 후보 선택`,
  `1B. 어떤 관점으로 검증할까요?`, selected active state, and no
  selected-button disabled opacity.
- [x] Add RED service tests for `weighted_portfolio_mix -> 혼합 포트폴리오`,
  `latest_backtest_run -> 단일 전략 실행`.
- [x] Add RED page tests proving replay and selection use
  `st.rerun(scope="fragment")`, while `save_and_move` route navigation uses
  app rerun.
- [x] Extract the one-shell interaction into an `@st.fragment` render boundary.
- [x] Keep the same Python intent validation and current-session replay guards.
- [x] Add React pending state so only Step 2/result content shows revalidation
  progress while Step 1 remains mounted.
- [x] Run focused UI boundary tests, React production build, py_compile.
- [x] Commit: `Practical Validation 후보 선택과 부분 재검증 개선`.

### Task 7: Plain-Language Explanation And Category Evidence UI

**Files:**
- Create: `app/services/backtest_practical_validation_explanation.py`
- Modify: `app/services/backtest_practical_validation_decision_workspace.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/types.ts`
- Create: `tests/test_backtest_practical_validation_explanation.py`
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `tests/test_practical_validation_market_context_visual_contract.py`

**Interfaces:**
- Produces `explain_practical_validation_row(row, *, stage_owner) -> dict`
- Produces `display_title`, `status_label`, `what_was_checked`,
  `result_summary`, `meaning`, `next_action`, `evidence_state`,
  `technical_trace`
- Produces five normalized evidence categories and per-category counts

- [x] Add RED tests for walk-forward, regime split, provider freshness,
  cost sensitivity, tax/account, NOT_RUN, and NOT_APPLICABLE explanations.
- [x] Add RED tests proving first-read text contains no raw function path and
  technical trace is nested separately.
- [x] Implement the pure explanation mapping without importing private Final
  Review functions.
- [x] Project verified findings, cautions, and technical rows through the new
  explanation contract.
- [x] Replace the all-expanded detail list with category selectors and one
  active category panel.
- [x] Mirror the same explanation order in Python fallback.
- [x] Run focused service / visual contract tests, React build, py_compile.
- [x] Commit: `Practical Validation 검증 설명과 상세 근거 개선`.

### Task 8: In-Scope Missing Validation And Aggregation Hardening

**Files:**
- Modify as required:
  `app/services/backtest_validation_efficacy.py`,
  `app/services/backtest_construction_risk_audit.py`,
  `app/services/backtest_realism_audit.py`,
  `app/services/backtest_practical_validation_modules.py`,
  `app/services/backtest_evidence_closure.py`
- Modify focused tests for each changed producer

**Constraints:**
- Do not add a historical universe / delisting provider.
- Do not redesign DB schema or strategy runtime.
- Reuse existing replay / provider collection handlers only.

- [x] Add RED tests proving PASS / NOT_APPLICABLE rows do not keep a module in
  REVIEW solely because of an irrelevant row.
- [x] Add RED tests distinguishing stress `기간 미포함` from a missing validator.
- [x] Add RED tests ensuring required strategy-specific validation that is
  genuinely NOT_RUN becomes engineering-required rather than handoff.
- [x] Connect refreshable provider gaps to the existing registered Level2
  collection action; leave non-refreshable missing validators blocked.
- [x] Run focused producer / module / closure regressions and py_compile.
- [x] Commit: `Practical Validation 미검증 항목과 집계 기준 보강`.

### Task 9: Runtime QA, Documentation, And Closeout

**Files:**
- Modify canonical finance docs only where behavior changed
- Modify active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify root handoff logs

- [x] Reproject the current latest GRS row read-only and record Level2
  validated-caution / action / engineering / explicit handoff counts.
- [x] Add a RED/GREEN regression proving measured accepted-limit evidence
  remains a Final Review handoff instead of disappearing into the Level2
  measured-caution lane.
- [x] Run all focused closure / service / boundary / visual contract tests.
- [x] Run React production build, target py_compile, `git diff --check`.
- [x] Restart only the Streamlit process serving this worktree if needed.
- [ ] Execute desktop and 760px Browser QA, including replay partial refresh,
  console, outer/component overflow, candidate/policy separation, readable
  evidence, and empty-action suppression.
- [ ] Capture generated screenshots and keep them unstaged.
- [x] Synchronize canonical flow / architecture docs, active task, INDEX /
  ROADMAP, and root handoff logs.
- [x] Confirm protected registries, run history, saved JSONL, screenshots,
  `.superpowers/`, and run artifacts are absent from staged files.
- [x] Commit: `Practical Validation Level2 보정 QA와 문서 동기화`.

## Correction Completion Gate

Do not close this task until:

- Task 5~9 Korean commits exist.
- Level2 caution is not blindly handed to Final Review.
- missing required validation blocks instead of becoming accepted limit.
- candidate and validation policy are visually distinct.
- replay keeps the upper selection context stable.
- user-facing validation evidence is plain Korean with raw trace secondary.
- desktop / 760px Browser QA and screenshots exist.
- focused tests, React build, py_compile, and diff-check pass freshly.
- protected files and generated artifacts remain unstaged and uncommitted.

---

## Approved Provider And Final Review Handoff Execution

2026-07-17 사용자 승인에 따라 기존 closeout 뒤 발견된 provider adapter와
Final Review handoff 소비 불일치를 아래 Task 10~12로 보정한다.

### Task 10: ETF Provider Adapter Contract

**Files:**
- Modify: `finance/data/etf_provider.py`
- Modify: focused provider tests

**Interfaces:**
- Produces parser `ishares_workbook`
- Produces parser `vanguard_json`
- Reuses `finance_meta.etf_provider_source_map`
- Reuses `finance_meta.etf_holdings_snapshot`
- Reuses `finance_meta.etf_exposure_snapshot`

- [x] Add RED tests for COMT/EFA/LQD/TIP SpreadsheetML verification and parsing.
- [x] Add RED tests for VNQ source discovery, verification, and JSON parsing.
- [x] Implement the two provider adapters without schema or ingestion-job changes.
- [x] Run focused provider/source-map/collection tests and py_compile.
- [x] Commit: `ETF 공식 보유종목 수집 어댑터 보강`.

### Task 11: Final Review Handoff Promotion Contract

**Files:**
- Modify: `app/services/backtest_final_review_decision_brief.py`
- Modify: `app/services/backtest_practical_validation_decision_workspace.py`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: focused Final Review / Level2 tests

**Interfaces:**
- Produces `level2_handoff` with distinct `final_decisions`, `accepted_limits`,
  `monitoring_conditions`
- Preserves Final Review route and persistence ownership
- Suppresses incomplete unstructured monitoring transfer

- [x] Add RED tests proving each resolution class has one explicit Final Review section.
- [x] Add RED tests proving duplicate root issues and incomplete monitoring conditions are excluded.
- [x] Add RED tests for blocked Level2 prospective copy and eligible promotion copy.
- [x] Implement Python projection, React presentation, and Streamlit fallback.
- [x] Run focused service / boundary / visual tests, React build, py_compile.
- [x] Commit: `Final Review Level2 인계 판단 화면 보강`.

### Task 12: Runtime QA, Docs, And Closeout

**Files:**
- Modify canonical finance docs where source and handoff behavior changed
- Modify active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify root handoff logs

- [x] Run actual official-source collection for COMT, EFA, LQD, TIP, VNQ through the
  existing job and verify read-only snapshot projection.
- [x] Re-run designated candidate Level2 projection and Final Review read model.
- [x] Run fresh focused and completion test suites.
- [x] Run both React production builds, target py_compile, and `git diff --check`.
- [x] Execute desktop and 760px Browser QA and keep screenshots unstaged.
- [x] Synchronize canonical docs, active task, and root handoff logs.
- [x] Confirm protected registry/run-history/saved/artifact files are not committed.
- [x] Commit: `ETF 수집과 Final Review 인계 QA 문서 동기화`.

---

## Approved Atomic Revalidation And Actionable Handoff Execution

2026-07-17 사용자 승인에 따라 재검증 one-shell 공백 회귀와 정적인 Final Review
handoff를 아래 Task 13~16으로 보정한다. 기존 validation 계산, canonical route,
append-only registry 계약은 유지한다.

### Task 13: Atomic Practical Validation Revalidation

**Files:**
- Modify: `app/web/components/practical_validation_decision_workspace/component.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- `render_practical_validation_decision_workspace(..., on_change: Callable[[], None] | None)`
- `_consume_practical_validation_component_change(*, component_key, sources, source, validation_result, replay_result)`
- `_consume_practical_validation_decision_workspace_intent(..., rerun_scope="none")`

- [x] Add a RED wrapper test proving `on_change` reaches the declared component.
- [x] Add a RED callback test proving replay is consumed before projection and does not call `st.rerun`.
- [x] Add a RED boundary test rejecting explicit fragment rerun for local replay intent.
- [x] Implement callback-first local intent consumption and keep app rerun only for route movement.
- [x] Run:
  `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py tests/test_backtest_refactor_boundaries.py -q`.
- [x] Run target py_compile and commit `Practical Validation 재검증 화면 유지 보정`.

### Task 14: Compact Level2 Handoff Summary

**Files:**
- Modify: `app/services/backtest_practical_validation_decision_workspace.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/types.ts`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `tests/test_practical_validation_market_context_visual_contract.py`

**Interfaces:**
- Produces `handoff_summary.state/title/detail/counts/items`.
- Each item contains `root_issue_id`, `handoff_kind`, `handoff_label`, `title`,
  `summary`, `next_stage_action`.
- Keeps legacy `resolution_lanes.final_review_handoff` for compatibility only.

- [x] Add a RED service test for compact class labels and root deduplication.
- [x] Add a RED visual contract test proving the first-read uses
  `Final Review 인계 준비 완료` and does not render three empty lanes.
- [x] Implement the pure projection, React compact summary, and Python fallback.
- [x] Run focused service / visual tests and React production build.
- [x] Commit `Practical Validation Final Review 인계 요약 개선`.

### Task 15: Actionable Final Review Handoff

**Files:**
- Modify: `app/services/backtest_final_review_decision_brief.py`
- Modify: `app/web/backtest_final_review_helpers.py`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: `tests/test_backtest_final_review_decision_brief.py`
- Modify: relevant `tests/test_service_contracts.py`

**Interfaces:**
- Intent field `accepted_limit_acknowledgements: Array<{root_issue_id: string, decision: "accepted" | "return_to_level2"}>`.
- Python validator returns normalized root-deduplicated acknowledgements or one user-facing error.
- Persistence field `decision_brief_snapshot.accepted_limit_acknowledgements`.

- [x] Add RED pure-service tests for expected roots, duplicate/unknown roots, allowed decisions, and route consistency.
- [x] Add a RED page test proving missing acknowledgements do not append a decision row.
- [x] Add a RED persistence test proving normalized acknowledgements are stored.
- [x] Add RED React contract assertions for the two accepted-limit choices and intent payload.
- [x] Implement Python validation, React inputs, fallback inputs, and append-only snapshot persistence.
- [x] Run focused Final Review service / page / persistence / visual tests and React build.
- [x] Commit `Final Review 인계 한계 판단 기록 추가`.

### Task 16: Runtime QA, Documentation, And Closeout

**Files:**
- Modify canonical Backtest architecture / flow docs only where behavior changed.
- Modify active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`.
- Modify root handoff logs.

- [x] Run all focused Practical Validation / Final Review / closure / boundary tests freshly.
- [x] Run both React production builds, target py_compile, and `git diff --check`.
- [x] Browser QA desktop and 760px: replay pending, no one-shell disappearance,
  compact Level2 handoff, overflow, and console errors. 당시 8506 Browser policy
  차단분은 Task 17~18의 current 8505 build QA로 대체했다. accepted-limit 선택과
  return-to-Level2 route의 비시각 계약은 focused tests에서 확인했다.
- [x] Keep Task 17~18 current-build QA screenshots generated and unstaged.
- [x] Synchronize canonical docs, active task, and root handoff logs.
- [x] Confirm registry, run history, saved JSONL, screenshots, `.superpowers/`, and
  run artifacts are absent from staged files.
- [x] Commit `Practical Validation 인계 UX QA와 문서 동기화`.

---

## Approved Stable Context / Refresh Surface Execution

2026-07-17 사용자 재확인으로 Task 13의 callback-only 보정이 실제 iframe
unmount를 막지 못한 것을 확인했다. 기존 task와 branch에서 아래 Task 17~18을
이어 실행한다.

### Task 17: Stable Context / Decision Fragment Boundary

**Files:**
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Modify: `app/web/components/practical_validation_decision_workspace/component.py`
- Modify: Practical Validation React `src/` files
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: focused visual contract tests where needed

**Interfaces:**
- `render_practical_validation_decision_workspace(..., surface="context" | "decision")`
- context surface owns source/profile intent outside replay fragment
- decision surface owns replay/resolution/save intent inside replay fragment
- Python callback consumer validates a per-surface action allow-list

- [x] Add RED wrapper/React tests proving the explicit context/decision surface contract.
- [x] Add RED page boundary tests proving context render is outside the decision fragment.
- [x] Add RED callback tests rejecting cross-surface replay/profile intents.
- [x] Implement the two render boundaries without changing replay, Gate, or persistence truth.
- [x] Keep Python fallback aligned with the same two surfaces.
- [x] Run focused tests, Practical React production build, target py_compile, diff-check.
- [x] Commit `Practical Validation 재검증 렌더 경계 분리`.

### Task 18: Runtime QA, Documentation, And Closeout

**Files:**
- Modify canonical Backtest architecture / flow docs only where behavior changed.
- Modify active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`.
- Modify root handoff logs.

- [x] Restart only this worktree's Streamlit server when the current build is stale.
- [x] Browser QA desktop and 760px: replay click, stable upper context, lower pending/result
  replacement, scroll preservation, iframe seam, overflow, console error.
- [x] Capture generated screenshots and keep them unstaged.
- [x] Run fresh focused/completion suites, React build, py_compile, diff-check.
- [x] Synchronize canonical docs, active task, and root handoff logs.
- [x] Confirm protected registry/run-history/saved/artifact files are not staged or committed.
- [x] Commit `Practical Validation 재검증 경계 QA와 문서 동기화`.

---

## Approved Step 1 Selection IA Execution

2026-07-17 사용자는 visual companion의 B안 `선택 요약 + 컴팩트 컨트롤`과
760px profile 2열 줄바꿈을 승인했다. Task 19~21은 `DESIGN.md` acceptance
criteria 33~40만 구현하며 decision surface, replay lifecycle, Gate, persistence,
read model schema는 변경하지 않는다.

### Task 19: React Step 1 Compact Selection Surface

**Files:**
- Modify: `tests/test_practical_validation_market_context_visual_contract.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- Modify generated build files under `app/web/components/practical_validation_decision_workspace/frontend/build/`

**Interfaces:**
- Consumes existing `workspace.candidate`, `workspace.candidate_selector.options`, and
  `workspace.profile.options` without a schema change.
- Produces only existing `select_source` and `select_profile_preset` intents.
- `candidateListOpen: boolean` is React-local presentation state and is never sent to Python.

- [x] **Step 1: Replace the old header/grid visual assertions with RED selection-IA tests**

  Update `tests/test_practical_validation_market_context_visual_contract.py` with explicit
  source-order and responsive contracts:

  ```python
  def test_selected_candidate_context_is_inside_step_one_not_header(self) -> None:
      source = WORKSPACE.read_text(encoding="utf-8")
      header = source.split('<header className="pv2-header">', 1)[1].split("</header>", 1)[0]
      step_one = source.split('<section className="pv2-step">', 1)[1]

      self.assertNotIn("pv2-target-context", header)
      self.assertIn("pv2-selection-summary", step_one)
      self.assertIn("검증 대상", step_one)
      self.assertIn("판정 기준", step_one)
      self.assertLess(
          step_one.index("pv2-selection-summary"),
          step_one.index("pv2-candidate-toggle"),
      )

  def test_validation_profiles_use_five_columns_and_two_column_mobile_wrap(self) -> None:
      style = STYLE.read_text(encoding="utf-8")
      responsive = style.split("@media (max-width: 760px)", 1)[1]

      self.assertIn("grid-template-columns: repeat(5, minmax(0, 1fr));", style)
      self.assertIn(".pv2-profile-grid {\n    grid-template-columns: repeat(2, minmax(0, 1fr));", responsive)
      self.assertIn(".pv2-profile-grid button:last-child:nth-child(odd)", responsive)
      self.assertIn("grid-column: 1 / -1;", responsive)
  ```

  Extend `tests/test_backtest_refactor_boundaries.py`:

  ```python
  def test_practical_validation_candidate_selector_is_collapsed_inline_list(self) -> None:
      source = (PROJECT_ROOT / "app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx").read_text()
      context = source.split('{surface === "context"', 1)[1].split('{surface === "decision"', 1)[0]

      self.assertIn("candidateListOpen", context)
      self.assertIn('aria-expanded={candidateListOpen}', context)
      self.assertIn("pv2-candidate-list", context)
      self.assertNotIn('<div className="pv2-choice-grid">', context)
  ```

- [x] **Step 2: Run RED tests and confirm the old layout fails for the expected reasons**

  Run:

  ```bash
  .venv/bin/python -m unittest \
    tests.test_practical_validation_market_context_visual_contract \
    tests.test_backtest_refactor_boundaries
  ```

  Expected: FAIL because the header still owns `pv2-target-context`, the candidate grid is
  always open, and profile CSS is still 6-column `3 + 2`.

- [x] **Step 3: Implement the compact React selection surface**

  In `PracticalValidationDecisionWorkspace.tsx`, add local state and replace the context
  header/Step 1 selection markup with this contract:

  ```tsx
  const [candidateListOpen, setCandidateListOpen] = useState(false)

  <header className="pv2-header">
    <div>
      <p className="pv2-kicker">Practical Validation Decision Workspace</p>
      <h1>{workspace.header.question || "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?"}</h1>
      <p>{workspace.header.detail}</p>
    </div>
  </header>

  <div className="pv2-selection-summary">
    <div>
      <span>검증 대상</span>
      <strong>{workspace.candidate.title}</strong>
      <small>{workspace.candidate.source_type_label} · {workspace.candidate.as_of || "기준일 미측정"}</small>
    </div>
    <div>
      <span>판정 기준</span>
      <strong>{selectedProfile?.label || "판정 기준 미선택"}</strong>
    </div>
  </div>

  <div className="pv2-selection-section pv2-candidate-section">
    <div className="pv2-selection-control-row">
      <div className="pv2-subsection-title">
        <span>1A</span>
        <div>
          <h3>1A. 검증할 후보</h3>
          <p>현재 후보를 바꾸려면 목록을 여세요.</p>
        </div>
      </div>
      <button
        type="button"
        className="pv2-candidate-toggle"
        aria-expanded={candidateListOpen}
        onClick={() => setCandidateListOpen((open) => !open)}
      >
        {candidateListOpen ? "후보 목록 닫기" : "후보 변경"}
      </button>
    </div>
    {candidateListOpen && (
      <div className="pv2-candidate-list">
        {workspace.candidate_selector.options.map((option) => (
          <button
            type="button"
            className={option.selected ? "is-selected" : ""}
            aria-pressed={option.selected}
            disabled={!option.eligible}
            key={option.selection_source_id}
            onClick={() => {
              if (option.selected) {
                setCandidateListOpen(false)
                return
              }
              emit({
                action: "select_source",
                intent_id: intentId("source"),
                selection_source_id: option.selection_source_id,
                validation_result_id: workspace.validation_result_id,
              })
            }}
          >
            <strong>{option.title}</strong>
            <span>{option.source_type_label}</span>
          </button>
        ))}
      </div>
    )}
  </div>
  ```

  Resolve the selected profile label from the existing option list in React rather than
  adding a read-model field:

  ```tsx
  const selectedProfile = workspace.profile.options.find((option) => option.selected)
  ```

  Display `selectedProfile?.label || "판정 기준 미선택"` in the summary.

- [x] **Step 4: Implement exact desktop and 760px CSS behavior**

  In `style.css`, remove the old target aside, choice grid, 6-column profile, and centered
  fourth-button rules. Add:

  ```css
  .pv2-header { grid-template-columns: minmax(0, 1fr); }
  .pv2-selection-summary {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(180px, .4fr);
    gap: 10px;
    margin-top: 16px;
  }
  .pv2-selection-control-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 12px;
    align-items: center;
  }
  .pv2-candidate-list {
    display: grid;
    max-height: 264px;
    overflow-y: auto;
    overscroll-behavior: contain;
    gap: 8px;
  }
  .pv2-profile-grid { grid-template-columns: repeat(5, minmax(0, 1fr)); }
  .pv2-profile-grid button { grid-column: auto; }
  ```

  Under `@media (max-width: 760px)` add:

  ```css
  .pv2-selection-summary,
  .pv2-selection-control-row { grid-template-columns: 1fr; }
  .pv2-profile-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .pv2-profile-grid button:last-child:nth-child(odd) { grid-column: 1 / -1; }
  .pv2-candidate-toggle { width: 100%; }
  ```

- [x] **Step 5: Run GREEN tests and production build**

  Run the Step 2 command again. Expected: all tests pass.

  Run:

  ```bash
  cd app/web/components/practical_validation_decision_workspace/frontend
  npm run build
  ```

  Expected: Vite production build succeeds and tracked `build/` references the new bundle.

- [x] **Step 6: Commit the React implementation unit**

  Stage only the two tests, React source/CSS, and generated Practical build files. Confirm
  protected paths are absent, then commit:

  ```bash
  git commit -m "Practical Validation Step1 선택 UI 개선"
  ```

### Task 20: Python Fallback Selection Parity

**Files:**
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`

**Interfaces:**
- Consumes the same workspace candidate, selector options, and profile options.
- Produces the existing `_workspace_intent(action, workspace=workspace, **payload)` for
  `select_source` and `select_profile_preset`.
- Does not add session keys, registry writes, Gate calculation, or replay actions.

- [x] **Step 1: Add a RED fallback structure test**

  Add to `tests/test_backtest_refactor_boundaries.py`:

  ```python
  def test_practical_validation_fallback_summarizes_selection_before_change_controls(self) -> None:
      source = (PROJECT_ROOT / "app/web/backtest_practical_validation/workspace_panel.py").read_text()
      body = source.split("def _render_practical_validation_context_surface_fallback", 1)[1].split("\ndef ", 1)[0]

      self.assertIn('st.markdown("#### 1. 후보와 검증 기준")', body)
      self.assertIn('st.caption("검증 대상")', body)
      self.assertIn('st.caption("판정 기준")', body)
      self.assertIn('with st.expander("1A. 후보 변경", expanded=False):', body)
      self.assertLess(body.index('st.caption("검증 대상")'), body.index('with st.expander("1A. 후보 변경"')))
  ```

- [x] **Step 2: Run the focused fallback test and verify RED**

  Run:

  ```bash
  .venv/bin/python -m unittest \
    tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_fallback_summarizes_selection_before_change_controls
  ```

  Expected: FAIL because fallback currently puts the candidate caption above Step 1 and
  renders all candidates without an expander.

- [x] **Step 3: Align the Python fallback information order**

  Change `_render_practical_validation_context_surface_fallback` to render the fixed hero,
  Step 1 summary, and collapsed candidate list in this exact order:

  ```python
  st.markdown(
      f"### {header.get('question') or '이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?'}"
  )
  st.caption(str(header.get("detail") or ""))
  st.markdown("#### 1. 후보와 검증 기준")

  profile_options = [
      dict(row)
      for row in list(profile.get("options") or [])
      if isinstance(row, dict)
  ]
  selected_profile = next(
      (row for row in profile_options if bool(row.get("selected"))),
      {},
  )
  summary_columns = st.columns((3, 1))
  with summary_columns[0]:
      st.caption("검증 대상")
      st.markdown(f"**{candidate.get('title') or '-'}**")
      st.caption(f"{candidate.get('source_type_label') or '-'} · {candidate.get('as_of') or '-'}")
  with summary_columns[1]:
      st.caption("판정 기준")
      st.markdown(f"**{selected_profile.get('label') or '미선택'}**")

  with st.expander("1A. 후보 변경", expanded=False):
      if source_options:
          for option in source_options:
              option_id = str(option.get("selection_source_id") or "")
              if bool(option.get("selected")):
                  with st.container(border=True):
                      st.markdown(f"**✓ {option.get('title') or option_id or '후보'}**")
                      st.caption(str(option.get("source_type_label") or "검증 후보"))
                  continue
              if st.button(
                  str(option.get("title") or option_id or "후보"),
                  key=f"pv2-fallback-source-{option_id}",
                  width="stretch",
                  disabled=not bool(option.get("eligible", True)),
              ):
                  return _workspace_intent(
                      "select_source",
                      workspace=workspace,
                      selection_source_id=option_id,
                  )
      else:
          st.info("Backtest Analysis에서 검증할 후보를 먼저 보내세요.")
  ```

  Keep the existing 1B option order and intent behavior below the expander.

- [x] **Step 4: Run fallback and full focused GREEN tests**

  Run:

  ```bash
  .venv/bin/python -m unittest \
    tests.test_backtest_practical_validation_decision_workspace \
    tests.test_backtest_refactor_boundaries \
    tests.test_practical_validation_market_context_visual_contract
  ```

  Expected: all focused tests pass.

- [x] **Step 5: Run target py_compile and commit fallback parity**

  Run:

  ```bash
  .venv/bin/python -m py_compile app/web/backtest_practical_validation/workspace_panel.py
  git diff --check
  ```

  Stage only the fallback source and boundary test, then commit:

  ```bash
  git commit -m "Practical Validation Step1 fallback 선택 흐름 정렬"
  ```

### Task 21: Runtime QA, Documentation, And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Documents the approved Step 1 compact selection IA without changing runtime contracts.
- QA uses current worktree Streamlit and generated screenshots only; screenshots remain unstaged.

- [x] **Step 1: Restart only this worktree's stale Streamlit process and open Practical Validation**

  Use the existing worktree run command and select
  `GTAA U3/U5 + GRS Compact Monitoring Candidate 20260608`. Do not write the Practical
  Validation registry during QA.

- [x] **Step 2: Execute desktop Browser QA**

  Confirm all of the following on the current build:

  - hero contains the fixed Level2 question and no candidate-specific aside;
  - Step 1 summary contains the selected candidate and profile;
  - candidate list is closed initially, opens inline from `후보 변경`, and selected/ineligible
    meaning is visible;
  - choosing another eligible candidate updates only Step 1 selection context after the
    expected app rerun;
  - 1B shows five equal-width buttons in one row;
  - opening/closing the list updates iframe height without clipping or page horizontal overflow.

- [x] **Step 3: Execute 760px Browser QA**

  Confirm candidate summary/control is one column, 1B is two columns, `사용자 지정` spans
  both columns, candidate list vertical scroll is usable, and component/outer widths have no
  overflow. Capture desktop and 760px screenshots outside tracked paths.

- [x] **Step 4: Run fresh completion verification**

  Run:

  ```bash
  .venv/bin/python -m unittest \
    tests.test_backtest_evidence_closure \
    tests.test_backtest_final_review_decision_brief \
    tests.test_backtest_practical_validation_decision_workspace \
    tests.test_backtest_practical_validation_explanation \
    tests.test_backtest_refactor_boundaries \
    tests.test_final_review_market_context_visual_contract \
    tests.test_practical_validation_level2_hardening \
    tests.test_practical_validation_market_context_visual_contract
  npm --prefix app/web/components/practical_validation_decision_workspace/frontend run build
  .venv/bin/python -m py_compile \
    app/web/backtest_practical_validation/page.py \
    app/web/backtest_practical_validation/workspace_panel.py \
    app/web/components/practical_validation_decision_workspace/component.py
  git diff --check
  ```

  Expected: all Python tests, React production build, py_compile, and diff-check pass freshly.

- [x] **Step 5: Synchronize durable documentation and active task evidence**

  Record the compact Step 1 ownership in the four canonical docs, RED/GREEN commands and QA
  screenshot paths in active task `RUNS.md`, completed status in `STATUS.md`, future Streamlit
  responsive/lifecycle risk in `RISKS.md`, and 3~5-line milestone entries in both root handoff
  logs. Do not copy transient command output into canonical docs.

- [x] **Step 6: Audit protected paths and create the closeout commit**

  Confirm staged files exclude registries, run history, saved JSONL, screenshots,
  `.superpowers/`, and run artifacts. Commit only docs/task/root logs:

  ```bash
  git commit -m "Practical Validation Step1 선택 UX QA와 문서 동기화"
  ```
