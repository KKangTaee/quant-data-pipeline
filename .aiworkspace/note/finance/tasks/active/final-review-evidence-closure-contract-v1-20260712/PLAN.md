# Final Review Evidence Closure Contract V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task in the current `codex/backtest-dev` worktree. Every behavior change follows `superpowers:test-driven-development`; completion claims follow `superpowers:verification-before-completion`.

**Goal:** Practical Validation에서 해결 가능한 근거를 닫고, 해결 불가능한 핵심 근거를 차단하며, Final Review에 전달된 비핵심 한계와 판단 조건을 terminal state로 종결해 current eligible 후보의 미정 상태를 0개로 만든다.

**Architecture:** 새 Streamlit-free `app/services/backtest_evidence_closure.py`가 저장 validation의 module/audit/provenance를 root issue 단위로 정규화하고 actionability, Gate, terminal state, root-level score impact를 소유한다. Practical Validation module/workspace와 Final Review helper/read model은 이 단방향 contract를 소비하며, React는 Python payload를 표시하고 intent만 반환한다. GRS runtime은 signal/rebalance row와 valuation-only row를 분리하고 replay service는 전체 DB max가 아닌 source ticker 기준 날짜 계약을 저장한다.

**Tech Stack:** Python 3.12, pandas, `unittest`, Streamlit, React 18 + TypeScript + Vite, append-only JSONL runtime helpers.

## 이걸 하는 이유?

현재 `latest_replay`는 실제 stored provenance가 있어도 Final Review trace adapter가 없어 `missing_contract`가 되며, 같은 period gap이 Data Coverage의 `PIT price window coverage`에서 다시 반영된다. GRS는 BIL `2026-06-26`과 위험자산 `2026-06-30`의 ticker별 월말 날짜를 exact intersection해 2026-06 row를 잃고 `2026-05-29`에서 끝난다. 이 task는 copy 보강이 아니라 해결 가능성·중요도·소유 단계·실제 handler·종결 상태를 하나의 Python contract로 연결해 workflow를 끝낼 수 있게 한다.

## Global Constraints

- 기존 active task `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/`만 사용하고 새 task/worktree를 만들지 않는다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`, `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, saved JSONL, 기존 registry row는 rewrite/delete/stage/commit하지 않는다.
- historical universe/delisting 신규 provider와 DB schema는 추가하지 않는다. 근거 없는 dynamic universe는 `engineering_required + critical`로 defer/block한다.
- Final Review는 provider fetch, replay, DB ingestion, live approval, broker order, account sync, auto rebalance를 실행하지 않는다.
- React는 presentation과 intent만 소유하고 classification, Gate, replay, score, save, append는 Python이 소유한다.
- 하나의 `root_issue_id`는 card, closure, score에서 한 번만 반영하고 derived checks는 기술 근거로 보존한다.
- current Final Review eligible 후보의 `unresolved_actionable_count`와 `critical_engineering_count`는 모두 0이어야 한다.
- `missing_contract`는 숫자 감점이나 current Final Review 사용자 문구가 아니라 required contract Gate blocker다.
- 각 distinct implementation unit은 RED → GREEN → focused regression → `git diff --check`를 확인한 뒤 한국어 commit으로 닫는다.

## File Structure And Interfaces

### New file

- `app/services/backtest_evidence_closure.py`
  - validation module/audit/provenance → root issue normalization
  - `resolution_class`, `actionable_now`, handler contract, `terminal_state`
  - root dedup, Final Review eligibility summary, measured-only score impact
  - decision route별 accepted/monitoring/deferred/blocked closure snapshot

### Existing Python owners

- `app/services/backtest_data_coverage_audit.py`: static manual vs dynamic historical universe applicability와 lifecycle audit evidence 제공
- `app/services/backtest_practical_validation_replay.py`: requested/common/rebalance/valuation date contract와 replay period evidence 제공
- `app/services/backtest_practical_validation_modules.py`: closure blocker를 Final Review Gate에 병합
- `app/services/backtest_practical_validation_workspace.py`: `지금 해결 가능 / 개발 필요 / 한계 인수 가능` screen read model
- `app/services/backtest_evidence_read_model.py`: closure contract를 소비해 Final Review section과 root-level score impact 조립
- `app/web/backtest_final_review_helpers.py`: eligibility, save evaluation, decision row closure snapshot 저장
- `app/web/backtest_practical_validation/page.py`: Python-owned replay action handler와 closure group 렌더
- `app/web/backtest_final_review/page.py`: Python report/decision intent orchestration
- `finance/transform.py`, `finance/sample.py`, `finance/strategy.py`, `app/runtime/backtest/runners/global_relative_strength.py`: GRS valuation-only runtime contract

### Existing React owner

- `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`: `선정 전 미해결 항목`과 `인수한 한계와 최종 판단 항목` 표시, existing decision intent 유지

### Test ownership

- Create `tests/test_backtest_evidence_closure.py`: pure closure service RED/GREEN contract
- Modify `tests/test_service_contracts.py`: Practical Validation Gate/workspace, Final Review eligibility/save/read model/React source contract
- Modify `tests/test_global_relative_strength_strategy.py`: GRS signal/rebalance/valuation regression
- Modify `tests/test_gtaa_strategy.py` only if shared transform semantics change; GTAA existing latest-common behavior must stay green

---

## 1차: Evidence Truth / Root Dedup

### Task 1.1: Root issue pure service와 latest replay provenance adapter

**Files:**
- Create: `app/services/backtest_evidence_closure.py`
- Create: `tests/test_backtest_evidence_closure.py`

**Interfaces:**
- Produces: `build_evidence_closure_contract(validation: dict[str, Any]) -> dict[str, Any]`
- Produces: `build_latest_replay_evidence(validation: dict[str, Any]) -> dict[str, Any]`
- Produces schema:

```python
{
    "schema_version": "backtest_evidence_closure_v1",
    "issues": [{
        "root_issue_id": "replay_period_coverage",
        "title": "최신 재검증 기간 충족 여부",
        "observed": "요청 2026-07-10 / 실제 2026-05-29 / 42일 gap",
        "expected": "latest_common_price_date까지 valuation evidence 확보",
        "cause": "stored runtime period coverage",
        "derived_checks": ["latest_replay", "pit_price_window_coverage"],
        "resolution_class": "resolve_now",
        "owner_stage": "practical_validation",
        "actionable_now": True,
        "action_id": "run_practical_validation_replay",
        "completion_criteria": "period coverage가 PASS이거나 partial-month monitoring_transfer로 분류됨",
        "applicability": "required",
        "criticality": "critical",
        "gate_effect": "block_final_review",
        "terminal_state": "open",
    }],
    "summary": {
        "unresolved_actionable_count": 1,
        "critical_engineering_count": 0,
        "missing_contract_count": 0,
    },
    "current_final_review_eligible": False,
}
```

- [ ] **Step 1: Write failing pure-service tests**

```python
class EvidenceClosureContractTests(unittest.TestCase):
    def test_latest_replay_adapter_uses_stored_requested_actual_and_gap(self) -> None:
        contract = build_evidence_closure_contract(_grs_validation_fixture())
        issue = _issue(contract, "replay_period_coverage")
        self.assertEqual(issue["derived_checks"], ["latest_replay", "pit_price_window_coverage"])
        self.assertEqual(issue["period"]["requested_market_date"], "2026-07-10")
        self.assertEqual(issue["period"]["actual_result_date"], "2026-05-29")
        self.assertEqual(issue["period"]["end_gap_days"], 42)

    def test_replay_and_pit_rows_become_one_root_issue(self) -> None:
        contract = build_evidence_closure_contract(_grs_validation_fixture())
        self.assertEqual(
            [row["root_issue_id"] for row in contract["issues"]].count("replay_period_coverage"),
            1,
        )
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure.EvidenceClosureContractTests`

Expected: `ModuleNotFoundError: No module named 'app.services.backtest_evidence_closure'`.

- [ ] **Step 3: Implement minimal normalization and root merge**

```python
def build_latest_replay_evidence(validation: dict[str, Any]) -> dict[str, Any]:
    curve = dict(validation.get("curve_evidence") or {})
    provenance = dict(curve.get("curve_provenance") or {})
    period = dict(curve.get("period_coverage") or provenance.get("period_coverage") or {})
    return {
        "requested_market_date": _date_text(dict(period.get("requested_period") or {}).get("end")),
        "latest_common_price_date": _date_text(period.get("latest_common_price_date")),
        "last_complete_rebalance_date": _date_text(period.get("last_complete_rebalance_date")),
        "latest_valuation_date": _date_text(period.get("latest_valuation_date")),
        "actual_result_date": _date_text(dict(period.get("actual_period") or {}).get("end")),
        "end_gap_days": _optional_int(period.get("end_gap_days")),
    }


def build_evidence_closure_contract(validation: dict[str, Any]) -> dict[str, Any]:
    issues = _merge_root_issues(_build_issue_candidates(dict(validation or {})))
    summary = _closure_summary(issues)
    return {
        "schema_version": EVIDENCE_CLOSURE_SCHEMA_VERSION,
        "issues": issues,
        "summary": summary,
        "current_final_review_eligible": not summary["unresolved_actionable_count"]
        and not summary["critical_engineering_count"]
        and not summary["missing_contract_count"],
    }
```

- [ ] **Step 4: Run GREEN and regression**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure.EvidenceClosureContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`

Expected: all selected tests pass.

### Task 1.2: Historical universe root dedup과 missing-contract Gate truth

**Files:**
- Modify: `app/services/backtest_evidence_closure.py`
- Modify: `app/services/backtest_evidence_read_model.py`
- Modify: `app/services/backtest_practical_validation_modules.py`
- Modify: `tests/test_backtest_evidence_closure.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- `historical_universe_coverage` merges `universe_listing_evidence` and `survivorship_delisting_control`.
- `build_final_review_level2_review_disposition()` consumes `validation["evidence_closure"]` or builds it and never emits user-facing `missing_contract`.
- required module without an adapter becomes `engineering_required + critical + deferred` and is inserted into `final_review_gate.blocking_modules`.

- [ ] **Step 1: Write RED tests**

```python
def test_listing_and_survivorship_rows_become_one_root_issue(self) -> None:
    contract = build_evidence_closure_contract(_validation_with_lifecycle_review())
    issue = _issue(contract, "historical_universe_coverage")
    self.assertEqual(
        issue["derived_checks"],
        ["universe_listing_evidence", "survivorship_delisting_control"],
    )

def test_required_missing_adapter_blocks_without_user_missing_contract_copy(self) -> None:
    disposition = build_final_review_level2_review_disposition(validation=_required_unknown_module())
    self.assertNotIn("세부 설명 준비 안 됨", json.dumps(disposition, ensure_ascii=False))
    self.assertEqual(disposition["closure_summary"]["missing_contract_count"], 1)
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`

Expected: missing root merge/closure fields assertions fail.

- [ ] **Step 3: Implement closure consumption and Gate blocker merge**

```python
closure = build_evidence_closure_contract(validation)
validation["evidence_closure"] = closure
for issue in closure["issues"]:
    if issue["gate_effect"] == "block_final_review" and issue["terminal_state"] in {"open", "deferred"}:
        blocking_modules.append(_closure_blocker_row(issue))
```

- [ ] **Step 4: Run GREEN, full 1차 focused regression, diff check**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.DataCoverageAuditContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`

Run: `git diff --check`

Expected: all tests pass; no whitespace errors.

- [ ] **Step 5: Commit 1차**

```bash
git add app/services/backtest_evidence_closure.py app/services/backtest_evidence_read_model.py app/services/backtest_practical_validation_modules.py tests/test_backtest_evidence_closure.py tests/test_service_contracts.py
git commit -m "Final Review 근거 root issue 계약 도입"
```

Do not stage registry, run history, screenshots, or unrelated files.

---

## 2차: Level2 Actionability / Gate

### Task 2.1: resolution class, handler registry, terminal-state Gate

**Files:**
- Modify: `app/services/backtest_evidence_closure.py`
- Modify: `app/services/backtest_practical_validation_modules.py`
- Modify: `app/services/backtest_practical_validation_workspace.py`
- Modify: `app/web/backtest_final_review_helpers.py`
- Modify: `tests/test_backtest_evidence_closure.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Resolution values: `resolve_now`, `engineering_required`, `accepted_limit`, `final_decision`, `monitoring_transfer`.
- Terminal values: `open`, `resolved`, `accepted`, `monitoring_transferred`, `deferred`, `blocked`.
- Actual action registry:

```python
ACTION_HANDLER_CONTRACTS = {
    "run_practical_validation_replay": {
        "owner_stage": "practical_validation",
        "handler": "app.web.backtest_practical_validation.page:_render_actual_replay_panel",
    },
}
```

- Workspace adds `evidence_closure_groups` with exact labels `지금 해결 가능`, `개발 필요`, `한계 인수 가능`.
- Eligibility adds closure gate after existing pre-final enrichment and selected-route preflight.

- [ ] **Step 1: Write RED tests for actionability and eligibility**

```python
def test_resolve_now_without_registered_handler_has_no_cta_and_blocks(self) -> None:
    issue = normalize_evidence_issue({
        "root_issue_id": "unknown_action",
        "resolution_class": "resolve_now",
        "action_id": "missing_handler",
    })
    self.assertFalse(issue["actionable_now"])
    self.assertEqual(issue["resolution_class"], "engineering_required")
    self.assertEqual(issue["gate_effect"], "block_final_review")

def test_current_final_review_eligibility_requires_zero_unresolved_actionable(self) -> None:
    row = _eligible_validation_with_closure(unresolved_actionable_count=1)
    self.assertFalse(_is_final_review_eligible_validation_result(row))

def test_workspace_separates_now_engineering_and_accepted_limit(self) -> None:
    workspace = build_practical_validation_workspace(_closure_validation_fixture())
    self.assertEqual(
        [group["label"] for group in workspace["evidence_closure_groups"]],
        ["지금 해결 가능", "개발 필요", "한계 인수 가능"],
    )
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests`

Expected: missing action registry/workspace/eligibility fields fail.

- [ ] **Step 3: Implement minimal classification and Gate merge**

```python
def has_action_handler(action_id: Any) -> bool:
    return str(action_id or "") in ACTION_HANDLER_CONTRACTS


def is_current_final_review_eligible(contract: dict[str, Any]) -> bool:
    summary = dict(contract.get("summary") or {})
    return (
        int(summary.get("unresolved_actionable_count") or 0) == 0
        and int(summary.get("critical_engineering_count") or 0) == 0
        and int(summary.get("missing_contract_count") or 0) == 0
    )
```

- [ ] **Step 4: Run GREEN and focused regression**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`

Expected: all selected tests pass.

### Task 2.2: Level2 actionability UX와 Python replay handler 유지

**Files:**
- Modify: `app/services/backtest_practical_validation_workspace.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Closure card fields: `actionable_now`, `action_id`, `action_label`, `completion_criteria`, `terminal_state_label`.
- Only `action_id == "run_practical_validation_replay"` renders the existing Python-owned replay action.
- `engineering_required` renders `개발 후 재검토` without a collection/replay CTA.
- `accepted_limit` renders why Level2 may pass and what Final Review must close.
- Existing `_has_current_session_replay_result()` and save-and-move guard remain unchanged.

- [ ] **Step 1: Write RED source/workspace tests**

```python
def test_level2_closure_cards_only_render_registered_python_action(self) -> None:
    page_source = Path("app/web/backtest_practical_validation/page.py").read_text()
    self.assertIn('action_id == "run_practical_validation_replay"', page_source)
    self.assertNotIn('action_id == "missing_handler"', page_source)

def test_engineering_required_card_has_no_provider_collection_cta(self) -> None:
    workspace = build_practical_validation_workspace(_dynamic_universe_fixture())
    card = _closure_card(workspace, "historical_universe_coverage")
    self.assertFalse(card["actionable_now"])
    self.assertEqual(card["action_label"], "개발 후 재검토")
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests tests.test_service_contracts.PracticalValidationServiceContractTests`

Expected: missing render contract assertions fail.

- [ ] **Step 3: Implement Python-owned render/intent path**

```python
def _render_evidence_closure_groups(validation_result: dict[str, Any]) -> None:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    for group in list(workspace.get("evidence_closure_groups") or []):
        for item in list(group.get("items") or []):
            _render_evidence_closure_item(item)
            if item.get("action_id") == "run_practical_validation_replay" and item.get("actionable_now"):
                st.caption("Flow 2의 전략 재검증 실행으로 이 항목을 닫습니다.")
```

- [ ] **Step 4: Run GREEN, py_compile, Browser QA**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests`

Run: `.venv/bin/python -m py_compile app/services/backtest_evidence_closure.py app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_final_review_helpers.py`

Browser QA:

1. Final Review recovery에서 같은 후보 Practical Validation로 이동한다.
2. current-session replay가 없을 때 save-and-move가 비활성/거부되는지 확인한다.
3. Flow 4에서 `지금 해결 가능 / 개발 필요 / 한계 인수 가능`이 분리되는지 확인한다.
4. handler 없는 개발 필요 항목에 CTA가 없는지 확인한다.
5. 760px viewport에서 가로 overflow가 없는지 확인하고 screenshot은 generated artifact로만 남긴다.

- [ ] **Step 5: Commit 2차**

```bash
git add app/services/backtest_evidence_closure.py app/services/backtest_practical_validation_modules.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_final_review_helpers.py tests/test_backtest_evidence_closure.py tests/test_service_contracts.py
git commit -m "Practical Validation 근거 종결 Gate 강화"
```

---

## 3차: GRS Period / Survivorship Applicability

### Task 3.1: Source-specific replay date contract

**Files:**
- Modify: `app/services/backtest_practical_validation_replay.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Produces: `build_replay_market_date_contract(source: dict[str, Any], *, requested_end: Any | None = None) -> dict[str, Any]`
- Reads `finance.loaders.price.load_price_freshness_summary` for the active component tickers plus cash ticker.
- Date fields:

```python
{
    "requested_market_date": "2026-07-10",
    "latest_common_price_date": "2026-06-26",
    "last_complete_rebalance_date": "2026-06-30",
    "latest_valuation_date": "2026-06-26",
    "limiting_symbols": ["BIL"],
}
```

- `build_practical_validation_recheck_plan()` stores this contract and chooses the strategy-specific requested end instead of the whole DB max.

- [ ] **Step 1: Write RED replay date tests**

```python
def test_recheck_plan_uses_component_common_date_not_whole_db_max(self) -> None:
    with patch.object(replay_service, "load_latest_market_date", return_value="2026-07-10"), patch.object(
        replay_service,
        "load_price_freshness_summary",
        return_value=pd.DataFrame([
            {"symbol": "SPY", "latest_date": "2026-06-30", "row_count": 100},
            {"symbol": "BIL", "latest_date": "2026-06-26", "row_count": 100},
        ]),
    ):
        plan = replay_service.build_practical_validation_recheck_plan(_grs_source())
    self.assertEqual(plan["market_date_contract"]["latest_common_price_date"], "2026-06-26")
    self.assertEqual(plan["requested_period"]["end"], "2026-06-26")
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationReplayServiceContractTests`

Expected: missing market-date contract assertions fail.

- [ ] **Step 3: Implement source ticker date adapter and recheck plan wiring**

```python
def build_replay_market_date_contract(source: dict[str, Any], *, requested_end: Any | None = None) -> dict[str, Any]:
    symbols = _replay_component_symbols(source)
    freshness = load_price_freshness_summary(symbols=symbols, end=requested_end, timeframe="1d")
    latest_common = _date_text(freshness["latest_date"].min()) if not freshness.empty else None
    return {
        "requested_market_date": _date_text(requested_end),
        "latest_common_price_date": latest_common,
        "last_complete_rebalance_date": _last_complete_month_end(requested_end),
        "latest_valuation_date": latest_common,
        "limiting_symbols": _limiting_symbols(freshness),
    }
```

- [ ] **Step 4: Run GREEN**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationReplayServiceContractTests`

Expected: all replay service tests pass.

### Task 3.2: GRS exact month-end loss 보정과 valuation-only row

**Files:**
- Modify: `finance/transform.py`
- Modify: `finance/sample.py`
- Modify: `finance/strategy.py`
- Modify: `app/runtime/backtest/runners/global_relative_strength.py`
- Modify: `tests/test_global_relative_strength_strategy.py`
- Verify: `tests/test_gtaa_strategy.py`

**Interfaces:**
- Extend `append_latest_common_row(..., row_kind_col: str | None = None)` so appended rows can carry `Row Kind="valuation"`; existing period rows carry `Row Kind="signal"` only when requested.
- `global_relative_strength_allocation()` reads `Row Kind`; `valuation` rows update holdings value and returns but force `Rebalancing=False` and do not rank/select new holdings.
- Runtime bundle exposes `meta["grs_period_contract"]` with the four dates and valuation-row count.

- [ ] **Step 1: Write RED GRS regression tests**

```python
def test_grs_adds_latest_common_valuation_without_fake_rebalance(self) -> None:
    result = sample.get_global_relative_strength_from_db(...fixture with SPY 2026-06-30 and BIL 2026-06-26...)
    last = result.iloc[-1]
    self.assertEqual(pd.Timestamp(last["Date"]), pd.Timestamp("2026-06-26"))
    self.assertEqual(last["Row Kind"], "valuation")
    self.assertFalse(last["Rebalancing"])

def test_grs_valuation_row_keeps_prior_holdings_and_has_no_new_raw_selection(self) -> None:
    result = global_relative_strength_allocation(_signal_and_valuation_dfs(), ...)
    self.assertEqual(result.iloc[-1]["Next Ticker"], result.iloc[-2]["Next Ticker"])
    self.assertEqual(result.iloc[-1]["Raw Selected Ticker"], [])
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_global_relative_strength_strategy.GlobalRelativeStrengthRuntimeContractTests`

Expected: latest common valuation row/row kind assertions fail.

- [ ] **Step 3: Implement valuation-only transform and strategy semantics**

```python
row_kind = str(base_row.get("Row Kind") or "signal")
valuation_only = row_kind == "valuation"
rebalancing = False if valuation_only else ((signal_index == 0) or (signal_index % rebalance_interval == 0))
if not valuation_only:
    signal_index += 1
```

- [ ] **Step 4: Run GREEN and GTAA regression**

Run: `.venv/bin/python -m unittest tests.test_global_relative_strength_strategy tests.test_gtaa_strategy tests.test_etf_runtime_strategy_contracts`

Expected: all strategy/runtime tests pass; GTAA latest-common behavior remains intact.

### Task 3.3: Static manual vs dynamic historical survivorship policy

**Files:**
- Modify: `app/services/backtest_data_coverage_audit.py`
- Modify: `app/services/backtest_evidence_closure.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `tests/test_backtest_evidence_closure.py`

**Interfaces:**
- Data Coverage exposes `universe_contract`:

```python
{
    "mode": "static_manual" | "dynamic_historical",
    "requires_pit_membership": bool,
    "survivorship_applicability": "accepted_limit_allowed" | "critical_required",
}
```

- Static manual missing historical delisting evidence → `REVIEW`, closure `accepted_limit`, noncritical, no fixed score.
- Dynamic historical missing PIT membership/delisting → `NEEDS_INPUT`, closure `engineering_required`, critical, Final Review blocker.

- [ ] **Step 1: Write RED applicability tests**

```python
def test_static_manual_survivorship_gap_is_accepted_limit_candidate(self) -> None:
    contract = build_evidence_closure_contract(_manual_universe_review())
    issue = _issue(contract, "historical_universe_coverage")
    self.assertEqual(issue["resolution_class"], "accepted_limit")
    self.assertEqual(issue["criticality"], "noncritical")

def test_dynamic_universe_missing_pit_membership_is_critical_engineering_blocker(self) -> None:
    contract = build_evidence_closure_contract(_dynamic_universe_review())
    issue = _issue(contract, "historical_universe_coverage")
    self.assertEqual(issue["resolution_class"], "engineering_required")
    self.assertEqual(issue["criticality"], "critical")
    self.assertFalse(contract["current_final_review_eligible"])
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.DataCoverageAuditContractTests tests.test_backtest_evidence_closure.EvidenceClosureContractTests`

Expected: static/dynamic policy assertions fail.

- [ ] **Step 3: Implement applicability and closure mapping**

```python
if universe_mode in {"pit_monthly_snapshot", "historical_dynamic_pit", "dynamic_historical"}:
    contract = {"mode": "dynamic_historical", "requires_pit_membership": True}
else:
    contract = {"mode": "static_manual", "requires_pit_membership": False}
```

- [ ] **Step 4: Run GREEN, full 3차 regression, diff check**

Run: `.venv/bin/python -m unittest tests.test_global_relative_strength_strategy tests.test_gtaa_strategy tests.test_etf_runtime_strategy_contracts tests.test_service_contracts.PracticalValidationReplayServiceContractTests tests.test_service_contracts.DataCoverageAuditContractTests tests.test_backtest_evidence_closure`

Run: `git diff --check`

Expected: all selected tests pass; no whitespace errors.

- [ ] **Step 5: Commit 3차**

```bash
git add finance/transform.py finance/sample.py finance/strategy.py app/runtime/backtest/runners/global_relative_strength.py app/services/backtest_practical_validation_replay.py app/services/backtest_data_coverage_audit.py app/services/backtest_evidence_closure.py tests/test_global_relative_strength_strategy.py tests/test_service_contracts.py tests/test_backtest_evidence_closure.py
git commit -m "GRS 기간·생존편향 적용 계약 보정"
```

