# Futures Macro Pattern Outlook V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `Workspace > Overview > Futures Macro`를 오늘의 충격, 1D / 5D / 20D 패턴, 향후 5D / 20D 조건부 위험 체제를 한 흐름에서 읽는 단기 거시 레이더로 개선한다.

**Architecture:** 기존 stored futures daily OHLCV와 today thermometer를 보존하고, Streamlit-free `futures_macro_pattern.py`가 point-in-time 다중 기간 feature와 현재 상태를 소유한다. 별도 `futures_macro_pattern_validation.py`가 historical episode, forward outcome, walk-forward publication gate를 만들고, Python payload bridge가 Market Context형 React workbench에 현재·전망·근거를 전달한다.

**Tech Stack:** Python 3.11+, pandas, NumPy, unittest / pytest, Streamlit component bridge, React 18, TypeScript 5.7, Vite 6, CSS, MySQL-backed stored futures OHLCV.

## Global Constraints

- User-selected UI direction is `A · 맥락→전망형`; visible order is `현재 체제 -> 1주·1개월 전망 -> 패턴 경로와 근거 -> 60일 체제 ribbon -> 자산별 경로 -> 방법론`.
- 이 저장소의 현재 로컬 검증 표준은 `unittest`이며 `.venv`와 `pyproject.toml`에 `pytest`가 없다. 아래 pytest-style test snippets는 contract pseudocode로 읽고, executable test files와 commands는 동등한 `unittest.TestCase`, `subTest`, `assertAlmostEqual`, `python -m unittest`로 실행한다. 이 기능을 위해 pytest dependency를 추가하지 않는다.
- 전체 시장 위험 체제가 첫 결과이며 자산 family 방향은 보조 근거다.
- 관측 기간은 1D / 5D / 20D, 공개 전망은 5D / 20D다.
- 다음 1D 확률은 hero 결과로 만들지 않는다.
- 확률은 unconditional baseline, independent episode count, estimate status와 함께 표시한다.
- independent episode 30개 미만은 `UNAVAILABLE`, 30~59개는 최대 `PROVISIONAL`이다.
- 60개 이상이어도 chronological out-of-sample Brier score와 calibration gate를 통과해야 `VERIFIED`다.
- 우위가 없거나 confidence interval이 baseline과 구분되지 않으면 `방향 우위 미확인`이다.
- UI에서 provider / FRED를 직접 fetch하지 않는다. `Ingestion -> DB -> Service -> UI`를 유지한다.
- 신규 provider, DB schema, registry / saved JSONL, live approval, broker order, auto rebalance는 V1 범위 밖이다.
- 매수·매도·승인·선정·통과 표현을 사용자-facing copy에 쓰지 않는다.
- current evidence는 contextual attribution이며 인과관계 증명으로 표현하지 않는다.
- diagnostics run / row / failure count를 첫 화면의 주인공으로 만들지 않는다.
- continuous futures roll / maturity와 yfinance source caveat를 유지한다.
- 실행 위치는 현재 linked worktree `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`와 branch `codex/sub-dev`다. 중첩 worktree를 만들지 않는다.
- unrelated untracked research와 `.superpowers/`를 stage하거나 수정하지 않는다.

## File Structure

### Create

- `app/services/futures_macro_pattern.py`
  - point-in-time family feature frame, current regime / transition, 60D path / ribbon, change conditions.
- `app/services/futures_macro_pattern_validation.py`
  - forward outcome labels, independent episode matching, baseline comparison, chronological validation, publication status, cache.
- `tests/test_futures_macro_pattern.py`
  - multi-window feature와 current pattern deterministic contract.
- `tests/test_futures_macro_pattern_validation.py`
  - leakage, purge / embargo, episode spacing, probability, Brier / calibration, publication gate contract.
- `app/web/streamlit_components/futures_macro_workbench/src/PatternHorizonSection.tsx`
  - 현재 / 다음 1주 / 다음 1개월 horizon cards.
- `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
  - 최근 관측 경로와 5D / 20D probability zone.
- `app/web/streamlit_components/futures_macro_workbench/src/PatternRibbonSection.tsx`
  - 최근 60거래일 regime / transition ribbon.
- `app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx`
  - 주식·금리·달러·안전자산·원자재 current / outlook / change condition.
- `app/web/streamlit_components/futures_macro_workbench/src/MethodDisclosure.tsx`
  - effective sample, Brier / calibration, source / roll caveat, context-only boundary.

### Modify

- `app/services/futures_macro_thermometer.py:434-510,1173-1205,1276-1350`
  - normalized daily candles를 pattern builder에 연결하고 cache clear marker를 공유한다.
- `app/web/overview/futures_macro_helpers.py:120-158,731-807,818-842,1760-1790`
  - legacy lazy validation CTA를 제거하고 pattern outlook을 기본 payload에 연결한다.
- `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx:1-180`
  - V2 payload types와 새 reading order.
- `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx`
  - today brief를 current regime hero로 정리하고 evidence disclosure를 유지한다.
- `app/web/streamlit_components/futures_macro_workbench/src/CurrentEvidencePanel.tsx`
  - current / transition / outlook / invalidate evidence section 지원.
- `app/web/streamlit_components/futures_macro_workbench/src/style.css`
  - economic-cycle visual grammar와 responsive layout.
- `tests/test_service_contracts.py:7968-8245,25440-26055`
  - 기존 lazy validation / V1 payload 기대를 V2 기본 pattern outlook 계약으로 교체하고 cache / action 회귀를 보존한다.
- `.aiworkspace/note/finance/docs/flows/README.md`
  - Futures Macro flow를 current pattern / 5D / 20D outlook으로 갱신한다.
- `.aiworkspace/note/finance/docs/architecture/README.md`
  - 새 Streamlit-free pattern / validation ownership을 기록한다.
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
  - 새 service / React files의 소유 경계를 반영한다.
- `.aiworkspace/note/finance/WORK_PROGRESS.md`
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

### Retire From Active Render

- `RecentFlowSection.tsx`
- `HistoricalValidationPanel.tsx`

두 파일은 Task 6에서 import / render를 제거한다. 삭제 여부는 repository-wide reference가 0개임을 `rg`로 확인한 뒤 결정하며, compatibility를 위해 남기더라도 active render에는 포함하지 않는다.

---

### Task 1: Point-In-Time Multi-Window Feature Frame

**Files:**
- Create: `app/services/futures_macro_pattern.py`
- Create: `tests/test_futures_macro_pattern.py`
- Read: `app/services/futures_macro_thermometer.py:183-260,403-510`

**Interfaces:**
- Consumes: normalized candle `DataFrame` columns `provider_symbol`, `ts`, `Date`, `Close`; `SCORE_DEFINITIONS` and `SIGNAL_Z_THRESHOLD` from `futures_macro_thermometer.py`.
- Produces:
  - `PATTERN_WINDOWS: tuple[int, ...] = (1, 5, 20)`
  - `PATTERN_FAMILY_KEYS: tuple[str, ...]`
  - `PATTERN_FEATURE_COLUMNS: tuple[str, ...]`
  - `build_pattern_feature_frame(candles: pd.DataFrame, *, selected_symbols: Sequence[str]) -> pd.DataFrame`
  - one row per normalized date, index name `Date`, numeric wide columns such as `risk_on__1d_z`, `risk_on__5d_z`, `risk_on__20d_z`, `risk_on__5d_slope`, `risk_on__20d_slope`, `risk_on__acceleration`, `risk_on__5d_persistence`, `risk_on__20d_persistence`, `risk_on__breadth`, `risk_on__volatility_ratio`, plus `available_symbol_count`.

- [x] **Step 1: Write deterministic feature tests**

Create fixtures with 90 dates and at least `ES=F`, `NQ=F`, `RTY=F`, `ZN=F`, `ZB=F`, `GC=F`, `CL=F`, `HG=F`, `6E=F`, `6J=F`. Assert:

```python
def test_pattern_feature_frame_uses_only_trailing_rows_and_inverts_rates_and_fx():
    candles = _pattern_candles(days=90, shock_start=70)
    frame = build_pattern_feature_frame(candles, selected_symbols=SYMBOLS)

    assert frame.index.name == "Date"
    assert list(frame.index) == sorted(frame.index)
    latest = frame.iloc[-1]
    assert latest["risk_on__5d_z"] > 0
    assert latest["rate_pressure__5d_z"] > 0  # ZN / ZB price fall is inverted
    assert latest["dollar_pressure__5d_z"] > 0  # FX futures fall is inverted
    assert 0.0 <= latest["risk_on__5d_persistence"] <= 1.0
    assert 0.0 <= latest["risk_on__breadth"] <= 1.0


