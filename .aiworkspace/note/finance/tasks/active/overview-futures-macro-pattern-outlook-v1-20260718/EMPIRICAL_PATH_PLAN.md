# Futures Macro Empirical Conditional Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This session does not delegate to subagents.

**Goal:** 고정 체제 분기를 과거 유사 episode의 step별 중앙 이동과 가운데 50% 범위로 교체해 5D와 20D가 실제로 다른 조건부 경로를 표시하게 한다.

**Architecture:** validation service가 as-of volatility로 표준화한 각 episode의 2차원 stepwise forward movement와 시간순 path validation을 소유한다. Overview helper는 `conditional_path`를 숫자 정규화만 해 React에 전달하고, Pattern Map은 기존 관측 anchor와 probability reading을 유지한 채 중앙 점선·희박한 50% 범위·terminal marker를 렌더링한다.

**Tech Stack:** Python 3.11+, pandas, unittest, React 18, TypeScript 5.7, SVG, Vite 6, Streamlit component bridge.

## Global Constraints

- current coordinate는 기존 `risk_on 5D z / macro pressure 5D z`를 유지한다.
- forecast coordinate는 `current coordinate + historical analog median forward delta`다.
- episode origin의 60D volatility만 사용하며 current 이후 실제 데이터는 forecast 계산에 사용하지 않는다.
- 5D / 20D 독립 episode spacing과 기존 30 / 60 publication threshold를 낮추지 않는다.
- conditional path status는 probability estimate status보다 강할 수 없다.
- fixed regime target, supervised model, provider, DB schema, registry, saved setup, price target, trading signal을 추가하지 않는다.
- probability horizon cards와 우측 probability reading은 유지한다.
- actual Browser QA에서 5D / 20D SVG forecast coordinates가 달라야 한다.
- unrelated untracked research와 `.superpowers/`는 수정하거나 stage하지 않는다.

## File Structure

- `app/services/futures_macro_pattern_validation.py`: stepwise coordinate frame, conditional path aggregate, walk-forward path metrics, conservative status.
- `tests/test_futures_macro_pattern_validation.py`: coordinate, leakage, aggregate, insufficient sample, chronological validation tests.
- `app/web/overview/futures_macro_helpers.py`: conditional path payload normalization and unavailable suppression.
- `tests/test_service_contracts.py`: V2 payload and React source contracts.
- `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`: conditional path types.
- `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`: empirical path, uncertainty checkpoints, terminal position.
- `app/web/streamlit_components/futures_macro_workbench/src/style.css`: conditional path visual grammar.
- Active task docs plus the smallest durable Futures Macro flow / architecture / project-map set: QA and closeout.

---

### Task 1: Stepwise Historical Coordinate Paths

**Files:**
- Modify: `tests/test_futures_macro_pattern_validation.py`
- Modify: `app/services/futures_macro_pattern_validation.py`

**Interfaces:**
- Consumes: normalized candle frame, feature frame, `SCORE_DEFINITIONS`.
- Produces: `build_forward_coordinate_frame(candles, feature_frame, *, selected_symbols) -> pd.DataFrame` with `as_of_date`, `horizon`, `step`, `delta_x`, `delta_y`.
- Produces: `_conditional_path_payload(selected_paths, *, current_location, horizon, episode_count, status, validation) -> dict[str, Any]`.

- [ ] **Step 1: Write coordinate RED tests**