---

## 4차: Final Review Closure / Score / QA / Docs

### Task 4.1: Decision route별 terminal-state snapshot과 save guard

**Files:**
- Modify: `app/services/backtest_evidence_closure.py`
- Modify: `app/web/backtest_final_review_helpers.py`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `tests/test_backtest_evidence_closure.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Produces: `finalize_evidence_closure(contract: dict[str, Any], *, decision_route: str, operator_reason: str) -> dict[str, Any]`
- Selected route: `accepted_limit -> accepted`, `monitoring_transfer -> monitoring_transferred`, `final_decision -> accepted`.
- Hold/re-review: relevant items → `deferred`.
- Reject: all unresolved final items → `blocked`.
- Output includes `terminal_state_counts`, `accepted_limit_summary`, `monitoring_conditions`, `decision_reason_summary`, `open_count`.
- `_build_final_review_decision_row()` stores `evidence_closure_snapshot`; no new registry is created.

- [ ] **Step 1: Write RED save/finalization tests**

```python
def test_selected_decision_finalizes_limits_and_monitoring_for_same_validation(self) -> None:
    snapshot = finalize_evidence_closure(
        _closable_contract(validation_id="validation-1"),
        decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
        operator_reason="한계를 확인하고 추적 조건을 수용함",
    )
    self.assertEqual(snapshot["validation_id"], "validation-1")
    self.assertEqual(snapshot["terminal_state_counts"]["accepted"], 1)
    self.assertEqual(snapshot["terminal_state_counts"]["monitoring_transferred"], 1)
    self.assertEqual(snapshot["open_count"], 0)

def test_decision_row_stores_closure_snapshot_without_new_persistence(self) -> None:
    row = _build_final_review_decision_row(...)
    self.assertEqual(row["evidence_closure_snapshot"]["open_count"], 0)
    self.assertFalse(row["live_approval"])
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`

Expected: finalize/snapshot assertions fail.

- [ ] **Step 3: Implement finalization and save evaluation**

```python
closure_snapshot = finalize_evidence_closure(
    build_evidence_closure_contract(validation),
    decision_route=decision_route_clean,
    operator_reason=operator_reason,
)
checks.append({
    "Criteria": "Evidence closure",
    "Ready": closure_snapshot["open_count"] == 0,
    "Current": f"open={closure_snapshot['open_count']}",
    "Meaning": "모든 Final Review issue가 terminal state로 종결되어야 합니다.",
})
```

- [ ] **Step 4: Run GREEN**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`

Expected: all selected tests pass.

### Task 4.2: Root-level measured-only score와 Final Review read model

**Files:**
- Modify: `app/services/backtest_evidence_closure.py`
- Modify: `app/services/backtest_evidence_read_model.py`
- Modify: `tests/test_backtest_evidence_closure.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- `score_impact` exists only when an issue has explicit numeric `measurement = {observed, threshold, comparison, target_dimension}`.
- `missing_contract`, `resolve_now + open`, `engineering_required + critical` create Gate effects, not numeric deductions.
- `accepted_limit` without measurement shows confidence impact label but `score_effect=0`.
- `build_final_review_investment_report()` exposes:
  - `pre_selection_unresolved_items`
  - `accepted_limits_and_decisions`
  - `evidence_closure_summary`
- current eligible report always has empty `pre_selection_unresolved_items`.

- [ ] **Step 1: Write RED score/read-model tests**

```python
def test_score_impact_is_measured_and_root_deduplicated(self) -> None:
    report = build_final_review_investment_report(...validation with duplicate replay/PIT root...)
    impacts = report["scorecard"]["review_impacts"]
    self.assertEqual([row["root_issue_id"] for row in impacts].count("replay_period_coverage"), 1)
    self.assertTrue(all(row["measurement"] for row in impacts if row["score_effect"] != 0))

def test_missing_contract_and_open_actionable_are_gate_not_score(self) -> None:
    scorecard = build_final_review_scorecard(...)
    self.assertEqual(scorecard["review_impacts"], [])
    self.assertIn("evidence_closure_blocker", [row["code"] for row in scorecard["route_constraints"]])

def test_current_eligible_report_has_zero_pre_selection_unresolved_items(self) -> None:
    report = build_final_review_investment_report(...)
    self.assertEqual(report["pre_selection_unresolved_items"], [])
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`

Expected: old fixed `-6/-4` and duplicate impact assertions fail.

- [ ] **Step 3: Replace role-fixed deduction with closure issue impacts**

```python
review_impacts = [
    _closure_score_impact(issue)
    for issue in closure["issues"]
    if dict(issue.get("measurement") or {}).get("observed") is not None
    and dict(issue.get("measurement") or {}).get("threshold") is not None
]
```

Remove fixed role deduction mapping from `_review_impact_for_item`; keep display compatibility fields sourced from the root issue.

- [ ] **Step 4: Run GREEN**

Run: `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests`

Expected: all selected tests pass.

### Task 4.3: Final Review React presentation and intent-only contract

**Files:**
- Modify: `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- React types add `EvidenceClosureIssue`, `EvidenceClosureSummary` and read Python-provided arrays.
- Presentation order:
  1. existing summary and four interpretations
  2. existing final decision route/reason CTA
  3. `선정 전 미해결 항목` only when legacy/stale recovery has rows; current eligible shows count 0 compact state
  4. `인수한 한계와 최종 판단 항목`
  5. derived checks/source/as-of in disclosure
- React must not contain resolution-class inference, Gate math, score calculation, save evaluation, provider/replay calls, or JSONL append.

- [ ] **Step 1: Write RED React source contract**

```python
def test_final_review_react_renders_python_closure_sections_without_domain_recalculation(self) -> None:
    source = Path(".../FinalReviewInvestmentReport.tsx").read_text()
    self.assertIn("선정 전 미해결 항목", source)
    self.assertIn("인수한 한계와 최종 판단 항목", source)
    self.assertNotIn("resolutionClass ===", source)
    self.assertNotIn("fetch(", source)
    self.assertNotIn("scoreEffect =", source)
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests`

Expected: new section source assertions fail.

- [ ] **Step 3: Implement typed presentation components**

```tsx
function EvidenceClosureSections({ report }: { report: InvestmentReport }) {
  const unresolved = field(report.preSelectionUnresolvedItems, report.pre_selection_unresolved_items) ?? []
  const closable = field(report.acceptedLimitsAndDecisions, report.accepted_limits_and_decisions) ?? []
  return (
    <section className="fr-closure-shell">
      <EvidenceRows title="선정 전 미해결 항목" items={unresolved} emptyLabel="현재 후보 0개" limit={6} />
      <EvidenceRows title="인수한 한계와 최종 판단 항목" items={closable} emptyLabel="종결할 항목 없음" limit={8} />
    </section>
  )
}
```

- [ ] **Step 4: Run GREEN and production build**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests`

Run: `npm run build --prefix app/web/components/final_review_investment_report/frontend`

Expected: tests pass; Vite production build exits 0.

### Task 4.4: Fresh verification, Browser QA, docs/task sync, closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

- [ ] **Step 1: Run fresh focused and runtime regressions**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_evidence_closure \
  tests.test_global_relative_strength_strategy \
  tests.test_gtaa_strategy \
  tests.test_etf_runtime_strategy_contracts \
  tests.test_service_contracts.PracticalValidationServiceContractTests \
  tests.test_service_contracts.DataCoverageAuditContractTests \
  tests.test_service_contracts.PracticalValidationReplayServiceContractTests \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests
```

Expected: 0 failures / 0 errors. Record exact test count in `RUNS.md` and final response.

- [ ] **Step 2: Run target compile and React build**

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/backtest_evidence_closure.py \
  app/services/backtest_data_coverage_audit.py \
  app/services/backtest_practical_validation_replay.py \
  app/services/backtest_practical_validation_modules.py \
  app/services/backtest_practical_validation_workspace.py \
  app/services/backtest_evidence_read_model.py \
  app/web/backtest_practical_validation/page.py \
  app/web/backtest_final_review_helpers.py \
  app/web/backtest_final_review/page.py \
  app/runtime/backtest/runners/global_relative_strength.py \
  finance/transform.py finance/sample.py finance/strategy.py
npm run build --prefix app/web/components/final_review_investment_report/frontend
git diff --check
```

Expected: every command exits 0.

- [ ] **Step 3: Browser QA**

Check current GRS candidate and one legacy/stale path:

1. Practical Validation Flow 2 current-session replay guard.
2. Flow 4 `지금 해결 가능 / 개발 필요 / 한계 인수 가능` separation.
3. Final Review current eligible candidate has `선정 전 미해결 항목 0` and no `세부 설명 준비 안 됨`.
4. Accepted limit and Monitoring transfer summary appear next to existing decision route/reason without extra checkbox explosion.
5. Candidate selector stale guard still hides previous report.
6. 760px compact viewport has no document or closure-card horizontal overflow.
7. Capture one QA screenshot; do not stage/commit it.

- [ ] **Step 4: Synchronize durable docs and active task records**

Record:

- `app/services/backtest_evidence_closure.py` ownership
- Practical Validation completion criterion changes from review-count handling to unresolved-actionable/critical-engineering zero
- Final Review terminal-state closure and measured-only root score semantics
- GRS requested/common/rebalance/valuation date split and valuation-only row
- static manual vs dynamic historical survivorship applicability
- exact RED/GREEN/QA commands and residual risks

- [ ] **Step 5: Verify staging excludes user/generated artifacts**

Run:

```bash
git status --short
git diff --name-only --cached
```

Expected: registry, run history, saved JSONL, screenshots, run artifacts are absent from the staged list.

- [ ] **Step 6: Commit 4차 implementation and closeout docs as distinct units**

```bash
git add app/services/backtest_evidence_closure.py app/services/backtest_evidence_read_model.py app/web/backtest_final_review_helpers.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx app/web/components/final_review_investment_report/frontend/src/style.css tests/test_backtest_evidence_closure.py tests/test_service_contracts.py
git commit -m "Final Review 근거 종결과 점수 흐름 통합"
```

Then:

```bash
git add .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "Final Review 근거 종결 QA와 문서 동기화"
```

Do not use broad `git add .`.

## Stop Conditions

Stop and report before continuing only if one of these occurs:

- implementation requires a new historical-universe/delisting provider, DB schema, or separate workflow-state registry;
- GRS valuation-only correction cannot preserve existing GTAA and GRS strategy semantics without a broader core-engine redesign;
- current registry rows must be rewritten/deleted to satisfy the contract;
- DESIGN.md invariants conflict with a verified runtime fact;
- the same implementation hypothesis fails three times and systematic debugging indicates an architectural mismatch.

## Self-Review

### Spec coverage

- [x] 1차 latest replay provenance, requested/common/actual/gap, root dedup, missing-contract Gate covered.
- [x] 2차 resolution class, terminal state, actual handler-only CTA, three-way UX, Final Review eligibility covered.
- [x] 3차 four-date replay contract, GRS valuation-only row, static/dynamic survivorship policy covered.
- [x] 4차 unresolved/accepted split, terminal-state save snapshot, fixed deduction removal, root-only measured score, React build, Browser QA, docs covered.
- [x] current-session replay and save-and-move guard explicitly preserved.
- [x] registry/run-history/saved/generated artifact exclusions are explicit at every commit boundary.

### Placeholder scan

- [x] No `TBD`, `TODO`, `implement later`, or unspecified “appropriate tests/error handling” steps.
- [x] Every code unit names exact files, interfaces, RED command, GREEN command, and commit scope.

### Type consistency

- [x] `root_issue_id`, `resolution_class`, `action_id`, `terminal_state`, `evidence_closure`, `evidence_closure_snapshot` names are consistent across service, workspace, Final Review, React, and tests.
- [x] Date contract consistently uses `requested_market_date`, `latest_common_price_date`, `last_complete_rebalance_date`, `latest_valuation_date`.
- [x] Final Review uses Python snake_case payload with existing React camel/snake `field()` compatibility.

---

## Follow-up UX Correction — Practical Validation Closure Summary (2026-07-12)

**Goal:** Flow 4의 중복 `근거 종결 경로` 카드 묶음을 제거하고, Final Review에서 판단할 비핵심 한계의 개수만 기존 Flow 3 검증 결론 요약에 표시한다.

**Architecture:** Python은 기존 `evidence_closure` 분류와 Gate를 그대로 소유하고 `accepted_limit` root issue 개수만 workspace summary로 전달한다. React는 그 개수를 Flow 3의 기존 4열 summary band에 표시하고, Flow 4는 기존 카테고리별 기준 상세와 action board만 렌더링한다.

**Tech Stack:** Python 3, Streamlit, React/TypeScript, unittest, Vite

### Global Constraints

- registry / saved JSONL 기존 row를 재작성하거나 삭제하지 않는다.
- `PRACTICAL_VALIDATION_RESULTS.jsonl`, `BACKTEST_RUN_HISTORY.jsonl`, generated QA artifact를 stage/commit하지 않는다.
- `evidence_closure`, Final Review Gate, replay, score, 저장 계약은 변경하지 않는다.
- React는 전달받은 개수를 표시할 뿐 분류나 종결 상태를 계산하지 않는다.

### Task 5.1: Flow 4 closure card 제거와 Flow 3 compact handoff

**Files:**
- Modify: `tests/test_backtest_evidence_closure.py`
- Modify: `app/services/backtest_practical_validation_workspace.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Modify: `app/web/components/practical_validation_fix_queue/component.py`
- Modify: `app/web/components/practical_validation_fix_queue/frontend/src/index.tsx`
- Modify: `app/web/components/practical_validation_fix_queue/frontend/src/PracticalValidationFixQueue.tsx`

**Interfaces:**
- Consumes: `validation["evidence_closure"]["issues"][].resolution_class`
- Produces: `workspace["summary"]["final_review_limit_count"]: int`
- Produces: React prop `finalReviewLimitCount: number`

- [x] **Step 1: Write the failing workspace and source contract tests**

```python
workspace = build_practical_validation_workspace(validation)
self.assertEqual(workspace["summary"]["final_review_limit_count"], 1)
self.assertNotIn("evidence_closure_groups", workspace)
self.assertNotIn("_render_evidence_closure_groups", page_source)
self.assertIn("Final Review 판단에 반영할 한계", component_source)
```

- [x] **Step 2: Run RED and confirm the old card contract fails**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_evidence_closure.EvidenceClosureContractTests.test_workspace_summarizes_final_review_limits_without_closure_card_groups \
  tests.test_backtest_evidence_closure.EvidenceClosureContractTests.test_level2_hides_standalone_closure_cards_and_uses_compact_final_review_handoff
```

Expected: FAIL because `final_review_limit_count` is absent and the old renderer/source remains.

- [x] **Step 3: Implement the minimal Python read-model and UI change**

```python
final_review_limit_root_issue_ids = {
    str(issue.get("root_issue_id") or "").strip()
    for issue in closure_issues
    if issue.get("resolution_class") == "accepted_limit"
}
final_review_limit_count = len(final_review_limit_root_issue_ids - {""})
```

Remove the workspace `evidence_closure_groups` field, `_render_evidence_closure_groups()`, and its Flow 4 call. Pass `final_review_limit_count` through the existing component wrapper; render it as the fourth Flow 3 summary cell labelled `Final Review 판단에 반영할 한계`. Replace the empty blocker copy with `즉시 해결하거나 개발해야 할 차단 항목 없음`.

- [x] **Step 4: Run GREEN and focused regressions**

Run:

```bash
.venv/bin/python -m unittest tests.test_backtest_evidence_closure
npm run build --prefix app/web/components/practical_validation_fix_queue/frontend
```

Expected: all focused tests pass and Vite exits 0.

- [x] **Step 5: Verify and commit the implementation unit**

Run target `py_compile`, `git diff --check`, and confirm staged files exclude registry/run-history/artifacts.

```bash
git commit -m "Practical Validation 근거 종결 UI 중복 제거"
```

### Task 5.2: Browser QA and durable flow sync

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

- [x] **Step 1: Run Browser QA at desktop and 760px**

Verify Flow 3 shows the compact Final Review limit count and zero immediate/development blockers; Flow 4 starts with category criteria and contains no `근거 종결 경로`, raw closure diagnostic, or `미정` closure card. Capture one untracked screenshot.

- [x] **Step 2: Run fresh completion verification**

```bash
.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_service_contracts.PracticalValidationServiceContractTests
.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py app/web/components/practical_validation_fix_queue/component.py
npm run build --prefix app/web/components/practical_validation_fix_queue/frontend
git diff --check
```

Expected: 0 failures / 0 errors and every non-test command exits 0.

- [x] **Step 3: Synchronize docs and commit**

Record the presentation correction, RED/GREEN commands, Browser QA scope, and the unchanged internal Gate/closure contract.

```bash
git commit -m "Practical Validation 근거 종결 UX 문서 동기화"
```

### Follow-up Self-Review

- [x] The plan removes only the redundant presentation surface; closure classification and Final Review persistence stay unchanged.
- [x] The accepted-limit count is calculated once in Python by root issue, then displayed without React domain logic.
- [x] Flow 3 and Flow 4 ownership, RED/GREEN evidence, build, Browser QA, docs, and artifact exclusions are covered.
- [x] Function, field, test, and commit names are consistent and no placeholder remains.

---

# Final Review Decision Workspace Implementation Plan — 2026-07-16 Continuation

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended when explicitly authorized) or `superpowers:executing-plans` to implement this continuation task-by-task in the existing `codex/backtest-dev` worktree. Every behavior change follows `superpowers:test-driven-development`; every defect investigation follows `superpowers:systematic-debugging`; completion and commit claims follow `superpowers:verification-before-completion`.

**Goal:** Final Review를 validation contract inspector에서 `이 포트폴리오를 실제 투자 검토 대상으로 계속 추적할 가치가 있는가`에 답하는 React-first Decision Workspace로 바꾸고, 저장된 성과·위험·구성·실행 관측값으로 포트폴리오의 실제 강점과 약점, Monitoring 변화 조건, 최종 판단을 한 흐름에서 종결한다.

**Architecture:** 새 Streamlit-free `app/services/backtest_final_review_decision_brief.py`가 current eligible validation, investability packet, latest stored replay, selection source snapshot을 `decision_brief_v1`으로 투영한다. Python이 eligibility, canonical route, curve alignment, underwater 계산, observation normalization, root/observation dedup, trait status, strength/weakness/trigger 선택, save capability를 소유한다. React는 후보 선택·route·reason intent와 SVG 표현만 맡고, Streamlit page는 compact heading, payload orchestration, intent consumption, compact fallback만 맡는다. 기존 `build_final_review_investment_report()`와 scorecard 함수는 과거 테스트·row 호환용 inactive adapter로 남기되 current Final Review page에서는 호출하지 않는다.

**Tech Stack:** Python 3.12, pandas, `unittest`, Streamlit, React 18 + TypeScript + Vite, dependency-free SVG charts, append-only JSONL runtime helpers.

## 이걸 하는 이유?

현재 화면은 올바른 Gate와 evidence closure 계약을 갖고도 투자 검토에 필요한 관측값보다 workflow 내부 상태를 먼저 보여준다. 상단 Streamlit command center와 후보 확인 UI, 하단 React report가 서로 다른 visual shell을 사용하며, React report 안에서도 투자 매력도·근거 신뢰도·Monitoring 준비도 점수, 총평 해석 4행, 저장 전 질문, 10개 pattern guide, Level2 disposition, 상세 탭이 같은 사실을 반복한다. 이 continuation은 기존 correctness와 append-only 계약은 유지하면서, 사용자에게는 결론 → 행동 근거 → 실제 강점/약점 → 변화 조건 → 판단이라는 한 가지 읽기 순서만 제공한다.

## Global Constraints

- 기존 active task `.aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/`와 현재 worktree만 사용한다. 새 task/worktree를 만들지 않는다.
- 승인된 설계 원본은 `.aiworkspace/note/finance/researches/active/2026-07-final-review-decision-workspace-redesign/RECOMMENDATION.md`다. 구현 중 verified runtime fact가 이 설계와 충돌하거나 scope를 provider/DB/core engine까지 확장해야 할 때만 멈춘다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`, `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, saved JSONL, 기존 registry row를 rewrite/delete/stage/commit하지 않는다.
- QA screenshot, `.superpowers/`, run artifact, local snapshot은 생성 가능하지만 commit하지 않는다.
- Final Review에서 provider fetch, replay, DB ingestion, validation save, live approval, broker order, account sync, auto rebalance를 실행하지 않는다.
- historical universe / delisting provider를 추가하지 않는다. 해당 근거가 필요한 dynamic universe는 기존 Level2 Gate에서 block/defer한다.
- current Final Review eligible 후보의 `unresolved_actionable_count`, `critical_engineering_count`, `missing_contract_count`, `pre_selection_unresolved_count`는 모두 0이어야 한다. 0개인 미해결 section은 렌더링하지 않는다.
- overall investment score와 `투자 매력도 / 근거 신뢰도 / Monitoring 준비도` headline score 3종을 current Decision Workspace payload와 UI에서 제거한다. `evidence_confidence` 하나만 보조 metadata로 허용하며 route, strength, weakness, trait를 결정하지 않는다.
- 같은 `root_issue_id` 또는 `observation_id`는 strength, weakness, monitoring trigger 중 하나의 `primary_role`만 가진다. disclosure provenance는 중복 표현이 아니라 trace로만 연결한다.
- measured observation과 comparator/threshold가 모두 있을 때만 strength/weakness와 `normalized_value`를 만든다. 누락 axis는 `normalized_value=None`, `status="unmeasured"`다.
- React는 domain 분류, Gate, curve 계산, normalization, dedup, score, save validation, append를 수행하지 않는다.
- distinct implementation unit마다 RED → GREEN → focused regression → `git diff --check`를 새로 확인하고 한국어 commit을 만든다. broad `git add .`를 사용하지 않는다.

## Approved Product Contract

First-read 순서는 고정한다.

1. 추적 가치 결론과 thesis
2. 누적 성과·benchmark와 underwater drawdown
3. 구성·회전·비용·유동성 execution observation
4. 직접 관측값 기반 강점과 약점
5. Portfolio trait map
6. 실제 저장할 Monitoring 변화 조건 2~4개
7. 최종 route와 판단 사유
8. 접힌 evidence confidence / accepted limits / provenance

UI label과 저장 route의 mapping은 다음을 유지한다.

```python
DECISION_BRIEF_ROUTE_PRESENTATION = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": "계속 추적",
    "HOLD_FOR_MORE_PAPER_TRACKING": "관찰 후 재검토",
    "REJECT_FOR_PRACTICAL_USE": "추적 대상에서 제외",
    "RE_REVIEW_REQUIRED": "Level2로 돌려보내기",
}
```

## File Structure And Interfaces

### New Python owner

- Create: `app/services/backtest_final_review_decision_brief.py`
  - `build_final_review_candidate_selector(candidates: list[dict[str, Any]], *, active_source_id: str | None) -> dict[str, Any]`
  - `build_final_review_decision_brief(*, source: dict[str, Any], validation: dict[str, Any], paper_observation: dict[str, Any], decision_evidence: dict[str, Any], investability_packet: dict[str, Any], decision_id: str, existing_decision_ids: set[str]) -> dict[str, Any]`
  - `build_final_review_decision_brief_snapshot(decision_brief: dict[str, Any]) -> dict[str, Any]`
  - internal pure helpers: `_build_eligibility`, `_build_evidence_confidence`, `_stored_curve_inputs`, `_build_behavior_board`, `_build_execution_observations`, `_build_trait_map`, `_build_findings`, `_build_monitoring_conditions`, `_build_decision_action`, `_deduplicate_primary_roles`

### New test and fixture owners

- Create: `tests/test_backtest_final_review_decision_brief.py`
- Create: `tests/fixtures/final_review_grs_decision_brief.json`

### Existing owners to modify

- `app/web/backtest_final_review/page.py`: current page orchestration을 Decision Brief로 교체하고 React candidate intent와 compact fallback을 소비한다.
- `app/web/backtest_final_review_helpers.py`: final decision row에 compact `decision_brief_snapshot`을 저장한다. save evaluation과 append-only boundary는 유지한다.
- `app/web/components/final_review_investment_report/component.py`: Python prop을 `decision_brief` / `candidate_selector`로 바꾸고 새 renderer name을 export한다.
- `app/web/components/final_review_investment_report/__init__.py`: 새 availability/render export를 노출한다.
- `app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts`: snake_case payload의 current TypeScript contract.
- `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx`: Python points만 그리는 cumulative/underwater/trait SVG.
- `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`: CandidateSelector, VerdictHero, BehaviorBoard, StrengthWeaknessSection, MonitoringConditions, EvidenceDisclosure, DecisionAction.
- `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`: legacy report renderer를 제거하고 새 workspace export adapter로 축소한다.
- `app/web/components/final_review_investment_report/frontend/src/index.tsx`: `decision_brief`와 `candidate_selector` Streamlit args를 연결한다.
- `app/web/components/final_review_investment_report/frontend/src/style.css`: Workspace Overview와 같은 light neutral shell, 하나의 grid rhythm, desktop/narrow responsive hierarchy로 교체한다.
- `app/runtime/backtest/read_models/final_selected_portfolios.py`: selected row에 `decision_brief_snapshot.monitoring_conditions`가 있으면 Monitoring trigger source로 우선 사용하고 기존 `paper_tracking_snapshot.review_triggers`를 fallback으로 유지한다.
- `tests/test_service_contracts.py`: page/component/source/persistence/Monitoring compatibility contract를 교체·추가한다.
- `tests/test_backtest_refactor_boundaries.py`: Decision Brief service ownership과 React 비소유 token을 검증한다.

### Current payload schema

```python
{
    "schema_version": "decision_brief_v1",
    "candidate": {
        "source_id": str,
        "validation_id": str,
        "title": str,
        "source_type": str,
        "as_of": str | None,
    },
    "eligibility": {
        "eligible": bool,
        "unresolved_actionable_count": int,
        "critical_engineering_count": int,
        "missing_contract_count": int,
        "pre_selection_unresolved_count": int,
        "select_allowed": bool,
    },
    "verdict": {
        "route": str,
        "label": str,
        "tone": "positive" | "warning" | "danger" | "neutral",
        "headline": str,
        "thesis": str,
    },
    "evidence_confidence": {
        "value": int,
        "label": str,
        "ready_checks": int,
        "total_checks": int,
        "basis": str,
    },
    "behavior_board": {
        "period": {"start": str | None, "end": str | None, "frequency": str},
        "cumulative_series": dict,
        "benchmark_series": dict,
        "underwater_series": dict,
        "execution_observations": list[dict[str, Any]],
    },
    "trait_map": {"axes": list[dict[str, Any]], "aggregate_score": None},
    "strengths": list[dict[str, Any]],
    "weaknesses": list[dict[str, Any]],
    "monitoring_conditions": list[dict[str, Any]],
    "decision_action": dict[str, Any],
    "disclosures": dict[str, Any],
    "capabilities": {
        "can_record_decision": bool,
        "can_select_for_monitoring": bool,
        "provider_fetch": False,
        "validation_rerun": False,
        "storage_append_in_react": False,
    },
}
```

Series contract는 다음을 사용한다.

```python
{
    "status": "measured" | "unmeasured",
    "label": str,
    "source": str | None,
    "basis": "net_cost_applied" | "stored_curve_cost_unverified" | "benchmark",
    "missing_reason": str | None,
    "points": [{"date": "YYYY-MM-DD", "value": float}],
}
```

Observation/finding/trigger contract는 다음 stable identifiers를 공유한다.

```python
{
    "observation_id": str,
    "root_issue_id": str | None,
    "title": str,
    "interpretation": str,
    "measured_value": float | str,
    "display_value": str,
    "threshold_or_comparator": float | str,
    "evidence_refs": list[str],
    "as_of": str | None,
    "primary_role": "strength" | "weakness" | "monitoring",
}
```

---

## 1차: Decision Brief Contract

### Task 6.1: Pure schema, eligibility, verdict, route, candidate intent 계약

**Files:**

- Create: `app/services/backtest_final_review_decision_brief.py`
- Create: `tests/test_backtest_final_review_decision_brief.py`

**Interfaces and invariants:**

- `build_final_review_candidate_selector()`는 candidate context에서 `source_id`, `validation_id`, `title`, `source_type`, `eligible`, `selected`만 projection한다. React가 후보 상태를 재분류하지 않는다.
- `_build_eligibility()`는 stored `evidence_closure.summary`와 `selection_gate_policy_snapshot.select_allowed`를 읽는다. 네 count 중 하나라도 0이 아니면 `eligible=False`, verdict route는 `RE_REVIEW_REQUIRED`다.
- eligible 후보의 suggested route는 `selection_gate_policy_snapshot.suggested_decision_route` → `decision_evidence.suggested_decision_route` 순서로 읽고 canonical route가 아니면 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 제한한다. composite score를 route input으로 사용하지 않는다.
- `_build_evidence_confidence()`는 `investability_packet.checks`의 `Ready=True` 비율만 0~100으로 표현하고 source count를 같이 전달한다. strength/weakness/route/trait 함수는 이 값을 인자로 받지 않는다.
- 1차에서는 behavior lane과 trait axis를 제거하지 않고 명시적 `unmeasured` contract로 반환한다. 이는 placeholder가 아니라 approved missing-data state다.
- `_build_decision_action()`은 현재 `decision_id`, `existing_decision_ids`, selection gate로 각 canonical route의 `recordable`, `disabled_reason`, `reason_placeholder`, `button_label`을 만든다. route UI label은 approved mapping을 사용한다.

- [ ] **Step 1: Write failing contract tests**

Add these methods to `FinalReviewDecisionBriefContractTests`:

- `test_decision_brief_has_v1_schema_without_investment_scores`: assert `schema_version == "decision_brief_v1"` and the serialized payload contains none of the forbidden score keys/labels below.
- `test_current_eligible_brief_has_zero_preselection_unknowns`: assert all four eligibility counts are 0, `eligible=True`, and no pre-selection unresolved disclosure section exists.
- `test_unresolved_or_missing_contract_forces_level2_route`: table-test actionable, critical-engineering, and missing-contract inputs; each must set `eligible=False`, route `RE_REVIEW_REQUIRED`, and `can_select_for_monitoring=False`.
- `test_route_labels_preserve_canonical_persistence_values`: assert the four approved labels map one-to-one to the four existing canonical route values.
- `test_evidence_confidence_is_secondary_ready_check_metadata`: with 3/4 ready checks, assert `value=75`, `ready_checks=3`, `total_checks=4`, while verdict route stays equal when the ready-check ratio changes.
- `test_root_issue_and_observation_primary_roles_are_unique`: assert the concatenated visible findings contain unique non-empty stable ids and exactly one primary role per id.
- `test_candidate_selector_projects_python_owned_selection_state`: assert only the requested active source has `selected=True` and no registry/write capability appears in an option.
- `test_duplicate_decision_id_disables_recording_without_writing`: assert every option has `recordable=False`, duplicate reason is present, and all storage capabilities remain false.

Assert these forbidden keys are absent from the full JSON dump: `overall_score`, `headline_scores`, `investment_score`, `monitoring_readiness_score`, `투자 매력도`, `Monitoring 준비도`.

- [ ] **Step 2: Run RED and verify the missing service failure**

```bash
.venv/bin/python -m unittest tests.test_backtest_final_review_decision_brief
```

Expected: FAIL with `ModuleNotFoundError: app.services.backtest_final_review_decision_brief` before implementation.

- [ ] **Step 3: Implement the minimal pure contract**

Use no Streamlit/runtime store import. Build explicit route presentation, eligibility, confidence, empty-but-explicit behavior/trait state, disclosure, capabilities, and decision action. Keep `decision_brief_v1` JSON serializable.

Eligibility assertion used by the builder:

```python
eligible = (
    bool(gate.get("select_allowed"))
    and unresolved_actionable_count == 0
    and critical_engineering_count == 0
    and missing_contract_count == 0
    and pre_selection_unresolved_count == 0
)
```

- [ ] **Step 4: Run GREEN and boundary regression**

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief \
  tests.test_backtest_evidence_closure
.venv/bin/python -m py_compile app/services/backtest_final_review_decision_brief.py
git diff --check
```

