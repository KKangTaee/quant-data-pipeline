"""Train, validate, and materialize point-in-time economic-cycle results."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, replace
from datetime import date, datetime
from typing import Any, Callable, Mapping, Sequence

import pandas as pd

from finance.data.economic_cycle_results import (
    CycleSnapshot,
    HorizonProbability,
    deserialize_horizon_model_artifact,
    serialize_horizon_model_artifact,
    upsert_cycle_model_artifact,
    upsert_cycle_snapshots,
)
from finance.economic_cycle_catalog import get_economic_cycle_catalog
from finance.economic_cycle_features import build_monthly_feature_panel
from finance.economic_cycle_labels import build_retrospective_phase_labels
from finance.economic_cycle_model import (
    HORIZONS,
    PHASES,
    HorizonModelArtifact,
    apply_temperature,
    blend_likelihood_and_transition,
    estimate_transition_matrix,
    explain_phase_prediction,
    fit_forecast_models,
    fit_temperature,
    predict_phase_probabilities,
)
from finance.economic_cycle_validation import (
    PublicationDecision,
    ValidationReport,
    evaluate_publication_gate,
    run_rolling_origin_validation,
)
from finance.loaders.economic_cycle import (
    load_economic_cycle_vintage_history,
    load_economic_cycle_vintages,
    load_latest_approved_cycle_artifact,
)

FEATURE_SCHEMA_VERSION = "economic_cycle_features_v1"
MODEL_FAMILY = "economic-cycle-v1"
DEFAULT_HISTORY_START = date(1959, 1, 31)


def _as_date(value: object, *, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc


def month_end_origins(
    start_date: str | date,
    end_date: str | date,
) -> tuple[date, ...]:
    """Return inclusive month-end origins with stable calendar semantics."""

    start = _as_date(start_date, field="start_date")
    end = _as_date(end_date, field="end_date")
    if start > end:
        raise ValueError("start_date must be earlier than or equal to end_date")
    return tuple(
        timestamp.date() for timestamp in pd.date_range(start=start, end=end, freq="ME")
    )


def _json_safe(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (date, datetime, pd.Timestamp)):
        return pd.Timestamp(value).date().isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(
        _json_safe(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


class EconomicCyclePipelineLoader:
    """Default DB-only loader with one strict vintage read cached per origin."""

    def __init__(self, *, history_start: date = DEFAULT_HISTORY_START) -> None:
        self.history_start = history_start
        self._origin_rows: dict[str, list[dict[str, object]]] = {}
        self._panel_cache_cutoff: date | None = None
        self._panel_cache: pd.DataFrame | None = None

    def remember_origin(
        self,
        origin: str | date,
        rows: Sequence[Mapping[str, object]],
    ) -> None:
        key = _as_date(origin, field="origin").isoformat()
        self._origin_rows[key] = [dict(row) for row in rows]

    def load_for_origin(self, origin: str | date) -> list[dict[str, object]]:
        resolved = _as_date(origin, field="origin")
        key = resolved.isoformat()
        if key not in self._origin_rows:
            self._origin_rows[key] = load_economic_cycle_vintages(
                [item.series_id for item in get_economic_cycle_catalog()],
                start_date=self.history_start,
                end_date=resolved,
                as_of_date=resolved,
            )
        return [dict(row) for row in self._origin_rows[key]]

    def _panel_through(self, cutoff: date) -> pd.DataFrame:
        if (
            self._panel_cache is not None
            and self._panel_cache_cutoff is not None
            and self._panel_cache_cutoff >= cutoff
        ):
            origins = pd.to_datetime(
                self._panel_cache["forecast_origin"], errors="coerce"
            )
            return self._panel_cache.loc[
                origins <= pd.Timestamp(cutoff)
            ].reset_index(drop=True).copy()
        return self.prime_panel(cutoff)

    def prime_panel(self, cutoff: str | date) -> pd.DataFrame:
        """Build one bounded PIT panel and reuse safe prefixes during replay."""

        resolved_cutoff = _as_date(cutoff, field="cutoff")
        origins = month_end_origins(self.history_start, resolved_cutoff)
        rows = load_economic_cycle_vintage_history(
            [item.series_id for item in get_economic_cycle_catalog()],
            start_date=self.history_start,
            end_date=resolved_cutoff,
            as_of_date=resolved_cutoff,
        )
        panel = build_monthly_feature_panel(
            rows,
            get_economic_cycle_catalog(),
            forecast_origins=origins,
        )
        self._panel_cache_cutoff = resolved_cutoff
        self._panel_cache = panel.reset_index(drop=True).copy()
        return self._panel_cache.copy()

    def load_training_data(
        self,
        trained_through: str | date,
    ) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
        cutoff = _as_date(trained_through, field="trained_through")
        panel = self._panel_through(cutoff)
        training_labels = build_retrospective_phase_labels(
            panel, label_as_of_date=cutoff
        )
        # Scoring truth is an explicit output even when the current default uses
        # the same PIT label frame. Alternate loaders can provide final truth.
        return panel, training_labels, training_labels.copy()

    def load_prediction_data(self, as_of_date: str | date) -> dict[str, object]:
        cutoff = _as_date(as_of_date, field="as_of_date")
        panel = self._panel_through(cutoff)
        if panel.empty:
            raise LookupError(f"No economic-cycle features available for {cutoff}")
        return panel.iloc[-1].to_dict()

    def load_artifact(
        self,
        *,
        as_of_date: str | date,
        model_version: str | None = None,
    ) -> dict[str, object] | None:
        row = load_latest_approved_cycle_artifact(as_of_date=as_of_date)
        if row is None:
            return None
        if model_version is not None and str(row.get("model_version")) != str(
            model_version
        ):
            return None
        return row


class EconomicCyclePipelineWriter:
    """Default persistence seam for approved artifacts and compact snapshots."""

    def upsert_artifact(self, row: dict[str, object]) -> int:
        return upsert_cycle_model_artifact(row)

    def upsert_snapshot(self, row: dict[str, object]) -> int:
        return upsert_cycle_snapshots([row])


def _required_validation_metadata(report: ValidationReport) -> bool:
    required_metrics = {"brier_score", "log_loss", "accuracy", "ece"}
    required_baselines = {"persistence", "historical_transition"}
    for horizon in HORIZONS:
        validation = report.horizons.get(horizon)
        if validation is None:
            return False
        if not required_metrics.issubset(validation.metrics):
            return False
        if not required_baselines.issubset(validation.baseline_metrics):
            return False
        if any(phase not in validation.phase_support for phase in PHASES):
            return False
    return True


def _validation_decisions(
    report: ValidationReport,
    artifacts: Mapping[int, HorizonModelArtifact],
) -> tuple[dict[int, PublicationDecision], bool]:
    metadata_complete = _required_validation_metadata(report)
    decisions: dict[int, PublicationDecision] = {}
    for horizon in HORIZONS:
        if not metadata_complete:
            decisions[horizon] = PublicationDecision(
                horizon_months=horizon,
                status="LIMITED",
                reason_codes=("MISSING_GATE_METADATA",),
            )
            continue
        gate = evaluate_publication_gate(report, horizon)
        artifact = artifacts[horizon]
        reasons = list(gate.reason_codes)
        if artifact.publication_status != "READY":
            reasons.extend(artifact.reason_codes or ("MODEL_NOT_READY",))
        reasons = list(dict.fromkeys(reasons))
        decisions[horizon] = PublicationDecision(
            horizon_months=horizon,
            status="LIMITED" if reasons else "READY",
            reason_codes=tuple(reasons),
        )
    return decisions, metadata_complete


def _temperature_for_horizon(report: ValidationReport, horizon: int) -> float:
    rows = [item for item in report.predictions if item.horizon_months == horizon]
    if len(rows) < 2:
        return 1.0
    return fit_temperature(
        [item.probabilities for item in rows],
        [item.target_label for item in rows],
    )


def _write_artifact(writer: object, row: dict[str, object]) -> int:
    if callable(writer) and not hasattr(writer, "upsert_artifact"):
        return int(writer(row))
    return int(getattr(writer, "upsert_artifact")(row))


def train_validate_economic_cycle_model(
    *,
    trained_through: str | date,
    loader: object | None = None,
    writer: object | None = None,
    validator: Callable[..., ValidationReport] = run_rolling_origin_validation,
    initial_train_months: int = 120,
    preloaded_vintage_rows: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Persist a deterministic artifact only after all gate evidence exists."""

    cutoff = _as_date(trained_through, field="trained_through")
    resolved_loader = loader or EconomicCyclePipelineLoader()
    resolved_writer = writer or EconomicCyclePipelineWriter()

    # All fallible reads/fits happen before persistence, preserving last approved rows.
    panel, training_labels, evaluation_labels = getattr(
        resolved_loader, "load_training_data"
    )(cutoff)
    report = validator(
        panel,
        evaluation_labels,
        training_labels=training_labels,
        initial_train_months=initial_train_months,
    )
    fitted = fit_forecast_models(panel, training_labels)
    transition_matrix = estimate_transition_matrix(training_labels)
    provisional = {
        horizon: replace(
            fitted[horizon],
            temperature=_temperature_for_horizon(report, horizon),
            trained_through=cutoff.isoformat(),
            transition_matrix=transition_matrix,
        )
        for horizon in HORIZONS
    }
    decisions, metadata_complete = _validation_decisions(report, provisional)
    decided = {
        horizon: replace(
            provisional[horizon],
            publication_status=decisions[horizon].status,
            reason_codes=decisions[horizon].reason_codes,
        )
        for horizon in HORIZONS
    }
    hash_payload = _canonical_json(
        {
            "trained_through": cutoff,
            "artifacts": {
                str(horizon): asdict(artifact) for horizon, artifact in decided.items()
            },
            "decisions": {
                str(horizon): asdict(decision)
                for horizon, decision in decisions.items()
            },
        }
    )
    model_version = (
        f"{MODEL_FAMILY}-{hashlib.sha256(hash_payload.encode()).hexdigest()[:12]}"
    )
    artifacts = {
        horizon: replace(artifact, model_version=model_version)
        for horizon, artifact in decided.items()
    }
    status_payload = {
        str(horizon): {
            "status": decision.status,
            "reason_codes": list(decision.reason_codes),
        }
        for horizon, decision in decisions.items()
    }
    overall_status = (
        "READY"
        if metadata_complete
        and any(decision.status == "READY" for decision in decisions.values())
        else "LIMITED"
    )
    artifact_row = {
        "model_version": model_version,
        "trained_through": cutoff.isoformat(),
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "parameters_json": _canonical_json(
            {
                "schema_version": MODEL_FAMILY,
                "horizons": {
                    str(horizon): json.loads(serialize_horizon_model_artifact(artifact))
                    for horizon, artifact in artifacts.items()
                },
            }
        ),
        "validation_metrics_json": _canonical_json(asdict(report)),
        "publication_status": overall_status,
        "publication_status_json": _canonical_json(status_payload),
    }
    rows_written = _write_artifact(resolved_writer, artifact_row)
    return {
        "model_version": model_version,
        "trained_through": cutoff.isoformat(),
        "publication_status": overall_status,
        "horizon_statuses": status_payload,
        "validation_report": report,
        "artifact_row": artifact_row,
        "rows_written": rows_written,
    }


