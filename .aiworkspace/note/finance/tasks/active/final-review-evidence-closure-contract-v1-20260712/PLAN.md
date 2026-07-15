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
