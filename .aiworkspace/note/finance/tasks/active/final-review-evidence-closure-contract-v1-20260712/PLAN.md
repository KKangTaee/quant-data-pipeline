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