def test_pattern_feature_frame_is_point_in_time_stable_when_future_rows_are_appended():
    base = _pattern_candles(days=80, shock_start=70)
    extended = _pattern_candles(days=90, shock_start=70)

    before = build_pattern_feature_frame(base, selected_symbols=SYMBOLS)
    after = build_pattern_feature_frame(extended, selected_symbols=SYMBOLS)

    pd.testing.assert_series_equal(before.iloc[-1], after.loc[before.index[-1]], check_names=False)


def test_pattern_feature_frame_requires_past_sixty_day_volatility():
    frame = build_pattern_feature_frame(_pattern_candles(days=40), selected_symbols=SYMBOLS)
    assert frame.empty
```

- [x] **Step 2: Run the focused test and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern.py -q
```

Expected: collection/import failure because `app.services.futures_macro_pattern` does not exist.

- [x] **Step 3: Implement family mapping and trailing feature frame**

Use exact family keys and map existing score definitions without duplicating weights:

```python
PATTERN_WINDOWS = (1, 5, 20)
PATTERN_FAMILY_KEYS = (
    "risk_on",
    "growth",
    "rate_pressure",
    "dollar_pressure",
    "safe_haven",
    "inflation_pressure",
)
PATTERN_FEATURE_SUFFIXES = (
    "1d_z",
    "5d_z",
    "20d_z",
    "5d_slope",
    "20d_slope",
    "acceleration",
    "5d_persistence",
    "20d_persistence",
    "breadth",
    "volatility_ratio",
)
PATTERN_FEATURE_COLUMNS = tuple(
    f"{family}__{suffix}"
    for family in PATTERN_FAMILY_KEYS
    for suffix in PATTERN_FEATURE_SUFFIXES
)
SCORE_TO_FAMILY_KEY = {
    "Risk-On Score": "risk_on",
    "Growth Score": "growth",
    "Rate Pressure Score": "rate_pressure",
    "Dollar Pressure Score": "dollar_pressure",
    "Safe Haven Score": "safe_haven",
    "Inflation Pressure Score": "inflation_pressure",
}


def _daily_symbol_z(close_matrix: pd.DataFrame) -> pd.DataFrame:
    returns = close_matrix.pct_change(fill_method=None)
    trailing_vol = returns.rolling(60, min_periods=60).std(ddof=0)
    return returns.divide(trailing_vol.where(trailing_vol.abs() > 1e-12))


def _family_daily_z(symbol_z: pd.DataFrame, definition: ScoreDefinition) -> pd.DataFrame:
    members = [symbol for symbol in definition.members if symbol in symbol_z.columns]
    weighted = pd.concat(
        [symbol_z[symbol] * float(definition.members[symbol]) for symbol in members],
        axis=1,
    )
    return pd.DataFrame({
        "value": weighted.mean(axis=1, skipna=True),
        "breadth": weighted.gt(0).sum(axis=1).divide(weighted.notna().sum(axis=1).replace(0, pd.NA)),
        "coverage": weighted.notna().sum(axis=1),
    })


def build_pattern_feature_frame(
    candles: pd.DataFrame,
    *,
    selected_symbols: Sequence[str],
) -> pd.DataFrame:
    close_matrix = _pattern_close_matrix(candles, selected_symbols)
    symbol_z = _daily_symbol_z(close_matrix)
    output = pd.DataFrame(index=symbol_z.index)
    for definition in SCORE_DEFINITIONS:
        family = SCORE_TO_FAMILY_KEY[definition.name]
        daily = _family_daily_z(symbol_z, definition)
        output[f"{family}__1d_z"] = daily["value"]
        output[f"{family}__5d_z"] = daily["value"].rolling(5, min_periods=5).sum() / (5 ** 0.5)
        output[f"{family}__20d_z"] = daily["value"].rolling(20, min_periods=20).sum() / (20 ** 0.5)
        output[f"{family}__5d_slope"] = daily["value"] - daily["value"].shift(4)
        output[f"{family}__20d_slope"] = daily["value"] - daily["value"].shift(19)
        output[f"{family}__acceleration"] = daily["value"].rolling(5).mean() - daily["value"].shift(5).rolling(5).mean()
        sign = daily["value"].apply(lambda value: 1.0 if value > 0 else (-1.0 if value < 0 else 0.0))
        output[f"{family}__5d_persistence"] = sign.rolling(5).apply(_dominant_sign_ratio, raw=False)
        output[f"{family}__20d_persistence"] = sign.rolling(20).apply(_dominant_sign_ratio, raw=False)
        output[f"{family}__breadth"] = daily["breadth"]
        output[f"{family}__volatility_ratio"] = daily["value"].rolling(20).std(ddof=0).divide(
            daily["value"].rolling(60).std(ddof=0).replace(0, pd.NA)
        )
    output["available_symbol_count"] = close_matrix.notna().sum(axis=1)
    output.index.name = "Date"
    return output.dropna(subset=[f"{family}__20d_z" for family in PATTERN_FAMILY_KEYS], how="all")
```

Implement `_pattern_close_matrix()` with normalized dates and no forward fill across missing symbol observations. Implement `_dominant_sign_ratio()` as `max(positive_count, negative_count) / non_zero_count`, returning `0.0` for an all-zero window.

- [x] **Step 4: Run focused tests and existing thermometer regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'macro_thermometer_builds_flow_context or macro_thermometer_inverts_rates'
```

Expected: all selected tests pass.

- [x] **Step 5: Commit Task 1**

```bash
git add app/services/futures_macro_pattern.py tests/test_futures_macro_pattern.py
git commit -m "선물 매크로 다중 기간 패턴 feature 추가"
```

---

### Task 2: Current Regime, Transition, Path, And Change Conditions

**Files:**
- Modify: `app/services/futures_macro_pattern.py`
- Modify: `tests/test_futures_macro_pattern.py`

**Interfaces:**
- Consumes: Task 1 `build_pattern_feature_frame()` output.
- Produces:
  - `classify_pattern_state(row: pd.Series) -> dict[str, Any]`
  - `build_current_pattern_snapshot(feature_frame: pd.DataFrame, *, path_limit: int = 60) -> dict[str, Any]`
  - snapshot keys: `schema_version`, `status`, `as_of_date`, `regime`, `regime_label`, `transition`, `transition_label`, `summary`, `families`, `evidence`, `change_conditions`, `path`, `ribbon`, `coverage`.

- [ ] **Step 1: Add RED tests for state semantics**

```python
def test_current_pattern_labels_persistent_defensive_regime():
    frame = _feature_frame(
        risk_on=(-1.1, -1.4, -1.2),
        safe_haven=(0.8, 1.0, 0.9),
        dollar_pressure=(0.4, 0.7, 0.6),
    )
    snapshot = build_current_pattern_snapshot(frame)
    assert snapshot["regime"] == "defensive"
    assert snapshot["transition"] == "persisting"
    assert "방어" in snapshot["summary"]
    assert snapshot["path"][-1]["date"] == frame.index[-1].date().isoformat()


def test_current_pattern_labels_transition_attempt_when_one_and_five_day_reverse_twenty_day():
    frame = _feature_frame(
        risk_on=(0.9, 0.7, -1.2),
        safe_haven=(-0.6, -0.4, 0.8),
    )
    snapshot = build_current_pattern_snapshot(frame)
    assert snapshot["transition"] == "transition_attempt"
    assert any("5D" in item for item in snapshot["change_conditions"])


def test_current_pattern_keeps_conflict_and_low_signal_distinct():
    conflict = build_current_pattern_snapshot(_conflict_feature_frame())
    quiet = build_current_pattern_snapshot(_low_signal_feature_frame())
    assert (conflict["regime"], conflict["transition"]) == ("mixed", "conflicting")
    assert (quiet["regime"], quiet["transition"]) == ("mixed", "low_signal")


def test_current_pattern_returns_partial_without_forcing_missing_family():
    frame = _feature_frame(drop_families={"dollar_pressure"})
    snapshot = build_current_pattern_snapshot(frame)
    assert snapshot["status"] == "PARTIAL"
    assert snapshot["families"]["dollar_pressure"]["status"] == "UNAVAILABLE"
