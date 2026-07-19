from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Callable, Mapping, Protocol

from finance.data.db.mysql import MySQLClient

from .persistence import FINANCE_META_DB
from .schemas import DiagnosisSnapshotIdentity


@dataclass(frozen=True)
class DiagnosisSnapshotCapture:
    identity: DiagnosisSnapshotIdentity
    inserted: bool
    payload: dict[str, Any]


class HistoryRepository(Protocol):
    def insert_snapshot_if_absent(self, identity: tuple[str, date, str, str], payload: Mapping[str, Any]) -> Any: ...
    def list_snapshots(self, group_id: str, start_date: date, end_date: date) -> list[dict[str, Any]]: ...


class MySQLMonitoringHistoryRepository:
    def __init__(self, db_factory: Callable[[], MySQLClient]) -> None:
        self._db_factory = db_factory

    def insert_snapshot_if_absent(self, identity, payload):
        group_id, as_of_date, config_fingerprint, policy_version = identity
        db = self._db_factory()
        try:
            db.use_db(FINANCE_META_DB)
            existing = db.query(
                """SELECT diagnosis_snapshot_id FROM monitoring_diagnosis_snapshot
                   WHERE portfolio_group_id=%s AND as_of_date=%s AND config_fingerprint=%s AND policy_version=%s""",
                [group_id, as_of_date, config_fingerprint, policy_version],
            )
            db.execute(
                """
                INSERT IGNORE INTO monitoring_diagnosis_snapshot
                  (portfolio_group_id, as_of_date, config_fingerprint, policy_version, macro_version,
                   publication_time, source_dates_json, observations_json, outcome_21, outcome_63,
                   outcome_status, outcome_measured_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                [
                    group_id, as_of_date, config_fingerprint, policy_version, payload["macro_version"],
                    payload["publication_time"], json.dumps(payload["source_dates"], ensure_ascii=False, sort_keys=True),
                    json.dumps(payload["observations"], ensure_ascii=False, sort_keys=True),
                    payload.get("outcome_21"), payload.get("outcome_63"), payload.get("outcome_status", "pending"),
                    payload.get("outcome_measured_at"),
                ],
            )
        finally:
            db.close()
        return {**dict(payload), "inserted": not bool(existing)}

    def list_snapshots(self, group_id: str, start_date: date, end_date: date) -> list[dict[str, Any]]:
        db = self._db_factory()
        try:
            db.use_db(FINANCE_META_DB)
            rows = db.query(
                """SELECT * FROM monitoring_diagnosis_snapshot
                   WHERE portfolio_group_id=%s AND as_of_date BETWEEN %s AND %s
                   ORDER BY as_of_date ASC, diagnosis_snapshot_id ASC""",
                [group_id, start_date, end_date],
            )
        finally:
            db.close()
        return rows


def _date_text(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    return str(value or "")


def _compact_row(row: Mapping[str, Any], *, macro: bool) -> dict[str, Any]:
    common = {
        "rule_id": row.get("rule_id"),
        "severity": row.get("severity"),
        "confidence": row.get("confidence"),
        "source_dates": list(row.get("source_dates") or []),
    }
    if macro:
        return {
            **common,
            "state": row.get("state"),
            "affected_weight": row.get("affected_weight"),
            "matched_conditions": list(row.get("matched_conditions") or []),
            "current_observation": row.get("current_observation"),
            "change_condition": row.get("change_condition"),
        }
    return {
        **common,
        "classification": row.get("classification"),
        "measured_fact": row.get("measured_fact"),
        "threshold": row.get("threshold"),
        "change_condition": row.get("change_condition"),
    }


def capture_diagnosis_snapshot(
    group_id: str,
    as_of_date: date,
    workspace: Mapping[str, Any],
    repository: HistoryRepository,
) -> DiagnosisSnapshotCapture:
    """Append one compact PIT snapshot and never copy raw price/macro series."""

    clean_group = str(group_id or "").strip()
    if not clean_group or not isinstance(as_of_date, date):
        raise ValueError("group id and as-of date are required")
    fingerprint = str(workspace.get("config_fingerprint") or "")
    if len(fingerprint) != 64 or any(character not in "0123456789abcdef" for character in fingerprint.lower()):
        raise ValueError("a 64-character config fingerprint is required")
    diagnosis = dict(workspace.get("diagnosis") or {})
    macro = dict(workspace.get("macro_observation") or {})
    policy_version = str(diagnosis.get("policy_version") or "")
    macro_version = str(macro.get("version") or "")
    if not policy_version or not macro_version:
        raise ValueError("policy and macro versions are required")
    source_health = dict(workspace.get("source_health") or {})
    source_dates = {str(key): _date_text(value)[:10] for key, value in dict(source_health.get("as_of_dates") or {}).items() if value}
    for value in source_dates.values():
        if date.fromisoformat(value) > as_of_date:
            raise ValueError("future source date is not valid for an as-of snapshot")
    publication_time = _date_text(workspace.get("generated_at"))
    observations = {
        "diagnosis": [_compact_row(dict(row), macro=False) for row in diagnosis.get("all_rows") or [] if isinstance(row, Mapping)],
        "macro": [_compact_row(dict(row), macro=True) for row in macro.get("rows") or [] if isinstance(row, Mapping)],
        "macro_publication": source_health.get("publication"),
    }
    payload = {
        "portfolio_group_id": clean_group,
        "as_of_date": as_of_date.isoformat(),
        "config_fingerprint": fingerprint,
        "policy_version": policy_version,
        "macro_version": macro_version,
        "publication_time": publication_time,
        "source_dates": source_dates,
        "observations": observations,
        "outcome_21": None,
        "outcome_63": None,
        "outcome_status": "pending",
        "outcome_measured_at": None,
    }
    identity_tuple = (clean_group, as_of_date, fingerprint, policy_version)
    result = repository.insert_snapshot_if_absent(identity_tuple, payload)
    inserted = bool(dict(result or {}).get("inserted", False))
    return DiagnosisSnapshotCapture(
        identity=DiagnosisSnapshotIdentity(clean_group, as_of_date, fingerprint, policy_version),
        inserted=inserted,
        payload=payload,
    )


def _json_object(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if value in (None, ""):
        return {} if value is None else value
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def load_diagnosis_history(
    group_id: str,
    start_date: date,
    end_date: date,
    *,
    repository: HistoryRepository,
) -> list[dict[str, Any]]:
    rows = repository.list_snapshots(str(group_id), start_date, end_date)
    normalized = []
    for row in rows:
        value = dict(row)
        value["as_of_date"] = _date_text(value.get("as_of_date"))[:10]
        value["publication_time"] = _date_text(value.get("publication_time"))
        if "source_dates_json" in value:
            value["source_dates"] = _json_object(value.pop("source_dates_json"))
        if "observations_json" in value:
            value["observations"] = _json_object(value.pop("observations_json"))
        normalized.append(value)
    return normalized