Expected: all focused tests pass, compile and diff check exit 0.

- [ ] **Step 5: Stage only 1차 files and commit**

```bash
git add app/services/backtest_final_review_decision_brief.py tests/test_backtest_final_review_decision_brief.py
git diff --cached --check
git commit -m "Final Review Decision Brief 계약 도입"
```

Before commit, `git diff --name-only --cached` must not include registry, run history, `.superpowers`, screenshots, or run artifacts.

---

## 2차: Portfolio Behavior Projection

### Task 6.2: Stored curve, underwater, execution observation, trait, strength/weakness/trigger projection

**Files:**

- Modify: `app/services/backtest_final_review_decision_brief.py`
- Modify: `tests/test_backtest_final_review_decision_brief.py`
- Create: `tests/fixtures/final_review_grs_decision_brief.json`

**Source adapter priority:**

1. `validation.curve_evidence.replay_attempt.portfolio_curve` / `.benchmark_curve`
2. `validation.selection_source_snapshot.result_curve` / `.benchmark_curve`
3. `source.result_curve` / `.benchmark_curve`

The builder uses `normalize_result_curve()` from `app/services/backtest_practical_validation_curve.py`; it performs no replay or DB read. Candidate and benchmark are restricted to exact common dates. If fewer than two common points remain, both relative lanes are `unmeasured` with the parity reason instead of interpolating or silently hiding.

**Behavior calculations:**

```python
cumulative_value = round(total_balance / first_total_balance * 100.0, 4)
running_peak = max(running_peak, cumulative_value)
underwater_value = round((cumulative_value / running_peak - 1.0) * 100.0, 4)
```

- `basis="net_cost_applied"` only when `build_cost_model_source_contract(validation).application_status` proves curve application. Otherwise show the measured curve with `basis="stored_curve_cost_unverified"` and add disclosure; do not label it net.
- execution observations use structured data only:
  - concentration: `validation.metrics.max_weight` vs `validation.validation_profile.thresholds.max_weight_review`
  - turnover: `build_turnover_evidence_contract(validation).avg_turnover` vs an explicit profile/audit threshold when present
  - cost: `build_cost_model_source_contract(validation).transaction_cost_bps` and `application_status`
  - liquidity/capacity: stored provider/backtest realism structured status and `as_of_date`
  - drawdown/relative behavior: aligned curve calculations and benchmark comparator
- finding generation never parses arbitrary Korean/English prose into a number. If a legacy row has only `Current` text and no structured metric/comparator, it remains disclosure/unmeasured.

**Trait axes and normalization:**

Approved axes are `concentration_pressure`, `drawdown_pressure`, `turnover_burden`, `cost_burden`, `regime_dependency`. Every axis is present. For a higher-is-more-pressure measurement with positive threshold:

```python
normalized_value = round(max(0.0, min(100.0, measured / threshold * 50.0)), 1)
```

`50` means the stored review threshold, not neutral quality. Missing measurement or threshold yields `normalized_value=None`, `status="unmeasured"`; no aggregate/average/ranking field is produced.

**Primary-role selection:**

- Build a registry keyed by `observation_id`.
- comparator breach becomes `weakness`; explicitly favorable direct comparison becomes `strength`.
- Monitoring candidates come from structured `paper_observation.review_trigger_details`, closure `monitoring_transfer`, benchmark-relative comparator, or drawdown threshold. When an observation is selected as a trigger, remove it from strength/weakness cards and set `primary_role="monitoring"`.
- Select 2~4 conditions when structured measurements exist. Each condition contains `observation`, `threshold`, `cadence`, `re_review_action`, `evidence_refs`; generic string-only triggers go to disclosure, not the visible condition list.
- Thesis uses the first strength and first weakness/trade-off. If one side is unmeasured, the sentence states that evidence gap without inventing portfolio quality.

- [ ] **Step 1: Add failing behavior tests and current GRS fixture**

Add these exact behavior tests:

- `test_latest_stored_replay_wins_over_stale_source_curve`: give replay and source different terminal dates; assert the visible end date/source are the replay values.
- `test_aligned_curves_are_rebased_to_100_on_same_dates`: assert candidate and benchmark point dates are identical and both first values equal `100.0`.
- `test_underwater_series_uses_running_peak_and_recovery_path`: use balances `100, 120, 90, 120`; assert values `0.0, 0.0, -25.0, 0.0`.
- `test_missing_benchmark_is_explicitly_unmeasured`: assert benchmark status `unmeasured`, points empty, and non-empty `missing_reason`/source gap.
- `test_cost_unverified_curve_is_not_presented_as_net`: assert basis `stored_curve_cost_unverified`, label excludes `net/순`, and disclosure names cost application gap.
- `test_execution_observations_use_structured_values_and_refs`: assert concentration/turnover/cost observations carry the fixture values, comparator where available, evidence refs, and as-of.
- `test_trait_axes_keep_unmeasured_as_none_without_aggregate_score`: assert five axes exist, missing axes have `None`, and `aggregate_score is None`.
- `test_strengths_and_weaknesses_require_measurement_and_comparator`: remove comparator from one observation and assert it appears in neither list; favorable/breached comparisons appear on the correct side.
- `test_monitoring_conditions_are_structured_limited_and_primary_role_deduped`: assert length is 2~4, all required trigger fields are non-empty, and trigger ids do not occur in strengths/weaknesses.
- `test_current_grs_fixture_keeps_2026_06_valuation_in_behavior_series`: assert `2026-06-30` is the last chart point while the stored last complete rebalance remains `2026-05-29`.

Fixture contains a compact GRS source/validation with `requested_market_date=2026-06-30`, `last_complete_rebalance_date=2026-05-29`, `latest_valuation_date=2026-06-30`, a June valuation point, benchmark curve, cost/turnover evidence, profile thresholds, and no registry identifiers from a real user row.

- [ ] **Step 2: Run RED and verify missing projections**

```bash
.venv/bin/python -m unittest tests.test_backtest_final_review_decision_brief
```

Expected: the new behavior tests fail because lanes are still `unmeasured` and findings/triggers are empty.

- [ ] **Step 3: Implement projections in the pure service**

Implement source priority, common-date alignment, rebasing, underwater values, execution adapters, measured-only trait axes, primary-role registry, thesis, structured triggers, and disclosure source gaps. Do not modify runtime/replay code in this phase; the previous GRS period fix is consumed as stored evidence.

- [ ] **Step 4: Run GREEN and GRS regressions**

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief \
  tests.test_backtest_evidence_closure \
  tests.test_global_relative_strength_strategy
.venv/bin/python -m py_compile app/services/backtest_final_review_decision_brief.py
git diff --check
```

Expected: all focused contract and GRS tests pass; June valuation is present without a fake June rebalance.

- [ ] **Step 5: Stage only 2차 files and commit**

```bash
git add \
  app/services/backtest_final_review_decision_brief.py \
  tests/test_backtest_final_review_decision_brief.py \
  tests/fixtures/final_review_grs_decision_brief.json
git diff --cached --check
git commit -m "Final Review 포트폴리오 행동 근거 투영"
```

---

## 3차: React Decision Workspace

### Task 6.3: One-shell candidate-to-decision UI와 compact Streamlit fallback

**Files:**

- Modify: `app/web/backtest_final_review/page.py`
- Modify: `app/web/components/final_review_investment_report/component.py`
- Modify: `app/web/components/final_review_investment_report/__init__.py`
- Create: `app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts`
- Create: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx`
- Create: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/index.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: `tests/test_service_contracts.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Page contract:**

- Keep one compact `### Final Review` heading and one caption explaining the primary question.
- Remove current first-read calls to `render_fr_command_center()` and `_render_candidate_selection_panel()`.
- Build candidate selector payload in Python. Store active source id under `final_review_active_decision_brief_source_id`; default to the first eligible option.
- Add `_consume_final_review_candidate_intent(intent, *, source_options) -> None`. It accepts only `action="select_candidate"`, validates the source id against current eligible options, stores it, and reruns. It never writes a registry.
- Build one active Decision Brief and pass `decision_brief`, `candidate_selector` into React.
- Replace `_render_investment_report_fallback()` with `_render_final_review_decision_brief_fallback()`. Fallback renders verdict/thesis, measured behavior summary, strength/weakness, Monitoring conditions, route/reason controls, disclosure expander; it does not resurrect scorecard/pattern guide/Level2 card groups.
- Existing `_consume_final_review_decision_intent()` remains the only append path. Current-session `intent_id`, decision id, candidate mismatch, reason-required, selected-route gate guards remain.
- Current page must not call `build_final_review_investment_report()`.

**React contract:**

- `CandidateSelector` emits `{action: "select_candidate", intent_id, source_id}` only.
- `DecisionAction` emits the existing `{action: "record_final_decision", intent_id, decision_route, operator_reason}` only.
- `BehaviorBoard` uses Python points directly. SVG computes coordinates only; it does not rebase returns or calculate drawdown.
- `PortfolioTraitMap` draws line segments only between adjacent measured axes. An unmeasured axis displays `미측정` and must break the polygon path; outside does not mean better.
- No charting dependency is added. SVG has accessible label/summary text and a tabular compact fallback under `details`.
- Visible order follows the approved eight-section order. Candidate selector and DecisionAction share the same surface/grid rhythm.
- Remove visible strings and sections: `투자 매력도`, `핵심 점수 구분`, `이 후보를 읽는 네 가지 기준`, `저장 전 확인 질문`, `Monitoring 방향 가이드`, ten-pattern cards, Level2 review disposition cards, weakness experiment proposals.
- Disclosure contains evidence confidence, accepted limits, source gaps, and provenance only.

- [ ] **Step 1: Write failing page/component source contracts**

Add/update these source and behavior contract tests:

- `test_final_review_page_uses_decision_brief_not_legacy_investment_report`: assert current render body imports/calls the new builder and does not call the legacy report builder or command center.
- `test_final_review_page_keeps_python_candidate_and_save_intent_guards`: assert candidate id validation, consumed intent id, decision id, reason-required evaluation, and existing append function remain Python-owned.
- `test_final_review_component_accepts_decision_brief_and_candidate_selector`: assert wrapper/index args are exactly the two snake_case payloads plus the existing component key/default mechanics.
- `test_final_review_react_source_has_approved_reading_order`: compare source indices for selector, verdict, behavior, findings, trait, monitoring, decision, disclosure.
- `test_final_review_react_source_removes_scores_questions_patterns_and_level2_cards`: assert the approved forbidden labels/component names are absent from the new workspace source.
- `test_final_review_react_does_not_own_gate_normalization_dedup_or_persistence`: assert source lacks `select_allowed` derivation, cumulative/drawdown financial formulas, threshold normalization, root dedup, registry/append tokens.
- `test_final_review_trait_map_breaks_on_unmeasured_axis`: assert the chart path builder splits measured segments and never coerces `null` to zero.
- `test_final_review_fallback_uses_same_decision_brief_sections`: assert the fallback source consumes verdict, behavior board, findings, trait status, monitoring conditions, decision action, disclosures and no legacy scorecard/pattern fields.

Boundary assertions require page import of `build_final_review_decision_brief` and forbid the current render body from containing `build_final_review_investment_report(`, `render_fr_command_center(`, provider collection, replay, or append outside `_consume_final_review_decision_intent()`.

- [ ] **Step 2: Run RED and confirm the old surface is detected**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
```

Expected: FAIL because current page still builds the legacy report and TSX still contains score/question/pattern/Level2 sections.

- [ ] **Step 3: Implement Python component boundary and compact fallback**

Add `render_final_review_decision_workspace()` and `is_final_review_decision_workspace_available()`. Update page orchestration and intent consumption. Keep the component directory/name for Streamlit build compatibility but change args to `decision_brief` and `candidate_selector`.

- [ ] **Step 4: Implement React workspace and SVG visuals**

Replace legacy report body with the new components. Use CSS variables shared across all sections, white/light-neutral panels, restrained green/orange/red state color, 12-column desktop grid collapsing to one column at 760px, and no pill/card repetition for every line. Charts remain first-class; trait map is secondary.

- [ ] **Step 5: Run GREEN, build, and target compile**

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py
npm run build --prefix app/web/components/final_review_investment_report/frontend
git diff --check
```

Expected: Python tests pass, Vite production build exits 0, and target compile/diff check exit 0.

- [ ] **Step 6: Run Browser QA before committing UI**

Use `browser:control-in-app-browser` against the local Streamlit app.

Desktop 1440px checks:

- candidate selector, verdict/thesis, charts, strengths/weaknesses, trait map, triggers, decision action appear in approved order;
- one visual shell is used below the compact Streamlit heading;
- no investment/headline score, save-before questions, pattern guide, Level2 remediation card appears;
- measured/unmeasured labels match the Python payload;
- switching candidates reruns to the chosen eligible candidate without writing a row.

Narrow 760px checks:

- no horizontal clipping;
- chart labels and decision buttons remain readable;
- trait unmeasured axes remain visibly broken/not zero;
- reason input and save CTA remain reachable.

Capture one untracked screenshot named `qa-final-review-decision-workspace-760.png` and do not stage it.

- [ ] **Step 7: Stage only 3차 implementation and commit**

```bash
git add \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py \
  app/web/components/final_review_investment_report/__init__.py \
  app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts \
  app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx \
  app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx \
  app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx \
  app/web/components/final_review_investment_report/frontend/src/index.tsx \
  app/web/components/final_review_investment_report/frontend/src/style.css \
  tests/test_service_contracts.py \
  tests/test_backtest_refactor_boundaries.py
git diff --cached --check
git commit -m "Final Review Decision Workspace UI 전환"
```

Do not stage `frontend/build` unless it is already a tracked project artifact changed by the established component workflow; verify with `git ls-files` before deciding.

---

## 4차: Persistence, Monitoring Handoff, QA, Docs

### Task 6.4: Compact snapshot, route compatibility, full regression, durable sync

**Files:**

- Modify: `app/services/backtest_final_review_decision_brief.py`
- Modify: `app/web/backtest_final_review_helpers.py`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `app/runtime/backtest/read_models/final_selected_portfolios.py`
- Modify: `tests/test_backtest_final_review_decision_brief.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: approved research bundle status/risks only if implementation evidence changes a recorded assumption.

**Persistence contract:**

`build_final_review_decision_brief_snapshot()` excludes chart points and technical bulk. It returns:

```python
{
    "schema_version": "decision_brief_snapshot_v1",
    "verdict": {"route": str, "label": str, "headline": str},
    "evidence_confidence": {"value": int, "basis": str},
    "strength_observation_ids": list[str],
    "weakness_observation_ids": list[str],
    "monitoring_conditions": [{
        "observation_id": str,
        "title": str,
        "threshold": str,
        "cadence": str,
        "re_review_action": str,
    }],
    "accepted_limit_root_issue_ids": list[str],
    "source_gaps": list[str],
}
```

- `_build_final_review_decision_row(*, source: dict[str, Any], validation: dict[str, Any], paper_observation: dict[str, Any], evidence: dict[str, Any], investability_packet: dict[str, Any] | None, decision_brief: dict[str, Any], decision_id: str, decision_route: str, operator_reason: str, operator_constraints: str, operator_next_action: str) -> dict[str, Any]` stores the compact brief under `decision_brief_snapshot` while preserving existing schema version, canonical `decision_route`, `operator_decision`, `evidence_closure_snapshot`, gate snapshots, and append-only behavior.
- selected route only becomes `monitoring_candidate=True` through the existing selected-route gate and finalized closure. Snapshot content never bypasses the gate.
- Monitoring read model uses structured snapshot conditions first and converts them to display strings; old rows without a snapshot keep using `paper_tracking_snapshot.review_triggers`.
- non-select routes store the judgment and snapshot but do not become Monitoring candidates.
- No existing JSONL row is migrated or rewritten.

- [ ] **Step 1: Write failing persistence and downstream compatibility tests**

Add these exact persistence/downstream tests:

- `test_decision_brief_snapshot_excludes_curve_points_and_keeps_trigger_contract`: assert serialized snapshot lacks `points`/behavior bulk and retains all five trigger fields.
- `test_final_review_decision_row_stores_compact_decision_brief_snapshot`: assert schema/version, verdict route, finding ids, conditions, accepted root ids, and source gaps match the input brief.
- `test_selected_route_still_requires_existing_gate_and_closed_evidence`: table-test gate blocked and closure open; both must keep `monitoring_candidate=False` despite a selected-route brief.
- `test_non_select_route_records_judgment_without_monitoring_handoff`: assert row is `judgment_decision`, handoff `not_requested`, and snapshot/operator reason remain stored.
- `test_monitoring_read_model_prefers_structured_brief_conditions`: assert snapshot condition titles/thresholds/cadence become the selected Monitoring trigger display.
- `test_monitoring_read_model_falls_back_for_legacy_rows`: remove snapshot and assert existing paper trigger strings remain unchanged.
- `test_existing_canonical_route_values_are_unchanged`: assert all four route values and selected-only handoff behavior match the existing constants.

- [ ] **Step 2: Run RED and confirm snapshot/downstream failures**

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests
```

- [ ] **Step 3: Implement compact snapshot and fallback-safe Monitoring consumption**

Pass the same active Decision Brief consumed by React into `_build_final_review_decision_row()`. Add no write path outside the existing append function. Update read model with snapshot-first/fallback behavior.

- [ ] **Step 4: Run GREEN focused persistence regressions**

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review_helpers.py \
  app/web/backtest_final_review/page.py \
  app/runtime/backtest/read_models/final_selected_portfolios.py
git diff --check
```

Expected: selected/non-select/legacy contracts pass without touching registry files.

- [ ] **Step 5: Run fresh full completion verification**

Invoke `superpowers:verification-before-completion`, then run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief \
  tests.test_backtest_evidence_closure \
  tests.test_global_relative_strength_strategy \
  tests.test_backtest_refactor_boundaries \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests \
  tests.test_service_contracts.PracticalValidationServiceContractTests
npm run build --prefix app/web/components/final_review_investment_report/frontend
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review/page.py \
  app/web/backtest_final_review_helpers.py \
  app/web/components/final_review_investment_report/component.py \
  app/runtime/backtest/read_models/final_selected_portfolios.py
git diff --check
```

Then re-run desktop 1440px and narrow 760px Browser QA on:

- eligible GRS current candidate;
- missing benchmark/unmeasured lane fixture or safe local UI state;
- candidate switch;
- all four route selections without saving, then one disposable local test intent only if it does not mutate protected user registry;
- save blocker copy for duplicate/stale intent;
- selected route Monitoring handoff summary.

Do not create a real protected registry row solely for QA. Use contract tests for append behavior when safe UI isolation is unavailable. Record exact test count, build result, compile targets, Browser viewport/state coverage, and any skipped mutation in `RUNS.md`.

- [ ] **Step 6: Synchronize durable docs**

Use `finance-doc-sync` and update:

- PROJECT_MAP: new Decision Brief service owner; legacy investment report is inactive compatibility only.
- SCRIPT_STRUCTURE_MAP: Python projection → React presentation/intent → existing save boundary.
- BACKTEST_UI_FLOW: primary question and eight-section order; Level2 remediation absent; no composite score.
- PORTFOLIO_SELECTION_FLOW: canonical route mapping, compact decision snapshot, structured Monitoring conditions, legacy fallback.
- Active task: 1~4차 commits, RED/GREEN commands, Browser QA, residual risks.
- Root handoff logs: 3~5 line milestone/decision/handoff only.

- [ ] **Step 7: Stage 4차 code separately and commit**

```bash
git add \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review_helpers.py \
  app/web/backtest_final_review/page.py \
  app/runtime/backtest/read_models/final_selected_portfolios.py \
  tests/test_backtest_final_review_decision_brief.py \
  tests/test_service_contracts.py
git diff --cached --check
git commit -m "Final Review 판단과 Monitoring 조건 저장 통합"
```

- [ ] **Step 8: Verify protected/generated files are unstaged, then commit closeout docs**

```bash
git status --short
git diff --name-only --cached
```

Expected staged list excludes `PRACTICAL_VALIDATION_RESULTS.jsonl`, `BACKTEST_RUN_HISTORY.jsonl`, saved JSONL, screenshots, `.superpowers`, frontend cache, and run artifacts.

```bash
git add \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md \
  .aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git commit -m "Final Review Decision Workspace QA와 문서 동기화"
```

## Stop Conditions

Stop and report before continuing only if one of these occurs:

- current GRS/source validation does not persist any curve points and satisfying the approved chart contract would require a new replay, provider fetch, registry rewrite, or runtime result schema redesign;
- structured Monitoring conditions cannot be persisted without changing the final decision registry schema incompatibly or rewriting existing rows;
- behavior strength/weakness requires inventing thresholds not present in validation profile, benchmark comparator, or named audit contract;
- React candidate intent cannot preserve current candidate/validation id save guard without a broader Streamlit component protocol change;
- implementation requires new historical-universe/delisting provider, DB schema, live/deployment workflow, or order/account capability;
- approved design invariants conflict with a verified runtime fact;
- the same implementation hypothesis fails three times and systematic debugging identifies an architectural mismatch.

## Continuation Self-Review

### Spec coverage

- [x] Primary question and approved information order are explicit.
- [x] Overall investment score and three headline scores are removed from the current page contract; evidence confidence is secondary only.
- [x] Latest stored replay, cumulative/benchmark, underwater, execution observations, missing-data behavior, and GRS June valuation fixture are covered.
- [x] True strengths/weaknesses require measured value, comparator, evidence refs, and as-of.
- [x] Trait map is pressure/exposure only, breaks on unmeasured axes, and has no aggregate score.
- [x] Monitoring conditions are structured, limited to 2~4, persisted compactly, and do not disguise Level2 work.
- [x] Candidate selection through final reason/save intent is one React visual shell with Python-owned state and guards.
- [x] Canonical routes, append-only row behavior, closure finalization, current-session intent dedup, selected-route Gate, non-select judgment, and legacy Monitoring fallback are preserved.
- [x] Browser QA, production build, target compile, GRS regression, finance docs, active task, and root handoff sync are included.
- [x] Protected registry/run-history/saved/generated artifact exclusions are explicit at each commit boundary.

### Placeholder scan

- [x] No `TBD`, `TODO`, `implement later`, “similar to”, or unspecified “appropriate tests/error handling” step remains.
- [x] Every implementation unit names exact files, public interfaces, failing tests, RED command, minimal behavior, GREEN command, QA, and commit.

### Type and ownership consistency

- [x] `decision_brief_v1`, `decision_brief_snapshot_v1`, `observation_id`, `root_issue_id`, `primary_role`, `normalized_value`, `monitoring_conditions` names are consistent across Python, TypeScript, persistence, Monitoring, and tests.
- [x] Python snake_case is canonical; TypeScript consumes it directly without duplicate camel/snake domain fields.
- [x] React computes SVG coordinates only; every financial classification and stored value comes from Python.
- [x] `build_final_review_investment_report()` remains inactive compatibility code and is absent from the current page render path.

# Final Review Market Context Visual Fidelity Correction Plan — 2026-07-16

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` for inline execution. Every source change follows `superpowers:test-driven-development`; completion and commits follow `superpowers:verification-before-completion`.

**Goal:** 승인한 A안과 실제 `Workspace > Overview > 시장 맥락`의 visual language를 Final Review Decision Workspace에 적용하되, 이미 검증된 Python Decision Brief·Gate·저장 계약은 변경하지 않는다.

**Architecture:** React presentation owner 세 파일만 구조/스타일을 교정한다. `DecisionBriefWorkspace.tsx`가 질문과 후보 selector를 하나의 header로 결합하고, `DecisionBriefCharts.tsx`는 Python points를 그대로 그리면서 chart palette만 기준 화면과 맞춘다. `style.css`는 Market Context의 font/color/radius/shadow/responsive token을 명시적으로 사용한다. Python, registry, run history, saved JSONL은 읽거나 쓰지 않는다.

**Tech Stack:** React 18, TypeScript, dependency-free SVG, CSS, Python `unittest` source contract, Vite production build, in-app Browser QA.

## Global Constraints

- 새 task/worktree를 만들지 않고 현재 active task와 `codex/backtest-dev`를 사용한다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`, `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, `.superpowers/`, screenshot/run artifact를 stage/commit하지 않는다.
- Python projection, route, Gate, scoring, replay, persistence, Monitoring snapshot contract를 수정하지 않는다.
- `Workspace > Overview > 시장 맥락` component를 직접 수정하거나 공용 component 추출로 scope를 넓히지 않는다.
- A안의 question-first hierarchy와 Market Context의 exact visual token을 함께 만족해야 한다.
- RED → GREEN → build → Browser QA → diff check 후 distinct Korean commit을 만든다.

## File Structure

- Create: `tests/test_final_review_market_context_visual_contract.py`
  - approved question-first structure, canonical CSS token, removed editorial drift token, chart palette를 검증한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
  - `WorkspaceHeader`를 추가해 primary question과 `CandidateSelector`를 한 rounded header에 배치한다.
  - `VerdictHero`에 compact verdict, thesis, period/as-of basis, secondary evidence confidence를 배치한다.
  - approved section order와 intent payload는 유지한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx`
  - candidate `#274764`, benchmark `#269789`, underwater `#e2763b` palette를 사용한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
  - one-column 18px workbench rhythm, 20px panels, 17px chart shells, 14px metric bands, compact type scale, 760/460 responsive contract로 전면 교체한다.
- Update tracked build output under `frontend/build/` only after Vite build.

## Task 7.1: Visual Contract RED

- [x] **Step 1: Add the failing source-contract test**

Create `FinalReviewMarketContextVisualContractTests` with three tests:

```python
def test_workspace_uses_approved_question_first_header(self):
    source = WORKSPACE.read_text(encoding="utf-8")
    render = source.split("export function DecisionBriefWorkspace", 1)[1]
    self.assertIn("function WorkspaceHeader", source)
    self.assertIn("이 포트폴리오를 실제 투자 검토 대상으로", source)
    self.assertLess(render.index("<WorkspaceHeader"), render.index("<VerdictHero"))

def test_style_uses_market_context_visual_tokens_without_editorial_drift(self):
    style = STYLE.read_text(encoding="utf-8")
    for token in ("#152033", "#647589", "#dae4ee", "border-radius: 20px", "border-radius: 17px", "0 10px 30px rgba(33, 53, 72, .055)"):
        self.assertIn(token, style)
    for token in ("--db-ink: #172019", "grid-template-columns: repeat(12", "border-radius: 2px", "4.3vw", "52px"):
        self.assertNotIn(token, style)

def test_charts_use_market_context_visual_family(self):
    source = CHARTS.read_text(encoding="utf-8")
    for color in ("#274764", "#269789", "#e2763b"):
        self.assertIn(color, source)
```

- [x] **Step 2: Run RED**

```bash
.venv/bin/python -m unittest tests.test_final_review_market_context_visual_contract -v
```

Expected: FAIL because `WorkspaceHeader` and canonical tokens/palette are absent while editorial tokens remain.

## Task 7.2: React Presentation GREEN

- [x] **Step 1: Implement the question-first shell**

Add `WorkspaceHeader({brief, model, onIntent})`; move `CandidateSelector` into its right-side summary area. Keep the existing `select_candidate` intent unchanged. Replace the top-level `<CandidateSelector>` call with `<WorkspaceHeader>` and keep all later section calls in their approved order.

- [x] **Step 2: Compact the verdict**

Render `brief.verdict.label`, `headline`, `thesis`, candidate period/as-of basis and `brief.evidence_confidence` in a soft answer panel. Evidence confidence remains secondary metadata and never becomes a route/score calculation.

- [x] **Step 3: Apply canonical visual tokens**

Replace the 12-column/editorial CSS with:

```css
.db-workspace { display: grid; gap: 18px; padding: 4px 2px 18px; }
.db-workspace-header { border: 1px solid #dae4ee; border-radius: 20px; background: linear-gradient(135deg, #f8fbff 0%, #f1f7f7 100%); }
.db-section { border: 1px solid #dae4ee; border-radius: 20px; background: #fff; box-shadow: 0 10px 30px rgba(33, 53, 72, .055); }
.db-chart-shell { border-radius: 17px; background: linear-gradient(180deg, #fff 0%, #fbfcfe 100%); }
.db-observation-strip { overflow: hidden; border-radius: 14px; }
```

Use 23/20/18px heading hierarchy and 760/460px responsive breakpoints. Keep visible focus, disabled, alert, table scroll and unmeasured states.

- [x] **Step 4: Align chart strokes**

Change only presentation colors in `DecisionBriefCharts.tsx`: candidate `#274764`, benchmark `#269789`, underwater `#e2763b`. Do not change series alignment, path calculation, trait segmentation or accessible labels.

- [x] **Step 5: Run GREEN and focused regression**

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
npm run build --prefix app/web/components/final_review_investment_report/frontend
git diff --check
```

Expected: all focused tests pass, Vite build exits 0, diff check exits 0.

- [x] **Step 6: Browser QA against the actual reference**

Desktop 1440px:

- open `Workspace > Overview > 시장 맥락` and Final Review in the same local app;
- compare font, blue-gray palette, 20px outer radius, soft shadow, 17px chart shell, 14px metric band, compact heading hierarchy;
- verify primary question, candidate switch, verdict, charts, findings, trait, Monitoring, route/reason appear in order;
- verify there is no angular green top-border hero or 52px editorial headline.

Narrow 760px:

- verify header, chart, finding, monitoring and route grids collapse without horizontal overflow;
- verify candidate switch, route selection, reason input, disclosure remain usable;
- do not click the append/save CTA against the protected registry.

Capture `qa-final-review-market-context-visual-parity-760.png` as an untracked artifact and do not stage it.

- [x] **Step 7: Commit the implementation unit**

Stage only the new visual test, three React source files and tracked Vite build output. Verify the staged list excludes registry, run history, `.superpowers`, screenshots and other generated artifacts.

```bash
git commit -m "Final Review 시장 맥락 시각 체계 적용"
```

## Task 7.3: Closeout Documentation

- [x] **Step 1: Record RED/GREEN/build/Browser QA evidence** in active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`.
- [x] **Step 2: Correct durable UI wording** in the Decision Workspace research recommendation/UI patterns and Backtest flow docs so future work treats Market Context as both projection and visual-language reference.
- [x] **Step 3: Add a concise root handoff milestone** without copying detailed QA logs.
- [x] **Step 4: Run fresh completion verification**:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
npm run build --prefix app/web/components/final_review_investment_report/frontend
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py
git diff --check
git status --short
```

- [x] **Step 5: Commit closeout docs** with `git commit -m "Final Review 시각 교정 QA와 문서 동기화"`.

## Correction Plan Self-Review

- [x] Approved A안 and actual Market Context reference are both named.
- [x] Exact font/color/radius/shadow/type/spacing tokens replace subjective “similar” wording.
- [x] Python/data/Gate/persistence owners are unchanged.
- [x] Tests fail on the current angular/editorial implementation before source changes.
- [x] Browser QA includes side-by-side reference comparison at 1440px and overflow/interaction checks at 760px.
- [x] Protected registry, run history, `.superpowers`, screenshots and saved JSONL remain unstaged.
- [x] Implementation and closeout docs are distinct Korean commits.

# Final Review Chart Interaction And Content Polish Implementation Plan — 2026-07-16

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` for inline execution. Every behavior change follows `superpowers:test-driven-development`; completion and commits follow `superpowers:verification-before-completion`. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Final Review의 섹션 제목 계층, 누적 성과/고점 대비 낙폭 chart hover와 X·Y축, observation strip의 빈 면과 긴 값 clipping을 보정한다.

**Architecture:** 기존 `decision_brief_v1` payload와 dependency-free React SVG를 유지한다. `DecisionBriefWorkspace.tsx`는 heading DOM grouping만, `DecisionBriefCharts.tsx`는 nice extent/tick/pointer/tooltip presentation state만, `style.css`는 responsive grid/wrapping/tooltip visual만 소유한다. Python 계산, exact-common alignment, running-peak drawdown, Gate, route, save, registry는 변경하지 않는다.

**Tech Stack:** React 18, TypeScript, dependency-free SVG, CSS, Python `unittest` source contract, Vite production build, in-app Browser QA.

## Global Constraints

- 현재 active task와 `codex/backtest-dev` worktree를 계속 사용하고 새 task/worktree를 만들지 않는다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`, run history, `.superpowers/`, screenshot/run artifact를 stage/commit하지 않는다.
- chart library나 npm dependency를 추가하지 않는다.
- Python Decision Brief, Gate, score, route, persistence, Monitoring snapshot을 수정하지 않는다.
- hover는 React local presentation state이며 Streamlit rerun이나 registry append를 만들지 않는다.
- 기존 수치 표 fallback과 SVG `title` / `desc` 접근성 contract를 유지한다.
- RED → GREEN → focused regression → build → Browser QA → `git diff --check` 순서를 지킨다.

---

## File Structure And Interfaces

- Modify: `tests/test_final_review_market_context_visual_contract.py`
  - heading grouping, hover/axis/tooltip, Underwater 한글 semantics, observation grid/wrap source contract를 고정한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
  - `SectionHeading`의 eyebrow/title DOM grouping만 변경한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx`
  - `ChartUnit`, `niceExtent`, `buildTickIndices`, `buildYTicks`, `pointerIndex`, interactive `SvgLineChart`를 소유한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
  - heading copy, chart plot/axis/tooltip, observation 3/2/1열과 wrap contract를 소유한다.
- Modify: tracked production bundle under `app/web/components/final_review_investment_report/frontend/build/` after GREEN.

## Task 8.1: Heading Hierarchy And Observation Layout

**Files:**
- Modify: `tests/test_final_review_market_context_visual_contract.py`
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`

**Interfaces:**
- Consumes: existing `SectionHeading({eyebrow, title, detail})` and `DecisionBriefObservation[]`.
- Produces: `.db-section-heading-copy` DOM grouping and `.db-observation-strip` 3/2/1-column responsive contract.

- [x] **Step 1: Write failing heading and observation source-contract tests**

Add to `FinalReviewMarketContextVisualContractTests`:

```python
def test_section_heading_groups_eyebrow_above_korean_title(self) -> None:
    source = WORKSPACE.read_text(encoding="utf-8")
    heading = source.split("function SectionHeading", 1)[1].split("function CandidateSelector", 1)[0]
    self.assertIn('className="db-section-heading-copy"', heading)
    self.assertLess(heading.index('{eyebrow}'), heading.index("<h2>{title}</h2>"))

def test_observation_strip_has_complete_responsive_grid_and_wraps_long_values(self) -> None:
    style = STYLE.read_text(encoding="utf-8")
    self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr));", style)
    self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr));", style)
    self.assertIn("overflow-wrap: anywhere;", style)
    self.assertIn("word-break: break-word;", style)
    observation_block = style.split(".db-observation-strip {", 1)[1].split(".db-empty,", 1)[0]
    self.assertNotIn("background: #e1e8f0;", observation_block)
```

- [x] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract.FinalReviewMarketContextVisualContractTests.test_section_heading_groups_eyebrow_above_korean_title \
  tests.test_final_review_market_context_visual_contract.FinalReviewMarketContextVisualContractTests.test_observation_strip_has_complete_responsive_grid_and_wraps_long_values -v
```

Expected: 2 failures because `.db-section-heading-copy`, explicit 3-column observation grid and wrap rules are absent.

- [x] **Step 3: Group eyebrow and title**

Replace `SectionHeading` body with:

```tsx
return (
  <header className="db-section-heading">
    <div className="db-section-heading-copy">
      <p className="db-kicker">{eyebrow}</p>
      <h2>{title}</h2>
    </div>
    {detail && <p className="db-section-detail">{detail}</p>}
  </header>
)
```

- [x] **Step 4: Apply complete observation layout and wrapping**

Use:

```css
.db-section-heading-copy { min-width: 0; }
.db-section-detail { max-width: 430px; margin: 2px 0 0; text-align: right; }
.db-observation-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; overflow: visible; border: 0; background: transparent; }
.db-observation-strip article { border: 1px solid #e1e8f0; border-radius: 14px; }
.db-observation-strip strong,
.db-observation-strip p,
.db-observation-strip small { overflow-wrap: anywhere; word-break: break-word; }
```

At `max-width: 760px`, use 2 columns; at `max-width: 460px`, use 1 column. Update the existing detail selector from `.db-section-heading > p:last-child` to `.db-section-detail`.

- [x] **Step 5: Run GREEN and focused visual regression**

Run:

```bash
.venv/bin/python -m unittest tests.test_final_review_market_context_visual_contract -v
git diff --check
```

Expected: 5 visual contract tests pass; diff check exits 0.

- [x] **Step 6: Commit heading/list implementation unit**

Stage only the test, workspace and style source files; verify the registry is excluded.

```bash
git commit -m "Final Review 제목 계층과 관측 목록 보정"
```

## Task 8.2: Interactive SVG Axes And Tooltip

**Files:**
- Modify: `tests/test_final_review_market_context_visual_contract.py`
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: tracked `frontend/build/` output after build

**Interfaces:**
- Produces: `type ChartUnit = "index" | "percent"`.
- Produces: `niceExtent(values: number[], unit: ChartUnit) -> [number, number]`.
- Produces: `buildTickIndices(count: number, maximumTicks?: number) -> number[]`.
- Produces: `buildYTicks(minimum: number, maximum: number, count?: number) -> number[]`.
- Consumes: existing `LineSeries[]`, exact-common `SeriesPoint[]`, `EvidenceTable`.

- [x] **Step 1: Write failing chart interaction source-contract test**

Add:

```python
def test_charts_expose_ticks_hover_tooltip_and_underwater_meaning(self) -> None:
    source = CHARTS.read_text(encoding="utf-8")
    style = STYLE.read_text(encoding="utf-8")
    for token in (
        "type ChartUnit",
        "function niceExtent",
        "function buildTickIndices",
        "function buildYTicks",
        "function pointerIndex",
        "onPointerMove",
        "db-chart-hover-rule",
        "db-chart-focus-dot",
        "db-chart-tooltip",
        'unit="percent"',
        "고점 대비 낙폭 (Underwater)",
        "0%는 이전 최고점 회복",
    ):
        self.assertIn(token, source + style)
```

- [x] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract.FinalReviewMarketContextVisualContractTests.test_charts_expose_ticks_hover_tooltip_and_underwater_meaning -v
```

Expected: failure because chart scale helpers, pointer handler, tooltip classes and Korean Underwater copy are absent.

- [x] **Step 3: Add chart geometry and tick helpers**

In `DecisionBriefCharts.tsx`, import `useEffect`, `useState` and add:

```tsx
type ChartUnit = "index" | "percent"
const CHART = { width: 720, height: 300, left: 58, right: 16, top: 20, bottom: 44 }

function niceExtent(values: number[], unit: ChartUnit): [number, number] {
  if (!values.length) return unit === "percent" ? [-5, 0] : [0, 100]
  const rawMin = unit === "percent" ? Math.min(...values, 0) : Math.min(...values)
  const rawMax = unit === "percent" ? 0 : Math.max(...values)
  const rawRange = Math.max(1, rawMax - rawMin)
  const lower = rawMin - rawRange * .08
  const upper = unit === "percent" ? 0 : rawMax + rawRange * .08
  const roughStep = Math.max(.01, (upper - lower) / 4)
  const magnitude = 10 ** Math.floor(Math.log10(roughStep))
  const normalized = roughStep / magnitude
  const step = (normalized <= 1.5 ? 1 : normalized <= 3 ? 2 : normalized <= 7 ? 5 : 10) * magnitude
  return [Math.floor(lower / step) * step, unit === "percent" ? 0 : Math.ceil(upper / step) * step]
}

function buildTickIndices(count: number, maximumTicks = 6): number[] {
  if (count <= 0) return []
  const tickCount = Math.min(count, maximumTicks)
  return Array.from(new Set(Array.from({ length: tickCount }, (_, index) =>
    Math.round(index * (count - 1) / Math.max(1, tickCount - 1)),
  )))
}

function buildYTicks(minimum: number, maximum: number, count = 5): number[] {
  return Array.from({ length: count }, (_, index) =>
    maximum - index * (maximum - minimum) / Math.max(1, count - 1),
  )
}

const plotWidth = CHART.width - CHART.left - CHART.right
const plotBottom = CHART.height - CHART.bottom
const plotHeight = plotBottom - CHART.top

function xAt(index: number, count: number): number {
  return count <= 1
    ? CHART.left + plotWidth / 2
    : CHART.left + index / (count - 1) * plotWidth
}

function yAt(value: number, minimum: number, maximum: number): number {
  return plotBottom - (value - minimum) / Math.max(.0001, maximum - minimum) * plotHeight
}

function linePath(points: SeriesPoint[], minimum: number, maximum: number): string {
  return points.map((point, index) =>
    `${index ? "L" : "M"} ${xAt(index, points.length).toFixed(2)} ${yAt(point.value, minimum, maximum).toFixed(2)}`,
  ).join(" ")
}

function pointerIndex(event: React.PointerEvent<SVGSVGElement>, count: number): number {
  if (count <= 1) return 0
  const rect = event.currentTarget.getBoundingClientRect()
  const cursor = (event.clientX - rect.left) / Math.max(1, rect.width) * CHART.width
  const ratio = Math.max(0, Math.min(1, (cursor - CHART.left) / plotWidth))
  return Math.round(ratio * (count - 1))
}
```

- [x] **Step 4: Implement interactive `SvgLineChart`**

Extend props with `subtitle: string` and `unit: ChartUnit`. Use `useState` for `activeIndex`, reset to the latest point when point count changes, and replace the complete function with:

```tsx
function formatChartValue(value: number | undefined, unit: ChartUnit): string {
  if (value == null || !Number.isFinite(value)) return "-"
  const formatted = Math.abs(value) >= 100 ? value.toFixed(0) : value.toFixed(2)
  return unit === "percent" ? `${formatted}%` : formatted
}