```

- [ ] **Step 2: Run the new tests and confirm RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern.py -q -k 'current_pattern'
```

Expected: failures because `build_current_pattern_snapshot` and state labels are absent.

- [ ] **Step 3: Implement deterministic current state**

Use these exact public state keys:

```python
REGIME_LABELS = {
    "risk_seeking": "위험선호 체제",
    "defensive": "방어적 위험 체제",
    "inflation_rate_pressure": "물가·금리 부담 체제",
    "mixed": "혼재 체제",
}
TRANSITION_LABELS = {
    "broadening": "확산 중",
    "persisting": "지속 중",
    "transition_attempt": "전환 시도",
    "conflicting": "충돌",
    "low_signal": "저신호 / 관망",
    "unavailable": "자료 부족",
}


def classify_pattern_state(row: pd.Series) -> dict[str, Any]:
    one = _family_values(row, "1d_z")
    five = _family_values(row, "5d_z")
    twenty = _family_values(row, "20d_z")
    macro_pressure = _mean_available(five, ("rate_pressure", "dollar_pressure", "inflation_pressure"))
    defensive_confirmed = five.get("risk_on", 0.0) <= -SIGNAL_Z_THRESHOLD and (
        five.get("safe_haven", 0.0) >= SIGNAL_Z_THRESHOLD
        or five.get("dollar_pressure", 0.0) >= SIGNAL_Z_THRESHOLD
    )
    inflation_confirmations = sum(
        five.get(key, 0.0) >= SIGNAL_Z_THRESHOLD
        for key in ("rate_pressure", "dollar_pressure", "inflation_pressure")
    )
    if inflation_confirmations >= 2 and five.get("risk_on", 0.0) < SIGNAL_Z_THRESHOLD:
        regime = "inflation_rate_pressure"
    elif defensive_confirmed:
        regime = "defensive"
    elif five.get("risk_on", 0.0) >= SIGNAL_Z_THRESHOLD and _breadth(row, "risk_on") >= 0.6:
        regime = "risk_seeking"
    else:
        regime = "mixed"
    transition = _transition_state(one=one, five=five, twenty=twenty, row=row, regime=regime)
    return {"regime": regime, "transition": transition, "macro_pressure": macro_pressure}


def build_current_pattern_snapshot(feature_frame: pd.DataFrame, *, path_limit: int = 60) -> dict[str, Any]:
    if feature_frame.empty:
        return _empty_pattern_snapshot("다중 기간 패턴을 계산할 일봉 이력이 부족합니다.")
    latest = feature_frame.iloc[-1]
    state = classify_pattern_state(latest)
    families = {family: _family_snapshot(latest, family) for family in PATTERN_FAMILY_KEYS}
    return {
        "schema_version": "futures_macro_pattern_v1",
        "status": _pattern_status(families),
        "as_of_date": _index_date(feature_frame.index[-1]),
        **state,
        "regime_label": REGIME_LABELS[state["regime"]],
        "transition_label": TRANSITION_LABELS[state["transition"]],
        "summary": _pattern_summary(state, families),
        "families": families,
        "evidence": _pattern_evidence(state, families),
        "change_conditions": _change_conditions(state, families),
        "path": _pattern_path(feature_frame.tail(path_limit)),
        "ribbon": _pattern_ribbon(feature_frame.tail(path_limit)),
        "coverage": _pattern_coverage(feature_frame, families),
    }
```

Implement `_transition_state()` with this precedence: unavailable → low signal → conflict → transition attempt → broadening → persisting. A transition attempt requires material 1D and 5D direction opposite to 20D; broadening requires 5D breadth ≥ 0.6 and 5D strength greater than 20D strength; persisting requires aligned material 5D / 20D.

- [ ] **Step 4: Run full pattern tests and compile**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern.py -q
.venv/bin/python -m py_compile app/services/futures_macro_pattern.py
```

Expected: all tests pass and compile exits 0.

- [ ] **Step 5: Commit Task 2**

```bash
git add app/services/futures_macro_pattern.py tests/test_futures_macro_pattern.py
git commit -m "선물 매크로 현재 패턴 상태 추가"
```

---

### Task 3: Forward Outcomes And Independent Similar Episodes

**Files:**
- Create: `app/services/futures_macro_pattern_validation.py`
- Create: `tests/test_futures_macro_pattern_validation.py`
- Read: `app/services/futures_macro_validation.py:206-632`

**Interfaces:**
- Consumes: Task 1 feature frame, normalized candle matrix, Task 2 current snapshot.
- Produces:
  - `OUTLOOK_HORIZONS = (5, 20)`
  - `OUTCOME_REGIMES = ("risk_seeking", "defensive", "inflation_rate_pressure", "mixed")`
  - `build_forward_outcome_frame(candles: pd.DataFrame, feature_frame: pd.DataFrame, *, selected_symbols: Sequence[str]) -> pd.DataFrame`
  - `select_similar_episodes(feature_frame: pd.DataFrame, *, current_date: pd.Timestamp, horizon: int, max_episodes: int = 120) -> pd.DataFrame`
  - output columns `as_of_date`, `horizon`, `outcome_regime`, family forward z values, `similarity_distance`, `effective_episode`.

- [ ] **Step 1: Write leakage, label, and episode tests**

```python
def test_forward_outcomes_use_as_of_volatility_and_have_mutually_exclusive_regimes():
    candles, features = _validation_fixture(days=180)
    outcomes = build_forward_outcome_frame(candles, features, selected_symbols=SYMBOLS)
    assert set(outcomes["horizon"]) == {5, 20}
    assert outcomes["outcome_regime"].isin(OUTCOME_REGIMES).all()
    assert outcomes.groupby(["as_of_date", "horizon"]).size().max() == 1


def test_appending_future_rows_does_not_change_earlier_forward_label_after_endpoint_is_complete():
    base_candles, base_features = _validation_fixture(days=160)
    more_candles, more_features = _validation_fixture(days=180)
    before = build_forward_outcome_frame(base_candles, base_features, selected_symbols=SYMBOLS)
    after = build_forward_outcome_frame(more_candles, more_features, selected_symbols=SYMBOLS)
    key = before.iloc[-30][["as_of_date", "horizon"]].tolist()
    left = before[(before.as_of_date == key[0]) & (before.horizon == key[1])].iloc[0]
    right = after[(after.as_of_date == key[0]) & (after.horizon == key[1])].iloc[0]
    assert left["outcome_regime"] == right["outcome_regime"]


def test_similar_episodes_exclude_current_and_forward_overlap_and_separate_anchors():
    _, features = _validation_fixture(days=240)
    current_date = features.index[-1]
    matches = select_similar_episodes(features, current_date=current_date, horizon=20)
    positions = [features.index.get_loc(date) for date in matches["as_of_date"]]
    current_pos = features.index.get_loc(current_date)
    assert all(position <= current_pos - 20 - 1 for position in positions)
    ordered = sorted(positions)
    assert min(right - left for left, right in zip(ordered, ordered[1:])) >= 20
    assert matches["similarity_distance"].is_monotonic_increasing


def test_similarity_uses_robust_train_history_scaling_not_full_sample_statistics():
    _, features = _validation_fixture(days=240)
    base = select_similar_episodes(features.iloc[:-20], current_date=features.index[-21], horizon=5)
    mutated = features.copy()
    mutated.iloc[-20:, :] = 999.0
    after = select_similar_episodes(mutated.iloc[:-20], current_date=features.index[-21], horizon=5)
    pd.testing.assert_series_equal(base["as_of_date"], after["as_of_date"])
```

- [ ] **Step 2: Run tests and confirm RED**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern_validation.py -q
```

Expected: module import failure.

- [ ] **Step 3: Implement forward outcome contract**