```python
def test_forward_coordinate_frame_has_5d_and_20d_steps(self) -> None:
    from app.services.futures_macro_pattern_validation import build_forward_coordinate_frame

    candles, features = _validation_fixture(days=180)
    coordinates = build_forward_coordinate_frame(candles, features, selected_symbols=SYMBOLS)
    completed = coordinates.dropna(subset=["delta_x", "delta_y"])
    counts = completed.groupby(["as_of_date", "horizon"])["step"].nunique()

    self.assertTrue({5, 20}.issubset(set(coordinates["horizon"])))
    self.assertTrue((counts[counts.index.get_level_values("horizon") == 5] <= 5).all())
    self.assertTrue((counts[counts.index.get_level_values("horizon") == 20] <= 20).all())
    self.assertTrue(coordinates["step"].ge(1).all())


def test_completed_coordinate_path_is_stable_after_later_rows_are_appended(self) -> None:
    from app.services.futures_macro_pattern_validation import build_forward_coordinate_frame

    base_candles, base_features = _validation_fixture(days=160)
    more_candles, more_features = _validation_fixture(days=180)
    before = build_forward_coordinate_frame(base_candles, base_features, selected_symbols=SYMBOLS)
    after = build_forward_coordinate_frame(more_candles, more_features, selected_symbols=SYMBOLS)
    origin = before[(before["horizon"] == 20) & before["delta_x"].notna()]["as_of_date"].iloc[-25]
    left = before[(before["as_of_date"] == origin) & (before["horizon"] == 20)].reset_index(drop=True)
    right = after[(after["as_of_date"] == origin) & (after["horizon"] == 20)].reset_index(drop=True)

    pd.testing.assert_frame_equal(left, right)
```

- [ ] **Step 2: Run coordinate RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern_validation.FuturesMacroPatternOutcomeTests -v
```

Expected: both new tests fail because `build_forward_coordinate_frame` is absent.

- [ ] **Step 3: Implement reusable step frames and coordinate frame**

```python
def _forward_family_step_frame(
    *,
    close: pd.DataFrame,
    as_of_volatility: pd.DataFrame,
    horizon: int,
    definition: ScoreDefinition,
) -> pd.DataFrame:
    member_columns = [symbol for symbol in definition.members if symbol in close.columns]
    if not member_columns:
        return pd.DataFrame(index=close.index, columns=range(1, int(horizon) + 1), dtype=float)
    output = pd.DataFrame(index=close.index)
    for step in range(1, int(horizon) + 1):
        forward_return = close[member_columns].shift(-step).divide(close[member_columns]).sub(1.0)
        scale = as_of_volatility[member_columns].mul(step**0.5).replace(0, pd.NA)
        scaled = forward_return.divide(scale)
        weighted = pd.concat(
            [scaled[symbol].mul(float(definition.members[symbol])) for symbol in member_columns],
            axis=1,
        )
        output[step] = weighted.mean(axis=1, skipna=True)
    return output


def build_forward_coordinate_frame(
    candles: pd.DataFrame,
    feature_frame: pd.DataFrame,
    *,
    selected_symbols: Sequence[str],
) -> pd.DataFrame:
    columns = ["as_of_date", "horizon", "step", "delta_x", "delta_y"]
    close = _pattern_close_matrix(candles, selected_symbols)
    if close.empty or feature_frame.empty:
        return pd.DataFrame(columns=columns)
    returns = close.pct_change(fill_method=None)
    volatility = returns.rolling(60, min_periods=60).std(ddof=0)
    definitions = {SCORE_TO_FAMILY_KEY[item.name]: item for item in SCORE_DEFINITIONS}
    rows: list[dict[str, Any]] = []
    origins = feature_frame.index.intersection(close.index)
    for horizon in OUTLOOK_HORIZONS:
        frames = {
            family: _forward_family_step_frame(
                close=close,
                as_of_volatility=volatility,
                horizon=horizon,
                definition=definition,
            )
            for family, definition in definitions.items()
        }
        for origin in origins:
            for step in range(1, horizon + 1):
                pressure = pd.Series(
                    [frames[family].at[origin, step] for family in ("rate_pressure", "dollar_pressure", "inflation_pressure")],
                    dtype=float,
                ).dropna()
                risk_on = frames["risk_on"].at[origin, step]
                rows.append({
                    "as_of_date": pd.Timestamp(origin),
                    "horizon": horizon,
                    "step": step,
                    "delta_x": float(risk_on) if pd.notna(risk_on) else None,
                    "delta_y": float(pressure.mean()) if not pressure.empty else None,
                })
    return pd.DataFrame(rows, columns=columns).sort_values(["as_of_date", "horizon", "step"]).reset_index(drop=True)