function SvgLineChart({
  title,
  subtitle,
  description,
  unit,
  series,
}: {
  title: string
  subtitle: string
  description: string
  unit: ChartUnit
  series: LineSeries[]
}) {
  const chartId = useId()
  const pointCount = series[0]?.points.length ?? 0
  const [activeIndex, setActiveIndex] = useState(Math.max(0, pointCount - 1))
  useEffect(() => setActiveIndex(Math.max(0, pointCount - 1)), [pointCount])
  const safeIndex = Math.min(activeIndex, Math.max(0, pointCount - 1))
  const values = series.flatMap((item) => item.points.map((point) => point.value))
  const [minY, maxY] = niceExtent(values, unit)
  const yTicks = buildYTicks(minY, maxY)
  const xTickIndices = buildTickIndices(pointCount)
  const activeX = xAt(safeIndex, pointCount)
  const activeDate = series[0]?.points[safeIndex]?.date ?? "-"
  const tooltipRight = activeX > CHART.width * .68
  const tooltipStyle = { left: `${activeX / CHART.width * 100}%` }

  return (
    <div className="db-chart-shell">
      <div className="db-chart-heading">
        <div>
          <p className="db-kicker">Portfolio behavior</p>
          <h3>{title}</h3>
          <p className="db-chart-subtitle">{subtitle}</p>
        </div>
        <div className="db-legend" aria-label="차트 범례">
          {series.map((item) => (
            <span key={item.label}><i style={{ background: item.color }} />{item.label}</span>
          ))}
        </div>
      </div>
      <div className="db-chart-plot">
        <svg
          className="db-line-chart"
          viewBox={`0 0 ${CHART.width} ${CHART.height}`}
          role="img"
          aria-labelledby={`${chartId}-title ${chartId}-desc`}
          onPointerMove={(event) => setActiveIndex(pointerIndex(event, pointCount))}
          onPointerLeave={() => setActiveIndex(Math.max(0, pointCount - 1))}
        >
          <title id={`${chartId}-title`}>{title}</title>
          <desc id={`${chartId}-desc`}>{description}</desc>
          {yTicks.map((value) => {
            const y = yAt(value, minY, maxY)
            return (
              <g key={value}>
                <line x1={CHART.left} x2={CHART.width - CHART.right} y1={y} y2={y} className="db-grid-line" />
                <text x={CHART.left - 10} y={y + 4} textAnchor="end" className="db-chart-y-label">
                  {formatChartValue(value, unit)}
                </text>
              </g>
            )
          })}
          {xTickIndices.map((index) => (
            <text key={index} x={xAt(index, pointCount)} y={CHART.height - 12} textAnchor="middle" className="db-chart-x-label">
              {series[0]?.points[index]?.date ?? "-"}
            </text>
          ))}
          {series.map((item) => (
            <path key={item.label} d={linePath(item.points, minY, maxY)} fill="none" stroke={item.color} strokeWidth="2" />
          ))}
          <line className="db-chart-hover-rule" x1={activeX} x2={activeX} y1={CHART.top} y2={plotBottom} />
          {series.map((item) => {
            const point = item.points[safeIndex]
            return point ? (
              <circle key={item.label} className="db-chart-focus-dot" cx={activeX} cy={yAt(point.value, minY, maxY)} r="4" style={{ fill: item.color }} />
            ) : null
          })}
        </svg>
        <div className={`db-chart-tooltip ${tooltipRight ? "is-right" : ""}`} style={tooltipStyle}>
          <span>{activeDate}</span>
          {series.map((item) => (
            <div key={item.label}>
              <i style={{ background: item.color }} />
              <small>{item.label}</small>
              <strong>{formatChartValue(item.points[safeIndex]?.value, unit)}</strong>
            </div>
          ))}
        </div>
      </div>
      <EvidenceTable series={series} />
    </div>
  )
}
```

Keep `EvidenceTable` immediately after the plot. Remove the old `.db-chart-axis` start/min-max/end row because the SVG now owns actual axes.

- [x] **Step 5: Apply chart copy and unit semantics**

Use cumulative props:

```tsx
title="누적 성과와 Benchmark"
subtitle="100은 관측 시작일의 기준값입니다. 같은 날짜의 후보와 Benchmark 경로를 비교합니다."
unit="index"
```

Use drawdown props:

```tsx
title="고점 대비 낙폭 (Underwater)"
subtitle="0%는 이전 최고점 회복, 음수는 최고점 대비 하락률입니다."
unit="percent"
```

Keep the Python running-peak description in the SVG `desc`.

- [x] **Step 6: Add chart axis and tooltip CSS**

Add `.db-chart-subtitle`, `.db-chart-plot`, `.db-chart-y-label`, `.db-chart-x-label`, `.db-chart-hover-rule`, `.db-chart-focus-dot`, `.db-chart-tooltip` and `.db-chart-tooltip.is-right`. Tooltip is absolute, pointer-events none, white translucent, rounded 11px and uses the existing blue-gray palette. At 460px reduce tooltip padding and type size without hiding values.

- [x] **Step 7: Run GREEN, focused regression and production build**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
npm run build --prefix app/web/components/final_review_investment_report/frontend
git diff --check
```

Expected: 115 focused tests pass after adding 3 new visual tests to the previous 112-test suite; Vite exits 0; diff check exits 0.

- [x] **Step 8: Browser QA**

Desktop:

- verify eyebrow is immediately above Korean title for Behavior, Findings, Trait, Monitoring and Decision sections;
- hover the cumulative chart at left/center/right and verify date, candidate and Benchmark values update with crosshair/dots;
- verify X date ticks and Y rebased-index ticks are readable and do not overlap;
- hover drawdown and verify date/value plus percent Y ticks; confirm its upper bound is 0%, not padded positive;
- verify six observations render 3×2 with no large gray unused area and long liquidity/comparator tokens wrap fully.

Narrow 760px:

- verify chart tooltip stays inside each card, axes remain readable, observations render 2×3 and component/document horizontal overflow is 0;
- do not click the Final Review save CTA or mutate protected registry.

Save one generated screenshot as `qa-final-review-chart-hover-content-polish-760.png` and do not stage it.

- [x] **Step 9: Commit chart interaction implementation unit**

Stage test/chart/style and tracked build output only. Verify cached names exclude registry, run history, screenshots and `.superpowers`.

```bash
git commit -m "Final Review 차트 축과 hover 상호작용 개선"
```

## Task 8.3: Closeout Documentation And Verification

**Files:**
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`, `PLAN.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: root `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Documents implemented presentation behavior only; no roadmap, architecture map or data contract changes.

- [x] **Step 1: Record root cause, RED/GREEN/build and Browser QA evidence** in the active task docs.
- [x] **Step 2: Add one durable flow sentence** that Final Review behavior charts expose date/value axes and hover while Underwater means running-peak drawdown.
- [x] **Step 3: Add concise root handoff milestones** without copying command logs.
- [x] **Step 4: Run fresh completion verification**:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
npm run build --prefix app/web/components/final_review_investment_report/frontend
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py
git diff --check
git status --short
```

Expected: 115 tests pass, 176-module Vite build exits 0, py_compile and diff check exit 0; only protected/generated files remain outside the staged doc set.

- [x] **Step 5: Commit closeout docs**:

```bash
git commit -m "Final Review 차트 상호작용 QA와 문서 동기화"
```

## Chart Polish Plan Self-Review

- [x] Heading, axes, hover, Underwater meaning, empty strip area and long-token clipping each map to an implementation task.
- [x] Function names and `ChartUnit` props are consistent between helper and render steps.
- [x] Python/data/Gate/persistence are explicitly out of scope.
- [x] RED commands fail on missing DOM/classes/helpers before source changes.
- [x] Desktop and 760px Browser QA cover hover, axes, wrapping and overflow without save mutation.
- [x] Plan, heading/list, chart interaction and closeout docs are distinct Korean commits.
- [x] 금지된 미완성 표식과 구체화되지 않은 오류 처리 단계가 새 계획 구간에 남아 있지 않다.

# Final Review Portfolio Character And Review Pressure Implementation Plan — 2026-07-16

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` for inline execution. Every behavior change follows `superpowers:test-driven-development`; completion and commits follow `superpowers:verification-before-completion`. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Final Review에서 실제 포트폴리오 성격을 threshold 유무와 관계없이 보여주고, 저장된 관리 기준 대비 이내·초과·기준 미설정·근거 없음 상태를 별도 영역으로 정확히 표시한다.

**Architecture:** `app/services/backtest_final_review_decision_brief.py`가 기존 structured execution observation을 한 번 만들고 `character_profile`과 `review_pressure`를 파생한다. 새 React owner `DecisionBriefCharacter.tsx`는 두 Python payload를 표시만 하며 radar/임의 0~100 normalization을 제거한다. Streamlit fallback도 같은 순서를 소비하고 Gate, route, persistence, Monitoring snapshot은 변경하지 않는다.

**Tech Stack:** Python 3.12, `unittest`, React 18, TypeScript, CSS, Vite, Streamlit fallback, in-app Browser QA.

## Global Constraints

- 기존 `codex/backtest-dev` worktree와 active task를 계속 사용하고 새 task/worktree를 만들지 않는다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`, run history, saved JSONL, `.superpowers/`, QA screenshot을 stage/commit하지 않는다.
- raw character와 review pressure는 같은 Python observation/evidence ref에서 파생한다. React는 threshold alias, comparison, delta를 계산하지 않는다.
- `mdd_review_line`은 canonical drawdown review criterion alias로 Python에서 연결한다.
- `one_way_cost_bps`는 비용 가정 자체이므로 cost review limit으로 사용하지 않는다.
- turnover/cost criterion을 임의 기본값으로 만들지 않고, regime provider/analytics도 추가하지 않는다.
- `trait_map`, `normalized_value`, `aggregate_score`, `83.3 / 100` pressure score와 radar polygon을 current payload/UI에서 제거한다.
- Final Review는 provider fetch, replay, DB ingestion, validation profile edit, registry append를 실행하지 않는다.
- RED → GREEN → focused regression → production build → Browser QA → fresh completion verification 순서를 지킨다.

---

## File Structure And Interfaces

- Modify: `app/services/backtest_final_review_decision_brief.py`
  - character measurement와 review criterion comparison을 소유한다.
- Modify: `tests/test_backtest_final_review_decision_brief.py`
  - current GRS character/criterion fixture와 Python contract를 고정한다.
- Create: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharacter.tsx`
  - 실제 성격과 관리 압력 presentation을 소유한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts`
  - `CharacterProfileItem`, `ReviewPressureItem`과 brief field를 정의한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
  - section order와 새 component orchestration만 소유한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx`
  - trait radar code와 `TraitAxis` 의존성을 제거하고 behavior chart만 유지한다.
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
  - desktop 2열 / 760px 1열 character layout과 status presentation을 소유한다.
- Modify: `app/web/backtest_final_review/page.py`
  - React build unavailable 시 동일 character/pressure fallback을 렌더한다.
- Modify: `tests/test_service_contracts.py`
  - React reading order, presentation-only boundary, fallback parity를 고정한다.
- Modify: `tests/test_final_review_market_context_visual_contract.py`
  - Market Context visual family와 character responsive source contract를 고정한다.
- Modify: tracked `frontend/build/` output after GREEN.

## Task 9.1: Python Character And Review Pressure Contract

**Files:**
- Modify: `tests/test_backtest_final_review_decision_brief.py`
- Modify: `app/services/backtest_final_review_decision_brief.py`

**Interfaces:**
- Produces: `_build_character_profile(observations: list[dict[str, Any]]) -> dict[str, Any]`.
- Produces: `_build_review_pressure(observations: list[dict[str, Any]]) -> dict[str, Any]`.
- Produces: `_criterion_favorable(measured: float, criterion: float, comparison: str) -> bool`.
- Produces payload fields: `character_profile.items[]`, `review_pressure.items[]`.
- Removes current payload field: `trait_map`.

- [x] **Step 1: Add a current-character fixture helper and failing contract tests**

Add to `FinalReviewDecisionBriefContractTests`:

```python
def _current_character_inputs(self) -> dict[str, object]:
    inputs = self._grs_inputs()
    validation = inputs["validation"]
    validation["metrics"]["max_weight"] = 100.0
    validation["validation_profile"]["thresholds"] = {
        "max_weight_review": 60.0,
        "mdd_review_line": -15.0,
        "one_way_cost_bps": 10.0,
    }
    source_snapshot = validation["selection_source_snapshot"]["source_snapshot"]
    source_snapshot["turnover_evidence_snapshot"]["avg_turnover"] = 0.032
    source_snapshot["cost_model_snapshot"].update(
        {
            "transaction_cost_bps": 10.0,
            "cost_application_status": "applied_to_result_curve",
        }
    )
    validation["curve_evidence"]["replay_attempt"]["portfolio_curve"][2][
        "Total Balance"
    ] = 105.084
    return inputs

def test_character_profile_exposes_observed_values_without_criteria(self) -> None:
    brief = self._build(self._current_character_inputs())
    items = {row["axis_id"]: row for row in brief["character_profile"]["items"]}

    self.assertEqual(list(items), ["concentration", "drawdown", "turnover", "cost", "regime_dependency"])
    self.assertEqual(items["concentration"]["display_value"], "100.00%")
    self.assertEqual(items["drawdown"]["display_value"], "-12.43%")
    self.assertEqual(items["turnover"]["display_value"], "3.20%")
    self.assertEqual(items["cost"]["display_value"], "10.00 bps")
    self.assertEqual(items["regime_dependency"]["measurement_status"], "evidence_missing")
    self.assertEqual(items["regime_dependency"]["display_value"], "분석 근거 없음")

def test_review_pressure_links_drawdown_alias_and_separates_missing_states(self) -> None:
    brief = self._build(self._current_character_inputs())
    pressure = {row["axis_id"]: row for row in brief["review_pressure"]["items"]}

    self.assertEqual(pressure["concentration"]["status"], "exceeds_limit")
    self.assertEqual(pressure["concentration"]["delta_value"], 40.0)
    self.assertEqual(pressure["drawdown"]["status"], "within_limit")
    self.assertEqual(pressure["drawdown"]["criterion_value"], -15.0)
    self.assertEqual(pressure["drawdown"]["delta_value"], -2.57)
    self.assertIn("관리선 -15.00%", pressure["drawdown"]["summary"])
    self.assertEqual(pressure["turnover"]["status"], "criterion_missing")
    self.assertEqual(pressure["cost"]["status"], "criterion_missing")
    self.assertEqual(pressure["regime_dependency"]["status"], "evidence_missing")

def test_one_way_cost_assumption_is_not_used_as_review_limit(self) -> None:
    brief = self._build(self._current_character_inputs())
    cost = next(row for row in brief["review_pressure"]["items"] if row["axis_id"] == "cost")

    self.assertEqual(cost["display_value"], "10.00 bps")
    self.assertIsNone(cost["criterion_value"])
    self.assertEqual(cost["status"], "criterion_missing")

def test_character_contract_has_no_trait_map_or_arbitrary_score(self) -> None:
    brief = self._build(self._current_character_inputs())
    serialized = json.dumps(brief, ensure_ascii=False, sort_keys=True)

    self.assertNotIn("trait_map", brief)
    self.assertNotIn("aggregate_score", serialized)
    self.assertNotIn("normalized_value", serialized)
```

Delete `test_trait_axes_keep_unmeasured_as_none_without_aggregate_score` because the approved contract removes `trait_map` rather than preserving it.

- [x] **Step 2: Run RED and confirm the old contract is the failure cause**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_character_profile_exposes_observed_values_without_criteria \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_review_pressure_links_drawdown_alias_and_separates_missing_states \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_one_way_cost_assumption_is_not_used_as_review_limit \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_character_contract_has_no_trait_map_or_arbitrary_score -v
```

Expected: 4 errors/failures because `character_profile` and `review_pressure` are absent and `trait_map` still exists.

- [x] **Step 3: Canonicalize character axes and drawdown comparison**

Replace `_TRAIT_AXES` with metadata that separates user character labels from missing evidence copy:

```python
_CHARACTER_AXES = (
    ("concentration", "집중 성향", "percent", "최대 구성 비중 근거가 없습니다."),
    ("drawdown", "손실 특성", "percent", "running-peak 낙폭 curve가 없습니다."),
    ("turnover", "회전 성향", "ratio_percent", "holdings 기반 회전율 근거가 없습니다."),
    ("cost", "비용 가정", "bps", "거래비용 가정 근거가 없습니다."),
    ("regime_dependency", "국면 의존", "text", "국면별 성과 분산을 계산할 structured evidence가 없습니다."),
)
```

Rename `_observation(..., trait_axis=...)` to `_observation(..., character_axis=...)`, store `_character_axis`, and use `concentration`, `turnover`, `cost`, `drawdown` in the four measured observation calls.

Resolve drawdown criterion without treating `0` as missing and preserve the signed observation:

```python
drawdown_threshold = _optional_float(thresholds.get("max_drawdown_review_pct"))
if drawdown_threshold is None:
    drawdown_threshold = _optional_float(thresholds.get("mdd_review_line"))

measured_value=max_drawdown,
threshold_or_comparator=drawdown_threshold,
comparison="absolute_less_or_equal",
character_axis="drawdown",
```

Add a shared comparison helper and use it in `_build_findings`:

```python
def _criterion_favorable(measured: float, criterion: float, comparison: str) -> bool:
    if comparison == "absolute_less_or_equal":
        return abs(measured) <= abs(criterion)
    if comparison == "less_or_equal":
        return measured <= criterion
    if comparison == "greater_or_equal":
        return measured >= criterion
    raise ValueError(f"unsupported review comparison: {comparison}")
```

- [x] **Step 4: Build actual character and review pressure projections**

Replace `_build_trait_map` with these focused builders:

```python
def _build_character_profile(observations: list[dict[str, Any]]) -> dict[str, Any]:
    by_axis = {
        str(row.get("_character_axis")): row
        for row in observations
        if str(row.get("_character_axis") or "").strip()
    }
    items: list[dict[str, Any]] = []
    for axis_id, label, unit, missing_reason in _CHARACTER_AXES:
        observation = by_axis.get(axis_id, {})
        measured = _optional_float(observation.get("measured_value"))
        observed = measured is not None
        items.append(
            {
                "axis_id": axis_id,
                "label": label,
                "measurement_status": "observed" if observed else "evidence_missing",
                "measured_value": measured,
                "display_value": (
                    str(observation.get("display_value")) if observed else "분석 근거 없음"
                ),
                "unit": unit,
                "interpretation": (
                    str(observation.get("interpretation") or "") if observed else missing_reason
                ),
                "evidence_refs": list(observation.get("evidence_refs") or []),
                "as_of": observation.get("as_of"),
            }
        )
    return {"items": items}

def _criterion_display(axis_id: str, value: float) -> str:
    if axis_id == "cost":
        return f"{value:.2f} bps"
    if axis_id == "turnover":
        return _display_percent(value, ratio=True)
    return _display_percent(value)

def _delta_display(axis_id: str, delta: float, *, favorable: bool) -> str:
    displayed = delta * 100.0 if axis_id == "turnover" else delta
    unit = "bps" if axis_id == "cost" else "%p"
    return f"{abs(displayed):.2f}{unit} {'이내' if favorable else '초과'}"

def _build_review_pressure(observations: list[dict[str, Any]]) -> dict[str, Any]:
    by_axis = {
        str(row.get("_character_axis")): row
        for row in observations
        if str(row.get("_character_axis") or "").strip()
    }
    items: list[dict[str, Any]] = []
    for axis_id, label, _unit, missing_reason in _CHARACTER_AXES:
        observation = by_axis.get(axis_id, {})
        measured = _optional_float(observation.get("measured_value"))
        criterion = _optional_float(observation.get("threshold_or_comparator"))
        comparison = str(observation.get("_comparison") or "")
        if measured is None:
            items.append(
                {
                    "axis_id": axis_id,
                    "label": label,
                    "status": "evidence_missing",
                    "measured_value": None,
                    "display_value": "분석 근거 없음",
                    "criterion_value": None,
                    "criterion_display": None,
                    "comparison": None,
                    "delta_value": None,
                    "delta_display": None,
                    "ratio_to_criterion": None,
                    "summary": missing_reason,
                    "evidence_refs": [],
                    "as_of": None,
                }
            )
            continue
        if criterion is None or not comparison:
            items.append(
                {
                    "axis_id": axis_id,
                    "label": label,
                    "status": "criterion_missing",
                    "measured_value": measured,
                    "display_value": str(observation.get("display_value") or measured),
                    "criterion_value": None,
                    "criterion_display": None,
                    "comparison": comparison or None,
                    "delta_value": None,
                    "delta_display": None,
                    "ratio_to_criterion": None,
                    "summary": f"{label} 값은 관측됐지만 review 기준이 설정되지 않았습니다.",
                    "evidence_refs": list(observation.get("evidence_refs") or []),
                    "as_of": observation.get("as_of"),
                }
            )
            continue
        if criterion == 0:
            raise ValueError(f"zero review criterion is invalid for {axis_id}")
        favorable = _criterion_favorable(measured, criterion, comparison)
        delta = round(abs(measured) - abs(criterion), 4)
        criterion_display = _criterion_display(axis_id, criterion)
        delta_display = _delta_display(axis_id, delta, favorable=favorable)
        criterion_prefix = "관리선" if axis_id == "drawdown" else "기준"
        items.append(
            {
                "axis_id": axis_id,
                "label": label,
                "status": "within_limit" if favorable else "exceeds_limit",
                "measured_value": measured,
                "display_value": str(observation.get("display_value") or measured),
                "criterion_value": criterion,
                "criterion_display": criterion_display,
                "comparison": comparison,
                "delta_value": round(delta * 100.0, 4) if axis_id == "turnover" else delta,
                "delta_display": delta_display,
                "ratio_to_criterion": round(abs(measured) / abs(criterion), 4),
                "summary": f"{criterion_prefix} {criterion_display} 대비 {delta_display}",
                "evidence_refs": list(observation.get("evidence_refs") or []),
                "as_of": observation.get("as_of"),
            }
        )
    return {"items": items}
```

In `build_final_review_decision_brief`, replace `trait_map` with:

```python
"character_profile": _build_character_profile(internal_observations),
"review_pressure": _build_review_pressure(internal_observations),
```

- [x] **Step 5: Run GREEN and focused Python regression**

Run:

```bash
.venv/bin/python -m unittest tests.test_backtest_final_review_decision_brief -v
.venv/bin/python -m py_compile app/services/backtest_final_review_decision_brief.py
git diff --check
```

Expected: 22 Decision Brief tests pass; compile and diff check exit 0.

- [x] **Step 6: Commit the Python contract unit**

Stage only the service and Decision Brief tests, confirm the protected registry is absent from cached names, then commit:

```bash
git commit -m "Final Review 실제 성격과 관리 압력 계약 도입"
```

## Task 9.2: React And Streamlit Presentation Separation

**Files:**
- Create: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharacter.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts`
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `tests/test_final_review_market_context_visual_contract.py`
- Modify: tracked `frontend/build/` after GREEN.

**Interfaces:**
- Consumes: `DecisionBrief.character_profile.items: CharacterProfileItem[]`.
- Consumes: `DecisionBrief.review_pressure.items: ReviewPressureItem[]`.
- Produces: `DecisionBriefCharacter({ characterItems, pressureItems })`.
- Removes: `TraitAxis`, `splitMeasuredSegments`, `PortfolioTraitMap`, `brief.trait_map`.

- [x] **Step 1: Write failing React/fallback source-contract tests**

Replace `test_final_review_trait_map_breaks_on_unmeasured_axis` in `tests/test_service_contracts.py` with:

```python
def test_final_review_character_ui_separates_actual_values_from_review_pressure(self) -> None:
    workspace = Path(
        "app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx"
    ).read_text(encoding="utf-8")
    character = Path(
        "app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharacter.tsx"
    ).read_text(encoding="utf-8")
    charts = Path(
        "app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx"
    ).read_text(encoding="utf-8")

    self.assertIn("<PortfolioCharacterSection", workspace)
    self.assertIn("포트폴리오 실제 성격", character)
    self.assertIn("관리 기준 대비 압력", character)
    self.assertIn("기준 미설정", character)
    self.assertIn("분석 근거 없음", character)
    self.assertNotIn("PortfolioTraitMap", workspace + charts)
    self.assertNotIn("splitMeasuredSegments", charts)
```

Update the reading-order test token from `<PortfolioTraitMap` to `<PortfolioCharacterSection`. Update fallback parity tokens to require `character_profile` and `review_pressure`, and forbid `trait_map` in the fallback body.

Add to `tests/test_final_review_market_context_visual_contract.py`:

```python
CHARACTER = FINAL_REVIEW_ROOT / "DecisionBriefCharacter.tsx"

def test_character_profile_keeps_market_context_layout_and_responsive_order(self) -> None:
    source = CHARACTER.read_text(encoding="utf-8")
    style = STYLE.read_text(encoding="utf-8")

    self.assertIn("db-character-layout", source + style)
    self.assertIn("db-character-list", source + style)
    self.assertIn("db-pressure-list", source + style)
    self.assertIn("grid-template-columns: minmax(0, 1.08fr) minmax(320px, .92fr);", style)
    self.assertIn(".db-character-layout", style.split("@media (max-width: 760px)", 1)[1])
    self.assertNotIn("83.3 / 100", source)
```

- [x] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_character_ui_separates_actual_values_from_review_pressure \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_react_source_has_approved_reading_order \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_fallback_uses_same_decision_brief_sections \
  tests.test_final_review_market_context_visual_contract.FinalReviewMarketContextVisualContractTests.test_character_profile_keeps_market_context_layout_and_responsive_order -v
```

Expected: failures/errors because `DecisionBriefCharacter.tsx`, new section token and fallback fields do not exist and old radar remains.

- [x] **Step 3: Replace TypeScript trait types with the approved contract**

In `decisionBriefTypes.ts`, delete `TraitAxis` and `trait_map`; add:

```tsx
export type CharacterProfileItem = {
  axis_id: string
  label: string
  measurement_status: "observed" | "evidence_missing"
  measured_value: number | null
  display_value: string
  unit: "percent" | "ratio_percent" | "bps" | "text"
  interpretation: string
  evidence_refs: string[]
  as_of: string | null
}

export type ReviewPressureItem = {
  axis_id: string
  label: string
  status: "within_limit" | "exceeds_limit" | "criterion_missing" | "evidence_missing"
  measured_value: number | null
  display_value: string
  criterion_value: number | null
  criterion_display: string | null
  comparison: "less_or_equal" | "absolute_less_or_equal" | "greater_or_equal" | null
  delta_value: number | null
  delta_display: string | null
  ratio_to_criterion: number | null
  summary: string
  evidence_refs: string[]
  as_of: string | null
}
```

Add to `DecisionBrief`:

```tsx
character_profile: { items: CharacterProfileItem[] }
review_pressure: { items: ReviewPressureItem[] }
```