```python
OUTLOOK_HORIZONS = (5, 20)
OUTCOME_REGIMES = ("risk_seeking", "defensive", "inflation_rate_pressure", "mixed")
MIN_INDEPENDENT_EPISODES = 30
VERIFIED_EPISODES = 60


def _classify_forward_regime(row: pd.Series) -> str:
    pressures = sum(
        row.get(f"{family}__forward_z", 0.0) >= SIGNAL_Z_THRESHOLD
        for family in ("rate_pressure", "dollar_pressure", "inflation_pressure")
    )
    if pressures >= 2 and row.get("risk_on__forward_z", 0.0) < SIGNAL_Z_THRESHOLD:
        return "inflation_rate_pressure"
    if row.get("risk_on__forward_z", 0.0) <= -SIGNAL_Z_THRESHOLD and (
        row.get("safe_haven__forward_z", 0.0) >= SIGNAL_Z_THRESHOLD
        or row.get("dollar_pressure__forward_z", 0.0) >= SIGNAL_Z_THRESHOLD
    ):
        return "defensive"
    if row.get("risk_on__forward_z", 0.0) >= SIGNAL_Z_THRESHOLD and row.get("risk_on__breadth", 0.0) >= 0.6:
        return "risk_seeking"
    return "mixed"


def build_forward_outcome_frame(
    candles: pd.DataFrame,
    feature_frame: pd.DataFrame,
    *,
    selected_symbols: Sequence[str],
) -> pd.DataFrame:
    close = _pattern_close_matrix(candles, selected_symbols)
    as_of_vol = close.pct_change(fill_method=None).rolling(60, min_periods=60).std(ddof=0)
    rows: list[dict[str, Any]] = []
    for horizon in OUTLOOK_HORIZONS:
        forward = close.shift(-horizon).divide(close).sub(1.0)
        scaled = forward.divide(as_of_vol.mul(horizon ** 0.5).replace(0, pd.NA))
        for as_of_date in feature_frame.index.intersection(scaled.index):
            record = _forward_family_record(
                as_of_date=as_of_date,
                horizon=horizon,
                scaled_symbol_returns=scaled.loc[as_of_date],
                feature_row=feature_frame.loc[as_of_date],
            )
            if record is not None:
                record["outcome_regime"] = _classify_forward_regime(pd.Series(record))
                rows.append(record)
    return pd.DataFrame(rows).sort_values(["as_of_date", "horizon"]).reset_index(drop=True)
```

Use Task 1 `SCORE_DEFINITIONS` weights in `_forward_family_record()`. Do not use future-window volatility. Store family endpoint return, median path return, interquartile path range, and max adverse path for asset pathway disclosure.

- [ ] **Step 4: Implement robust similarity and independent anchors**

```python
SIMILARITY_SUFFIXES = (
    "1d_z", "5d_z", "20d_z", "5d_slope", "20d_slope",
    "acceleration", "5d_persistence", "20d_persistence", "breadth", "volatility_ratio",
)


def select_similar_episodes(
    feature_frame: pd.DataFrame,
    *,
    current_date: pd.Timestamp,
    horizon: int,
    max_episodes: int = 120,
) -> pd.DataFrame:
    ordered = feature_frame.sort_index()
    current_pos = int(ordered.index.get_loc(current_date))
    eligible_end = current_pos - int(horizon)
    candidates = ordered.iloc[:max(0, eligible_end)].copy()
    columns = [column for column in PATTERN_FEATURE_COLUMNS if column.endswith(SIMILARITY_SUFFIXES)]
    train = candidates[columns].replace([float("inf"), float("-inf")], pd.NA)
    median = train.median(axis=0)
    scale = train.quantile(0.75) - train.quantile(0.25)
    scale = scale.where(scale.abs() > 1e-9, 1.0)
    current = feature_frame.loc[current_date, columns]
    distance = ((train - current).divide(scale)).pow(2).mean(axis=1, skipna=True).pow(0.5)
    ranked = distance.dropna().sort_values().rename("similarity_distance").reset_index()
    ranked = ranked.rename(columns={ranked.columns[0]: "as_of_date"})
    return _select_spaced_episode_anchors(ranked, minimum_spacing=horizon, limit=max_episodes)
```

`_select_spaced_episode_anchors()` receives the original feature index, converts candidate dates to trading-row positions, skips anchors whose positional gap is smaller than `minimum_spacing`, then returns accepted rows sorted by similarity distance. Calendar-day gaps must not substitute for trading-row gaps.

- [ ] **Step 5: Run focused tests and compile**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern_validation.py -q
.venv/bin/python -m py_compile app/services/futures_macro_pattern_validation.py
```

Expected: pass and compile exit 0.

- [ ] **Step 6: Commit Task 3**

```bash
git add app/services/futures_macro_pattern_validation.py tests/test_futures_macro_pattern_validation.py
git commit -m "선물 매크로 유사 패턴 episode 전망 추가"
```

---

### Task 4: Chronological Validation And Publication Gate

**Files:**
- Modify: `app/services/futures_macro_pattern_validation.py`
- Modify: `tests/test_futures_macro_pattern_validation.py`

**Interfaces:**
- Consumes: Task 3 outcomes and similar episode anchors.
- Produces:
  - `build_pattern_outlook_snapshot(candles, feature_frame, current_pattern, *, selected_symbols) -> dict[str, Any]`
  - `clear_futures_macro_pattern_validation_cache() -> None`
  - `load_overview_futures_macro_pattern_outlook(*, query_fn, symbols, years=5, cache_ttl_seconds=900) -> dict[str, Any]`
  - horizon item keys: `horizon`, `label`, `probabilities`, `baseline_probabilities`, `probability_lift`, `dominant_regime`, `episode_count`, `estimate_status`, `status_reason`, `brier_score`, `baseline_brier_score`, `calibration_error`, `closest_episodes`, `asset_pathways`.

- [ ] **Step 1: Add RED tests for publication thresholds**

```python
@pytest.mark.parametrize(
    ("episodes", "brier", "baseline_brier", "calibration", "expected"),
    [
        (29, 0.20, 0.25, 0.04, "UNAVAILABLE"),
        (30, 0.20, 0.25, 0.04, "PROVISIONAL"),
        (59, 0.20, 0.25, 0.04, "PROVISIONAL"),
        (60, 0.20, 0.25, 0.04, "VERIFIED"),
        (60, 0.26, 0.25, 0.04, "PROVISIONAL"),
        (60, 0.20, 0.25, 0.15, "PROVISIONAL"),
    ],
)
def test_publication_status_requires_sample_brier_and_calibration(
    episodes, brier, baseline_brier, calibration, expected
):
    assert publication_status_for_metrics(
        episode_count=episodes,
        brier_score=brier,
        baseline_brier_score=baseline_brier,
        calibration_error=calibration,
        fold_improvement_ratio=0.67,
    ) == expected


def test_walk_forward_folds_are_chronological_and_embargoed():
    frame = _dated_feature_frame(1200)
    folds = build_walk_forward_folds(frame, horizon=20)
    assert len(folds) >= 3
    for fold in folds:
        assert fold.train_end < fold.test_start
        assert frame.index.get_loc(fold.test_start) - frame.index.get_loc(fold.train_end) > 20


def test_outlook_reports_baseline_lift_and_no_edge_when_interval_overlaps_baseline():
    snapshot = build_pattern_outlook_snapshot(**_no_edge_fixture())
    horizon = snapshot["horizons"][0]
    assert sum(horizon["probabilities"].values()) == pytest.approx(1.0)
    assert set(horizon["probability_lift"]) == set(OUTCOME_REGIMES)
    assert horizon["edge_label"] == "방향 우위 미확인"


def test_outlook_isolates_current_pattern_when_validation_fails():
    snapshot = build_pattern_outlook_snapshot(**_short_history_fixture())
    assert snapshot["status"] == "LIMITED"
    assert all(item["estimate_status"] == "UNAVAILABLE" for item in snapshot["horizons"])
    assert snapshot["current_pattern"]["status"] in {"READY", "PARTIAL"}
```

- [ ] **Step 2: Run tests and confirm RED**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern_validation.py -q -k 'publication or walk_forward or outlook'
```

Expected: missing API failures.

- [ ] **Step 3: Implement probability, baseline, Brier, and calibration helpers**

