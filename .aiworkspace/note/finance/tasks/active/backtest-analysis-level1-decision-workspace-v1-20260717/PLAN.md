# Backtest Analysis Level1 Decision Workspace V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 단일 전략·Portfolio Mix runtime과 저장 경계를 보존하면서 Level1을 목적 분기형 4단계 decision workspace로 개편한다.

**Architecture:** Python pure service가 전략 목적·성숙도, configuration fingerprint, 결과 freshness, 사용자 설명, Level2 handoff Gate와 action availability를 하나의 read model로 만든다. 같은 React bundle을 `context`와 `decision` 두 surface로 mount하고, 기존 Streamlit 전략 설정 form은 fragment 안의 Python-owned Step 2 editor로 보존한다. 단일 전략 실행, weighted Mix 실행, Run History, saved Mix, Practical Validation source handoff는 기존 handler를 adapter로 호출한다.

**Tech Stack:** Python 3.11+, Streamlit fragment / session state, pandas, React 18, TypeScript 5.6, Vite 5, `streamlit-component-lib`, unittest / pytest.

## Global Constraints

- worktree는 `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev`, branch는 `codex/backtest-dev`를 그대로 사용한다.
- 별도 task, branch, worktree를 만들지 않는다.
- 모든 기능과 버그 수정은 RED -> GREEN을 확인한다.
- 각 distinct implementation unit은 한국어 커밋으로 기록한다.
- React는 presentation과 intent만 담당하고 Python이 분류, freshness, Gate, handler 검증, 실행, 저장을 소유한다.
- `Risk-On Momentum 5D`는 `development`로 보존하고 Level2 handoff를 차단한다.
- 성공 실행은 Run History만 기록하며 명시적 `후보로 저장하고 Level2로 이동` intent만 Practical Validation source를 등록한다.
- saved Mix는 reusable setup이며 Level2 candidate source와 동일하지 않다.
- 설정 변경은 이전 결과를 삭제하지 않고 `stale`로 표시한다.
- first-read에 raw field, callable path, traceback을 노출하지 않는다.
- desktop은 최대 2열, 760px 이하는 1열과 horizontal overflow 0을 만족한다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`, `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, `.aiworkspace/note/finance/saved/*.jsonl`, generated screenshot / run artifact, `.superpowers/`를 stage하거나 commit하지 않는다.
- strategy runtime, DB schema, Level2 / Final Review route, broker / live approval / account sync / auto rebalance를 재설계하지 않는다.

## Roadmap And Commit Units

| 전체 차수 | 구현 Task | 독립 완료 단위 |
|---|---|---|
| 1차 Truth / Handoff Contract | Task 1~2 | catalog·maturity·fingerprint, readiness·action truth |
| 2차 Decision Workspace Read Model | Task 3 | single / Mix 공통 pure projection |
| 3차 Single Strategy One-Shell | Task 4~6 | React shell, stable fragment·draft, result·handoff·fallback |
| 4차 Portfolio Mix One-Shell | Task 7~8 | pure Mix contract, role·weight·saved Mix integration |
| 5차 Runtime QA / Docs / Closeout | Task 9 | fresh verification, Browser QA, docs sync |

## File Ownership Map

### New Files

- `app/services/backtest_analysis_decision_workspace.py`: Level1 schema, fingerprint, strategy catalog projection, single / Mix result interpretation, freshness, action Gate.
- `tests/test_backtest_analysis_decision_workspace.py`: truth, read model, persistence-boundary unit tests.
- `app/web/backtest_analysis_workspace.py`: Streamlit state adapter, validated intent dispatcher, context / decision renderer.
- `app/web/backtest_analysis_workspace_panel.py`: same-read-model Python fallback.
- `app/web/components/backtest_analysis_decision_workspace/`: two-surface React component, wrapper, Vite project, responsive CSS.

### Existing Files With Narrow Responsibilities

- `app/services/backtest_strategy_catalog.py`: purpose and maturity metadata source.
- `app/services/backtest_portfolio_mix_readiness.py`: weighted Mix readiness와 role / weight truth.
- `app/services/backtest_weighted_portfolio.py`: optional component roles와 Level1 fingerprint 저장.
- `app/services/backtest_saved_portfolio_replay.py`: legacy role-less saved record 호환.
- `app/web/backtest_analysis.py`: Level1 entry와 stable context / mutable work fragment composition.
- `app/web/backtest_single_strategy.py`: selected strategy Step 2 routing과 stale preservation.
- `app/web/backtest_single_runner.py`: normalized draft / result fingerprint와 Run History context.
- `app/web/backtest_single_forms/*.py`: current draft payload와 contextual setting group.
- `app/web/backtest_result_display.py`: decision-first wrapper와 legacy detailed evidence 분리.
- `app/web/backtest_compare/page.py`: Mix Step 1 / Step 2, roles, saved replay adapter.
- `tests/test_backtest_refactor_boundaries.py`: intent-only, two-surface, fragment, responsive, fallback 경계.
- `tests/test_service_contracts.py`: 현재 runtime / persistence compatibility 회귀.

---

## 1차: Level1 Truth / Handoff Contract

### Task 1: Purpose Catalog, Maturity, And Configuration Fingerprint

**Files:**
- Modify: `app/services/backtest_strategy_catalog.py`
- Create: `app/services/backtest_analysis_decision_workspace.py`
- Create: `tests/test_backtest_analysis_decision_workspace.py`

**Interfaces:**
- Consumes: `SINGLE_STRATEGY_OPTIONS`, `STRATEGY_FAMILY_VARIANTS`.
- Produces: `build_level1_strategy_catalog()`, `level1_strategy_maturity()`, `build_level1_configuration_fingerprint()`.

- [x] **Step 1: Write failing catalog and fingerprint tests**

```python
from app.services.backtest_analysis_decision_workspace import (
    build_level1_configuration_fingerprint,
    build_level1_strategy_catalog,
    level1_strategy_maturity,
)


def test_level1_catalog_groups_each_strategy_once() -> None:
    groups = build_level1_strategy_catalog()
    options = [item["strategy_choice"] for group in groups for item in group["items"]]
    assert options == [
        "Quality + Value", "Quality", "Value", "GTAA",
        "Global Relative Strength", "Dual Momentum",
        "Risk Parity Trend", "Equal Weight", "Risk-On Momentum 5D",
    ]
    assert len(options) == len(set(options))


def test_risk_on_is_development_not_research() -> None:
    assert level1_strategy_maturity("Risk-On Momentum 5D") == "development"
    assert level1_strategy_maturity("GTAA") == "production"


def test_configuration_fingerprint_is_order_independent_and_sensitive() -> None:
    left = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"top": 3, "tickers": ["SPY", "TLT"]},
    )
    reordered = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"tickers": ["SPY", "TLT"], "top": 3},
    )
    changed = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"top": 2, "tickers": ["SPY", "TLT"]},
    )
    assert left == reordered
    assert left != changed
```

