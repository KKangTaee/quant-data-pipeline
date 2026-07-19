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
| 6차 Single Settings Corrective | Task 10~13 | Python-owned settings hierarchy, all-strategy form cleanup |
| 7차 Unified React Settings | Task 14~20 | schema/intent/payload parity, React editor, route cutover, QA |
| 8차 Modifier-Free Multi-Select | Task 21~22 | adaptive compact/search control, Browser QA, docs sync |
| 9차 Deterministic Preset Application | Task 23~25 | Python preset profile, React/fallback application, Browser QA, docs sync |
| 10차 Result Evidence Workspace | Task 26~30 | truth/read model, React result UI, lifecycle/fallback cutover, QA/docs |

## File Ownership Map

### New Files

- `app/services/backtest_analysis_decision_workspace.py`: Level1 schema, fingerprint, strategy catalog projection, single / Mix result interpretation, freshness, action Gate.
- `tests/test_backtest_analysis_decision_workspace.py`: truth, read model, persistence-boundary unit tests.
- `app/web/backtest_analysis_workspace.py`: Streamlit state adapter, validated intent dispatcher, context / decision renderer.
- `app/web/backtest_analysis_workspace_panel.py`: same-read-model Python fallback.
- `app/web/components/backtest_analysis_decision_workspace/`: two-surface React component, wrapper, Vite project, responsive CSS.
- `app/services/backtest_analysis_result_workspace.py`: Level1 result lifecycle, technical handoff,
  Level2 questions, performance/chart/holdings/table/evidence projection.
- `tests/test_backtest_analysis_result_workspace.py`: result truth, holdings, Mix, lifecycle unit tests.
- `app/web/backtest_analysis_result_workspace.py`: Streamlit state adapter, validated handoff intent,
  React/fallback mount.
- `app/web/backtest_analysis_result_workspace_panel.py`: same-read-model Python fallback.
- `app/web/components/backtest_analysis_result_workspace/`: dedicated result React component,
  SVG chart, responsive holdings/evidence/table presentation.

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

- [x] **Step 1: Write failing intent-only and responsive tests**

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

- [x] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q -k "backtest_analysis_react"`

Expected: failures because the component files do not exist.

- [x] **Step 3: Create the Python wrapper**

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

- [x] **Step 4: Create TypeScript types and intent-only presentation**

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

- [x] **Step 5: Add continuous height sync**

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

- [x] **Step 6: Add visual tokens and 760px CSS**

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

- [x] **Step 7: Install, build, and run GREEN**

```bash
cd app/web/components/backtest_analysis_decision_workspace/frontend
npm install
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q -k "backtest_analysis_react"
```

Expected: Vite exits 0 and both new boundary tests pass.

- [x] **Step 8: Commit without `frontend/build`**

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

- [x] **Step 1: Write failing boundary and runner tests**

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

- [x] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py -q -k "draft or context_is_outside or marks_stale"`

Expected: failures because adapter, fragment, and stale marker do not exist.

- [x] **Step 3: Implement validated intent and fallback contracts**

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

- [x] **Step 4: Replace the radio with stable context and fragment**

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

- [x] **Step 5: Preserve old result as stale**

Rename `_clear_last_run_if_strategy_selection_changed` to `_mark_last_run_stale_if_strategy_selection_changed`. Replace bundle clearing with:

```python
st.session_state.backtest_last_result_requires_rerun = True
st.session_state.backtest_last_result_reset_notice = (
    "현재 선택이 이전 실행과 달라 기존 결과를 참고용으로 유지합니다. "
    "현재 설정으로 다시 실행해야 Level2 전송이 열립니다."
)
```

- [x] **Step 6: Record the submitted current draft payload**

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

Streamlit forms do not send changed widget values to Python until submit. Keep every form's
runtime payload keys / defaults unchanged and record the normalized payload at the shared
runner boundary before execution. This avoids duplicating twelve payload builders while still
making a failed new execution mark the preserved prior result stale. Relabel groups as:

- universe controls: `Universe 상세`
- `Advanced Inputs`: `전략·보유 규칙`
- promotion / cost / guardrail: `비용·Guardrail`

- [x] **Step 7: Stamp result and history fingerprint**

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

- [x] **Step 8: Run GREEN and compatibility tests**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py -q -k "draft or backtest_analysis_context or marks_stale"
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k "single_strategy or latest_run or run_history"
```

Expected: all selected tests pass without touching actual JSONL paths.

- [x] **Step 9: Commit**

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

- [x] **Step 1: Write failing order and persistence tests**

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

- [x] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k "decision_first or explicit_intent or does_not_queue_candidate"`

Expected: failures because the current result screen renders header / trust / handoff directly.

- [x] **Step 3: Split first-read from details**

Keep `_render_last_run()` as the compatibility entry. Extract current tabs, charts, tables, policy signals, and raw meta into `_render_last_run_details(bundle)`. Remove `_render_practical_validation_next_action(bundle)` from details. Render:

```python
render_backtest_analysis_decision_surface(workspace)
with st.expander("상세 근거", expanded=False):
    _render_last_run_details(bundle)
```

- [x] **Step 4: Consume only an enabled explicit handoff**

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

- [x] **Step 5: Run GREEN, build, and compile**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k "backtest_analysis or latest_run or candidate_review_draft"
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile app/web/backtest_analysis_workspace.py app/web/backtest_analysis_workspace_panel.py app/web/backtest_single_strategy.py app/web/backtest_result_display.py
```

Expected: selected tests, build, and compilation pass.

- [x] **Step 6: Commit**

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

- [x] **Step 1: Write failing pure Mix tests**

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

- [x] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_service_contracts.py -q -k "mix_roles or inferred_roles or role_weight_projection"`

Expected: failures because pure role and readiness contracts do not exist.

- [x] **Step 3: Move Mix readiness into the service layer**

Move the complete body of `_build_weighted_mix_candidate_readiness_evaluation` from `app/web/backtest_compare/page.py` to `app/services/backtest_portfolio_mix_readiness.py` as:

```python
def build_weighted_mix_candidate_readiness_evaluation(
    weighted_bundle: dict[str, Any] | None,
    component_bundles: list[dict[str, Any]],
) -> dict[str, Any]:
```

Replace web call sites with this public import. Use a temporary compatibility alias only if `rg` shows a direct external import; delete the alias once tests confirm no caller needs it.

- [x] **Step 4: Implement role / weight truth**

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

- [x] **Step 5: Persist roles without breaking saved records**

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

- [x] **Step 6: Extend the Level1 read model for Mix**

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

- [x] **Step 7: Run GREEN and commit**

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

- [x] **Step 1: Write failing UI and persistence tests**

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

- [x] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k "mix_save or zero_actions or portfolio_mix_workspace"`

Expected: failures because roles and distinct actions are not integrated.

- [x] **Step 3: Put saved Mix inside Step 1**

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

- [x] **Step 4: Add roles beside weights**

```python
role = st.selectbox(
    f"{strategy_name} 역할",
    options=list(MIX_ROLE_OPTIONS),
    format_func=lambda value: MIX_ROLE_LABELS[value],
    key=f"mix_role_{strategy_name}",
)
```

Build `component_roles` in strategy order, show total weight and alignment from the pure service, and pass roles to `build_weighted_portfolio_bundle`.

- [x] **Step 5: Stamp the weighted draft and result**

Build the fingerprint from selected strategies, roles, weights, date policy, and compare source context before submit. Store it in:

```python
st.session_state.backtest_current_mix_configuration_fingerprint
weighted_bundle["meta"]["level1_configuration_fingerprint"]
```

If fingerprints differ, preserve the weighted result as stale and disable save / handoff actions requiring a current result.

- [x] **Step 6: Keep persistence handlers separate**

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

- [x] **Step 7: Replace the duplicate visible handoff panel**

After `_render_weighted_portfolio_result`, call the common Level1 decision surface. Remove the visible call to `_render_weighted_portfolio_practical_validation_panel(weighted_bundle)`. Delete the old function only after `rg` confirms there are no remaining imports or test contracts.

- [x] **Step 8: Run GREEN, build, compile, and commit**

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

- [x] **Step 1: Run fresh test suites**

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q
```

Expected: Level1 신규 failure 0. Repository baseline에 이미 존재하는 실패는 시작 전
목록과 정확히 대조하고 exact count를 `RUNS.md`에 기록한다.

- [x] **Step 2: Run fresh React build**

```bash
cd app/web/components/backtest_analysis_decision_workspace/frontend
npm run build
```

Expected: Vite exits 0. Record transformed module count and output files.

- [x] **Step 3: Run target compilation**

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

- [x] **Step 4: Run desktop Browser QA**

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

- [x] **Step 5: Run 760px Browser QA**

At 760px verify outer page and both iframes have zero horizontal overflow, all grids are one column, long names wrap, CTAs use full width, ResizeObserver updates height, and context remains visible during result fragment refresh.

Capture `backtest-analysis-level1-decision-workspace-760-qa.png`.

- [x] **Step 6: Run pre-doc diff and protection audit**

```bash
git diff --check
git status --short
git diff --cached --name-only
```

Expected: diff-check exits 0; registry, run history, saved JSONL, screenshots, build output, `.superpowers/` remain unstaged.

- [x] **Step 7: Synchronize durable docs with `finance-doc-sync`**

- `BACKTEST_UI_FLOW.md`: Level1 question and Single / Mix four-step flow.
- `PROJECT_MAP.md`, `SCRIPT_STRUCTURE_MAP.md`: pure service, adapter, two surfaces, fragment ownership.
- task docs: completed 1~5 roadmap, commits, exact verification and Browser evidence.
- root logs: 3~5 line milestone / decision / handoff only.

- [x] **Step 8: Repeat completion verification after docs edits**

Repeat Steps 1~3 and run:

```bash
git diff --check
git diff --name-only
```

Do not reuse pre-doc output as final evidence.

- [x] **Step 9: Stage only closeout docs and verify exclusions**

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

- [x] **Step 10: Commit closeout**

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

---

## 6차: Single Strategy Settings Workspace Corrective

### Task 10: Shared Settings Shell And Single Selection Boundary

**Files:**
- Create: `app/web/backtest_single_settings_workspace.py`
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: `LEVEL1_STRATEGY_PURPOSE_GROUPS`, `LEVEL1_STRATEGY_MATURITY`,
  `resolve_concrete_strategy_display_name()`, existing family variant session keys.
- Produces: `build_single_strategy_settings_summary()`,
  `render_single_strategy_settings_header()`, `single_settings_section()`,
  `build_compact_ticker_summary()`.

- [x] **Step 1: Write RED tests for summary and unique selection surface**

```python
def test_single_settings_summary_projects_purpose_variant_and_maturity():
    summary = build_single_strategy_settings_summary(
        "Quality + Value",
        "Strict Annual",
    )
    assert summary == {
        "strategy_choice": "Quality + Value",
        "display_name": "Quality + Value Snapshot (Strict Annual)",
        "variant": "Strict Annual",
        "purpose": "팩터 기반 종목 선정",
        "maturity": "production",
        "maturity_label": "운영 전략",
        "description": "기업의 품질과 가치평가를 함께 비교해 보유 후보를 고릅니다.",
    }


def test_single_workspace_has_no_duplicate_strategy_or_variant_selectbox():
    source = Path("app/web/backtest_single_strategy.py").read_text()
    assert 'st.selectbox(\n        "Strategy"' not in source
    assert 'f"{strategy_choice} Variant"' not in source
    assert "render_single_strategy_settings_header(" in source
```

Add a React boundary assertion that Single Strategy no longer renders the separate
`current_work` aside because the selected card state plus Python settings header own that
summary. Portfolio Mix keeps its current-work summary.

- [x] **Step 2: Run RED**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py -q \
  -k "single_settings or duplicate_strategy or current_work"
```

Expected: import / source assertions fail because the shared shell does not exist and the
duplicate selectboxes remain.

- [x] **Step 3: Implement the shared shell and compact variant selector**

Create `app/web/backtest_single_settings_workspace.py` with:

```python
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import streamlit as st

from app.services.backtest_strategy_catalog import (
    LEVEL1_STRATEGY_MATURITY,
    LEVEL1_STRATEGY_PURPOSE_GROUPS,
    resolve_concrete_strategy_display_name,
)

_STRATEGY_DESCRIPTIONS = {
    "Quality + Value": "기업의 품질과 가치평가를 함께 비교해 보유 후보를 고릅니다.",
    "Quality": "수익성과 재무 건전성이 상대적으로 좋은 기업을 고릅니다.",
    "Value": "기초가치 대비 가격 부담이 낮은 기업을 고릅니다.",
    "GTAA": "자산군의 상대강도와 추세를 비교해 공격·방어 자산을 선택합니다.",
    "Global Relative Strength": "글로벌 자산군의 상대강도를 비교해 상위 자산을 보유합니다.",
    "Dual Momentum": "상대·절대 모멘텀을 함께 확인해 공격·방어 자산을 선택합니다.",
    "Risk Parity Trend": "변동성과 추세를 함께 사용해 자산별 위험 기여를 조정합니다.",
    "Equal Weight": "선택한 자산을 같은 비중으로 보유하고 정해진 주기로 조정합니다.",
    "Risk-On Momentum 5D": "단기 위험선호 종목을 탐색하는 개발 중 전략입니다.",
}


def build_single_strategy_settings_summary(
    strategy_choice: str,
    selected_variant: str | None,
) -> dict[str, str | None]:
    purpose = next(
        (
            group["label"]
            for group in LEVEL1_STRATEGY_PURPOSE_GROUPS.values()
            if strategy_choice in group["items"]
        ),
        "기타 전략",
    )
    maturity = LEVEL1_STRATEGY_MATURITY.get(strategy_choice, "development")
    return {
        "strategy_choice": strategy_choice,
        "display_name": resolve_concrete_strategy_display_name(
            strategy_choice, selected_variant
        ),
        "variant": selected_variant,
        "purpose": purpose,
        "maturity": maturity,
        "maturity_label": "운영 전략" if maturity == "production" else "개발 중",
        "description": _STRATEGY_DESCRIPTIONS[strategy_choice],
    }


@contextmanager
def single_settings_section(title: str, description: str) -> Iterator[None]:
    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.caption(description)
        yield
```

`render_single_strategy_settings_header()` renders light-theme scoped summary HTML and, only
for family strategies, `st.segmented_control("실행 기준", ...)` using the existing variant
session key. It returns the selected variant so dispatch and stale detection use the same value.

In `backtest_single_strategy.py`, resolve / repair session selection as today, read
`strategy_choice` directly from session state, call the shared header, and remove both legacy
selectboxes. In React, render `current_work` aside only for `portfolio_mix`.

- [x] **Step 4: Run GREEN, build, and compile**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py -q
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_single_strategy.py
git diff --check
```

Expected: focused tests, React build, compile, diff-check pass.

- [x] **Step 5: Commit Task 10**

```bash
git add \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_single_strategy.py \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py
git commit -m "Backtest Analysis 단일 전략 설정 셸 도입"
```

### Task 11: Tactical And Allocation Form Hierarchy

**Files:**
- Modify: `app/web/backtest_common.py`
- Modify: `app/web/backtest_single_forms/equal_weight.py`
- Modify: `app/web/backtest_single_forms/gtaa.py`
- Modify: `app/web/backtest_single_forms/global_relative_strength.py`
- Modify: `app/web/backtest_single_forms/risk_parity.py`
- Modify: `app/web/backtest_single_forms/dual_momentum.py`
- Modify: `app/web/backtest_single_forms/risk_on_momentum.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 10 `single_settings_section()` and existing widget / payload keys.
- Produces: common five-section form hierarchy and compact universe evidence for six
  non-family strategies.

- [x] **Step 1: Write RED visual and compatibility contracts**

Add source contracts that require each form to use these ordered labels:

```python
section_labels = [
    "핵심 실행 설정",
    "투자 대상 Universe",
    "선택·보유 규칙",
    "비용·위험 기준",
]
for path in tactical_form_paths:
    source = path.read_text()
    offsets = [source.index(label) for label in section_labels]
    assert offsets == sorted(offsets), path.name
    assert 'form_submit_button("이 설정으로 백테스트 실행"' in source
```

Add a pure compact ticker test:

```python
summary = build_compact_ticker_summary(
    ["AAPL", "MSFT", "GOOG", "AMZN", "META"], preview_count=3
)
assert summary["headline"] == "선택 종목 5개 · 대표 AAPL, MSFT, GOOG"
assert summary["full_text"] == "AAPL, MSFT, GOOG, AMZN, META"
```

Keep existing payload key / prefill contract assertions green.

- [x] **Step 2: Run RED**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py -q \
  -k "single_strategy_form_hierarchy or compact_ticker or prefill"
```

Expected: hierarchy and compact summary assertions fail; existing compatibility tests pass.

- [x] **Step 3: Implement compact universe and six form layouts**

- Change `_render_ticker_preview()` to show `선택 종목 N개 · 대표 ...` first and keep the
  full list under `전체 종목 보기` disclosure.
- Keep `Preset` / `Manual` session values but show them through Korean `format_func` labels.
- Move primary period and main strategy controls outside the submit form into
  `핵심 실행 설정` so they appear before Universe and can rerun only the work fragment.
- Wrap immediate universe controls in `투자 대상 Universe`.
- Keep strategy / overlay inputs inside a borderless form under `선택·보유 규칙` and
  execution cost / benchmark / liquidity / guardrail under `비용·위험 기준`.
- Replace fixed `Timeframe=1d` and `Option=month_end` selectboxes with local constants while
  preserving identical payload values.
- Use Korean labels/help and `이 설정으로 백테스트 실행` submit copy.
- Keep every existing widget key, payload key, validation, prefill, handler call unchanged.

- [x] **Step 4: Run GREEN and focused regressions**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py -q \
  -k "single_strategy_form_hierarchy or compact_ticker or prefill or equal_weight or gtaa or global_relative_strength or risk_parity or dual_momentum or risk_on"
.venv/bin/python -m py_compile \
  app/web/backtest_common.py \
  app/web/backtest_single_forms/equal_weight.py \
  app/web/backtest_single_forms/gtaa.py \
  app/web/backtest_single_forms/global_relative_strength.py \
  app/web/backtest_single_forms/risk_parity.py \
  app/web/backtest_single_forms/dual_momentum.py \
  app/web/backtest_single_forms/risk_on_momentum.py
git diff --check
```

Expected: selected regressions and compilation pass without touching runtime JSONL.

- [x] **Step 5: Commit Task 11**

```bash
git add \
  app/web/backtest_common.py \
  app/web/backtest_single_forms/equal_weight.py \
  app/web/backtest_single_forms/gtaa.py \
  app/web/backtest_single_forms/global_relative_strength.py \
  app/web/backtest_single_forms/risk_parity.py \
  app/web/backtest_single_forms/dual_momentum.py \
  app/web/backtest_single_forms/risk_on_momentum.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py
git commit -m "Backtest Analysis 전술 전략 설정 흐름 통일"
```

### Task 12: Strict Factor Seven-Variant Settings Hierarchy

**Files:**
- Modify: `app/web/backtest_single_forms/strict_factor.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 10 sections, Task 11 compact universe and unchanged strict-factor helpers.
- Produces: Korean-first five-section flow for Quality / Value / Quality+Value annual and
  quarterly variants plus legacy Quality Snapshot replay path.

- [x] **Step 1: Write RED contracts for all concrete strict variants**

Assert that all seven renderer bodies contain the ordered section labels, Korean submit copy,
and no first-read raw phrases:

```python
for body in strict_variant_bodies:
    offsets = [body.index(label) for label in section_labels]
    assert offsets == sorted(offsets)
    assert "이 설정으로 백테스트 실행" in body

strict_source = strict_factor_path.read_text()
for raw_copy in (
    "Strict annual multi-factor strategy.",
    "Hidden defaults in this first pass",
    "Current mode:",
    "Selected tickers (300):",
):
    assert raw_copy not in strict_source
```

Retain service contracts that verify annual / quarterly strategy keys, factor arrays,
universe contract, costs, overlay, guardrail, and prefill mappings.

- [x] **Step 2: Run RED**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py -q \
  -k "strict_factor_settings_hierarchy or strict_annual or strict_quarterly or prefill"
```

Expected: hierarchy / Korean-first assertions fail on the legacy strict form source.

- [x] **Step 3: Refactor the seven renderer bodies without changing payloads**

For each renderer:

1. replace the English heading/caption with the shared selected-strategy header ownership;
2. render date / Top N under `핵심 실행 설정` before universe;
3. render preset/manual, compact ticker, PIT/readiness one-line status under
   `투자 대상 Universe`;
4. keep complete PIT / statement / membership evidence under `Universe 근거`;
5. group factor, overlay, weighting, rejected-slot, defensive rules under
   `선택·보유 규칙`;
6. group cost, benchmark, liquidity, promotion thresholds, drawdown guardrails under
   `비용·위험 기준`;
7. submit with Korean copy while preserving all widget keys and payload fields.

Do not change `_handle_backtest_run()` calls, concrete `strategy_key`, `statement_freq`,
`universe_contract`, factor default arrays, or prefill conversion.

- [x] **Step 4: Run GREEN, full strict regressions, and compile**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py -q \
  -k "strict_factor or quality_snapshot or value_snapshot or quality_value or prefill"
.venv/bin/python -m py_compile app/web/backtest_single_forms/strict_factor.py
git diff --check
```

Expected: strict hierarchy and existing runtime / payload compatibility tests pass.

- [x] **Step 5: Commit Task 12**

```bash
git add \
  app/web/backtest_single_forms/strict_factor.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py
git commit -m "Backtest Analysis 팩터 전략 설정 흐름 통일"
```

### Task 13: Runtime QA, Docs, And Corrective Closeout

