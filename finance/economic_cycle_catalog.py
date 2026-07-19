"""Locked indicator metadata for the U.S. economic-cycle model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorSpec:
    """Describe one source series and its point-in-time monthly transform."""

    series_id: str
    factor: str
    role: str
    frequency: str
    aggregation: str
    transform: str
    direction: int
    minimum_history_months: int


_CATALOG = (
    IndicatorSpec("INDPRO", "activity", "phase_forecast", "monthly", "month_end", "annualized_log_change_6m", 1, 60),
    IndicatorSpec("W875RX1", "activity", "phase_forecast", "monthly", "month_end", "annualized_log_change_6m", 1, 60),
    IndicatorSpec("RRSFS", "activity", "phase_forecast", "monthly", "month_end", "annualized_log_change_6m", 1, 60),
    IndicatorSpec("CFNAI", "activity", "phase_forecast", "monthly", "month_end", "mean_level_3m", 1, 60),
    IndicatorSpec("PAYEMS", "labor_income", "phase_forecast", "monthly", "month_end", "annualized_log_change_3m", 1, 60),
    IndicatorSpec("UNRATE", "labor_income", "phase_forecast", "monthly", "month_end", "level_change_3m", -1, 60),
    IndicatorSpec("ICSA", "labor_income", "phase_forecast", "weekly", "monthly_mean", "log_change_3m", -1, 60),
    IndicatorSpec("AWHMAN", "labor_income", "phase_forecast", "monthly", "month_end", "level_change_3m", 1, 60),
    IndicatorSpec("PERMIT", "financial_leading", "forecast_only", "monthly", "month_end", "annualized_log_change_6m", 1, 60),
    IndicatorSpec("USALOLITOAASTSAM", "financial_leading", "forecast_only", "monthly", "month_end", "cli_gap_and_change_3m", 1, 60),
    IndicatorSpec("T10Y3M", "financial_leading", "forecast_only", "daily", "monthly_mean", "level", 1, 60),
    IndicatorSpec("BAMLH0A0HYM2", "financial_leading", "forecast_only", "daily", "monthly_mean", "level", -1, 60),
    IndicatorSpec("ANFCI", "financial_leading", "forecast_only", "weekly", "month_end", "level", -1, 60),
    IndicatorSpec("PCEPILFE", "inflation_policy", "forecast_context", "monthly", "month_end", "annualized_log_change_3m_minus_2", 1, 60),
    IndicatorSpec("T10YIE", "inflation_policy", "forecast_context", "daily", "monthly_mean", "level_minus_2", 1, 60),
    IndicatorSpec("FEDFUNDS", "inflation_policy", "forecast_context", "monthly", "month_end", "level_change_3m", 1, 60),
    IndicatorSpec("USREC", "recession_anchor", "label_anchor", "monthly", "month_end", "level", 1, 1),
)


def get_economic_cycle_catalog() -> tuple[IndicatorSpec, ...]:
    """Return the immutable V1 catalog in its canonical display/model order."""

    return _CATALOG


def get_indicator_spec(series_id: str) -> IndicatorSpec:
    """Return one catalog item using a normalized FRED series identifier."""

    normalized = str(series_id or "").strip().upper()
    for item in _CATALOG:
        if item.series_id == normalized:
            return item
    raise KeyError(f"Unsupported economic-cycle series: {normalized}")
