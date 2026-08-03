from __future__ import annotations

from datetime import date

import pytest


def _tsv(rows: list[tuple[int, int, int, int, float, str]]) -> str:
    header = (
        "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\t"
        "left\ttop\twidth\theight\tconf\ttext"
    )
    body = [
        f"5\t1\t1\t1\t1\t{index}\t{left}\t{top}\t{width}\t{height}\t{confidence}\t{text}"
        for index, (left, top, width, height, confidence, text) in enumerate(
            rows, start=1
        )
    ]
    return "\n".join((header, *body))


def test_factset_tsv_parser_uses_current_and_next_calendar_year_bars() -> None:
    from finance.data.factset_sp500_eps import parse_factset_annual_eps_tsv

    rows = parse_factset_annual_eps_tsv(
        _tsv(
            [
                (450, 1450, 70, 28, 96.0, "119.40"),
                (1550, 1200, 70, 28, 96.0, "208.49"),
                (1950, 1000, 70, 28, 96.0, "239.69"),
                (2110, 850, 70, 28, 96.0, "274.59"),
                (1940, 1700, 90, 25, 92.0, "CY2024"),
                (2100, 1700, 90, 25, 92.0, "CY2025"),
                # Quarterly chart values must never be mistaken for annual EPS.
                (1950, 2700, 70, 28, 96.0, "70.81"),
                (2110, 2750, 70, 28, 96.0, "72.67"),
            ]
        ),
        image_width=2550,
        image_height=3300,
        release_date=date(2024, 11, 8),
        source_ref="https://example.test/EarningsInsight_110824.pdf",
        collected_at="2026-08-03T00:00:00Z",
    )

    assert [(row["period_end"], row["eps"]) for row in rows] == [
        ("2024-12-31", pytest.approx(239.69)),
        ("2025-12-31", pytest.approx(274.59)),
    ]
    assert rows[0]["value_status"] == "mixed"
    assert rows[1]["value_status"] == "estimate"
    assert {row["period_type"] for row in rows} == {"annual"}
    assert {row["source"] for row in rows} == {"factset_earnings_insight"}


def test_factset_tsv_parser_fails_closed_when_year_bar_is_not_verified() -> None:
    from finance.data.factset_sp500_eps import parse_factset_annual_eps_tsv

    with pytest.raises(ValueError, match="CY2025"):
        parse_factset_annual_eps_tsv(
            _tsv(
                [
                    (1950, 1000, 70, 28, 96.0, "239.69"),
                    (2110, 850, 70, 28, 96.0, "274.59"),
                    (1940, 1700, 90, 25, 92.0, "CY2024"),
                ]
            ),
            image_width=2550,
            image_height=3300,
            release_date=date(2024, 11, 8),
            source_ref="https://example.test/EarningsInsight_110824.pdf",
        )


def test_factset_tsv_parser_rejects_geometry_without_explicit_year_labels() -> None:
    from finance.data.factset_sp500_eps import parse_factset_annual_eps_tsv

    with pytest.raises(ValueError, match="CY2020"):
        parse_factset_annual_eps_tsv(
            _tsv(
                [
                    (450 + index * 160, 1500 - index * 30, 70, 28, 94.0, f"{100 + index * 8:.2f}")
                    for index in range(10)
                ]
            ),
            image_width=2050,
            image_height=3300,
            release_date=date(2020, 7, 31),
            source_ref="https://example.test/EarningsInsight_073120.pdf",
        )


def test_factset_report_candidates_cover_legacy_mirrors_and_a_suffix() -> None:
    from finance.data.factset_sp500_eps import candidate_factset_report_urls

    urls = candidate_factset_report_urls(date(2022, 8, 5))

    assert any("insight.factset.com/hubfs/Resources%20Section" in url for url in urls)
    assert any("advantage.factset.com/hubfs/Website/Resources%20Section" in url for url in urls)
    assert any(url.endswith("EarningsInsight_080522A.pdf") for url in urls)


