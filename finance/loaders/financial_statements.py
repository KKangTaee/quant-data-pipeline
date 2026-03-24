from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from finance.data.db.mysql import MySQLClient

from ._common import (
    normalize_date_range,
    normalize_loader_freq,
    resolve_loader_symbols,
    validate_snapshot_inputs,
)


STATEMENT_VALUE_COLUMNS = [
    "symbol",
    "freq",
    "period_start",
    "period_end",
    "period_label",
    "period_type",
    "source_period_type",
    "fiscal_year",
    "fiscal_period",
    "fiscal_quarter",
    "statement_type",
    "concept",
    "taxonomy",
    "label",
    "value",
    "unit",
    "filing_date",
    "accepted_at",
    "available_at",
    "report_date",
    "form_type",
    "accession_no",
    "data_quality",
    "is_audited",
    "is_restated",
    "is_estimated",
    "confidence",
]

STATEMENT_LABEL_COLUMNS = [
    "symbol",
    "statement_type",
    "concept",
    "as_of",
    "label",
    "as_of_label",
    "as_of_period_type",
    "as_of_fiscal_year",
    "as_of_fiscal_quarter",
    "label_kr",
    "taxonomy",
    "latest_unit",
    "latest_filing_date",
    "latest_accepted_at",
    "latest_available_at",
    "latest_accession_no",
    "latest_form_type",
    "confidence",
    "enabled",
    "priority",
    "condition_json",
]


