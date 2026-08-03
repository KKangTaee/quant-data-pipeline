from __future__ import annotations


def _compact(sql: str) -> str:
    return " ".join(sql.split())


def test_inflation_policy_schema_keeps_release_and_identity_boundaries() -> None:
    from finance.data.db.schema import INFLATION_POLICY_SCHEMAS, PROVIDER_SCHEMAS

    vintage = _compact(PROVIDER_SCHEMAS["macro_series_vintage_observation"])
    assert "released_at DATETIME(6) NULL" in vintage

    assert set(INFLATION_POLICY_SCHEMAS) == {
        "fomc_sep_distribution",
        "fomc_policy_decision",
        "inflation_policy_model_artifact",
        "inflation_policy_snapshot",
        "yield_resistance_definition",
        "yield_resistance_snapshot",
    }

    sep = _compact(INFLATION_POLICY_SCHEMAS["fomc_sep_distribution"])
    assert "participant_id" not in sep
    assert "released_at DATETIME(6) NOT NULL" in sep
    assert "participant_count SMALLINT NOT NULL" in sep


def test_inflation_policy_schema_uses_point_in_time_business_keys() -> None:
    from finance.data.db.schema import INFLATION_POLICY_SCHEMAS

    sep = _compact(INFLATION_POLICY_SCHEMAS["fomc_sep_distribution"])
    assert (
        "UNIQUE KEY uk_fomc_sep_distribution "
        "(released_at, target_period, variable_name, distribution_kind, bin_label)"
    ) in sep
    assert "KEY ix_fomc_sep_released (released_at, variable_name, target_period)" in sep

    decision = _compact(INFLATION_POLICY_SCHEMAS["fomc_policy_decision"])
    assert "UNIQUE KEY uk_fomc_policy_meeting (meeting_date)" in decision
    assert "KEY ix_fomc_policy_released (released_at, meeting_date)" in decision

    artifact = _compact(INFLATION_POLICY_SCHEMAS["inflation_policy_model_artifact"])
    assert (
        "UNIQUE KEY uk_inflation_policy_artifact "
        "(model_version, trained_cutoff_at, component)"
    ) in artifact
    assert "KEY ix_inflation_policy_artifact_cutoff (trained_cutoff_at, publication_status)" in artifact

    snapshot = _compact(INFLATION_POLICY_SCHEMAS["inflation_policy_snapshot"])
    assert (
        "UNIQUE KEY uk_inflation_policy_snapshot "
        "(as_of_at, model_version, run_kind)"
    ) in snapshot
    assert "KEY ix_inflation_policy_snapshot_as_of (as_of_at, publication_status)" in snapshot

    definition = _compact(INFLATION_POLICY_SCHEMAS["yield_resistance_definition"])
    assert "UNIQUE KEY uk_yield_resistance_definition (definition_id)" in definition
    assert "owner ENUM('AUTO','USER') NOT NULL" in definition

    resistance = _compact(INFLATION_POLICY_SCHEMAS["yield_resistance_snapshot"])
    assert (
        "UNIQUE KEY uk_yield_resistance_snapshot (definition_id, as_of_at)"
    ) in resistance
    assert "KEY ix_yield_resistance_snapshot_as_of (as_of_at, state)" in resistance


def test_inflation_policy_schema_keeps_json_payloads_and_rate_precision() -> None:
    from finance.data.db.schema import INFLATION_POLICY_SCHEMAS

    combined = " ".join(_compact(sql) for sql in INFLATION_POLICY_SCHEMAS.values())
    assert "DECIMAL(10,4)" in combined
    assert "confirmation_profile_json LONGTEXT NOT NULL" in combined
    assert "validation_json LONGTEXT NOT NULL" in combined
    assert "inflation_json LONGTEXT NOT NULL" in combined
    assert "equity_json LONGTEXT NOT NULL" in combined
    assert "quality_json LONGTEXT NOT NULL" in combined