def _decode_artifact_bundle(
    artifact_row: Mapping[str, object],
) -> dict[int, HorizonModelArtifact]:
    payload = json.loads(str(artifact_row["parameters_json"]))
    horizons = payload.get("horizons") or {}
    decoded: dict[int, HorizonModelArtifact] = {}
    for horizon in HORIZONS:
        raw = horizons.get(str(horizon))
        if raw is None:
            continue
        decoded[horizon] = deserialize_horizon_model_artifact(_canonical_json(raw))
    return decoded


def _predict_horizon(
    artifact: HorizonModelArtifact,
    feature_row: Mapping[str, object],
    *,
    current_phase: str | None,
) -> dict[str, float]:
    likelihood = predict_phase_probabilities(artifact, feature_row, temperature=1.0)
    if artifact.horizon_months == 0 or current_phase not in PHASES:
        blended = likelihood
    else:
        prior = artifact.transition_matrix.get(str(current_phase))
        blended = (
            blend_likelihood_and_transition(likelihood, prior) if prior else likelihood
        )
    return apply_temperature(blended, artifact.temperature)


def _snapshot_row(
    snapshot: CycleSnapshot,
    *,
    artifact_row: Mapping[str, object],
    run_kind: str,
    feature_row: Mapping[str, object],
) -> dict[str, object]:
    horizon_zero = next(
        (item for item in snapshot.horizons if item.horizon_months == 0), None
    )
    return {
        "as_of_date": snapshot.as_of_date.isoformat(),
        "model_version": snapshot.model_version,
        "run_kind": run_kind,
        "training_cutoff_date": str(artifact_row.get("trained_through")),
        "data_cutoff_date": snapshot.as_of_date.isoformat(),
        "status": snapshot.status,
        "current_phase": horizon_zero.dominant_phase if horizon_zero else None,
        "expected_transition": snapshot.expected_transition,
        "nber_recession": int(float(feature_row.get("USREC_signal") or 0.0) >= 0.5),
        "probabilities_json": _canonical_json(
            horizon_zero.probabilities if horizon_zero else None
        ),
        "forecast_path_json": _canonical_json(
            [asdict(item) for item in snapshot.horizons]
        ),
        "factor_contributions_json": _canonical_json(snapshot.factor_contributions),
        "top_evidence_json": _canonical_json(snapshot.top_evidence),
        "warnings_json": _canonical_json(snapshot.warnings),
    }


