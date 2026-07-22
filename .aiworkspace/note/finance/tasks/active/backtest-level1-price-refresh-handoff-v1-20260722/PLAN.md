# Level1 Price Refresh Handoff V1 Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Level1 결과의 공통 가격일이 요청 종료일의 마지막 완료 NYSE 거래일보다 이르면 필요한 종목만 수동 최신화하고, 명시적 동일 설정 재실행 전까지 Level2 인계를 차단한다.

**Architecture:** DB와 ingestion을 모르는 공통 pure freshness service가 Single Strategy와 Portfolio Mix 입력을 정규화하고 사용자-facing 상태를 만든다. 각 Streamlit web adapter가 기존 `backtest_price_refresh` plan/runner를 연결하고 nonce·run id·configuration fingerprint를 재검증한다. 두 활성 React workspace와 Python fallback은 동일 read model만 렌더링한다.

**Tech Stack:** Python 3.12, pytest, Streamlit, React/TypeScript/Vite, existing finance ingestion and MySQL price history.

## 이걸 하는 이유?

Level1 백테스트가 사용자가 요청한 종료일보다 이른 공통 가격일까지 계산되어도 현재 Result Workspace는 이를 행동 가능한 문제로 보여주지 않는다. 오래된 결과가 Level2 후보가 되는 것을 막고, 사용자가 필요한 종목 가격만 DB에 보강한 뒤 같은 설정으로 다시 실행할 수 있어야 한다.

## 확정된 제품 계약

- 수집 목표는 요청 종료일 이하의 마지막 완료 NYSE 거래일이다.
- 수동 최신화는 기존 `Ingestion -> DB -> Loader -> UI` 경계를 사용한다.
- 최신화 직후 백테스트를 자동 실행하지 않는다.
- 저장 row가 있으면 기존 결과를 참고용으로 유지하고 `같은 설정으로 다시 백테스트`를 노출한다.
- `refresh_required`, `provider_gap`, `rerun_required`에서는 Level2 인계를 차단한다.
- 저장 row가 0이고 미해결 종목이 남으면 같은 최신화 버튼을 반복 노출하지 않는다.
- Single Strategy와 Portfolio Mix는 공통 상태 계약을 쓰되 각자의 현재 활성 workspace에 연결한다.

## 파일 소유 구조

### 신규

- `app/services/backtest_level1_price_freshness.py`
- `tests/test_backtest_level1_price_freshness.py`

### Single Strategy

- `app/services/backtest_analysis_result_workspace.py`
- `app/web/backtest_analysis_result_workspace.py`
- `app/web/backtest_analysis_result_workspace_panel.py`
- `app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts`
- `app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx`
- `app/web/components/backtest_analysis_result_workspace/frontend/src/style.css`
- `tests/test_backtest_analysis_result_workspace.py`

### Portfolio Mix

- `app/services/backtest_portfolio_mix_workspace.py`
- `app/web/backtest_portfolio_mix_workspace.py`
- `app/web/components/backtest_portfolio_mix_workspace/frontend/src/App.tsx`
- `app/web/components/backtest_portfolio_mix_workspace/frontend/src/style.css`
- `tests/test_backtest_portfolio_mix_workspace.py`

### 조건부 최소 변경

- `app/services/backtest_price_refresh.py`: 공통 service에 필요한 값이 public result에 없을 때만 추가한다.
- `app/web/backtest_analysis_workspace.py`: 기존 pending-run 경로를 재사용할 수 없을 때만 최소 adapter를 추가한다.

## Task 1: 공통 Level1 가격 최신성 계약

**Files:**

- Create: `app/services/backtest_level1_price_freshness.py`
- Create: `tests/test_backtest_level1_price_freshness.py`
- Reference: `app/services/backtest_price_refresh.py`

### Step 1: RED — meta aggregation 계약 테스트

- [ ] 다음 입력을 포함하는 table-driven test를 작성한다.
  - Single bundle의 `meta.price_freshness`, `tickers`, `cash_ticker`, `benchmark_ticker`, `guardrail_reference_ticker`, `market_regime_benchmark`, `defensive_tickers`
  - Mix component bundle 둘의 symbol 중복과 서로 다른 `common_latest`
  - current configuration의 `end`가 component/weighted meta의 종료일보다 우선하는 경우