```

Refactor `_forward_path_stat_frame()` to call `_forward_family_step_frame()` and preserve existing parity tests.

- [ ] **Step 4: Write aggregate RED tests**

```python
def test_conditional_path_uses_step_medians_and_middle_fifty_percent(self) -> None:
    from app.services.futures_macro_pattern_validation import _conditional_path_payload

    selected = pd.DataFrame([
        {"step": 1, "delta_x": 0.0, "delta_y": -1.0},
        {"step": 1, "delta_x": 2.0, "delta_y": 1.0},
        {"step": 2, "delta_x": 1.0, "delta_y": 0.0},
        {"step": 2, "delta_x": 3.0, "delta_y": 2.0},
    ])
    result = _conditional_path_payload(
        selected,
        current_location={"x": -0.5, "y": 0.5},
        horizon=2,
        episode_count=40,
        status="PROVISIONAL",
        validation={},
    )

    self.assertEqual(len(result["points"]), 2)
    self.assertAlmostEqual(result["points"][0]["x"], 0.5)
    self.assertAlmostEqual(result["points"][0]["y"], 0.5)
    self.assertLess(result["points"][0]["lower_x"], result["points"][0]["upper_x"])
    self.assertEqual(result["terminal"], result["points"][-1])


def test_conditional_path_hides_coordinates_below_minimum_sample(self) -> None:
    from app.services.futures_macro_pattern_validation import _conditional_path_payload

    result = _conditional_path_payload(
        pd.DataFrame([{"step": 1, "delta_x": 0.1, "delta_y": 0.2}]),
        current_location={"x": 0.0, "y": 0.0},
        horizon=5,
        episode_count=29,
        status="UNAVAILABLE",
        validation={},
    )

    self.assertEqual(result["points"], [])
    self.assertIsNone(result["terminal"])