```python
def _regime_probabilities(rows: pd.DataFrame) -> dict[str, float]:
    counts = rows["outcome_regime"].value_counts()
    total = int(counts.sum())
    if total <= 0:
        return {}
    return {regime: float(counts.get(regime, 0)) / total for regime in OUTCOME_REGIMES}


def multiclass_brier_score(actual: Sequence[str], probabilities: Sequence[dict[str, float]]) -> float | None:
    if not actual or len(actual) != len(probabilities):
        return None
    losses = []
    for observed, forecast in zip(actual, probabilities):
        losses.append(sum((float(forecast.get(regime, 0.0)) - float(observed == regime)) ** 2 for regime in OUTCOME_REGIMES))
    return float(sum(losses) / len(losses))


def publication_status_for_metrics(
    *,
    episode_count: int,
    brier_score: float | None,
    baseline_brier_score: float | None,
    calibration_error: float | None,
    fold_improvement_ratio: float,
) -> str:
    if episode_count < MIN_INDEPENDENT_EPISODES:
        return "UNAVAILABLE"
    if episode_count < VERIFIED_EPISODES:
        return "PROVISIONAL"
    improved = brier_score is not None and baseline_brier_score is not None and brier_score < baseline_brier_score
    calibrated = calibration_error is not None and calibration_error <= 0.10
    stable = fold_improvement_ratio >= 0.60
    return "VERIFIED" if improved and calibrated and stable else "PROVISIONAL"
```

Calibration error is the weighted absolute difference between predicted probability buckets `(0,.2],(.2,.4],...` and observed frequency. Baseline is expanding historical regime frequency available before each test date.

- [ ] **Step 4: Implement chronological folds and current outlook**

```python
@dataclass(frozen=True)
class WalkForwardFold:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp


def build_walk_forward_folds(feature_frame: pd.DataFrame, *, horizon: int) -> list[WalkForwardFold]:
    dates = pd.DatetimeIndex(feature_frame.index).sort_values()
    minimum_train = max(252 * 3, horizon * 6)
    test_size = 63
    folds: list[WalkForwardFold] = []
    cursor = minimum_train + horizon
    while cursor + test_size <= len(dates):
        train_end_pos = cursor - horizon - 1
        folds.append(WalkForwardFold(dates[0], dates[train_end_pos], dates[cursor], dates[min(cursor + test_size - 1, len(dates) - 1)]))
        cursor += test_size
    return folds


def build_pattern_outlook_snapshot(
    candles: pd.DataFrame,
    feature_frame: pd.DataFrame,
    current_pattern: dict[str, Any],
    *,
    selected_symbols: Sequence[str],
) -> dict[str, Any]:
    outcomes = build_forward_outcome_frame(candles, feature_frame, selected_symbols=selected_symbols)
    horizons = [
        _build_horizon_outlook(
            horizon=horizon,
            feature_frame=feature_frame,
            outcomes=outcomes,
            current_date=feature_frame.index[-1],
        )
        for horizon in OUTLOOK_HORIZONS
    ]
    return {
        "schema_version": "futures_macro_pattern_outlook_v1",
        "status": "READY" if any(item["estimate_status"] != "UNAVAILABLE" for item in horizons) else "LIMITED",
        "as_of_date": current_pattern.get("as_of_date"),
        "current_pattern": current_pattern,
        "horizons": horizons,
        "method": _outlook_method_summary(horizons),
        "limitations": list(PATTERN_OUTLOOK_LIMITATIONS),
    }
```

`_build_horizon_outlook()` joins selected anchors to same-horizon outcomes, computes probabilities / baseline / lift, uses chronological fold metrics, and returns no probability numbers when status is `UNAVAILABLE`. `edge_label` is only a directional regime label when lift confidence interval excludes zero; otherwise `방향 우위 미확인`.

- [ ] **Step 5: Implement cache keyed by latest daily marker**

Reuse `_latest_daily_cache_marker()` and `_load_validation_futures_rows()` semantics, but keep a separate cache dictionary. The public loader must load five calendar years, normalize candles, build Task 1 features, Task 2 current pattern, and Task 4 outlook. Cache key includes selected symbols, years, latest stored daily marker, and algorithm version.

```python
PATTERN_ALGORITHM_VERSION = "pattern_outlook_v1"
_PATTERN_OUTLOOK_CACHE: dict[tuple[Any, ...], tuple[float, dict[str, Any]]] = {}


def clear_futures_macro_pattern_validation_cache() -> None:
    _PATTERN_OUTLOOK_CACHE.clear()
```

- [ ] **Step 6: Run validation tests and relevant legacy regression**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern_validation.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'macro_validation or interpretation_confidence or basket_forward_return'
.venv/bin/python -m py_compile app/services/futures_macro_pattern_validation.py
```

Expected: all selected tests pass.

- [ ] **Step 7: Commit Task 4**

```bash
git add app/services/futures_macro_pattern_validation.py tests/test_futures_macro_pattern_validation.py
git commit -m "선물 매크로 시간순 전망 검증 추가"
```

---

### Task 5: Default Pattern Outlook Service And React Payload V2

**Files:**
- Modify: `app/services/futures_macro_thermometer.py:1173-1205,1276-1350`
- Modify: `app/web/overview/futures_macro_helpers.py:18-22,87-158,731-842,1760-1790`
- Modify: `tests/test_service_contracts.py:7968-8245,25830-26055`

**Interfaces:**
- Consumes: Task 4 `load_overview_futures_macro_pattern_outlook()`.
- Produces:
  - `build_futures_macro_react_workbench_payload(macro: dict[str, Any], *, pattern_outlook: dict[str, Any]) -> dict[str, Any]`
  - schema `futures_macro_react_workbench_v2`
  - payload keys `command`, `hero`, `horizons`, `pattern_map`, `evidence`, `ribbon`, `asset_pathways`, `method`, `action_boundary`, `boundary_note`.

- [ ] **Step 1: Replace lazy validation contract tests with V2 payload tests**

```python
def test_futures_macro_v2_payload_separates_current_observation_and_future_probabilities(self):
    payload = build_futures_macro_react_workbench_payload(
        _macro_fixture(),
        pattern_outlook=_pattern_outlook_fixture(),
    )
    self.assertEqual(payload["schema_version"], "futures_macro_react_workbench_v2")
    self.assertEqual([item["key"] for item in payload["horizons"]], ["current", "5D", "20D"])
    self.assertEqual(payload["horizons"][0]["kind"], "observation")
    self.assertNotIn("probabilities", payload["horizons"][0])
    self.assertEqual(payload["horizons"][1]["kind"], "conditional_outlook")
    self.assertEqual(payload["horizons"][1]["baseline_label"], "평소 기준 확률")
    self.assertIn(payload["horizons"][1]["estimate_status"], {"VERIFIED", "PROVISIONAL", "UNAVAILABLE"})


def test_futures_macro_v2_payload_has_no_lazy_historical_validation_action(self):
    payload = build_futures_macro_react_workbench_payload(
        _macro_fixture(), pattern_outlook=_pattern_outlook_fixture()
    )
    action_ids = [item["id"] for item in payload["command"]["actions"]]
    self.assertEqual(action_ids, ["daily_refresh", "reload"])
    self.assertNotIn("validation", payload)
    self.assertNotIn("load_validation", str(payload))


def test_futures_macro_v2_payload_preserves_unavailable_without_made_up_probabilities(self):
    outlook = _pattern_outlook_fixture(estimate_status="UNAVAILABLE", probabilities={})
    payload = build_futures_macro_react_workbench_payload(_macro_fixture(), pattern_outlook=outlook)
    five_day = payload["horizons"][1]
    self.assertEqual(five_day["estimate_status"], "UNAVAILABLE")
    self.assertEqual(five_day["probabilities"], [])
    self.assertEqual(five_day["edge_label"], "방향 우위 미확인")


def test_futures_macro_refresh_and_reload_clear_pattern_outlook_cache(self):
    with patch("app.web.overview.futures_macro_helpers.clear_futures_macro_pattern_validation_cache") as clear:
        _reload_futures_macro_snapshot_for_ui()
        clear.assert_called_once_with()


def test_futures_macro_streamlit_fallback_does_not_render_legacy_validation_control(self):
    source = Path("app/web/overview/futures_macro_helpers.py").read_text()
    panel = source[source.index("def _render_futures_macro_panel"):source.index("def render_futures_macro_fragment")]
    self.assertNotIn("_render_futures_macro_validation_controls(", panel)
    self.assertIn("_render_futures_pattern_outlook_fallback(", panel)
```

- [ ] **Step 2: Run focused tests and confirm RED**

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'futures_macro_v2 or pattern_outlook_cache'
```

Expected: V2 schema and new signature failures.

- [ ] **Step 3: Attach current pattern to thermometer snapshot**