- [x] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py -q`

Expected: import error because the new service and functions do not exist.

- [x] **Step 3: Add purpose and maturity metadata**

Add to `app/services/backtest_strategy_catalog.py` and export through `__all__`:

```python
LEVEL1_STRATEGY_PURPOSE_GROUPS = OrderedDict(
    [
        ("factor_selection", {"label": "팩터 기반 종목 선정", "items": ["Quality + Value", "Quality", "Value"]}),
        ("tactical_allocation", {"label": "모멘텀·전술 자산배분", "items": ["GTAA", "Global Relative Strength", "Dual Momentum"]}),
        ("diversified_baseline", {"label": "분산·기본 포트폴리오", "items": ["Risk Parity Trend", "Equal Weight"]}),
        ("development", {"label": "개발 중 전략", "items": ["Risk-On Momentum 5D"]}),
    ]
)
LEVEL1_STRATEGY_MATURITY = {
    strategy: ("development" if strategy == "Risk-On Momentum 5D" else "production")
    for strategy in SINGLE_STRATEGY_OPTIONS
}
```

- [x] **Step 4: Implement catalog and fingerprint**

Create the service with these exact foundations:

```python
from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from typing import Any

from app.services.backtest_strategy_catalog import (
    LEVEL1_STRATEGY_MATURITY,
    LEVEL1_STRATEGY_PURPOSE_GROUPS,
    STRATEGY_FAMILY_VARIANTS,
)

BACKTEST_ANALYSIS_DECISION_WORKSPACE_SCHEMA_VERSION = "backtest_analysis_decision_workspace_v1"


