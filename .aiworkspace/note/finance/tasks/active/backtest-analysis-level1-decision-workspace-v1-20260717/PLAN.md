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
