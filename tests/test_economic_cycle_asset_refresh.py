from __future__ import annotations


def test_asset_refresh_uses_only_economic_cycle_pathway_sources() -> None:
    from app.jobs.economic_cycle_asset_refresh import (
        run_economic_cycle_asset_pathway_refresh,
    )

    calls: dict[str, object] = {}

    def macro_runner(**kwargs):
        calls["macro"] = kwargs
        return {
            "job_name": "macro",
            "status": "success",
            "rows_written": 9,
            "failed_symbols": [],
        }

    def futures_runner(**kwargs):
        calls["futures"] = kwargs
        return {
            "job_name": "futures",
            "status": "success",
            "rows_written": 4,
            "failed_symbols": [],
        }

    def equity_runner(symbols, **kwargs):
        calls["equity"] = {"symbols": symbols, **kwargs}
        return {
            "job_name": "equity",
            "status": "success",
            "rows_written": 2,
            "failed_symbols": [],
        }

    result = run_economic_cycle_asset_pathway_refresh(
        macro_runner=macro_runner,
        futures_runner=futures_runner,
        equity_runner=equity_runner,
    )

    assert tuple(calls["macro"]["series_ids"]) == (
        "DGS2",
        "DGS10",
        "DFII10",
        "T10YIE",
        "VIXCLS",
        "BAA10Y",
        "WCESTUS1",
        "WCRFPUS2",
        "WRPUPUS2",
    )
    assert calls["futures"]["symbols"] == [
        "GC=F",
        "DX-Y.NYB",
        "CL=F",
        "HG=F",
    ]
    assert calls["futures"]["period"] == "1y"
    assert calls["futures"]["interval"] == "1d"
    assert calls["equity"]["symbols"] == ["^GSPC", "SPY"]
    assert result["status"] == "success"
    assert result["rows_written"] == 15


def test_asset_refresh_keeps_price_success_when_macro_fails() -> None:
    from app.jobs.economic_cycle_asset_refresh import (
        run_economic_cycle_asset_pathway_refresh,
    )

    result = run_economic_cycle_asset_pathway_refresh(
        macro_runner=lambda **_kwargs: {
            "job_name": "macro",
            "status": "failed",
            "rows_written": 0,
            "failed_symbols": ["DGS2"],
        },
        futures_runner=lambda **_kwargs: {
            "job_name": "futures",
            "status": "success",
            "rows_written": 4,
            "failed_symbols": [],
        },
        equity_runner=lambda *_args, **_kwargs: {
            "job_name": "equity",
            "status": "success",
            "rows_written": 2,
            "failed_symbols": [],
        },
    )

    assert result["status"] == "partial_success"
    assert result["rows_written"] == 6
    assert result["failed_symbols"] == ["DGS2"]
    assert [row["scope"] for row in result["details"]["steps"]] == [
        "macro",
        "futures",
        "equity",
    ]