def _json_ready(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def build_level1_configuration_fingerprint(*, workspace_kind: str, selection: Mapping[str, Any], configuration: Mapping[str, Any]) -> str:
    payload = {"workspace_kind": workspace_kind, "selection": _json_ready(dict(selection)), "configuration": _json_ready(dict(configuration))}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def level1_strategy_maturity(strategy_choice: str | None) -> str:
    return LEVEL1_STRATEGY_MATURITY.get(str(strategy_choice or ""), "development")


def build_level1_strategy_catalog() -> list[dict[str, Any]]:
    groups = []
    for group_id, config in LEVEL1_STRATEGY_PURPOSE_GROUPS.items():
        items = [
            {
                "strategy_choice": choice,
                "maturity": level1_strategy_maturity(choice),
                "variants": list(STRATEGY_FAMILY_VARIANTS.get(choice, {}).keys()),
                "level2_handoff_supported": level1_strategy_maturity(choice) == "production",
            }
            for choice in config["items"]
        ]
        groups.append({"group_id": group_id, "label": config["label"], "items": items})
    return groups
```

- [x] **Step 5: Run GREEN**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py -q`

Expected: 3 passed.

- [x] **Step 6: Commit**

```bash
git add app/services/backtest_strategy_catalog.py app/services/backtest_analysis_decision_workspace.py tests/test_backtest_analysis_decision_workspace.py
git commit -m "Backtest Analysis 전략 분류와 설정 지문 계약 추가"
```

### Task 2: Freshness, Root Dedup, And Callable Action Truth

**Files:**
- Modify: `app/services/backtest_analysis_decision_workspace.py`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`

**Interfaces:**
- Consumes: `build_next_step_readiness_evaluation()`, `build_handoff_gate_summary()`, fingerprints, action handler mapping.
- Produces: `build_level1_readiness_projection()`, `_deduplicate_reasons()`.

- [x] **Step 1: Write failing truth tests**

```python
def test_stale_result_is_preserved_and_handoff_blocked() -> None:
    projection = build_level1_readiness_projection(
        workspace_kind="single_strategy", strategy_choice="GTAA",
        result_bundle={"meta": {"strategy_key": "gtaa"}},
        current_configuration_fingerprint="current",
        result_configuration_fingerprint="previous",
        action_handlers={"save_and_move": lambda: None},
    )
    assert projection["result_freshness"] == "stale"
    assert projection["handoff_state"] == "blocked"
    assert projection["result_available"] is True


def test_development_or_missing_handler_has_no_cta() -> None:
    development = build_level1_readiness_projection(
        workspace_kind="single_strategy", strategy_choice="Risk-On Momentum 5D",
        result_bundle={"meta": {"strategy_key": "risk_on_momentum_5d"}},
        current_configuration_fingerprint="same", result_configuration_fingerprint="same",
        action_handlers={"save_and_move": lambda: None},
    )
    missing = build_level1_readiness_projection(
        workspace_kind="single_strategy", strategy_choice="GTAA",
        result_bundle={"meta": {"strategy_key": "gtaa"}},
        current_configuration_fingerprint="same", result_configuration_fingerprint="same",
        action_handlers={"save_and_move": None},
    )
    assert "save_and_move" not in development["actions"]
    assert "save_and_move" not in missing["actions"]


def test_duplicate_root_reason_is_counted_once() -> None:
    rows = _deduplicate_reasons([
        {"root_issue_id": "price", "message": "가격 확인"},
        {"root_issue_id": "price", "message": "가격 확인"},
    ])
    assert rows == [{"root_issue_id": "price", "message": "가격 확인"}]
```

- [x] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py -q`

Expected: failures because readiness and dedup functions do not exist.

- [x] **Step 3: Implement readiness truth**

```python
from app.services.backtest_handoff_readiness import build_handoff_gate_summary, build_next_step_readiness_evaluation


def _deduplicate_reasons(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    result, seen = [], set()
    for row in rows:
        root = str(row.get("root_issue_id") or row.get("message") or "").strip()
        if root and root not in seen:
            seen.add(root)
            result.append({"root_issue_id": root, "message": str(row.get("message") or "")})
    return result


def build_level1_readiness_projection(
    *, workspace_kind: str, strategy_choice: str | None, result_bundle: dict[str, Any] | None,
    current_configuration_fingerprint: str, result_configuration_fingerprint: str | None,
    action_handlers: Mapping[str, Callable[..., Any] | None],
) -> dict[str, Any]:
    result_available = bool(result_bundle)
    freshness = "none" if not result_available else ("current" if current_configuration_fingerprint == result_configuration_fingerprint else "stale")
    maturity = level1_strategy_maturity(strategy_choice) if workspace_kind == "single_strategy" else "production"
    meta = dict((result_bundle or {}).get("meta") or {})
    evaluation = build_next_step_readiness_evaluation(meta) if result_available else {}
    can_enter = bool(evaluation.get("can_enter_practical_validation"))
    handoff = "ready" if result_available and freshness == "current" and maturity == "production" and can_enter else "blocked"
    actions = {}
    if handoff == "ready" and callable(action_handlers.get("save_and_move")):
        actions["save_and_move"] = {"id": "save_and_move", "label": "후보로 저장하고 Level2로 이동", "enabled": True}
    return {
        "result_available": result_available, "result_freshness": freshness,
        "strategy_maturity": maturity, "handoff_state": handoff,
        "actions": actions, "evaluation": evaluation,
        "gate_summary": build_handoff_gate_summary(meta) if result_available else {},
    }
```

- [x] **Step 4: Run GREEN and existing handoff regression**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "handoff_readiness or candidate_review_draft"
```

Expected: all new tests and selected existing tests pass.

- [x] **Step 5: Commit**

```bash
git add app/services/backtest_analysis_decision_workspace.py tests/test_backtest_analysis_decision_workspace.py
git commit -m "Backtest Analysis 결과 최신성과 인계 진실 계약 추가"
```

---

## 2차: Level1 Decision Workspace Read Model

### Task 3: Complete Single / Mix Decision Projection

**Files:**
- Modify: `app/services/backtest_analysis_decision_workspace.py`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`

**Interfaces:**
- Consumes: Task 1~2 contracts, result bundle, saved Mix summaries, last error.
- Produces: `build_backtest_analysis_decision_workspace()` with stable identity, status axes, user explanation, details, actions, boundaries.

- [x] **Step 1: Write failing full-projection tests**

```python
import pandas as pd
from unittest.mock import patch


def _successful_bundle() -> dict:
    return {
        "strategy_name": "GTAA",
        "summary_df": pd.DataFrame([{"CAGR": 0.12, "Maximum Drawdown": -0.18, "Sharpe Ratio": 0.8, "Standard Deviation": 0.14}]),
        "result_df": pd.DataFrame({"Date": ["2026-06-30"], "Total Balance": [11200.0]}),
        "chart_df": pd.DataFrame({"Date": ["2026-06-30"], "Total Balance": [11200.0]}),
        "meta": {"strategy_key": "gtaa", "promotion_decision": "pass", "price_freshness": {"status": "ok"}, "transaction_cost_bps": 10.0},
    }


def test_workspace_orders_decision_metrics_and_technical_evidence() -> None:
    selection, configuration = {"strategy_choice": "GTAA"}, {"top": 3}
    fingerprint = build_level1_configuration_fingerprint(workspace_kind="single_strategy", selection=selection, configuration=configuration)
    with patch(
        "app.services.backtest_analysis_decision_workspace.build_next_step_readiness_evaluation",
        return_value={"can_enter_practical_validation": True},
    ):
        workspace = build_backtest_analysis_decision_workspace(
            workspace_kind="single_strategy", selection=selection, configuration=configuration,
            result_bundle=_successful_bundle(), result_configuration_fingerprint=fingerprint,
            saved_mixes=[], last_error=None, last_error_kind=None,
            action_handlers={"save_and_move": lambda: None},
        )
    assert workspace["workspace_phase"] == "result"
    assert workspace["decision"]["headline"] == "Level2 검증 후보로 보낼 수 있습니다"
    assert [row["metric_id"] for row in workspace["decision"]["metrics"]] == ["cagr", "maximum_drawdown", "sharpe_ratio", "volatility"]
    assert workspace["details"]["technical_evidence"]["meta"]["strategy_key"] == "gtaa"


def test_first_read_hides_raw_path_and_error_preserves_result() -> None:
    bundle = _successful_bundle()
    bundle["meta"]["warnings"] = ["app.runtime.backtest._apply_transaction_cost_postprocess"]
    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="single_strategy", selection={"strategy_choice": "GTAA"}, configuration={},
        result_bundle=bundle, result_configuration_fingerprint="old", saved_mixes=[],
        last_error="Backtest data issue: missing SPY", last_error_kind="data",
        action_handlers={"save_and_move": lambda: None},
    )
    assert workspace["workspace_phase"] == "error"
    assert workspace["error"]["kind"] == "data_required"
    assert workspace["decision"]["result_available"] is True
    assert "app.runtime" not in str(workspace["decision"])
```

- [x] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py -q`

Expected: failures because the complete builder does not exist.

- [x] **Step 3: Implement error, KPI, and plain-reason helpers**

```python
_ERROR_KIND_MAP = {"input": "configuration_required", "data": "data_required", "system": "execution_failed"}


def _metric_items(summary_df: Any) -> list[dict[str, Any]]:
    if summary_df is None or getattr(summary_df, "empty", True):
        return []
    row = summary_df.iloc[0]
    definitions = [("cagr", "연환산 수익률", "CAGR"), ("maximum_drawdown", "최대 낙폭", "Maximum Drawdown"), ("sharpe_ratio", "위험 대비 수익", "Sharpe Ratio"), ("volatility", "변동성", "Standard Deviation")]
    return [{"metric_id": key, "label": label, "value": row.get(column)} for key, label, column in definitions if column in row.index]


def _plain_reasons(readiness: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = []
    for index, message in enumerate(list(dict(readiness.get("gate_summary") or {}).get("action_items") or [])):
        text = str(message)
        if "app." in text or "result_df." in text:
            text = "실행 계약의 기술 근거를 상세 근거에서 확인해야 합니다."
        rows.append({"root_issue_id": f"gate:{index}:{text}", "message": text})
    return _deduplicate_reasons(rows)[:3]
```

- [x] **Step 4: Implement the complete builder**

The function body is fixed to compute every projected variable before returning it:

```python
def build_backtest_analysis_decision_workspace(
    *, workspace_kind: str, selection: Mapping[str, Any], configuration: Mapping[str, Any],
    result_bundle: dict[str, Any] | None, result_configuration_fingerprint: str | None,
    saved_mixes: Sequence[Mapping[str, Any]], last_error: str | None, last_error_kind: str | None,
    action_handlers: Mapping[str, Callable[..., Any] | None],
    component_bundles: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    fingerprint = build_level1_configuration_fingerprint(
        workspace_kind=workspace_kind,
        selection=selection,
        configuration=configuration,
    )
    strategy_choice = str(selection.get("strategy_choice") or "") or None
    readiness = build_level1_readiness_projection(
        workspace_kind=workspace_kind,
        strategy_choice=strategy_choice,
        result_bundle=result_bundle,
        current_configuration_fingerprint=fingerprint,
        result_configuration_fingerprint=result_configuration_fingerprint,
        action_handlers=action_handlers,
    )
    meta = dict((result_bundle or {}).get("meta") or {})
    phase = "error" if last_error else ("result" if result_bundle else ("configuring" if selection else "selecting"))
    maturity = readiness["strategy_maturity"]
    if maturity == "development":
        headline = "개발 중이므로 현재 Level2로 보낼 수 없습니다"
    elif readiness["handoff_state"] == "ready":
        headline = "Level2 검증 후보로 보낼 수 있습니다"
    else:
        headline = "Level1에서 먼저 해결할 항목이 있습니다"
    error = None
    if last_error:
        error = {"kind": _ERROR_KIND_MAP.get(str(last_error_kind or ""), "execution_failed"), "message": str(last_error)}
    current_work = {
        "title": strategy_choice or str(selection.get("mix_name") or "Portfolio Mix"),
        "workspace_kind": workspace_kind,
    }
    decision = {
        "headline": headline,
        "summary": "성과만으로 판단하지 않고 실행·데이터·인계 준비 상태를 함께 확인합니다.",
        "reasons": _plain_reasons(readiness),
        "metrics": _metric_items((result_bundle or {}).get("summary_df")),
        "result_available": readiness["result_available"],
    }
    return {
        "schema_version": BACKTEST_ANALYSIS_DECISION_WORKSPACE_SCHEMA_VERSION,
        "workspace_id": fingerprint[:16],
        "workspace_kind": workspace_kind,
        "configuration_fingerprint": fingerprint,
        "run_result_id": meta.get("run_id"),
        "candidate_source_id": meta.get("selection_source_id"),
        "workspace_phase": phase,
        "result_freshness": readiness["result_freshness"],
        "handoff_state": readiness["handoff_state"],
        "strategy_maturity": maturity,
        "header": {"question": "이 전략 또는 조합을 Level2 검증 후보로 만들 수 있는가?"},
        "current_work": current_work,
        "strategy_catalog": build_level1_strategy_catalog(),
        "configuration_summary": dict(configuration),
        "saved_mixes": [dict(row) for row in saved_mixes],
        "component_bundle_count": len(component_bundles),
        "decision": decision,
        "error": error,
        "actions": readiness["actions"],
        "details": {"technical_evidence": {"meta": meta}},
        "boundaries": {
            "react_executes_backtest": False,
            "react_writes_history": False,
            "react_writes_saved_mix": False,
            "react_writes_candidate_source": False,
            "python_validates_intent": True,
        },
    }
```

- [x] **Step 5: Run GREEN, compile, and diff-check**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
.venv/bin/python -m py_compile app/services/backtest_strategy_catalog.py app/services/backtest_analysis_decision_workspace.py
git diff --check
```

Expected: all commands exit 0.

- [x] **Step 6: Commit**

```bash
git add app/services/backtest_analysis_decision_workspace.py tests/test_backtest_analysis_decision_workspace.py
git commit -m "Backtest Analysis 판단 워크스페이스 모델 도입"
```

---

## 3차: Single Strategy One-Shell

### Task 4: React Context / Decision Component And Boundary Tests

**Files:**
- Create: `app/web/components/backtest_analysis_decision_workspace/__init__.py`
- Create: `app/web/components/backtest_analysis_decision_workspace/component.py`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/index.html`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/package.json`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/package-lock.json`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/tsconfig.json`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/vite.config.ts`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/src/index.tsx`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
- Create: `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: Task 3 JSON-compatible workspace.
- Produces: `is_backtest_analysis_decision_workspace_available()`, `render_backtest_analysis_decision_workspace(...)`; intents `select_workspace_kind`, `select_strategy`, `save_and_move`.

- [ ] **Step 1: Write failing intent-only and responsive tests**

```python
def test_backtest_analysis_react_is_intent_only(self) -> None:
    source = (PROJECT_ROOT / "app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx").read_text()
    for action in ("select_workspace_kind", "select_strategy", "save_and_move"):
        self.assertIn(action, source)
    for forbidden in ("fetch(", "promotion_decision ===", "append_backtest_run_history(", "save_saved_portfolio(", "_queue_candidate_review_draft("):
        self.assertNotIn(forbidden, source)


def test_backtest_analysis_react_has_two_surfaces_and_resize_observer(self) -> None:
    component = (PROJECT_ROOT / "app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx").read_text()
    index = (PROJECT_ROOT / "app/web/components/backtest_analysis_decision_workspace/frontend/src/index.tsx").read_text()
    style = (PROJECT_ROOT / "app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css").read_text()
    self.assertIn('surface: "context" | "decision"', index)
    self.assertIn("data-surface={surface}", component)
    self.assertIn("ResizeObserver", index)
    self.assertIn("Streamlit.setFrameHeight", index)
    self.assertIn("@media (max-width: 760px)", style)
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q -k "backtest_analysis_react"`

Expected: failures because the component files do not exist.

- [ ] **Step 3: Create the Python wrapper**

```python
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Literal

import streamlit.components.v1 as components

_COMPONENT_NAME = "backtest_analysis_decision_workspace"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"
_component = components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR)) if _FRONTEND_BUILD_DIR.exists() else None


def is_backtest_analysis_decision_workspace_available() -> bool:
    return _component is not None


def render_backtest_analysis_decision_workspace(
    *, workspace: dict[str, Any], surface: Literal["context", "decision"],
    key: str, on_change: Callable[[], None] | None = None,
) -> dict[str, Any] | None:
    if _component is None:
        return None
    value = _component(workspace=workspace, surface=surface, key=key, default=None, on_change=on_change)
    return value if isinstance(value, dict) else None
```

Export both functions from `__init__.py`.

- [ ] **Step 4: Create TypeScript types and intent-only presentation**

`types.ts` defines the Task 3 schema, nullable identities, Python-owned `actions`, and:

```ts
export type WorkspaceSurface = "context" | "decision"
export type WorkspaceIntent = {
  action: "select_workspace_kind" | "select_strategy" | "save_and_move"
  payload: Record<string, unknown>
  nonce: string
}
```

All buttons emit through one helper:

```tsx
function emitIntent(action: WorkspaceIntent["action"], payload: Record<string, unknown> = {}) {
  Streamlit.setComponentValue({action, payload, nonce: `${Date.now()}-${Math.random()}`})
}
```

The context surface renders the fixed question, two workspace-kind cards, current-work summary, purpose groups, selected strategy, and Step 2 summary. The decision surface renders Step 3 headline / reasons / metrics, optional error, and Step 4 only when `actions.save_and_move?.enabled === true`.

- [ ] **Step 5: Add continuous height sync**

`src/index.tsx` contains:

```tsx
function App({ args }: AppProps) {
  useEffect(() => {
    const observer = new ResizeObserver(() => Streamlit.setFrameHeight())
    observer.observe(document.documentElement)
    Streamlit.setFrameHeight()
    return () => observer.disconnect()
  }, [args])
  return args.workspace ? (
    <BacktestAnalysisDecisionWorkspace workspace={args.workspace} surface={args.surface ?? "decision"} />
  ) : (
    <div className="bt1-empty">Backtest Analysis workspace payload를 읽을 수 없습니다.</div>
  )
}
```

- [ ] **Step 6: Add visual tokens and 760px CSS**

Use `#152033` ink, blue-gray lines, 20px hero radius, 17px step radius, 14px compact controls, and soft shadow. Include:

```css
@media (max-width: 760px) {
  .bt1-entry-grid, .bt1-purpose-grid, .bt1-metric-grid, .bt1-reason-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .bt1-workspace, .bt1-step, .bt1-header {
    min-width: 0;
    width: 100%;
  }
  .bt1-action-button { width: 100%; }
}
```

- [ ] **Step 7: Install, build, and run GREEN**

```bash
cd app/web/components/backtest_analysis_decision_workspace/frontend
npm install
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q -k "backtest_analysis_react"
```

Expected: Vite exits 0 and both new boundary tests pass.

- [ ] **Step 8: Commit without `frontend/build`**

```bash
git add \
  app/web/components/backtest_analysis_decision_workspace/__init__.py \
  app/web/components/backtest_analysis_decision_workspace/component.py \
  app/web/components/backtest_analysis_decision_workspace/frontend/index.html \
  app/web/components/backtest_analysis_decision_workspace/frontend/package.json \
  app/web/components/backtest_analysis_decision_workspace/frontend/package-lock.json \
  app/web/components/backtest_analysis_decision_workspace/frontend/tsconfig.json \
  app/web/components/backtest_analysis_decision_workspace/frontend/vite.config.ts \
  app/web/components/backtest_analysis_decision_workspace/frontend/src \
  tests/test_backtest_refactor_boundaries.py
git commit -m "Backtest Analysis 원셸 React 화면 추가"
```

### Task 5: Stable Context, Fragment Boundary, Draft Fingerprint, Contextual Settings

**Files:**
- Create: `app/web/backtest_analysis_workspace.py`
- Create: `app/web/backtest_analysis_workspace_panel.py`
- Modify: `app/web/backtest_analysis.py`
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `app/web/backtest_single_runner.py`
- Modify: `app/web/backtest_single_forms/equal_weight.py`
- Modify: `app/web/backtest_single_forms/gtaa.py`
- Modify: `app/web/backtest_single_forms/global_relative_strength.py`
- Modify: `app/web/backtest_single_forms/risk_parity.py`
- Modify: `app/web/backtest_single_forms/dual_momentum.py`
- Modify: `app/web/backtest_single_forms/risk_on_momentum.py`
- Modify: `app/web/backtest_single_forms/strict_factor.py`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: Task 3 builder, Task 4 component, existing forms and `_handle_backtest_run`.
- Produces: `record_single_strategy_draft()`, `build_current_backtest_analysis_workspace()`, `consume_backtest_analysis_intent()`, context outside fragment and work inside fragment.

- [ ] **Step 1: Write failing boundary and runner tests**

```python
def test_backtest_analysis_context_is_outside_work_fragment(self) -> None:
    source = (PROJECT_ROOT / "app/web/backtest_analysis.py").read_text()
    render_prefix = source.split("def render_backtest_analysis_workspace", 1)[1].split("@st.fragment", 1)[0]
    fragment = source.split("def _render_backtest_analysis_work_fragment", 1)[1]
    self.assertIn('surface="context"', render_prefix)
    self.assertIn('surface="decision"', fragment)
    self.assertNotIn('surface="context"', fragment)


def test_single_strategy_change_marks_stale_without_clearing_bundle(self) -> None:
    source = (PROJECT_ROOT / "app/web/backtest_single_strategy.py").read_text()
    body = source.split("def _mark_last_run_stale_if_strategy_selection_changed", 1)[1].split("\ndef ", 1)[0]
    self.assertIn("backtest_last_result_requires_rerun", body)
    self.assertNotIn("backtest_last_bundle = None", body)
```

Add a mocked runner test that asserts a successful bundle meta and Run History context carry the same `level1_configuration_fingerprint` and `_queue_candidate_review_draft` is never called.

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py -q -k "draft or context_is_outside or marks_stale"`

Expected: failures because adapter, fragment, and stale marker do not exist.

- [ ] **Step 3: Implement validated intent and fallback contracts**

`app/web/backtest_analysis_workspace.py` gathers current mode, selection, current draft, last result / error, and saved Mix summaries. It passes only callable handlers into the pure builder and uses:

```python
_CONTEXT_ACTIONS = {"select_workspace_kind", "select_strategy"}
_DECISION_ACTIONS = {"save_and_move"}


def _new_component_intent(intent: dict[str, Any] | None, *, consumed_nonce: str | None) -> bool:
    nonce = str(dict(intent or {}).get("nonce") or "")
    return bool(nonce and nonce != consumed_nonce)
```

`app/web/backtest_analysis_workspace_panel.py` exposes:

```python
def render_backtest_analysis_workspace_fallback(
    workspace: dict[str, Any], *, surface: Literal["context", "decision"]
) -> dict[str, Any] | None:
```

The fallback reads only the read model. It must not execute runtime, history, saved-store, or candidate-source functions.

- [ ] **Step 4: Replace the radio with stable context and fragment**

```python
def render_backtest_analysis_workspace() -> None:
    workspace = build_current_backtest_analysis_workspace()
    render_backtest_analysis_context_surface(workspace)
    _render_backtest_analysis_work_fragment()


@st.fragment
def _render_backtest_analysis_work_fragment() -> None:
    if st.session_state.backtest_analysis_mode == BACKTEST_ANALYSIS_MODE_COMPARE:
        render_compare_portfolio_workspace()
    else:
        render_single_strategy_workspace()
```

Workspace / strategy selection uses app rerun. Strategy execution and result refresh remain inside the fragment.

- [ ] **Step 5: Preserve old result as stale**

Rename `_clear_last_run_if_strategy_selection_changed` to `_mark_last_run_stale_if_strategy_selection_changed`. Replace bundle clearing with:

```python
st.session_state.backtest_last_result_requires_rerun = True
st.session_state.backtest_last_result_reset_notice = (
    "현재 선택이 이전 실행과 달라 기존 결과를 참고용으로 유지합니다. "
    "현재 설정으로 다시 실행해야 Level2 전송이 열립니다."
)
```

- [ ] **Step 6: Record every current draft payload**

Add:

```python
def record_single_strategy_draft(payload: dict, *, strategy_name: str) -> str:
    normalized = normalize_single_strategy_payload(payload, strategy_name=strategy_name)
    selection = {"strategy_choice": st.session_state.get("backtest_strategy_choice"), "strategy_name": strategy_name}
    fingerprint = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy", selection=selection, configuration=normalized
    )
    st.session_state.backtest_current_draft_payload = normalized
    st.session_state.backtest_current_configuration_fingerprint = fingerprint
    return fingerprint