In `build_macro_thermometer_read_model()` call Task 1 / Task 2 using the already normalized current candle frame:

```python
feature_frame = build_pattern_feature_frame(candles, selected_symbols=selected_symbols)
pattern = build_current_pattern_snapshot(feature_frame)
return {
    # existing today score / evidence keys stay intact
    "pattern": pattern,
    "pattern_feature_frame": feature_frame,
    ...
}
```

Do not serialize `pattern_feature_frame` into React payload or logs. It is internal service handoff only.

- [ ] **Step 4: Load pattern outlook by default in the tab helper**

In the render path, replace `_futures_macro_session_validation()` and lazy `load_validation` handling with one default read used by both React and fallback:

```python
pattern_outlook = load_overview_futures_macro_pattern_outlook()
payload = build_futures_macro_react_workbench_payload(
    macro,
    pattern_outlook=pattern_outlook,
)
```

When React static build is unavailable, call `_render_futures_pattern_outlook_fallback(pattern_outlook)` after the today brief. The fallback renders current regime / transition, two horizon status rows, and change conditions with native Streamlit; it never renders the legacy historical-validation load button. Daily refresh and reload call both `clear_overview_futures_macro_snapshot_cache()` and `clear_futures_macro_pattern_validation_cache()`. Keep legacy session keys only long enough to delete stale state safely; do not render their data.

- [ ] **Step 5: Implement exact V2 payload shape**

```python
def build_futures_macro_react_workbench_payload(
    macro: dict[str, Any],
    *,
    pattern_outlook: dict[str, Any],
) -> dict[str, Any]:
    pattern = dict(pattern_outlook.get("current_pattern") or macro.get("pattern") or {})
    horizons = [
        _current_pattern_horizon(pattern),
        *[_future_pattern_horizon(item) for item in list(pattern_outlook.get("horizons") or [])],
    ]
    return {
        "schema_version": "futures_macro_react_workbench_v2",
        "component": "FuturesMacroWorkbench",
        "command": _pattern_command_payload(macro, pattern_outlook),
        "hero": _pattern_hero_payload(macro, pattern),
        "horizons": horizons,
        "pattern_map": {
            "title": "최근 패턴 경로",
            "x_label": "위험선호",
            "y_label": "매크로 부담",
            "path": list(pattern.get("path") or []),
            "zones": _pattern_outlook_zones(pattern_outlook),
        },
        "evidence": _pattern_evidence_payload(pattern, pattern_outlook, macro),
        "ribbon": {"title": "최근 60거래일 체제", "items": list(pattern.get("ribbon") or [])},
        "asset_pathways": _pattern_asset_pathways(pattern, pattern_outlook),
        "method": _pattern_method_payload(pattern_outlook),
        "action_boundary": "python_dispatch_only",
        "boundary_note": "이 화면은 빠른 시장 재가격화와 조건부 위험 체제를 설명하며 매수매도 신호가 아닙니다.",
    }
```

`_future_pattern_horizon()` emits probability rows ordered `risk_seeking`, `defensive`, `inflation_rate_pressure`, `mixed`; when unavailable it emits an empty list and a reason. `_pattern_asset_pathways()` always emits the five canonical groups in the design order.

- [ ] **Step 6: Run focused and full Futures Macro Python contracts**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern.py tests/test_futures_macro_pattern_validation.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'futures_macro or macro_thermometer or macro_validation'
.venv/bin/python -m py_compile app/services/futures_macro_thermometer.py app/web/overview/futures_macro_helpers.py
```

Expected: all selected tests pass.

- [ ] **Step 7: Commit Task 5**

```bash
git add app/services/futures_macro_thermometer.py app/web/overview/futures_macro_helpers.py tests/test_service_contracts.py
git commit -m "선물 매크로 패턴 전망 payload 연결"
```

---

### Task 6: Market Context-Style React Workbench V2

**Files:**
- Create: `app/web/streamlit_components/futures_macro_workbench/src/PatternHorizonSection.tsx`
- Create: `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
- Create: `app/web/streamlit_components/futures_macro_workbench/src/PatternRibbonSection.tsx`
- Create: `app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx`
- Create: `app/web/streamlit_components/futures_macro_workbench/src/MethodDisclosure.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/CurrentEvidencePanel.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Modify: `tests/test_service_contracts.py:8035-8245`
- Build: `app/web/streamlit_components/futures_macro_workbench/component_static/`

**Interfaces:**
- Consumes: Task 5 V2 payload.
- Produces: responsive visible order `Hero -> Horizon path -> Pattern map + Evidence -> Ribbon -> Asset pathways -> Method`.

- [ ] **Step 1: Add React source contract RED tests**

```python
def test_futures_macro_react_v2_renders_market_context_reading_order(self):
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    source = (root / "FuturesMacroWorkbench.tsx").read_text()
    self.assertIn("PatternHorizonSection", source)
    self.assertIn("PatternMapSection", source)
    self.assertIn("PatternRibbonSection", source)
    self.assertIn("AssetPathwaysSection", source)
    self.assertLess(source.index("<MacroContextSection"), source.index("<PatternHorizonSection"))
    self.assertLess(source.index("<PatternHorizonSection"), source.index("<PatternMapSection"))
    self.assertNotIn("<RecentFlowSection", source)
    self.assertNotIn("<HistoricalValidationPanel", source)


def test_futures_macro_react_v2_has_responsive_probability_and_unavailable_contract(self):
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    horizon = (root / "PatternHorizonSection.tsx").read_text()
    style = (root / "style.css").read_text()
    self.assertIn("estimate_status", horizon)
    self.assertIn("probabilities.length", horizon)
    self.assertIn("방향 우위 미확인", horizon)
    self.assertIn("@media (max-width: 760px)", style)
    self.assertIn("grid-template-columns: 1fr", style)


def test_futures_macro_react_copy_avoids_trade_and_causal_claims(self):
    source = "\n".join(path.read_text() for path in Path(
        "app/web/streamlit_components/futures_macro_workbench/src"
    ).glob("*.tsx"))
    for forbidden in ("매수", "매도", "승인", "선정", "통과", "원인 확정"):
        self.assertNotIn(forbidden, source)
```

- [ ] **Step 2: Run contract tests and confirm RED**

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'react_v2 or react_copy_avoids'
```

Expected: missing component source failures.

- [ ] **Step 3: Replace V1 payload types and root reading order**

Define V2 types in `FuturesMacroWorkbench.tsx`:

```tsx
export type EstimateStatus = "VERIFIED" | "PROVISIONAL" | "UNAVAILABLE";
export type RegimeKey = "risk_seeking" | "defensive" | "inflation_rate_pressure" | "mixed";
export type FuturesMacroAction = { id: "daily_refresh" | "reload"; label: string; kind: "primary" | "secondary"; detail?: string };
export type CommandPayload = { title: string; detail: string; actions: FuturesMacroAction[] };
export type HeroPayload = {
  kicker: string;
  title: string;
  transition_label: string;
  summary: string;
  as_of_date: string;
  estimate_status: EstimateStatus;
  coverage_label: string;
  evidence: string[];
};
export type ProbabilityRow = { key: RegimeKey; label: string; value: number; baseline: number; lift: number };
export type HorizonCard = {
  key: "current" | "5D" | "20D";
  label: string;
  kind: "observation" | "conditional_outlook";
  title: string;
  summary: string;
  estimate_status: EstimateStatus;
  edge_label: string;
  probabilities: ProbabilityRow[];
  episode_count?: number;
  status_reason?: string;
};
export type PatternPoint = { date: string; x: number; y: number; regime: RegimeKey; regime_label: string; transition_label: string };
export type PatternZone = { horizon: "5D" | "20D"; regime: RegimeKey; center_x: number; center_y: number; radius_x: number; radius_y: number; probability: number };
export type PatternMapPayload = { title: string; x_label: string; y_label: string; path: PatternPoint[]; zones: PatternZone[] };
export type EvidenceGroup = { key: "current" | "transition" | "outlook" | "invalidate"; label: string; items: string[] };
export type EvidencePayload = { title: string; groups: EvidenceGroup[] };
export type RibbonItem = { date: string; regime: RegimeKey; regime_label: string; transition: string; transition_label: string };
export type RibbonPayload = { title: string; items: RibbonItem[] };
export type AssetPathwayPayload = {
  key: "risk_assets" | "rates" | "dollar" | "safe_haven" | "commodities";
  label: string;
  current: { one_day: string; five_day: string; twenty_day: string };
  outlook: { five_day: string; twenty_day: string };
  change_condition: string;
  estimate_status: EstimateStatus;
};
export type MethodPayload = {
  source: string;
  effective_episodes: string;
  brier: string;
  baseline_brier: string;
  calibration: string;
  caveats: string[];
};

export type FuturesMacroWorkbenchPayload = {
  schema_version: "futures_macro_react_workbench_v2";
  component: "FuturesMacroWorkbench";
  command: CommandPayload;
  hero: HeroPayload;
  horizons: HorizonCard[];
  pattern_map: PatternMapPayload;
  evidence: EvidencePayload;
  ribbon: RibbonPayload;
  asset_pathways: AssetPathwayPayload[];
  method: MethodPayload;
  action_boundary: "python_dispatch_only";
  boundary_note: string;
};
```

