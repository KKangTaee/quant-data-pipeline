"""Validate and persist inflation-policy model and resistance results."""

from __future__ import annotations

import json
import math
import uuid
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Callable

from .db.mysql import MySQLClient
from .db.schema import INFLATION_POLICY_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
PUBLICATION_STATUSES = {"READY", "LIMITED", "NOT_AVAILABLE", "FAILED"}
RUN_KINDS = {"current", "historical_replay", "scenario"}
RESISTANCE_OWNERS = {"AUTO", "USER"}
RESISTANCE_STATES = {"APPROACH", "ATTEMPT", "CONFIRMED", "HOLD", "FAILED"}


def _assert_finite(value: object, *, path: str) -> None:
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, (int, float)):
        if not math.isfinite(float(value)):
            raise ValueError(f"{path} must contain only finite numbers")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _assert_finite(item, path=f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _assert_finite(item, path=f"{path}[{index}]")


def _canonical_json(value: object, *, field: str) -> str:
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field} must be valid JSON") from exc
    _assert_finite(parsed, path=field)
    try:
        return json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be JSON serializable") from exc


def _sql_datetime(value: object, *, field: str) -> str:
    try:
        parsed = (
            value
            if isinstance(value, datetime)
            else datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        )
    except ValueError as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.strftime("%Y-%m-%d %H:%M:%S.%f")


def _finite_number(
    value: object,
    *,
    field: str,
    optional: bool = False,
) -> float | None:
    if value is None and optional:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def _required(row: Mapping[str, object], fields: Sequence[str]) -> dict[str, object]:
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    return dict(row)


def _store_one(
    *,
    table: str,
    row: dict[str, object],
    sql: str,
    db_factory: Callable[..., object],
) -> None:
    db = db_factory("localhost", "root", "1234", 3306)
    try:
        db.use_db(DB_META)
        schema = INFLATION_POLICY_SCHEMAS[table]
        db.execute(schema)
        sync_table_schema(db, table, schema, DB_META)
        db.executemany(sql, [row])
    finally:
        db.close()


def save_inflation_policy_model_artifact(
    row: Mapping[str, object],
    *,
    db_factory: Callable[..., object] = MySQLClient,
) -> None:
    """Persist one validated model component by its exact training key."""

    prepared = _required(
        row,
        (
            "model_version",
            "trained_cutoff_at",
            "component",
            "feature_schema_version",
            "transform_schema_version",
            "state_schema_version",
            "training_start_date",
            "forecast_horizon",
            "parameters_json",
            "validation_json",
            "calibration_json",
            "publication_status",
            "publication_reasons_json",
        ),
    )
    status = str(prepared["publication_status"])
    if status not in PUBLICATION_STATUSES:
        raise ValueError("Invalid publication_status")
    prepared["trained_cutoff_at"] = _sql_datetime(
        prepared["trained_cutoff_at"], field="trained_cutoff_at"
    )
    prepared["ensemble_weight"] = _finite_number(
        prepared.get("ensemble_weight"), field="ensemble_weight", optional=True
    )
    for field in (
        "parameters_json",
        "validation_json",
        "calibration_json",
        "publication_reasons_json",
    ):
        prepared[field] = _canonical_json(prepared[field], field=field)
    sql = """
    INSERT INTO inflation_policy_model_artifact (
      model_version, trained_cutoff_at, component, feature_schema_version,
      transform_schema_version, state_schema_version, training_start_date,
      forecast_horizon, ensemble_weight, parameters_json, validation_json,
      calibration_json, publication_status, publication_reasons_json
    ) VALUES (
      %(model_version)s, %(trained_cutoff_at)s, %(component)s,
      %(feature_schema_version)s, %(transform_schema_version)s,
      %(state_schema_version)s, %(training_start_date)s, %(forecast_horizon)s,
      %(ensemble_weight)s, %(parameters_json)s, %(validation_json)s,
      %(calibration_json)s, %(publication_status)s, %(publication_reasons_json)s
    )
    ON DUPLICATE KEY UPDATE
      feature_schema_version = VALUES(feature_schema_version),
      transform_schema_version = VALUES(transform_schema_version),
      state_schema_version = VALUES(state_schema_version),
      training_start_date = VALUES(training_start_date),
      forecast_horizon = VALUES(forecast_horizon),
      ensemble_weight = VALUES(ensemble_weight),
      parameters_json = VALUES(parameters_json),
      validation_json = VALUES(validation_json),
      calibration_json = VALUES(calibration_json),
      publication_status = VALUES(publication_status),
      publication_reasons_json = VALUES(publication_reasons_json)
    """
    _store_one(
        table="inflation_policy_model_artifact",
        row=prepared,
        sql=sql,
        db_factory=db_factory,
    )