```

In all six non-factor forms and six strict factor variant forms, build the existing payload before `if not submitted: return`, call `record_single_strategy_draft`, and keep the runtime payload keys / defaults unchanged. Relabel groups as:

- universe controls: `Universe 상세`
- `Advanced Inputs`: `전략·보유 규칙`
- promotion / cost / guardrail: `비용·Guardrail`

- [ ] **Step 7: Stamp result and history fingerprint**

In `_handle_backtest_run`:

```python
fingerprint = record_single_strategy_draft(payload, strategy_name=strategy_name)
bundle = dict(result.bundle)
bundle["meta"] = dict(bundle.get("meta") or {})
bundle["meta"]["level1_configuration_fingerprint"] = fingerprint
st.session_state.backtest_last_configuration_fingerprint = fingerprint
st.session_state.backtest_last_bundle = bundle
append_backtest_run_history(
    bundle=bundle, run_kind="single_strategy",
    context={"level1_configuration_fingerprint": fingerprint},
)
```

Do not add candidate-source persistence here.

- [ ] **Step 8: Run GREEN and compatibility tests**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py -q -k "draft or backtest_analysis_context or marks_stale"
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "single_strategy or latest_run or run_history"
```

Expected: all selected tests pass without touching actual JSONL paths.

- [ ] **Step 9: Commit**