- [x] **Step 4: Create the focused character presentation owner**

Create `DecisionBriefCharacter.tsx`:

```tsx
import React from "react"
import { CharacterProfileItem, ReviewPressureItem } from "./decisionBriefTypes"

const PRESSURE_LABELS: Record<ReviewPressureItem["status"], string> = {
  within_limit: "기준 이내",
  exceeds_limit: "기준 초과",
  criterion_missing: "기준 미설정",
  evidence_missing: "분석 근거 없음",
}

export function DecisionBriefCharacter({
  characterItems,
  pressureItems,
}: {
  characterItems: CharacterProfileItem[]
  pressureItems: ReviewPressureItem[]
}) {
  return (
    <div className="db-character-layout">
      <section className="db-character-panel" aria-labelledby="db-character-profile-title">
        <div className="db-character-panel-heading">
          <p className="db-kicker">Observed character</p>
          <h3 id="db-character-profile-title">포트폴리오 실제 성격</h3>
          <p>저장된 관측값을 기준 유무와 관계없이 먼저 읽습니다.</p>
        </div>
        <div className="db-character-list">
          {characterItems.map((item) => (
            <article key={item.axis_id} className={`db-character-card is-${item.measurement_status}`}>
              <span>{item.label}</span>
              <strong>{item.display_value}</strong>
              <p>{item.interpretation}</p>
              <small>{item.as_of ? `기준일 ${item.as_of}` : "저장된 기준일 없음"}</small>
            </article>
          ))}
        </div>
      </section>
      <section className="db-pressure-panel" aria-labelledby="db-review-pressure-title">
        <div className="db-character-panel-heading">
          <p className="db-kicker">Review pressure</p>
          <h3 id="db-review-pressure-title">관리 기준 대비 압력</h3>
          <p>점수가 아니라 저장된 review criterion과의 차이입니다.</p>
        </div>
        <div className="db-pressure-list">
          {pressureItems.map((item) => (
            <article key={item.axis_id} className={`db-pressure-row is-${item.status}`}>
              <div>
                <span>{item.label}</span>
                <strong>{PRESSURE_LABELS[item.status]}</strong>
              </div>
              <p>{item.summary}</p>
              {item.criterion_display && (
                <small>관측 {item.display_value} · 기준 {item.criterion_display}</small>
              )}
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
```

- [x] **Step 5: Wire the workspace and remove the radar**

In `DecisionBriefWorkspace.tsx`, replace the chart import and section function with:

```tsx
import { DecisionBriefCharacter } from "./DecisionBriefCharacter"

function PortfolioCharacterSection({ brief }: { brief: DecisionBrief }) {
  return (
    <section className="db-section db-character" aria-labelledby="db-character-title">
      <SectionHeading
        eyebrow="Portfolio character"
        title="포트폴리오 성격"
        detail="실제 관측값과 관리 기준 대비 상태를 분리해 읽습니다."
      />
      <DecisionBriefCharacter
        characterItems={brief.character_profile.items}
        pressureItems={brief.review_pressure.items}
      />
    </section>
  )
}
```

Replace `<PortfolioTraitMap brief={decisionBrief} />` with `<PortfolioCharacterSection brief={decisionBrief} />`. In `DecisionBriefCharts.tsx`, delete `TraitAxis` import and all code from `splitMeasuredSegments` through `PortfolioTraitMap`; keep cumulative and underwater chart code unchanged.

- [x] **Step 6: Implement responsive visual contract**

Delete `.db-trait-*` radar/list rules and add:

```css
.db-character-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(320px, .92fr);
  gap: 14px;
}

.db-character-panel,
.db-pressure-panel {
  min-width: 0;
  padding: 18px;
  border: 1px solid #dae4ee;
  border-radius: 17px;
  background: linear-gradient(145deg, #fff 0%, #f8fbfd 100%);
}

.db-character-list,
.db-pressure-list {
  display: grid;
  gap: 9px;
  margin-top: 15px;
}

.db-character-list {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.db-character-card,
.db-pressure-row {
  min-width: 0;
  padding: 13px 14px;
  border: 1px solid #e1e8f0;
  border-radius: 14px;
  background: rgba(255, 255, 255, .88);
}

.db-character-card strong {
  display: block;
  margin-top: 5px;
  color: #152033;
  font-size: 20px;
}

.db-pressure-row > div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.db-pressure-row.is-within_limit strong { color: #17695e; }
.db-pressure-row.is-exceeds_limit strong { color: #a24d19; }
.db-pressure-row.is-criterion_missing strong,
.db-pressure-row.is-evidence_missing strong { color: #647589; }
```

At `max-width: 760px`, set `.db-character-layout { grid-template-columns: 1fr; }`. At `max-width: 460px`, set `.db-character-list { grid-template-columns: 1fr; }`. Apply `overflow-wrap: anywhere` to card copy and values.

- [x] **Step 7: Synchronize the Streamlit fallback**

In `_render_final_review_decision_brief_fallback`, replace `trait_map` and its dataframe with:

```python
character_profile = dict(decision_brief.get("character_profile") or {})
review_pressure = dict(decision_brief.get("review_pressure") or {})

st.markdown("##### 포트폴리오 실제 성격")
character_rows = [
    {
        "특성": row.get("label"),
        "관측값": row.get("display_value"),
        "상태": "관측됨" if row.get("measurement_status") == "observed" else "분석 근거 없음",
        "의미": row.get("interpretation"),
        "기준일": row.get("as_of") or "-",
    }
    for row in list(character_profile.get("items") or [])
]
st.dataframe(pd.DataFrame(character_rows), width="stretch", hide_index=True)

st.markdown("##### 관리 기준 대비 압력")
pressure_rows = [
    {
        "특성": row.get("label"),
        "상태": row.get("status"),
        "관측값": row.get("display_value"),
        "관리 기준": row.get("criterion_display") or "기준 미설정",
        "해석": row.get("summary"),
    }
    for row in list(review_pressure.get("items") or [])
]
st.dataframe(pd.DataFrame(pressure_rows), width="stretch", hide_index=True)
```

- [x] **Step 8: Run GREEN, focused regression and production build**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
npm run build --prefix app/web/components/final_review_investment_report/frontend
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py
git diff --check
```

Expected: 120 focused tests pass, Vite transforms 177 modules after adding the new component, compile and diff check exit 0.

- [x] **Step 9: Commit the presentation unit**

Stage only React source, fallback, related tests and tracked build output. Verify registry/run history/screenshots are excluded, then commit:

```bash
git commit -m "Final Review 실제 성격과 관리 압력 UI 분리"
```

## Task 9.3: Current GRS Browser QA And Documentation Closeout

**Files:**
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: root `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md`
- Generated only: `qa-final-review-character-pressure-760.png`

**Interfaces:**
- Verifies current Python payload and React/fallback presentation; no new product contract.

- [x] **Step 1: Run desktop Browser QA on the current GRS candidate**

Open `Backtest > Final Review` without clicking the save CTA. Verify:

- `포트폴리오 실제 성격` appears before `관리 기준 대비 압력` and before `실제 강점과 약점`;
- character values show `100.00%`, `-12.43%`, `3.20%`, `10.00 bps` and only regime shows `분석 근거 없음`;
- concentration shows `기준 초과`, drawdown shows `기준 이내`, turnover/cost show `기준 미설정`, regime shows `분석 근거 없음`;
- no `83.3 / 100`, radar polygon, aggregate score or generic `미측정` remains in the character section;
- chart hover and prior Final Review decision controls still work.

- [x] **Step 2: Run 760px responsive Browser QA**

Set temporary viewport to `760×900`, verify component/document horizontal overflow is 0, character panel precedes pressure panel in one column, character cards remain 2 columns until 460px, long summaries wrap, and decision controls remain visible. Save `qa-final-review-character-pressure-760.png` as a generated artifact, then reset viewport. Do not click Final Review save.

- [x] **Step 3: Synchronize durable and task documentation**

Record:

- `STATUS.md`: 3-slice completion and commit ids;
- `NOTES.md`: raw measurement vs criterion semantics, drawdown alias, cost assumption non-limit;
- `RUNS.md`: RED/GREEN output, focused count, build, desktop/760 QA;
- `RISKS.md`: regime evidence remains unavailable; turnover/cost criterion remains intentionally unset;
- `BACKTEST_UI_FLOW.md`: actual character appears independently of review criterion, pressure is a separate comparison surface;
- root logs: 3–5 line milestone and next review location only.

- [x] **Step 4: Run fresh completion verification**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
npm run build --prefix app/web/components/final_review_investment_report/frontend
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py
git diff --check
git status --short
```

Expected: 120 tests pass, Vite transforms 177 modules, compile/diff check exit 0; only protected registry, run history and generated artifacts remain outside the staged doc set.

- [x] **Step 5: Commit closeout docs**

Stage only the listed docs, verify protected/generated paths are excluded, then commit:

```bash
git commit -m "Final Review 실제 성격 QA와 문서 동기화"
```

## Portfolio Character Plan Self-Review

- [x] DESIGN의 actual character, review pressure, status taxonomy, alias, non-goals가 모두 task와 test에 연결된다.
- [x] Python function names, payload field names, TypeScript types와 React props가 일치한다.
- [x] `decisionBriefTypes.ts`와 새 `DecisionBriefCharacter.tsx`의 실제 경로가 file map과 code step에서 일치한다.
- [x] raw drawdown은 signed value를 유지하고 comparison/delta는 magnitude 기준이라는 규칙이 Python helper와 test에 반영된다.
- [x] cost `one_way_cost_bps` non-limit, turnover/cost criterion missing, regime evidence missing을 각각 별도 test/QA로 고정한다.
- [x] radar/normalized score 제거, fallback parity, Market Context visual family와 760px responsive QA가 포함된다.
- [x] Gate, route, persistence, Monitoring, provider/replay/DB, registry rewrite가 범위 밖으로 고정된다.
- [x] Python contract, presentation, closeout이 서로 독립적으로 검토·커밋 가능한 세 단위다.
- [x] 새 PLAN 구간에 `TBD`, `TODO`, 구체화되지 않은 error handling 또는 정의되지 않은 함수 참조가 없다.

---

# Final Review Monitoring Change Condition Producer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. This work stays inline in the existing worktree; do not create a new task, worktree, or sub-agent.

**Goal:** 현재 GRS에 이미 저장된 낙폭·Benchmark 관측과 explicit comparator를 Final Review의 구조화된 Monitoring 변화 조건으로 투영해 empty state를 제거한다.

**Architecture:** `app/services/backtest_final_review_decision_brief.py`가 stored complete `review_trigger_details`를 우선 소비하고, 부족할 때 이미 생성한 internal observation에서 drawdown과 Benchmark 조건을 파생한다. React와 Streamlit fallback은 기존 `monitoring_conditions` contract를 그대로 표시하며 registry row를 재작성하지 않는다.

**Tech Stack:** Python 3.12, `unittest`, Streamlit, React/TypeScript tracked production bundle, in-app Browser QA.

## Global Constraints

