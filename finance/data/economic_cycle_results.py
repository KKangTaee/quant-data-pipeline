"""Persist approved economic-cycle model artifacts and compact snapshots."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from finance.economic_cycle_model import HorizonModelArtifact, PHASES

from .db.mysql import MySQLClient
from .db.schema import ECONOMIC_CYCLE_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
ARTIFACT_TABLE = "economic_cycle_model_artifact"
SNAPSHOT_TABLE = "economic_cycle_snapshot"


@dataclass(frozen=True)
class HorizonProbability:
    horizon_months: int
    probabilities: dict[str, float] | None
    dominant_phase: str | None
    confidence: float | None
    publication_status: str
    reason: str | None = None


@dataclass(frozen=True)
class CycleSnapshot:
    as_of_date: date
    model_version: str
    status: str
    horizons: tuple[HorizonProbability, ...]
    factor_contributions: tuple[dict[str, object], ...]
    top_evidence: tuple[dict[str, object], ...]
    warnings: tuple[str, ...]
    expected_transition: str | None = None


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def serialize_horizon_model_artifact(artifact: HorizonModelArtifact) -> str:
    """Serialize an artifact with stable key order for hashing/persistence."""

    return _canonical_json(asdict(artifact))


def deserialize_horizon_model_artifact(payload: str) -> HorizonModelArtifact:
    """Restore tuple fields and exact phase maps from canonical JSON."""

    raw = json.loads(payload)
    return HorizonModelArtifact(
        horizon_months=int(raw["horizon_months"]),
        feature_names=tuple(raw["feature_names"]),
        class_priors={phase: float(raw["class_priors"][phase]) for phase in PHASES},
        means={
            phase: {name: float(value) for name, value in raw["means"][phase].items()}
            for phase in PHASES
        },
        variances={
            phase: {
                name: float(value) for name, value in raw["variances"][phase].items()
            }
            for phase in PHASES
        },
        phase_support={phase: int(raw["phase_support"][phase]) for phase in PHASES},
        minimum_variance=float(raw["minimum_variance"]),
        publication_status=str(raw["publication_status"]),
        reason_codes=tuple(raw.get("reason_codes") or ()),
        temperature=float(raw.get("temperature") or 1.0),
        trained_through=raw.get("trained_through"),
        model_version=str(raw.get("model_version") or "economic_cycle_gaussian_v1"),
        transition_matrix={
            str(origin): {str(target): float(value) for target, value in row.items()}
            for origin, row in (raw.get("transition_matrix") or {}).items()
        },
    )


def serialize_cycle_snapshot(snapshot: CycleSnapshot) -> str:
    """Serialize the compact UI-facing snapshot without model/source rows."""

    payload = asdict(snapshot)
    payload["as_of_date"] = snapshot.as_of_date.isoformat()
    return _canonical_json(payload)


def deserialize_cycle_snapshot(payload: str) -> CycleSnapshot:
    raw = json.loads(payload)
    return CycleSnapshot(
        as_of_date=date.fromisoformat(raw["as_of_date"]),
        model_version=str(raw["model_version"]),
        status=str(raw["status"]),
        horizons=tuple(
            HorizonProbability(
                horizon_months=int(item["horizon_months"]),
                probabilities=(
                    {phase: float(item["probabilities"][phase]) for phase in PHASES}
                    if item.get("probabilities") is not None
                    else None
                ),
                dominant_phase=item.get("dominant_phase"),
                confidence=(
                    float(item["confidence"])
                    if item.get("confidence") is not None
                    else None
                ),
                publication_status=str(item["publication_status"]),
                reason=item.get("reason"),
            )
            for item in raw["horizons"]
        ),
        factor_contributions=tuple(dict(item) for item in raw["factor_contributions"]),
        top_evidence=tuple(dict(item) for item in raw["top_evidence"]),
        warnings=tuple(str(item) for item in raw["warnings"]),
        expected_transition=raw.get("expected_transition"),
    )


def ensure_economic_cycle_result_schemas(
    *,
    connection: Any = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    owns_connection = connection is None
    db = connection or MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        for table_name, schema in ECONOMIC_CYCLE_SCHEMAS.items():
            db.execute(schema)
            sync_table_schema(db, table_name, schema, DB_META)
    finally:
        if owns_connection:
            db.close()


def upsert_cycle_model_artifact(
    row: dict[str, object],
    *,
    connection: Any = None,
) -> int:
    owns_connection = connection is None
    db = connection or MySQLClient("localhost", "root", "1234", 3306)
    try:
        if owns_connection:
            db.use_db(DB_META)
            schema = ECONOMIC_CYCLE_SCHEMAS[ARTIFACT_TABLE]
            db.execute(schema)
            sync_table_schema(db, ARTIFACT_TABLE, schema, DB_META)
        sql = f"""
        INSERT INTO {ARTIFACT_TABLE} (
          model_version, trained_through, feature_schema_version,
          parameters_json, validation_metrics_json,
          publication_status, publication_status_json
        ) VALUES (
          %(model_version)s, %(trained_through)s, %(feature_schema_version)s,
          %(parameters_json)s, %(validation_metrics_json)s,
          %(publication_status)s, %(publication_status_json)s
        )
        ON DUPLICATE KEY UPDATE
          feature_schema_version = VALUES(feature_schema_version),
          parameters_json = VALUES(parameters_json),
          validation_metrics_json = VALUES(validation_metrics_json),
          publication_status = VALUES(publication_status),
          publication_status_json = VALUES(publication_status_json)
        """
        db.executemany(sql, [row])
        return 1
    finally:
        if owns_connection:
            db.close()


def upsert_cycle_snapshots(
    rows: list[dict[str, object]],
    *,
    connection: Any = None,
) -> int:
    if not rows:
        return 0
    owns_connection = connection is None
    db = connection or MySQLClient("localhost", "root", "1234", 3306)
    try:
        if owns_connection:
            db.use_db(DB_META)
            schema = ECONOMIC_CYCLE_SCHEMAS[SNAPSHOT_TABLE]
            db.execute(schema)
            sync_table_schema(db, SNAPSHOT_TABLE, schema, DB_META)
        normalized_rows = []
        for row in rows:
            normalized = dict(row)
            normalized.setdefault("baseline_as_of_date", None)
            normalized.setdefault("source_collected_at", None)
            normalized.setdefault("source_coverage_json", None)
            normalized_rows.append(normalized)
        sql = f"""
        INSERT INTO {SNAPSHOT_TABLE} (
          as_of_date, model_version, run_kind, training_cutoff_date,
          data_cutoff_date, baseline_as_of_date, source_collected_at,
          source_coverage_json, status, current_phase, expected_transition,
          nber_recession, probabilities_json, forecast_path_json,
          factor_contributions_json, top_evidence_json, warnings_json
        ) VALUES (
          %(as_of_date)s, %(model_version)s, %(run_kind)s, %(training_cutoff_date)s,
          %(data_cutoff_date)s, %(baseline_as_of_date)s, %(source_collected_at)s,
          %(source_coverage_json)s, %(status)s, %(current_phase)s, %(expected_transition)s,
          %(nber_recession)s, %(probabilities_json)s, %(forecast_path_json)s,
          %(factor_contributions_json)s, %(top_evidence_json)s, %(warnings_json)s
        )
        ON DUPLICATE KEY UPDATE
          training_cutoff_date = VALUES(training_cutoff_date),
          data_cutoff_date = VALUES(data_cutoff_date),
          baseline_as_of_date = VALUES(baseline_as_of_date),
          source_collected_at = VALUES(source_collected_at),
          source_coverage_json = VALUES(source_coverage_json),
          status = VALUES(status),
          current_phase = VALUES(current_phase),
          expected_transition = VALUES(expected_transition),
          nber_recession = VALUES(nber_recession),
          probabilities_json = VALUES(probabilities_json),
          forecast_path_json = VALUES(forecast_path_json),
          factor_contributions_json = VALUES(factor_contributions_json),
          top_evidence_json = VALUES(top_evidence_json),
          warnings_json = VALUES(warnings_json)
        """
        db.executemany(sql, normalized_rows)
        return len(normalized_rows)
    finally:
        if owns_connection:
            db.close()