```bash
git add app/web/backtest_analysis_workspace.py app/web/backtest_analysis_workspace_panel.py app/web/backtest_analysis.py app/web/backtest_single_strategy.py app/web/backtest_single_runner.py app/web/backtest_single_forms tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py
git commit -m "Backtest Analysis 단일 전략 안정 컨텍스트 연결"
```

### Task 6: Decision-First Result, Explicit Handoff, Detailed Evidence

**Files:**
- Modify: `app/web/backtest_result_display.py`
- Modify: `app/web/backtest_analysis_workspace.py`
- Modify: `app/web/backtest_analysis_workspace_panel.py`
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 3 projection, current bundle, `_candidate_review_draft_from_bundle`, `_queue_candidate_review_draft`.
- Produces: React / fallback Step 3 + 4, `_render_last_run_details(bundle)`, explicit validated handoff.

- [ ] **Step 1: Write failing order and persistence tests**

Add a boundary test asserting the decision surface renders before `상세 근거`, and the detailed renderer does not call `_render_practical_validation_next_action(bundle)`.

Add a mocked test that supplies an enabled current projection and a real session bundle:

```python
from unittest.mock import MagicMock, patch


class _SessionState(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def test_explicit_intent_queues_candidate_once() -> None:
    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState({
        "backtest_last_bundle": {"strategy_name": "GTAA", "meta": {"strategy_key": "gtaa"}},
        "backtest_analysis_consumed_nonce": None,
    })
    current = {"actions": {"save_and_move": {"enabled": True}}}
    with (
        patch("app.web.backtest_analysis_workspace.st", fake_streamlit),
        patch("app.web.backtest_analysis_workspace.build_current_backtest_analysis_workspace", return_value=current),
        patch("app.web.backtest_analysis_workspace._candidate_review_draft_from_bundle", return_value={"source_kind": "latest_backtest_run"}),
        patch("app.web.backtest_analysis_workspace._queue_candidate_review_draft") as queue_candidate,
    ):
        consume_backtest_analysis_intent({"action": "save_and_move", "payload": {}, "nonce": "n-1"})
    queue_candidate.assert_called_once_with({"source_kind": "latest_backtest_run"})
```