- 기존 `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` row를 수정·stage·commit하지 않는다.
- `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, saved JSONL, QA screenshot을 stage하지 않는다.
- CAGR/Data Trust에 임의 threshold를 만들거나 문장형 trigger에서 숫자를 파싱하지 않는다.
- Final Review에서 provider fetch, replay, DB ingestion, save CTA 실행을 하지 않는다.
- current strengths/weaknesses observation을 Monitoring으로 이동시켜 비우지 않는다.
- Gate, canonical route, score, persistence schema version은 변경하지 않는다.

---

## Task 10.1: Python Monitoring Condition Producer

**Files:**

- Modify: `app/services/backtest_final_review_decision_brief.py`
- Modify: `tests/test_backtest_final_review_decision_brief.py`

**Interfaces:**

- Consumes: `_build_behavior_board()`의 `internal_observations`, `behavior_board["period"]`, `paper_observation.review_trigger_details`, `paper_observation.review_cadence`.
- Produces:

```python
def _build_monitoring_conditions(
    *,
    paper_observation: dict[str, Any],
    observations: list[dict[str, Any]],
    behavior_period: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    ...
```

- Stable derived ids:
  - `monitoring:drawdown-breach`
  - `monitoring:benchmark-underperformance`
- Complete condition fields remain `observation_id`, `root_issue_id`, `title`, `interpretation`, `measured_value`, `display_value`, `threshold_or_comparator`, `evidence_refs`, `as_of`, `observation`, `threshold`, `cadence`, `re_review_action`, `primary_role`.

- [x] **Step 1: Add the current production-shape helper and failing tests**

Add:

```python
def _current_monitoring_inputs(self) -> dict[str, object]:
    inputs = self._current_character_inputs()
    paper = inputs["paper_observation"]
    paper.pop("review_trigger_details", None)
    paper.update(
        {
            "review_cadence": "monthly_or_rebalance_review",
            "review_triggers": [
                "CAGR deterioration review",
                "MDD expansion review",
                "Benchmark-relative underperformance review",
                "Data Trust refresh review",
            ],
        }
    )
    return inputs
```

Add three tests:

```python
def test_current_grs_derives_drawdown_and_benchmark_monitoring_conditions(self) -> None:
    brief = self._build(self._current_monitoring_inputs())
    conditions = {
        row["observation_id"]: row for row in brief["monitoring_conditions"]
    }

    self.assertEqual(
        set(conditions),
        {
            "monitoring:drawdown-breach",
            "monitoring:benchmark-underperformance",
        },
    )
    drawdown = conditions["monitoring:drawdown-breach"]
    self.assertEqual(drawdown["measured_value"], -12.43)
    self.assertEqual(drawdown["threshold_or_comparator"], -15.0)
    self.assertEqual(drawdown["cadence"], "월간 또는 리밸런싱 시점")
    self.assertIn("-15.00%", drawdown["threshold"])
    self.assertEqual(drawdown["evidence_refs"], ["behavior_board.underwater_series"])
    benchmark = conditions["monitoring:benchmark-underperformance"]
    self.assertEqual(benchmark["threshold_or_comparator"], 0.0)
    self.assertIn("0.00%p 이하", benchmark["threshold"])
    self.assertEqual(
        benchmark["evidence_refs"],
        ["behavior_board.cumulative_series", "behavior_board.benchmark_series"],
    )
```

```python
def test_derived_monitoring_conditions_preserve_current_findings(self) -> None:
    brief = self._build(self._current_monitoring_inputs())
    findings = {
        row["observation_id"] for row in [*brief["strengths"], *brief["weaknesses"]]
    }

    self.assertIn("drawdown-recovery-path", findings)
    self.assertIn("benchmark-relative-terminal", findings)
    self.assertIn("concentration-pressure", findings)
```

```python
def test_monitoring_producer_does_not_invent_cagr_or_data_trust_thresholds(self) -> None:
    brief = self._build(self._current_monitoring_inputs())
    serialized = json.dumps(brief["monitoring_conditions"], ensure_ascii=False)

    self.assertNotIn("CAGR", serialized)
    self.assertNotIn("Data Trust", serialized)
    self.assertNotIn("deterioration", serialized)
```

- [x] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_current_grs_derives_drawdown_and_benchmark_monitoring_conditions \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_derived_monitoring_conditions_preserve_current_findings \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_monitoring_producer_does_not_invent_cagr_or_data_trust_thresholds
```

Expected: first test fails because current production-shaped input yields zero conditions. The finding test may pass before implementation; if so, keep it as a regression guard and verify the first test is the required RED.

- [x] **Step 3: Add cadence normalization and complete stored-row adapter**

Add:

```python
def _monitoring_cadence(
    paper_observation: dict[str, Any],
    behavior_period: dict[str, Any],
) -> str:
    stored = str(paper_observation.get("review_cadence") or "").strip()
    labels = {
        "monthly_or_rebalance_review": "월간 또는 리밸런싱 시점",
        "monthly": "월간",
        "quarterly": "분기",
        "rebalance": "리밸런싱 시점",
    }
    if stored:
        return labels.get(stored, stored)
    frequency = str(behavior_period.get("frequency") or "").strip().lower()
    return {"monthly": "월간", "quarterly": "분기"}.get(frequency, "")
```

Refactor the current `review_trigger_details` loop into a helper that returns a complete condition or `None`. Keep incomplete stored detail titles in `unstructured_monitoring_triggers`.

- [x] **Step 4: Derive the two safe conditions**

Index observations by `observation_id`. When the required numeric value/comparator/comparison, cadence, evidence refs, and as-of exist, build:

```python
{
    "observation_id": "monitoring:drawdown-breach",
    "root_issue_id": None,
    "title": "낙폭 관리선 이탈 재검토",
    "interpretation": "최대 낙폭이 관리선을 벗어나면 손실 감내 조건과 계속 추적 thesis를 다시 검토합니다.",
    "measured_value": drawdown["measured_value"],
    "display_value": drawdown["display_value"],
    "threshold_or_comparator": drawdown["threshold_or_comparator"],
    "evidence_refs": drawdown["evidence_refs"],
    "as_of": drawdown["as_of"],
    "observation": f"현재 최대 underwater 낙폭 {drawdown['display_value']}",
    "threshold": f"최대 낙폭이 {criterion_display} 관리선을 벗어남",
    "cadence": cadence,
    "re_review_action": "손실 감내 조건과 계속 추적 thesis를 다시 검토합니다.",
    "primary_role": "monitoring",
}
```

and:

```python
{
    "observation_id": "monitoring:benchmark-underperformance",
    "root_issue_id": None,
    "title": "Benchmark 상대 성과 재검토",
    "interpretation": "동일 기간 상대 성과가 0%p 이하로 내려가면 Benchmark 대비 추적 가치를 다시 검토합니다.",
    "measured_value": benchmark["measured_value"],
    "display_value": benchmark["display_value"],
    "threshold_or_comparator": benchmark["threshold_or_comparator"],
    "evidence_refs": benchmark["evidence_refs"],
    "as_of": benchmark["as_of"],
    "observation": f"현재 동일 기간 Benchmark 상대 성과 {benchmark['display_value']}",
    "threshold": "동일 기간 Benchmark 상대 성과가 0.00%p 이하",
    "cadence": cadence,
    "re_review_action": "Benchmark 대비 추적 가치와 최종 route를 다시 검토합니다.",
    "primary_role": "monitoring",
}
```

Use a canonical id set to prevent duplicate stored/derived conditions. Stored complete details remain first. Keep the four-condition cap.

- [x] **Step 5: Wire the builder**

Change:

```python
projected_conditions, unstructured_triggers = _build_monitoring_conditions(
    paper_observation=paper_observation,
    observations=internal_observations,
    behavior_period=_as_dict(behavior_board.get("period")),
)
```

Do not change React types, fallback, snapshot schema, Gate, route, or persistence.

- [x] **Step 6: Run GREEN and focused regression**

Run:

```bash
.venv/bin/python -m unittest tests.test_backtest_final_review_decision_brief
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review/page.py
git diff --check
```

Expected: Decision Brief 26 tests and full focused suite 123 tests pass.

- [x] **Step 7: Commit the producer**

Stage only service and its contract test:

```bash
git add \
  app/services/backtest_final_review_decision_brief.py \
  tests/test_backtest_final_review_decision_brief.py
git diff --cached --name-only
git diff --cached --check
git commit -m "Final Review Monitoring 변화 조건 생성"
```

## Task 10.2: Current GRS Browser QA And Closeout

**Files:**

- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: root `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md`
- Generated only: `qa-final-review-monitoring-conditions-760.png`

**Interfaces:**

- Consumes unchanged React `MonitoringConditions` component and new Python payload.
- Produces no new product API.

- [ ] **Step 1: Run current GRS desktop Browser QA**

Restart the Streamlit process after Python contract changes. Open `Backtest > Final Review`, do not click the save CTA, and verify:

- empty state is absent;
- `낙폭 관리선 이탈 재검토` and `Benchmark 상대 성과 재검토` are visible;
- each card shows 변화 조건, 확인 주기, 재검토 행동;
- strengths still show drawdown/Benchmark and weakness still shows concentration;
- Final Review route/reason controls remain visible.

- [ ] **Step 2: Run 760px QA**

Set viewport `760×900`, verify the two condition cards fit without horizontal overflow or clipped copy, capture `qa-final-review-monitoring-conditions-760.png`, and reset the viewport. Treat the screenshot as generated and do not stage it.

- [x] **Step 3: Synchronize task and durable docs**

Record the production contract gap, derived-condition policy, verification results, commit ids, and residuals. Do not mark CAGR/Data Trust as implemented conditions.

- [x] **Step 4: Run fresh completion verification**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
npm run build --prefix app/web/components/final_review_investment_report/frontend
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py
git diff --check
git status --short
```

Expected: 123 focused tests, 177-module production build, compile/diff check exit 0; only protected registry, run history, `.superpowers`, and generated QA artifacts remain unstaged.

- [x] **Step 5: Commit closeout docs**

Stage only the listed docs and commit:

```bash
git commit -m "Final Review Monitoring 조건 QA와 문서 동기화"
```

## Monitoring Producer Plan Self-Review

- [x] production root cause and current stored input shape are reflected in tests.
- [x] complete stored detail priority and derived fallback order are explicit.
- [x] drawdown and Benchmark mappings use existing observations and comparators.
- [x] current findings are preserved by separate monitoring stable ids.
- [x] CAGR/Data Trust arbitrary threshold and prose number parsing are prohibited.
- [x] registry rewrite, provider/replay/DB, Gate/route/score changes are excluded.
- [x] RED/GREEN commands, focused counts, Browser QA, commit boundaries are concrete.
- [x] no undefined function, placeholder, `TBD`, or incomplete error policy remains.

---

# Final Review Observation Freshness Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task in the current approved worktree. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Final Review에서 현재 후보의 누적 성과와 underwater 관측 기간이 오래됐을 때 Level2로 이동하지 않고, 한 번의 사용자 action으로 기존 가격 수집 → 동일 전략 replay → 새 Practical Validation append → 최신 chart 재선택을 완료한다.

**Architecture:** 새 Python service가 source-specific freshness read model과 갱신 orchestration을 소유한다. 기존 price refresh / Practical Validation replay / validation builder / append writer를 dependency-injected adapter로 재사용하고, Decision Brief는 compact freshness projection과 selected-route-only Gate를 제공한다. React는 freshness 상태를 표시하고 `refresh_observation` intent만 보내며 Streamlit Python이 stable identity, 실행, 저장, rerun을 담당한다.

**Tech Stack:** Python 3.12, pandas, Streamlit, unittest, React 18, TypeScript, Vite, append-only JSONL registry.

## 이걸 하는 이유?

current GRS의 stored replay curve는 `2026-06-26`에서 끝나지만 현재 최신 완료 NYSE session은 `2026-07-15`다. DB의 BIL 가격이 `2026-06-26`에 머물러 있어 replay만으로는 관측 기간이 늘어나지 않는다. 사용자가 Final Review에서 같은 후보를 판단하다가 이 문제만을 위해 Practical Validation Flow 2로 이동하는 것은 불필요한 단계 회귀이므로, Final Review 안에서 명시적으로 요청한 최신화만 Python orchestration 예외로 허용한다.

## Global Constraints

- worktree는 `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev`, branch는 `codex/backtest-dev`를 그대로 사용한다.
- 새 task, 새 phase, 새 worktree를 만들지 않는다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`의 현재 사용자 변경을 stage, commit, rewrite, delete하지 않는다.
- `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`을 stage 또는 commit하지 않는다.
- generated screenshot, browser artifact, `.superpowers/`를 commit하지 않는다.
- registry 기존 row를 수정하지 않고 새 validation만 append한다.
- Browser QA에서 실제 refresh 또는 Final Review save를 눌러 protected registry에 row를 쓰지 않는다.
- historical universe / delisting provider, background scheduler, live approval, broker order, account sync, auto rebalance는 범위 밖이다.
- React는 presentation과 intent만 담당한다. 날짜 판정, symbol freshness, ingestion, replay, Gate, validation build, append는 Python이 소유한다.
- 월간 GRS latest valuation row는 signal / rebalance row와 분리해 가짜 rebalance를 만들지 않는다.

## File Structure And Interfaces

### New Python owner

- Create: `app/services/backtest_final_review_refresh.py`
  - source / validation stable identity 확인
  - stored curve end / latest completed market date / DB common date / limiting symbol projection
  - price refresh meta adapter
  - price refresh → replay → validation build → Gate → append orchestration
  - partial / failure / retry result contract

### Existing Python owners to modify

- Modify: `app/services/backtest_price_refresh.py`
  - `latest_completed_nyse_session()` public wrapper 추가
- Modify: `app/services/backtest_practical_validation_replay.py`
  - `replay_component_symbols()` public helper
  - `build_replay_market_date_contract(..., freshness_loader=...)`
  - `symbol_latest_dates`, `stale_symbols` projection
- Modify: `app/services/backtest_final_review_decision_brief.py`
  - `observation_freshness` payload
  - refresh 가능한 stale 상태에서 selected route만 recordable false
  - `can_refresh_observation` capability
- Modify: `app/web/backtest_final_review_helpers.py`
  - authoritative save evaluation에 optional freshness selected-route guard
- Modify: `app/web/backtest_final_review/page.py`
  - refresh status build
  - session result merge
  - refresh intent stable identity / duplicate guard / spinner / rerun
  - fallback freshness action
- Modify: `app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts`
  - freshness payload와 `RefreshObservationIntent`
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
  - chart 위 compact freshness strip
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
  - Market Context 계열 responsive freshness layout

### Test owners

- Create: `tests/test_backtest_final_review_refresh.py`
- Modify: `tests/test_backtest_final_review_decision_brief.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `tests/test_final_review_market_context_visual_contract.py`

### Stable interfaces

```python
def latest_completed_nyse_session(now: datetime | None = None) -> date:
    """Return the latest NYSE session whose regular or early close has completed."""
```

```python
def replay_component_symbols(source: dict[str, Any]) -> list[str]:
    """Return the active symbols required by the existing replay contract."""
```

```python
def build_replay_market_date_contract(
    source: dict[str, Any],
    *,
    requested_end: Any | None = None,
    freshness_loader: Callable[..., pd.DataFrame] | None = None,
) -> dict[str, Any]:
    """Return source-specific common coverage and per-symbol latest dates."""
```

```python
def build_final_review_refresh_status(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    now: datetime | None = None,
    freshness_loader: Callable[..., pd.DataFrame] | None = None,
) -> dict[str, Any]:
    """Build a read-only observation freshness model for one current validation."""
```

```python
def run_final_review_observation_refresh(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    now: datetime | None = None,
    freshness_loader: Callable[..., pd.DataFrame] | None = None,
    price_refresh_runner: Callable[..., Mapping[str, Any]] | None = None,
    replay_runner: Callable[..., dict[str, Any]] | None = None,
    validation_builder: Callable[..., dict[str, Any]] | None = None,
    validation_saver: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Refresh stored observations and append a new validation only after a safe replay."""
```

Freshness payload:

```python
{
    "schema_version": "final_review_observation_freshness_v1",
    "status": "up_to_date | replay_available | price_refresh_available | partial_refresh | blocked",
    "tone": "positive | warning | danger | neutral",
    "label": "최신 | 재계산 가능 | 가격 최신화 필요 | 일부 최신화 | 갱신 불가",
    "summary": str,
    "detail": str,
    "selection_source_id": str,
    "validation_id": str,
    "stored_curve_end": str | None,
    "latest_completed_market_date": str | None,
    "db_common_price_date": str | None,
    "refresh_target_date": str | None,
    "limiting_symbols": list[str],
    "stale_symbols": list[str],
    "missing_symbols": list[str],
    "provider_gap_symbols": list[str],
    "refreshable_symbols": list[str],
    "can_refresh": bool,
    "selection_blocked": bool,
    "button_label": "최신 데이터로 다시 계산",
}
```

Refresh result:

```python
{
    "schema_version": "final_review_observation_refresh_result_v1",
    "status": "refreshed | partial_refresh | up_to_date | blocked | failed | failed_after_price_refresh",
    "message": str,
    "selection_source_id": str,
    "previous_validation_id": str,
    "new_validation_id": str | None,
    "previous_curve_end": str | None,
    "refreshed_curve_end": str | None,
    "target_market_date": str | None,
    "db_common_price_date": str | None,
    "limiting_symbols": list[str],
    "provider_gap_symbols": list[str],
    "price_refresh_executed": bool,
    "price_rows_written": int,
    "replay_executed": bool,
    "validation_saved": bool,
}
```

## 1차: Freshness Truth And Selected-Route Gate

### Task 11.1: source-specific freshness model과 public date adapter

**Files:**

- Create: `tests/test_backtest_final_review_refresh.py`
- Create: `app/services/backtest_final_review_refresh.py`
- Modify: `app/services/backtest_price_refresh.py`
- Modify: `app/services/backtest_practical_validation_replay.py`

**Interfaces:**

- Consumes: current validation의 `selection_source_snapshot`, `curve_evidence.replay_attempt.portfolio_curve`, `observation_refresh_snapshot`
- Produces: `latest_completed_nyse_session`, `replay_component_symbols`, `build_final_review_refresh_status`

- [ ] **Step 1: Write the failing freshness tests**

Create `tests/test_backtest_final_review_refresh.py` with reusable fixtures and the first five contracts:

```python
from __future__ import annotations

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd


ET = ZoneInfo("America/New_York")


def source_fixture() -> dict[str, object]:
    return {
        "selection_source_id": "selection-grs-current",
        "source_kind": "single_candidate",
        "period": {"actual_start": "2016-01-29", "actual_end": "2026-06-26"},
        "components": [
            {
                "component_id": "grs",
                "title": "Global Relative Strength",
                "target_weight": 100.0,
                "strategy_key": "global_relative_strength",
                "contract": {
                    "tickers": ["SPY", "QQQ", "GLD", "IEF", "TLT"],
                    "cash_ticker": "BIL",
                },
            }
        ],
    }


def validation_fixture(*, curve_end: str = "2026-06-26") -> dict[str, object]:
    return {
        "validation_id": "validation-grs-current",
        "selection_source_id": "selection-grs-current",
        "selection_source_snapshot": source_fixture(),
        "validation_profile": {
            "profile_id": "balanced_core",
            "answers": {"capital_priority": "balanced"},
        },
        "curve_evidence": {
            "replay_attempt": {
                "portfolio_curve": [
                    {"Date": "2016-01-29", "Total Balance": 10000.0},
                    {"Date": curve_end, "Total Balance": 53000.0},
                ]
            }
        },
    }


def freshness_frame(bil: str, others: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"symbol": "SPY", "latest_date": others, "row_count": 2500},
            {"symbol": "QQQ", "latest_date": others, "row_count": 2500},
            {"symbol": "GLD", "latest_date": others, "row_count": 2500},
            {"symbol": "IEF", "latest_date": others, "row_count": 2500},
            {"symbol": "TLT", "latest_date": others, "row_count": 2500},
            {"symbol": "BIL", "latest_date": bil, "row_count": 2500},
        ]
    )


class FinalReviewRefreshStatusTests(unittest.TestCase):
    def test_current_grs_requires_price_refresh_and_names_bil_limiter(self) -> None:
        from app.services.backtest_final_review_refresh import (
            build_final_review_refresh_status,
        )

        status = build_final_review_refresh_status(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-06-26", "2026-07-10"),
        )

        self.assertEqual(status["status"], "price_refresh_available")
        self.assertEqual(status["stored_curve_end"], "2026-06-26")
        self.assertEqual(status["latest_completed_market_date"], "2026-07-15")
        self.assertEqual(status["db_common_price_date"], "2026-06-26")
        self.assertEqual(status["limiting_symbols"], ["BIL"])
        self.assertIn("BIL", status["refreshable_symbols"])
        self.assertTrue(status["selection_blocked"])

    def test_db_common_date_newer_than_curve_requires_replay_only(self) -> None:
        from app.services.backtest_final_review_refresh import build_final_review_refresh_status

        status = build_final_review_refresh_status(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-07-15", "2026-07-15"),
        )

        self.assertEqual(status["status"], "replay_available")
        self.assertEqual(status["db_common_price_date"], "2026-07-15")
        self.assertTrue(status["can_refresh"])

    def test_curve_at_target_is_up_to_date(self) -> None:
        from app.services.backtest_final_review_refresh import build_final_review_refresh_status

        status = build_final_review_refresh_status(
            source=source_fixture(),
            validation=validation_fixture(curve_end="2026-07-15"),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-07-15", "2026-07-15"),
        )

        self.assertEqual(status["status"], "up_to_date")
        self.assertFalse(status["can_refresh"])
        self.assertFalse(status["selection_blocked"])

    def test_known_provider_gap_is_partial_not_endless_refresh(self) -> None:
        from app.services.backtest_final_review_refresh import build_final_review_refresh_status

        validation = validation_fixture()
        validation["observation_refresh_snapshot"] = {
            "target_market_date": "2026-07-15",
            "provider_gap_symbols": ["BIL"],
        }
        status = build_final_review_refresh_status(
            source=source_fixture(),
            validation=validation,
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-06-26", "2026-07-10"),
        )

        self.assertEqual(status["status"], "partial_refresh")
        self.assertEqual(status["provider_gap_symbols"], ["BIL"])
        self.assertFalse(status["can_refresh"])
        self.assertFalse(status["selection_blocked"])

    def test_missing_selection_source_contract_is_blocked(self) -> None:
        from app.services.backtest_final_review_refresh import build_final_review_refresh_status

        status = build_final_review_refresh_status(
            source={},
            validation={"validation_id": "validation-missing"},
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: pd.DataFrame(),
        )

        self.assertEqual(status["status"], "blocked")
        self.assertFalse(status["can_refresh"])
        self.assertTrue(status["selection_blocked"])
```

- [ ] **Step 2: Run RED and verify the missing service/API failure**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_refresh.FinalReviewRefreshStatusTests -v
```

Expected: `ModuleNotFoundError: No module named 'app.services.backtest_final_review_refresh'` or missing public adapter errors. The tests must not fail because of fixture syntax.

- [ ] **Step 3: Expose the latest completed session and replay symbols**

In `app/services/backtest_price_refresh.py` add:

```python
def latest_completed_nyse_session(now: datetime | None = None) -> date:
    """Return the latest NYSE session whose regular or early close has completed."""

    return _latest_completed_nyse_session(now)
```

In `app/services/backtest_practical_validation_replay.py` rename the private symbol helper through a public wrapper and inject the loader:

```python
def replay_component_symbols(source: dict[str, Any]) -> list[str]:
    """Collect only the active source tickers required by the replay runtime."""

    return _replay_component_symbols(source)
```

```python
def build_replay_market_date_contract(
    source: dict[str, Any],
    *,
    requested_end: Any | None = None,
    freshness_loader: Callable[..., pd.DataFrame] | None = None,
) -> dict[str, Any]:
    selected_loader = freshness_loader or load_price_freshness_summary
    freshness = selected_loader(
        symbols=symbols,
        end=requested_market_date,
        timeframe="1d",
    )
```

Return the additional keys:

```python
symbol_latest_dates = {
    symbol: _date_text(rows.loc[rows["symbol"] == symbol, "latest_date"].iloc[-1])
    for symbol in symbols
    if not rows.loc[rows["symbol"] == symbol, "latest_date"].empty
}
stale_symbols = [
    symbol
    for symbol in symbols
    if symbol not in symbol_latest_dates
    or (
        requested_market_date
        and symbol_latest_dates[symbol] < requested_market_date
    )
]
```

```python
{
    "symbol_latest_dates": symbol_latest_dates,
    "stale_symbols": stale_symbols,
}
```

Keep all existing market-date keys unchanged.

- [ ] **Step 4: Implement the minimal freshness service**

Create `app/services/backtest_final_review_refresh.py` with:

```python
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any

import pandas as pd

from app.services.backtest_price_refresh import latest_completed_nyse_session
from app.services.backtest_practical_validation_replay import (
    build_replay_market_date_contract,
)


FRESHNESS_SCHEMA_VERSION = "final_review_observation_freshness_v1"
REFRESH_RESULT_SCHEMA_VERSION = "final_review_observation_refresh_result_v1"


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _selection_source(
    source: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    snapshot = dict(validation.get("selection_source_snapshot") or {})
    if snapshot:
        return snapshot
    row = dict(source.get("row") or {})
    nested = dict(row.get("selection_source_snapshot") or {})
    if nested:
        return nested
    return dict(source or {})


def _stored_curve_end(validation: Mapping[str, Any]) -> str | None:
    replay = dict(dict(validation.get("curve_evidence") or {}).get("replay_attempt") or {})
    points = [
        dict(row)
        for row in list(replay.get("portfolio_curve") or [])
        if isinstance(row, Mapping)
    ]
    dates = [_date_text(row.get("Date") or row.get("date")) for row in points]
    dates = [value for value in dates if value]
    if dates:
        return max(dates)
    period = dict(replay.get("actual_period") or {})
    coverage = dict(replay.get("period_coverage") or {})
    coverage_period = dict(coverage.get("actual_period") or {})
    return _date_text(
        period.get("end")
        or coverage_period.get("end")
        or dict(validation.get("input_evidence") or {}).get("source_period", {}).get("actual_end")
    )
```

Implement `build_final_review_refresh_status()` so it:

1. resolves the selection source;
2. computes target with `latest_completed_nyse_session(now).isoformat()`;
3. calls `build_replay_market_date_contract(..., freshness_loader=freshness_loader)`;
4. subtracts same-target `observation_refresh_snapshot.provider_gap_symbols` from stale symbols;
5. returns `price_refresh_available` first when refreshable stale/missing symbols remain, even if common date is newer than curve;
6. returns `replay_available` when common date is newer than curve and no automatic price refresh target remains;
7. returns `partial_refresh` when only known provider gaps remain;
8. returns `up_to_date` when curve/common/target are aligned;
9. returns `blocked` when source, symbols, curve, or date contract is missing.

Use explicit state mapping:

```python
presentation = {
    "up_to_date": ("positive", "최신"),
    "replay_available": ("warning", "재계산 가능"),
    "price_refresh_available": ("warning", "가격 최신화 필요"),
    "partial_refresh": ("neutral", "일부 최신화"),
    "blocked": ("danger", "갱신 불가"),
}
```

Only `replay_available` and `price_refresh_available` set `can_refresh=True`. They also set `selection_blocked=True`. `partial_refresh` sets both false because no automatic refresh target remains; existing evidence closure Gate still owns critical period gaps.

- [ ] **Step 5: Run GREEN and focused replay regression**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_refresh.FinalReviewRefreshStatusTests \
  tests.test_service_contracts.PracticalValidationReplayServiceContractTests -v
```

Expected: all tests `OK`.

- [ ] **Step 6: Commit 1차**

```bash
git add \
  app/services/backtest_final_review_refresh.py \
  app/services/backtest_price_refresh.py \
  app/services/backtest_practical_validation_replay.py \
  tests/test_backtest_final_review_refresh.py
git diff --cached --check
git commit -m "Final Review 관측 최신성 계약 도입"
```

Do not stage registry, run history, screenshots, or `.superpowers/`.

## 2차: Python One-Click Refresh Orchestration

### Task 11.2: price refresh → replay → validation append

**Files:**

- Modify: `tests/test_backtest_final_review_refresh.py`
- Modify: `app/services/backtest_final_review_refresh.py`

**Interfaces:**

- Consumes: Task 11.1 freshness payload, `run_backtest_price_refresh`, `run_practical_validation_actual_replay`, `build_practical_validation_result`, `save_practical_validation_result`
- Produces: `run_final_review_observation_refresh`, compact `observation_refresh_snapshot`

- [ ] **Step 1: Write RED orchestration tests**

Append to `tests/test_backtest_final_review_refresh.py`:

```python
from unittest.mock import MagicMock


def replay_result(*, end: str = "2026-07-10", status: str = "PASS") -> dict[str, object]:
    return {
        "status": status,
        "portfolio_curve": [
            {"Date": "2016-01-29", "Total Balance": 10000.0},
            {"Date": end, "Total Balance": 54000.0},
        ],
        "period_coverage": {
            "status": "PASS",
            "actual_period": {"start": "2016-01-29", "end": end},
        },
        "market_date_contract": {
            "requested_market_date": "2026-07-15",
            "latest_common_price_date": end,
            "limiting_symbols": ["BIL"] if end < "2026-07-15" else [],
        },
    }


class FinalReviewRefreshOrchestrationTests(unittest.TestCase):
    def test_replay_available_skips_ingestion_and_appends_new_validation(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        price_runner = MagicMock()
        replay_runner = MagicMock(return_value=replay_result(end="2026-07-15"))
        validation_builder = MagicMock(
            return_value={
                "validation_id": "validation-grs-refreshed",
                "selection_source_id": "selection-grs-current",
                "final_review_gate": {"can_save_and_move": True},
            }
        )
        saver = MagicMock()

        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-07-15", "2026-07-15"),
            price_refresh_runner=price_runner,
            replay_runner=replay_runner,
            validation_builder=validation_builder,
            validation_saver=saver,
        )

        price_runner.assert_not_called()
        replay_runner.assert_called_once()
        saver.assert_called_once()
        self.assertEqual(result["status"], "refreshed")
        self.assertEqual(result["new_validation_id"], "validation-grs-refreshed")
        self.assertTrue(result["validation_saved"])

    def test_price_refresh_runs_before_replay_when_common_date_is_stale(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        frames = iter(
            [
                freshness_frame("2026-06-26", "2026-07-10"),
                freshness_frame("2026-07-15", "2026-07-15"),
            ]
        )
        price_runner = MagicMock(
            return_value={
                "status": "success",
                "rows_written": 18,
                "details": {
                    "post_refresh_unresolved_symbols": [],
                    "post_refresh_price_freshness": {"details": {"classification_rows": []}},
                },
            }
        )
        replay_runner = MagicMock(return_value=replay_result(end="2026-07-15"))
        validation_builder = MagicMock(
            return_value={
                "validation_id": "validation-grs-latest",
                "selection_source_id": "selection-grs-current",
                "final_review_gate": {"can_save_and_move": True},
            }
        )
        saver = MagicMock()

        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: next(frames),
            price_refresh_runner=price_runner,
            replay_runner=replay_runner,
            validation_builder=validation_builder,
            validation_saver=saver,
        )

        refresh_meta = price_runner.call_args.args[0]
        self.assertEqual(refresh_meta["end"], "2026-07-15")
        self.assertIn("BIL", refresh_meta["price_freshness"]["details"]["stale_symbols_all"])
        replay_runner.assert_called_once()
        saver.assert_called_once()
        self.assertEqual(result["status"], "refreshed")
        self.assertEqual(result["refreshed_curve_end"], "2026-07-15")

    def test_replay_failure_after_price_refresh_never_saves_validation(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        frames = iter(
            [
                freshness_frame("2026-06-26", "2026-07-10"),
                freshness_frame("2026-07-15", "2026-07-15"),
            ]
        )
        saver = MagicMock()
        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: next(frames),
            price_refresh_runner=MagicMock(
                return_value={"status": "success", "rows_written": 12, "details": {}}
            ),
            replay_runner=MagicMock(return_value=replay_result(status="BLOCKED")),
            validation_builder=MagicMock(),
            validation_saver=saver,
        )

        self.assertEqual(result["status"], "failed_after_price_refresh")
        self.assertFalse(result["validation_saved"])
        saver.assert_not_called()

    def test_blocked_new_validation_is_not_appended(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        saver = MagicMock()
        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-07-10", "2026-07-10"),
            price_refresh_runner=MagicMock(),
            replay_runner=MagicMock(return_value=replay_result(end="2026-07-10")),
            validation_builder=MagicMock(
                return_value={
                    "validation_id": "validation-blocked",
                    "selection_source_id": "selection-grs-current",
                    "final_review_gate": {"can_save_and_move": False},
                }
            ),
            validation_saver=saver,
        )

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["validation_saved"])
        saver.assert_not_called()

    def test_no_curve_progress_returns_partial_without_append(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        frames = iter(
            [
                freshness_frame("2026-06-26", "2026-07-10"),
                freshness_frame("2026-06-26", "2026-07-10"),
            ]
        )
        saver = MagicMock()
        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: next(frames),
            price_refresh_runner=MagicMock(
                return_value={
                    "status": "partial_success",
                    "rows_written": 5,
                    "details": {
                        "post_refresh_unresolved_symbols": ["BIL"],
                        "post_refresh_price_freshness": {
                            "details": {
                                "classification_rows": [
                                    {
                                        "symbol": "BIL",
                                        "reason": "persistent_source_gap_or_symbol_issue",
                                    }
                                ]
                            }
                        },
                    },
                }
            ),
            replay_runner=MagicMock(),
            validation_builder=MagicMock(),
            validation_saver=saver,
        )

        self.assertEqual(result["status"], "partial_refresh")
        self.assertEqual(result["provider_gap_symbols"], ["BIL"])
        self.assertFalse(result["replay_executed"])
        saver.assert_not_called()
```

- [ ] **Step 2: Run RED and verify the orchestration function is missing**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_refresh.FinalReviewRefreshOrchestrationTests -v
```

Expected: import or attribute failures for `run_final_review_observation_refresh`.

- [ ] **Step 3: Implement price refresh meta and result helpers**

In `app/services/backtest_final_review_refresh.py` add:

```python
def _price_refresh_meta(
    *,
    selection_source: Mapping[str, Any],
    freshness: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "tickers": list(freshness.get("symbols") or []),
        "symbols": list(freshness.get("symbols") or []),
        "start": dict(selection_source.get("period") or {}).get("actual_start")
        or dict(selection_source.get("period") or {}).get("start"),
        "end": freshness.get("refresh_target_date"),
        "actual_result_end": freshness.get("stored_curve_end"),
        "price_freshness": {
            "status": "warning",
            "details": {
                "common_latest_date": freshness.get("db_common_price_date"),
                "effective_end_date": freshness.get("refresh_target_date"),
                "stale_symbols_all": list(freshness.get("refreshable_symbols") or []),
                "missing_symbols_all": list(freshness.get("missing_symbols") or []),
                "refresh_symbols_all": list(freshness.get("refreshable_symbols") or []),
                "classification_rows": [],
            },
        },
    }
```

```python
def _provider_gap_symbols(result: Mapping[str, Any]) -> list[str]:
    details = dict(result.get("details") or {})
    post = dict(details.get("post_refresh_price_freshness") or {})
    rows = list(dict(post.get("details") or {}).get("classification_rows") or [])
    markers = (
        "persistent_source_gap",
        "provider_source_gap",
        "provider_no_data",
        "likely_delisted",
        "symbol_changed",
        "asset_profile_error",
        "unavailable_from_provider",
    )
    return sorted(
        {
            str(row.get("symbol") or "").strip().upper()
            for row in rows
            if isinstance(row, Mapping)
            and any(marker in str(row.get("reason") or "").lower() for marker in markers)
            and str(row.get("symbol") or "").strip()
        }
    )
```

- [ ] **Step 4: Implement the orchestration**

Select defaults lazily inside `run_final_review_observation_refresh()` to avoid import cycles:

```python
if price_refresh_runner is None:
    from app.services.backtest_price_refresh import run_backtest_price_refresh
    price_refresh_runner = run_backtest_price_refresh
if replay_runner is None:
    from app.services.backtest_practical_validation_replay import (
        run_practical_validation_actual_replay,
    )
    replay_runner = run_practical_validation_actual_replay
if validation_builder is None or validation_saver is None:
    from app.services.backtest_practical_validation import (
        build_practical_validation_result,
        save_practical_validation_result,
    )
    validation_builder = validation_builder or build_practical_validation_result
    validation_saver = validation_saver or save_practical_validation_result
```

Required execution rules:

```python
initial = build_final_review_refresh_status(
    source=source,
    validation=validation,
    now=now,
    freshness_loader=freshness_loader,
)
```

- `up_to_date`: return without runner calls.
- `blocked`: return without runner calls.
- `price_refresh_available`: call price runner with `_price_refresh_meta`, then rebuild status.
- if post-refresh common date is not later than `stored_curve_end`, return `partial_refresh` without replay/save.
- otherwise call:

```python
replay = replay_runner(
    selection_source,
    mode="extend_to_latest",
    end_override=post_status.get("refresh_target_date"),
)
```

- require replay status `PASS` or `REVIEW`, non-empty portfolio curve, and `refreshed_curve_end > previous_curve_end`.
- preserve current validation profile:

```python
profile = dict(validation.get("validation_profile") or {})
validation_profile = {
    "profile_id": profile.get("profile_id") or "balanced_core",
    "answers": dict(profile.get("answers") or {}),
}
new_validation = validation_builder(
    selection_source,
    validation_profile=validation_profile,
    replay_result=replay,
)
```

- require same `selection_source_id` and `final_review_gate.can_save_and_move=True`.
- attach before save:

```python
new_validation["observation_refresh_snapshot"] = {
    "schema_version": "final_review_observation_refresh_snapshot_v1",
    "attempted_at": datetime.now().isoformat(timespec="seconds"),
    "target_market_date": post_status.get("refresh_target_date"),
    "previous_curve_end": previous_curve_end,
    "refreshed_curve_end": refreshed_curve_end,
    "db_common_price_date": post_status.get("db_common_price_date"),
    "limiting_symbols": list(post_status.get("limiting_symbols") or []),
    "provider_gap_symbols": provider_gap_symbols,
    "price_refresh_executed": price_refresh_executed,
    "price_rows_written": price_rows_written,
}
```

- call `validation_saver(new_validation)` only after all guards.
- result status is `refreshed` when curve reaches target, otherwise `partial_refresh`.

Catch exceptions at orchestration boundaries. If price rows were already written, use `failed_after_price_refresh`; otherwise use `failed`. Never attempt DB rollback.

- [ ] **Step 5: Run GREEN and append-writer regression**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_refresh \
  tests.test_service_contracts.PracticalValidationReplayServiceContractTests \
  tests.test_service_contracts.PracticalValidationServiceContractTests -v
```

Expected: all tests `OK`.

- [ ] **Step 6: Commit 2차**

```bash
git add \
  app/services/backtest_final_review_refresh.py \
  tests/test_backtest_final_review_refresh.py
git diff --cached --check
git commit -m "Final Review 최신 관측 재계산 오케스트레이션"
```

## 3차: Decision Brief Gate And Streamlit Intent

### Task 11.3: selected-route-only Gate, stable intent, rerun

**Files:**

- Modify: `tests/test_backtest_final_review_decision_brief.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/backtest_final_review_decision_brief.py`
- Modify: `app/web/backtest_final_review_helpers.py`
- Modify: `app/web/backtest_final_review/page.py`

**Interfaces:**

- Consumes: Task 11.1 freshness status, Task 11.2 refresh result
- Produces: Decision Brief `observation_freshness`, Python refresh intent consumer, authoritative selected-route save guard

- [ ] **Step 1: Write RED Decision Brief Gate tests**

Append to `tests/test_backtest_final_review_decision_brief.py`:

```python
    def test_refreshable_stale_observation_blocks_only_selected_route(self) -> None:
        inputs = self._inputs()
        inputs["observation_freshness"] = {
            "schema_version": "final_review_observation_freshness_v1",
            "status": "price_refresh_available",
            "selection_blocked": True,
            "can_refresh": True,
            "button_label": "최신 데이터로 다시 계산",
        }

        brief = self._build(inputs)
        options = {
            row["route"]: row for row in brief["decision_action"]["options"]
        }

        self.assertEqual(
            brief["observation_freshness"]["status"],
            "price_refresh_available",
        )
        self.assertFalse(
            options["SELECT_FOR_PRACTICAL_PORTFOLIO"]["recordable"]
        )
        self.assertIn(
            "최신 데이터",
            options["SELECT_FOR_PRACTICAL_PORTFOLIO"]["disabled_reason"],
        )
        self.assertTrue(options["HOLD_FOR_MORE_PAPER_TRACKING"]["recordable"])
        self.assertTrue(options["REJECT_FOR_PRACTICAL_USE"]["recordable"])
        self.assertTrue(options["RE_REVIEW_REQUIRED"]["recordable"])
        self.assertTrue(brief["capabilities"]["can_refresh_observation"])
        self.assertFalse(brief["capabilities"]["provider_fetch"])
        self.assertFalse(brief["capabilities"]["validation_rerun"])

    def test_up_to_date_observation_keeps_selected_route_recordable(self) -> None:
        inputs = self._inputs()
        inputs["observation_freshness"] = {
            "schema_version": "final_review_observation_freshness_v1",
            "status": "up_to_date",
            "selection_blocked": False,
            "can_refresh": False,
        }

        brief = self._build(inputs)
        selected = next(
            row
            for row in brief["decision_action"]["options"]
            if row["route"] == "SELECT_FOR_PRACTICAL_PORTFOLIO"
        )

        self.assertTrue(selected["recordable"])
        self.assertFalse(brief["capabilities"]["can_refresh_observation"])
```

Update `_inputs()` so it accepts the new optional parameter through the build call:

```python
"observation_freshness": {},
```

- [ ] **Step 2: Write RED Streamlit consumer tests**

Add focused tests to the current Final Review contract class in `tests/test_service_contracts.py`:

```python
    def test_final_review_refresh_intent_runs_once_and_selects_new_validation(self) -> None:
        import app.web.backtest_final_review.page as page

        fake_st = MagicMock()
        fake_st.session_state = {}
        fake_st.rerun.side_effect = RuntimeError("rerun")
        refresh_runner = MagicMock(
            return_value={
                "status": "refreshed",
                "message": "2026-07-15까지 다시 계산했습니다.",
                "selection_source_id": "selection-a",
                "new_validation_id": "validation-new",
                "validation_saved": True,
            }
        )
        intent = {
            "action": "refresh_observation",
            "intent_id": "refresh-once",
            "source_id": "selection-a",
            "validation_id": "validation-old",
        }

        with (
            patch.object(page, "st", fake_st),
            patch.object(
                page,
                "run_final_review_observation_refresh",
                refresh_runner,
            ),
            self.assertRaisesRegex(RuntimeError, "rerun"),
        ):
            page._consume_final_review_observation_refresh_intent(
                intent,
                source={"source_id": "validation-old"},
                validation={
                    "validation_id": "validation-old",
                    "selection_source_id": "selection-a",
                    "selection_source_snapshot": {"selection_source_id": "selection-a"},
                },
                observation_freshness={
                    "can_refresh": True,
                    "selection_source_id": "selection-a",
                    "validation_id": "validation-old",
                },
            )

        refresh_runner.assert_called_once()
        self.assertEqual(
            fake_st.session_state["final_review_active_decision_brief_source_id"],
            "practical_validation_result:validation-new",
        )
        self.assertEqual(
            fake_st.session_state[
                "final_review_observation_refresh_result_selection-a"
            ]["status"],
            "refreshed",
        )

    def test_final_review_refresh_intent_rejects_stale_identity(self) -> None:
        import app.web.backtest_final_review.page as page

        fake_st = MagicMock()
        fake_st.session_state = {}
        refresh_runner = MagicMock()

        with (
            patch.object(page, "st", fake_st),
            patch.object(
                page,
                "run_final_review_observation_refresh",
                refresh_runner,
            ),
        ):
            page._consume_final_review_observation_refresh_intent(
                {
                    "action": "refresh_observation",
                    "intent_id": "refresh-stale",
                    "source_id": "selection-other",
                    "validation_id": "validation-old",
                },
                source={"source_id": "validation-old"},
                validation={
                    "validation_id": "validation-old",
                    "selection_source_id": "selection-a",
                },
                observation_freshness={"can_refresh": True},
            )

        refresh_runner.assert_not_called()
        fake_st.error.assert_called_once()

    def test_final_review_selected_save_guard_rechecks_observation_freshness(self) -> None:
        from app.web.backtest_final_review_helpers import (
            _build_final_review_save_evaluation,
        )

        result = _build_final_review_save_evaluation(
            evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet={
                "selection_gate_policy_snapshot": {"select_allowed": True}
            },
            decision_id="decision-freshness",
            decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            operator_reason="현재 관측을 확인했다.",
            existing_decision_ids=set(),
            observation_freshness={
                "selection_blocked": True,
                "status": "price_refresh_available",
            },
        )

        self.assertFalse(result["can_save"])
        self.assertIn("Observation freshness", result["blockers"])
```

- [ ] **Step 3: Run RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_refreshable_stale_observation_blocks_only_selected_route \
  tests.test_backtest_final_review_decision_brief.FinalReviewDecisionBriefContractTests.test_up_to_date_observation_keeps_selected_route_recordable \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_refresh_intent_runs_once_and_selects_new_validation \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_refresh_intent_rejects_stale_identity \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_selected_save_guard_rechecks_observation_freshness -v
```

Expected: missing `observation_freshness` parameter, missing consumer, or missing save guard failures.

- [ ] **Step 4: Extend Decision Brief without changing React authority**

In `build_final_review_decision_brief()` add:

```python
observation_freshness: dict[str, Any] | None = None,
```

Normalize it:

```python
observation_freshness = _as_dict(observation_freshness)
```

Pass it to `_build_decision_action()`:

```python
decision_action = _build_decision_action(
    route=route,
    eligibility=eligibility,
    decision_id=decision_id,
    existing_decision_ids={str(value) for value in existing_decision_ids},
    observation_freshness=observation_freshness,
)
```

Modify `_build_decision_action()`:

```python
refresh_blocked = bool(observation_freshness.get("selection_blocked"))
selected_route_blocked = (
    option_route == SELECT_FOR_PRACTICAL_PORTFOLIO
    and (
        not bool(eligibility.get("select_allowed"))
        or refresh_blocked
    )
)
```

Use `"최신 데이터로 다시 계산한 뒤 계속 추적으로 기록할 수 있습니다."` when refresh is the reason.

Return:

```python
"observation_freshness": observation_freshness,
```

and capability:

```python
"can_refresh_observation": bool(observation_freshness.get("can_refresh")),
```

Keep `provider_fetch=False`, `validation_rerun=False`, `storage_append_in_react=False`.

- [ ] **Step 5: Add the authoritative save guard**

Extend `_build_final_review_save_evaluation()`:

```python
observation_freshness: dict[str, Any] | None = None,
```

Add one check:

```python
{
    "Criteria": "Observation freshness",
    "Ready": (
        not selected_route
        or not bool(dict(observation_freshness or {}).get("selection_blocked"))
    ),
    "Current": dict(observation_freshness or {}).get("status") or "not_provided",
    "Meaning": "계속 추적 선정은 현재 확보 가능한 관측 기간을 반영한 뒤 저장합니다.",
}
```

All existing callers remain valid because the parameter defaults to `None`. `_consume_final_review_decision_intent()` must receive and pass the current freshness model so a forged React intent cannot bypass the button state.

- [ ] **Step 6: Implement Streamlit freshness build and intent consumer**

Import:

```python
from app.services.backtest_final_review_refresh import (
    build_final_review_refresh_status,
    run_final_review_observation_refresh,
)
```

Add:

```python
def _refresh_result_state_key(selection_source_id: Any) -> str:
    return (
        "final_review_observation_refresh_result_"
        f"{_paper_ledger_slug(selection_source_id)}"
    )
```

Implement `_consume_final_review_observation_refresh_intent()` with these guards:

```python
if payload.get("action") != "refresh_observation":
    return
if payload source_id != validation.selection_source_id:
    st.error(...)
    return
if payload validation_id != validation.validation_id:
    st.error(...)
    return
if not observation_freshness.get("can_refresh"):
    st.error(...)
    return
if consumed intent id matches:
    return
```

Run under:

```python
with st.spinner(
    "최신 가격을 확인하고 같은 전략을 다시 계산하는 중입니다...",
    show_time=True,
):
    result = run_final_review_observation_refresh(
        source=dict(validation.get("selection_source_snapshot") or {}),
        validation=validation,
    )
```

Store result by `selection_source_id`. If `validation_saved` and `new_validation_id` are present:

```python
st.session_state["final_review_active_decision_brief_source_id"] = (
    f"practical_validation_result:{new_validation_id}"
)
```

Set a success/warning/error notice from result status, then `st.rerun()`.

In `render_final_review_workspace()`:

1. build status before Decision Brief;
2. merge `last_result` from session;
3. pass it to `build_final_review_decision_brief`;
4. consume candidate intent;
5. consume refresh intent;
6. consume decision intent with the same freshness model.

In the Streamlit fallback, show the four dates/limiter and return the same refresh intent button before charts.

- [ ] **Step 7: Run GREEN and focused Final Review regression**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_refresh \
  tests.test_backtest_final_review_decision_brief \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests -v
```

Expected: all tests `OK`.

- [ ] **Step 8: Commit 3차**

```bash
git add \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review_helpers.py \
  app/web/backtest_final_review/page.py \
  tests/test_backtest_final_review_decision_brief.py \
  tests/test_service_contracts.py
git diff --cached --check
git commit -m "Final Review 최신 관측 intent와 선정 Gate 연결"
```

## 4차: React Freshness UI, Browser QA, Docs

### Task 11.4: compact freshness strip와 closeout

**Files:**

- Modify: `tests/test_final_review_market_context_visual_contract.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts`
- Modify: `app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**

- Consumes: Decision Brief `observation_freshness`
- Produces: `RefreshObservationIntent`, compact chart-adjacent freshness UI, durable flow documentation

- [ ] **Step 1: Write RED React source contract**

Append to `tests/test_final_review_market_context_visual_contract.py`:

```python
    def test_observation_freshness_is_compact_and_intent_only(self) -> None:
        workspace = WORKSPACE.read_text(encoding="utf-8")
        types = (FINAL_REVIEW_ROOT / "decisionBriefTypes.ts").read_text(
            encoding="utf-8"
        )
        style = STYLE.read_text(encoding="utf-8")

        behavior_body = workspace.split("function BehaviorBoard", 1)[1]
        behavior_body = behavior_body.split("function FindingColumn", 1)[0]

        self.assertIn("ObservationFreshness", behavior_body)
        self.assertIn("현재 차트", workspace)
        self.assertIn("최신 완료 시장일", workspace)
        self.assertIn("DB 공통일", workspace)
        self.assertIn("제한 종목", workspace)
        self.assertIn("최신 데이터로 다시 계산", workspace)
        self.assertIn('action: "refresh_observation"', workspace)
        self.assertIn("RefreshObservationIntent", types)
        self.assertIn(".db-freshness-strip", style)
        self.assertIn(".db-freshness-action", style)
        self.assertNotIn("fetch(", workspace)
        self.assertNotIn("registry", workspace.lower())
        self.assertNotIn("run_practical_validation", workspace)
```

Update the Final Review source contract in `tests/test_service_contracts.py` to require `refresh_observation` in source and built assets while continuing to forbid React DB/provider/replay imports.

- [ ] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_final_review_market_context_visual_contract.FinalReviewMarketContextVisualContractTests.test_observation_freshness_is_compact_and_intent_only -v
```

Expected: missing type/component/class failures.

- [ ] **Step 3: Add the TypeScript contract**

In `decisionBriefTypes.ts` add:

```typescript
export type ObservationFreshness = {
  schema_version: "final_review_observation_freshness_v1"
  status: "up_to_date" | "replay_available" | "price_refresh_available" | "partial_refresh" | "blocked"
  tone: Tone
  label: string
  summary: string
  detail: string
  selection_source_id: string
  validation_id: string
  stored_curve_end: string | null
  latest_completed_market_date: string | null
  db_common_price_date: string | null
  refresh_target_date: string | null
  limiting_symbols: string[]
  stale_symbols: string[]
  missing_symbols: string[]
  provider_gap_symbols: string[]
  refreshable_symbols: string[]
  can_refresh: boolean
  selection_blocked: boolean
  button_label: string
  last_result?: {
    status: string
    message: string
    previous_curve_end?: string | null
    refreshed_curve_end?: string | null
  }
}
```

Add `observation_freshness: ObservationFreshness` to `DecisionBrief`.

Add:

```typescript
export type RefreshObservationIntent = {
  action: "refresh_observation"
  intent_id: string
  source_id: string
  validation_id: string
}
```

Extend:

```typescript
export type DecisionWorkspaceIntent =
  | CandidateSelectionIntent
  | RefreshObservationIntent
  | FinalDecisionIntent
```

- [ ] **Step 4: Render the compact freshness strip**

In `DecisionBriefWorkspace.tsx` add:

```tsx
function ObservationFreshness({
  brief,
  onIntent,
}: {
  brief: DecisionBrief
  onIntent: WorkspaceProps["onIntent"]
}) {
  const freshness = brief.observation_freshness
  const [pending, setPending] = useState(false)
  const limiter = freshness.limiting_symbols.length
    ? freshness.limiting_symbols.join(", ")
    : "없음"

  return (
    <section
      className={`db-freshness-strip db-tone-${freshness.tone}`}
      aria-label="관측 최신성"
    >
      <div className="db-freshness-state">
        <span>{freshness.label}</span>
        <strong>{freshness.summary}</strong>
        <p>{freshness.detail}</p>
      </div>
      <dl className="db-freshness-dates">
        <div><dt>현재 차트</dt><dd>{freshness.stored_curve_end || "미측정"}</dd></div>
        <div><dt>최신 완료 시장일</dt><dd>{freshness.latest_completed_market_date || "미측정"}</dd></div>
        <div><dt>DB 공통일</dt><dd>{freshness.db_common_price_date || "미측정"}</dd></div>
        <div><dt>제한 종목</dt><dd>{limiter}</dd></div>
      </dl>
      {freshness.last_result?.message && (
        <p className="db-freshness-result">{freshness.last_result.message}</p>
      )}
      {freshness.can_refresh && (
        <button
          type="button"
          className="db-freshness-action"
          disabled={pending}
          onClick={() => {
            if (pending) return
            setPending(true)
            onIntent({
              action: "refresh_observation",
              intent_id: nextIntentId("refresh"),
              source_id: freshness.selection_source_id,
              validation_id: freshness.validation_id,
            })
          }}
        >
          {pending ? "다시 계산하는 중..." : freshness.button_label}
        </button>
      )}
    </section>
  )
}
```

Render it in `BehaviorBoard` after `SectionHeading` and before `.db-chart-grid`:

```tsx
<ObservationFreshness brief={brief} onIntent={onIntent} />
```

Update `BehaviorBoard` to receive `onIntent` and pass it from the workspace.

- [ ] **Step 5: Apply the approved visual language**

Add CSS:

```css
.db-freshness-strip {
  display: grid;
  grid-template-columns: minmax(220px, 1.2fr) minmax(360px, 1.8fr) auto;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px 18px;
  border: 1px solid #dae4ee;
  border-radius: 14px;
  background: linear-gradient(135deg, #f8fbff 0%, #f3f7f8 100%);
}

.db-freshness-state {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.db-freshness-state span {
  color: #284e69;
  font-size: 10px;
  font-weight: 800;
}

.db-freshness-state strong {
  color: #152033;
  font-size: 13px;
  line-height: 1.45;
}

.db-freshness-state p,
.db-freshness-result {
  margin: 0;
  color: #647589;
  font-size: 10px;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.db-freshness-dates {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 0;
  border: 1px solid #dae4ee;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, .86);
}

.db-freshness-dates div {
  min-width: 0;
  padding: 10px 11px;
  border-right: 1px solid #dae4ee;
}

.db-freshness-dates div:last-child {
  border-right: 0;
}

.db-freshness-dates dt {
  color: #7a8998;
  font-size: 9px;
}

.db-freshness-dates dd {
  margin: 3px 0 0;
  color: #24364a;
  font-size: 11px;
  font-weight: 760;
  overflow-wrap: anywhere;
}

.db-freshness-action {
  min-height: 42px;
  padding: 0 15px;
  border: 0;
  border-radius: 11px;
  color: #fff;
  background: #284e69;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
}

.db-freshness-action:disabled {
  cursor: wait;
  opacity: .65;
}

.db-freshness-result {
  grid-column: 1 / -1;
  padding-top: 10px;
  border-top: 1px solid #dae4ee;
}
```

At `max-width: 960px`, use one column and keep dates four columns. At `max-width: 760px`, make dates two columns and remove every second vertical border correctly. At `max-width: 460px`, make dates one column and use bottom borders. No horizontal overflow.

- [ ] **Step 6: Run GREEN, build, and Python regressions**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_refresh \
  tests.test_backtest_final_review_decision_brief \
  tests.test_final_review_market_context_visual_contract \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_service_contracts.PracticalValidationReplayServiceContractTests \
  tests.test_global_relative_strength_strategy -v
```

Run:

```bash
cd app/web/components/final_review_investment_report/frontend
npm run build
```

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_refresh.py \
  app/services/backtest_price_refresh.py \
  app/services/backtest_practical_validation_replay.py \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review_helpers.py \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py
git diff --check
```

Expected: all unittest modules `OK`, Vite production build success, py_compile success, no diff-check output.

- [ ] **Step 7: Run read-only current GRS runtime probe**

Use the current registry loader and latest-row policy without saving:

```bash
.venv/bin/python - <<'PY'
from app.runtime import load_practical_validation_results
from app.web.backtest_final_review_helpers import (
    _latest_practical_validation_rows_by_source,
)
from app.services.backtest_final_review_refresh import (
    build_final_review_refresh_status,
)

rows = _latest_practical_validation_rows_by_source(
    load_practical_validation_results(limit=100)
)
row = next(
    item
    for item in rows
    if item.get("validation_id")
    == "validation_selection_rebuilt_grs_macro_top1_ma200_aef1f226_7bca4e1a"
)
status = build_final_review_refresh_status(
    source=dict(row.get("selection_source_snapshot") or {}),
    validation=row,
)
print(
    status["status"],
    status["stored_curve_end"],
    status["latest_completed_market_date"],
    status["db_common_price_date"],
    status["limiting_symbols"],
)
PY
```

Expected before executing real refresh: `price_refresh_available 2026-06-26 2026-07-15 2026-06-26 ['BIL']`.

- [ ] **Step 8: Restart the local app and run Browser QA**

Read and use `browser:control-in-app-browser` before Browser QA.

Restart the 8505 Streamlit process after the tracked React build if its watcher is disabled.

Browser QA, without clicking the actual refresh or final decision save:

1. Open `http://localhost:8505/backtest`.
2. Navigate to Final Review current GRS.
3. Desktop:
   - freshness strip is between section heading and charts;
   - current chart `2026-06-26`;
   - latest completed market `2026-07-15`;
   - DB common `2026-06-26`;
   - limiter `BIL`;
   - button label `최신 데이터로 다시 계산`;
   - selected route is disabled while hold / reject / re-review remain selectable;
   - cumulative and underwater hover still work.
4. 760px:
   - freshness state, dates, action stack without clipping;
   - date cells become two columns;
   - charts and observation cards remain one-column/two-column as designed;
   - outer and component `scrollWidth == clientWidth`;
   - no console errors.
5. Save one screenshot as `qa-final-review-observation-refresh-760.png`.
6. Do not click refresh because that would append a real validation row after ingestion/replay.

- [ ] **Step 9: Synchronize durable documentation**

Read and use `finance-doc-sync`.

Document:

- Final Review can request a bounded Python-owned observation refresh without routing to Level2.
- this is explicit user action, not auto refresh;
- ingestion still uses the existing job and DB boundary;
- replay uses the same source contract and creates no new strategy;
- success appends a new Practical Validation row;
- selected route is blocked only while an automatic refresh path remains;
- hold / reject / re-review remain recordable;
- React stays intent-only;
- Browser QA does not execute the mutating action against the protected registry.

Update active task:

- `STATUS.md`: four slices completed or exact remaining blocker
- `NOTES.md`: root cause, chosen one-click boundary, provider-gap semantics
- `RUNS.md`: every RED/GREEN/build/compile/runtime/Browser result and commit id
- `RISKS.md`: provider no-data partial refresh, long-running synchronous job, QA non-click residual

Keep root logs to 3–5 concise lines with a pointer to the active task.

- [ ] **Step 10: Fresh completion verification**

Read and use `superpowers:verification-before-completion`.

Run the complete focused suite again from a clean test invocation:

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_final_review_refresh \
  tests.test_backtest_final_review_decision_brief \
  tests.test_final_review_market_context_visual_contract \
  tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests \
  tests.test_service_contracts.PracticalValidationReplayServiceContractTests \
  tests.test_service_contracts.PracticalValidationServiceContractTests \
  tests.test_global_relative_strength_strategy -v
```

Run:

```bash
cd app/web/components/final_review_investment_report/frontend
npm run build
```

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/backtest_final_review_refresh.py \
  app/services/backtest_price_refresh.py \
  app/services/backtest_practical_validation_replay.py \
  app/services/backtest_final_review_decision_brief.py \
  app/web/backtest_final_review_helpers.py \
  app/web/backtest_final_review/page.py \
  app/web/components/final_review_investment_report/component.py
git diff --check
git status --short
```

Verify `git status` contains no staged or committed protected registry, run history, `.superpowers/`, or QA artifact.

- [ ] **Step 11: Commit 4차 closeout**

```bash
git add \
  app/web/components/final_review_investment_report/frontend/src/decisionBriefTypes.ts \
  app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx \
  app/web/components/final_review_investment_report/frontend/src/style.css \
  app/web/components/final_review_investment_report/frontend/build \
  tests/test_final_review_market_context_visual_contract.py \
  tests/test_service_contracts.py \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/STATUS.md \
  .aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/NOTES.md \
  .aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/RUNS.md \
  .aiworkspace/note/finance/tasks/active/final-review-evidence-closure-contract-v1-20260712/RISKS.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git commit -m "Final Review 최신 관측 UI와 문서 동기화"
```

Do not add `qa-final-review-observation-refresh-760.png`.

## Stop Conditions

Stop and report before implementation expansion only if:

1. current selection source snapshot cannot reconstruct the existing replay contract;
2. price refresh would require a new provider or DB schema rather than the existing OHLCV job;
3. new validation cannot preserve the current validation profile without changing user meaning;
4. latest valuation extension creates a signal/rebalance row in the GRS regression;
5. append safety requires rewriting existing registry rows;
6. the actual Final Review source identity cannot be made stable without replacing the current selector contract.

Do not stop for a normal provider gap, partial refresh result, or a test-discovered implementation detail that fits the approved boundaries.

## Observation Refresh Plan Self-Review

### Spec coverage

- [x] Level2 이동 없이 Final Review one-click action을 구현한다.
- [x] 현재 chart end / latest session / DB common / limiter를 구분한다.
- [x] replay-only와 price-refresh-then-replay 경로가 분리돼 있다.
- [x] existing validation profile을 재사용하고 새 row만 append한다.
- [x] selected route만 stale Gate 영향을 받고 다른 route는 유지한다.
- [x] failure와 partial result에서 기존 chart를 보존한다.
- [x] React intent-only와 Python authority를 유지한다.
- [x] current GRS, GRS valuation row, build, Browser QA, docs, protected files 검증이 포함됐다.

### Placeholder scan

- [x] 새 plan section에 미정 placeholder나 추상적인 “테스트 추가” 문구가 없다.
- [x] 모든 production code step에 함수명, payload key, 분기 규칙이 있다.
- [x] 모든 test step에 실제 test name, command, expected failure/pass가 있다.

### Type and ownership consistency

- [x] Python `observation_freshness`와 TypeScript `ObservationFreshness` key가 일치한다.
- [x] `refresh_observation` intent의 `source_id`, `validation_id`, `intent_id`가 Python consumer와 일치한다.
- [x] refresh result와 saved `observation_refresh_snapshot`의 date/provider fields가 일치한다.
- [x] latest session owner는 price refresh, common date owner는 replay contract, orchestration owner는 새 Final Review refresh service다.
- [x] append writer는 기존 `save_practical_validation_result`를 재사용하고 React/Streamlit wrapper는 registry path를 소유하지 않는다.