def save_inflation_policy_snapshot(
    row: Mapping[str, object],
    *,
    db_factory: Callable[..., object] = MySQLClient,
) -> None:
    """Persist one validated forward/reverse workbench snapshot."""

    json_fields = (
        "inflation_json",
        "policy_json",
        "rates_json",
        "reverse_json",
        "equity_json",
        "recession_json",
        "evidence_json",
        "freshness_json",
        "warnings_json",
    )
    source = dict(row)
    source.setdefault(
        "equity_json",
        {
            "publication_status": "NOT_AVAILABLE",
            "reason": "verified_eps_vintages_or_joint_paths_not_available",
        },
    )
    source.setdefault(
        "recession_json",
        {
            "publication_status": "NOT_AVAILABLE",
            "reason": "recession_model_not_available",
        },
    )
    prepared = _required(
        source,
        (
            "as_of_at",
            "model_version",
            "run_kind",
            "publication_status",
            *json_fields,
        ),
    )
    if str(prepared["run_kind"]) not in RUN_KINDS:
        raise ValueError("Invalid run_kind")
    if str(prepared["publication_status"]) not in PUBLICATION_STATUSES:
        raise ValueError("Invalid publication_status")
    prepared["as_of_at"] = _sql_datetime(prepared["as_of_at"], field="as_of_at")
    for field in json_fields:
        prepared[field] = _canonical_json(prepared[field], field=field)
    sql = """
    INSERT INTO inflation_policy_snapshot (
      as_of_at, model_version, run_kind, publication_status,
      inflation_json, policy_json, rates_json, reverse_json,
      equity_json, recession_json, evidence_json, freshness_json, warnings_json
    ) VALUES (
      %(as_of_at)s, %(model_version)s, %(run_kind)s, %(publication_status)s,
      %(inflation_json)s, %(policy_json)s, %(rates_json)s, %(reverse_json)s,
      %(equity_json)s, %(recession_json)s, %(evidence_json)s, %(freshness_json)s, %(warnings_json)s
    )
    ON DUPLICATE KEY UPDATE
      publication_status = VALUES(publication_status),
      inflation_json = VALUES(inflation_json),
      policy_json = VALUES(policy_json),
      rates_json = VALUES(rates_json),
      reverse_json = VALUES(reverse_json),
      equity_json = VALUES(equity_json),
      recession_json = VALUES(recession_json),
      evidence_json = VALUES(evidence_json),
      freshness_json = VALUES(freshness_json),
      warnings_json = VALUES(warnings_json)
    """
    _store_one(
        table="inflation_policy_snapshot",
        row=prepared,
        sql=sql,
        db_factory=db_factory,
    )