The Task 5 runner test remains the proof that successful execution itself never calls `_queue_candidate_review_draft`.

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k "decision_first or explicit_intent or does_not_queue_candidate"`

Expected: failures because the current result screen renders header / trust / handoff directly.

- [ ] **Step 3: Split first-read from details**

Keep `_render_last_run()` as the compatibility entry. Extract current tabs, charts, tables, policy signals, and raw meta into `_render_last_run_details(bundle)`. Remove `_render_practical_validation_next_action(bundle)` from details. Render:

```python
render_backtest_analysis_decision_surface(workspace)
with st.expander("상세 근거", expanded=False):
    _render_last_run_details(bundle)
```

- [ ] **Step 4: Consume only an enabled explicit handoff**

```python
if action == "save_and_move":
    current = build_current_backtest_analysis_workspace()
    enabled = bool(dict(dict(current.get("actions") or {}).get("save_and_move") or {}).get("enabled"))
    bundle = st.session_state.get("backtest_last_bundle")
    if not enabled or not bundle:
        return
    _queue_candidate_review_draft(_candidate_review_draft_from_bundle(bundle))
    st.session_state.backtest_analysis_consumed_nonce = nonce
    st.rerun(scope="app")
```

The fallback reads the same decision / actions and does not reconstruct Gate from raw meta.

- [ ] **Step 5: Run GREEN, build, and compile**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k "backtest_analysis or latest_run or candidate_review_draft"
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile app/web/backtest_analysis_workspace.py app/web/backtest_analysis_workspace_panel.py app/web/backtest_single_strategy.py app/web/backtest_result_display.py
```

Expected: selected tests, build, and compilation pass.

- [ ] **Step 6: Commit**

```bash
git add app/web/backtest_result_display.py app/web/backtest_analysis_workspace.py app/web/backtest_analysis_workspace_panel.py app/web/backtest_single_strategy.py tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py
git commit -m "Backtest Analysis 단일 전략 판단과 명시적 인계 연결"
```

---

## 4차: Portfolio Mix One-Shell

### Task 7: Pure Mix Readiness, Role / Weight Contract, Replay Compatibility

**Files:**
- Modify: `app/services/backtest_portfolio_mix_readiness.py`
- Modify: `app/services/backtest_weighted_portfolio.py`
- Modify: `app/services/backtest_saved_portfolio_replay.py`
- Modify: `app/services/backtest_analysis_decision_workspace.py`
- Modify: `app/web/backtest_compare/page.py`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: web-owned `_build_weighted_mix_candidate_readiness_evaluation`, weighted inputs, legacy role-less saved records.
- Produces: `build_weighted_mix_candidate_readiness_evaluation()`, `build_mix_role_weight_rows()`, `resolve_saved_mix_component_roles()`, optional persisted `component_roles`.

- [ ] **Step 1: Write failing pure Mix tests**

```python
def test_mix_roles_and_weights_are_python_owned() -> None:
    rows = build_mix_role_weight_rows(
        strategy_names=["GTAA", "Global Relative Strength", "Risk Parity Trend"],
        weights_percent=[45.0, 35.0, 20.0],
        component_roles=["core", "growth", "defense"],
    )
    assert [row["role"] for row in rows] == ["core", "growth", "defense"]
    assert sum(row["weight_percent"] for row in rows) == 100.0
    assert all(row["valid"] for row in rows)


def test_legacy_saved_mix_without_roles_uses_inferred_roles() -> None:
    roles = resolve_saved_mix_component_roles(
        {"portfolio_context": {}},
        strategy_names=["GTAA", "Risk Parity Trend"],
    )
    assert roles == ["core", "defense"]


def test_mix_workspace_uses_role_weight_projection() -> None:
    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="portfolio_mix", selection={"mix_mode": "new"},
        configuration={
            "strategy_names": ["GTAA", "Risk Parity Trend"],
            "weights_percent": [50.0, 50.0],
            "component_roles": ["core", "defense"],
        },
        result_bundle=None, result_configuration_fingerprint=None,
        saved_mixes=[], last_error=None, last_error_kind=None,
        action_handlers={}, component_bundles=(),
    )
    assert workspace["mix"]["role_weight_rows"][0]["role_label"] == "Core"
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_service_contracts.py -q -k "mix_roles or inferred_roles or role_weight_projection"`

Expected: failures because pure role and readiness contracts do not exist.

- [ ] **Step 3: Move Mix readiness into the service layer**

Move the complete body of `_build_weighted_mix_candidate_readiness_evaluation` from `app/web/backtest_compare/page.py` to `app/services/backtest_portfolio_mix_readiness.py` as:

```python
def build_weighted_mix_candidate_readiness_evaluation(
    weighted_bundle: dict[str, Any] | None,
    component_bundles: list[dict[str, Any]],
) -> dict[str, Any]:
```

Replace web call sites with this public import. Use a temporary compatibility alias only if `rg` shows a direct external import; delete the alias once tests confirm no caller needs it.

- [ ] **Step 4: Implement role / weight truth**