Render:

```tsx
<MacroContextSection hero={payload.hero} command={payload.command} onAction={emitAction} />
<PatternHorizonSection horizons={payload.horizons} />
<div className="fm-workbench__pattern-layout">
  <PatternMapSection patternMap={payload.pattern_map} />
  <CurrentEvidencePanel evidence={payload.evidence} />
</div>
<PatternRibbonSection ribbon={payload.ribbon} />
<AssetPathwaysSection pathways={payload.asset_pathways} />
<MethodDisclosure method={payload.method} boundaryNote={payload.boundary_note} />
```

- [ ] **Step 4: Implement horizon and probability cards**

`PatternHorizonSection.tsx` must:

- render current observation without probability bars;
- render 5D / 20D probabilities only when non-empty;
- show baseline and signed lift for each regime;
- display VERIFIED / PROVISIONAL / UNAVAILABLE badge;
- display `방향 우위 미확인` and status reason when no publishable edge.

Use semantic class names `estimate-verified`, `estimate-provisional`, `estimate-unavailable`, matching Economic Cycle colors.

```tsx
function ProbabilityBar({ row }: { row: ProbabilityRow }) {
  return (
    <div className="fm-workbench__probability-row">
      <span>{row.label}</span>
      <div><i style={{ width: `${Math.round(row.value * 100)}%` }} /></div>
      <strong>{Math.round(row.value * 100)}%</strong>
      <small>평소 {Math.round(row.baseline * 100)}% · {row.lift >= 0 ? "+" : ""}{Math.round(row.lift * 100)}%p</small>
    </div>
  );
}

export default function PatternHorizonSection({ horizons }: { horizons: HorizonCard[] }) {
  return (
    <section className="fm-workbench__horizon-section" aria-labelledby="fm-horizon-title">
      <div className="fm-workbench__section-heading">
        <div><span>Probability path</span><h3 id="fm-horizon-title">현재와 다음 1주·1개월</h3></div>
        <small>현재는 관측 · 미래는 조건부 분포</small>
      </div>
      <div className="fm-workbench__horizon-grid">
        {horizons.map((item) => (
          <article className={`fm-workbench__horizon-card estimate-${item.estimate_status.toLowerCase()}`} key={item.key}>
            <header><div><span>{item.label}</span><strong>{item.title}</strong></div><b>{item.estimate_status}</b></header>
            <p>{item.summary}</p>
            {item.kind === "conditional_outlook" && item.probabilities.length > 0
              ? item.probabilities.map((row) => <ProbabilityBar key={row.key} row={row} />)
              : <div className="fm-workbench__no-edge">{item.edge_label || "방향 우위 미확인"}</div>}
            {item.status_reason ? <small>{item.status_reason}</small> : null}
          </article>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 5: Implement pattern map probability zones**

`PatternMapSection.tsx` renders an SVG with:

```tsx
<polyline className="fm-pattern-map__observed" points={observedPoints} />
{patternMap.zones.map((zone) => (
  <ellipse
    className={`fm-pattern-map__zone horizon-${zone.horizon.toLowerCase()}`}
    cx={zone.center_x}
    cy={zone.center_y}
    rx={zone.radius_x}
    ry={zone.radius_y}
    opacity={Math.max(0.12, Math.min(0.58, zone.probability))}
    key={`${zone.horizon}-${zone.regime}`}
  />
))}
```

Do not connect current point to zone centers with a forecast line. Tooltip / focus text must identify `관측 경로` versus `조건부 결과 영역`.

- [ ] **Step 6: Implement ribbon, evidence, and asset pathways**

- Ribbon: recent 60 trading dates, regime color plus transition hatch; keyboard-focusable cells with date / regime / transition label.
- Evidence: four groups `현재 위치`, `지속·전환`, `전망 우위`, `바뀌는 조건`.
- Asset pathways: canonical order `주식 위험선호`, `금리 부담`, `달러 압력`, `안전자산`, `원자재·물가`; each shows current 1D / 5D / 20D, 5D / 20D auxiliary distribution, and one change condition.
- Method disclosure: source, effective episodes, Brier / baseline Brier, calibration, roll caveat, no-trade boundary.

`MethodDisclosure.tsx` owns the collapsed `<details>` block and renders `MethodPayload` without initiating Python actions.

```tsx
// PatternRibbonSection.tsx
import type { CSSProperties } from "react";
export function PatternRibbonSection({ ribbon }: { ribbon: RibbonPayload }) {
  return (
    <section className="fm-workbench__ribbon-section">
      <div className="fm-workbench__section-heading"><div><span>Regime path</span><h3>{ribbon.title}</h3></div></div>
      <div className="fm-workbench__ribbon" style={{ "--ribbon-count": Math.max(1, ribbon.items.length) } as CSSProperties}>
        {ribbon.items.map((item) => (
          <span
            className={`regime-${item.regime} transition-${item.transition}`}
            aria-label={`${item.date} · ${item.regime_label} · ${item.transition_label}`}
            key={item.date}
            role="img"
            tabIndex={0}
          />
        ))}
      </div>
    </section>
  );
}