def save_yield_resistance_definition(
    row: Mapping[str, object],
    *,
    db_factory: Callable[..., object] = MySQLClient,
) -> str:
    """Persist one AUTO/USER resistance definition and return its stable id."""

    prepared = _required(
        row,
        (
            "owner",
            "instrument",
            "short_lookback_days",
            "long_lookback_days",
            "zone_lower_pct",
            "zone_upper_pct",
            "confirmation_profile_json",
            "known_at",
            "algorithm_version",
            "saved_at",
        ),
    )
    if str(prepared["owner"]) not in RESISTANCE_OWNERS:
        raise ValueError("Invalid resistance owner")
    prepared["definition_id"] = str(
        prepared.get("definition_id") or uuid.uuid4()
    )
    prepared.setdefault("definition_name", None)
    prepared.setdefault("buffer_pct", 0.0)
    prepared.setdefault("is_active", 1)
    for field in ("zone_lower_pct", "zone_upper_pct", "buffer_pct"):
        prepared[field] = _finite_number(prepared[field], field=field)
    if float(prepared["zone_lower_pct"]) > float(prepared["zone_upper_pct"]):
        raise ValueError("zone_lower_pct cannot exceed zone_upper_pct")
    prepared["confirmation_profile_json"] = _canonical_json(
        prepared["confirmation_profile_json"], field="confirmation_profile_json"
    )
    prepared["known_at"] = _sql_datetime(prepared["known_at"], field="known_at")
    prepared["saved_at"] = _sql_datetime(prepared["saved_at"], field="saved_at")
    sql = """
    INSERT INTO yield_resistance_definition (
      definition_id, owner, definition_name, instrument, short_lookback_days,
      long_lookback_days, zone_lower_pct, zone_upper_pct, buffer_pct,
      confirmation_profile_json, known_at, algorithm_version, is_active, saved_at
    ) VALUES (
      %(definition_id)s, %(owner)s, %(definition_name)s, %(instrument)s,
      %(short_lookback_days)s, %(long_lookback_days)s, %(zone_lower_pct)s,
      %(zone_upper_pct)s, %(buffer_pct)s, %(confirmation_profile_json)s,
      %(known_at)s, %(algorithm_version)s, %(is_active)s, %(saved_at)s
    )
    ON DUPLICATE KEY UPDATE
      owner = VALUES(owner), definition_name = VALUES(definition_name),
      instrument = VALUES(instrument), short_lookback_days = VALUES(short_lookback_days),
      long_lookback_days = VALUES(long_lookback_days),
      zone_lower_pct = VALUES(zone_lower_pct), zone_upper_pct = VALUES(zone_upper_pct),
      buffer_pct = VALUES(buffer_pct),
      confirmation_profile_json = VALUES(confirmation_profile_json),
      known_at = VALUES(known_at), algorithm_version = VALUES(algorithm_version),
      is_active = VALUES(is_active), saved_at = VALUES(saved_at)
    """
    _store_one(
        table="yield_resistance_definition",
        row=prepared,
        sql=sql,
        db_factory=db_factory,
    )
    return str(prepared["definition_id"])


def save_yield_resistance_snapshot(
    row: Mapping[str, object],
    *,
    db_factory: Callable[..., object] = MySQLClient,
) -> None:
    """Persist one validated resistance state by definition and as-of time."""

    json_fields = ("timeframe_confluence_json", "quality_json", "evidence_json")
    prepared = _required(
        row,
        (
            "definition_id",
            "as_of_at",
            "current_value_pct",
            "distance_to_zone_pct",
            "state",
            *json_fields,
        ),
    )
    if str(prepared["state"]) not in RESISTANCE_STATES:
        raise ValueError("Invalid resistance state")
    for field in (
        "current_value_pct",
        "distance_to_zone_pct",
        "zone_strength",
        "breakout_probability",
        "hold_probability",
    ):
        prepared[field] = _finite_number(
            prepared.get(field), field=field, optional=field not in prepared
        )
    for field in ("breakout_probability", "hold_probability"):
        value = prepared[field]
        if value is not None and not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{field} must be between 0 and 1")
    prepared.setdefault("dominant_driver", None)
    prepared["as_of_at"] = _sql_datetime(prepared["as_of_at"], field="as_of_at")
    for field in json_fields:
        prepared[field] = _canonical_json(prepared[field], field=field)
    sql = """
    INSERT INTO yield_resistance_snapshot (
      definition_id, as_of_at, current_value_pct, distance_to_zone_pct, state,
      zone_strength, timeframe_confluence_json, breakout_probability,
      hold_probability, dominant_driver, quality_json, evidence_json
    ) VALUES (
      %(definition_id)s, %(as_of_at)s, %(current_value_pct)s,
      %(distance_to_zone_pct)s, %(state)s, %(zone_strength)s,
      %(timeframe_confluence_json)s, %(breakout_probability)s,
      %(hold_probability)s, %(dominant_driver)s, %(quality_json)s,
      %(evidence_json)s
    )
    ON DUPLICATE KEY UPDATE
      current_value_pct = VALUES(current_value_pct),
      distance_to_zone_pct = VALUES(distance_to_zone_pct), state = VALUES(state),
      zone_strength = VALUES(zone_strength),
      timeframe_confluence_json = VALUES(timeframe_confluence_json),
      breakout_probability = VALUES(breakout_probability),
      hold_probability = VALUES(hold_probability),
      dominant_driver = VALUES(dominant_driver), quality_json = VALUES(quality_json),
      evidence_json = VALUES(evidence_json)
    """
    _store_one(
        table="yield_resistance_snapshot",
        row=prepared,
        sql=sql,
        db_factory=db_factory,
    )