```python
MIX_ROLE_OPTIONS = ("core", "growth", "defense", "satellite")
MIX_ROLE_LABELS = {"core": "Core", "growth": "Growth", "defense": "Defense", "satellite": "Satellite"}


def infer_mix_role(strategy_name: str) -> str:
    normalized = str(strategy_name).lower()
    if "risk parity" in normalized:
        return "defense"
    if "gtaa" in normalized or "equal weight" in normalized:
        return "core"
    if "relative strength" in normalized or "momentum" in normalized:
        return "growth"
    return "satellite"


def build_mix_role_weight_rows(
    *, strategy_names: list[str], weights_percent: list[float], component_roles: list[str] | None
) -> list[dict[str, object]]:
    roles = list(component_roles or [])
    if len(roles) != len(strategy_names):
        roles = [infer_mix_role(name) for name in strategy_names]
    return [
        {
            "strategy_name": name,
            "role": role,
            "role_label": MIX_ROLE_LABELS.get(role, role),
            "weight_percent": float(weight),
            "valid": role in MIX_ROLE_OPTIONS and float(weight) >= 0.0,
        }
        for name, weight, role in zip(strategy_names, weights_percent, roles)
    ]
```

- [ ] **Step 5: Persist roles without breaking saved records**

Add `component_roles: list[str] | None = None` to `build_weighted_portfolio_bundle`. Store supplied or inferred roles in `weighted_bundle["component_roles"]` and `weighted_bundle["meta"]["component_roles"]`.

Add to `backtest_saved_portfolio_replay.py`:

```python
def resolve_saved_mix_component_roles(record: dict[str, Any], *, strategy_names: list[str]) -> list[str]:
    portfolio_context = dict(record.get("portfolio_context") or {})
    roles = [str(role) for role in list(portfolio_context.get("component_roles") or [])]
    if len(roles) == len(strategy_names):
        return roles
    return [infer_mix_role(name) for name in strategy_names]
```

Saved replay calls this helper and passes the list into the weighted builder. Do not reject legacy records.

- [ ] **Step 6: Extend the Level1 read model for Mix**

For `workspace_kind == "portfolio_mix"`, add:

```python
"mix": {
    "role_weight_rows": build_mix_role_weight_rows(
        strategy_names=strategy_names,
        weights_percent=weights_percent,
        component_roles=component_roles,
    ),
    "total_weight_percent": round(sum(weights_percent), 4),
    "saved_entry_mode": str(selection.get("mix_mode") or "new"),
}
```

Use `build_weighted_mix_candidate_readiness_evaluation` for Mix handoff; do not reuse single-strategy meta heuristics.

Call it with the stable optional `component_bundles` argument introduced in Task 3.

- [ ] **Step 7: Run GREEN and commit**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_service_contracts.py -q -k "weighted_mix or saved_portfolio_replay or mix_role"
git add app/services/backtest_portfolio_mix_readiness.py app/services/backtest_weighted_portfolio.py app/services/backtest_saved_portfolio_replay.py app/services/backtest_analysis_decision_workspace.py app/web/backtest_compare/page.py tests/test_backtest_analysis_decision_workspace.py tests/test_service_contracts.py
git commit -m "Portfolio Mix 역할 비중과 인계 계약 서비스화"
```

Expected: selected tests pass before the commit.

### Task 8: Mix Step 1 / Step 2, Saved Mix, Persistence Separation

**Files:**
- Modify: `app/web/backtest_compare/page.py`
- Modify: `app/web/backtest_compare/components.py`
- Modify: `app/web/backtest_analysis_workspace.py`
- Modify: `app/web/backtest_analysis_workspace_panel.py`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 7 pure contract, `load_saved_portfolios`, `save_saved_portfolio`, replay and source handoff handlers.
- Produces: P1 inner mode, role selects, weighted fingerprint, `build_backtest_analysis_action_handlers()`, distinct `select_mix_mode` / `save_mix` / `save_and_move` intents.

- [ ] **Step 1: Write failing UI and persistence tests**

```python
def test_mix_save_and_candidate_handoff_use_different_handlers() -> None:
    handlers = build_backtest_analysis_action_handlers()
    assert callable(handlers["save_mix"])
    assert callable(handlers["save_and_move"])
    assert handlers["save_mix"] is not handlers["save_and_move"]


def test_zero_actions_do_not_render_empty_action_board() -> None:
    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="portfolio_mix",
        selection={"mix_mode": "new"},
        configuration={"strategy_names": [], "weights_percent": [], "component_roles": []},
        result_bundle=None,
        result_configuration_fingerprint=None,
        saved_mixes=[],
        last_error=None,
        last_error_kind=None,
        action_handlers={},
        component_bundles=(),
    )
    assert workspace["actions"] == {}
```

Add source assertions for `새 Mix 만들기`, `저장된 Mix 불러오기`, `mix_role_`, and absence of the visible call `_render_weighted_portfolio_practical_validation_panel(weighted_bundle)`.

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k "mix_save or zero_actions or portfolio_mix_workspace"`

Expected: failures because roles and distinct actions are not integrated.

- [ ] **Step 3: Put saved Mix inside Step 1**

Keep `COMPARE_MODE_STRATEGY` and `COMPARE_MODE_SAVED_MIX`, but display them under Step 1 as `새 Mix 만들기` and `저장된 Mix 불러오기`. Do not create a third top-level Level1 card.

The selected saved record first-read shows name, strategies, roles, weights, updated time, and `이 Mix로 계속`. Raw JSON stays under detailed evidence.

Extend the TypeScript `WorkspaceIntent` union and Python allowlist with `select_mix_mode` and `save_mix`. When `actions.save_mix.enabled` is true, the decision surface renders a Mix name and memo field and emits them as `payload.name` and `payload.description`. Add:

```python
def build_backtest_analysis_action_handlers() -> dict[str, Callable[..., Any]]:
    return {
        "save_mix": _save_current_weighted_mix,
        "save_and_move": _handoff_current_weighted_mix,
    }
```

The two values must remain different callables and are used only after nonce and current projection validation.

- [ ] **Step 4: Add roles beside weights**

```python
role = st.selectbox(
    f"{strategy_name} 역할",
    options=list(MIX_ROLE_OPTIONS),
    format_func=lambda value: MIX_ROLE_LABELS[value],
    key=f"mix_role_{strategy_name}",
)
```

Build `component_roles` in strategy order, show total weight and alignment from the pure service, and pass roles to `build_weighted_portfolio_bundle`.

- [ ] **Step 5: Stamp the weighted draft and result**

Build the fingerprint from selected strategies, roles, weights, date policy, and compare source context before submit. Store it in:

```python
st.session_state.backtest_current_mix_configuration_fingerprint
weighted_bundle["meta"]["level1_configuration_fingerprint"]
```

If fingerprints differ, preserve the weighted result as stale and disable save / handoff actions requiring a current result.

- [ ] **Step 6: Keep persistence handlers separate**

Extract the current save and handoff blocks into these adapter signatures:

```python
def _save_current_weighted_mix(payload: Mapping[str, Any]) -> dict[str, Any]:
    bundles = list(st.session_state.backtest_compare_bundles)
    return save_saved_portfolio(
        name=str(payload.get("name") or "").strip(),
        description=str(payload.get("description") or "").strip(),
        compare_context=_build_saved_portfolio_compare_context(bundles),
        portfolio_context=_build_saved_portfolio_context(
            bundles=bundles,
            weighted_bundle=st.session_state.backtest_weighted_bundle,
        ),
        source_context={
            "created_from": "backtest_analysis_decision_workspace",
            "source_strategy_names": [str(bundle.get("strategy_name") or "") for bundle in bundles],
            "compare_source_context": dict(
                st.session_state.get("backtest_compare_source_context") or {}
            ),
        },
    )


def _handoff_current_weighted_mix(payload: Mapping[str, Any]) -> None:
    weighted_bundle = st.session_state.backtest_weighted_bundle
    prefill = _build_weighted_mix_practical_validation_prefill_payload(weighted_bundle)
    source = build_selection_source_from_weighted_mix_prefill(prefill)
    _apply_practical_validation_source_handoff(source)
```

- `save_mix` calls only the first adapter, with roles included by `_build_saved_portfolio_context`.
- `save_and_move` calls only the second adapter.
- 기존 saved Mix의 `source_strategy_names`와 `compare_source_context`는 그대로 보존한다.
- weighted execution calls `append_backtest_run_history` once.
- React calls none of these functions.

Patch `SAVED_PORTFOLIO_FILE` and Practical Validation source persistence to temporary paths in tests.

- [ ] **Step 7: Replace the duplicate visible handoff panel**

After `_render_weighted_portfolio_result`, call the common Level1 decision surface. Remove the visible call to `_render_weighted_portfolio_practical_validation_panel(weighted_bundle)`. Delete the old function only after `rg` confirms there are no remaining imports or test contracts.

- [ ] **Step 8: Run GREEN, build, compile, and commit**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k "portfolio_mix or weighted_mix or saved_portfolio"
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile app/services/backtest_portfolio_mix_readiness.py app/services/backtest_weighted_portfolio.py app/services/backtest_saved_portfolio_replay.py app/web/backtest_compare/page.py
git add app/web/backtest_compare/page.py app/web/backtest_compare/components.py app/web/backtest_analysis_workspace.py app/web/backtest_analysis_workspace_panel.py app/web/components/backtest_analysis_decision_workspace/frontend/src tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py
git commit -m "Portfolio Mix 원셸 흐름과 저장 경계 연결"
```

Expected: tests, build, and compilation pass before commit.

---

## 5차: Runtime QA / Docs / Closeout

### Task 9: Fresh Verification, Browser QA, Docs, Protected-File Audit

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md` only if it describes the old Level1 contract.
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`.
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate, never stage: `backtest-analysis-level1-decision-workspace-desktop-qa.png`
- Generate, never stage: `backtest-analysis-level1-decision-workspace-760-qa.png`

**Interfaces:**
- Consumes: completed Task 1~8.
- Produces: fresh test / build / compile / Browser evidence and synchronized durable docs.

- [ ] **Step 1: Run fresh test suites**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q
```

Expected: zero failures. Record exact passed / skipped counts in `RUNS.md`.

- [ ] **Step 2: Run fresh React build**

```bash
cd app/web/components/backtest_analysis_decision_workspace/frontend
npm run build
```

Expected: Vite exits 0. Record transformed module count and output files.

- [ ] **Step 3: Run target compilation**

```bash
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_analysis_decision_workspace.py \
  app/services/backtest_strategy_catalog.py \
  app/services/backtest_portfolio_mix_readiness.py \
  app/services/backtest_weighted_portfolio.py \
  app/services/backtest_saved_portfolio_replay.py \
  app/web/backtest_analysis.py \
  app/web/backtest_analysis_workspace.py \
  app/web/backtest_analysis_workspace_panel.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_single_runner.py \
  app/web/backtest_result_display.py \
  app/web/backtest_compare/page.py
```

Expected: exit 0 with no output.

- [ ] **Step 4: Run desktop Browser QA**

Use `http://localhost:8505/backtest`. Restart only if the current process does not serve the new build. Verify:

1. fixed Level1 title while strategy changes;
2. only Single Strategy / Portfolio Mix entry cards;
3. purpose groups select GTAA and Quality + Value correctly;
4. Risk-On Momentum 5D shows `개발 중` and no Level2 CTA;
5. Universe / strategy-holding / cost-guardrail disclosures;
6. execution refresh keeps context mounted;
7. decision -> KPI -> data / action -> details order;
8. changed selection preserves stale result;
9. run alone does not hand off, explicit action does;
10. new / saved Mix inner mode;
11. roles, weights, total alignment;
12. separate save Mix and Level2 handoff effects.

Capture `backtest-analysis-level1-decision-workspace-desktop-qa.png` with result and action visible.

- [ ] **Step 5: Run 760px Browser QA**

At 760px verify outer page and both iframes have zero horizontal overflow, all grids are one column, long names wrap, CTAs use full width, ResizeObserver updates height, and context remains visible during result fragment refresh.

Capture `backtest-analysis-level1-decision-workspace-760-qa.png`.

- [ ] **Step 6: Run pre-doc diff and protection audit**

```bash
git diff --check
git status --short
git diff --cached --name-only
```

Expected: diff-check exits 0; registry, run history, saved JSONL, screenshots, build output, `.superpowers/` remain unstaged.

- [ ] **Step 7: Synchronize durable docs with `finance-doc-sync`**

- `BACKTEST_UI_FLOW.md`: Level1 question and Single / Mix four-step flow.
- `PROJECT_MAP.md`, `SCRIPT_STRUCTURE_MAP.md`: pure service, adapter, two surfaces, fragment ownership.
- task docs: completed 1~5 roadmap, commits, exact verification and Browser evidence.
- root logs: 3~5 line milestone / decision / handoff only.

- [ ] **Step 8: Repeat completion verification after docs edits**

Repeat Steps 1~3 and run:

```bash
git diff --check
git diff --name-only
```

Do not reuse pre-doc output as final evidence.

- [ ] **Step 9: Stage only closeout docs and verify exclusions**

```bash
git add \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
if git diff --cached --name-only | rg -q 'registries/|run_history/|saved/|\.superpowers/|\.png$'; then
  echo "protected path staged"
  exit 1
fi
```

Expected: staged diff-check passes and protected-path search returns no match.

- [ ] **Step 10: Commit closeout**

```bash
git commit -m "Backtest Analysis Level1 QA와 문서 동기화"
```

## Final Completion Report Contract

Final response must include:

- 전체 roadmap 1~5차 완료 상태;
- 생성한 한국어 commit 목록;
- fresh focused / boundary / service regression test counts;
- React build, target py_compile, diff-check results;
- desktop / 760px Browser QA 범위와 screenshot links;
- registry, run history, saved JSONL, generated artifact, `.superpowers/`가 commit되지 않았다는 audit;
- 남은 위험과 active task 위치.