**Files:**
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`, `PLAN.md`.
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate, never stage: `backtest-analysis-level1-single-settings-desktop-qa.png`
- Generate, never stage: `backtest-analysis-level1-single-settings-760-qa.png`

**Interfaces:**
- Consumes: Task 10~12.
- Produces: actual runtime evidence, responsive screenshots, canonical docs, protected-path audit.

- [x] **Step 1: Run fresh verification**

```bash
uv run --with pytest python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_common.py \
  app/web/backtest_single_forms/*.py
git diff --check
```

Record exact counts and compare service failures to the known 11-failure baseline.

- [x] **Step 2: Run desktop Browser QA**

At `http://localhost:8505/backtest`, verify Quality + Value Strict Annual first, then Equal
Weight, GTAA, Risk Parity, Dual Momentum, GRS, and development Risk-On:

1. no duplicate Strategy selectbox;
2. family variant segmented control changes Annual / Quarterly;
3. one selected settings summary;
4. common section order and Korean submit copy;
5. compact 300-ticker summary and collapsed full evidence;
6. actual Quality + Value and Equal Weight execution;
7. fresh -> strategy change stale preservation;
8. no automatic Level2 handoff;
9. development strategy remains handoff-blocked.

Capture `backtest-analysis-level1-single-settings-desktop-qa.png`.

- [x] **Step 3: Run 760px Browser QA**

Verify summary grid, segmented control, setting cards, disclosures, input labels, and CTA have
zero horizontal overflow and readable one-column flow. Capture
`backtest-analysis-level1-single-settings-760-qa.png`.

- [x] **Step 4: Synchronize docs and task evidence**

Use `finance-doc-sync` to document the shared settings shell, unique selection ownership,
variant segmented control, five-section form hierarchy, verification counts, Browser evidence,
and remaining baseline risks.

- [x] **Step 5: Stage only closeout files and audit protection**

```bash
git diff --check
git add \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
if git diff --cached --name-only | rg -q 'registries/|run_history/|saved/|\.superpowers/|\.png$'; then
  exit 1
fi
```

- [x] **Step 6: Commit corrective closeout**

```bash
git commit -m "Backtest Analysis 단일 전략 설정 QA와 문서 동기화"
```

## 6차 Completion Report Contract

- 6차 Task 10~13 완료 상태;
- corrective commit 목록;
- focused / boundary / service counts and known baseline comparison;
- React build / target py_compile / diff-check;
- desktop / 760px QA scope and screenshot links;
- protected registry / history / saved / `.superpowers/` / screenshots exclusion;
- remaining risks and active task location.

---

## 7차: Unified React Strategy Settings Workspace

### 7차 Goal And Architecture Amendment

6차에서 공통 정보 계층만 적용하고 보존했던 strategy-specific native Streamlit form을
primary 경로에서 제거한다. Python pure service가 9개 strategy choice / 13개 concrete
variant의 profile, field schema, option, default, validation, payload projection을 소유하고,
기존 `backtest_analysis_decision_workspace` React bundle은 supplied schema를 동일한 visual
language로 렌더링한다. React는 `{strategy_choice, variant, values}` intent만 전달하며
Python이 current selection, allow-list, type, range, option, visibility를 검증한 뒤 기존
`_handle_backtest_run(payload, strategy_name)`을 호출한다.

### 7차 File Ownership Map

- Create `app/services/backtest_single_settings_workspace.py`: pure schema catalog, draft
  validation, payload projection, field/user error projection.
- Create `tests/test_backtest_single_settings_workspace.py`: 13-variant coverage, payload parity,
  invalid draft, hidden-field, unknown-option contracts.
- Modify `app/web/backtest_single_settings_workspace.py`: runtime option/session/prefill adapter,
  component callback, same-read-model generic fallback.
- Modify `app/web/backtest_single_strategy.py`: primary React settings route, variant routing,
  stale-result preservation.
- Modify `app/web/backtest_analysis_workspace.py`: settings intent allow-list and callable handler
  dispatch.
- Modify `app/web/components/backtest_analysis_decision_workspace/component.py`: `settings`
  surface Python wrapper contract.
- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts`:
  settings read model and intent TypeScript types.
- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/index.tsx`:
  settings surface selection without changing `ResizeObserver` height sync.
- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`:
  schema-driven profile, fields, disclosure, validation, CTA.
- Modify `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`:
  desktop two-column and 760px one-column settings layout.
- Modify `tests/test_backtest_analysis_decision_workspace.py`: Python intent/handler/state
  integration.
- Modify `tests/test_backtest_refactor_boundaries.py`: React source/build, primary-route, fallback,
  protected-boundary contracts.
- Modify `tests/test_service_contracts.py`: representative runtime payload/prefill compatibility.
- Keep `app/web/backtest_single_forms/*.py` temporarily as non-primary compatibility references;
  do not call them from the normal React route after Task 19.

### Task 14: Pure Settings Schema, Validation, And Projection Foundation

**Files:**
- Create: `app/services/backtest_single_settings_workspace.py`
- Create: `tests/test_backtest_single_settings_workspace.py`

**Interfaces:**
- Consumes: JSON-ready scalar/list inputs and runtime-supplied option catalogs only; it does not
  import Streamlit or `app.web`.
- Produces: `SETTINGS_SCHEMA_VERSION`, `SINGLE_SETTINGS_CONCRETE_KEYS`,
  `build_single_settings_workspace(strategy_choice, variant, values, runtime_options)`,
  `validate_single_settings_draft(workspace, values)`, and
  `project_single_settings_payload(workspace, values)`.

- [x] **Step 1: Write RED coverage and schema-shape tests**

```python
EXPECTED = {
    "Equal Weight": (None,),
    "GTAA": (None,),
    "Global Relative Strength": (None,),
    "Risk Parity": (None,),
    "Dual Momentum": (None,),
    "Risk-On Momentum 5D": (None,),
    "Quality": ("Annual", "Quarterly", "Snapshot"),
    "Value": ("Annual", "Quarterly"),
    "Quality + Value": ("Annual", "Quarterly"),
}

def test_schema_covers_every_concrete_variant_once():
    assert SINGLE_SETTINGS_CONCRETE_KEYS == EXPECTED
    for choice, variants in EXPECTED.items():
        for variant in variants:
            workspace = build_single_settings_workspace(
                choice, variant, {}, runtime_options={}
            )
            assert workspace["schema_version"] == "backtest_single_settings_workspace_v2"
            assert [section["section_id"] for section in workspace["sections"]] == [
                "execution", "universe", "rules", "risk"
            ]
            assert workspace["action"]["id"] == "run_single_strategy"
```

Also assert field ids and payload keys are unique, controls are one of `date`, `number`, `text`,
`single_select`, `multi_select`, `segmented`, `toggle`, profile badges are plain strings, and every
field has Korean first-read `label` and `help`.

- [x] **Step 2: Run RED and confirm the module is absent**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py -q \
  -k "schema or concrete_variant or control"
```

Expected: collection fails with `ModuleNotFoundError` for the new pure service.

- [x] **Step 3: Implement immutable schema primitives and four-section projection**

Define typed dictionaries/dataclasses equivalent to:

```python
SETTINGS_SCHEMA_VERSION = "backtest_single_settings_workspace_v2"
ALLOWED_CONTROLS = frozenset({
    "date", "number", "text", "single_select", "multi_select", "segmented", "toggle"
})

def field(field_id, payload_key, label, control, default, **metadata): ...
def section(section_id, title, description, fields, disclosures=()): ...
def build_single_settings_workspace(
    strategy_choice: str,
    variant: str | None,
    values: Mapping[str, object] | None,
    runtime_options: Mapping[str, object] | None,
) -> dict[str, object]: ...
```

Return JSON-ready copies so callers cannot mutate module-level definitions. Implement the 13-key
registry and explicit invalid strategy/variant `ValueError` messages before strategy-specific
payload fields are added in Tasks 15~16.

- [x] **Step 4: Add RED validator tests for injection and type/range/option errors**

```python
def test_validator_rejects_unknown_hidden_and_invalid_fields():
    workspace = build_single_settings_workspace("Equal Weight", None, {}, RUNTIME_OPTIONS)
    errors = validate_single_settings_draft(workspace, {
        "unknown": "x", "rebalance_interval": 0, "preset_name": "not-allowed"
    })
    assert errors["unknown"] == "허용되지 않은 설정입니다."
    assert "최솟값" in errors["rebalance_interval"]
    assert "선택할 수 없는 값" in errors["preset_name"]
```

Add a conditional field fixture and assert a submitted hidden value is rejected. Assert invalid
date, number, toggle, text, list, required value, and duplicate multi-select option errors.

- [x] **Step 5: Implement validator and payload projector, then run GREEN**

Validation order is identity -> unknown field -> visibility -> required -> control type -> range
-> supplied options. `project_single_settings_payload()` must raise `SettingsValidationError`
containing field errors and must only copy declared `payload_key` values plus schema-owned constant
payload values.

```bash
uv run --with pytest python -m pytest tests/test_backtest_single_settings_workspace.py -q
.venv/bin/python -m py_compile app/services/backtest_single_settings_workspace.py
git diff --check
```

Expected: foundation tests pass with no Streamlit import in the service.

- [x] **Step 6: Commit Task 14**

```bash
git add app/services/backtest_single_settings_workspace.py \
  tests/test_backtest_single_settings_workspace.py
git commit -m "Backtest Analysis React 설정 스키마 기반 구축"
```

### Task 15: Tactical And Allocation Strategy Payload Parity

**Files:**
- Modify: `app/services/backtest_single_settings_workspace.py`
- Modify: `tests/test_backtest_single_settings_workspace.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 14 schema primitives and runtime option names `presets`, `tickers`,
  `defensive_tickers`, `benchmarks`, `score_horizons`, `policy_signal_options`.
- Produces: complete Equal Weight, GTAA, Global Relative Strength, Risk Parity, Dual Momentum,
  Risk-On Momentum 5D schemas and payloads compatible with existing runners.

- [x] **Step 1: Write RED golden payload tests for the six strategy groups**

For representative drafts assert exact payload dictionaries, including:

```python
assert project("Equal Weight", values) == {
    "strategy_key": "equal_weight", "tickers": ["VIG", "SCHD"],
    "start": "2016-01-01", "end": "2026-07-18", "timeframe": "1Day",
    "option": "backtest", "rebalance_interval": 12, "min_price_filter": 5.0,
    "transaction_cost_bps": 10.0, "benchmark_ticker": "SPY",
    "promotion_min_etf_aum_b": 1.0, "promotion_max_bid_ask_spread_pct": 0.25,
    "universe_mode": "preset", "preset_name": "Dividend ETFs",
}
```

Add complete expected key sets for GTAA (including score/trend/regime/crash and guardrails), GRS,
Risk Parity, Dual Momentum, and Risk-On (execution/exit/ATR/macro/liquidity/random/comparison flags).
Assert Python defaults reproduce current renderer defaults when `values={}`.

- [x] **Step 2: Run RED and record missing field/key failures**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py \
  tests/test_service_contracts.py -q \
  -k "equal_weight or gtaa or global_relative_strength or risk_parity or dual_momentum or risk_on"
```

Expected: exact payload tests fail because Task 14 only provides base schema fields.

- [x] **Step 3: Add the six complete declarative schemas**

Map every existing renderer payload key to one field or an explicit schema-owned constant. Place
date/timeframe/rebalance/holding count in `execution`; preset/manual/tickers/cash/benchmark universe
inputs in `universe`; score/trend/regime/exit/macro rules in `rules`; cost/liquidity/promotion/
guardrail fields in `risk`. Mark secondary controls `advanced=True` so React puts them in the
technical disclosure without changing payload availability.

The service must receive preset members and option labels through `runtime_options`; it must not
copy `EQUAL_WEIGHT_PRESETS`, `GTAA_PRESETS`, or other `app.web.backtest_common` constants.

- [x] **Step 4: Run GREEN and compare exact payload keys**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py \
  tests/test_service_contracts.py -q \
  -k "settings_workspace and (equal_weight or gtaa or global_relative_strength or risk_parity or dual_momentum or risk_on)"
.venv/bin/python -m py_compile app/services/backtest_single_settings_workspace.py
git diff --check
```

Expected: six strategy groups have no missing/extra payload key and existing handler signatures are
unchanged.

- [x] **Step 5: Commit Task 15**

```bash
git add app/services/backtest_single_settings_workspace.py \
  tests/test_backtest_single_settings_workspace.py tests/test_service_contracts.py
git commit -m "Backtest Analysis 전술 전략 React 설정 계약 이관"
```

### Task 16: Strict Factor Seven-Variant Payload Parity

**Files:**
- Modify: `app/services/backtest_single_settings_workspace.py`
- Modify: `tests/test_backtest_single_settings_workspace.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 14 projection and runtime options for PIT universe, factor families, weighting,
  overlays, benchmarks, guardrails, promotion thresholds.
- Produces: Quality Annual/Quarterly/Snapshot, Value Annual/Quarterly, Quality + Value
  Annual/Quarterly schemas and exact payload projection.

- [x] **Step 1: Write RED annual/quarterly/snapshot parity tests**

Assert exact concrete strategy keys and complete key sets for all seven variants. Required invariant
examples:

```python
assert annual["statement_freq"] == "annual"
assert quarterly["statement_freq"] == "quarterly"
assert snapshot["strategy_key"] == "quality_snapshot"
assert annual["universe_contract"] == "pit_monthly_snapshot"
assert annual["quality_factors"] == submitted_quality_factors
assert value_annual["value_factors"] == submitted_value_factors
assert combined["quality_factors"] and combined["value_factors"]
```

Also assert Top N, factor coverage, rejected-slot policy, overlay, defensive holding, weighting,
cost, liquidity, promotion, benchmark, underperformance/drawdown guardrails, preset/manual and PIT
membership values survive projection without renaming.

- [x] **Step 2: Run RED and capture missing strict-field failures**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py \
  tests/test_service_contracts.py -q \
  -k "settings_workspace and (quality or value or strict or snapshot)"
```

Expected: strict-factor key/constant/default assertions fail.

- [x] **Step 3: Add seven concrete schema builders without factor-domain duplication**

Use shared schema fragments for dates, PIT universe, factor selection, rejected slots, overlays,
weighting, cost/liquidity, and guardrails. Each concrete registration must explicitly supply its
`strategy_key`, `statement_freq`, allowed factor families, default factor arrays, and variant label.
Snapshot omits fields its existing payload does not accept rather than submitting empty annual
fields. All detailed PIT/readiness text goes in supplied evidence/disclosure, not first-read fields.

- [x] **Step 4: Run GREEN, legacy prefill regressions, and compile**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py \
  tests/test_service_contracts.py -q \
  -k "settings_workspace or strict_annual or strict_quarterly or quality_snapshot or prefill"
.venv/bin/python -m py_compile app/services/backtest_single_settings_workspace.py
git diff --check
```

Expected: all seven concrete variants project compatible payloads and legacy history prefill
contracts still pass.

- [x] **Step 5: Commit Task 16**

```bash
git add app/services/backtest_single_settings_workspace.py \
  tests/test_backtest_single_settings_workspace.py tests/test_service_contracts.py
git commit -m "Backtest Analysis 팩터 전략 React 설정 계약 이관"
```

### Task 17: Python Runtime Adapter, Validated Intent, And Generic Fallback

**Files:**
- Modify: `app/web/backtest_single_settings_workspace.py`
- Modify: `app/web/backtest_analysis_workspace.py`
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 14~16 pure workspace, existing session selection/prefill and
  `_handle_backtest_run(payload, strategy_name)`.
- Produces: `build_current_single_settings_workspace()`,
  `consume_single_settings_intent(intent, *, run_handler)`,
  `render_single_settings_fallback(workspace, *, on_submit)`, and a settings component callback.

- [x] **Step 1: Write RED intent-boundary and fallback tests**

```python
def test_run_intent_validates_before_calling_handler():
    calls = []
    result = consume_single_settings_intent(
        {"action": "run_single_strategy", "strategy_choice": "GTAA",
         "variant": None, "values": valid_gtaa_values},
        run_handler=lambda payload, name: calls.append((payload, name)),
    )
    assert result["ok"] is True
    assert len(calls) == 1

def test_invalid_or_mismatched_intent_never_runs_or_persists():
    ...
    assert calls == []
```

Cover unknown action, missing/non-callable handler, strategy mismatch, variant mismatch, replayed
intent id, unknown/hidden field, invalid option/range. Assert fallback imports the same
`build_single_settings_workspace` and `project_single_settings_payload` rather than form-specific
renderers.

- [x] **Step 2: Run RED**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py -q \
  -k "single_settings_intent or settings_fallback or current_settings_workspace"
```

Expected: new adapter/consumer functions are absent.

- [x] **Step 3: Implement runtime option and prefill adapter**

Build one JSON-ready runtime option catalog from existing `backtest_common` presets/helpers, current
DB-backed ticker choices, benchmark/options, and selected history prefill. The adapter passes those
values into the pure service and never lets React import or infer them. Persist selected variant and
validation errors under keys scoped by `draft_key`.

- [x] **Step 4: Implement callable-verified intent consumer and fallback**

`select_strategy_variant` accepts only the current family option and updates Python session state.
`run_single_strategy` checks current identity, consumes a unique intent id once, calls pure
validation/projection, and then calls the supplied runner. Validation failure returns field errors
and submitted values without clearing prior successful result. The generic fallback iterates the
same sections/fields and maps seven allowed controls to Streamlit widgets; it is invoked only when
the component is unavailable or raises during render.

- [x] **Step 5: Run GREEN and state/persistence regressions**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py -q \
  -k "single_settings or stale or prefill or history or practical_validation"
.venv/bin/python -m py_compile \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_analysis_workspace.py \
  app/web/backtest_single_strategy.py
git diff --check
```

Expected: invalid intents make zero runner/registry/history calls; valid intents call the unchanged
runner once; failure/stale/prefill contracts remain green.

- [x] **Step 6: Commit Task 17**

```bash
git add app/web/backtest_single_settings_workspace.py \
  app/web/backtest_analysis_workspace.py app/web/backtest_single_strategy.py \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py
git commit -m "Backtest Analysis React 설정 intent와 fallback 연결"
```

### Task 18: React Schema-Driven Settings Surface

**Files:**
- Modify: `app/web/components/backtest_analysis_decision_workspace/component.py`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/index.tsx`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: Task 17 JSON read model and emits only `select_strategy_variant` or
  `run_single_strategy` intents.
- Produces: `settings` surface with local draft state, all seven field controls, errors, disclosure,
  pending lock, and responsive layout.

- [x] **Step 1: Write RED source and component-boundary tests**

Assert `WorkspaceSurface` includes `settings`, the wrapper accepts the new surface, TS types contain
`SettingsField` and `SingleSettingsWorkspace`, and source contains render paths for all seven
controls. Assert the source does not classify raw strategy status/maturity/Gate, does not call the
runner, and does not render `dangerouslySetInnerHTML`. Assert CSS includes a two-column settings grid
and `@media (max-width: 760px)` one-column override.

- [x] **Step 2: Run RED**

```bash
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q \
  -k "react_settings_surface or settings_control or responsive_settings"
```

Expected: `settings` surface/type/control assertions fail.

- [x] **Step 3: Extend wrapper/types/index with the settings read model**

Add the schema/profile/variant/section/field/evidence/action/error interfaces exactly matching Task
14. Keep `ResizeObserver` and `Streamlit.setFrameHeight()` in `index.tsx`; route `surface ===
\"settings\"` to the same component with supplied data.

- [x] **Step 4: Implement local editor, profile, four sections, disclosure, and intent emission**

Initialize local values from `draft_key`; reset only when `draft_key` changes. Field edits stay in
React state. Variant clicks immediately emit `select_strategy_variant`. Submit emits one
`run_single_strategy` intent with `intent_id`, strategy, variant and complete values; disable the CTA
while pending. Render badges as text nodes, errors at field/section position, full-width wide fields,
and advanced/evidence rows inside `고급 설정과 기술 근거`.

- [x] **Step 5: Implement responsive CSS and run GREEN/build**

```bash
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q \
  -k "react_settings_surface or settings_control or responsive_settings or resize_observer"
cd app/web/components/backtest_analysis_decision_workspace/frontend
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
git diff --check
```

Expected: focused source tests pass and Vite production build exits 0.

- [x] **Step 6: Commit Task 18**

```bash
git add app/web/components/backtest_analysis_decision_workspace/component.py \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/index.tsx \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css \
  tests/test_backtest_refactor_boundaries.py
git commit -m "Backtest Analysis 전체 전략 React 설정 화면 구현"
```

### Task 19: Primary Route Cutover And Legacy Form Isolation

**Files:**
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `app/web/backtest_single_settings_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 17 adapter and Task 18 settings surface.
- Produces: every active Single Strategy selection uses React settings first; legacy renderer files
  are not imported/called by the primary route.

- [x] **Step 1: Write RED active-route and 13-variant smoke tests**

Assert `render_single_strategy_workspace()` calls the current settings builder/component and does not
dispatch `render_equal_weight_form`, `render_gtaa_form`, `render_global_relative_strength_form`,
`render_risk_parity_form`, `render_dual_momentum_form`, `render_risk_on_form`, or strict renderer
functions on the normal path. Parameterize 13 variants and assert profile, four sections, CTA,
projected payload, and runner strategy name are available.

- [x] **Step 2: Run RED**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q \
  -k "primary_single_settings_route or every_single_variant or no_legacy_form_dispatch"
```

Expected: route still dispatches native strategy forms.

- [x] **Step 3: Cut over the primary route and isolate compatibility code**

Render selected strategy profile/settings once through the React component. Keep the prior successful
result and existing decision surface after the settings component. On component failure call only
the generic same-schema fallback. Remove duplicate selected header/native shell from the active path;
do not delete legacy files in this task because service/history compatibility tests may still import
their pure helpers.

- [x] **Step 4: Run focused and full regressions**

```bash
uv run --with pytest python -m pytest tests/test_backtest_single_settings_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
.venv/bin/python -m py_compile \
  app/services/backtest_single_settings_workspace.py \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_analysis_workspace.py
git diff --check
```

Expected: new focused suites pass; service suite is no worse than the recorded pre-7차 baseline and
any unrelated baseline failure is documented rather than masked.

- [x] **Step 5: Commit Task 19**

```bash
git add app/web/backtest_single_strategy.py \
  app/web/backtest_single_settings_workspace.py \
  tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py
git commit -m "Backtest Analysis 단일 전략 React 설정 경로 전환"
```

### Task 20: Runtime QA, Finance Docs, And 7차 Closeout

**Files:**
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`, `PLAN.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate, never stage: `backtest-analysis-level1-react-settings-desktop-qa.png`
- Generate, never stage: `backtest-analysis-level1-react-settings-760-qa.png`

**Interfaces:**
- Consumes: Task 14~19.
- Produces: fresh verification evidence, all-strategy visual/runtime QA, canonical docs, protected
  path audit, closeout commit.

- [x] **Step 1: Use verification-before-completion and rerun fresh automated checks**

```bash
uv run --with pytest python -m pytest tests/test_backtest_single_settings_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_single_settings_workspace.py \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_analysis_workspace.py \
  app/web/components/backtest_analysis_decision_workspace/component.py
git diff --check
```

Record exact pass/fail counts and compare `tests/test_service_contracts.py` to the pre-7차 baseline.

- [x] **Step 2: Run desktop Browser QA across all choices and variants**

At `http://localhost:8505/backtest`, visit Equal Weight, GTAA, Global Relative Strength, Risk
Parity, Dual Momentum, Risk-On Momentum 5D, Quality Annual/Quarterly/Snapshot, Value
Annual/Quarterly, Quality + Value Annual/Quarterly. Verify each has one profile, the same four
sections, Korean first-read labels, collapsed technical disclosure and one CTA; verify no raw
`<span>`, legacy `Score Horizons`, duplicate strategy picker, or primary native form. Actually run
Equal Weight, GTAA, and Quality + Value Annual and verify result fresh/stale behavior and explicit
Level2 handoff separation. Capture the desktop screenshot.

- [x] **Step 3: Run 760px Browser QA**

Set viewport width 760px and verify all 13 variant surfaces use one column, segmented controls wrap,
multi-selects/disclosures/CTA do not overflow, iframe height follows content, and strategy or variant
change does not blank the fixed Level1 context. Capture the 760px screenshot.

- [x] **Step 4: Use finance-doc-sync for canonical and task handoff alignment**

Document pure schema ownership, React intent boundary, generic fallback, primary route cutover,
payload/stale/handoff preservation, automated counts, Browser scope/screenshots, and remaining risks
in canonical architecture/flow docs, task evidence files, and 3~5-line root handoff entries.

- [x] **Step 5: Audit staged paths and protected artifacts**

```bash
git diff --check
git add \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
if git diff --cached --name-only | rg -q \
  'registries/|run_history/|saved/|\.superpowers/|\.png$|run_artifacts/'; then
  exit 1
fi
```

Expected: no protected JSONL, saved record, `.superpowers/`, screenshot or generated artifact is
staged.

- [x] **Step 6: Commit Task 20**

```bash
git commit -m "Backtest Analysis 전체 전략 React 설정 QA와 문서 동기화"
```

## 7차 Completion Report Contract

- 전체 roadmap 1~7차 완료 상태와 남은 차수;
- Task 14~20 한국어 commit 목록;
- focused / boundary / service exact counts and baseline comparison;
- React production build / target `py_compile` / `git diff --check` 결과;
- desktop / 760px QA 범위와 screenshot absolute links;
- registry / run history / saved / `.superpowers/` / screenshot 보호 감사;
- remaining risks and next handoff location.


# Backtest Analysis Result Interpretation Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Level1 Result Workspace의 normalized chart에 실제 날짜, pointer-only tooltip, Benchmark identity를 추가하고 holdings 일정과 raw technical appendix를 사용자 언어로 보정한다.

**Architecture:** `app/services/backtest_analysis_result_workspace.py`가 공통 timeline, normalized return, Benchmark identity, rebalance schedule, calculation/data basis를 JSON-ready read model로 계산한다. React와 Python fallback은 같은 read model을 표시하며 React는 pointer 위치와 responsive tick 선택만 소유한다.

**Tech Stack:** Python 3.12, pandas, pytest, React 18, TypeScript, dependency-free SVG, Streamlit custom components, Vite 5.

## Global Constraints

- 현재 worktree와 branch `codex/backtest-dev`를 그대로 사용한다.
- 투자금 입력, 달러 환산, 고정 10,000달러 reference value를 추가하지 않는다.
- chart dependency, zoom/pan/range selector를 추가하지 않는다.
- Python이 normalized return, Benchmark 의미, rebalance window, metadata label을 소유한다.
- React는 raw metadata를 분류하거나 Gate, allocation, next date를 계산하지 않는다.
- exact next trading date는 만들지 않고 explicit cadence가 있을 때 `YYYY-MM 월말 예상`만 제공한다.
- broker holdings/order, tax, minimum lot, live/auto rebalance, strategy runtime과 DB schema는 범위 밖이다.
- 모든 feature/bugfix는 RED -> GREEN을 확인하고 distinct unit마다 한국어 커밋을 만든다.
- registry, run history, saved JSONL, `.superpowers/`, screenshots, run artifacts를 stage/commit하지 않는다.

---

### Task 31: Chart Timeline, Normalized Return, And Benchmark Identity

**Files:**
- Modify: `app/services/backtest_analysis_result_workspace.py:520-635`
- Modify: `tests/test_backtest_analysis_result_workspace.py:192-270`

**Interfaces:**
- Consumes: `_curve_rows()`, `_normalize_curve()`, `_date_label()`, `result_bundle["meta"]`.
- Produces: `_select_date_ticks(dates: Sequence[str], *, limit: int)`, `_benchmark_identity(meta, *, available)`, expanded `_chart_projection(bundle)` with common timeline, ticks, hover rows and Benchmark identity.

- [x] **Step 1: Write chart interpretation RED tests**

Append:

```python
def test_chart_publishes_real_date_ticks_returns_and_benchmark_identity() -> None:
    bundle = result_bundle()
    dates = pd.date_range("2026-01-31", periods=7, freq="ME")
    bundle["chart_df"] = pd.DataFrame(
        {"Date": dates, "Total Balance": [100, 101, 99, 104, 108, 110, 124.9]}
    )
    bundle["benchmark_chart_df"] = pd.DataFrame(
        {"Date": dates, "Benchmark Total Balance": [100, 100, 101, 103, 104, 106, 112]}
    )
    bundle["meta"].update({"benchmark_ticker": "SPY", "benchmark_label": "S&P 500 (SPY)"})

    chart = _build_workspace(bundle)["chart"]

    assert chart["normalized_base"] == 100.0
    assert "124.9" in chart["normalized_explanation"]
    assert chart["benchmark"]["label"] == "S&P 500 (SPY)"
    assert chart["timeline_dates"] == [date.date().isoformat() for date in dates]
    assert len(chart["desktop_x_ticks"]) == 6
    assert len(chart["compact_x_ticks"]) == 3
    assert chart["desktop_x_ticks"][0]["date"] == "2026-01-31"
    assert chart["desktop_x_ticks"][-1]["date"] == "2026-07-31"
    assert chart["hover_rows"][-1]["strategy_return_label"] == "+24.9%"
    assert chart["hover_rows"][-1]["benchmark_return_label"] == "+12.0%"


def test_sparse_benchmark_keeps_timeline_positions_without_fake_values() -> None:
    bundle = result_bundle()
    bundle["chart_df"] = pd.DataFrame([
        {"Date": "2026-01-31", "Total Balance": 100.0},
        {"Date": "2026-02-28", "Total Balance": 105.0},
        {"Date": "2026-03-31", "Total Balance": 110.0},
    ])
    bundle["benchmark_chart_df"] = pd.DataFrame([
        {"Date": "2026-01-31", "Benchmark Total Balance": 100.0},
        {"Date": "2026-03-31", "Benchmark Total Balance": 104.0},
    ])
    bundle["meta"]["benchmark_ticker"] = "SPY"

    chart = _build_workspace(bundle)["chart"]

    assert chart["timeline_dates"] == ["2026-01-31", "2026-02-28", "2026-03-31"]
    assert chart["hover_rows"][1]["benchmark_value"] is None
    assert [row["date"] for row in chart["benchmark_series"]] == [
        "2026-01-31", "2026-03-31"
    ]
```

- [x] **Step 2: Run RED**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py::test_chart_publishes_real_date_ticks_returns_and_benchmark_identity \
  tests/test_backtest_analysis_result_workspace.py::test_sparse_benchmark_keeps_timeline_positions_without_fake_values -q
```

Expected: missing `normalized_base`, `timeline_dates`, `hover_rows` or current common-date filtering 때문에 fail.

- [x] **Step 3: Implement common timeline/display helpers**

Add before `_chart_projection`:

```python
def _format_signed_percent(value: Any) -> str:
    numeric = _optional_float(value)
    return "-" if numeric is None else f"{numeric:+.1%}"


def _select_date_ticks(
    dates: Sequence[str],
    *,
    limit: int,
) -> list[dict[str, str]]:
    unique = list(dict.fromkeys(str(value) for value in dates if str(value)))
    if len(unique) <= limit:
        selected = unique
    else:
        last = len(unique) - 1
        indexes = sorted({
            round(offset * last / (limit - 1))
            for offset in range(limit)
        })
        selected = [unique[index] for index in indexes]
    return [{"date": value, "label": value} for value in selected]


def _benchmark_identity(
    meta: Mapping[str, Any],
    *,
    available: bool,
) -> dict[str, Any]:
    ticker = str(meta.get("benchmark_ticker") or "").strip().upper()
    contract = str(meta.get("benchmark_contract") or "").strip()
    label = str(meta.get("benchmark_label") or ticker or contract).strip()
    return {
        "available": available,
        "label": label,
        "ticker": ticker,
        "contract_label": contract,
        "missing_reason": (
            "" if available
            else "동일 기간 기준지수 곡선이 없어 Level2에서 비교합니다."
        ),
    }
```

Replace common-date filtering with union timeline and hover rows:

```python
    strategy_series = _normalize_curve(strategy_rows)
    benchmark_series = _normalize_curve(benchmark_rows)
    timeline_dates = sorted(
        {row["date"] for row in strategy_series}.union(
            row["date"] for row in benchmark_series
        )
    )
    strategy_by_date = {row["date"]: row for row in strategy_series}
    benchmark_by_date = {row["date"]: row for row in benchmark_series}
    hover_rows = []
    for timeline_date in timeline_dates:
        strategy = strategy_by_date.get(timeline_date)
        benchmark = benchmark_by_date.get(timeline_date)
        hover_rows.append({
            "date": timeline_date,
            "strategy_value": strategy.get("value") if strategy else None,
            "strategy_value_label": strategy.get("value_label") if strategy else "-",
            "strategy_return": (
                round(float(strategy["value"]) / 100.0 - 1.0, 6)
                if strategy else None
            ),
            "strategy_return_label": (
                _format_signed_percent(float(strategy["value"]) / 100.0 - 1.0)
                if strategy else "-"
            ),
            "benchmark_value": benchmark.get("value") if benchmark else None,
            "benchmark_value_label": benchmark.get("value_label") if benchmark else "-",
            "benchmark_return": (
                round(float(benchmark["value"]) / 100.0 - 1.0, 6)
                if benchmark else None
            ),
            "benchmark_return_label": (
                _format_signed_percent(float(benchmark["value"]) / 100.0 - 1.0)
                if benchmark else "-"
            ),
        })
```

Return:

```python
        "normalized_base": 100.0,
        "normalized_explanation": (
            f"첫 공통 시점을 100으로 맞췄습니다. 마지막 전략 지수 "
            f"{strategy_series[-1]['value_label'] if strategy_series else '-'}는 누적 "
            f"{hover_rows[-1]['strategy_return_label'] if hover_rows else '-'}를 의미합니다."
        ),
        "strategy_label": str(
            bundle.get("strategy_name") or meta.get("strategy_name") or "전략"
        ),
        "benchmark": _benchmark_identity(meta, available=bool(benchmark_series)),
        "timeline_dates": timeline_dates,
        "desktop_x_ticks": _select_date_ticks(timeline_dates, limit=6),
        "compact_x_ticks": _select_date_ticks(timeline_dates, limit=3),
        "hover_rows": hover_rows,
```

- [x] **Step 4: Run GREEN and commit**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py::test_chart_publishes_real_date_ticks_returns_and_benchmark_identity \
  tests/test_backtest_analysis_result_workspace.py::test_sparse_benchmark_keeps_timeline_positions_without_fake_values -q
uv run --with pytest python -m pytest tests/test_backtest_analysis_result_workspace.py -q
.venv/bin/python -m py_compile app/services/backtest_analysis_result_workspace.py
git diff --check
git add app/services/backtest_analysis_result_workspace.py tests/test_backtest_analysis_result_workspace.py
git diff --cached --check
git commit -m "Backtest Analysis 차트 해석 계약 보강"
```

### Task 32: Rebalance Schedule And Calculation/Data Basis

**Files:**
- Modify: `app/services/backtest_analysis_result_workspace.py:635-1040`
- Modify: `tests/test_backtest_analysis_result_workspace.py:110-360`

**Interfaces:**
- Consumes: sorted `result_df`, target row, `rebalance_interval/interval/rebalance_freq`, lifecycle and configuration fingerprint.
- Produces: `_rebalance_schedule()`, `holdings.schedule`, and `technical_appendix.sections/raw`.

- [x] **Step 1: Write schedule/appendix RED tests**

```python
def test_holdings_schedule_separates_signal_rebalance_and_next_window() -> None:
    bundle = result_bundle()
    bundle["meta"]["rebalance_interval"] = 3
    bundle["result_df"] = pd.DataFrame([
        {"Date": "2026-03-31", "Rebalancing": True, "End Ticker": ["SPY"],
         "End Balance": [100.0], "Next Ticker": ["SPY", "TLT"],
         "Next Weight": [0.6, 0.4], "Total Balance": 100.0, "Cash": 0.0},
        {"Date": "2026-04-30", "Rebalancing": False, "End Ticker": ["SPY", "TLT"],
         "End Balance": [61.0, 41.0], "Next Ticker": ["SPY", "TLT"],
         "Next Balance": [61.0, 41.0], "Total Balance": 102.0, "Cash": 0.0},
    ])

    schedule = _build_workspace(bundle)["holdings"]["schedule"]

    assert schedule["valuation_as_of"] == "2026-04-30"
    assert schedule["latest_signal_as_of"] == "2026-03-31"
    assert schedule["last_rebalance_as_of"] == "2026-03-31"
    assert schedule["cadence_label"] == "3개월마다"
    assert schedule["next_window_label"] == "2026-06 월말 예상"
    assert schedule["next_window_status"] == "estimated_window"


def test_missing_cadence_never_invents_next_rebalance_date() -> None:
    bundle = result_bundle()
    bundle["result_df"]["Rebalancing"] = True

    schedule = _build_workspace(bundle)["holdings"]["schedule"]

    assert schedule["last_rebalance_as_of"] == "2026-06-30"
    assert schedule["cadence_label"] == "주기 근거 없음"
    assert schedule["next_window_label"] == "다음 일정 확인 필요"
    assert schedule["next_window_status"] == "unknown"


def test_calculation_and_data_basis_hides_raw_keys_from_first_layer() -> None:
    bundle = result_bundle()
    bundle["meta"].update({
        "execution_mode": "db",
        "transaction_cost_bps": 10.0,
        "universe_name": "GTAA Universe",
        "benchmark_ticker": "SPY",
        "unknown_provider_payload": {"raw": True},
    })

    appendix = _build_workspace(bundle)["technical_appendix"]

    assert [section["section_id"] for section in appendix["sections"]] == [
        "calculation_basis", "data_basis", "result_trace"
    ]
    visible_labels = [
        row["label"]
        for section in appendix["sections"]
        for row in section["rows"]
    ]
    assert "실행 방식" in visible_labels
    assert "기준지수" in visible_labels
    assert "unknown_provider_payload" not in visible_labels
    assert "unknown_provider_payload" in appendix["raw"]["meta"]
```

- [x] **Step 2: Run RED**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py::test_holdings_schedule_separates_signal_rebalance_and_next_window \
  tests/test_backtest_analysis_result_workspace.py::test_missing_cadence_never_invents_next_rebalance_date \
  tests/test_backtest_analysis_result_workspace.py::test_calculation_and_data_basis_hides_raw_keys_from_first_layer -q
```

Expected: `holdings.schedule`, `technical_appendix.sections/raw` missing으로 fail.

- [x] **Step 3: Implement cadence and next window**

```python
def _cadence_months(meta: Mapping[str, Any]) -> int | None:
    for key in ("rebalance_interval", "interval"):
        numeric = _optional_float(meta.get(key))
        if numeric is not None and numeric >= 1 and float(numeric).is_integer():
            return int(numeric)
    frequency = str(meta.get("rebalance_freq") or "").strip().lower()
    return {
        "monthly": 1, "m": 1,
        "quarterly": 3, "q": 3,
        "annual": 12, "yearly": 12, "y": 12,
    }.get(frequency)


def _rebalance_schedule(
    result_df: pd.DataFrame,
    *,
    target_row: Mapping[str, Any] | None,
    meta: Mapping[str, Any],
) -> dict[str, Any]:
    prepared = _latest_rows(result_df)
    valuation = _date_label(prepared.iloc[-1].get("Date")) if not prepared.empty else ""
    signal = _date_label(dict(target_row or {}).get("Date"))
    rebalance_rows = (
        prepared[prepared["Rebalancing"].fillna(False).astype(bool)]
        if "Rebalancing" in prepared.columns else pd.DataFrame()
    )
    last_rebalance = (
        _date_label(rebalance_rows.iloc[-1].get("Date"))
        if not rebalance_rows.empty else ""
    )
    months = _cadence_months(meta)
    if months and last_rebalance:
        next_month = pd.Timestamp(last_rebalance) + pd.DateOffset(months=months)
        next_label = f"{next_month:%Y-%m} 월말 예상"
        status = "estimated_window"
        cadence = f"{months}개월마다"
    else:
        next_label = "다음 일정 확인 필요"
        status = "unknown"
        cadence = f"{months}개월마다" if months else "주기 근거 없음"
    return {
        "valuation_as_of": valuation,
        "latest_signal_as_of": signal or "확인 가능한 기록 없음",
        "last_rebalance_as_of": last_rebalance or "확인 가능한 기록 없음",
        "cadence_label": cadence,
        "next_window_label": next_label,
        "next_window_status": status,
        "explanation": (
            "최신 신호 기준 목표이며 다음 리밸런싱 전까지 현재 구성을 유지합니다."
        ),
    }
```

Attach `schedule` to the primary holdings projection, including cash-only/unavailable states.

- [x] **Step 4: Implement user basis plus raw trace**

Change `_technical_appendix` to accept lifecycle/fingerprint and return:

```python
def _basis_row(
    label: str,
    value: Any,
    explanation: str,
    *,
    status: str = "available",
) -> dict[str, Any]:
    value_label = (
        str(value).strip()
        if value not in (None, "")
        else "확인 가능한 근거 없음"
    )
    return {
        "label": label,
        "value_label": value_label,
        "explanation": explanation,
        "status": status if value_label != "확인 가능한 근거 없음" else "missing",
    }
```

Build exact sections `calculation_basis`, `data_basis`, `result_trace` with Korean rows for execution mode, cost, period/row count, universe, price freshness, Benchmark, factor readiness, run id, fingerprint and lifecycle. Preserve every original column, first 100 rows and all meta only under:

```python
"raw": {
    "row_count": len(result_df),
    "columns": [str(column) for column in result_df.columns],
    "prepared_rows": prepared_rows,
    "preview_limited": len(result_df) > len(prepared_rows),
    "meta": {
        str(key): _json_value(value)
        for key, value in sorted(meta.items(), key=lambda item: str(item[0]))
    },
}
```

Update builder call:

```python
"technical_appendix": _technical_appendix(
    bundle,
    lifecycle=lifecycle,
    configuration_fingerprint=current_configuration_fingerprint,
),
```

- [x] **Step 5: Run GREEN and commit**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py::test_holdings_schedule_separates_signal_rebalance_and_next_window \
  tests/test_backtest_analysis_result_workspace.py::test_missing_cadence_never_invents_next_rebalance_date \
  tests/test_backtest_analysis_result_workspace.py::test_calculation_and_data_basis_hides_raw_keys_from_first_layer -q
uv run --with pytest python -m pytest tests/test_backtest_analysis_result_workspace.py -q
.venv/bin/python -m py_compile app/services/backtest_analysis_result_workspace.py
git diff --check
git add app/services/backtest_analysis_result_workspace.py tests/test_backtest_analysis_result_workspace.py
git diff --cached --check
git commit -m "Backtest Analysis 리밸런싱과 계산 근거 정리"
```


### Task 33: Interactive SVG, Schedule Strip, Appendix UI, And Fallback

**Files:**
- Modify: app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts
- Modify: app/web/components/backtest_analysis_result_workspace/frontend/src/ResultWorkspaceChart.tsx
- Modify: app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx
- Modify: app/web/components/backtest_analysis_result_workspace/frontend/src/style.css
- Modify: app/web/backtest_analysis_result_workspace_panel.py
- Modify: tests/test_backtest_refactor_boundaries.py:570-625

**Interfaces:**
- Consumes: Task 31 chart timeline/ticks/hover/Benchmark and Task 32 schedule/appendix sections.
- Produces: pointer-only SVG, responsive schedule strip, calculation/data basis disclosure and fallback parity.

- [x] **Step 1: Write React/fallback RED boundary contract**

Extend test_level1_result_workspace_is_dedicated_intent_only_and_responsive:

~~~python
        for token in (
            "timeline_dates", "desktop_x_ticks", "compact_x_ticks",
            "hover_rows", "contract_label", "next_window_label",
            "calculation_basis", "data_basis", "result_trace",
        ):
            self.assertIn(token, types)
        for token in (
            "onPointerMove", "onPointerLeave",
            "bt1r-crosshair", "bt1r-chart-tooltip",
        ):
            self.assertIn(token, chart)
        self.assertIn("bt1r-schedule-strip", source)
        self.assertIn("계산 및 데이터 기준", source)
        self.assertIn("원본 필드 보기", source)
        self.assertIn(".bt1r-chart-tooltip", css)
        self.assertIn(".bt1r-schedule-strip", css)
        self.assertNotIn("value / 100", chart)
        self.assertIn("계산 및 데이터 기준", fallback)
        self.assertIn("next_window_label", fallback)
~~~

- [x] **Step 2: Run RED**

~~~bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_level1_result_workspace_is_dedicated_intent_only_and_responsive -q
~~~

Expected: new types, pointer events, schedule and disclosure labels absent로 fail.

- [x] **Step 3: Expand exact TypeScript types**

Add DateTick, HoverRow, BasisRow:

~~~typescript
type DateTick = { date: string; label: string }
type HoverRow = {
  date: string
  strategy_value: number | null
  strategy_value_label: string
  strategy_return: number | null
  strategy_return_label: string
  benchmark_value: number | null
  benchmark_value_label: string
  benchmark_return: number | null
  benchmark_return_label: string
}
type BasisRow = {
  label: string
  value_label: string
  explanation: string
  status: string
}
~~~

Expand chart with normalized_base, normalized_explanation, strategy_label, Benchmark identity, timeline_dates, both x tick arrays and hover_rows. Add holdings.schedule with valuation/signal/rebalance/cadence/next-window fields. Replace technical_appendix with three typed sections and raw row/column/meta trace.

- [x] **Step 4: Implement pointer-only SVG**

Use common timeline for every series:

~~~typescript
const [hoveredDate, setHoveredDate] = useState<string | null>(null)
const timelineIndex = new Map(
  chart.timeline_dates.map((date, index) => [date, index]),
)
const xForDate = (date: string) => {
  const index = timelineIndex.get(date) ?? 0
  return PADDING.left +
    (index / Math.max(chart.timeline_dates.length - 1, 1)) *
      (WIDTH - PADDING.left - PADDING.right)
}
const handlePointerMove = (event: React.PointerEvent<SVGSVGElement>) => {
  if (!chart.hover_rows.length) return
  const bounds = event.currentTarget.getBoundingClientRect()
  const pointer =
    ((event.clientX - bounds.left) / Math.max(bounds.width, 1)) * WIDTH
  const nearest = chart.hover_rows.reduce((best, row) =>
    Math.abs(xForDate(row.date) - pointer) <
    Math.abs(xForDate(best.date) - pointer) ? row : best
  )
  setHoveredDate(nearest.date)
}
const hovered =
  chart.hover_rows.find((row) => row.date === hoveredDate) ?? null
~~~

Change pathFor to xForDate(point.date). Attach onPointerMove and onPointerLeave to SVG. Render actual legend labels and desktop/compact tick groups. While hovered exists, render bt1r-crosshair and bt1r-chart-tooltip using only Python-provided labels. React must not divide by 100 or infer Benchmark identity.

- [x] **Step 5: Render schedule and calculation/data basis**

Before holdings cards:

~~~tsx
<div className="bt1r-schedule-strip">
  <div><span>현재 평가일</span><strong>{schedule.valuation_as_of || "-"}</strong></div>
  <div><span>최신 신호일</span><strong>{schedule.latest_signal_as_of}</strong></div>
  <div><span>마지막 리밸런싱</span><strong>{schedule.last_rebalance_as_of}</strong></div>
  <div><span>주기</span><strong>{schedule.cadence_label}</strong></div>
  <div><span>다음 예상</span><strong>{schedule.next_window_label}</strong></div>
</div>
~~~

Replace raw-first appendix:

~~~tsx
<details className="bt1r-appendix">
  <summary>계산 및 데이터 기준</summary>
  <div className="bt1r-basis-grid">
    {workspace.technical_appendix.sections.map((section) => (
      <article key={section.section_id}>
        <h3>{section.label}</h3>
        {section.rows.map((row) => (
          <div key={row.label}>
            <strong>{row.label}</strong>
            <span>{row.value_label}</span>
            <small>{row.explanation}</small>
          </div>
        ))}
      </article>
    ))}
  </div>
  <details className="bt1r-raw-disclosure">
    <summary>원본 필드 보기</summary>
    <p>원본 결과 {workspace.technical_appendix.raw.row_count}행</p>
    <code>{workspace.technical_appendix.raw.columns.join(", ")}</code>
  </details>
</details>
~~~

Mirror the same labels/order in Python fallback. Use one Streamlit expander and a plain raw subheading/code block; do not nest Streamlit expanders.

- [x] **Step 6: Add responsive CSS and run GREEN/build**

Add crosshair, tooltip, desktop/compact ticks, schedule strip, basis grid and raw disclosure selectors. Desktop shows desktop ticks and five schedule columns. At max-width 760px, show compact ticks, contain tooltip and make schedule/basis one column.

~~~bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_level1_result_workspace_is_dedicated_intent_only_and_responsive -q
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py \
  tests/test_backtest_refactor_boundaries.py -q
cd app/web/components/backtest_analysis_result_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_result_workspace_panel.py
git diff --check
~~~

Expected: focused suites/build/compile/diff-check pass.

- [x] **Step 7: Commit Task 33**

~~~bash
git add \
  app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts \
  app/web/components/backtest_analysis_result_workspace/frontend/src/ResultWorkspaceChart.tsx \
  app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx \
  app/web/components/backtest_analysis_result_workspace/frontend/src/style.css \
  app/web/backtest_analysis_result_workspace_panel.py \
  tests/test_backtest_refactor_boundaries.py
git diff --cached --check
git commit -m "Backtest Analysis 결과 상호작용 UI 보강"
~~~


### Task 34: Browser QA, Verification, Docs, And 11차 Closeout

**Files:**
- Modify: active task PLAN.md, STATUS.md, NOTES.md, RUNS.md, RISKS.md
- Modify: .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md
- Modify: .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md
- Modify: .aiworkspace/note/finance/WORK_PROGRESS.md
- Modify: .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
- Generate, never stage: backtest-analysis-level1-result-interpretation-desktop-qa.png
- Generate, never stage: backtest-analysis-level1-result-interpretation-760-qa.png

**Interfaces:**
- Consumes: Task 31~33 read model and renderer.
- Produces: actual interaction evidence, fresh verification, canonical docs and protected-path audit.

- [x] **Step 1: Run desktop Browser QA**

1. Run Equal Weight and confirm real X dates, normalized explanation and actual Benchmark label.
2. Move pointer across start/middle/end; tooltip/crosshair appear only inside SVG.
3. Confirm tooltip date, strategy index/return and Benchmark index/return match the curve.
4. Confirm valuation, signal, last rebalance, cadence and next window are distinct.
5. Select a strategy without cadence and confirm 다음 일정 확인 필요.
6. Open 계산 및 데이터 기준, verify three user sections, then raw fields secondary disclosure.
7. Change settings and confirm stale result interpretation stays visible while handoff is locked.

Capture desktop screenshot and never stage it.

- [x] **Step 2: Run 760px Browser QA**

Confirm compact X-axis has at most 3 dates, tooltip remains inside chart, schedule/basis cards are one column, raw/table internal scroll does not expand the page, disclosure height sync works, and outer/component horizontal overflow is 0. Capture screenshot and never stage it.

- [x] **Step 3: Run verification-before-completion**

~~~bash
uv run --with pytest python -m pytest tests/test_backtest_analysis_result_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd ../../backtest_analysis_result_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_result_workspace_panel.py \
  app/web/backtest_result_display.py \
  app/web/components/backtest_analysis_result_workspace/component.py
git diff --check
~~~

Record exact counts/module counts/results and baseline failures without describing them as new passes.

- [x] **Step 4: Sync finance docs and audit protected paths**

Document date/hover, Benchmark identity, schedule semantics, no-dollar decision and calculation/data basis. Update active task/root logs.

~~~bash
git add \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
if git diff --cached --name-only | rg -q \
  'registries/|run_history/|saved/|\.superpowers/|\.png$|run_artifacts/'; then
  exit 1
fi
~~~

- [x] **Step 5: Commit Task 34**

~~~bash
git commit -m "Backtest Analysis 결과 해석 보정 QA와 문서 동기화"
~~~

## 11차 Completion Report Contract

- Task 31~34 완료 상태와 한국어 commit 목록
- result/decision/boundary/service exact counts와 baseline failures
- Decision/Result React build, target py_compile, diff-check
- desktop/760px hover, Benchmark, schedule, appendix QA와 screenshots
- protected paths가 commit되지 않았는지
- accessibility, sparse Benchmark, cadence/provider remaining risks


## 8차 Corrective Plan: Modifier-Free Multi-Select Controls

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Quality/Value와 GTAA를 포함한 모든 React `multi_select` 설정을 modifier key 없이
기존 선택을 유지하며 추가·제거할 수 있는 adaptive control로 교체한다.

**Architecture:** Python-owned schema, validation, payload projector와 runner는 변경하지 않는다.
React가 option 20개 이하를 checkbox-card grid, 21개 이상을 검색 가능한 bounded checkbox
list와 selected chip shelf로 렌더링하고, 모든 selection은 schema catalog 순서로 정규화한
배열을 기존 settings intent에 넣는다.

**Tech Stack:** React 18, TypeScript 5.6, Vite 5, CSS, Python unittest / pytest source contracts,
Streamlit custom component Browser QA.

### 8차 Global Constraints

- `MULTI_SELECT_COMPACT_LIMIT`은 20, `MULTI_SELECT_RESULT_LIMIT`은 100으로 고정한다.
- compact `전체 선택`은 field option 전체, large `검색 결과 전체 선택`은 현재 filter 결과만
  기존 selection에 추가한다.
- compact/large `선택 해제`는 current selection 전체를 빈 배열로 만들고 required 판단은
  기존 Python validator에 맡긴다.
- option identity는 `String(option.value)`이며 output은 항상 schema catalog 순서다.
- ordinary selection edit는 React local state만 바꾸고 Streamlit intent를 emit하지 않는다.
- 기존 `{strategy_choice, variant, values}` 실행 intent와 Python validation/payload/runner,
  Run History, Level2 handoff 계약은 변경하지 않는다.
- initial large result DOM은 최대 100개이며 selected value는 결과 밖이어도 chip으로 보인다.
- desktop / 760px horizontal overflow 0, keyboard focus, selected border/check/ARIA를 유지한다.
- protected JSONL, saved record, `.superpowers/`, screenshot과 run artifact는 stage하지 않는다.

### Task 21: Adaptive Modifier-Free Multi-Select TDD

**Files:**
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`

**Interfaces:**
- Consumes: `SettingsField.options`, current `unknown[]` field value, existing
  `onChange(value: unknown)` callback.
- Produces: `normalizeMultiSelectValues(field, values): unknown[]` and
  `MultiSelectFieldControl({field, value, onChange, inputId})` with compact/search render modes.
- Preserves: `SingleSettingsEditor` local draft, `emitSettingsIntent`, Python intent adapter,
  schema validator and payload projector.

- [x] **Step 1: Write the failing adaptive-control source contract**

Add this test next to `test_react_settings_surface_is_schema_driven_and_responsive`:

```python
def test_react_multi_select_is_modifier_free_and_adaptive(self) -> None:
    root = (
        PROJECT_ROOT
        / "app/web/components/backtest_analysis_decision_workspace"
    )
    component = (
        root / "frontend/src/BacktestAnalysisDecisionWorkspace.tsx"
    ).read_text()
    style = (root / "frontend/src/style.css").read_text()

    self.assertNotIn("event.target.selectedOptions", component)
    self.assertNotIn("select[multiple]", style)
    for token in (
        "const MULTI_SELECT_COMPACT_LIMIT = 20",
        "const MULTI_SELECT_RESULT_LIMIT = 100",
        "function normalizeMultiSelectValues(",
        "function MultiSelectFieldControl(",
        'className="bt1-multi-select-compact"',
        'className="bt1-multi-select-search"',
        'role="checkbox"',
        'aria-pressed={selected}',
        "검색 결과 전체 선택",
        "bt1-selected-chip",
        ".slice(0, MULTI_SELECT_RESULT_LIMIT)",
    ):
        self.assertIn(token, component)
    for token in (
        ".bt1-multi-select-compact",
        "repeat(auto-fit, minmax(140px, 1fr))",
        ".bt1-multi-select-results",
        "max-height: 280px",
        "overflow-y: auto",
        ".bt1-selected-chip",
        ":focus-visible",
    ):
        self.assertIn(token, style)
    responsive = style.split("@media (max-width: 760px)", 1)[1]
    self.assertIn(".bt1-multi-select-compact", responsive)
```

- [x] **Step 2: Run RED and confirm the intended failure**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_react_multi_select_is_modifier_free_and_adaptive \
  -q
```

Expected: FAIL because `event.target.selectedOptions` and native `select[multiple]` still exist and
adaptive constants/components are absent. A collection/import error is not an accepted RED.

- [x] **Step 3: Add catalog-order selection helpers and the custom control**

Add below `optionFromString()`:

```tsx
const MULTI_SELECT_COMPACT_LIMIT = 20
const MULTI_SELECT_RESULT_LIMIT = 100

function optionIdentity(value: unknown) {
  return String(value)
}

function normalizeMultiSelectValues(field: SettingsField, values: unknown[]) {
  const selected = new Set(values.map(optionIdentity))
  return (field.options ?? [])
    .filter((option) => selected.has(optionIdentity(option.value)))
    .map((option) => option.value)
}

function MultiSelectFieldControl({
  field,
  value,
  onChange,
  inputId,
}: {
  field: SettingsField
  value: unknown
  onChange: (value: unknown) => void
  inputId: string
}) {
  const options = field.options ?? []
  const selectedValues = Array.isArray(value) ? value : []
  const selectedKeys = new Set(selectedValues.map(optionIdentity))
  const [query, setQuery] = useState("")
  const normalizedQuery = query.trim().toLocaleLowerCase()
  const filteredOptions = options.filter((option) => {
    if (!normalizedQuery) return true
    return `${option.label} ${String(option.value)}`
      .toLocaleLowerCase()
      .includes(normalizedQuery)
  })
  const visibleOptions = filteredOptions.slice(0, MULTI_SELECT_RESULT_LIMIT)
  const remainingCount = Math.max(0, filteredOptions.length - visibleOptions.length)

  const toggleValue = (nextValue: unknown) => {
    const key = optionIdentity(nextValue)
    const next = selectedKeys.has(key)
      ? selectedValues.filter((item) => optionIdentity(item) !== key)
      : [...selectedValues, nextValue]
    onChange(normalizeMultiSelectValues(field, next))
  }
  const clearSelection = () => onChange([])

  if (options.length <= MULTI_SELECT_COMPACT_LIMIT) {
    return (
      <div className="bt1-settings-multi-select" id={inputId} role="group" aria-label={field.label}>
        <div className="bt1-multi-select-toolbar">
          <button type="button" onClick={() => onChange(options.map((option) => option.value))}>
            전체 선택
          </button>
          <button type="button" onClick={clearSelection}>선택 해제</button>
        </div>
        <div className="bt1-multi-select-compact">
          {options.map((option) => {
            const selected = selectedKeys.has(optionIdentity(option.value))
            return (
              <button
                type="button"
                className={selected ? "is-selected" : ""}
                aria-pressed={selected}
                key={optionIdentity(option.value)}
                onClick={() => toggleValue(option.value)}
              >
                <span aria-hidden="true">{selected ? "✓" : ""}</span>
                {option.label}
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  const addFilteredOptions = () =>
    onChange(
      normalizeMultiSelectValues(field, [
        ...selectedValues,
        ...filteredOptions.map((option) => option.value),
      ]),
    )

  return (
    <div className="bt1-settings-multi-select bt1-multi-select-search" id={inputId}>
      <input
        type="search"
        value={query}
        aria-label={`${field.label} 검색`}
        placeholder="종목 또는 값을 검색"
        onChange={(event) => setQuery(event.target.value)}
      />
      <div className="bt1-selected-chip-shelf" aria-label="현재 선택">
        {selectedValues.map((item) => (
          <button
            type="button"
            className="bt1-selected-chip"
            aria-label={`${optionLabel(field, item)} 선택 해제`}
            key={optionIdentity(item)}
            onClick={() => toggleValue(item)}
          >
            {optionLabel(field, item)} <span aria-hidden="true">×</span>
          </button>
        ))}
      </div>
      <div className="bt1-multi-select-toolbar">
        <button type="button" onClick={addFilteredOptions}>검색 결과 전체 선택</button>
        <button type="button" onClick={clearSelection}>선택 해제</button>
      </div>
      <div className="bt1-multi-select-results" role="group" aria-label={`${field.label} 옵션`}>
        {visibleOptions.map((option) => {
          const selected = selectedKeys.has(optionIdentity(option.value))
          return (
            <button
              type="button"
              role="checkbox"
              aria-checked={selected}
              className={selected ? "is-selected" : ""}
              key={optionIdentity(option.value)}
              onClick={() => toggleValue(option.value)}
            >
              <span aria-hidden="true">{selected ? "✓" : ""}</span>
              {option.label}
            </button>
          )
        })}
      </div>
      {remainingCount > 0 && <small>검색 결과 {remainingCount}개가 더 있습니다.</small>}
    </div>
  )
}
```

Replace the native `case "multi_select"` branch with:

```tsx
case "multi_select":
  control = (
    <MultiSelectFieldControl
      field={field}
      value={value}
      onChange={onChange}
      inputId={inputId}
    />
  )
  break
```

Exclude the custom group from `htmlFor` just as the segmented control is excluded:

```tsx
<label
  htmlFor={
    field.control === "segmented" || field.control === "multi_select"
      ? undefined
      : inputId
  }
>
```

- [x] **Step 4: Add compact/search/chip/focus/responsive styling**

Remove `.bt1-settings-field select[multiple]` and add:

```css
.bt1-settings-multi-select {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.bt1-multi-select-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.bt1-multi-select-toolbar button,
.bt1-selected-chip {
  min-height: 34px;
  padding: 7px 11px;
  border: 1px solid #c9d7e2;
  border-radius: 999px;
  color: #486579;
  background: #fff;
  font: inherit;
  cursor: pointer;
}

.bt1-multi-select-compact {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}

.bt1-multi-select-compact > button,
.bt1-multi-select-results > button {
  display: grid;
  grid-template-columns: 20px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  min-width: 0;
  min-height: 44px;
  padding: 9px 11px;
  border: 1px solid #cbd8e2;
  border-radius: 11px;
  color: #31495d;
  background: #fff;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.bt1-multi-select-compact > button > span,
.bt1-multi-select-results > button > span {
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
  border: 1px solid #b9c9d5;
  border-radius: 6px;
  color: #fff;
  background: #fff;
}

.bt1-multi-select-compact > button.is-selected,
.bt1-multi-select-results > button.is-selected {
  border-color: #6f95aa;
  color: #244e65;
  background: #edf5f8;
  box-shadow: inset 0 0 0 1px #6f95aa;
}

.bt1-multi-select-compact > button.is-selected > span,
.bt1-multi-select-results > button.is-selected > span {
  border-color: #547f95;
  background: #547f95;
}

.bt1-selected-chip-shelf {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  min-width: 0;
}

.bt1-selected-chip {
  border-color: #8fafbd;
  color: #2d6079;
  background: #eef6f9;
}

.bt1-multi-select-results {
  display: grid;
  gap: 6px;
  max-height: 280px;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 4px;
  border: 1px solid #d9e3ea;
  border-radius: 12px;
  background: #f8fbfc;
}

.bt1-settings-multi-select button:focus-visible,
.bt1-settings-multi-select input:focus-visible {
  outline: 3px solid rgba(70, 119, 145, 0.28);
  outline-offset: 2px;
}
```

Add inside the existing `@media (max-width: 760px)` block:

```css
.bt1-multi-select-compact {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.bt1-multi-select-toolbar button {
  flex: 1 1 140px;
}
```

- [x] **Step 5: Run GREEN, focused regression and production build**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_react_multi_select_is_modifier_free_and_adaptive \
  -q
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
cd app/web/components/backtest_analysis_decision_workspace/frontend
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
git diff --check
```

Expected: new test and full boundary suite pass, TypeScript/Vite build exits 0, diff-check exits 0.

- [x] **Step 6: Commit Task 21**

```bash
git add \
  tests/test_backtest_refactor_boundaries.py \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css
git diff --cached --check
git commit -m "Backtest Analysis 복수 선택 상호작용 개선"
```

### Task 22: Runtime QA, Finance Docs, And 8차 Closeout

**Files:**
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate, never stage: `backtest-analysis-level1-multi-select-desktop-qa.png`
- Generate, never stage: `backtest-analysis-level1-multi-select-760-qa.png`

**Interfaces:**
- Consumes: Task 21 adaptive React control.
- Produces: actual Quality/GTAA/large option interaction evidence, fresh automated verification,
  canonical flow alignment, protected-path audit and closeout commit.

- [x] **Step 1: Run actual desktop Browser QA**

At `http://localhost:8505/backtest`, choose `Quality + Value / Strict Annual` and click two
unselected Quality indicators without Command/Ctrl. Confirm the
selection summary grows from 5 to 6 to 7, both prior and new items remain selected, `전체 선택` and
`선택 해제` affect only that field, and no Streamlit page reset occurs. Choose GTAA and repeat with
two score lookback options. Open `고급 설정과 기술 근거`, locate the large defensive asset field,
search `SPY`, add it, confirm the chip, remove it through the chip, and verify initial results render
at most 100 rows. Capture the desktop screenshot without committing it.

- [x] **Step 2: Run 760px Browser QA**

Set viewport width 760px. Confirm compact options wrap to two columns, search input/chips/toolbar,
result list and CTA have horizontal overflow 0, keyboard focus is visible, iframe height follows
content, and strategy/field edits do not blank the fixed Level1 context. Capture the 760px screenshot
without committing it.

- [x] **Step 3: Use verification-before-completion for fresh automated checks**

```bash
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_backtest_single_settings_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_single_settings_workspace.py \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_analysis_workspace.py \
  app/web/components/backtest_analysis_decision_workspace/component.py
git diff --check
```

Record exact pass/fail counts and any pre-existing service baseline mismatch in `RUNS.md` and
`RISKS.md`; do not mask unrelated failures.

- [x] **Step 4: Use finance-doc-sync and audit protected paths**

Update the active task/root handoff logs and `BACKTEST_UI_FLOW.md` with adaptive multi-select
ownership, Python contract preservation, automated counts, Browser QA range/screenshots and remaining
risk. Then run:

```bash
git diff --check
git add \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
if git diff --cached --name-only | rg -q \
  'registries/|run_history/|saved/|\.superpowers/|\.png$|run_artifacts/'; then
  exit 1
fi
```

Expected: no registry, run history, saved JSONL, `.superpowers/`, screenshot or run artifact is staged.

- [x] **Step 5: Commit Task 22**

```bash
git commit -m "Backtest Analysis 복수 선택 QA와 문서 동기화"
```

## 8차 Completion Report Contract

- 전체 roadmap 1~8차 완료 상태와 남은 차수;
- 8차 design / implementation / closeout 한국어 commit 목록;
- focused / boundary / settings / decision / service exact test counts;
- React production build / target `py_compile` / `git diff --check` 결과;
- desktop / 760px QA 범위와 screenshot absolute links;
- registry / run history / saved / `.superpowers/` / screenshot 보호 감사;
- remaining risks and next handoff location.

## 9차 Corrective Plan: Deterministic Preset Application

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to execute
> Task 23~25 inline in the current worktree. Every production change must follow a witnessed
> RED -> GREEN cycle.

**Goal:** 모든 named preset이 strategy / variant 기본 규칙을 deterministic하게 적용하고,
검증 근거가 있는 GTAA preset만 명시적 override를 더해 universe와 선택·보유 규칙의 불일치를
없앤다.

**Architecture:** Python pure service가 schema default와 canonical override로
`preset_profiles`를 만들고 initial prefill precedence와 generic apply helper를 소유한다. React와
Python fallback은 profile의 `values`와 feedback만 기계적으로 적용하며 strategy별 숫자,
validation, payload 또는 Gate를 계산하지 않는다.

**Tech Stack:** Python 3.11+, Streamlit session state / fallback controls, React 18,
TypeScript 5.6, Vite 5, pytest / unittest, in-app Browser QA.

### Task 23: Python Preset Profile And Fallback TDD

**Files:**
- Modify: `app/web/backtest_common.py`
- Modify: `app/services/backtest_single_settings_workspace.py`
- Modify: `app/web/backtest_single_settings_workspace.py`
- Modify: `tests/test_backtest_single_settings_workspace.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: current schema field defaults, `GTAA_PRESETS`, legacy preset notes,
  `GTAA_PRESET_PARAMETER_DEFAULTS`, saved replay / prefill draft values.
- Produces: `preset_profiles` read-model property,
  `apply_single_settings_preset(workspace, values, preset_name)`, canonical GTAA override map,
  runtime injection and same-profile Python fallback callback.

- [x] **Step 1: Write failing canonical GTAA contract tests**

Extend `BacktestPresetCatalogContractTests` in `tests/test_service_contracts.py`:

```python
def test_gtaa_evidence_backed_presets_publish_parameter_defaults(self) -> None:
    from app.web.backtest_common import GTAA_PRESET_PARAMETER_DEFAULTS

    assert GTAA_PRESET_PARAMETER_DEFAULTS[
        "GTAA Universe (U3 Commodity Candidate Base)"
    ] == {
        "top": 2,
        "interval": 3,
        "score_lookback_months": [1, 3, 6],
    }
    assert GTAA_PRESET_PARAMETER_DEFAULTS[
        "GTAA Universe (U1 Offensive Candidate Base)"
    ] == {
        "top": 2,
        "interval": 3,
        "score_lookback_months": [1, 3, 6, 12],
    }
    assert GTAA_PRESET_PARAMETER_DEFAULTS[
        "GTAA Universe (U5 Smallcap Value Candidate Base)"
    ] == {
        "top": 3,
        "interval": 3,
        "score_lookback_months": [1, 3, 6, 12],
    }
    assert GTAA_PRESET_PARAMETER_DEFAULTS[
        "GTAA SPY Low-MDD Style Top-3"
    ] == {
        "top": 3,
        "interval": 3,
        "score_lookback_months": [1, 6],
        "trend_filter_window": 250,
        "risk_off_mode": "cash_only",
        "benchmark_ticker": "SPY",
    }
```

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_service_contracts.py::BacktestPresetCatalogContractTests::test_gtaa_evidence_backed_presets_publish_parameter_defaults \
  -q
```

Expected RED: missing U3 / U1 / U5 / Top-3 keys in `GTAA_PRESET_PARAMETER_DEFAULTS`.

- [x] **Step 2: Write failing pure profile and precedence tests**

Add an injected runtime fixture with two GTAA presets and parameter defaults to
`tests/test_backtest_single_settings_workspace.py`, then add:

```python
def test_every_named_preset_has_schema_safe_complete_profile() -> None:
    runtime = deepcopy(RUNTIME_OPTIONS)
    runtime["presets"]["GTAA"] = {
        "GTAA Universe": ["SPY", "TLT", "GLD"],
        "GTAA Evidence": ["QQQ", "IEF", "TLT"],
    }
    runtime["preset_parameter_defaults_by_strategy_key"] = {
        "gtaa": {
            "GTAA Evidence": {
                "top": 2,
                "interval": 4,
                "score_lookback_months": [1, 6],
                "defensive_tickers": ["IEF", "TLT"],
            }
        }
    }
    workspace = build_single_settings_workspace("GTAA", None, {}, runtime)
    field_ids = {
        field["field_id"]
        for section in workspace["sections"]
        for field in section["fields"]
    }

    assert set(workspace["preset_profiles"]) == {
        "GTAA Universe",
        "GTAA Evidence",
    }
    assert set(workspace["preset_profiles"]["GTAA Universe"]["values"]) <= field_ids
    assert workspace["preset_profiles"]["GTAA Universe"]["application_kind"] == "strategy_default"
    assert workspace["preset_profiles"]["GTAA Evidence"]["application_kind"] == "validated_override"
    assert workspace["preset_profiles"]["GTAA Evidence"]["values"]["top"] == 2
    assert workspace["preset_profiles"]["GTAA Evidence"]["values"]["interval"] == 4
```

Add a catalog-wide parametrized check so the contract is not GTAA-only:

```python
@pytest.mark.parametrize(
    ("strategy_choice", "variant"),
    [
        ("Equal Weight", None),
        ("GTAA", None),
        ("Global Relative Strength", None),
        ("Risk Parity Trend", None),
        ("Dual Momentum", None),
        ("Quality", "Annual"),
        ("Quality", "Quarterly"),
        ("Quality", "Snapshot"),
        ("Value", "Annual"),
        ("Value", "Quarterly"),
        ("Quality + Value", "Annual"),
        ("Quality + Value", "Quarterly"),
    ],
)
def test_all_named_preset_families_publish_complete_profiles(
    strategy_choice: str,
    variant: str | None,
) -> None:
    workspace = build_single_settings_workspace(
        strategy_choice,
        variant,
        {},
        RUNTIME_OPTIONS,
    )
    members = workspace["runtime_context"]["preset_members"]

    assert set(workspace["preset_profiles"]) == set(members)
    assert all(profile["values"] for profile in workspace["preset_profiles"].values())
```

```python
def test_apply_preset_resets_owned_fields_but_preserves_dates_and_manual_tickers() -> None:
    runtime = _runtime_with_gtaa_evidence_preset()
    workspace = build_single_settings_workspace("GTAA", None, {}, runtime)

    applied = apply_single_settings_preset(
        workspace,
        {
            "start": "2020-01-01",
            "end": "2025-12-31",
            "tickers": ["CUSTOM"],
            "top": 9,
            "interval": 9,
            "score_lookback_months": [12],
        },
        "GTAA Evidence",
    )

    assert applied["values"]["start"] == "2020-01-01"
    assert applied["values"]["end"] == "2025-12-31"
    assert applied["values"]["tickers"] == ["CUSTOM"]
    assert applied["values"]["universe_mode"] == "preset"
    assert applied["values"]["preset_name"] == "GTAA Evidence"
    assert applied["values"]["top"] == 2
    assert applied["values"]["interval"] == 4
    assert applied["values"]["score_lookback_months"] == [1, 6]
    assert applied["application"]["application_kind"] == "validated_override"
```

```python
def test_initial_explicit_prefill_wins_over_selected_preset_profile() -> None:
    runtime = _runtime_with_gtaa_evidence_preset()
    workspace = build_single_settings_workspace(
        "GTAA",
        None,
        {
            "preset_name": "GTAA Evidence",
            "top": 5,
            "score_lookback_months": [3, 12],
        },
        runtime,
    )
    values = _field_values(workspace)

    assert values["preset_name"] == "GTAA Evidence"
    assert values["top"] == 5
    assert values["score_lookback_months"] == [3, 12]
    assert values["interval"] == 4
```

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py::test_every_named_preset_has_schema_safe_complete_profile \
  tests/test_backtest_single_settings_workspace.py::test_all_named_preset_families_publish_complete_profiles \
  tests/test_backtest_single_settings_workspace.py::test_apply_preset_resets_owned_fields_but_preserves_dates_and_manual_tickers \
  tests/test_backtest_single_settings_workspace.py::test_initial_explicit_prefill_wins_over_selected_preset_profile \
  -q
```

Expected RED: `preset_profiles` and `apply_single_settings_preset` do not exist.

- [x] **Step 3: Implement canonical overrides and pure preset profiles**

Expand `GTAA_PRESET_PARAMETER_DEFAULTS` only with values already stated by the legacy preset notes.
In `app/services/backtest_single_settings_workspace.py`, add:

```python
_PRESET_PRESERVED_FIELD_IDS = frozenset({"start", "end", "tickers"})


def _build_preset_profiles(
    workspace: Mapping[str, object],
    *,
    concrete_strategy_key: str,
    runtime_options: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    fields = _all_fields(workspace)
    default_values = {
        str(field["field_id"]): deepcopy(field.get("value"))
        for field in fields
        if str(field["field_id"]) not in _PRESET_PRESERVED_FIELD_IDS
    }
    members = dict(dict(workspace["runtime_context"])["preset_members"])
    all_overrides = runtime_options.get("preset_parameter_defaults_by_strategy_key")
    strategy_overrides = (
        dict(all_overrides.get(concrete_strategy_key, {}))
        if isinstance(all_overrides, Mapping)
        and isinstance(all_overrides.get(concrete_strategy_key), Mapping)
        else {}
    )
    profiles: dict[str, dict[str, object]] = {}
    for preset_name in members:
        overrides = dict(strategy_overrides.get(preset_name, {}))
        values = {
            **deepcopy(default_values),
            **deepcopy(overrides),
            "universe_mode": "preset",
            "preset_name": preset_name,
        }
        profiles[preset_name] = {
            "application_kind": (
                "validated_override" if overrides else "strategy_default"
            ),
            "source_label": (
                "검증된 프리셋 설정을 적용했습니다."
                if overrides
                else "전략 기본 규칙을 적용했습니다."
            ),
            "values": values,
        }
    return profiles


def apply_single_settings_preset(
    workspace: Mapping[str, object],
    values: Mapping[str, object] | None,
    preset_name: str,
) -> dict[str, object]:
    profiles = workspace.get("preset_profiles")
    profile = profiles.get(preset_name) if isinstance(profiles, Mapping) else None
    if not isinstance(profile, Mapping):
        raise ValueError(f"알 수 없는 preset입니다: {preset_name}")
    updated = deepcopy(dict(values or {}))
    updated.update(deepcopy(dict(profile.get("values") or {})))
    return {
        "values": updated,
        "application": {
            "preset_name": preset_name,
            "application_kind": profile["application_kind"],
            "source_label": profile["source_label"],
        },
    }
```

Build `preset_profiles` after `runtime_context` exists, apply the supplied `preset_name` profile before
overlaying supplied explicit values, and export `apply_single_settings_preset`. Reject an override field
that is not declared by the current schema and validate its type/range/option through the existing
validator during the focused tests.

- [x] **Step 4: Inject runtime override ownership and add fallback application**

Add to `build_single_settings_runtime_options()`:

```python
"preset_parameter_defaults_by_strategy_key": {
    "gtaa": deepcopy(common.GTAA_PRESET_PARAMETER_DEFAULTS),
},
```

Import `deepcopy` and `apply_single_settings_preset`. Refactor `render_single_settings_fallback()` from
`st.form` to the same keyed native controls plus a final `st.button`, because Streamlit form widgets
cannot run preset callbacks before submit. For the `preset_name` selectbox, set an `on_change` callback
that reads the selected widget key, applies `apply_single_settings_preset()`, writes only profile values
to the corresponding `draft_key:field_id` session keys, stores the feedback label, and lets the normal
rerun redraw the controls. When `universe_mode` changes from manual to preset, invoke the same helper
for the current preset. Do not invoke the runner or persistence from either callback.

- [x] **Step 5: Run GREEN and focused Python regression**

```bash
uv run --with pytest python -m pytest \
  tests/test_service_contracts.py::BacktestPresetCatalogContractTests \
  tests/test_backtest_single_settings_workspace.py \
  -q
.venv/bin/python -m py_compile \
  app/services/backtest_single_settings_workspace.py \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_common.py
git diff --check
```

Expected: focused preset/settings tests pass, py_compile and diff-check exit 0.

- [x] **Step 6: Commit Task 23**

```bash
git add \
  app/web/backtest_common.py \
  app/services/backtest_single_settings_workspace.py \
  app/web/backtest_single_settings_workspace.py \
  tests/test_backtest_single_settings_workspace.py \
  tests/test_service_contracts.py
git diff --cached --check
git commit -m "Backtest Analysis 프리셋 적용 계약 복원"
```

### Task 24: React Generic Preset Application TDD

**Files:**
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: Task 23 `preset_profiles` with `application_kind`, `source_label`, `values`.
- Produces: strategy-agnostic preset reducer, manual-to-preset application, visible feedback and
  unchanged run intent payload.

- [x] **Step 1: Write failing React boundary contract**

Add to `tests/test_backtest_refactor_boundaries.py`:

```python
def test_react_settings_applies_python_owned_preset_profiles_without_strategy_rules(self) -> None:
    source = Path(
        "app/web/components/backtest_analysis_decision_workspace/frontend/src/"
        "BacktestAnalysisDecisionWorkspace.tsx"
    ).read_text()
    types = Path(
        "app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts"
    ).read_text()
    css = Path(
        "app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css"
    ).read_text()

    self.assertIn("preset_profiles", types)
    self.assertIn("applyPresetProfileChange", source)
    self.assertIn('fieldId === "preset_name"', source)
    self.assertIn('fieldId === "universe_mode" && nextValue === "preset"', source)
    self.assertIn("profile.values", source)
    self.assertIn("profile.source_label", source)
    self.assertIn("bt1-preset-application", source)
    self.assertIn(".bt1-preset-application", css)
    self.assertNotIn('workspace.strategy_choice === "GTAA"', source)
    self.assertNotIn("GTAA SPY Low-MDD", source)
```

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_react_settings_applies_python_owned_preset_profiles_without_strategy_rules \
  -q
```

Expected RED: preset profile types, reducer and feedback selectors are absent.

- [x] **Step 2: Add read-model types and generic reducer**

Add to `types.ts`:

```ts
export type SettingsPresetProfile = {
  application_kind: "strategy_default" | "validated_override"
  source_label: string
  values: Record<string, unknown>
}
```

Add `preset_profiles: Record<string, SettingsPresetProfile>` to `SingleSettingsWorkspace`. In the React
source, implement:

```tsx
type PresetApplication = {
  preset_name: string
  application_kind: "strategy_default" | "validated_override"
  source_label: string
}

function applyPresetProfileChange(
  workspace: SingleSettingsWorkspace,
  current: SettingsValues,
  fieldId: string,
  nextValue: unknown,
) {
  const changed = { ...current, [fieldId]: nextValue }
  const presetName =
    fieldId === "preset_name"
      ? String(nextValue)
      : fieldId === "universe_mode" && nextValue === "preset"
        ? String(changed.preset_name ?? "")
        : ""
  const profile = workspace.preset_profiles[presetName]
  if (!profile) return { values: changed, application: null }
  return {
    values: { ...changed, ...profile.values },
    application: {
      preset_name: presetName,
      application_kind: profile.application_kind,
      source_label: profile.source_label,
    },
  }
}
```

This reducer may branch only on generic schema field ids; it must not contain a strategy name or
preset-specific value.

- [x] **Step 3: Wire local state and feedback without rerun**

Add `presetApplication` state beside `values`. Replace the one-field `setFieldValue()` with the reducer,
setting both returned values and application. Reset feedback only when `workspace.draft_key` changes.
Pass the application message to the `preset_name` field control and render:

```tsx
{presetApplication && field.field_id === "preset_name" && (
  <p
    className={`bt1-preset-application is-${presetApplication.application_kind}`}
    role="status"
  >
    {presetApplication.source_label}
  </p>
)}
```

Keep `emitSettingsIntent("run_single_strategy", ..., values)` unchanged so Python validation and payload
projection remain authoritative.

- [x] **Step 4: Add compact feedback styling**

Add:

```css
.bt1-preset-application {
  margin: 8px 0 0;
  padding: 9px 11px;
  border: 1px solid #d3e0e7;
  border-radius: 10px;
  color: #486579;
  background: #f5f9fb;
  font-size: 0.88rem;
  line-height: 1.45;
}

.bt1-preset-application.is-validated_override {
  border-color: #9fbfcb;
  color: #285a6f;
  background: #edf6f8;
}
```

At 760px keep width at 100%, allow wrapping and horizontal overflow 0.

- [x] **Step 5: Run GREEN, focused regression and React build**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_backtest_single_settings_workspace.py \
  -q
cd app/web/components/backtest_analysis_decision_workspace/frontend
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
git diff --check
```

Expected: boundary/settings tests pass, TypeScript/Vite production build and diff-check exit 0.

- [x] **Step 6: Commit Task 24**

```bash
git add \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css \
  tests/test_backtest_refactor_boundaries.py
git diff --cached --check
git commit -m "Backtest Analysis 프리셋 자동 적용 UI 연결"
```

### Task 25: Runtime QA, Finance Docs, And 9차 Closeout

**Files:**
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate, never stage: `backtest-analysis-level1-preset-desktop-qa.png`
- Generate, never stage: `backtest-analysis-level1-preset-760-qa.png`

**Interfaces:**
- Consumes: Task 23 Python preset profile/fallback and Task 24 React reducer/feedback.
- Produces: actual all-family preset evidence, fresh verification, canonical docs alignment,
  protected-path audit and closeout commit.

- [x] **Step 1: Run desktop Browser QA across preset families**

At `http://localhost:8505/backtest`:

1. Equal Weight: change `Dividend ETFs -> Core ETFs`, confirm universe preset changes and strategy base
   `rebalance_interval=12` / cost defaults are restored after a manual edit.
2. GTAA base: manually edit top / interval / score horizons, switch to an ordinary GTAA universe, confirm
   base `top=3`, `interval=1`, `1/3/6/12` and `strategy_default` feedback.
3. GTAA U3: confirm `top=2`, `interval=3`, `1/3/6`.
4. GTAA Top-2 ADV20: confirm `top=2`, `interval=4`, `1/6`, `MA200`, `IEF/TLT`, `ADV20=20M`,
   `validated_override` feedback.
5. Quality + Value Annual: edit factor / overlay values, change managed preset and confirm variant base
   selection/holding/risk values return while start/end stay unchanged.
6. GRS: change core -> compact preset and confirm GRS base top / interval / score / trend values are
   restored. Risk Parity and Dual Momentum each have one named preset, so edit a base rule, move to direct
   input and back to preset, then confirm the strategy base profile is restored.
7. Direct input -> preset transition: confirm current selected preset applies and manual ticker draft is
   available when returning to direct input.

Do not run a backtest or trigger persistence. Capture desktop screenshot as a generated artifact only.

- [x] **Step 2: Run 760px Browser QA**

Set viewport width to 760px. Repeat GTAA validated preset and Quality + Value managed preset changes.
Confirm feedback copy wraps, settings cards remain one column, compact multi-select remains usable,
iframe height follows content and outer/settings horizontal overflow is 0. Capture the 760px screenshot
without staging it.

- [x] **Step 3: Use verification-before-completion for fresh automated checks**

```bash
uv run --with pytest python -m pytest tests/test_backtest_single_settings_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_single_settings_workspace.py \
  app/web/backtest_single_settings_workspace.py \
  app/web/backtest_common.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_analysis_workspace.py \
  app/web/components/backtest_analysis_decision_workspace/component.py
git diff --check
```

Record exact counts and compare repository-wide service failures to the existing 11-failure baseline;
do not hide unrelated failures.

- [x] **Step 4: Use finance-doc-sync and audit protected paths**

Update canonical flow, active task/root handoff logs with preset ownership, application precedence,
Browser QA evidence, test counts and remaining risks. Then run:

```bash
git diff --check
git add \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
if git diff --cached --name-only | rg -q \
  'registries/|run_history/|saved/|\.superpowers/|\.png$|run_artifacts/'; then
  exit 1
fi
```

Expected: no registry, run history, saved JSONL, `.superpowers/`, screenshot or run artifact is staged.

- [x] **Step 5: Commit Task 25**

```bash
git commit -m "Backtest Analysis 프리셋 적용 QA와 문서 동기화"
```

## 9차 Completion Report Contract

- 전체 roadmap 1~9차 완료 상태와 남은 차수;
- 9차 design / Python contract / React UI / closeout 한국어 commit 목록;
- focused / boundary / decision / service exact test counts;
- React production build / target `py_compile` / `git diff --check` 결과;
- desktop / 760px QA 범위와 screenshot absolute links;
- registry / run history / saved / `.superpowers/` / screenshot 보호 감사;
- remaining risks and next handoff location.

## 10차 Corrective Plan: Result Evidence And Level2 Handoff Workspace

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to execute
> Task 26~30 inline in the current worktree. Every behavior change must follow a witnessed
> RED -> GREEN cycle and every task ends with a Korean commit.

**Goal:** 실행 전에는 결과 영역을 숨기고, 성공 결과를 성과·차트·현재/목표 보유·Level2
검증 질문·사용자 표의 단일 흐름으로 제공하면서 Level1 technical handoff와 Level2 practical
validation 책임을 분리한다.

**Architecture:** 새 Python pure service가 lifecycle, result identity, formatted KPI, normalized
chart, current/target holdings, technical handoff, Level2 questions, evidence groups와 user tables를
JSON-ready read model로 만든다. 전용 React component와 Python fallback은 같은 read model을
표시하고, `backtest_result_display.py`는 state adapter와 compatibility appendix만 남긴다.

**Tech Stack:** Python 3.11+, pandas, Streamlit fragment/session state, React 18,
TypeScript 5.6, dependency-free SVG, Vite 5, pytest/unittest, in-app Browser QA.

### 10차 Global Constraints

- no-run과 first failure에서는 result workspace를 렌더링하지 않는다.
- 이전 성공 결과는 설정 변경·rerun·rerun failure 동안 reference로 보존한다.
- Level1 blocker는 실행, settings/result fingerprint, core result identity/contract,
  production maturity, callable handoff handler뿐이다.
- benchmark, rolling/split/OOS, cost/turnover, liquidity, ETF operability, concentration,
  latest-data replay와 evidence development는 Level2 validation question이다.
- `run_result_id`는 Level1 실행 identity이고 `validation_result_id`는 successful handoff 뒤의
  Level2 identity다. append-only validation registry row를 overwrite하지 않는다.
- current holdings는 backtest-simulated last valuation allocation, target은 last valid
  signal/rebalance allocation이며 broker account나 order가 아니다.
- React는 raw status classification, Gate, handler validation, percentage, weight,
  benchmark normalization을 계산하지 않는다.
- 신규 chart dependency를 추가하지 않는다.
- protected JSONL, saved setup, `.superpowers/`, screenshots, run artifacts는 stage하지 않는다.

### Task 26: Result Lifecycle, Technical Handoff, And Level2 Question Truth

**Files:**
- Create: `app/services/backtest_analysis_result_workspace.py`
- Create: `tests/test_backtest_analysis_result_workspace.py`

**Interfaces:**
- Consumes: configuration fingerprints, result bundle/meta, last error, strategy maturity,
  `save_and_move` handler availability.
- Produces: `build_result_lifecycle(...)`,
  `build_level1_technical_handoff_readiness(...)`,
  `build_level2_validation_questions(...)`. Existing runtime cutover is intentionally deferred to
  Task 29 so this pure-service commit cannot block current handoff before new run identities exist.

- [x] **Step 1: Write lifecycle and stage-ownership RED tests**

Create `tests/test_backtest_analysis_result_workspace.py` with a reusable result fixture and explicit
state matrix:

```python
from __future__ import annotations

import pandas as pd

from app.services.backtest_analysis_result_workspace import (
    build_level1_technical_handoff_readiness,
    build_level2_validation_questions,
    build_result_lifecycle,
)


def result_bundle(*, run_id: str = "run-current") -> dict:
    return {
        "strategy_name": "GTAA",
        "summary_df": pd.DataFrame([{"CAGR": 0.12}]),
        "chart_df": pd.DataFrame(
            [{"Date": "2026-06-30", "Total Balance": 100.0}]
        ),
        "result_df": pd.DataFrame(
            [{"Date": "2026-06-30", "Total Balance": 100.0}]
        ),
        "meta": {
            "run_id": run_id,
            "strategy_key": "gtaa",
            "benchmark_available": False,
            "rolling_review_status": "review",
            "etf_operability_status": "unavailable",
            "liquidity_policy_status": "caution",
        },
    }


def test_no_run_is_hidden_and_previous_error_result_is_reference() -> None:
    hidden = build_result_lifecycle(
        result_bundle=None,
        current_configuration_fingerprint="a",
        result_configuration_fingerprint=None,
        result_requires_rerun=False,
        is_running=False,
        last_error=None,
        last_error_kind=None,
    )
    failed_rerun = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="new",
        result_configuration_fingerprint="old",
        result_requires_rerun=True,
        is_running=False,
        last_error="provider timeout",
        last_error_kind="data",
    )
    assert hidden["state"] == "hidden"
    assert hidden["show_workspace"] is False
    assert failed_rerun["state"] == "error_with_reference"
    assert failed_rerun["show_workspace"] is True
    assert failed_rerun["reference_only"] is True


def test_level1_gate_ignores_practical_validation_signals() -> None:
    lifecycle = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        result_requires_rerun=False,
        is_running=False,
        last_error=None,
        last_error_kind=None,
    )
    readiness = build_level1_technical_handoff_readiness(
        workspace_kind="single_strategy",
        strategy_choice="GTAA",
        result_bundle=result_bundle(),
        lifecycle=lifecycle,
        action_handlers={"save_and_move": lambda payload: None},
    )
    assert readiness["state"] == "ready"
    assert readiness["can_handoff"] is True
    assert readiness["reasons"] == []


def test_practical_validation_gaps_become_level2_questions_once() -> None:
    questions = build_level2_validation_questions(
        meta=result_bundle()["meta"],
        workspace_kind="single_strategy",
        component_bundles=(),
    )
    assert {row["question_id"] for row in questions} >= {
        "benchmark_comparison",
        "rolling_oos_validation",
        "etf_operability",
        "liquidity_realism",
    }
    assert len({row["root_issue_id"] for row in questions}) == len(questions)
```

- [x] **Step 2: Run RED and witness missing service contracts**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py -q
```

Expected RED: import fails because `backtest_analysis_result_workspace.py` and its functions do not
exist.

- [x] **Step 3: Implement the lifecycle and Level1 technical gate**

Create the service with the exact state contract:

```python
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from app.services.backtest_strategy_catalog import LEVEL1_STRATEGY_MATURITY


BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION = (
    "backtest_analysis_result_workspace_v1"
)


def _strategy_maturity(strategy_choice: str | None) -> str:
    return LEVEL1_STRATEGY_MATURITY.get(str(strategy_choice or ""), "development")


def build_result_lifecycle(
    *,
    result_bundle: Mapping[str, Any] | None,
    current_configuration_fingerprint: str,
    result_configuration_fingerprint: str | None,
    result_requires_rerun: bool,
    is_running: bool,
    last_error: str | None,
    last_error_kind: str | None,
) -> dict[str, Any]:
    result_available = bool(result_bundle)
    fingerprint_matches = bool(
        result_available
        and result_configuration_fingerprint
        and current_configuration_fingerprint == result_configuration_fingerprint
    )
    reference_only = bool(
        result_available
        and (result_requires_rerun or not fingerprint_matches or last_error)
    )
    if is_running:
        state = "running_with_reference" if result_available else "running"
    elif last_error:
        state = "error_with_reference" if result_available else "error"
    elif not result_available:
        state = "hidden"
    elif reference_only:
        state = "stale"
    else:
        state = "fresh"
    display_labels = {
        "hidden": "",
        "running": "첫 결과를 만드는 중",
        "running_with_reference": "새 설정으로 실행 중",
        "error": "실행 결과를 만들지 못했습니다",
        "error_with_reference": "이전 설정 결과 · 참고용",
        "stale": "이전 설정 결과 · 참고용",
        "fresh": "현재 설정 결과",
    }
    return {
        "state": state,
        "display_label": display_labels[state],
        "show_workspace": result_available,
        "result_available": result_available,
        "fingerprint_matches": fingerprint_matches,
        "reference_only": reference_only or state == "running_with_reference",
        "is_running": is_running,
        "error": (
            {"kind": str(last_error_kind or "execution_failed"), "message": str(last_error)}
            if last_error
            else None
        ),
    }


def _core_result_reasons(result_bundle: Mapping[str, Any] | None) -> list[dict[str, str]]:
    bundle = dict(result_bundle or {})
    meta = dict(bundle.get("meta") or {})
    reasons: list[dict[str, str]] = []
    if not str(meta.get("run_id") or ""):
        reasons.append({"root_issue_id": "run_identity", "message": "실행 결과 식별자가 없습니다."})
    for key, label in (("summary_df", "성과 요약"), ("result_df", "결과 표"), ("chart_df", "성과 곡선")):
        value = bundle.get(key)
        if value is None or bool(getattr(value, "empty", False)):
            reasons.append({"root_issue_id": f"core:{key}", "message": f"{label} 계약이 비어 있습니다."})
    return reasons


def build_level1_technical_handoff_readiness(
    *,
    workspace_kind: str,
    strategy_choice: str | None,
    result_bundle: Mapping[str, Any] | None,
    lifecycle: Mapping[str, Any],
    action_handlers: Mapping[str, Callable[..., Any] | None],
) -> dict[str, Any]:
    if not lifecycle.get("result_available"):
        return {"state": "result_required", "label": "결과 준비 필요", "can_handoff": False, "reasons": [], "action": None}
    if workspace_kind == "single_strategy" and _strategy_maturity(strategy_choice) != "production":
        return {"state": "unsupported", "label": "인계 기능 미지원", "can_handoff": False, "reasons": [], "action": None}
    if not callable(action_handlers.get("save_and_move")):
        return {"state": "unsupported", "label": "인계 기능 미지원", "can_handoff": False, "reasons": [], "action": None}
    reasons = _core_result_reasons(result_bundle)
    if lifecycle.get("state") != "fresh":
        return {"state": "rerun_required", "label": "재실행 필요", "can_handoff": False, "reasons": reasons, "action": None}
    if reasons:
        return {"state": "result_required", "label": "결과 준비 필요", "can_handoff": False, "reasons": reasons, "action": None}
    return {
        "state": "ready",
        "label": "Level2 인계 가능",
        "can_handoff": True,
        "reasons": [],
        "action": {"id": "save_and_move", "label": "후보로 저장하고 Level2로 이동", "enabled": True},
    }
```

- [x] **Step 4: Implement deduplicated Level2 question projection**

Use a declarative field map and root deduplication; no practical signal may affect the technical gate:

```python
_LEVEL2_QUESTION_SPECS = (
    ("benchmark_comparison", "benchmark", "benchmark_available", {False, None, ""}, "기준지수와 손익·낙폭 비교", "동일 기간 기준지수와의 차이를 Practical Validation에서 확인합니다."),
    ("rolling_oos_validation", "temporal_validation", "rolling_review_status", {"review", "not_run", "unavailable", ""}, "구간별 성과 지속성", "rolling/OOS 구간에서 결과가 유지되는지 확인합니다."),
    ("split_oos_validation", "temporal_validation", "out_of_sample_review_status", {"review", "not_run", "unavailable", ""}, "분할·홀드아웃 재검증", "학습 외 구간의 재현성을 확인합니다."),
    ("cost_turnover_realism", "execution_realism", "net_cost_curve_status", {"not_run", "unavailable", "applied_without_turnover_estimate", ""}, "비용·교체 현실성", "turnover와 거래비용 반영 수준을 확인합니다."),
    ("liquidity_realism", "execution_realism", "liquidity_policy_status", {"caution", "review", "unavailable", ""}, "유동성 적합성", "보유 후보의 거래 가능 규모를 확인합니다."),
    ("etf_operability", "execution_realism", "etf_operability_status", {"caution", "review", "unavailable", ""}, "ETF 운용 가능성", "AUM·spread·holdings 근거를 확인합니다."),
    ("regime_validation", "temporal_validation", "regime_split_validation_status", {"review", "not_run", "unavailable", ""}, "시장 국면별 재현성", "상승·하락·중립 국면에서 결과가 유지되는지 확인합니다."),
    ("construction_overlap", "execution_realism", "construction_risk_status", {"review", "not_run", "unavailable", ""}, "집중도·중복 구성", "상위 보유 집중도와 구성 간 중복을 확인합니다."),
    ("latest_data_replay", "temporal_validation", "latest_data_replay_status", {"review", "not_run", "unavailable", ""}, "최신 데이터 재검증", "현재 DB 기준으로 같은 설정을 다시 실행해 차이를 확인합니다."),
    ("evidence_development", "execution_realism", "evidence_adapter_status", {"review", "not_run", "unavailable", ""}, "추가 검증 근거 필요 여부", "현재 근거로 확인할 수 없는 항목은 Level2에서 adapter 개발 필요성을 판단합니다."),
)


def build_level2_validation_questions(
    *,
    meta: Mapping[str, Any],
    workspace_kind: str,
    component_bundles: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    del workspace_kind, component_bundles
    lane_labels = {
        "benchmark": "성과·위험 검증",
        "temporal_validation": "기간·재현성 검증",
        "execution_realism": "실행 현실성 검증",
    }
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for question_id, lane, field, unresolved, title, summary in _LEVEL2_QUESTION_SPECS:
        raw = meta.get(field)
        normalized = str(raw).strip().lower() if not isinstance(raw, bool) else raw
        if normalized not in unresolved:
            continue
        root = f"level2:{lane}:{question_id}"
        if root in seen:
            continue
        seen.add(root)
        rows.append({
            "question_id": question_id,
            "root_issue_id": root,
            "lane": lane,
            "lane_label": lane_labels[lane],
            "status": "needs_validation",
            "title": title,
            "summary": summary,
        })
    return rows
```

Keep one root id across all lanes and counts.

- [x] **Step 5: Run GREEN, compile, and commit**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py -q
.venv/bin/python -m py_compile app/services/backtest_analysis_result_workspace.py
git diff --check
git add \
  app/services/backtest_analysis_result_workspace.py \
  tests/test_backtest_analysis_result_workspace.py
git diff --cached --check
git commit -m "Backtest Analysis 결과 인계 진실 분리"
```

Expected: new lifecycle/stage tests pass; compile/diff-check exit 0.

### Task 27: Performance, Holdings, Evidence, And User Table Read Model

**Files:**
- Modify: `app/services/backtest_analysis_result_workspace.py`
- Modify: `tests/test_backtest_analysis_result_workspace.py`

**Interfaces:**
- Consumes: Task 26 lifecycle/readiness/questions, single or weighted result bundle, optional benchmark
  and component bundles.
- Produces: `build_backtest_analysis_result_workspace(...)` with identity, formatted KPI, normalized chart,
  current/target holdings, four evidence groups, performance rows, holding-change rows and JSON-ready
  technical appendix.

- [x] **Step 1: Write holdings and result projection RED tests**

Add tests covering direct weight, balance-derived weight, cash-only, non-rebalance latest row, missing
holdings and partial Mix:

```python
def test_holdings_projects_current_and_last_valid_signal_without_future_guess() -> None:
    bundle = result_bundle()
    bundle["result_df"] = pd.DataFrame([
        {
            "Date": "2026-05-31", "Rebalancing": True,
            "End Ticker": ["SPY"], "End Balance": [100.0],
            "Next Ticker": ["SPY", "TLT"], "Next Weight": [0.6, 0.4],
            "Added Ticker": ["TLT"], "Removed Ticker": [],
            "Cash": 0.0, "Total Balance": 100.0,
        },
        {
            "Date": "2026-06-30", "Rebalancing": False,
            "End Ticker": ["SPY", "TLT"], "End Balance": [63.0, 39.0],
            "Next Ticker": ["SPY", "TLT"], "Next Balance": [63.0, 39.0],
            "Cash": 0.0, "Total Balance": 102.0,
        },
    ])
    model = build_backtest_analysis_result_workspace(
        workspace_kind="single_strategy",
        strategy_choice="GTAA",
        result_bundle=bundle,
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        result_requires_rerun=False,
        is_running=False,
        last_error=None,
        last_error_kind=None,
        action_handlers={"save_and_move": lambda payload: None},
        component_bundles=(),
    )
    assert model["holdings"]["current_allocation"] == [
        {"ticker": "SPY", "weight": 0.617647, "weight_label": "61.8%"},
        {"ticker": "TLT", "weight": 0.382353, "weight_label": "38.2%"},
    ]
    assert model["holdings"]["target_allocation"][0]["ticker"] == "SPY"
    assert model["holdings"]["status"] == "hold_current_until_rebalance"


def test_cash_only_is_not_an_empty_holding_state() -> None:
    bundle = result_bundle()
    bundle["result_df"] = pd.DataFrame([{
        "Date": "2026-06-30", "Rebalancing": True,
        "End Ticker": [], "End Balance": [], "Next Ticker": [],
        "Next Balance": [], "Cash": 100.0, "Total Balance": 100.0,
    }])
    model = build_backtest_analysis_result_workspace(
        workspace_kind="single_strategy", strategy_choice="GTAA",
        result_bundle=bundle, current_configuration_fingerprint="same",
        result_configuration_fingerprint="same", result_requires_rerun=False,
        is_running=False, last_error=None, last_error_kind=None,
        action_handlers={"save_and_move": lambda payload: None}, component_bundles=(),
    )
    assert model["holdings"]["current_allocation"] == [
        {"ticker": "현금", "weight": 1.0, "weight_label": "100.0%"}
    ]
    assert model["holdings"]["status"] == "cash_only"


def test_user_tables_and_chart_use_stable_labels_not_raw_columns() -> None:
    bundle = result_bundle()
    bundle["summary_df"] = pd.DataFrame([{
        "Start Date": "2026-05-31", "End Date": "2026-06-30",
        "Start Balance": 100.0, "End Balance": 102.0,
        "CAGR": 0.24, "Maximum Drawdown": -0.05,
        "Sharpe Ratio": 1.2, "Standard Deviation": 0.15,
    }])
    bundle["chart_df"] = pd.DataFrame([
        {"Date": "2026-05-31", "Total Balance": 100.0},
        {"Date": "2026-06-30", "Total Balance": 102.0},
    ])
    bundle["result_df"] = pd.DataFrame([
        {"Date": "2026-05-31", "Total Balance": 100.0, "Total Return": 0.0,
         "End Ticker": [], "End Balance": [], "Next Ticker": ["SPY"],
         "Next Balance": [100.0], "Rebalancing": True, "Cash": 0.0},
        {"Date": "2026-06-30", "Total Balance": 102.0, "Total Return": 0.02,
         "End Ticker": ["SPY"], "End Balance": [102.0], "Next Ticker": ["SPY"],
         "Next Balance": [102.0], "Rebalancing": False, "Cash": 0.0},
    ])
    model = build_backtest_analysis_result_workspace(
        workspace_kind="single_strategy", strategy_choice="GTAA",
        result_bundle=bundle,
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same", result_requires_rerun=False,
        is_running=False, last_error=None, last_error_kind=None,
        action_handlers={"save_and_move": lambda payload: None}, component_bundles=(),
    )
    assert [item["metric_id"] for item in model["performance_summary"]] == [
        "period", "cumulative_return", "cagr", "maximum_drawdown", "sharpe", "volatility"
    ]
    assert model["chart"]["strategy_series"][0]["value"] == 100.0
    assert list(model["performance_rows"][0]) == [
        "date", "balance", "period_return", "drawdown", "holding_count", "turnover", "cost"
    ]
    assert "Total Balance" not in model["performance_rows"][0]
```

- [x] **Step 2: Run RED and witness missing builder**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py -q
```

Expected RED: `build_backtest_analysis_result_workspace` and holdings/chart projections are absent.

- [x] **Step 3: Implement safe scalar/list/date and display helpers**

Add focused helpers that never expose pandas/numpy objects:

```python
def _format_percent(value: Any) -> str:
    numeric = _optional_float(value)
    return "-" if numeric is None else f"{numeric:.1%}"


def _allocation_rows(
    tickers: list[str],
    *,
    weights: list[float] | None = None,
    balances: list[float] | None = None,
    total_balance: float | None = None,
    cash: float | None = None,
) -> list[dict[str, Any]]:
    resolved = list(weights or [])
    if not resolved and balances and total_balance and total_balance > 0:
        resolved = [float(balance) / float(total_balance) for balance in balances[: len(tickers)]]
    rows = [
        {
            "ticker": ticker,
            "weight": round(resolved[index], 6) if index < len(resolved) else None,
            "weight_label": _format_percent(resolved[index]) if index < len(resolved) else "비중 근거 없음",
        }
        for index, ticker in enumerate(tickers)
    ]
    cash_weight = float(cash or 0.0) / float(total_balance or 0.0) if total_balance else 0.0
    if cash_weight > 0 or (not rows and cash and total_balance):
        rows.append({"ticker": "현금", "weight": round(cash_weight, 6), "weight_label": _format_percent(cash_weight)})
    return rows
```

Use strict list length alignment. If ticker/weight/balance cells cannot be parsed, return an explicit
`unavailable_reason`; never assume equal weights except where a strategy row already provides equal
`End Balance` / `Next Balance`.

- [x] **Step 4: Implement chart, holdings, tables, evidence groups, and top-level builder**

The builder must return the exact shape consumed by Task 28:

```python
def build_backtest_analysis_result_workspace(
    *,
    workspace_kind: str,
    strategy_choice: str | None,
    result_bundle: Mapping[str, Any] | None,
    current_configuration_fingerprint: str,
    result_configuration_fingerprint: str | None,
    result_requires_rerun: bool,
    is_running: bool,
    last_error: str | None,
    last_error_kind: str | None,
    action_handlers: Mapping[str, Callable[..., Any] | None],
    component_bundles: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    lifecycle = build_result_lifecycle(
        result_bundle=result_bundle,
        current_configuration_fingerprint=current_configuration_fingerprint,
        result_configuration_fingerprint=result_configuration_fingerprint,
        result_requires_rerun=result_requires_rerun,
        is_running=is_running,
        last_error=last_error,
        last_error_kind=last_error_kind,
    )
    if not lifecycle["show_workspace"]:
        return {
            "schema_version": BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION,
            "visible": False,
            "lifecycle": lifecycle,
        }
    bundle = dict(result_bundle or {})
    meta = dict(bundle.get("meta") or {})
    readiness = build_level1_technical_handoff_readiness(
        workspace_kind=workspace_kind,
        strategy_choice=strategy_choice,
        result_bundle=bundle,
        lifecycle=lifecycle,
        action_handlers=action_handlers,
    )
    return {
        "schema_version": BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION,
        "visible": True,
        "configuration_fingerprint": current_configuration_fingerprint,
        "lifecycle": lifecycle,
        "identity": {
            "run_result_id": str(meta.get("run_id") or ""),
            "candidate_source_id": str(meta.get("selection_source_id") or ""),
            "validation_result_id": str(meta.get("validation_result_id") or ""),
            "strategy_name": str(bundle.get("strategy_name") or strategy_choice or "Portfolio Mix"),
            "variant_name": str(meta.get("variant") or ""),
        },
        "performance_summary": _performance_summary(bundle.get("summary_df"), bundle.get("result_df")),
        "chart": _chart_projection(bundle),
        "holdings": _holdings_projection(bundle, component_bundles=component_bundles),
        "technical_handoff_readiness": readiness,
        "level2_validation_questions": build_level2_validation_questions(
            meta=meta, workspace_kind=workspace_kind, component_bundles=component_bundles
        ),
        "evidence_groups": _evidence_groups(bundle),
        "performance_rows": _performance_rows(bundle.get("result_df")),
        "holding_change_rows": _holding_change_rows(bundle.get("result_df")),
        "technical_appendix": _technical_appendix(bundle),
        "actions": {"save_and_move": readiness["action"]} if readiness.get("action") else {},
        "boundaries": {
            "react_calculates_gate": False,
            "react_calculates_weights": False,
            "react_classifies_status": False,
            "python_validates_intent": True,
        },
    }
```

Implementation requirements:

- normalize strategy and benchmark curves to `100.0` at the common first valid date;
- project high, low and maximum-drawdown markers only when calculable;
- build current allocation from latest valuation `End Ticker`/`End Balance` and cash; for static
  Equal Weight rows only, allow `Ticker` when its length exactly matches `End Balance`;
- build target allocation from last valid signal/rebalance `Next Ticker`, explicit `Next Weight` first,
  then `Next Balance / Total Balance`; for static Equal Weight rows only, allow `Ticker` when its length
  exactly matches `Next Balance`;
- when latest row is not a rebalance row set `status=hold_current_until_rebalance`;
- aggregate Portfolio Mix underlying ticker weights only when all component target evidence exists;
  otherwise return component allocations plus `evidence_status=partial`;
- performance rows use only date/balance/period return/drawdown/holding count/turnover/cost;
- holding-change rows use only date/state/current/target/additions/removals/cash;
- cap component props to 420 user rows and 100 appendix preview rows while preserving full raw data only
  in the Python compatibility path.

- [x] **Step 5: Add all-family result-column boundary matrix**

In `tests/test_backtest_analysis_result_workspace.py`, create a matrix over Equal Weight, GTAA/GRS, Risk Parity,
Dual Momentum, strict factor and weighted Mix fixture shapes. For each, call the pure builder and assert:

```python
self.assertTrue(workspace["visible"])
self.assertEqual(workspace["identity"]["run_result_id"], case["run_id"])
self.assertIn(workspace["holdings"]["status"], {
    "available", "cash_only", "hold_current_until_rebalance", "partial", "unavailable"
})
self.assertEqual(len({row["root_issue_id"] for row in workspace["level2_validation_questions"]}),
                 len(workspace["level2_validation_questions"]))
```

- [x] **Step 6: Run GREEN, focused service regression, compile, and commit**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py \
  tests/test_backtest_analysis_decision_workspace.py -q
.venv/bin/python -m py_compile app/services/backtest_analysis_result_workspace.py
git diff --check
git add \
  app/services/backtest_analysis_result_workspace.py \
  tests/test_backtest_analysis_result_workspace.py
git diff --cached --check
git commit -m "Backtest Analysis 결과 근거 읽기 모델 구현"
```

Expected: focused result/decision tests pass; compile/diff-check exit 0.

### Task 28: Dedicated React Result Workspace And Python Fallback

**Files:**
- Create: `app/web/components/backtest_analysis_result_workspace/__init__.py`
- Create: `app/web/components/backtest_analysis_result_workspace/component.py`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/package.json`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/package-lock.json`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/tsconfig.json`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/vite.config.ts`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/index.html`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/src/index.tsx`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/src/ResultWorkspaceChart.tsx`
- Create: `app/web/components/backtest_analysis_result_workspace/frontend/src/style.css`
- Create: `app/web/backtest_analysis_result_workspace_panel.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: Task 27 `BacktestAnalysisResultWorkspace` JSON model.
- Produces: `render_backtest_analysis_result_workspace_component(...)`, availability helper,
  same-read-model fallback and `save_and_move` presentation intent only.

- [x] **Step 1: Write RED visual and ownership boundary tests**

Add a focused boundary test that requires dedicated files and forbids React-side domain logic:

```python
def test_level1_result_workspace_is_dedicated_intent_only_and_responsive(self) -> None:
    root = PROJECT_ROOT / "app/web/components/backtest_analysis_result_workspace/frontend/src"
    source = (root / "BacktestAnalysisResultWorkspace.tsx").read_text()
    chart = (root / "ResultWorkspaceChart.tsx").read_text()
    types = (root / "types.ts").read_text()
    css = (root / "style.css").read_text()
    index = (root / "index.tsx").read_text()

    for token in (
        "performance_summary", "strategy_series", "current_allocation",
        "target_allocation", "technical_handoff_readiness",
        "level2_validation_questions", "evidence_groups",
        "performance_rows", "holding_change_rows", "technical_appendix",
    ):
        self.assertIn(token, types)
    self.assertIn('emitIntent("save_and_move"', source)
    self.assertIn("<svg", chart)
    self.assertIn("ResizeObserver", index)
    self.assertIn("@media (max-width: 760px)", css)
    self.assertNotIn("benchmark_available", source)
    self.assertNotIn("Next Balance", source)
    self.assertNotIn("canHandoff =", source)
    self.assertNotIn("/ total", source)
```

Run only this test and witness RED because the dedicated component does not exist.

- [x] **Step 2: Create component wrapper, Vite project, and exact read-model types**

Use component name `backtest_analysis_result_workspace`. The Python wrapper accepts only `workspace`,
`key`, and `on_change`; the TypeScript type mirrors Task 27 fields. Define intent as:

```ts
export type ResultWorkspaceIntent = {
  action: "save_and_move"
  payload: {
    run_result_id: string
    current_configuration_fingerprint: string
  }
  nonce: string
}
```

The component wrapper returns a dict only; availability depends on `frontend/build/index.html`.

- [x] **Step 3: Implement dependency-free SVG chart and single-flow result UI**

Adapt the Final Review `DecisionBriefCharts.tsx` visual language without importing or adding a package.
The component order must be exactly:

```tsx
<main className="bt1r-workspace">
  <ResultHeader identity={workspace.identity} lifecycle={workspace.lifecycle} />
  <PerformanceSummary items={workspace.performance_summary} />
  <ResultWorkspaceChart chart={workspace.chart} />
  <HoldingsComparison holdings={workspace.holdings} />
  <HandoffAndQuestions
    readiness={workspace.technical_handoff_readiness}
    questions={workspace.level2_validation_questions}
    onHandoff={() => emitIntent("save_and_move", {
      run_result_id: workspace.identity.run_result_id,
      current_configuration_fingerprint: workspace.configuration_fingerprint,
    })}
  />
  <EvidenceGroups groups={workspace.evidence_groups} />
  <UserTables
    performanceRows={workspace.performance_rows}
    holdingRows={workspace.holding_change_rows}
  />
  <TechnicalAppendix appendix={workspace.technical_appendix} />
</main>
```

Render no action board when `workspace.actions` is empty. Use local disclosure and table-page state only;
all labels, formatted values, state, count and availability come from Python.

- [x] **Step 4: Implement same-read-model Python fallback**

Create `render_backtest_analysis_result_workspace_fallback(workspace)`. Return `None` unless the enabled
`save_and_move` button is clicked. Render the same order with `st.metric`, `st.line_chart` from prepared
series, holdings/evidence cards, user-facing dataframes and one collapsed technical appendix. Do not call
`build_next_step_readiness_evaluation()` or calculate weights/status in the fallback.

- [x] **Step 5: Add responsive and accessibility contract**

- use `color-scheme: light` and workspace-scoped text colors;
- desktop KPI/holdings/question cards use at most two columns;
- `@media (max-width: 760px)` makes all grids one column;
- table shells use bounded internal scrolling without expanding page width;
- chart has `<title>`, `<desc>`, focusable point/tooltip behavior and visible legend;
- `ResizeObserver` updates Streamlit frame height after disclosure/table changes;
- lifecycle reference/running/error uses `role=status` or `role=alert` without removing prior content.

- [x] **Step 6: Run GREEN boundary, production build, compile, and commit**

```bash
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
cd app/web/components/backtest_analysis_result_workspace/frontend
npm install
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/web/backtest_analysis_result_workspace_panel.py \
  app/web/components/backtest_analysis_result_workspace/component.py
git diff --check
git add \
  app/web/components/backtest_analysis_result_workspace \
  app/web/backtest_analysis_result_workspace_panel.py \
  tests/test_backtest_refactor_boundaries.py
git diff --cached --check
git commit -m "Backtest Analysis 결과 워크스페이스 UI 구현"
```

Expected: boundary tests, 175+ module Vite production build, py_compile and diff-check pass. Do not
stage `node_modules/` or generated QA screenshots.

### Task 29: Runtime Lifecycle, Adapter, Fallback Cutover, And Legacy Cleanup

**Files:**
- Create: `app/web/backtest_analysis_result_workspace.py`
- Modify: `app/services/backtest_analysis_decision_workspace.py`
- Modify: `app/web/backtest_result_display.py`
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `app/web/backtest_single_runner.py`
- Modify: `app/web/backtest_compare/page.py`
- Modify: `app/runtime/backtest/stores/run_history.py`
- Modify: `app/web/backtest_candidate_review_helpers.py`
- Modify: `app/services/backtest_practical_validation_source.py`
- Modify: `tests/test_backtest_analysis_decision_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 27 pure builder, Task 28 component/fallback, existing Python action handlers.
- Produces: current session-state adapter, validated `save_and_move` intent, no-run hidden route,
  preserved stale/running/error result, new run identity and primary legacy-detail cutover.

- [x] **Step 1: Write RED route, lifecycle, identity, and intent tests**

Add tests asserting:

```python
def test_result_route_hides_before_first_run_and_removes_legacy_expander() -> None:
    source = Path("app/web/backtest_result_display.py").read_text()
    body = source.split("def _render_last_run()", 1)[1].split("\ndef ", 1)[0]
    assert body.index("if not bundle") < body.index("render_backtest_analysis_result_workspace")
    assert 'st.expander("상세 근거"' not in body
    assert "render_backtest_analysis_decision_surface" not in body


def test_result_intent_requires_exact_current_run_and_enabled_action() -> None:
    workspace = {
        "configuration_fingerprint": "fingerprint-current",
        "identity": {"run_result_id": "run-current"},
        "actions": {"save_and_move": {"enabled": True}},
    }
    assert validate_result_workspace_intent(
        {"action": "save_and_move", "payload": {
            "run_result_id": "run-current",
            "current_configuration_fingerprint": workspace["configuration_fingerprint"],
        }, "nonce": "n-1"},
        workspace=workspace,
    )["ok"] is True
    assert validate_result_workspace_intent(
        {"action": "save_and_move", "payload": {"run_result_id": "run-old"}, "nonce": "n-2"},
        workspace=workspace,
    )["ok"] is False
```

Add runner/page source contracts requiring `meta["run_id"]`, pending single execution, old result
preservation on weighted failure and removal of `_render_real_money_details_legacy` after a repository-wide
reference assertion.

- [x] **Step 2: Build state adapter and validated intent dispatcher**

Create `build_current_backtest_analysis_result_workspace()` by adapting:

- single: `backtest_last_bundle`, current/result fingerprint, rerun flag, pending flag, last error;
- Mix: `backtest_weighted_bundle`, current/result fingerprint, pending/error, component bundles;
- action handlers from `build_backtest_analysis_action_handlers()`.

Implement `validate_result_workspace_intent(intent, workspace)` and consume only when:

- nonce is new;
- action is `save_and_move`;
- enabled action exists in the current read model;
- payload run id equals `identity.run_result_id`;
- payload fingerprint equals current configuration fingerprint;
- Python resolves a callable handler at dispatch time.

Do not trust component `enabled`, state or handler name.

In the same task, change `build_level1_readiness_projection()` compatibility output so `handoff_state`
and `save_and_move` availability delegate to Task 26 technical truth. Preserve the old read-model keys
for the context surface, but expose practical gaps only as
`evaluation["level2_validation_questions"]`; do not use
`build_next_step_readiness_evaluation()` to decide the Level2 action.

- [x] **Step 3: Assign stable run identity before persistence**

In every successful current execution path, before storing bundle and appending history:

```python
from uuid import uuid4

bundle["meta"] = dict(bundle.get("meta") or {})
bundle["meta"].setdefault("run_id", f"level1-{uuid4().hex}")
```

Apply this to single runner, new weighted Mix, and saved Mix replay weighted bundle. Component strategy
comparison bundles remain component evidence; the weighted result owns the Level1 `run_result_id`.

Persist the same identity across handoff boundaries by inserting these exact entries in the existing
record/return mappings:

```python
# app/runtime/backtest/stores/run_history.py
"run_result_id": meta.get("run_id"),

# app/web/backtest_candidate_review_helpers.py
"run_result_id": meta.get("run_id"),

# app/services/backtest_practical_validation_source.py
"run_result_id": draft.get("run_result_id"),
```

Add the same top-level `run_result_id` to weighted/saved Mix prefill payloads and selection sources. The
new field is additive and must not change current schema versions or rewrite existing JSONL rows.

- [x] **Step 4: Queue single execution so the previous result renders during rerun**

Change the validated settings intent handler to queue normalized payload and strategy name in
`backtest_pending_single_run` instead of executing inside the component callback. At the end of the
fragment flow:

```python
pending = st.session_state.get("backtest_pending_single_run")
_render_last_run(is_running=bool(pending))
if isinstance(pending, dict):
    try:
        _handle_backtest_run(
            dict(pending["payload"]),
            strategy_name=str(pending["strategy_name"]),
        )
    finally:
        st.session_state.pop("backtest_pending_single_run", None)
    st.rerun(scope="fragment")
```

The React settings button keeps its existing local `실행 요청 중…` state. The result builder receives
`is_running=True`, so the previous success stays visible with `새 설정으로 실행 중`. First execution has
no result workspace and shows progress only. Deduplicate the queued intent id before execution.

- [x] **Step 5: Preserve weighted result on failure and cut over primary result route**

- do not clear `backtest_weighted_bundle` when a new weighted build or saved replay fails;
- mark the old result reference-only through current/result fingerprint or error state;
- make `_render_last_run(is_running=False)` return before component mount when bundle is absent;
- replace old decision surface and collapsed detail expander with the dedicated result workspace renderer;
- render first-run errors adjacent to settings without an empty result shell;
- keep full raw table/meta export only inside the new technical appendix/fallback compatibility path.

- [x] **Step 6: Prove and remove the unused real-money legacy renderer**

Run:

```bash
rg -n "_render_real_money_details_legacy" app tests
```

Expected before removal: one definition and no caller. Add a boundary assertion for zero definition/caller,
then remove the complete function. Do not remove helpers still referenced by history, compare or Practical
Validation adapters.

- [x] **Step 7: Run GREEN, focused/full regression, React builds, compile, and commit**

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd ../../backtest_analysis_result_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_result_workspace.py \
  app/services/backtest_analysis_decision_workspace.py \
  app/web/backtest_analysis_result_workspace_panel.py \
  app/web/backtest_result_display.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_single_runner.py \
  app/web/backtest_compare/page.py \
  app/runtime/backtest/stores/run_history.py \
  app/web/backtest_candidate_review_helpers.py \
  app/services/backtest_practical_validation_source.py
git diff --check
git add \
  app/web/backtest_analysis_result_workspace.py \
  app/services/backtest_analysis_decision_workspace.py \
  app/web/backtest_result_display.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_single_runner.py \
  app/web/backtest_compare/page.py \
  app/runtime/backtest/stores/run_history.py \
  app/web/backtest_candidate_review_helpers.py \
  app/services/backtest_practical_validation_source.py \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py
git diff --cached --check
git commit -m "Backtest Analysis 결과 실행 흐름 전환"
```

Expected: focused suites pass; full service result matches or improves baseline; both React builds,
py_compile and diff-check exit 0.

### Task 30: Runtime Browser QA, Finance Docs, And 10차 Closeout

**Files:**
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate, never stage: `backtest-analysis-level1-result-workspace-desktop-qa.png`
- Generate, never stage: `backtest-analysis-level1-result-workspace-760-qa.png`

**Interfaces:**
- Consumes: Task 26~29 result truth, read model, UI and runtime lifecycle.
- Produces: actual all-family evidence, desktop/760px screenshots, fresh verification, canonical docs and
  protected-file audit.

- [x] **Step 1: Run desktop Browser QA on current local app**

At the current Backtest route:

1. open fresh Level1 and confirm no Step 3/result/detail shell before first run;
2. run Equal Weight and verify formatted KPI, normalized strategy chart, current/target holdings,
   technical handoff state, Level2 question lanes, user tables and technical appendix;
3. change one setting and verify previous result says `이전 설정 결과 · 참고용` and handoff is locked;
4. rerun and verify old result remains with running state until atomic fresh replacement;
5. inject or reproduce one controlled failure and verify old result plus error remains while handoff stays locked;
6. run GTAA, GRS, Risk Parity, Dual Momentum, one strict factor family and Portfolio Mix; verify each produces
   the same result hierarchy and no raw code path/decimal-first copy;
7. verify development Risk-On result can be viewed but says `인계 기능 미지원`;
8. verify successful `save_and_move` uses current run identity and opens the existing Practical Validation route.

Do not rewrite or stage the validation registry generated by QA. Capture desktop screenshot only as a local
artifact.

- [x] **Step 2: Run 760px Browser QA**

Set viewport width to 760px and repeat fresh result, stale result, holdings comparison, chart tooltip,
questions, user tables and technical appendix. Confirm:

- KPI/holdings/questions are one column;
- chart labels and holdings do not overlap;
- internal table scrolling does not expand outer page;
- `document.documentElement.scrollWidth === clientWidth` for app and component iframe;
- ResizeObserver updates height after disclosures;
- no browser console application error.

Capture the 760px screenshot without staging it.

- [x] **Step 3: Use verification-before-completion for fresh automated checks**

```bash
uv run --with pytest python -m pytest tests/test_backtest_analysis_result_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd ../../backtest_analysis_result_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_analysis_result_workspace.py \
  app/services/backtest_analysis_decision_workspace.py \
  app/web/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_result_workspace_panel.py \
  app/web/backtest_result_display.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_single_runner.py \
  app/web/backtest_compare/page.py \
  app/runtime/backtest/stores/run_history.py \
  app/web/backtest_candidate_review_helpers.py \
  app/services/backtest_practical_validation_source.py \
  app/web/components/backtest_analysis_result_workspace/component.py
git diff --check
```

Record exact test counts, build module counts, compiler results and any repository baseline failure. Do not
describe an existing failure as a new pass.

- [x] **Step 4: Use finance-doc-sync and audit protected paths**

Update canonical ownership/flow docs with:

- no-run hidden result surface;
- technical Level1 handoff versus Level2 validation questions;
- result workspace service/component/fallback ownership;
- backtest current/target holdings meaning;
- stale/running/error preservation and run/validation identity boundary.

Then stage only canonical docs and active task/root handoff logs:

```bash
git diff --check
git add \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md \
  .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
if git diff --cached --name-only | rg -q \
  'registries/|run_history/|saved/|\.superpowers/|\.png$|run_artifacts/'; then
  exit 1
fi
```

- [x] **Step 5: Commit Task 30**

```bash
git commit -m "Backtest Analysis 결과 워크스페이스 QA와 문서 동기화"
```

## 10차 Completion Report Contract

- 전체 roadmap 1~10차 완료 상태와 남은 차수;
- 10차 design / plan / truth / read-model / UI / lifecycle / closeout 한국어 commit 목록;
- focused result / decision / boundary / service exact test counts;
- two React production builds / target `py_compile` / `git diff --check` 결과;
- desktop / 760px Browser QA 범위와 screenshot absolute links;
- registry / run history / saved / `.superpowers/` / screenshot 보호 감사;
- remaining risks and next handoff location.

# Backtest Analysis Current Selection And Factor Presentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 현재 전략 설정, 이전 실행 결과, factor 사용자 표시명과 원본 기술 근거를 분리해 Level1의 남은 Streamlit 레거시와 잘못된 GTAA 설정 투영을 제거한다.

**Architecture:** Python service가 context summary, factor value/label, stale reference reason/message를 소유하고 React와 Python fallback은 전달받은 사용자 계약만 표시한다. 이전 성공 결과와 raw payload는 보존하지만 current settings와 섞지 않고 first-read 운영 표와 snake_case label을 제거한다.

**Tech Stack:** Python 3.12, Streamlit, React 18, TypeScript, CSS, pytest, Vite

## Global Constraints

- 기존 worktree `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev`와 branch `codex/backtest-dev`를 그대로 사용한다.
- factor 계산 value와 runner payload key는 변경하지 않는다.
- 이전 성공 결과는 참고용으로 보존하고 strategy 변경 시 삭제하지 않는다.
- React는 strategy 일치 판정, stale 원인 분류, factor key 번역 또는 Gate 계산을 하지 않는다.
- raw run/job/status 중심 운영 진단 dashboard를 추가하지 않는다.
- registry, run history, saved JSONL, `.superpowers/`, screenshot, run artifact를 stage/commit하지 않는다.
- 모든 기능과 버그 수정은 RED → GREEN으로 확인하고 distinct implementation unit마다 한국어 commit을 만든다.
- desktop / 760px Browser QA와 fresh verification-before-completion을 수행한다.

---

### Task 35: Current Selection Context Contract

**Files:**
- Modify: `app/services/backtest_analysis_decision_workspace.py`
- Test: `tests/test_backtest_analysis_decision_workspace.py`

**Interfaces:**
- Consumes: `build_backtest_analysis_decision_workspace(workspace_kind, selection, configuration, ...)`의 current selection과 draft configuration.
- Produces: `_configuration_summary(workspace_kind: str, configuration: Mapping[str, Any]) -> dict[str, Any]`; Single Strategy는 빈 summary, Portfolio Mix는 사용자 label을 가진 compact summary를 반환한다.

- [x] **Step 1: Write the failing current-selection tests**

Add these tests to `tests/test_backtest_analysis_decision_workspace.py`:

```python
def test_single_context_does_not_project_previous_strategy_raw_configuration() -> None:
    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "Quality + Value"},
        configuration={
            "strategy_key": "gtaa",
            "timeframe": "1d",
            "option": "month_end",
            "promotion_min_benchmark_coverage": 0.95,
        },
        result_bundle=_successful_bundle(),
        result_configuration_fingerprint="previous",
        saved_mixes=[],
        last_error=None,
        last_error_kind=None,
        action_handlers={"save_and_move": lambda payload: None},
    )

    assert workspace["current_work"]["title"] == "Quality + Value"
    assert workspace["configuration_summary"] == {}


def test_portfolio_mix_context_uses_user_configuration_labels() -> None:
    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="portfolio_mix",
        selection={"mix_name": "Balanced Mix", "mix_mode": "new"},
        configuration={
            "strategy_names": ["GTAA", "Equal Weight"],
            "weights_percent": [60.0, 40.0],
            "component_roles": ["core", "satellite"],
        },
        result_bundle=None,
        result_configuration_fingerprint=None,
        saved_mixes=[],
        last_error=None,
        last_error_kind=None,
        action_handlers={"save_mix": lambda payload: None, "save_and_move": lambda payload: None},
    )

    assert workspace["configuration_summary"] == {
        "구성 전략": "GTAA, Equal Weight",
        "목표 비중": "60%, 40%",
        "구성 수": 2,
    }
    assert "strategy_names" not in workspace["configuration_summary"]
```

- [x] **Step 2: Run RED and confirm the stale GTAA summary failure**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_decision_workspace.py::test_single_context_does_not_project_previous_strategy_raw_configuration \
  tests/test_backtest_analysis_decision_workspace.py::test_portfolio_mix_context_uses_user_configuration_labels -q
```

Expected: FAIL because Single Strategy returns the raw GTAA dictionary and Portfolio Mix uses raw snake_case keys.

- [x] **Step 3: Implement the minimal Python-owned context summary**

Add this helper near `_metric_items()` in `app/services/backtest_analysis_decision_workspace.py`:

```python
def _configuration_summary(
    workspace_kind: str,
    configuration: Mapping[str, Any],
) -> dict[str, Any]:
    """Keep previous run payloads out of the current Single Strategy selector."""

    if workspace_kind == "single_strategy":
        return {}
    strategy_names = [
        str(name) for name in list(configuration.get("strategy_names") or [])
    ]
    weights = [
        float(weight) for weight in list(configuration.get("weights_percent") or [])
    ]
    return {
        "구성 전략": ", ".join(strategy_names) or "구성 전",
        "목표 비중": ", ".join(f"{weight:g}%" for weight in weights) or "설정 전",
        "구성 수": len(strategy_names),
    }
```

Replace the raw projection in `build_backtest_analysis_decision_workspace()`:

```python
"configuration_summary": _configuration_summary(
    workspace_kind,
    configuration,
),
```

Do not clear `backtest_current_draft_payload` or `backtest_last_bundle`; the projection boundary alone prevents the wrong GTAA summary.

- [x] **Step 4: Run GREEN and focused decision regression**

Run:

```bash
uv run --with pytest python -m pytest tests/test_backtest_analysis_decision_workspace.py -q
```

Expected: all decision workspace tests PASS and existing stale result preservation remains unchanged.

- [x] **Step 5: Commit the current-selection unit**

```bash
git add \
  app/services/backtest_analysis_decision_workspace.py \
  tests/test_backtest_analysis_decision_workspace.py
git diff --cached --check
git commit -m "Backtest Analysis 현재 선택 설정 경계 수정"
```

### Task 36: Human-Readable Factor Option Contract And Responsive Grid

**Files:**
- Modify: `app/services/backtest_single_settings_workspace.py`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx`
- Modify: `app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css`
- Test: `tests/test_backtest_single_settings_workspace.py`
- Test: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: runtime `quality_factor_options` / `value_factor_options` raw key arrays.
- Produces: `factor_option_label(value: str) -> str`, option objects `{value: raw_key, label: user_label}`, React `.bt1-multi-select-option-label` presentation, unchanged submitted raw arrays.

- [x] **Step 1: Write RED tests for every factor label and unchanged payload**

Add to `tests/test_backtest_single_settings_workspace.py`:

```python
def test_strict_factor_options_have_human_labels_and_raw_values() -> None:
    workspace = build_single_settings_workspace(
        "Quality + Value",
        "Annual",
        {},
        runtime_options=RUNTIME_OPTIONS,
    )
    fields = {field["field_id"]: field for field in _fields(workspace)}
    quality = {option["value"]: option["label"] for option in fields["quality_factors"]["options"]}
    value = {option["value"]: option["label"] for option in fields["value_factors"]["options"]}

    assert quality["roe"] == "자기자본이익률 (ROE)"
    assert quality["net_margin"] == "순이익률"
    assert quality["net_debt_to_equity"] == "순부채 대비 자기자본"
    assert value["book_to_market"] == "장부가치 대비 시가"
    assert value["operating_income_yield"] == "영업이익 수익률"
    assert value["ev_ebit"] == "기업가치 대비 영업이익 (EV/EBIT)"
    assert set(quality) == set(RUNTIME_OPTIONS["quality_factor_options"])
    assert set(value) == set(RUNTIME_OPTIONS["value_factor_options"])


def test_human_factor_labels_do_not_change_projected_factor_keys() -> None:
    workspace = build_single_settings_workspace(
        "Quality + Value",
        "Annual",
        {
            "quality_factors": ["roe", "net_margin"],
            "value_factors": ["book_to_market", "operating_income_yield"],
        },
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert payload["quality_factors"] == ["roe", "net_margin"]
    assert payload["value_factors"] == ["book_to_market", "operating_income_yield"]
```

Update `test_react_multi_select_is_modifier_free_and_adaptive()` in `tests/test_backtest_refactor_boundaries.py` to require:

```python
self.assertIn('className="bt1-multi-select-option-label"', component)
self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", style)
self.assertIn("overflow-wrap: anywhere", style)
self.assertNotIn("repeat(auto-fit, minmax(140px, 1fr))", style)
compact_mobile = style.split("@media (max-width: 520px)", 1)[1]
self.assertIn(".bt1-multi-select-compact", compact_mobile)
self.assertIn("grid-template-columns: minmax(0, 1fr)", compact_mobile)
```

- [x] **Step 2: Run RED for schema and visual contract**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py::test_strict_factor_options_have_human_labels_and_raw_values \
  tests/test_backtest_single_settings_workspace.py::test_human_factor_labels_do_not_change_projected_factor_keys \
  tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_react_multi_select_is_modifier_free_and_adaptive -q
```

Expected: label assertions and new CSS/component tokens FAIL while raw payload projection already remains compatible.

- [x] **Step 3: Add the complete Python factor label map**

Add to `app/services/backtest_single_settings_workspace.py` near `_VARIANT_LABELS`:

```python
_FACTOR_OPTION_LABELS = {
    "roe": "자기자본이익률 (ROE)",
    "roa": "총자산이익률 (ROA)",
    "net_margin": "순이익률",
    "asset_turnover": "자산회전율",
    "current_ratio": "유동비율",
    "cash_ratio": "현금비율",
    "operating_margin": "영업이익률",
    "interest_coverage": "이자보상배율",
    "ocf_margin": "영업현금흐름률",
    "fcf_margin": "잉여현금흐름률",
    "net_debt_to_equity": "순부채 대비 자기자본",
    "debt_to_assets": "총자산 대비 부채",
    "debt_ratio": "부채비율",
    "gross_margin": "매출총이익률",
    "book_to_market": "장부가치 대비 시가",
    "earnings_yield": "이익수익률",
    "sales_yield": "매출수익률",
    "ocf_yield": "영업현금흐름 수익률",
    "fcf_yield": "잉여현금흐름 수익률",
    "operating_income_yield": "영업이익 수익률",
    "liquidation_value": "청산가치",
    "per": "주가수익비율 (PER)",
    "pbr": "주가순자산비율 (PBR)",
    "psr": "주가매출비율 (PSR)",
    "pcr": "주가현금흐름비율 (PCR)",
    "pfcr": "주가잉여현금흐름비율 (PFCR)",
    "ev_ebit": "기업가치 대비 영업이익 (EV/EBIT)",
    "por": "영업이익 대비 주가 (POR)",
}


def factor_option_label(value: str) -> str:
    """Return a user label while keeping the calculation key unchanged."""

    normalized = str(value).strip()
    return _FACTOR_OPTION_LABELS.get(
        normalized,
        normalized.replace("_", " ").title(),
    )
```

Change both factor option projections in `_strict_factor_field()`:

```python
options=[_option(value, factor_option_label(value)) for value in options],
```

Export `factor_option_label` in `__all__` only if tests import it directly; otherwise keep it module-owned.

- [x] **Step 4: Render labels in an explicit wrapping element**

In both compact and search result buttons in `BacktestAnalysisDecisionWorkspace.tsx`, replace the direct text node:

```tsx
<span aria-hidden="true">{selected ? "✓" : ""}</span>
<span className="bt1-multi-select-option-label">{option.label}</span>
```

In `style.css`, use a stable two-column layout and wrapping:

```css
.bt1-multi-select-compact {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.bt1-multi-select-option-label {
  min-width: 0;
  overflow-wrap: anywhere;
  line-height: 1.35;
}

@media (max-width: 520px) {
  .bt1-multi-select-compact {
    grid-template-columns: minmax(0, 1fr);
  }
}
```

Keep the outer settings section responsive grid unchanged; this only changes factor option cards.

- [x] **Step 5: Run GREEN, production build, and payload regression**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py \
  tests/test_backtest_refactor_boundaries.py -q
cd app/web/components/backtest_analysis_decision_workspace/frontend
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
```

Expected: both suites PASS and Vite production build exits 0. Build output under the tracked component build is included only when changed by the production build; `node_modules` is never staged.

- [x] **Step 6: Commit the factor presentation unit**

```bash
git add \
  app/services/backtest_single_settings_workspace.py \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx \
  app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css \
  app/web/components/backtest_analysis_decision_workspace/frontend/build \
  tests/test_backtest_single_settings_workspace.py \
  tests/test_backtest_refactor_boundaries.py
git diff --cached --check
git commit -m "Backtest Analysis 팩터 지표 표시 개선"
```

### Task 37: Reference-Only Lifecycle And Legacy Streamlit Cleanup

**Files:**
- Modify: `app/services/backtest_analysis_result_workspace.py`
- Modify: `app/web/backtest_analysis_result_workspace.py`
- Modify: `app/web/backtest_analysis_result_workspace_panel.py`
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `app/web/backtest_result_display.py`
- Modify: `app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts`
- Modify: `app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx`
- Test: `tests/test_backtest_analysis_result_workspace.py`
- Test: `tests/test_backtest_refactor_boundaries.py`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: fingerprint mismatch, `backtest_last_result_requires_rerun`, optional `backtest_last_result_refresh_result`, rerun error.
- Produces: lifecycle `reference_reason: str | None`, `reference_message: str`, one React/fallback lifecycle strip, no `_render_backtest_rerun_required_notice()` or Streamlit reset notice.

- [x] **Step 1: Write RED lifecycle reason tests**

Add to `tests/test_backtest_analysis_result_workspace.py`:

```python
def test_reference_only_lifecycle_explains_settings_price_and_failure_reasons() -> None:
    settings = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="new",
        result_configuration_fingerprint="old",
        result_requires_rerun=True,
        is_running=False,
        last_error=None,
        last_error_kind=None,
    )
    price = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        result_requires_rerun=True,
        is_running=False,
        last_error=None,
        last_error_kind=None,
        reference_reason="price_refresh",
    )
    failed = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="new",
        result_configuration_fingerprint="old",
        result_requires_rerun=True,
        is_running=False,
        last_error="provider timeout",
        last_error_kind="data",
    )

    assert settings["reference_reason"] == "settings_changed"
    assert settings["reference_message"] == "현재 설정으로 다시 실행하면 Level2 인계를 다시 확인할 수 있습니다."
    assert price["display_label"] == "가격 갱신 전 결과 · 참고용"
    assert price["reference_reason"] == "price_refresh"
    assert failed["reference_reason"] == "rerun_failed"
    assert failed["reference_message"] == "재실행에 실패해 마지막 성공 결과를 참고용으로 유지합니다."
```

Add a boundary test to `tests/test_backtest_refactor_boundaries.py`:

```python
def test_single_result_route_has_no_legacy_rerun_notice_or_raw_refresh_table(self) -> None:
    strategy = (PROJECT_ROOT / "app/web/backtest_single_strategy.py").read_text()
    result_display = (PROJECT_ROOT / "app/web/backtest_result_display.py").read_text()
    result_component = (
        PROJECT_ROOT
        / "app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx"
    ).read_text()

    assert "backtest_last_result_reset_notice" not in strategy
    assert "_render_backtest_rerun_required_notice" not in result_display
    assert '"Refresh Message"' not in result_display
    assert "reference_message" in result_component
```

Replace the legacy expectation in `test_price_refresh_preserves_stale_result_and_blocks_handoff_until_rerun()`:

```python
self.assertNotIn("_render_backtest_rerun_required_notice", last_run_body)
self.assertIn("backtest_last_result_refresh_result", result_display_source)
self.assertIn("render_backtest_analysis_result_workspace", last_run_body)
self.assertNotIn("Refresh Message", last_run_body)
```

- [x] **Step 2: Run RED and verify missing reason plus legacy tokens**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py::test_reference_only_lifecycle_explains_settings_price_and_failure_reasons \
  tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_single_result_route_has_no_legacy_rerun_notice_or_raw_refresh_table \
  tests/test_service_contracts.py::BacktestRuntimeContractTests::test_price_refresh_preserves_stale_result_and_blocks_handoff_until_rerun -q
```

Expected: lifecycle keys are missing and legacy notice/table assertions fail.

- [x] **Step 3: Extend the pure lifecycle contract**

Add `reference_reason: str | None = None` to the end of `build_result_lifecycle()` and `build_backtest_analysis_result_workspace()` keyword signatures. In `build_result_lifecycle()` resolve reason/message after `state`:

```python
resolved_reference_reason: str | None = None
if state == "error_with_reference":
    resolved_reference_reason = "rerun_failed"
elif state in {"stale", "running_with_reference"}:
    resolved_reference_reason = reference_reason or "settings_changed"

reference_messages = {
    "settings_changed": "현재 설정으로 다시 실행하면 Level2 인계를 다시 확인할 수 있습니다.",
    "price_refresh": "최신 가격 기준으로 다시 실행하면 성과와 Level2 인계 상태가 갱신됩니다.",
    "rerun_failed": "재실행에 실패해 마지막 성공 결과를 참고용으로 유지합니다.",
}
if resolved_reference_reason == "price_refresh" and state == "stale":
    display_labels[state] = "가격 갱신 전 결과 · 참고용"
```

Return these additive keys:

```python
"reference_reason": resolved_reference_reason,
"reference_message": reference_messages.get(resolved_reference_reason, ""),
```

Pass `reference_reason` from `build_backtest_analysis_result_workspace()` into `build_result_lifecycle()`.

- [x] **Step 4: Adapt Streamlit state without exposing refresh job rows**

In `build_current_backtest_analysis_result_workspace()` read the refresh result only to classify the lifecycle:

```python
refresh_result = st.session_state.get("backtest_last_result_refresh_result")
reference_reason = (
    "price_refresh"
    if result_requires_rerun and isinstance(refresh_result, Mapping)
    else None
)
```

Use `reference_reason = None` for Portfolio Mix and pass it to `build_backtest_analysis_result_workspace()`.

In `app/web/backtest_single_strategy.py`:

- keep setting `backtest_last_result_requires_rerun = True` and clearing stale refresh identity on strategy change;
- remove `backtest_last_result_reset_notice` assignment;
- remove the `reset_notice` `st.info()` block between the settings editor and `_render_last_run()`.

In `app/web/backtest_result_display.py`:

- delete `_render_backtest_rerun_required_notice()` completely;
- delete its conditional call from `_render_last_run()`;
- keep `backtest_last_result_refresh_result` and `backtest_last_result_requires_rerun` mutations because the new read model consumes them;
- do not render the old warning or `Strategy / Refresh Message / Saved Rows / Target End / Collection Start / Tickers` DataFrame.

- [x] **Step 5: Render one lifecycle strip in React and fallback**

Extend lifecycle in `frontend/src/types.ts`:

```ts
reference_reason: string | null
reference_message: string
```

In `ResultHeader()` render the Python message below the label:

```tsx
{workspace.lifecycle.reference_message && (
  <small className="bt1r-reference-message">
    {workspace.lifecycle.reference_message}
  </small>
)}
{workspace.lifecycle.error && <small>{workspace.lifecycle.error.message}</small>}
```

In `render_backtest_analysis_result_workspace_fallback()` append the same message to the lifecycle caption or a single `st.caption`; do not introduce a warning/table.

- [x] **Step 6: Run GREEN, React build, and focused lifecycle regression**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_analysis_result_workspace.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py::BacktestRuntimeContractTests::test_price_refresh_preserves_stale_result_and_blocks_handoff_until_rerun -q
cd app/web/components/backtest_analysis_result_workspace/frontend
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
```

Expected: focused suites PASS, old result remains visible/stale, handoff remains blocked, React production build exits 0.

- [x] **Step 7: Commit the lifecycle cleanup unit**

```bash
git add \
  app/services/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_result_workspace_panel.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_result_display.py \
  app/web/components/backtest_analysis_result_workspace/frontend/src \
  app/web/components/backtest_analysis_result_workspace/frontend/build \
  tests/test_backtest_analysis_result_workspace.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py
git diff --cached --check
git commit -m "Backtest Analysis 참고 결과 안내 통합"
```

### Task 38: Runtime Browser QA, Verification, Docs, And 12차 Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate, never stage: `backtest-analysis-level1-factor-presentation-desktop-qa.png`
- Generate, never stage: `backtest-analysis-level1-factor-presentation-760-qa.png`

**Interfaces:**
- Consumes: Task 35~37 current selection, factor label, responsive UI and stale lifecycle contracts.
- Produces: actual Browser evidence, fresh verification results, canonical finance docs, protected-path audit and closeout commit.

- [ ] **Step 1: Run desktop Browser QA on the requested reproduction**

At the current Backtest Analysis route:

1. run or load GTAA so a successful GTAA result exists;
2. select `Quality + Value` and Annual/Strict Annual settings;
3. confirm `목적과 핵심 설정` has no GTAA `strategy_key`, `timeframe`, `option`, promotion summary;
4. confirm the previous GTAA result remains below as `이전 설정 결과 · 참고용` and Level2 handoff is disabled;
5. confirm there is no Streamlit blue reset notice, yellow refresh notice, or raw refresh DataFrame between settings and result;
6. inspect Quality and Value factor lists and confirm Korean meaning + standard abbreviation labels, unchanged default selections, two-column wrapping and no clipping;
7. rerun Quality + Value and confirm the result atomically becomes `현재 설정 결과`.

Capture the desktop screenshot as a local untracked artifact only.

- [ ] **Step 2: Run 760px Browser QA**

Set viewport width to 760px and confirm:

- Quality / Value sections stack without outer horizontal overflow;
- each factor option grid remains two columns and labels wrap inside the card;
- lifecycle strip stays inside the result header;
- `document.documentElement.scrollWidth === clientWidth` for app and component iframe;
- ResizeObserver updates component height after advanced disclosure and factor selection;
- no browser console application error.

Capture the 760px screenshot without staging it.

- [x] **Step 3: Use verification-before-completion for fresh automated checks**

Run:

```bash
uv run --with pytest python -m pytest \
  tests/test_backtest_single_settings_workspace.py \
  tests/test_backtest_analysis_decision_workspace.py \
  tests/test_backtest_analysis_result_workspace.py \
  tests/test_backtest_refactor_boundaries.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -q --tb=short
cd app/web/components/backtest_analysis_decision_workspace/frontend && npm run build
cd ../../backtest_analysis_result_workspace/frontend && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
.venv/bin/python -m py_compile \
  app/services/backtest_single_settings_workspace.py \
  app/services/backtest_analysis_decision_workspace.py \
  app/services/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_workspace.py \
  app/web/backtest_analysis_result_workspace.py \
  app/web/backtest_analysis_result_workspace_panel.py \
  app/web/backtest_single_strategy.py \
  app/web/backtest_result_display.py \
  app/web/components/backtest_analysis_decision_workspace/component.py \
  app/web/components/backtest_analysis_result_workspace/component.py
git diff --check
```

Expected: focused tests pass; full `test_service_contracts.py` matches or improves the recorded repository baseline of 821 passed / 12 failed; both React builds, py_compile, and diff-check exit 0. Record exact fresh counts and do not describe baseline failures as new passes.

- [x] **Step 4: Apply finance-doc-sync and update active/root handoff logs**

Document:

- current selection catalog/settings versus previous result payload ownership;
- Single Strategy raw configuration summary suppression;
- factor raw value/user label split and responsive grid;
- one reference-only lifecycle strip and removed Streamlit reset/refresh table;
- unchanged runner payload, result preservation, Level2 handoff block and protected artifacts.

Record detailed commands/results in `RUNS.md`, decisions in `NOTES.md`, remaining gaps in `RISKS.md`, completion in `STATUS.md`, and only 3~5 line handoffs in root logs.

- [x] **Step 5: Audit protected paths and commit closeout**

```bash
git diff --check
git add \
  .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md \
  .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
if git diff --cached --name-only | rg -q \
  'registries/|run_history/|saved/|\.superpowers/|\.png$|run_artifacts/'; then
  exit 1
fi
git commit -m "Backtest Analysis 현재 선택과 팩터 표시 QA 동기화"
```

## 12차 Completion Report Contract

- 전체 roadmap 1~12차 완료 상태와 남은 차수;
- 12차 design / plan / current-selection / factor-label / lifecycle / closeout 한국어 commit 목록;
- focused settings / decision / result / boundary와 full service exact test counts;
- two React production builds / target py_compile / `git diff --check` 결과;
- desktop / 760px Browser QA 범위와 screenshot absolute links;
- registry / run history / saved / `.superpowers/` / screenshot 보호 감사;
- 남은 위험과 다음에 이어서 볼 active task 위치.

## 13차 Corrective Plan: Backtest Workflow Top Shell Redesign

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 초기 Streamlit 제목·중복 설명·red underline pills를 제거하고, Python-owned 3단계 계약을 표시하는 A안 React workflow top shell로 교체한다.

**Architecture:** 새 pure service가 Level1~3의 고정 순서, 사용자 label, 단계 책임과 active state를 JSON-ready read model로 만든다. Python adapter가 기존 route request helper를 통해 validated `select_stage` intent만 처리하고 React / Python fallback은 같은 read model을 렌더링한다. `backtest_page.py`는 shell과 기존 workspace dispatcher만 조합하며 Level 내부 Gate와 persistence는 변경하지 않는다.

**Tech Stack:** Python 3.11+, Streamlit session state / components v1, React 18, TypeScript 5.6, Vite 5, `streamlit-component-lib`, unittest / pytest.

### 13차 Global Constraints

- current linked worktree `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev`와 branch `codex/backtest-dev`를 그대로 사용한다.
- 별도 task, branch, worktree를 만들지 않는다.
- Python이 stage catalog, active state, intent allow-list와 route request를 소유한다.
- React는 presentation, focus/hover/selected state와 `select_stage` intent만 소유한다.
- top shell은 Level1/2/3의 Gate, blocker/count, eligibility, registry status를 계산하지 않는다.
- 기존 `BACKTEST_STAGE_OPTIONS`, legacy route normalization과 Level workspace renderer를 유지한다.
- primary route에서는 legacy `st.title("Backtest")`, obsolete caption, 별도 `후보 선정 흐름`, `st.pills`와 red active CSS를 제거한다.
- desktop hero는 2열 / rail 3열, 760px hero는 1열 / rail 3열, 520px 이하는 rail 1열이다.
- component/fallback은 같은 read model 의미를 사용하고 keyboard button, `aria-current="step"`, reduced motion과 ResizeObserver를 지원한다.
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`, `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, `.aiworkspace/note/finance/saved/*.jsonl`, `.superpowers/`, generated screenshot / run artifact를 stage하거나 commit하지 않는다.

### 13차 File Ownership Map

**New files**

- `app/services/backtest_workflow_shell.py`: 3단계 catalog, active-stage normalization, read model과 intent resolution.
- `tests/test_backtest_workflow_shell.py`: pure stage / active / invalid / duplicate intent contract.
- `app/web/backtest_workflow_shell.py`: session adapter, route request, component/fallback mount.
- `app/web/backtest_workflow_shell_panel.py`: same-read-model Streamlit fallback.
- `app/web/components/backtest_workflow_shell/`: Python component wrapper와 React source/build.

**Narrow existing changes**

- `app/web/backtest_page.py`: native pills를 shell renderer로 교체하고 기존 stage dispatch 유지.
- `app/web/streamlit_app.py`: legacy Backtest title과 obsolete caption 제거.
- `tests/test_backtest_refactor_boundaries.py`: React ownership / responsive / accessibility source boundary.
- `tests/test_service_contracts.py`: primary route가 새 shell을 사용하고 legacy selector를 제거했는지 검증.
- active task / canonical finance docs / root handoff logs: QA와 최종 상태 동기화.

---

### Task 39: Pure Workflow Shell Read Model And Intent Truth

**Files:**
- Create: `app/services/backtest_workflow_shell.py`
- Create: `tests/test_backtest_workflow_shell.py`

**Interfaces:**
- Consumes: `BACKTEST_STAGE_ANALYSIS`, `BACKTEST_STAGE_PRACTICAL_VALIDATION`, `BACKTEST_STAGE_FINAL_REVIEW`, `BACKTEST_STAGE_OPTIONS`.
- Produces: `build_backtest_workflow_shell(active_stage: str | None) -> dict[str, Any]`.
- Produces: `resolve_backtest_workflow_shell_intent(intent: Mapping[str, Any] | None, *, active_stage: str | None, consumed_nonce: str | None) -> dict[str, Any]`.

- [x] **Step 1: Write the failing pure-contract tests**

```python
from app.services.backtest_workflow_shell import (
    build_backtest_workflow_shell,
    resolve_backtest_workflow_shell_intent,
)
from app.web.backtest_workflow_routes import (
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_FINAL_REVIEW,
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
)


def test_workflow_shell_projects_three_stages_once_in_route_order() -> None:
    shell = build_backtest_workflow_shell(BACKTEST_STAGE_PRACTICAL_VALIDATION)
    assert [row["stage_key"] for row in shell["stages"]] == [
        BACKTEST_STAGE_ANALYSIS,
        BACKTEST_STAGE_PRACTICAL_VALIDATION,
        BACKTEST_STAGE_FINAL_REVIEW,
    ]
    assert sum(bool(row["is_active"]) for row in shell["stages"]) == 1
    assert shell["active_stage_index"] == 1
    assert shell["active_stage_context"]["title"] == "실전 검증"
    assert "최신 데이터" in shell["active_stage_context"]["responsibility"]


def test_workflow_shell_normalizes_unknown_stage_to_level1() -> None:
    shell = build_backtest_workflow_shell("unknown")
    assert shell["active_stage"] == BACKTEST_STAGE_ANALYSIS
    assert shell["active_stage_context"]["level_label"] == "LEVEL 1"


def test_workflow_shell_accepts_only_new_allowed_noncurrent_intent() -> None:
    accepted = resolve_backtest_workflow_shell_intent(
        {
            "type": "select_stage",
            "stage_key": BACKTEST_STAGE_FINAL_REVIEW,
            "nonce": "intent-1",
        },
        active_stage=BACKTEST_STAGE_ANALYSIS,
        consumed_nonce=None,
    )
    duplicate = resolve_backtest_workflow_shell_intent(
        {
            "type": "select_stage",
            "stage_key": BACKTEST_STAGE_FINAL_REVIEW,
            "nonce": "intent-1",
        },
        active_stage=BACKTEST_STAGE_ANALYSIS,
        consumed_nonce="intent-1",
    )
    invalid = resolve_backtest_workflow_shell_intent(
        {"type": "select_stage", "stage_key": "unknown", "nonce": "intent-2"},
        active_stage=BACKTEST_STAGE_ANALYSIS,
        consumed_nonce=None,
    )
    current = resolve_backtest_workflow_shell_intent(
        {
            "type": "select_stage",
            "stage_key": BACKTEST_STAGE_ANALYSIS,
            "nonce": "intent-3",
        },
        active_stage=BACKTEST_STAGE_ANALYSIS,
        consumed_nonce=None,
    )
    assert accepted == {
        "accepted": True,
        "stage_key": BACKTEST_STAGE_FINAL_REVIEW,
        "nonce": "intent-1",
    }
    assert duplicate["accepted"] is False
    assert invalid["accepted"] is False
    assert current["accepted"] is False
```

- [x] **Step 2: Run RED and confirm the missing-service failure**

Run: `.venv/bin/python -m pytest tests/test_backtest_workflow_shell.py -q`

Expected: FAIL during collection with `ModuleNotFoundError: No module named 'app.services.backtest_workflow_shell'`.

- [x] **Step 3: Implement the minimal Python-owned stage and intent contract**

```python
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.web.backtest_workflow_routes import (
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_FINAL_REVIEW,
    BACKTEST_STAGE_OPTIONS,
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
)


WORKFLOW_STAGE_PRESENTATION = (
    {
        "stage_key": BACKTEST_STAGE_ANALYSIS,
        "level_label": "LEVEL 1",
        "title": "후보 분석",
        "english_title": "Backtest Analysis",
        "responsibility": "전략을 실행하고 비교해 실전 검증 후보를 준비합니다.",
    },
    {
        "stage_key": BACKTEST_STAGE_PRACTICAL_VALIDATION,
        "level_label": "LEVEL 2",
        "title": "실전 검증",
        "english_title": "Practical Validation",
        "responsibility": "최신 데이터로 검증하고 해결할 일과 넘길 판단을 구분합니다.",
    },
    {
        "stage_key": BACKTEST_STAGE_FINAL_REVIEW,
        "level_label": "LEVEL 3",
        "title": "최종 검토",
        "english_title": "Final Review",
        "responsibility": "검증된 한계와 Monitoring 이관 조건을 바탕으로 최종 판단합니다.",
    },
)


def _normalized_stage(active_stage: str | None) -> str:
    candidate = str(active_stage or "")
    return candidate if candidate in BACKTEST_STAGE_OPTIONS else BACKTEST_STAGE_ANALYSIS


def build_backtest_workflow_shell(active_stage: str | None) -> dict[str, Any]:
    normalized = _normalized_stage(active_stage)
    stages = [
        {**row, "is_active": row["stage_key"] == normalized}
        for row in WORKFLOW_STAGE_PRESENTATION
    ]
    active_index = next(index for index, row in enumerate(stages) if row["is_active"])
    return {
        "schema_version": "backtest-workflow-shell-v1",
        "headline": "후보를 만들고 검증해 최종 투자 판단까지 이어갑니다",
        "description": "각 단계에서 해야 할 일을 분리하고, 검증된 근거만 다음 판단으로 넘깁니다.",
        "active_stage": normalized,
        "active_stage_index": active_index,
        "active_stage_context": dict(stages[active_index]),
        "stages": stages,
    }


def resolve_backtest_workflow_shell_intent(
    intent: Mapping[str, Any] | None,
    *,
    active_stage: str | None,
    consumed_nonce: str | None,
) -> dict[str, Any]:
    payload = dict(intent or {})
    nonce = str(payload.get("nonce") or "")
    stage_key = str(payload.get("stage_key") or "")
    accepted = bool(
        payload.get("type") == "select_stage"
        and nonce
        and nonce != consumed_nonce
        and stage_key in BACKTEST_STAGE_OPTIONS
        and stage_key != _normalized_stage(active_stage)
    )
    return (
        {"accepted": True, "stage_key": stage_key, "nonce": nonce}
        if accepted
        else {"accepted": False}
    )
```

- [x] **Step 4: Run GREEN and focused route regression**

Run: `.venv/bin/python -m pytest tests/test_backtest_workflow_shell.py tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_backtest_state_exports_workflow_helpers -q`

Expected: all tests pass.

- [x] **Step 5: Commit the pure contract**

```bash
git add app/services/backtest_workflow_shell.py tests/test_backtest_workflow_shell.py
git commit -m "Backtest 상단 단계 계약 구현"
```

---

### Task 40: Python Adapter, Validated Route Intent, And Fallback

**Files:**
- Create: `app/web/backtest_workflow_shell.py`
- Create: `app/web/backtest_workflow_shell_panel.py`
- Create: `app/web/components/backtest_workflow_shell/__init__.py`
- Create: `app/web/components/backtest_workflow_shell/component.py`
- Modify: `tests/test_backtest_workflow_shell.py`

**Interfaces:**
- Consumes: `build_backtest_workflow_shell()`, `resolve_backtest_workflow_shell_intent()`, `request_backtest_panel()`.
- Produces: `apply_backtest_workflow_shell_intent(intent, *, session_state, request_handler) -> bool`.
- Produces: `render_backtest_workflow_shell() -> str`.
- Produces: `render_backtest_workflow_shell_fallback(shell) -> dict[str, Any] | None`.

- [x] **Step 1: Add failing adapter and fallback ownership tests**

```python
def test_adapter_requests_route_once_for_new_valid_intent() -> None:
    from app.web.backtest_workflow_shell import apply_backtest_workflow_shell_intent

    requested: list[str] = []
    session_state = {
        "backtest_active_panel": BACKTEST_STAGE_ANALYSIS,
        "backtest_workflow_shell_consumed_nonce": None,
    }
    accepted = apply_backtest_workflow_shell_intent(
        {
            "type": "select_stage",
            "stage_key": BACKTEST_STAGE_PRACTICAL_VALIDATION,
            "nonce": "route-1",
        },
        session_state=session_state,
        request_handler=requested.append,
    )
    repeated = apply_backtest_workflow_shell_intent(
        {
            "type": "select_stage",
            "stage_key": BACKTEST_STAGE_PRACTICAL_VALIDATION,
            "nonce": "route-1",
        },
        session_state=session_state,
        request_handler=requested.append,
    )
    assert accepted is True
    assert repeated is False
    assert requested == [BACKTEST_STAGE_PRACTICAL_VALIDATION]
    assert session_state["backtest_workflow_shell_consumed_nonce"] == "route-1"


def test_adapter_rejects_unknown_stage_without_route_request() -> None:
    from app.web.backtest_workflow_shell import apply_backtest_workflow_shell_intent

    requested: list[str] = []
    accepted = apply_backtest_workflow_shell_intent(
        {"type": "select_stage", "stage_key": "unknown", "nonce": "route-2"},
        session_state={"backtest_active_panel": BACKTEST_STAGE_ANALYSIS},
        request_handler=requested.append,
    )
    assert accepted is False
    assert requested == []
```

- [x] **Step 2: Run RED and confirm the missing-adapter failure**

Run: `.venv/bin/python -m pytest tests/test_backtest_workflow_shell.py -q`

Expected: existing pure tests pass and new tests fail with `ModuleNotFoundError: No module named 'app.web.backtest_workflow_shell'`.

- [x] **Step 3: Implement the adapter and same-read-model fallback**

```python
def apply_backtest_workflow_shell_intent(
    intent: dict[str, Any] | None,
    *,
    session_state: MutableMapping[str, Any],
    request_handler: Callable[[str], None],
) -> bool:
    resolution = resolve_backtest_workflow_shell_intent(
        intent,
        active_stage=str(session_state.get("backtest_active_panel") or ""),
        consumed_nonce=str(session_state.get("backtest_workflow_shell_consumed_nonce") or "") or None,
    )
    if not resolution.get("accepted"):
        return False
    request_handler(str(resolution["stage_key"]))
    session_state["backtest_workflow_shell_consumed_nonce"] = str(resolution["nonce"])
    return True
```

`render_backtest_workflow_shell()`은 current session으로 read model을 만들고 component가 있으면
`render_backtest_workflow_shell_component(..., on_change=...)`, 없으면
`render_backtest_workflow_shell_fallback()`을 호출한다. component callback은 state key의 intent를
`apply_backtest_workflow_shell_intent()`로 처리하고 기존 `request_backtest_panel()`만 호출한다.
정상 렌더 경로는 normalized `active_stage`를 반환하며 accepted fallback intent는 app rerun을 요청한다.

fallback은 `shell["headline"]`, `active_stage_context["responsibility"]`와 `stages`를 사용해
container / columns / buttons를 렌더링하고 다음 intent만 반환한다.

```python
{
    "type": "select_stage",
    "stage_key": stage["stage_key"],
    "nonce": uuid4().hex,
}
```

component wrapper는 `_FRONTEND_BUILD_DIR.exists()`일 때만 v1 component를 declare하고 `shell`, `key`,
`on_change`를 넘긴다. build가 아직 없으면 `is_backtest_workflow_shell_available()`은 `False`다.

- [x] **Step 4: Run GREEN and Python compile**

Run: `.venv/bin/python -m pytest tests/test_backtest_workflow_shell.py -q`

Run: `.venv/bin/python -m py_compile app/services/backtest_workflow_shell.py app/web/backtest_workflow_shell.py app/web/backtest_workflow_shell_panel.py app/web/components/backtest_workflow_shell/component.py`

Expected: all tests pass and compile exits 0.

- [x] **Step 5: Commit the Python adapter/fallback**

```bash
git add tests/test_backtest_workflow_shell.py app/web/backtest_workflow_shell.py app/web/backtest_workflow_shell_panel.py app/web/components/backtest_workflow_shell/__init__.py app/web/components/backtest_workflow_shell/component.py
git commit -m "Backtest 상단 단계 이동 어댑터 구현"
```

---

### Task 41: React Decision Header And Stage Rail

**Files:**
- Create: `app/web/components/backtest_workflow_shell/frontend/index.html`
- Create: `app/web/components/backtest_workflow_shell/frontend/package.json`
- Create: `app/web/components/backtest_workflow_shell/frontend/package-lock.json`
- Create: `app/web/components/backtest_workflow_shell/frontend/tsconfig.json`
- Create: `app/web/components/backtest_workflow_shell/frontend/vite.config.ts`
- Create: `app/web/components/backtest_workflow_shell/frontend/src/types.ts`
- Create: `app/web/components/backtest_workflow_shell/frontend/src/BacktestWorkflowShell.tsx`
- Create: `app/web/components/backtest_workflow_shell/frontend/src/index.tsx`
- Create: `app/web/components/backtest_workflow_shell/frontend/src/style.css`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: Python `shell` projection from Task 39.
- Produces: Streamlit component intent `{type: "select_stage", stage_key: string, nonce: string}`.

- [x] **Step 1: Add failing React source-boundary tests**

```python
def test_backtest_workflow_shell_react_is_intent_only_and_accessible(self) -> None:
    component = (
        PROJECT_ROOT
        / "app/web/components/backtest_workflow_shell/frontend/src/BacktestWorkflowShell.tsx"
    ).read_text()
    index = (
        PROJECT_ROOT
        / "app/web/components/backtest_workflow_shell/frontend/src/index.tsx"
    ).read_text()
    self.assertIn('type: "select_stage"', component)
    self.assertIn('aria-current={stage.is_active ? "step" : undefined}', component)
    self.assertIn("Streamlit.setComponentValue", component)
    self.assertNotIn("eligibility", component)
    self.assertNotIn("blocker", component)
    self.assertIn("ResizeObserver", index)
    self.assertIn("Streamlit.setFrameHeight", index)


def test_backtest_workflow_shell_react_has_responsive_visual_contract(self) -> None:
    css = (
        PROJECT_ROOT / "app/web/components/backtest_workflow_shell/frontend/src/style.css"
    ).read_text()
    self.assertIn("grid-template-columns: minmax(0, 1.65fr) minmax(240px, 0.7fr)", css)
    self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr))", css)
    self.assertIn("@media (max-width: 760px)", css)
    self.assertIn("@media (max-width: 520px)", css)
    self.assertIn("overflow-x: hidden", css)
    self.assertIn("@media (prefers-reduced-motion: reduce)", css)
```

- [x] **Step 2: Run RED and confirm missing frontend source**

Run: `.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_backtest_workflow_shell_react_is_intent_only_and_accessible tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_backtest_workflow_shell_react_has_responsive_visual_contract -q`

Expected: both tests fail with `FileNotFoundError` for the new frontend source.

- [x] **Step 3: Implement the approved A visual and minimal intent component**

`types.ts` defines only the Python projection:

```typescript
export type WorkflowStage = {
  stage_key: string
  level_label: string
  title: string
  english_title: string
  responsibility: string
  is_active: boolean
}

export type WorkflowShell = {
  schema_version: string
  headline: string
  description: string
  active_stage: string
  active_stage_index: number
  active_stage_context: WorkflowStage
  stages: WorkflowStage[]
}
```

`BacktestWorkflowShell.tsx` renders kicker / headline / description, one current-stage context card and three
button stage cards. A non-current click emits exactly:

```typescript
Streamlit.setComponentValue({
  type: "select_stage",
  stage_key: stage.stage_key,
  nonce: `${Date.now()}-${Math.random()}`,
})
```

Each button uses `aria-current={stage.is_active ? "step" : undefined}` and disabled is not used so current
stage remains keyboard-readable; current click returns without emitting. User copy comes only from `shell`.

`index.tsx` uses `withStreamlitConnection`, observes `document.documentElement` with ResizeObserver and calls
`Streamlit.setFrameHeight()` on mount and content changes.

`style.css` follows the approved A mockup:

- shell gradient `#f7fbfe -> #edf5f8`, border `#d3e2eb`, radius 24px
- top grid `minmax(0, 1.65fr) minmax(240px, 0.7fr)`
- current context white translucent card
- rail `repeat(3, minmax(0, 1fr))`, current border/background/CURRENT marker
- all cards `min-width: 0`, `overflow-wrap: anywhere`
- 760px top grid 1 column while rail remains 3 columns
- 520px rail becomes 1 column
- body / root horizontal overflow hidden and reduced-motion transitions disabled

Use the existing React 18 / TypeScript / Vite / streamlit-component-lib versions. Run `npm install` in the new
frontend directory to generate `package-lock.json`; do not introduce a chart, icon or CSS dependency.

- [x] **Step 4: Run GREEN, TypeScript production build, and source tests**

Run: `npm install`

Working directory: `app/web/components/backtest_workflow_shell/frontend`

Run: `npm run build`

Working directory: `app/web/components/backtest_workflow_shell/frontend`

Run: `.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_backtest_workflow_shell_react_is_intent_only_and_accessible tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_backtest_workflow_shell_react_has_responsive_visual_contract -q`

Expected: Vite production build succeeds and both source-boundary tests pass.

- [x] **Step 5: Commit the React shell**

```bash
git add tests/test_backtest_refactor_boundaries.py app/web/components/backtest_workflow_shell
git commit -m "Backtest 상단 React 워크플로 셸 구현"
```

---

### Task 42: Primary Route Cutover And Legacy Top Removal

**Files:**
- Modify: `app/web/backtest_page.py`
- Modify: `app/web/streamlit_app.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `render_backtest_workflow_shell() -> str`.
- Preserves: existing Level1 / Level2 / Level3 renderer dispatch and legacy request normalization.

- [x] **Step 1: Replace the old selector test with failing primary-shell tests**

```python
def test_backtest_page_uses_react_workflow_shell_without_legacy_selector(self) -> None:
    source = Path("app/web/backtest_page.py").read_text(encoding="utf-8")
    self.assertIn("from app.web.backtest_workflow_shell import render_backtest_workflow_shell", source)
    self.assertIn("active_panel = render_backtest_workflow_shell()", source)
    self.assertNotIn("st.pills(", source)
    self.assertNotIn("stBaseButton-pillsActive", source)
    self.assertNotIn("#ff4b4b", source)
    self.assertNotIn("후보 선정 흐름", source)


def test_streamlit_backtest_entry_defers_identity_to_workflow_shell(self) -> None:
    source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")
    body = source.split("def _render_backtest_page() -> None:", 1)[1]
    body = body.split("\ndef ", 1)[0]
    self.assertEqual(body.count("render_backtest_tab()"), 1)
    self.assertNotIn('st.title("Backtest")', body)
    self.assertNotIn("Pre-Live", body)
    self.assertNotIn("Portfolio Proposal", body)
```

Update the Final Review wording source assertion to read `app/services/backtest_workflow_shell.py`, where the
top-level Final Review responsibility now lives, instead of expecting the old copy in `backtest_page.py`.

- [x] **Step 2: Run RED and confirm the legacy selector/title assertions fail**

Run: `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'backtest_page_uses_react_workflow_shell_without_legacy_selector or streamlit_backtest_entry_defers_identity_to_workflow_shell or final_review_top_summary_is_short_and_action_focused' -q`

Expected: the two new route tests fail because the old title/pills remain; the Final Review source assertion passes after its test ownership update.

- [x] **Step 3: Cut the primary route over to the new shell**

In `app/web/backtest_page.py`:

- remove `BACKTEST_WORKFLOW_STAGE_DISPLAY`, `_backtest_workflow_stage_label()`, `_backtest_workflow_nav_css()` and `_render_backtest_panel_selector()`
- remove unused `activate_backtest_workflow_panel` and `BACKTEST_WORKFLOW_PANEL_OPTIONS` imports
- import `render_backtest_workflow_shell`
- after `init_backtest_state()`, use `active_panel = render_backtest_workflow_shell()`
- keep the existing `if/elif` workspace dispatch unchanged
- remove the direct-run `st.title("Backtest")`

In `app/web/streamlit_app.py`, make `_render_backtest_page()` call only `render_backtest_tab()`.

- [x] **Step 4: Run GREEN and focused route/boundary regression**

Run: `.venv/bin/python -m pytest tests/test_backtest_workflow_shell.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -k 'workflow_shell or backtest_page or streamlit_backtest_entry or final_review_top_summary' -q`

Run: `.venv/bin/python -m py_compile app/web/backtest_page.py app/web/streamlit_app.py app/web/backtest_workflow_shell.py`

Expected: selected tests pass and compile exits 0.

- [x] **Step 5: Commit the primary route cutover**

```bash
git add app/web/backtest_page.py app/web/streamlit_app.py tests/test_service_contracts.py
git commit -m "Backtest 상단 진입부를 React 셸로 전환"
```

---

### Task 43: Runtime QA, Fresh Verification, Docs, And 13차 Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate but do not stage: `backtest-workflow-top-shell-desktop-qa.png`, `backtest-workflow-top-shell-760-qa.png`

**Interfaces:**
- Consumes: completed shell service, adapter, component and route cutover.
- Produces: fresh verification evidence, desktop/760 screenshots and durable documentation alignment.

- [x] **Step 1: Run fresh focused and broader Python verification**

Run: `.venv/bin/python -m pytest tests/test_backtest_workflow_shell.py tests/test_backtest_refactor_boundaries.py -q`

Run: `.venv/bin/python -m pytest tests/test_service_contracts.py -q`

Expected: shell/boundary tests pass. Compare full service failures against the documented pre-13차 baseline of Sentiment / Final Review / liquidity copy / Practical Validation failures; no new Backtest top-shell failure is allowed.

- [x] **Step 2: Run fresh frontend, compile, and diff checks**

Run: `npm run build`

Working directory: `app/web/components/backtest_workflow_shell/frontend`

Run: `.venv/bin/python -m py_compile app/services/backtest_workflow_shell.py app/web/backtest_workflow_shell.py app/web/backtest_workflow_shell_panel.py app/web/components/backtest_workflow_shell/component.py app/web/backtest_page.py app/web/streamlit_app.py`

Run: `git diff --check`

Expected: build and compile succeed; diff-check has no output.

- [x] **Step 3: Run desktop Browser QA on a fresh source/build pair**

Start or restart the Streamlit Backtest app from current source/build. At desktop width around 1440px verify:

1. legacy `Backtest` title/caption, `후보 선정 흐름`, red underline pills are absent
2. hero is 2 columns and stage rail is 3 columns
3. Level1 current card and Level1 workspace agree
4. clicking Level2 updates current card and opens Practical Validation
5. clicking Level3 updates current card and opens Final Review
6. returning Level1 restores Backtest Analysis without changing registry/saved data
7. no component console error and iframe height contains the entire shell

Save `backtest-workflow-top-shell-desktop-qa.png` as generated/untracked evidence.

- [x] **Step 4: Run 760px Browser QA**

At 760px viewport verify:

1. hero text and current-stage card are one column
2. stage rail remains 3 columns and Korean/English labels wrap without clipping
3. `document.documentElement.scrollWidth === document.documentElement.clientWidth`
4. component iframe `scrollWidth === clientWidth`
5. stage navigation and ResizeObserver height remain functional

Save `backtest-workflow-top-shell-760-qa.png` as generated/untracked evidence.

- [x] **Step 5: Apply finance-doc-sync and record closeout evidence**

Update canonical maps/flows with the page-level Python read model + React intent shell and remove durable references
to the old Streamlit pills entry. Record exact test counts, build modules/assets, compile/diff results, Browser QA
coverage, screenshot names, baseline failures and remaining accessibility/dependency risks in active task docs.
Keep root logs to a 3~5 line milestone/handoff summary.

- [x] **Step 6: Audit protected paths and commit closeout**

Run:

```bash
git status --short
git diff --cached --name-only
git diff --cached --check
```

Expected staged paths do not include registry JSONL, Run History, saved JSONL, `.superpowers/`, screenshots or run artifacts.

Commit:

```bash
git add .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md .aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717/STATUS.md .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717/NOTES.md .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717/RUNS.md .aiworkspace/note/finance/tasks/active/backtest-analysis-level1-decision-workspace-v1-20260717/RISKS.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "Backtest 상단 워크플로 셸 QA와 문서 동기화"
```

## 13차 Completion Report Contract

- Task 39~43 완료 상태와 각 한국어 commit hash
- fresh focused / full service test pass/fail counts와 baseline 비교
- React production build, target py_compile, diff-check 결과
- desktop / 760px Browser QA 범위와 generated screenshot 경로
- legacy title/caption/pills 제거와 Level1/2/3 route dispatch 확인
- protected registry / Run History / saved JSONL / `.superpowers/` / screenshot 미커밋 확인
- 남은 repository baseline, dependency audit와 keyboard manual QA 위험

## 14차 Corrective Plan: Stage-Local Legacy Title Removal

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Level2와 Level3의 중복 Streamlit stage title/caption을 제거해 Level1~3 모두 `공통 workflow shell -> active React hero -> body` 순서를 사용하게 한다.

**Architecture:** 기존 page-level workflow shell, Level별 React workspace와 Python route/Gate owner는 유지한다. `render_practical_validation_workspace()`와 `render_final_review_workspace()`의 presentation-only title pair만 제거하고 source boundary regression과 Browser QA로 중복 제거와 fallback 의미 보존을 확인한다.

**Tech Stack:** Python 3.12, Streamlit, React build artifact read-only reuse, unittest / pytest, in-app Browser QA.

### 14차 Global Constraints

- current worktree와 branch, active task를 그대로 사용하고 새 task/branch/worktree를 만들지 않는다.
- Level1, page-level workflow shell과 Level React hero source는 변경하지 않는다.
- route, Gate, replay, validation result, Final Review decision, registry와 persistence 계약을 변경하지 않는다.
- React unavailable fallback body를 삭제하거나 static stage title을 새로 추가하지 않는다.
- RED를 먼저 확인한 뒤 Level2/3 renderer의 중복 title/caption만 최소 제거한다.
- `.aiworkspace/note/finance/registries/`, `.aiworkspace/note/finance/run_history/`, `.aiworkspace/note/finance/saved/`, `.superpowers/`, generated screenshot/run artifact를 stage하거나 commit하지 않는다.

### 14차 File Ownership Map

**Narrow product changes**

- `app/web/backtest_practical_validation/page.py`: primary Level2 renderer의 legacy stage title/caption 제거.
- `app/web/backtest_final_review/page.py`: primary Level3 renderer의 legacy stage title/caption 제거.
- `tests/test_backtest_refactor_boundaries.py`: Level2/3 stage-local title 부재와 React hero 유지 source contract.

**Closeout-only changes**

- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`: 공통 shell과 Level hero title ownership 기록.
- active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`: RED/GREEN, QA, verification 기록.
- root handoff logs: 3~5줄 milestone / decision / follow-up만 기록.

---

### Task 44: Remove Duplicate Level2 And Level3 Stage Titles

**Files:**
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `app/web/backtest_final_review/page.py`

**Interfaces:**
- Consumes: existing page-level `render_backtest_workflow_shell()` and Level-specific React/fallback renderers.
- Produces: no new runtime interface; primary Level2/3 entry starts directly with the existing workspace component/fallback.

- [x] **Step 1: Write the failing title-ownership boundary test**

Add this method to `BacktestRefactorBoundaryTests`:

```python
def test_level2_and_level3_primary_routes_do_not_repeat_stage_titles(self) -> None:
    pv_source = (
        PROJECT_ROOT / "app/web/backtest_practical_validation/page.py"
    ).read_text(encoding="utf-8")
    final_source = (
        PROJECT_ROOT / "app/web/backtest_final_review/page.py"
    ).read_text(encoding="utf-8")
    pv_entry = pv_source.split(
        "def render_practical_validation_workspace() -> None:", 1
    )[1].split("sources = load_portfolio_selection_sources", 1)[0]
    final_entry = final_source.split(
        "def render_final_review_workspace() -> None:", 1
    )[1].split("current_rows = load_current_candidate_registry_latest", 1)[0]

    self.assertNotIn('st.markdown("### Practical Validation")', pv_entry)
    self.assertNotIn(
        "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?",
        pv_entry,
    )
    self.assertNotIn('st.markdown("### Final Review")', final_entry)
    self.assertNotIn(
        "이 포트폴리오를 실제 투자 검토 대상으로 계속 추적할 가치가 있는가?",
        final_entry,
    )

    pv_react = (
        PROJECT_ROOT
        / "app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx"
    ).read_text(encoding="utf-8")
    final_react = (
        PROJECT_ROOT
        / "app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx"
    ).read_text(encoding="utf-8")
    self.assertIn("Practical Validation Decision Workspace", pv_react)
    self.assertIn("Final Review Decision Workspace", final_react)
```

- [x] **Step 2: Run RED and confirm the duplicate-title failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_level2_and_level3_primary_routes_do_not_repeat_stage_titles -q
```

Expected: FAIL because Level2 and Level3 entry prefixes still contain the legacy Streamlit stage title/caption.

- [x] **Step 3: Remove only the two presentation-only title pairs**

In `render_practical_validation_workspace()` retain `render_pv_styles()` and start source loading immediately:

```python
def render_practical_validation_workspace() -> None:
    render_pv_styles()
    sources = load_portfolio_selection_sources(limit=100)
```

In `render_final_review_workspace()` start registry loading immediately:

```python
def render_final_review_workspace() -> None:
    current_rows = load_current_candidate_registry_latest()
```

Do not change the component/fallback selection, fragments, route request, candidate selection or persistence paths.

- [x] **Step 4: Run GREEN and focused regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py::BacktestRefactorBoundaryTests::test_level2_and_level3_primary_routes_do_not_repeat_stage_titles -q
.venv/bin/python -m pytest tests/test_backtest_workflow_shell.py tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m py_compile app/web/backtest_practical_validation/page.py app/web/backtest_final_review/page.py
git diff --check
```

Expected: targeted test and focused suite pass; compile/diff-check exit 0.

- [x] **Step 5: Commit the presentation cleanup**

```bash
git add tests/test_backtest_refactor_boundaries.py app/web/backtest_practical_validation/page.py app/web/backtest_final_review/page.py
git commit -m "Backtest 단계별 중복 타이틀 제거"
```

---

### Task 45: Browser QA, Fresh Verification, Docs, And 14차 Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate but do not stage: `backtest-stage-title-cleanup-desktop-qa.png`, `backtest-stage-title-cleanup-760-qa.png`

**Interfaces:**
- Consumes: completed title cleanup and existing source/build pair.
- Produces: desktop/760 Browser evidence, fresh regression evidence and durable title-ownership documentation.

- [x] **Step 1: Run desktop Browser QA from a fresh app process**

At approximately 1440px verify:

1. Level2 top shell is followed directly by `Practical Validation Decision Workspace` hero.
2. visible legacy `Practical Validation` title/caption above the React hero is absent.
3. Level3 top shell is followed directly by `Final Review Decision Workspace` hero.
4. visible legacy `Final Review` title/caption above the React hero is absent.
5. Level1 remains unchanged and stage navigation still opens the matching workspace.
6. application console error count is 0.

Save `backtest-stage-title-cleanup-desktop-qa.png` as generated/untracked evidence.

- [x] **Step 2: Run 760px Browser QA**

At 760x1000 verify Level2/3 have no duplicate title or artificial blank title gap, hero text is not clipped,
and both outer page and active component iframe satisfy `scrollWidth === clientWidth`.

Save `backtest-stage-title-cleanup-760-qa.png` as generated/untracked evidence.

- [x] **Step 3: Run fresh completion verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_workflow_shell.py tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q
.venv/bin/python -m py_compile app/web/backtest_practical_validation/page.py app/web/backtest_final_review/page.py
git diff --check
```

Expected: focused suite passes. Full service failures must match the documented Sentiment 1, Final Review 4,
liquidity copy 1, Practical Validation 6 baseline; no new stage-title failure is allowed.

- [x] **Step 4: Apply finance-doc-sync and record closeout**

Update `BACKTEST_UI_FLOW.md` so the durable reading order is `page workflow shell -> active Level React hero ->
body` and stage-local Streamlit title is not an active owner. Record exact tests, Browser viewport/overflow,
screenshots, baseline failures and remaining accessibility/dependency risks in task docs; keep root logs concise.

- [x] **Step 5: Audit protected paths and commit closeout**

Run:

```bash
git status --short
git diff --cached --name-only
git diff --cached --check
```

Explicitly stage only the canonical flow doc, active task docs and root logs. Staged paths must not include
registry, Run History, saved JSONL, `.superpowers/`, screenshots or run artifacts.

Commit:

```bash
git commit -m "Backtest 단계별 타이틀 정리 QA와 문서 동기화"
```

## 14차 Completion Report Contract

- Task 44~45 완료 상태와 한국어 commit hash
- RED failure와 GREEN focused/full verification counts
- target py_compile / diff-check 결과
- desktop / 760px Level2/3 title removal, route and overflow QA
- generated screenshot 경로
- protected artifacts 미커밋 확인
- baseline service failures와 남은 risk

---

## 15차 Corrective Plan: Portfolio Mix React One-Shell Completion

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Each task must complete RED, GREEN, focused verification and its Korean commit before the next task begins.

**Goal:** Portfolio Mix의 legacy Streamlit 구성·비중·saved replay·결과 surface를 하나의 Python-owned React four-step workspace로 교체하고, 현재 설정과 일치하는 실행 결과만 저장 또는 Level2로 인계한다.

**Architecture:** 새 pure service가 draft normalization, Single settings composition, validation, fingerprint, stale/result/action projection을 소유한다. 새 Python web adapter가 intent allow-list, session lifecycle, existing compare runner/weighted builder, saved setup과 Level2 source handler를 소유한다. React는 pure payload를 표시하고 intent만 반환하며, primary route는 새 workspace를 한 번만 mount한다.

**Tech Stack:** Python 3, Streamlit, Streamlit custom component, React 18, TypeScript, Vite, pytest, existing Backtest compare/weighted/persistence services.

### Global Constraints

- 현재 `codex/backtest-dev` branch와 active task를 계속 사용하며 새 task, branch, worktree를 만들지 않는다.
- strategy/factor/performance 계산, DB schema, Level2/Final Review route와 Gate 의미는 바꾸지 않는다.
- `app/services/backtest_single_settings_workspace.py`의 schema/preset/validation/payload projection을 component마다 재사용한다.
- React는 catalog grouping, validation, fingerprint, runner, Gate, persistence를 계산하거나 호출하지 않는다.
- legacy prototype row를 새 schema로 자동 migration하거나 보정하지 않는다.
- protected registry, Run History, saved JSONL, `.superpowers/`, screenshot/run artifact는 rewrite/delete/stage/commit하지 않는다.
- current draft가 바뀌거나 component 실행이 실패해도 마지막 성공 결과와 다른 component draft를 삭제하지 않는다.
- callable action이 0개이면 빈 action board를 렌더링하지 않는다.

### Task 46: Portfolio Mix Truth And Pure Read Model (15-1)

**Files:**
- Create: `app/services/backtest_portfolio_mix_workspace.py`
- Create: `tests/test_backtest_portfolio_mix_workspace.py`
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**

```python
PORTFOLIO_MIX_WORKSPACE_SCHEMA_VERSION = "backtest_portfolio_mix_workspace_v1"
PORTFOLIO_MIX_SAVED_SCHEMA_VERSION = "backtest_portfolio_mix_saved_v1"

class PortfolioMixValidationError(ValueError):
    errors: Mapping[str, str]

def normalize_portfolio_mix_draft(
    draft: Mapping[str, Any] | None,
    *,
    runtime_options: Mapping[str, Any] | None = None,
    today: date | None = None,
) -> dict[str, Any]: ...

def validate_portfolio_mix_draft(draft: Mapping[str, Any]) -> dict[str, str]: ...

def project_portfolio_mix_component_payloads(
    draft: Mapping[str, Any],
) -> list[dict[str, Any]]: ...

def build_portfolio_mix_fingerprint(draft: Mapping[str, Any]) -> str: ...

def build_portfolio_mix_workspace(
    *,
    draft: Mapping[str, Any] | None,
    saved_records: Sequence[Mapping[str, Any]] = (),
    component_states: Mapping[str, Mapping[str, Any]] | None = None,
    current_result: Mapping[str, Any] | None = None,
    last_result: Mapping[str, Any] | None = None,
    action_capabilities: Mapping[str, bool] | None = None,
    runtime_options: Mapping[str, Any] | None = None,
    today: date | None = None,
) -> dict[str, Any]: ...
```

Normalized draft contract:

```python
{
    "draft_id": "mix-draft-...",
    "source_saved_portfolio_id": None,
    "shared": {
        "start": "2016-01-01",
        "end": "2026-07-19",
        "timeframe": "1d",
        "option": "month_end",
        "date_policy": "intersection",
    },
    "components": [
        {
            "component_id": "component-1",
            "strategy_choice": "GTAA",
            "variant": None,
            "settings_values": {},
            "role": "core",
            "weight_percent": 50.0,
        }
    ],
}
```

- component ID는 draft가 제공하면 보존하고, 누락 시 position 기반 stable default를 만든다.
- fingerprint에는 `draft_id`와 saved row identity를 넣지 않고 shared values와 ordered effective component settings/role/weight만 canonical JSON으로 hash한다.
- concrete execution key는 strategy choice와 strict factor variant를 함께 정규화한다. 같은 concrete key 중복은 validation error다.
- role allow-list는 `core`, `growth`, `defense`, `satellite`; 사용자 label은 pure projection에서 제공한다.
- component 수는 2~4, weight는 각 0 초과, 합계는 tolerance `0.01` 안에서 100이어야 한다.
- saved shelf에는 `backtest_portfolio_mix_saved_v1` row만 투영하고 legacy row는 migration 없이 제외한다.
- result fingerprint가 current fingerprint와 다르면 `last_result`/`reference_result`로만 표시하고 current save/handoff action은 제공하지 않는다.

- [x] **Step 1: Write RED truth/read-model tests**

Add tests for:

1. 2~4 component constraint and stable missing component IDs.
2. duplicate concrete strategy/variant rejection.
3. role/weight/shared validation and exact 100% total.
4. Single settings preset composition and exact projected compare override for GTAA, Equal Weight and Quality + Value Strict Annual.
5. semantically equal drafts produce one fingerprint; effective setting/role/weight change produces a different fingerprint.
6. pre-run workspace has no verdict/result/action board.
7. stale result remains a reference and disables current save/handoff.
8. saved shelf accepts only the new schema and exposes no raw JSON or absolute path.
9. root validation issue is projected and counted once.

Run and confirm RED is caused by the missing service:

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q
```

- [x] **Step 2: Implement the pure service**

Compose existing Single settings functions instead of copying catalog or field rules:

```python
single_workspace = build_single_settings_workspace(
    strategy_choice=strategy_choice,
    variant=variant,
    values=settings_values,
    runtime_options=runtime_options,
    today=today,
)
field_errors = validate_single_settings_draft(single_workspace)
payload = project_single_settings_payload(single_workspace)
```

Normalize dates/numbers/arrays before fingerprinting. Deduplicate issues by stable `root_issue_id`, keep user-facing Korean labels separate from raw execution keys, and return JSON-serializable values only.

- [x] **Step 3: Run GREEN and regression**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'single_settings or portfolio_mix or weighted_portfolio or compare_execution'
.venv/bin/python -m py_compile app/services/backtest_portfolio_mix_workspace.py
git diff --check
```

Record exact counts. Any full-suite failure must be classified against the documented Sentiment/Final Review/liquidity/Practical Validation baseline; no new Portfolio Mix failure is allowed.

- [x] **Step 4: Commit the implementation unit**

Stage only the new service/test and active task records, audit staged paths, then commit:

```bash
git commit -m "Portfolio Mix 진실과 읽기 모델 구현"
```

### Task 47: Portfolio Mix React One-Shell And Intent Adapter (15-2)

**Files:**
- Create: `app/web/backtest_portfolio_mix_workspace.py`
- Create: `app/web/components/backtest_portfolio_mix_workspace/__init__.py`
- Create: `app/web/components/backtest_portfolio_mix_workspace/component.py`
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/package.json`
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/package-lock.json`
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/tsconfig.json`
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/vite.config.ts`
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/index.html`
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/main.tsx`
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/App.tsx`
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/styles.css`
- Modify: `tests/test_backtest_portfolio_mix_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Python adapter interfaces:**

```python
MIX_SESSION_KEYS = {
    "draft": "backtest_portfolio_mix_draft",
    "component_states": "backtest_portfolio_mix_component_states",
    "current_result": "backtest_portfolio_mix_current_result",
    "last_result": "backtest_portfolio_mix_last_result",
    "last_intent_id": "backtest_portfolio_mix_last_intent_id",
}

def build_initial_portfolio_mix_session_draft() -> dict[str, Any]: ...
def consume_portfolio_mix_intent(intent: Mapping[str, Any]) -> None: ...
def render_backtest_portfolio_mix_workspace_fallback(
    workspace: Mapping[str, Any],
) -> Mapping[str, Any] | None: ...
def render_backtest_portfolio_mix_workspace() -> None: ...
```

Validated intent allow-list:

```text
set_mode
add_component
remove_component
set_strategy
set_variant
apply_preset
set_component_field
set_shared_field
set_role
set_weight
restore_saved_mix
run_saved_mix
run_mix
save_mix
handoff_level2
```

The React event contract is `{event: {id, intent_id, payload}}`. Python rejects unknown intents, duplicate intent IDs, unknown component IDs, invalid strategy/variant/field/option values and actions not advertised by the current read model.

- [x] **Step 1: Write RED adapter and UI-boundary tests**

Add tests that require:

1. initial session draft uses 2 valid components and a 100% default allocation.
2. add/remove/role/weight/shared/settings intents update only the addressed draft region.
3. duplicate/unknown/replayed intent is ignored or rejected without mutating session state.
4. fallback consumes the same workspace read model and returns the same intent vocabulary.
5. React source contains four approved step headings, saved/new modes, component detail, role/weight, result and final action sections.
6. React source has no runner import, raw status classification, fingerprint/Gate calculation, persistence call, raw JSON or absolute path rendering.
7. component wrapper and Vite build directory follow existing Backtest component conventions including ResizeObserver height sync.

Run RED:

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py tests/test_backtest_refactor_boundaries.py -q -k 'portfolio_mix'
```

- [x] **Step 2: Implement Python intent adapter and fallback**

- Rebuild the workspace after every accepted intent from session state.
- Use service-provided strategy/variant/preset/field options as the only allow-lists.
- Preserve `current_result` when editing, but move it to reference/stale presentation through fingerprint mismatch.
- Do not wire runner/persistence actions in this task; unsupported action capabilities remain false so no empty action board appears.
- Python fallback exposes the same four steps and editing/actions that are currently callable.

- [x] **Step 3: Implement React four-step presentation**

Step layout:

1. `구성 전략과 공통 기준`: new/saved mode, 2~4 component cards, shared fields, preset-first and details disclosure.
2. `역할과 목표 비중`: role selector, percentage control, total and alignment guidance.
3. `Mix 실행과 해석`: no pre-run verdict; component state and current/stale result only when present.
4. `저장하고 Level2로 이동`: only service-advertised callable actions.

Use a two-column desktop component board, one column at 760px, no horizontal overflow, keyboard-focusable buttons/disclosures and `aria-selected`, `aria-expanded`, `aria-live` where state changes.

- [x] **Step 4: Run GREEN, production build and compile**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py tests/test_backtest_refactor_boundaries.py -q -k 'portfolio_mix'
npm run build --prefix app/web/components/backtest_portfolio_mix_workspace/frontend
.venv/bin/python -m py_compile app/web/backtest_portfolio_mix_workspace.py app/web/components/backtest_portfolio_mix_workspace/component.py
git diff --check
```

- [x] **Step 5: Commit the implementation unit**

Stage only adapter/component/tests/task records and commit:

```bash
git commit -m "Portfolio Mix React 원셸 UI 구현"
```

### Task 48: Runtime, Saved Mix, Level2 Handoff And Primary Cutover (15-3)

**Files:**
- Modify: `app/web/backtest_portfolio_mix_workspace.py`
- Modify: `app/web/backtest_analysis.py`
- Modify: `app/web/backtest_compare/page.py` only for helpers proven unreachable after cutover
- Modify: `app/services/backtest_portfolio_mix_workspace.py`
- Modify: `tests/test_backtest_portfolio_mix_workspace.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `tests/test_service_contracts.py` only where the public Mix contract changes
- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Runtime interfaces:**

```python
def execute_current_portfolio_mix(
    draft: Mapping[str, Any],
    *,
    run_component: Callable[..., Mapping[str, Any]],
) -> dict[str, Any]: ...

def save_current_portfolio_mix(
    workspace: Mapping[str, Any],
) -> dict[str, Any]: ...

def handoff_current_portfolio_mix(
    workspace: Mapping[str, Any],
) -> dict[str, Any]: ...
```

- Each component payload is projected/validated before any runner call.
- Components run through existing `backtest_compare_catalog.run_compare_strategy`; weighted result is built through `build_weighted_portfolio_bundle`.
- Runtime stores per-component pending/running/success/error state and top-level `run_result_id` plus current fingerprint.
- Run History append, saved setup write and Level2 candidate source write remain three distinct side effects.
- Save writes `backtest_portfolio_mix_saved_v1`; load/restore accepts only this schema.
- One component failure preserves successful bundles, current draft and previous successful weighted result; no partial weighted result is promoted current.
- Primary Mix route mounts only `render_backtest_portfolio_mix_workspace()` and no longer mounts `render_compare_portfolio_workspace()` or generic Mix `render_backtest_analysis_decision_surface()`.
- Legacy page helpers are deleted only after `rg` and boundary tests prove no production/test references. Compatibility helpers may remain unmounted when deletion would expand scope.

- [x] **Step 1: Write RED runtime/persistence/cutover tests**

Add tests for:

1. invalid draft never calls a component runner.
2. GTAA + Quality + Value Strict Annual + Equal Weight produces three component bundles and one weighted bundle with current fingerprint/run identity.
3. component failure preserves draft/previous result and reports the failing component only once.
4. settings edit marks result stale and disables save/handoff until rerun.
5. save and Level2 handoff are separately callable and a failure does not roll back the other state.
6. saved restore changes the draft without inventing a result; saved rerun executes the restored snapshot.
7. primary route source imports/mounts only the new Mix workspace and does not mount legacy form/raw replay/generic duplicate decision.
8. protected persistence modules are called through existing public helpers; tests use temp paths/mocks, never real JSONL.

Run RED:

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k 'portfolio_mix or weighted_portfolio or compare_execution'
```

- [x] **Step 2: Implement atomic component and weighted execution**

Project all component payloads first. Run components sequentially in Python, update status by stable component ID, and build the weighted bundle only after all component calls succeed. Preserve old current result as a reference until the new weighted build completes; replace current result atomically on success.

- [x] **Step 3: Implement saved setup and Level2 source actions**

- Save a reusable new-schema snapshot with normalized draft, roles, weights, fingerprint and user-facing summary.
- Restore snapshot into a fresh `draft_id` while preserving component IDs/settings.
- Handoff only a fresh current weighted result and retain `run_result_id`/fingerprint in the selection-source context.
- Expose action cards only when the corresponding Python handler is callable and the service Gate permits it.

- [x] **Step 4: Cut over the primary route and remove duplicate legacy mounts**

Change the Mix branch in `app/web/backtest_analysis.py` to:

```python
if mode == BACKTEST_ANALYSIS_MODE_COMPARE:
    render_backtest_portfolio_mix_workspace()
    return
```

Keep Single Strategy behavior unchanged. Confirm through source/boundary tests that legacy component form, saved replay page, raw JSON/path and generic decision mount are absent from the primary Mix DOM.

- [x] **Step 5: Run GREEN and focused regression**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'portfolio_mix or weighted_portfolio or compare_execution or single_settings'
npm run build --prefix app/web/components/backtest_portfolio_mix_workspace/frontend
.venv/bin/python -m py_compile app/services/backtest_portfolio_mix_workspace.py app/web/backtest_portfolio_mix_workspace.py app/web/backtest_analysis.py
git diff --check
```

- [x] **Step 6: Commit the implementation unit**

Stage only code/tests/task records and commit:

```bash
git commit -m "Portfolio Mix 실행 저장 인계 통합"
```

### Task 49: Browser QA, Fresh Verification, Docs And 15차 Closeout (15-4)

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate but do not stage: `backtest-portfolio-mix-one-shell-desktop-qa.png`, `backtest-portfolio-mix-one-shell-760-qa.png`

- [x] **Step 1: Start a fresh app and execute desktop Browser QA**

At approximately 1440px:

1. open Portfolio Mix and confirm one React four-step workspace with no legacy Streamlit form or duplicate generic Level1 verdict.
2. create GTAA + Quality + Value Strict Annual + Equal Weight components.
3. edit common period, presets/details, roles and weights; verify total/validation and stable cards.
4. execute; confirm component states, weighted result and current fingerprint lifecycle.
5. save the Mix; restore it in the same shell; edit it and verify old result becomes reference/stale.
6. rerun and confirm save and Level2 actions become available only for the new fresh result.
7. confirm raw JSON, absolute save path, internal callable/status table and empty action board are absent.
8. confirm browser console error count is 0.

Save `backtest-portfolio-mix-one-shell-desktop-qa.png` as generated/untracked evidence. Any saved/run/registry rows created by QA remain protected/untracked and must not be staged.

- [x] **Step 2: Execute 760px Browser QA**

At 760x1000 verify:

- component cards, shared fields, role/weight board, detail editor, saved shelf, result and final actions wrap to one column.
- expanded detail editor and result text are not clipped.
- outer page and component iframe each satisfy `scrollWidth === clientWidth`.
- ResizeObserver synchronizes component height without nested blank space or scroll trapping.
- keyboard focus and disclosure/action aria state remain available.

Save `backtest-portfolio-mix-one-shell-760-qa.png` as generated/untracked evidence.

- [x] **Step 3: Apply `superpowers:verification-before-completion` with fresh commands**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py tests/test_backtest_workflow_shell.py tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q
npm run build --prefix app/web/components/backtest_portfolio_mix_workspace/frontend
.venv/bin/python -m py_compile app/services/backtest_portfolio_mix_workspace.py app/web/backtest_portfolio_mix_workspace.py app/web/backtest_analysis.py app/web/components/backtest_portfolio_mix_workspace/component.py
git diff --check
```

The full service suite may retain only the already documented baseline failures; any new Portfolio Mix failure blocks closeout.

- [x] **Step 4: Apply `finance-doc-sync`**

Document durable ownership:

- `BACKTEST_UI_FLOW.md`: Portfolio Mix is a single React four-step Level1 workspace.
- `PORTFOLIO_SELECTION_FLOW.md`: fresh weighted result, saved setup and Level2 candidate source are distinct contracts.
- `SCRIPT_STRUCTURE_MAP.md`: new pure service, web adapter and component ownership; legacy compare page is not the primary Mix renderer.
- active task docs: exact RED/GREEN counts, runtime/Browser evidence, baseline failures and remaining risks.
- root logs: only a 3~5 line milestone/decision/handoff summary.

- [x] **Step 5: Audit protected paths and commit closeout**

```bash
git status --short
git diff --cached --name-only
git diff --cached --check
```

Explicitly stage only canonical docs, active task docs and root handoff logs. Staged paths must not include registries, Run History, saved JSONL, `.superpowers/`, screenshots or run artifacts.

Commit:

```bash
git commit -m "Portfolio Mix 원셸 QA와 문서 동기화"
```

## 15차 Completion Report Contract

- 15-1~15-4 전체 roadmap 완료 상태
- distinct Korean commit hash 목록
- RED/GREEN focused/full test counts와 baseline failure 분류
- React production build / target py_compile / `git diff --check` 결과
- desktop / 760px actual Mix create/run/save/restore/edit/rerun/Level2 boundary QA 범위
- generated screenshot 절대 경로
- protected registry/Run History/saved JSONL/`.superpowers/`/screenshot 미커밋 확인
- legacy compatibility surface, accessibility 자동화와 남은 위험

# Portfolio Mix Step 3 Result Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Portfolio Mix 실행 결과를 KPI만 보여 주는 상태에서 누적 성과, 월별 수익률, 기여도, 계산 근거를 실제 계산값과 동일한 계약으로 해석할 수 있는 Step 3 작업 공간으로 확장한다.

**Architecture:** `app/services/backtest_portfolio_mix_workspace.py`가 weighted result bundle을 사용자 표시용 JSON-safe evidence로 변환하고, web adapter는 성공한 현재 결과에 이 evidence만 연결한다. React는 Python이 만든 표시값과 시계열을 SVG/HTML로 표현하고 hover·focus intent만 소유하며, 수익률 분류·포맷·benchmark 추론은 하지 않는다.

**Tech Stack:** Python 3, pandas, Streamlit component bridge, React 18, TypeScript, SVG, pytest, Browser QA.

## Global Constraints

- 기존 weighted portfolio 계산식, 리샘플링, 저장 JSONL schema와 Level2 handoff contract는 변경하지 않는다.
- 실제 공통 날짜와 `result_df.Total Balance` / `result_df.Total Return`만 사용하고 존재하지 않는 benchmark, 보유 종목, 월 수익률을 만들지 않는다.
- 퍼센트·금액·역할·data trust 문구는 Python에서 완성하고 React는 raw key를 해석하지 않는다.
- 누적 성과는 시작값 100으로 정규화하며 desktop 날짜 tick은 최대 6개, 760px은 최대 3개다.
- 월별 수익률의 계산 불가 행은 표에 `계산값 없음`으로 보존하고 막대 차트에서는 제외한다.
- 누적 차트와 월별 막대는 pointer hover와 keyboard focus에서 같은 tooltip 정보를 제공하고 pointer leave/blur에서 제거한다.
- 기본 화면은 KPI, 누적 성과, 월별 수익률까지이며 기여도·월별 표·계산 및 데이터 근거는 disclosure 안에 둔다.
- 신규 chart dependency를 추가하지 않고 기존 React/SVG/CSS만 사용한다.
- 보호 대상 registry, Run History, saved JSONL, `.superpowers/`, QA screenshot과 run artifact는 stage/commit하지 않는다.

---

### Task 50: Weighted Mix Result Evidence Contract (16-1)

**Files:**
- Modify: `app/services/backtest_portfolio_mix_workspace.py`
- Modify: `app/web/backtest_portfolio_mix_workspace.py`
- Modify: `tests/test_backtest_portfolio_mix_workspace.py`
- Modify: active task `PLAN.md`, `STATUS.md`, `RUNS.md`

**Interfaces:**
- Consumes: `execute_weighted_portfolio()`가 반환하는 `summary_df`, `result_df`, `chart_df`, `component_contribution_amount_df`, `component_contribution_share_df`, `component_data_trust_rows`, component role/weight metadata.
- Produces: `build_portfolio_mix_result_evidence(weighted_bundle: Mapping[str, Any]) -> dict[str, Any]`와 `current_result["evidence"]`.
- Evidence keys: `identity`, `kpis`, `equity_chart`, `monthly_returns`, `contribution`, `calculation_basis`, `data_trust_rows`.

- [x] **Step 1: Write the RED service contract tests**

Add tests with a pandas fixture containing sparse actual dates, one unavailable monthly return and two component contribution series:

```python
def test_mix_result_evidence_projects_user_labels_charts_and_contribution():
    evidence = build_portfolio_mix_result_evidence(_weighted_result_fixture())
    assert evidence["kpis"][0] == {
        "id": "annualized_return",
        "label": "연환산 수익률",
        "value": 0.096,
        "value_label": "9.60%",
    }
    assert evidence["equity_chart"]["rows"][0]["index_value"] == 100.0
    assert evidence["monthly_returns"]["chart_rows"][0]["month_label"] == "2026.02"
    assert evidence["contribution"]["summary_rows"][0]["target_weight_label"] == "50.00%"


def test_mix_result_evidence_preserves_sparse_and_unavailable_months():
    evidence = build_portfolio_mix_result_evidence(_weighted_result_fixture())
    assert len(evidence["equity_chart"]["desktop_ticks"]) <= 6
    assert len(evidence["equity_chart"]["compact_ticks"]) <= 3
    assert evidence["monthly_returns"]["table_rows"][0]["return_label"] == "계산값 없음"
    assert all(row["available"] for row in evidence["monthly_returns"]["chart_rows"])
```

Add a web adapter test that executes a successful weighted draft and asserts `current_result["evidence"]` is present without removing `run_result_id`, fingerprint, summary or period.

- [x] **Step 2: Run RED and record the intended failure**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_backtest_portfolio_mix_workspace.py::test_mix_result_evidence_projects_user_labels_charts_and_contribution \
  tests/test_backtest_portfolio_mix_workspace.py::test_mix_result_evidence_preserves_sparse_and_unavailable_months \
  -q
```

Expected: collection/import failure because `build_portfolio_mix_result_evidence` does not exist.

- [x] **Step 3: Implement the pure evidence builder**

Add finite-number, ISO date, percent, ratio, amount and actual-tick helpers, then expose:

```python
def build_portfolio_mix_result_evidence(
    weighted_bundle: Mapping[str, Any],
) -> dict[str, Any]:
    """Project a weighted run into user-readable, JSON-safe result evidence."""
```

The function must:

- create four KPI rows: annualized return, maximum drawdown, Sharpe ratio and end balance, each with `value` and Python-computed `value_label`.
- normalize finite `Total Balance` rows to a starting index of 100 and add date, balance, cumulative return and display labels.
- choose tick dates from actual rows only, preserving first/last rows and limiting desktop/compact ticks to 6/3.
- retain all dated monthly rows in `table_rows`, mark non-finite `Total Return` as unavailable, and include only finite rows in `chart_rows`.
- translate contribution frames into ending summary rows and amount/share timeline rows using component labels, role labels and target-weight labels.
- translate `component_data_trust_rows` into Korean user-facing labels without raw internal keys or absolute paths.
- return only JSON-safe scalars, lists and dictionaries.

Export the function in `__all__` and call it from `execute_portfolio_mix_draft()` only after the weighted build succeeds:

```python
evidence = build_portfolio_mix_result_evidence(weighted_bundle)
current_result = {
    **existing_current_result,
    "evidence": evidence,
}
```

- [x] **Step 4: Run GREEN and focused regression**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'portfolio_mix or weighted_portfolio'
.venv/bin/python -m py_compile app/services/backtest_portfolio_mix_workspace.py app/web/backtest_portfolio_mix_workspace.py
git diff --check
```

Expected: new evidence tests pass; any repository baseline failure must be shown to be unrelated before continuing.

- [x] **Step 5: Commit the implementation unit**

Stage only the two Python modules, the focused test and active task records. Commit:

```bash
git commit -m "Portfolio Mix 결과 근거 계약 구현"
```

### Task 51: React Charts, Hover And Result Spacing (16-2)

**Files:**
- Create: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/PortfolioMixResult.tsx`
- Modify: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/App.tsx`
- Modify: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/styles.css`
- Modify: `tests/test_backtest_portfolio_mix_workspace.py`
- Modify: active task `PLAN.md`, `STATUS.md`, `RUNS.md`

**Interfaces:**
- Consumes: Task 50 `current_result.evidence` without reclassifying status, percentage or data trust.
- Produces: `PortfolioMixResult` presentation component with cumulative SVG, monthly return SVG, disclosure evidence and hover/focus tooltip state.

- [x] **Step 1: Write the RED visual contract tests**

Add source/boundary assertions requiring:

```python
assert "PortfolioMixResult" in app_source
assert "equity_chart" in result_source
assert "monthly_returns" in result_source
assert "onPointerMove" in result_source
assert "onPointerLeave" in result_source
assert "onFocus" in result_source
assert "onBlur" in result_source
assert "mix-result-shell" in styles_source
assert "mix-chart-grid" in styles_source
assert "mix-chart-tooltip" in styles_source
```

Also assert the result component contains no `* 100`, benchmark inference or raw `promotion_min_`/filesystem labels.

- [x] **Step 2: Run RED and record the intended failure**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q -k 'result or hover or visual_contract'
```

Expected: FAIL because `PortfolioMixResult.tsx` and chart/hover CSS contracts do not exist.

- [x] **Step 3: Implement the result presentation and hover/focus intent**

Create `PortfolioMixResult.tsx` with typed evidence interfaces and focused subcomponents:

```tsx
export function PortfolioMixResult({ evidence }: { evidence: MixResultEvidence }) {
  return (
    <div className="mix-result-stack">
      <ResultIdentity evidence={evidence.identity} />
      <KpiGrid rows={evidence.kpis} />
      <div className="mix-chart-grid">
        <EquityChart model={evidence.equity_chart} />
        <MonthlyReturnChart model={evidence.monthly_returns} />
      </div>
      <ResultEvidenceDetails evidence={evidence} />
    </div>
  )
}
```

`EquityChart` must choose the nearest actual point from pointer coordinates, draw a crosshair/marker and display date, base-100 index, cumulative-return label and balance label. `MonthlyReturnChart` must display positive/negative bars around zero and show month, monthly-return label and month-end balance. Both charts must clear tooltip state on `onPointerLeave`/`onBlur`, expose the same content on keyboard `onFocus`, and use the Python labels verbatim.

The disclosure must render ending component contribution, amount/share segmented timelines, monthly result table and calculation/data-trust copy. When an evidence list is empty it renders a concise unavailable message, not an empty board.

Replace the summary-only result branch in `App.tsx` with:

```tsx
<div className="mix-result-shell">
  {notice && <div className="mix-notice">{notice}</div>}
  {currentResult?.evidence && <PortfolioMixResult evidence={currentResult.evidence} />}
</div>
```

- [x] **Step 4: Implement responsive spacing and chart CSS**

Add these structural contracts and supporting SVG/table/tooltip styles:

```css
.mix-result-shell { display: grid; gap: 18px; margin-top: 18px; }
.mix-result-stack { display: grid; gap: 16px; }
.mix-current { display: grid; gap: 18px; }
.mix-chart-grid { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(0, .9fr); gap: 14px; }
@media (max-width: 760px) { .mix-chart-grid { grid-template-columns: minmax(0, 1fr); } }
```

Use `min-width: 0`, wrapped labels, horizontally scrollable dense tables only inside disclosure, visible focus rings and tooltip placement clamped inside the chart card.

- [x] **Step 5: Run GREEN, production build and focused regression**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q
npm run build --prefix app/web/components/backtest_portfolio_mix_workspace/frontend
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q
git diff --check
```

Expected: focused tests and React production build pass with no TypeScript error.

- [x] **Step 6: Commit the implementation unit**

Stage only the React result component, App/CSS, focused tests and active task records. Commit:

```bash
git commit -m "Portfolio Mix 결과 차트와 호버 구현"
```

### Task 52: Runtime Browser QA, Documentation And Closeout (16-3)

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate but do not stage: `backtest-portfolio-mix-result-evidence-desktop-qa.png`
- Generate but do not stage: `backtest-portfolio-mix-result-evidence-760-qa.png`

**Interfaces:**
- Consumes: Task 50 evidence contract and Task 51 presentation component.
- Produces: verified desktop/760px runtime behavior, canonical ownership documentation and protected-path audit.

- [x] **Step 1: Execute desktop Browser QA with an actual Mix run**

At approximately 1440px:

1. open Backtest Analysis → Portfolio Mix.
2. select GTAA and Equal Weight, assign roles and set 50%/50% weights.
3. execute the Mix and confirm feedback and result boxes have visible separation.
4. confirm KPI labels show `9.60%` style percentages, a two-decimal Sharpe and a localized end balance.
5. confirm cumulative performance starts at 100, uses actual date labels and has no invented benchmark.
6. hover first/middle/last cumulative points and confirm tooltip date, index, cumulative return and balance update; move the pointer out and confirm tooltip disappears.
7. hover positive and negative monthly bars and confirm month, return and ending balance; move out and confirm tooltip disappears.
8. open `상세 결과 근거` and verify component contribution, monthly table and calculation/data basis; confirm no raw JSON, absolute path or internal key is visible.
9. confirm the browser console error count remains 0.

Save `backtest-portfolio-mix-result-evidence-desktop-qa.png` as generated/untracked evidence.

- [x] **Step 2: Execute 760px Browser QA**

At 760x1000 verify:

- cumulative and monthly charts stack to one column and actual tick labels are limited to at most three.
- cards, axis labels, tooltip, disclosure tables and contribution labels do not clip.
- pointer hover and keyboard focus reveal equivalent tooltip content and clear on leave/blur.
- page and component iframe satisfy `scrollWidth === clientWidth` except the explicitly scrollable table wrapper.
- ResizeObserver keeps the component height synchronized without nested blank space or scroll trapping.

Save `backtest-portfolio-mix-result-evidence-760-qa.png` as generated/untracked evidence.

- [x] **Step 3: Apply `superpowers:verification-before-completion` with fresh commands**

```bash
.venv/bin/python -m pytest \
  tests/test_backtest_portfolio_mix_workspace.py \
  tests/test_backtest_workflow_shell.py \
  tests/test_backtest_refactor_boundaries.py \
  -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q
npm run build --prefix app/web/components/backtest_portfolio_mix_workspace/frontend
.venv/bin/python -m py_compile \
  app/services/backtest_portfolio_mix_workspace.py \
  app/web/backtest_portfolio_mix_workspace.py \
  app/web/backtest_analysis.py \
  app/web/components/backtest_portfolio_mix_workspace/component.py
git diff --check
```

Any new Portfolio Mix failure blocks closeout. A repository baseline failure may be reported only after a focused passing command demonstrates this implementation is not the cause.

- [x] **Step 4: Apply `finance-doc-sync`**

Record durable ownership:

- `BACKTEST_UI_FLOW.md`: Step 3 defaults to KPI + cumulative performance + monthly returns, with contribution/table/basis disclosure.
- `PORTFOLIO_SELECTION_FLOW.md`: Mix result interpretation uses the current weighted run only and does not synthesize benchmark or holdings.
- `SCRIPT_STRUCTURE_MAP.md`: the pure Mix result evidence builder owns formatting and JSON-safe projection; React owns display and hover/focus intent.
- active task docs: exact RED/GREEN counts, build/compile output, Browser QA evidence, baseline failures and residual risks.
- root logs: only a 3–5 line milestone, decision and handoff summary.

- [x] **Step 5: Audit protected paths and commit closeout**

```bash
git status --short
git diff --cached --name-only
git diff --cached --check
```

Explicitly stage only canonical docs, active task docs and root handoff logs. Staged paths must not include registry JSONL, Run History, saved JSONL, `.superpowers/`, screenshots or run artifacts.

Commit:

```bash
git commit -m "Portfolio Mix 결과 해석 QA와 문서 동기화"
```

## 16차 Completion Report Contract

- 16-1~16-3 전체 roadmap 완료 상태
- distinct Korean commit hash 목록
- RED/GREEN focused/full test counts와 baseline failure 분류
- React production build / target py_compile / `git diff --check` 결과
- desktop / 760px actual Mix run, hover/focus, disclosure, no-benchmark QA 범위
- generated screenshot 절대 경로
- protected registry/Run History/saved JSONL/`.superpowers/`/screenshot 미커밋 확인
- sparse/unavailable month, very long history SVG density, keyboard/browser 자동화와 남은 위험

# Portfolio Mix Chart Geometry And Full-Width Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 누적 성과 hover가 실제 plot point와 같은 위치를 선택하게 고치고 두 결과 chart를 각각 전체 폭 한 행으로 확장한다.

**Architecture:** React의 chart geometry helper가 client X를 viewBox와 plot padding을 고려한 index로 바꾸며, chart cards는 CSS single-column grid를 사용한다. Python evidence와 weighted runtime은 변경하지 않는다.

**Tech Stack:** React 18, TypeScript, SVG, CSS Grid, pytest source contract, Vite, Browser QA.

## Global Constraints

- `PLOT_LEFT`, `PLOT_RIGHT`, `CHART_WIDTH`의 실제 plot geometry를 한 helper에서 사용한다.
- tooltip edge clamp, keyboard focus, actual-date evidence와 no-benchmark 계약을 유지한다.
- chart dependency, Python result schema, saved/run-history/Level2 schema를 추가하거나 바꾸지 않는다.
- registry, Run History, saved JSONL, `.superpowers/`, screenshots는 stage/commit하지 않는다.

---

### Task 53: Plot-Aware Hover And Full-Width Charts (17-1)

**Files:**
- Modify: `tests/test_backtest_portfolio_mix_workspace.py`
- Modify: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/PortfolioMixResult.tsx`
- Modify: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/styles.css`
- Modify: active task `STATUS.md`, `RUNS.md`

**Interfaces:**
- Consumes: pointer `clientX`, SVG `getBoundingClientRect()`, existing `PLOT_LEFT/PLOT_RIGHT/CHART_WIDTH`, row count.
- Produces: `nearestPlotIndex(clientX, left, width, count)` and a one-column `.mix-chart-grid` at every viewport.

- [ ] **Step 1: Write RED source contracts**

Require `nearestPlotIndex`, viewBox conversion, plot-width subtraction and a desktop single-column grid:

```python
assert "function nearestPlotIndex" in result_source
assert "CHART_WIDTH - PLOT_LEFT - PLOT_RIGHT" in result_source
assert "nearestPlotIndex(event.clientX, rect.left, rect.width, rows.length)" in result_source
assert ".mix-chart-grid { display: grid; grid-template-columns: minmax(0, 1fr);" in styles_source
```

- [ ] **Step 2: Run RED**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q -k 'chart_geometry or visual_contract'
```

Expected: `nearestPlotIndex`와 desktop single-column CSS가 아직 없어 FAIL.

- [ ] **Step 3: Implement minimal geometry and layout correction**

Replace full-SVG ratio selection with:

```tsx
function nearestPlotIndex(clientX: number, left: number, width: number, count: number) {
  if (count <= 1 || width <= 0) return 0
  const chartX = ((clientX - left) / width) * CHART_WIDTH
  const plotWidth = CHART_WIDTH - PLOT_LEFT - PLOT_RIGHT
  const ratio = clamp((chartX - PLOT_LEFT) / plotWidth, 0, 1)
  return Math.round(ratio * (count - 1))
}
```

Use it in both chart pointer handlers. Change `.mix-chart-grid` to one `minmax(0, 1fr)` column and keep the 760px rule consistent.

- [ ] **Step 4: Run GREEN and build**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q
npm run build --prefix app/web/components/backtest_portfolio_mix_workspace/frontend
git diff --check
```

Expected: focused tests and Vite production build pass.

- [ ] **Step 5: Commit**

```bash
git commit -m "Portfolio Mix 차트 위치와 크기 개선"
```

### Task 54: Actual Browser QA And Closeout (17-2)

**Files:**
- Modify: active task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Generate but do not stage: `backtest-portfolio-mix-chart-geometry-desktop-qa.png`
- Generate but do not stage: `backtest-portfolio-mix-chart-geometry-760-qa.png`

- [ ] **Step 1: Run actual desktop QA**

Run GTAA 50 / Equal Weight 50, confirm two full-width chart rows, hover plot first/middle/last and verify
crosshair/date follow the cursor position. Hover positive/negative monthly bars and confirm tooltip values.

- [ ] **Step 2: Run 760px QA**

Confirm both charts remain one column, axis/ticks/tooltips do not clip, component/page horizontal overflow is 0,
and ResizeObserver height remains synchronized.

- [ ] **Step 3: Apply fresh verification and protected-path audit**

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py tests/test_backtest_workflow_shell.py tests/test_backtest_refactor_boundaries.py -q
npm run build --prefix app/web/components/backtest_portfolio_mix_workspace/frontend
.venv/bin/python -m py_compile app/services/backtest_portfolio_mix_workspace.py app/web/backtest_portfolio_mix_workspace.py
git diff --check
git diff --cached --name-only
```

- [ ] **Step 4: Sync closeout records and commit**

Record exact RED/GREEN, Browser QA and residual automation gaps without changing the canonical data/runtime contract.

```bash
git commit -m "Portfolio Mix 차트 사용성 QA 정리"
```