- [ ] 기대값은 대문자 정규화·중복 제거된 symbol union, stale/missing/provider-gap union, component 중 가장 이른 `common_latest`, current requested end다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_level1_price_freshness.py -q
```

Expected: module 또는 public 함수 부재로 FAIL.

### Step 2: GREEN — pure meta builder 구현

- [ ] 아래 public 함수를 구현한다.

```python
def build_level1_price_refresh_meta(
    *,
    result_bundle: Mapping[str, Any],
    component_bundles: Sequence[Mapping[str, Any]] = (),
    configuration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize the exact Level1 symbols and date evidence used by refresh planning."""
```

- [ ] DB, Streamlit, collector import 없이 JSON-ready mapping만 반환한다.
- [ ] `configuration["end"]`가 있으면 requested end의 canonical source로 사용한다.
- [ ] component가 없으면 Single bundle만 집계하고, component가 있으면 weighted bundle과 모든 component를 함께 집계한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_level1_price_freshness.py -q
```

Expected: aggregation tests PASS.

### Step 3: RED — 사용자 상태 전이 테스트

- [ ] `build_level1_price_freshness_action()`의 네 상태를 고정한다.
  - eligible plan -> `refresh_required`, `primary_action.id == "refresh_prices"`
  - stored rows > 0 + rerun flag -> `rerun_required`, `primary_action.id == "rerun_same_configuration"`
  - zero rows + unresolved symbols -> `provider_gap`, primary action 없음
  - refresh 필요 없음 -> `current`, `handoff_blocked is False`
- [ ] 모든 비-current 상태에서 `handoff_blocked is True`를 검증한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_level1_price_freshness.py -q
```

Expected: action builder 부재로 FAIL.

### Step 4: GREEN — 사용자 상태 builder 구현

- [ ] 아래 public 함수를 구현한다.

```python
def build_level1_price_freshness_action(
    *,
    plan: Mapping[str, Any] | None,
    refresh_result: Mapping[str, Any] | None = None,
    result_requires_rerun: bool = False,
) -> dict[str, Any]:
    """Project a refresh plan/result into one user action and a Level2 gate."""
```

- [ ] 공통 필드를 고정한다: `state`, `requested_end`, `target_trading_end`, `current_common_latest`, `affected_symbol_count`, `affected_symbol_sample`, `summary`, `guidance`, `handoff_blocked`, `primary_action`, `feedback`.
- [ ] raw job명·저장 row 수는 first-read 문구에 노출하지 않는다.
- [ ] `price_refresh_result_requires_backtest_rerun()`과 기존 plan status semantics를 재사용한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_level1_price_freshness.py -q
.venv/bin/python -m py_compile app/services/backtest_level1_price_freshness.py
```

Expected: PASS, compile exit 0.

### Step 5: Commit

```bash
git add app/services/backtest_level1_price_freshness.py tests/test_backtest_level1_price_freshness.py
git commit -m "기능: Level1 가격 최신성 공통 계약 추가"
```

## Task 2: Single Strategy pure Result Workspace gate

**Files:**

- Modify: `app/services/backtest_analysis_result_workspace.py`
- Test: `tests/test_backtest_analysis_result_workspace.py`

### Step 1: RED — readiness와 actions 계약 테스트

- [ ] `build_level1_technical_handoff_readiness()`에 `price_freshness_action`을 주입하는 테스트를 추가한다.
- [ ] `refresh_required`이면 state가 `data_refresh_required`, `can_handoff=False`, `save_and_move` action 없음인지 검증한다.
- [ ] `rerun_required`이면 state가 `rerun_required`, `can_handoff=False`인지 검증한다.
- [ ] `provider_gap`도 차단하지만 refresh retry action은 만들지 않는지 검증한다.
- [ ] `current`이면 기존 `save_and_move` gate가 그대로 동작하는 회귀 테스트를 유지한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_result_workspace.py -q
```

Expected: 새 인자/필드 부재로 FAIL.

### Step 2: GREEN — workspace projection과 handoff gate 구현

- [ ] `build_level1_technical_handoff_readiness()`와 `build_backtest_analysis_result_workspace()`에 optional `price_freshness_action: Mapping[str, Any] | None = None`을 추가한다.
- [ ] workspace root에 `data_freshness_action`을 투영한다.
- [ ] 비-current 상태에서는 `actions`에 오직 enabled primary action만 넣고 `save_and_move`를 제거한다.
- [ ] current 상태에서는 기존 lifecycle, core result contract, maturity, handler gate를 보존한다.
- [ ] service는 refresh runner, DB, Streamlit을 import하지 않는다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_result_workspace.py -q
.venv/bin/python -m py_compile app/services/backtest_analysis_result_workspace.py
```

Expected: PASS, 기존 result lifecycle tests 포함 회귀 없음.

### Step 3: Commit

```bash
git add app/services/backtest_analysis_result_workspace.py tests/test_backtest_analysis_result_workspace.py
git commit -m "기능: Level1 가격 부족 시 인계 차단"
```

## Task 3: Single Strategy web adapter와 mutation 경계

**Files:**

- Modify: `app/web/backtest_analysis_result_workspace.py`
- Conditional modify: `app/web/backtest_analysis_workspace.py`
- Test: `tests/test_backtest_analysis_result_workspace.py`

### Step 1: RED — intent validation 테스트

- [ ] 허용 action을 `save_and_move`, `refresh_prices`, `rerun_same_configuration`으로 확장하는 테스트를 추가한다.
- [ ] 세 action 모두 nonce, current run id, current configuration fingerprint, workspace action enabled를 검증하는지 테스트한다.
- [ ] stale run id, stale fingerprint, duplicate nonce, disabled action이 handler를 호출하지 않는지 검증한다.
- [ ] refresh action이 current plan에서 더 이상 eligible하지 않으면 runner를 호출하지 않는지 검증한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_result_workspace.py -q
```

Expected: `refresh_prices`와 `rerun_same_configuration`이 invalid intent로 거절되어 FAIL.

### Step 2: GREEN — current workspace에 DB-aware plan 주입

- [ ] `build_current_backtest_analysis_result_workspace()`에서 current Single bundle과 `backtest_current_draft_payload`로 `build_level1_price_refresh_meta()`를 만든다.
- [ ] web adapter에서만 `build_backtest_price_refresh_plan()`을 호출한다.
- [ ] session의 `backtest_last_result_refresh_result`와 `backtest_last_result_requires_rerun`을 넣어 `build_level1_price_freshness_action()`을 호출한다.
- [ ] pure workspace builder에 완성된 `price_freshness_action`을 주입한다.
- [ ] current result가 없거나 lifecycle workspace가 보이지 않으면 plan을 만들지 않는다.

### Step 3: GREEN — refresh와 명시적 rerun handler 구현

- [ ] `refresh_prices` handler는 validation을 통과한 현재 meta에 대해 `run_backtest_price_refresh()`를 정확히 한 번 호출한다.
- [ ] refresh result를 `backtest_last_result_refresh_result`에 저장한다.
- [ ] `price_refresh_result_requires_backtest_rerun(result)`가 true이면 `backtest_last_result_requires_rerun=True`로 설정한다.
- [ ] 저장 row가 0이고 unresolved가 남으면 rerun flag를 만들지 않고 공통 action builder가 `provider_gap`을 표시하게 한다.
- [ ] `rerun_same_configuration` handler는 current `backtest_current_draft_payload`와 current strategy selection으로 `backtest_pending_single_run`을 설정해 기존 실행 소유자가 다음 rerun에서 실행하도록 한다.
- [ ] refresh handler는 backtest runner를 호출하지 않고, rerun handler는 collector를 호출하지 않는다.
- [ ] 새 Single run 성공 시 기존 실행 경로가 `backtest_last_result_refresh_result`와 rerun flag를 비우는 현재 계약을 확인하고, 빠져 있다면 성공 commit 지점에만 clear를 추가한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_result_workspace.py -q
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q -k "result_workspace or pending_single"
.venv/bin/python -m py_compile app/web/backtest_analysis_result_workspace.py app/web/backtest_analysis_workspace.py
```

Expected: PASS; refresh와 rerun side effect가 서로 분리됨.

### Step 4: Commit

```bash
git add app/web/backtest_analysis_result_workspace.py app/web/backtest_analysis_workspace.py tests/test_backtest_analysis_result_workspace.py
git commit -m "기능: Level1 가격 최신화와 재실행 연결"
```

`app/web/backtest_analysis_workspace.py`가 실제로 변경되지 않았다면 stage 대상에서 제외한다.

## Task 4: Single Strategy React와 fallback 행동 카드

**Files:**

- Modify: `app/web/backtest_analysis_result_workspace_panel.py`
- Modify: `app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts`
- Modify: `app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx`
- Modify: `app/web/components/backtest_analysis_result_workspace/frontend/src/style.css`
- Test: `tests/test_backtest_analysis_result_workspace.py`
- Test: relevant component source/build tests discovered by `rg`

### Step 1: RED — renderer 계약 테스트

- [ ] Python fallback이 Result Header 다음에 freshness card를 렌더링하는 테스트를 추가한다.
- [ ] card가 요청 종료일, 목표 거래일, 현재 공통 기준일, 대상 종목 수를 보여주는지 검증한다.
- [ ] state별 primary button payload가 `refresh_prices` 또는 `rerun_same_configuration`이고 `save_and_move`는 숨겨지는지 검증한다.
- [ ] `current`에서는 card가 없고 기존 결과 UI가 유지되는지 검증한다.
- [ ] React source contract test가 있다면 동일 필드와 action union을 검증한다.

Run:

```bash
rg -n "BacktestAnalysisResultWorkspace|data_freshness_action|save_and_move" tests app/web/components/backtest_analysis_result_workspace
.venv/bin/python -m pytest tests/test_backtest_analysis_result_workspace.py -q
```

Expected: 새 card/action 계약 부재로 FAIL.

### Step 2: GREEN — React 타입과 card 구현

- [ ] intent union을 `save_and_move | refresh_prices | rerun_same_configuration`으로 확장한다.
- [ ] `DataFreshnessAction` 타입을 공통 service 필드와 정확히 맞춘다.
- [ ] Result Header 직후, Performance Summary 전에 card를 배치한다.
- [ ] 제목과 문구는 사용자의 결과 영향과 다음 행동을 우선하고 raw run/job/row 진단값을 노출하지 않는다.
- [ ] primary action 하나만 렌더링하며 run id와 current fingerprint를 payload에 포함한다.
- [ ] desktop에서는 4개 핵심 값을 한 줄, 760px 이하에서는 2열로 표시하고 긴 symbol 텍스트가 overflow하지 않게 한다.

### Step 3: GREEN — Python fallback parity 구현

- [ ] fallback도 같은 read model과 동일 payload를 사용한다.
- [ ] React 사용 불가/예외 상황에서도 freshness gate와 action이 사라지지 않게 한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_analysis_result_workspace.py -q
npm --prefix app/web/components/backtest_analysis_result_workspace/frontend run build
git diff --check
```

Expected: pytest PASS, Vite build exit 0, whitespace error 없음.

### Step 4: Commit

```bash
git add app/web/backtest_analysis_result_workspace_panel.py app/web/components/backtest_analysis_result_workspace/frontend/src/types.ts app/web/components/backtest_analysis_result_workspace/frontend/src/BacktestAnalysisResultWorkspace.tsx app/web/components/backtest_analysis_result_workspace/frontend/src/style.css tests/test_backtest_analysis_result_workspace.py
git commit -m "개선: Level1 가격 최신화 행동 카드 표시"
```

## Task 5: Portfolio Mix 합집합 최신화와 명시적 재실행

**Files:**

- Modify: `app/services/backtest_portfolio_mix_workspace.py`
- Modify: `app/web/backtest_portfolio_mix_workspace.py`
- Modify: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/App.tsx`
- Modify: `app/web/components/backtest_portfolio_mix_workspace/frontend/src/style.css`
- Test: `tests/test_backtest_portfolio_mix_workspace.py`

### Step 1: RED — pure Mix workspace gate 테스트

- [ ] `build_portfolio_mix_workspace()`에 optional `price_freshness_action`을 넣는 테스트를 추가한다.
- [ ] `refresh_required`와 `provider_gap`에서 `save_mix`/`handoff_level2`를 숨기고 refresh card 계약을 반환하는지 검증한다.
- [ ] `rerun_required`에서 기존 `run_mix` 실행 경로를 `같은 설정으로 다시 백테스트` primary action으로 노출하는지 검증한다.
- [ ] `current`에서 기존 save/handoff/action 계약이 유지되는지 검증한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q
```

Expected: 새 인자/field 부재로 FAIL.

### Step 2: GREEN — Mix pure read model 구현

- [ ] `build_portfolio_mix_workspace()`와 `build_portfolio_mix_workspace_from_session()`에 optional freshness action을 전달한다.
- [ ] root `data_freshness_action`을 React/fallback 공통 계약으로 둔다.
- [ ] blocked 상태에서는 Level2 action을 만들지 않는다.
- [ ] `rerun_required` primary action id는 기존 deferred action `run_mix`를 사용하고 label만 `같은 설정으로 다시 백테스트`로 투영한다.

### Step 3: RED — Mix refresh mutation 테스트

- [ ] `MIX_SESSION_KEYS`에 `price_refresh_result`를 추가하는 테스트를 작성한다.
- [ ] component bundle + weighted bundle + draft shared end의 합집합 meta가 refresh runner에 한 번 전달되는지 검증한다.
- [ ] component 중복 symbol은 runner 입력에서 한 번만 나타나는지 검증한다.
- [ ] refresh 성공 직후 `run_current_portfolio_mix()`가 호출되지 않는지 검증한다.
- [ ] 다음 명시적 `run_mix` 성공 후 refresh result가 clear되는지 검증한다.
- [ ] no-row unresolved result에서는 refresh retry action이 사라지고 handoff는 계속 차단되는지 검증한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q
```

Expected: refresh action/handler/session key 부재로 FAIL.

### Step 4: GREEN — Mix web adapter와 handler 구현

- [ ] `MIX_SESSION_KEYS["price_refresh_result"]`를 추가한다.
- [ ] current result가 있을 때 `component_bundles`, `weighted_bundle`, draft `shared.end`로 공통 meta와 existing refresh plan을 만든다.
- [ ] `_DEFERRED_ACTIONS`와 current handlers에 `refresh_prices`를 추가한다.
- [ ] refresh handler는 current result identity/fingerprint와 eligible plan을 다시 검증하고 `run_backtest_price_refresh()`만 호출한다.
- [ ] 결과를 Mix 전용 refresh session key에 저장한다.
- [ ] `run_current_portfolio_mix()`의 전체 성공 commit 지점에서만 Mix refresh result를 clear한다.
- [ ] saved mix restore/run은 기존 계약을 유지하고 새 current result를 만든 뒤 freshness를 다시 계산한다.

### Step 5: GREEN — Mix React/fallback parity 구현

- [ ] Result 영역 상단에 Single과 동일한 freshness card를 표시한다.
- [ ] `refresh_required`는 `refresh_prices`, `rerun_required`는 기존 `run_mix` intent를 보낸다.
- [ ] fallback도 동일 상태, 날짜, 대상 수, primary action을 사용한다.
- [ ] 1280px/760px에서 기존 Mix form과 result layout을 침범하지 않게 한다.

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_portfolio_mix_workspace.py -q
.venv/bin/python -m py_compile app/services/backtest_portfolio_mix_workspace.py app/web/backtest_portfolio_mix_workspace.py
npm --prefix app/web/components/backtest_portfolio_mix_workspace/frontend run build
git diff --check
```

Expected: PASS, compile/build exit 0, 중복 수집 없음.

### Step 6: Commit

```bash
git add app/services/backtest_portfolio_mix_workspace.py app/web/backtest_portfolio_mix_workspace.py app/web/components/backtest_portfolio_mix_workspace/frontend/src/App.tsx app/web/components/backtest_portfolio_mix_workspace/frontend/src/style.css tests/test_backtest_portfolio_mix_workspace.py
git commit -m "기능: Portfolio Mix 가격 최신화 인계 연결"
```

## Task 6: 통합 검증, 실제 GTAA QA, 문서 동기화

**Files:**

- Modify: `.aiworkspace/note/finance/tasks/active/backtest-level1-price-refresh-handoff-v1-20260722/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-level1-price-refresh-handoff-v1-20260722/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-level1-price-refresh-handoff-v1-20260722/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-level1-price-refresh-handoff-v1-20260722/RISKS.md`
- Modify only if durable contract changed: relevant `.aiworkspace/note/finance/docs/flows/` or `docs/architecture/` canonical document
- Generate, do not commit: `backtest-level1-price-refresh-handoff-v1-qa.png`

### Step 1: focused automated verification

- [ ] 공통 service, Single workspace, Mix workspace, boundary tests를 실행한다.

```bash
.venv/bin/python -m pytest tests/test_backtest_level1_price_freshness.py tests/test_backtest_analysis_result_workspace.py tests/test_backtest_portfolio_mix_workspace.py -q
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m py_compile app/services/backtest_level1_price_freshness.py app/services/backtest_analysis_result_workspace.py app/services/backtest_portfolio_mix_workspace.py app/web/backtest_analysis_result_workspace.py app/web/backtest_portfolio_mix_workspace.py
npm --prefix app/web/components/backtest_analysis_result_workspace/frontend run build
npm --prefix app/web/components/backtest_portfolio_mix_workspace/frontend run build
git diff --check
```

Expected: all PASS/build exit 0/diff check clean.

### Step 2: 실제 GTAA read-only plan 검증

- [ ] 현재 DB를 다시 읽어 요청 종료일 `2026-07-22`에 대한 last completed NYSE date, common latest, stale/missing/provider-gap symbol, refresh target을 기록한다.
- [ ] 값은 2026-07-22 진단 당시 수치로 hard-code하지 않고 실행 시점 DB 결과와 workspace model이 일치하는지만 검증한다.
- [ ] 수집 실행은 Browser QA의 명시적 버튼 클릭에서만 발생하게 한다.

Expected: service plan과 화면 날짜/대상 수가 동일함.

### Step 3: Browser QA — Single Strategy

- [ ] GTAA에서 종료일 `2026-07-22`로 백테스트한다.
- [ ] 결과 상단 card가 요청일·목표 거래일·공통 기준일·대상 수를 보여주고 Level2 인계를 숨기는지 확인한다.
- [ ] `종목 데이터 최신화`를 한 번 누르고 백테스트가 자동 실행되지 않는지 확인한다.
- [ ] 기존 결과가 참고용으로 남고 `같은 설정으로 다시 백테스트`가 표시되는지 확인한다.
- [ ] 같은 설정 재실행 후 실제 runtime 기준으로 `current`, `refresh_required`, `provider_gap` 중 올바른 상태가 되는지 확인한다.

### Step 4: Browser QA — Portfolio Mix와 responsive

- [ ] component symbol이 겹치는 Mix에서 최신화 target이 합집합·중복 제거되는지 확인한다.
- [ ] refresh 직후 Mix가 자동 실행되지 않고 명시적 `run_mix`가 필요한지 확인한다.
- [ ] desktop 1280px와 compact 760px에서 card/button overflow가 없는지 확인한다.
- [ ] application console error가 0인지 확인한다.
- [ ] 대표 화면을 `backtest-level1-price-refresh-handoff-v1-qa.png`로 저장하고 커밋하지 않는다.

### Step 5: finance-doc-sync와 task closeout

- [ ] `finance-doc-sync` skill을 사용해 durable flow/architecture 문서 변경 필요성을 판정한다.
- [ ] task `STATUS.md`에 roadmap 3/3, 실제 완료 조건, 남은 공백을 기록한다.
- [ ] `RUNS.md`에 정확한 명령과 결과, `NOTES.md`에 최종 계약, `RISKS.md`에 provider/DB 환경 공백을 기록한다.
- [ ] root handoff logs에는 3~5줄 milestone과 다음 위치만 남긴다.

### Step 6: protected artifact 확인과 최종 commit

```bash
git status --short
git diff --check
git diff --name-only --cached
```

- [ ] 아래 파일/폴더가 stage되지 않았는지 확인한다.
  - `.aiworkspace/note/finance/registries/*.jsonl`
  - `.aiworkspace/note/finance/saved/*.jsonl`
  - `.aiworkspace/note/finance/run_history/`
  - `*.png`, `*.md` QA snapshot generated artifact
  - `.superpowers/`

```bash
git add .aiworkspace/note/finance/tasks/active/backtest-level1-price-refresh-handoff-v1-20260722
git add .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: Level1 가격 최신화 흐름 완료 기록"
```

Canonical docs가 실제로 변경됐다면 해당 파일만 명시적으로 추가한다.

## 전체 완료 조건

- [ ] 실제 DB evidence와 화면의 날짜·대상 수가 일치한다.
- [ ] 사용자는 결과 상단에서 왜 기간이 짧은지와 다음 행동을 바로 이해한다.
- [ ] 최신화는 기존 ingestion runner와 DB 저장 경계를 따른다.
- [ ] 최신화 직후 백테스트가 자동 실행되지 않는다.
- [ ] 보강 필요/재실행 필요/provider gap 상태에서 Level2 인계가 불가능하다.
- [ ] 새 실행이 current freshness를 통과하면 기존 저장·Level2 흐름이 열린다.
- [ ] Single Strategy와 Portfolio Mix, React와 fallback의 상태 계약이 같다.
- [ ] focused tests, TypeScript builds, Browser QA, screenshot, documentation closeout이 완료된다.

## 실행 시 주의사항

- 기존 legacy `_render_last_run_details()`나 Data Trust block을 primary route로 복원하지 않는다.
- provider field가 없다는 이유로 임의 가격/합성 데이터를 만들지 않는다.
- registry, saved portfolio, run history의 현재 사용자 변경을 되돌리거나 commit하지 않는다.
- 구현 중 current route가 문서와 다르면 behavior를 임의 변경하지 말고 소유 경계만 계획/문서에 바로잡는다.