def materialize_economic_cycle_snapshot(
    *,
    as_of_date: str | date,
    model_version: str | None = None,
    run_kind: str = "current",
    loader: object | None = None,
    writer: object | None = None,
    artifact_row: Mapping[str, object] | None = None,
    preloaded_vintage_rows: Sequence[Mapping[str, object]] | None = None,
) -> CycleSnapshot:
    """Materialize only horizon probabilities that passed their own gate."""

    if run_kind not in {"current", "historical_replay"}:
        raise ValueError(f"Unsupported run_kind: {run_kind}")
    origin = _as_date(as_of_date, field="as_of_date")
    resolved_loader = loader or EconomicCyclePipelineLoader()
    resolved_writer = writer or EconomicCyclePipelineWriter()
    if preloaded_vintage_rows is not None and hasattr(
        resolved_loader, "remember_origin"
    ):
        getattr(resolved_loader, "remember_origin")(origin, preloaded_vintage_rows)
    selected_row = (
        dict(artifact_row)
        if artifact_row is not None
        else getattr(resolved_loader, "load_artifact")(
            as_of_date=origin, model_version=model_version
        )
    )
    if not selected_row:
        raise LookupError(f"No approved economic-cycle artifact for {origin}")
    resolved_model_version = str(selected_row["model_version"])
    artifacts = _decode_artifact_bundle(selected_row)
    statuses = json.loads(str(selected_row.get("publication_status_json") or "{}"))
    feature_row = getattr(resolved_loader, "load_prediction_data")(origin)

    horizons: list[HorizonProbability] = []
    warnings: list[str] = []
    current_phase: str | None = None
    for horizon in HORIZONS:
        status_item = statuses.get(str(horizon)) or {}
        publication_status = str(status_item.get("status") or "LIMITED")
        reasons = tuple(str(item) for item in status_item.get("reason_codes") or ())
        artifact = artifacts.get(horizon)
        if publication_status != "READY" or artifact is None:
            reason = reasons[0] if reasons else "MISSING_APPROVED_HORIZON"
            horizons.append(
                HorizonProbability(
                    horizon_months=horizon,
                    probabilities=None,
                    dominant_phase=None,
                    confidence=None,
                    publication_status="LIMITED",
                    reason=reason,
                )
            )
            warnings.append(f"{horizon}개월 지평은 제한적입니다: {reason}")
            continue
        probabilities = _predict_horizon(
            artifact, feature_row, current_phase=current_phase
        )
        dominant = max(PHASES, key=probabilities.__getitem__)
        if horizon == 0:
            current_phase = dominant
        horizons.append(
            HorizonProbability(
                horizon_months=horizon,
                probabilities=probabilities,
                dominant_phase=dominant,
                confidence=probabilities[dominant],
                publication_status="READY",
            )
        )

    h0_artifact = artifacts.get(0)
    explanation: dict[str, object] = {}
    if h0_artifact is not None and horizons[0].publication_status == "READY":
        explanation = explain_phase_prediction(h0_artifact, feature_row)
    contributions = tuple(
        {
            "factor": name,
            "value": float(value),
        }
        for name, value in sorted(
            dict(explanation.get("contributions") or {}).items(),
            key=lambda item: abs(float(item[1])),
            reverse=True,
        )
    )
    evidence = tuple(
        {
            "factor": name,
            "value": float(feature_row[name]),
        }
        for name in (
            "activity_score",
            "labor_income_score",
            "financial_leading_score",
            "inflation_policy_score",
        )
        if name in feature_row and pd.notna(feature_row[name])
    )
    one_month = next(item for item in horizons if item.horizon_months == 1)
    expected_transition = (
        f"{current_phase}_to_{one_month.dominant_phase}"
        if current_phase and one_month.dominant_phase
        else None
    )
    snapshot = CycleSnapshot(
        as_of_date=origin,
        model_version=resolved_model_version,
        status=(
            "READY"
            if all(item.publication_status == "READY" for item in horizons)
            else "LIMITED"
        ),
        horizons=tuple(horizons),
        factor_contributions=contributions,
        top_evidence=evidence,
        warnings=tuple(warnings),
        expected_transition=expected_transition,
    )
    row = _snapshot_row(
        snapshot,
        artifact_row=selected_row,
        run_kind=run_kind,
        feature_row=feature_row,
    )
    if callable(resolved_writer) and not hasattr(resolved_writer, "upsert_snapshot"):
        resolved_writer(row)
    else:
        getattr(resolved_writer, "upsert_snapshot")(row)
    return snapshot