```

- [ ] **Step 5: Run aggregate RED and implement aggregate**

After confirming the missing helper failure, implement:

```python
def _conditional_path_payload(
    selected_paths: pd.DataFrame,
    *,
    current_location: dict[str, Any],
    horizon: int,
    episode_count: int,
    status: str,
    validation: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "status": str(status),
        "episode_count": int(episode_count),
        "band_label": "과거 유사 패턴 가운데 50%",
        "validation": dict(validation),
    }
    if str(status) == "UNAVAILABLE" or episode_count < MIN_INDEPENDENT_EPISODES or selected_paths.empty:
        return {**base, "status": "UNAVAILABLE", "points": [], "terminal": None}
    current_x = float(current_location.get("x") or 0.0)
    current_y = float(current_location.get("y") or 0.0)
    points: list[dict[str, float | int]] = []
    for step, rows in selected_paths.groupby("step", sort=True):
        x_values = pd.to_numeric(rows["delta_x"], errors="coerce").dropna()
        y_values = pd.to_numeric(rows["delta_y"], errors="coerce").dropna()
        if x_values.empty or y_values.empty:
            continue
        points.append({
            "step": int(step),
            "x": current_x + float(x_values.median()),
            "y": current_y + float(y_values.median()),
            "lower_x": current_x + float(x_values.quantile(0.25)),
            "upper_x": current_x + float(x_values.quantile(0.75)),
            "lower_y": current_y + float(y_values.quantile(0.25)),
            "upper_y": current_y + float(y_values.quantile(0.75)),
        })
    if len(points) < max(1, (int(horizon) + 1) // 2):
        return {**base, "status": "UNAVAILABLE", "points": [], "terminal": None}
    return {**base, "points": points, "terminal": points[-1]}
```

- [ ] **Step 6: Run GREEN and commit**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern_validation.FuturesMacroPatternOutcomeTests -v
.venv/bin/python -m unittest tests.test_futures_macro_pattern -q
.venv/bin/python -m py_compile app/services/futures_macro_pattern_validation.py
git diff --check
git add app/services/futures_macro_pattern_validation.py tests/test_futures_macro_pattern_validation.py
git commit -m "선물 매크로 경험적 경로 계산 추가"
```

Expected: tests pass and checks exit 0 before the commit.

---

### Task 2: Chronological Path Validation And Horizon Integration

**Files:**
- Modify: `tests/test_futures_macro_pattern_validation.py`
- Modify: `app/services/futures_macro_pattern_validation.py`

**Interfaces:**
- Consumes: coordinate frame, walk-forward folds, similar episode dates.
- Produces: `_walk_forward_path_metrics(*, feature_frame: pd.DataFrame, coordinates: pd.DataFrame, horizon: int) -> dict[str, float | int | None]`.
- Produces: `path_publication_status(*, episode_count, median_error, baseline_median_error, coverage_50, evaluated_fold_count) -> str` and horizon `conditional_path`.

- [ ] **Step 1: Write validation RED tests**

```python
def test_path_status_requires_error_improvement_coverage_and_two_folds(self) -> None:
    from app.services.futures_macro_pattern_validation import path_publication_status

    cases = (
        (29, 0.5, 0.8, 0.5, 3, "UNAVAILABLE"),
        (40, 0.5, 0.8, 0.5, 3, "PROVISIONAL"),
        (60, 0.5, 0.8, 0.5, 2, "VERIFIED"),
        (60, 0.9, 0.8, 0.5, 3, "PROVISIONAL"),
        (60, 0.5, 0.8, 0.8, 3, "PROVISIONAL"),
    )
    for episodes, error, baseline, coverage, folds, expected in cases:
        with self.subTest(episodes=episodes, error=error, coverage=coverage):
            self.assertEqual(path_publication_status(episode_count=episodes, median_error=error, baseline_median_error=baseline, coverage_50=coverage, evaluated_fold_count=folds), expected)


def test_outlook_attaches_distinct_horizon_conditional_paths(self) -> None:
    from app.services.futures_macro_pattern_validation import build_pattern_outlook_snapshot

    snapshot = build_pattern_outlook_snapshot(**_outlook_fixture(days=300))
    paths = {item["horizon"]: item["conditional_path"] for item in snapshot["horizons"]}

    self.assertEqual(len(paths[5]["points"]), 5)
    self.assertEqual(len(paths[20]["points"]), 20)
    self.assertNotEqual(paths[5]["terminal"], paths[20]["terminal"])
    self.assertIn(paths[5]["status"], {"VERIFIED", "PROVISIONAL"})
```

- [ ] **Step 2: Run RED**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern_validation.FuturesMacroPatternPublicationTests -v
```

Expected: missing status function and missing `conditional_path` failures.

- [ ] **Step 3: Implement path metrics and status**

```python
def _euclidean_error(actual_x: float, actual_y: float, predicted_x: float, predicted_y: float) -> float:
    return float(((actual_x - predicted_x) ** 2 + (actual_y - predicted_y) ** 2) ** 0.5)


def path_publication_status(
    *,
    episode_count: int,
    median_error: float | None,
    baseline_median_error: float | None,
    coverage_50: float | None,
    evaluated_fold_count: int,
) -> str:
    if episode_count < MIN_INDEPENDENT_EPISODES:
        return "UNAVAILABLE"
    verified = (
        episode_count >= VERIFIED_EPISODES
        and median_error is not None
        and baseline_median_error is not None
        and median_error < baseline_median_error
        and coverage_50 is not None
        and 0.35 <= coverage_50 <= 0.65
        and evaluated_fold_count >= 2
    )
    return "VERIFIED" if verified else "PROVISIONAL"
```

Implement `_walk_forward_path_metrics()` with completed train rows only:

```python
def _walk_forward_path_metrics(
    *,
    feature_frame: pd.DataFrame,
    coordinates: pd.DataFrame,
    horizon: int,
) -> dict[str, float | int | None]:
    terminal = coordinates[
        (coordinates["horizon"] == horizon)
        & (coordinates["step"] == horizon)
    ].dropna(subset=["delta_x", "delta_y"])
    errors: list[float] = []
    baseline_errors: list[float] = []
    coverage_rows: list[float] = []
    evaluated_folds = 0
    for fold in build_walk_forward_folds(feature_frame, horizon=horizon):
        train = terminal[terminal["as_of_date"] <= fold.train_end]
        test = terminal[
            (terminal["as_of_date"] >= fold.test_start)
            & (terminal["as_of_date"] <= fold.test_end)
        ].iloc[:: max(1, horizon)]
        if train.empty or test.empty:
            continue
        fold_predictions = 0
        baseline_x = float(train["delta_x"].median())
        baseline_y = float(train["delta_y"].median())
        for _, actual in test.iterrows():
            test_date = pd.Timestamp(actual["as_of_date"])
            matches = select_similar_episodes(
                feature_frame,
                current_date=test_date,
                horizon=horizon,
            )
            analogs = matches.merge(
                train[["as_of_date", "delta_x", "delta_y"]],
                on="as_of_date",
                how="inner",
            )
            if len(analogs) < 10:
                continue
            lower_x, predicted_x, upper_x = analogs["delta_x"].quantile([0.25, 0.5, 0.75]).tolist()
            lower_y, predicted_y, upper_y = analogs["delta_y"].quantile([0.25, 0.5, 0.75]).tolist()
            actual_x = float(actual["delta_x"])
            actual_y = float(actual["delta_y"])
            errors.append(_euclidean_error(actual_x, actual_y, predicted_x, predicted_y))
            baseline_errors.append(_euclidean_error(actual_x, actual_y, baseline_x, baseline_y))
            coverage_rows.append(float(lower_x <= actual_x <= upper_x and lower_y <= actual_y <= upper_y))
            fold_predictions += 1
        evaluated_folds += int(fold_predictions > 0)
    return {
        "median_error": float(pd.Series(errors).median()) if errors else None,
        "baseline_median_error": float(pd.Series(baseline_errors).median()) if baseline_errors else None,
        "coverage_50": float(sum(coverage_rows) / len(coverage_rows)) if coverage_rows else None,
        "evaluated_fold_count": evaluated_folds,
    }
```

- [ ] **Step 4: Integrate horizon paths**

Compute coordinates once in `build_pattern_outlook_snapshot()`. Extend `_build_horizon_outlook()` with `coordinates` and `current_location`. For each horizon, inner-join selected episode dates with that horizon's coordinate rows, compute path metrics/status, choose the more conservative of probability and path status, and attach:

```python
conditional_path = _conditional_path_payload(
    selected_paths,
    current_location=current_location,
    horizon=horizon,
    episode_count=episode_count,
    status=conditional_status,
    validation=path_metrics,
)
```

Every unavailable horizon returns `conditional_path` with status `UNAVAILABLE`, empty points, and `terminal=None`.

- [ ] **Step 5: Run GREEN, measure, and commit**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern_validation -v
.venv/bin/python -m unittest tests.test_futures_macro_pattern -q
.venv/bin/python -m py_compile app/services/futures_macro_pattern_validation.py
git diff --check
git add app/services/futures_macro_pattern_validation.py tests/test_futures_macro_pattern_validation.py
git commit -m "선물 매크로 경로 시간순 검증 연결"
```

Expected: all pattern tests pass. Measure uncached actual snapshot time and record it in `RUNS.md`; profile before UI work if it exceeds 10 seconds.

---

### Task 3: Payload And Empirical Path UI

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`

**Interfaces:**
- Consumes: horizon `conditional_path` and existing probability rows.
- Produces: normalized `HorizonCard.conditional_path`, empirical SVG path, three uncertainty checkpoints, terminal label.

- [ ] **Step 1: Write payload RED tests**

Extend `_pattern_outlook_payload_fixture()` with deterministic 5-point / 20-point conditional paths. Add assertions that normalized horizon cards preserve point counts and distinct terminals. For unavailable fixture assert empty points and `terminal is None`.

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_v2_payload_hides_unavailable_probabilities -v
```

Expected: `conditional_path` is absent from normalized cards.

- [ ] **Step 2: Implement Python normalization**

Add `_future_conditional_path(item, status)`:

```python
def _future_conditional_path(item: dict[str, Any], status: str) -> dict[str, Any]:
    raw = dict(item.get("conditional_path") or {})
    path_status = str(raw.get("status") or "UNAVAILABLE")
    base = {
        "status": path_status,
        "episode_count": int(raw.get("episode_count") or item.get("episode_count") or 0),
        "band_label": _display_text(raw.get("band_label"), "과거 유사 패턴 가운데 50%"),
        "validation": dict(raw.get("validation") or {}),
    }
    if status == "UNAVAILABLE" or path_status == "UNAVAILABLE":
        return {**base, "status": "UNAVAILABLE", "points": [], "terminal": None}
    coordinate_keys = ("x", "y", "lower_x", "upper_x", "lower_y", "upper_y")
    points: list[dict[str, Any]] = []
    for raw_point in list(raw.get("points") or []):
        point = dict(raw_point or {})
        if point.get("step") is None or any(point.get(key) is None for key in coordinate_keys):
            continue
        points.append({
            "step": int(point["step"]),
            **{key: float(point[key]) for key in coordinate_keys},
        })
    return {
        **base,
        "points": points,
        "terminal": points[-1] if points else None,
    }
```

Attach it as `conditional_path` in `_future_pattern_horizon()` without changing probability rows.

- [ ] **Step 3: Write React source RED**

Update the focused source contract to require `ConditionalPathPayload`, `fm-pattern-map__conditional-path`, `fm-pattern-map__uncertainty`, `유사 패턴 중앙 위치`, and `selectedCard?.conditional_path`; reject `REGIME_TARGETS`, `function Branch`, and `fm-pattern-map__outcome-dot`.

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches -v
```

Expected: the old branch component fails the new contract.

- [ ] **Step 4: Add TypeScript types**

```typescript
export type ConditionalPathPoint = {
  step: number; x: number; y: number;
  lower_x: number; upper_x: number; lower_y: number; upper_y: number;
};
export type ConditionalPathPayload = {
  status: EstimateStatus;
  episode_count: number;
  band_label: string;
  points: ConditionalPathPoint[];
  terminal?: ConditionalPathPoint | null;
  validation?: Record<string, number | null>;
};
```

Add `conditional_path?: ConditionalPathPayload` to `HorizonCard`.

- [ ] **Step 5: Replace fixed branches with empirical render**

In `PatternMapSection.tsx` remove `REGIME_TARGETS` and `Branch`. Read only the selected card's path and build bounds and SVG coordinates as follows:

```typescript
const conditionalPath = selectedCard?.kind === "conditional_outlook" ? selectedCard.conditional_path : undefined;
const forecastPoints = conditionalPath?.status !== "UNAVAILABLE" ? conditionalPath?.points || [] : [];
const xValues = [
  ...anchors.map((point) => point.x),
  ...forecastPoints.flatMap((point) => [point.x, point.lower_x, point.upper_x]),
];
const yValues = [
  ...anchors.map((point) => point.y),
  ...forecastPoints.flatMap((point) => [point.y, point.lower_y, point.upper_y]),
];
const xBound = Math.max(1.25, ...xValues.map((value) => Math.abs(value) * 1.12));
const yBound = Math.max(1.1, ...yValues.map((value) => Math.abs(value) * 1.12));
const forecastPolyline = latest
  ? [`${sx(latest.x)},${sy(latest.y)}`, ...forecastPoints.map((point) => `${sx(point.x)},${sy(point.y)}`)].join(" ")
  : "";
const midpointStep = Math.ceil(forecastPoints.length / 2);
const uncertaintySteps = forecastPoints.filter((point) =>
  point.step === 1 || point.step === midpointStep || point.step === forecastPoints.length
);
```

Render three sparse 50% rectangles, the median dotted line, and terminal marker:

```tsx
{uncertaintySteps.map((point) => (
  <rect
    className="fm-pattern-map__uncertainty"
    data-forecast-step={point.step}
    key={`uncertainty-${selectedHorizon}-${point.step}`}
    x={sx(point.lower_x)}
    y={sy(point.upper_y)}
    width={Math.max(2, sx(point.upper_x) - sx(point.lower_x))}
    height={Math.max(2, sy(point.lower_y) - sy(point.upper_y))}
    rx="10"
  />
))}
{forecastPolyline ? (
  <polyline
    className="fm-pattern-map__conditional-path"
    data-horizon={selectedHorizon}
    points={forecastPolyline}
  />
) : null}
{conditionalPath?.terminal ? (
  <g className="fm-pattern-map__terminal">
    <circle cx={sx(conditionalPath.terminal.x)} cy={sy(conditionalPath.terminal.y)} r="8" />
    <text x={sx(conditionalPath.terminal.x)} y={sy(conditionalPath.terminal.y) - 14} textAnchor="middle">
      유사 패턴 중앙 위치
    </text>
  </g>
) : null}
```

Keep the existing probability `<dl>` in the right reading. Update legend/copy to `조건부 중앙 경로`, `가운데 50% 범위`, and `실제 미래 경로가 아닙니다`.

- [ ] **Step 6: Add CSS and remove obsolete selectors**

```css
.fm-pattern-map__uncertainty { fill: rgba(111, 167, 202, 0.14); stroke: rgba(57, 125, 168, 0.28); stroke-width: 1; }
.fm-pattern-map__conditional-path { fill: none; stroke: #397da8; stroke-dasharray: 7 7; stroke-linecap: round; stroke-linejoin: round; stroke-width: 3; }
.fm-pattern-map__terminal circle { fill: #e5f0f6; stroke: #397da8; stroke-width: 3; }
.fm-pattern-map__terminal text { fill: #40566a; font-size: 11px; font-weight: 800; paint-order: stroke; stroke: #fff; stroke-width: 4px; }
```

Delete active branch/outcome and regime-specific branch selectors.

- [ ] **Step 7: Run GREEN, build, and commit**

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_v2_payload_hides_unavailable_probabilities tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches -v
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py
git diff --check
git add app/web/overview/futures_macro_helpers.py app/web/streamlit_components/futures_macro_workbench tests/test_service_contracts.py
git commit -m "선물 매크로 경험적 예측 경로 UI 적용"
```

Expected: focused contracts pass, Vite build exits 0, compile and diff check are clean.

---

### Task 4: Actual QA, Documentation Sync, And Closeout

**Files:**
- Modify: active task docs.
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`.
- Modify: `.aiworkspace/note/finance/docs/architecture/README.md`.
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`.
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`.
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`.

**Interfaces:**
- Consumes: completed service/payload/UI implementation.
- Produces: actual evidence, responsive screenshot, durable ownership and semantic documentation.

- [ ] **Step 1: Run complete focused verification**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
.venv/bin/python -m py_compile app/services/futures_macro_pattern_validation.py app/web/overview/futures_macro_helpers.py
git diff --check
```

Expected: Futures Macro suites pass. If the known unrelated Sentiment source-string contract remains, record it exactly and separately confirm every Futures Macro-selected contract passes.

- [ ] **Step 2: Inspect actual snapshot**

Record both horizons' estimate status, path status, episode count, point count, terminal x/y and bounds, four path-validation metrics, and uncached/cached runtime. Confirm 5D has five points, 20D has twenty, values are finite, and terminals differ.

- [ ] **Step 3: Browser QA**

At desktop and 420px verify:

- `관측만`: forecast path 0, uncertainty 0.
- `다음 5D`: forecast path 1, five-point data, terminal 1.
- `다음 20D`: forecast path 1, twenty-point data, terminal 1.
- 5D / 20D polyline points differ and probability reading changes.
- root `clientWidth == scrollWidth`; console errors 0.

Save one unstaged desktop screenshot under `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/`.

- [ ] **Step 4: Synchronize docs**

Record `observed anchors + historical-analog conditional median path + middle-50% range`, the `current location + standardized conditional movement` coordinate meaning, and separate conservative probability/path status. Keep root handoff entries at 3~5 lines and detailed metrics in task `RUNS.md` / `RISKS.md`.

- [ ] **Step 5: Re-run fresh verification and commit**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
.venv/bin/python -m py_compile app/services/futures_macro_pattern_validation.py app/web/overview/futures_macro_helpers.py
git diff --check
git status --short
git add app .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md tests/test_futures_macro_pattern_validation.py tests/test_service_contracts.py
git commit -m "선물 매크로 경험적 경로 검증과 문서 정리"
```

Expected: tests/build/checks pass before commit; generated screenshot and unrelated untracked paths remain unstaged.

## Completion Checklist

- [ ] Task 1: stepwise historical coordinate paths.
- [ ] Task 2: chronological path validation and horizon integration.
- [ ] Task 3: payload and empirical path UI.
- [ ] Task 4: actual QA, documentation sync, and closeout.

## Overall Roadmap State

- 1차 empirical path 설계: approved and committed (`5ad4eed5`).
- 2차 detailed TDD plan: this document.
- 3차 service / validation: pending.
- 4차 payload / React UI: pending.
- 5차 actual QA / docs closeout: pending.