// AssetPathwaysSection.tsx
export function AssetPathwaysSection({ pathways }: { pathways: AssetPathwayPayload[] }) {
  return (
    <section className="fm-workbench__asset-section">
      <div className="fm-workbench__section-heading"><div><span>Measured pathways</span><h3>자산별 확인 포인트</h3></div></div>
      <div className="fm-workbench__asset-grid">
        {pathways.map((item) => (
          <article key={item.key}>
            <header><strong>{item.label}</strong><b>{item.estimate_status}</b></header>
            <div className="fm-workbench__asset-current">
              <span>1D {item.current.one_day}</span>
              <span>5D {item.current.five_day}</span>
              <span>20D {item.current.twenty_day}</span>
            </div>
            <div className="fm-workbench__asset-outlook">
              <span>다음 5D {item.outlook.five_day}</span>
              <span>다음 20D {item.outlook.twenty_day}</span>
            </div>
            <p>{item.change_condition}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

// MethodDisclosure.tsx
export default function MethodDisclosure({ method, boundaryNote }: { method: MethodPayload; boundaryNote: string }) {
  return (
    <details className="fm-workbench__method">
      <summary>방법론과 품질</summary>
      <div className="fm-workbench__method-grid">
        <div><span>원천</span><strong>{method.source}</strong></div>
        <div><span>독립 표본</span><strong>{method.effective_episodes}</strong></div>
        <div><span>Brier</span><strong>{method.brier}</strong></div>
        <div><span>기준 Brier</span><strong>{method.baseline_brier}</strong></div>
        <div><span>확률 보정</span><strong>{method.calibration}</strong></div>
      </div>
      <ul>{method.caveats.map((item) => <li key={item}>{item}</li>)}</ul>
      <p>{boundaryNote}</p>
    </details>
  );
}
```

- [ ] **Step 7: Apply economic-cycle visual grammar and responsive CSS**

Reuse these design tokens rather than copying the entire stylesheet:

```css
.fm-workbench {
  --ink: #172536;
  --muted: #64768a;
  --line: #dbe4eb;
  --positive: #39a47f;
  --warning: #f0ad45;
  --danger: #d66f62;
  display: grid;
  gap: 20px;
  color: var(--ink);
}

.fm-workbench__hero {
  padding: 28px 30px;
  border: 1px solid #d9e5e8;
  border-radius: 23px;
  background: radial-gradient(circle at 90% 18%, rgba(79,143,199,.15), transparent 34%), linear-gradient(135deg,#f8fbfd,#f3f8f6);
  box-shadow: 0 16px 42px rgba(30,56,75,.07);
}

.fm-workbench__horizon-grid { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 13px; }
.fm-workbench__pattern-layout { display: grid; grid-template-columns: minmax(360px,.92fr) minmax(0,1.08fr); gap: 16px; }

@media (max-width: 760px) {
  .fm-workbench__horizon-grid,
  .fm-workbench__pattern-layout,
  .fm-workbench__asset-grid { grid-template-columns: 1fr; }
}
```

- [ ] **Step 8: Build component and run contracts**

```bash
cd app/web/streamlit_components/futures_macro_workbench
npm run build
cd ../../../../..
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'futures_macro_react or futures_macro_v2'
git diff --check
```

Expected: Vite build succeeds, selected tests pass, diff check is clean.

- [ ] **Step 9: Confirm retired sections are not active**

```bash
rg -n 'RecentFlowSection|HistoricalValidationPanel' app/web/streamlit_components/futures_macro_workbench/src
```

Expected: no imports or render calls from `FuturesMacroWorkbench.tsx`. If the only matches are the old files themselves, either delete those two source files and rebuild or retain them as unreferenced compatibility files; record the choice in task `NOTES.md`.

- [ ] **Step 10: Commit Task 6**

```bash
git add app/web/streamlit_components/futures_macro_workbench/src app/web/streamlit_components/futures_macro_workbench/component_static tests/test_service_contracts.py
git commit -m "선물 매크로 패턴 전망 화면 개편"
```

---

### Task 7: Actual Data QA, Performance Gate, Documentation Sync, And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/README.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Generated, do not stage: Browser QA screenshot and `.playwright-mcp/` artifacts.

**Interfaces:**
- Consumes: complete Python + React V2 implementation.
- Produces: measured actual publication state, latency evidence, desktop/mobile QA, durable ownership / flow docs, roadmap 5/5 closeout.

- [ ] **Step 1: Run complete focused Python verification**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern.py tests/test_futures_macro_pattern_validation.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'futures_macro or macro_thermometer or macro_validation'
.venv/bin/python -m py_compile app/services/futures_macro_pattern.py app/services/futures_macro_pattern_validation.py app/services/futures_macro_thermometer.py app/web/overview/futures_macro_helpers.py
git diff --check
```

Expected: all selected tests pass, compile exits 0, diff check clean.

- [ ] **Step 2: Measure actual local snapshot without mutating data**

Run a read-only script:

```python
from time import perf_counter
from app.services.futures_macro_pattern_validation import load_overview_futures_macro_pattern_outlook

started = perf_counter()
snapshot = load_overview_futures_macro_pattern_outlook(cache_ttl_seconds=0)
elapsed = perf_counter() - started
print({
    "status": snapshot.get("status"),
    "as_of_date": snapshot.get("as_of_date"),
    "regime": (snapshot.get("current_pattern") or {}).get("regime"),
    "transition": (snapshot.get("current_pattern") or {}).get("transition"),
    "horizons": [
        {
            "horizon": item.get("horizon"),
            "estimate_status": item.get("estimate_status"),
            "episode_count": item.get("episode_count"),
            "edge_label": item.get("edge_label"),
            "brier": item.get("brier_score"),
            "baseline_brier": item.get("baseline_brier_score"),
        }
        for item in snapshot.get("horizons") or []
    ],
    "elapsed_seconds": round(elapsed, 3),
})
```

Record exact output in task `RUNS.md`. Do not lower gates to turn an actual `UNAVAILABLE` / `PROVISIONAL` result into `VERIFIED`.

- [ ] **Step 3: Apply runtime performance stop condition**

- If uncached actual build ≤ 5 seconds and cached reload ≤ 0.5 seconds, keep default cached computation.
- If uncached build > 5 seconds, profile service functions and optimize vectorized calculation / cache key first.
- If it still exceeds 5 seconds, stop before adding DB schema; document a daily materialization proposal and request separate approval.

Add a regression test that two calls with the same marker return the identical cached object and a changed marker rebuilds once.

```python
def test_pattern_outlook_cache_reuses_same_marker_and_rebuilds_on_new_daily_row(monkeypatch):
    marker = {"value": "2026-07-17"}
    calls = []
    monkeypatch.setattr(service, "_latest_daily_cache_marker", lambda query, symbols: marker["value"])
    monkeypatch.setattr(service, "build_pattern_outlook_snapshot", lambda *args, **kwargs: calls.append(kwargs) or {"call": len(calls)})
    service.clear_futures_macro_pattern_validation_cache()
    first = service.load_overview_futures_macro_pattern_outlook(cache_ttl_seconds=60)
    second = service.load_overview_futures_macro_pattern_outlook(cache_ttl_seconds=60)
    marker["value"] = "2026-07-18"
    third = service.load_overview_futures_macro_pattern_outlook(cache_ttl_seconds=60)
    assert first is second
    assert third["call"] == 2
```

- [ ] **Step 4: Run Streamlit and perform Browser QA**

Start the repository’s existing Streamlit app command from the runbook/current task history. Verify:

- desktop: hero, 3 horizon cards, path map + evidence, ribbon, 5 asset pathways, method disclosure;
- mobile 420px: all primary sections stack to one column, no horizontal clipping;
- VERIFIED / PROVISIONAL / UNAVAILABLE badge is legible;
- unavailable probability shows no fabricated percentages;
- no `오늘과 비슷한 과거 흐름 확인` button;
- refresh / reload remain secondary actions;
- console errors 0;
- attach one desktop QA screenshot in the final response, do not stage it.

- [ ] **Step 5: Update task docs with measured facts**

Update:

- `STATUS.md`: stages 1~5 and exact completion state;
- `NOTES.md`: actual regime / transition, publication states, performance decision, retired component decision;
- `RUNS.md`: exact commands, pass counts, build output, Browser QA URL / screenshot;
- `RISKS.md`: remaining history / roll / calibration gaps only.

- [ ] **Step 6: Synchronize durable finance docs**

Use `finance-doc-sync` during execution and make these exact durable changes:

- `flows/README.md`: replace `Recent Flow + lazy Historical Validation` with `today shock -> multi-window current pattern -> default 5D / 20D conditional outlook -> method disclosure`.
- `architecture/README.md`: record `futures_macro_pattern.py` and `futures_macro_pattern_validation.py` as Streamlit-free services.
- `PROJECT_MAP.md`: include the two new services and four React sections in Overview Futures Macro ownership.
- root logs: 3~5 line milestone / decision / handoff only, pointing to this active task.

- [ ] **Step 7: Run final verification after docs**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_pattern.py tests/test_futures_macro_pattern_validation.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'futures_macro or macro_thermometer or macro_validation'
(cd app/web/streamlit_components/futures_macro_workbench && npm run build)
.venv/bin/python -m py_compile app/services/futures_macro_pattern.py app/services/futures_macro_pattern_validation.py app/services/futures_macro_thermometer.py app/web/overview/futures_macro_helpers.py
git diff --check
git status --short
```

Expected: tests pass, build succeeds, compile exits 0, diff check clean, only intended files plus pre-existing unrelated untracked paths appear.

- [ ] **Step 8: Commit closeout**

```bash
git add .aiworkspace/note/finance/docs/flows/README.md .aiworkspace/note/finance/docs/architecture/README.md .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718
git commit -m "선물 매크로 패턴 전망 검증과 문서 정리"
```

Do not stage the QA screenshot, `.playwright-mcp/`, registries, saved setups, run history, or unrelated research.

---

## Implementation Completion Checklist

- [x] Task 1: point-in-time multi-window feature frame
- [ ] Task 2: current regime / transition / path / change conditions
- [ ] Task 3: forward outcomes / independent similar episodes
- [ ] Task 4: chronological validation / publication gate / cache
- [ ] Task 5: default service integration / Python React payload V2
- [ ] Task 6: Market Context-style React workbench V2 / build
- [ ] Task 7: actual QA / performance gate / docs sync / closeout

## Overall Roadmap State

- 1차 설계 계약: approved and committed (`c207690b`)
- 2차 상세 구현 계획: this document
- 3차 service / validation implementation: pending execution
- 4차 React UI implementation: pending execution
- 5차 actual QA / docs closeout: pending execution