def replay_economic_cycle_history(
    *,
    start_date: str | date,
    end_date: str | date,
    cadence: str = "month_end",
    loader: object | None = None,
    writer: object | None = None,
    trainer: Callable[..., dict[str, object]] = train_validate_economic_cycle_model,
    materializer: Callable[..., object] = materialize_economic_cycle_snapshot,
) -> dict[str, object]:
    """Replay month ends with an origin-specific artifact and strict as-of rows."""

    if cadence != "month_end":
        raise ValueError(f"Unsupported replay cadence: {cadence}")
    origins = month_end_origins(start_date, end_date)
    resolved_loader = loader or EconomicCyclePipelineLoader()
    resolved_writer = writer or EconomicCyclePipelineWriter()
    if hasattr(resolved_loader, "prime_panel"):
        getattr(resolved_loader, "prime_panel")(
            _as_date(end_date, field="end_date")
        )
    model_versions: list[str] = []
    for origin in origins:
        vintage_rows = getattr(resolved_loader, "load_for_origin")(origin)
        cutoff = (pd.Timestamp(origin) - pd.offsets.MonthEnd(1)).date()
        training = trainer(
            trained_through=cutoff,
            loader=resolved_loader,
            writer=resolved_writer,
            preloaded_vintage_rows=vintage_rows,
        )
        model_version = str(training["model_version"])
        materializer(
            as_of_date=origin,
            model_version=model_version,
            run_kind="historical_replay",
            loader=resolved_loader,
            writer=resolved_writer,
            artifact_row=training["artifact_row"],
            preloaded_vintage_rows=vintage_rows,
        )
        model_versions.append(model_version)
    return {
        "start_date": _as_date(start_date, field="start_date").isoformat(),
        "end_date": _as_date(end_date, field="end_date").isoformat(),
        "cadence": cadence,
        "origins_processed": len(origins),
        "model_versions": model_versions,
    }