def test_verified_archive_month_does_not_require_reprobing_every_candidate() -> None:
    from finance.data.factset_sp500_eps import discover_factset_report_for_month

    report = discover_factset_report_for_month(
        2022,
        8,
        probe=lambda _url: (_ for _ in ()).throw(AssertionError("unexpected probe")),
    )

    assert report is not None
    assert report.release_date == date(2022, 8, 5)
    assert report.source_ref.endswith("EarningsInsight_080522A.pdf")


def test_factset_download_candidates_include_portal_owned_hubspot_asset() -> None:
    from finance.data.factset_sp500_eps import candidate_factset_download_urls

    source_ref = (
        "https://insight.factset.com/hubfs/Website/Resources%20Section/"
        "Research%20Desk/Earnings%20Insight/EarningsInsight_073126.pdf"
    )

    urls = candidate_factset_download_urls(source_ref)

    assert urls[0].startswith("https://cdn2.hubspot.net/hubfs/1803721/")
    assert urls[-1] == source_ref


def test_factset_pdf_page_locator_is_case_insensitive() -> None:
    from finance.data.factset_sp500_eps import locate_factset_eps_chart_page

    text = "cover\fBottom-up EPS Estimates: Current & Historical\nchart\flegal"

    assert locate_factset_eps_chart_page(text) == 2


def test_collector_reextracts_partial_and_latest_release(monkeypatch) -> None:
    from finance.data import factset_sp500_eps as module

    class FakeDB:
        def __init__(self) -> None:
            self.written: list[dict[str, object]] = []

        def query(self, sql: str, _params=()):
            if "GROUP BY source_release_date" in sql:
                return [
                    {
                        "source_release_date": date(2025, 4, 25),
                        "row_count": 1,
                        "current_year_rows": 1,
                        "next_year_rows": 0,
                    }
                ]
            if "COUNT(DISTINCT source_release_date)" in sql:
                return [
                    {
                        "release_count": 60,
                        "first_release_date": date(2020, 5, 29),
                        "latest_release_date": date(2025, 4, 25),
                    }
                ]
            raise AssertionError(sql)

        def executemany(self, _sql: str, rows):
            self.written.extend(dict(row) for row in rows)

        def begin(self):
            return None

        def commit(self):
            return None

        def rollback(self):
            return None

        def close(self):
            return None

    db = FakeDB()
    monkeypatch.setattr(module, "_open_meta_db", lambda *_args, **_kwargs: db)
    report = module.FactSetEarningsReport(
        release_date=date(2025, 4, 25),
        source_ref="https://example.test/EarningsInsight_042525.pdf",
    )
    discovered: list[tuple[tuple[int, int], ...]] = []

    def discover(months):
        discovered.append(tuple(months))
        return (report,), ()

    def extract(_payload, **kwargs):
        release = kwargs["release_date"]
        return [
            {
                "period_end": f"{release.year}-12-31",
                "period_type": "annual",
                "earnings_basis": "operating",
                "value_status": "mixed",
                "eps": 250.0,
                "source": module.FACTSET_EARNINGS_SOURCE,
                "source_ref": kwargs["source_ref"],
                "source_release_date": release.isoformat(),
                "collected_at": kwargs["collected_at"],
                "error_msg": None,
            },
            {
                "period_end": f"{release.year + 1}-12-31",
                "period_type": "annual",
                "earnings_basis": "operating",
                "value_status": "estimate",
                "eps": 275.0,
                "source": module.FACTSET_EARNINGS_SOURCE,
                "source_ref": kwargs["source_ref"],
                "source_release_date": release.isoformat(),
                "collected_at": kwargs["collected_at"],
                "error_msg": None,
            },
        ]

    result = module.collect_and_store_factset_sp500_eps_vintages(
        start_date="2025-04-01",
        end_date="2025-04-30",
        collected_at="2025-04-30T23:59:59Z",
        report_discoverer=discover,
        pdf_fetcher=lambda _url: b"%PDF-fake",
        extractor=extract,
    )

    assert discovered == [((2025, 4),)]
    assert len(db.written) == 2
    assert result["rows_written"] == 2