def _normalize_optional_list(values: str | Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        raw = values.replace("\n", ",").split(",")
    else:
        raw = list(values)

    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        val = str(item).strip()
        if not val or val in seen:
            continue
        seen.add(val)
        out.append(val)
    return out


def load_statement_values(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    freq: str = "annual",
    start: str | None = None,
    end: str | None = None,
    statement_type: str | None = None,
    concepts: str | Iterable[str] | None = None,
    units: str | Iterable[str] | None = None,
) -> pd.DataFrame:
    resolved_symbols = resolve_loader_symbols(symbols=symbols, universe_source=universe_source)
    normalized_freq = normalize_loader_freq(freq)
    start_ts, end_ts = normalize_date_range(start=start, end=end)
    concept_list = _normalize_optional_list(concepts)
    unit_list = _normalize_optional_list(units)

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_fundamental")
        where: list[str] = []
        params: list[object] = []

        placeholders = ",".join(["%s"] * len(resolved_symbols))
        where.append(f"symbol IN ({placeholders})")
        params.extend(resolved_symbols)

        where.append("freq = %s")
        params.append(normalized_freq)

        if start_ts is not None:
            where.append("period_end >= %s")
            params.append(start_ts.strftime("%Y-%m-%d"))
        if end_ts is not None:
            where.append("period_end <= %s")
            params.append(end_ts.strftime("%Y-%m-%d"))
        if statement_type:
            where.append("statement_type = %s")
            params.append(statement_type)
        if concept_list:
            placeholders = ",".join(["%s"] * len(concept_list))
            where.append(f"concept IN ({placeholders})")
            params.extend(concept_list)
        if unit_list:
            placeholders = ",".join(["%s"] * len(unit_list))
            where.append(f"unit IN ({placeholders})")
            params.extend(unit_list)

        sql = f"""
        SELECT {", ".join(STATEMENT_VALUE_COLUMNS)}
        FROM nyse_financial_statement_values
        WHERE {" AND ".join(where)}
        ORDER BY symbol ASC, statement_type ASC, concept ASC, period_end ASC, available_at ASC
        """
        rows = db.query(sql, params)
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    for col in ["period_start", "period_end", "filing_date", "report_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    for col in ["accepted_at", "available_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def load_statement_labels(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    statement_type: str | None = None,
    as_of: str | None = None,
) -> pd.DataFrame:
    resolved_symbols = resolve_loader_symbols(symbols=symbols, universe_source=universe_source)

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_fundamental")
        where: list[str] = []
        params: list[object] = []

        placeholders = ",".join(["%s"] * len(resolved_symbols))
        where.append(f"symbol IN ({placeholders})")
        params.extend(resolved_symbols)

        if statement_type:
            where.append("statement_type = %s")
            params.append(statement_type)
        if as_of:
            where.append("as_of = %s")
            params.append(pd.Timestamp(as_of).strftime("%Y-%m-%d"))

        sql = f"""
        SELECT {", ".join(STATEMENT_LABEL_COLUMNS)}
        FROM nyse_financial_statement_labels
        WHERE {" AND ".join(where)}
        ORDER BY symbol ASC, statement_type ASC, concept ASC, as_of ASC
        """
        rows = db.query(sql, params)
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    for col in ["as_of", "latest_filing_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    for col in ["latest_accepted_at", "latest_available_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def load_statement_snapshot_strict(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    as_of_date: str,
    freq: str = "annual",
    statement_type: str | None = None,
    concepts: str | Iterable[str] | None = None,
    units: str | Iterable[str] | None = None,
) -> pd.DataFrame:
    as_of_ts = validate_snapshot_inputs(as_of_date=as_of_date)
    df = load_statement_values(
        symbols=symbols,
        universe_source=universe_source,
        freq=freq,
        statement_type=statement_type,
        concepts=concepts,
        units=units,
    )
    if df.empty:
        return df

    strict = df[
        df["accession_no"].notna()
        & (df["accession_no"] != "")
        & df["unit"].notna()
        & (df["unit"] != "")
        & df["available_at"].notna()
        & (df["available_at"] <= as_of_ts)
    ].copy()
    if strict.empty:
        return strict

    strict = strict.sort_values(
        ["symbol", "statement_type", "concept", "unit", "available_at", "period_end", "accession_no"],
        ascending=[True, True, True, True, True, True, True],
    )
    snapshot = (
        strict.groupby(["symbol", "statement_type", "concept", "unit"], as_index=False)
        .tail(1)
        .sort_values(["symbol", "statement_type", "concept", "unit"])
        .reset_index(drop=True)
    )
    snapshot["as_of_date"] = as_of_ts.normalize()
    return snapshot


def load_statement_coverage_summary(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    freq: str = "annual",
) -> pd.DataFrame:
    df = load_statement_values(
        symbols=symbols,
        universe_source=universe_source,
        freq=freq,
    )
    if df.empty:
        return pd.DataFrame(
            columns=[
                "symbol",
                "freq",
                "strict_rows",
                "distinct_accessions",
                "distinct_period_ends",
                "min_period_end",
                "max_period_end",
                "min_available_at",
                "max_available_at",
                "statement_types",
            ]
        )

    strict = df[
        df["accession_no"].notna()
        & (df["accession_no"] != "")
        & df["unit"].notna()
        & (df["unit"] != "")
        & df["available_at"].notna()
    ].copy()
    if strict.empty:
        return pd.DataFrame(
            columns=[
                "symbol",
                "freq",
                "strict_rows",
                "distinct_accessions",
                "distinct_period_ends",
                "min_period_end",
                "max_period_end",
                "min_available_at",
                "max_available_at",
                "statement_types",
            ]
        )

    summary = (
        strict.groupby("symbol", as_index=False)
        .agg(
            strict_rows=("concept", "size"),
            distinct_accessions=("accession_no", "nunique"),
            distinct_period_ends=("period_end", "nunique"),
            min_period_end=("period_end", "min"),
            max_period_end=("period_end", "max"),
            min_available_at=("available_at", "min"),
            max_available_at=("available_at", "max"),
        )
        .sort_values("symbol")
        .reset_index(drop=True)
    )
    statement_types = (
        strict.groupby("symbol")["statement_type"]
        .apply(lambda s: ",".join(sorted({str(v) for v in s if pd.notna(v)})))
        .reset_index(name="statement_types")
    )
    summary = summary.merge(statement_types, on="symbol", how="left")
    summary["freq"] = normalize_loader_freq(freq)
    return summary[
        [
            "symbol",
            "freq",
            "strict_rows",
            "distinct_accessions",
            "distinct_period_ends",
            "min_period_end",
            "max_period_end",
            "min_available_at",
            "max_available_at",
            "statement_types",
        ]
    ]
