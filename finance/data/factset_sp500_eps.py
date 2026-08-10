"""Point-in-time S&P 500 bottom-up EPS vintages from public FactSet reports."""

from __future__ import annotations

import calendar
import csv
import re
import shutil
import subprocess
import tempfile
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pandas as pd
from PIL import Image

from .db.mysql import MySQLClient
from .db.schema import VALUATION_SCHEMAS, sync_table_schema


FACTSET_EARNINGS_SOURCE = "factset_earnings_insight"
FACTSET_EARNINGS_TOPIC_URL = "https://insight.factset.com/topic/earnings"
DB_META = "finance_meta"
MINIMUM_MODEL_VINTAGE_MONTHS = 60
_REPORT_TITLE = "bottom-up eps estimates: current & historical"
_USER_AGENT = "quant-data-pipeline/1.0 (+point-in-time earnings research)"
_LEGACY_REPORT = (
    "https://insight.factset.com/hubfs/Resources%20Section/Research%20Desk/"
    "Earnings%20Insight/EarningsInsight_{stamp}{suffix}.pdf"
)
_WEBSITE_REPORTS = (
    "https://insight.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/"
    "Earnings%20Insight/EarningsInsight_{stamp}{suffix}.pdf",
    "https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/"
    "Earnings%20Insight/EarningsInsight_{stamp}{suffix}.pdf",
    "https://go.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/"
    "Earnings%20Insight/EarningsInsight_{stamp}{suffix}.pdf",
)
_ARCHIVE_RELEASE_DATES = tuple(
    date.fromisoformat(value)
    for value in """
2018-01-19 2018-02-23 2018-03-23 2018-04-27 2018-05-25 2018-06-29
2018-07-27 2018-08-31 2018-09-28 2018-10-26 2018-11-30 2018-12-21
2019-01-25 2019-02-22 2019-03-29 2019-04-26 2019-05-31 2019-06-28
2019-07-26 2019-08-30 2019-09-27 2019-10-25 2019-11-22 2019-12-20
2020-01-31 2020-02-28 2020-03-27 2020-04-24 2020-05-29 2020-06-26
2020-07-31 2020-08-28 2020-09-25 2020-10-30 2020-11-20 2020-12-18
2021-01-29 2021-02-26 2021-03-26 2021-04-30 2021-05-21 2021-06-25
2021-07-30 2021-08-13 2021-09-24 2021-10-29 2021-11-19 2021-12-17
2022-01-28 2022-02-25 2022-03-25 2022-04-29 2022-05-27 2022-06-24
2022-07-29 2022-08-05 2022-09-23 2022-10-28 2022-11-04 2022-12-09
2023-01-20 2023-02-24 2023-03-31 2023-04-28 2023-05-26 2023-06-30
2023-07-28 2023-08-04 2023-09-29 2023-10-13 2023-11-17 2023-12-15
2024-01-19 2024-02-16 2024-03-15 2024-04-19 2024-05-31 2024-06-21
2024-07-26 2024-08-16 2024-09-27 2024-10-25 2024-11-22 2024-12-06
2025-01-31 2025-02-28 2025-03-28 2025-04-25 2025-05-30 2025-06-27
2025-07-25 2025-08-29 2025-09-26 2025-10-31 2025-11-21 2025-12-19
2026-01-30 2026-02-27 2026-03-27 2026-04-24 2026-05-15 2026-06-26
2026-07-31
""".split()
)
_ARCHIVE_RELEASE_BY_MONTH = {
    (release.year, release.month): release for release in _ARCHIVE_RELEASE_DATES
}


@dataclass(frozen=True)
class FactSetEarningsReport:
    release_date: date
    source_ref: str


def _coerce_date(value: str | date, *, field: str) -> date:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Invalid {field}: {value!r}")
    return pd.Timestamp(parsed).date()


def _month_range(start: date, end: date) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        result.append((year, month))
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1
    return tuple(result)


def _fridays(year: int, month: int) -> tuple[date, ...]:
    final_day = calendar.monthrange(year, month)[1]
    return tuple(
        date(year, month, day)
        for day in range(1, final_day + 1)
        if date(year, month, day).weekday() == calendar.FRIDAY
    )


def candidate_factset_report_urls(release_date: date) -> tuple[str, ...]:
    """Return known official FactSet HubSpot paths for one dated report."""

    stamp = release_date.strftime("%m%d%y")
    if release_date.year <= 2019:
        templates = (_LEGACY_REPORT, _WEBSITE_REPORTS[0], *_WEBSITE_REPORTS[1:])
    elif release_date.year <= 2024:
        templates = (_WEBSITE_REPORTS[1], _WEBSITE_REPORTS[0], _LEGACY_REPORT, _WEBSITE_REPORTS[2])
    else:
        templates = (_WEBSITE_REPORTS[0], _WEBSITE_REPORTS[1], _WEBSITE_REPORTS[2], _LEGACY_REPORT)
    urls: list[str] = []
    for template in templates:
        for suffix in ("", "A"):
            url = template.format(stamp=stamp, suffix=suffix)
            if url not in urls:
                urls.append(url)
    return tuple(urls)


def _probe_pdf_url(url: str, *, timeout: int = 15) -> bool:
    request = Request(url, method="HEAD", headers={"User-Agent": _USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = str(response.headers.get("Content-Type") or "").lower()
            return response.status == 200 and "pdf" in content_type
    except Exception:
        return False


def _fetch_pdf(url: str, *, timeout: int = 45) -> bytes:
    for attempt in range(5):
        request = Request(url, headers={"User-Agent": _USER_AGENT})
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = response.read()
            if not payload.startswith(b"%PDF-"):
                raise ValueError(f"FactSet report is not a PDF: {url}")
            return payload
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 4:
                raise
            retry_after = str(exc.headers.get("Retry-After") or "").strip()
            try:
                delay = float(retry_after)
            except ValueError:
                delay = float(2 ** attempt)
            time.sleep(max(0.5, min(delay, 10.0)))
    raise RuntimeError(f"FactSet report download retries exhausted: {url}")


def _archive_source_ref(release_date: date) -> str:
    stamp = release_date.strftime("%m%d%y")
    if release_date.year <= 2019:
        template, suffix = _LEGACY_REPORT, ""
    elif release_date == date(2022, 8, 5):
        template, suffix = _WEBSITE_REPORTS[0], "A"
    elif release_date.year <= 2024:
        template, suffix = _WEBSITE_REPORTS[1], ""
    else:
        template, suffix = _WEBSITE_REPORTS[0], ""
    return template.format(stamp=stamp, suffix=suffix)


def candidate_factset_download_urls(source_ref: str) -> tuple[str, ...]:
    """Return FactSet's portal-owned HubSpot asset URL before the public CNAME."""

    marker = "/hubfs/"
    if marker not in source_ref:
        return (source_ref,)
    asset_path = source_ref.split(marker, 1)[1]
    return (
        f"https://cdn2.hubspot.net/hubfs/1803721/{asset_path}",
        f"https://f.hubspotusercontent20.net/hubfs/1803721/{asset_path}",
        source_ref,
    )


def discover_factset_report_for_month(
    year: int,
    month: int,
    *,
    probe: Callable[[str], bool] = _probe_pdf_url,
) -> FactSetEarningsReport | None:
    """Discover the latest dated Friday report available for a calendar month."""

    archived = _ARCHIVE_RELEASE_BY_MONTH.get((int(year), int(month)))
    if archived is not None:
        return FactSetEarningsReport(
            release_date=archived,
            source_ref=_archive_source_ref(archived),
        )
    for release_date in reversed(_fridays(int(year), int(month))):
        for url in candidate_factset_report_urls(release_date):
            if probe(url):
                return FactSetEarningsReport(release_date=release_date, source_ref=url)
    return None


def discover_factset_monthly_reports(
    months: Iterable[tuple[int, int]],
    *,
    probe: Callable[[str], bool] = _probe_pdf_url,
    max_workers: int = 10,
) -> tuple[tuple[FactSetEarningsReport, ...], tuple[str, ...]]:
    """Discover one latest public report per month without hiding coverage gaps."""

    requested = tuple(dict.fromkeys((int(year), int(month)) for year, month in months))
    found: dict[tuple[int, int], FactSetEarningsReport] = {}
    with ThreadPoolExecutor(max_workers=max(1, int(max_workers))) as executor:
        futures = {
            executor.submit(
                discover_factset_report_for_month, year, month, probe=probe
            ): (year, month)
            for year, month in requested
        }
        for future in as_completed(futures):
            key = futures[future]
            report = future.result()
            if report is not None:
                found[key] = report
    missing = tuple(
        f"{year:04d}-{month:02d}" for year, month in requested if (year, month) not in found
    )
    return (
        tuple(found[key] for key in requested if key in found),
        missing,
    )


def locate_factset_eps_chart_page(pdf_text: str) -> int:
    """Locate the 1-based report page containing the annual/quarterly EPS charts."""

    for page_number, page_text in enumerate(str(pdf_text or "").split("\f"), start=1):
        if _REPORT_TITLE in page_text.casefold():
            return page_number
    raise ValueError("FactSet Bottom-Up EPS chart page was not found")


def _normalized_ocr_number(value: object) -> float | None:
    text = str(value or "").strip().replace("$", "").replace(",", "")
    if not re.fullmatch(r"\d{2,4}\.\d{2}", text):
        return None
    numeric = float(text)
    return numeric if 20.0 <= numeric <= 1000.0 else None


def parse_factset_annual_eps_tsv(
    tsv_text: str,
    *,
    image_width: int,
    image_height: int,
    release_date: str | date,
    source_ref: str,
    collected_at: str | None = None,
) -> list[dict[str, object]]:
    """Map OCR values to the explicitly labelled current/next calendar-year bars.

    FactSet's quarterly chart is a rolling twelve-quarter view, so it is not used to
    reconstruct a full next calendar year. The annual chart already publishes that
    exact bottom-up estimate and is the canonical vintage stored here. FactSet's
    comparable/adjusted analyst EPS is normalized to the existing ``operating`` basis.
    """

    release = _coerce_date(release_date, field="release_date")
    width = int(image_width)
    height = int(image_height)
    if width <= 0 or height <= 0:
        raise ValueError("OCR image dimensions must be positive")
    annual_values: list[tuple[float, float, float]] = []
    year_labels: dict[int, list[float]] = {}
    for row in csv.DictReader(StringIO(str(tsv_text or "")), delimiter="\t"):
        try:
            confidence = float(row.get("conf") or -1.0)
            left = float(row.get("left") or 0.0)
            top = float(row.get("top") or 0.0)
            item_width = float(row.get("width") or 0.0)
            item_height = float(row.get("height") or 0.0)
        except (TypeError, ValueError):
            continue
        center_x = left + item_width / 2.0
        center_y = top + item_height / 2.0
        text = str(row.get("text") or "").strip()
        year_match = re.search(r"20\d{2}", text)
        if (
            confidence >= 0.0
            and year_match
            and 0.43 * height <= center_y <= 0.60 * height
        ):
            year_labels.setdefault(int(year_match.group(0)), []).append(center_x)
        numeric = _normalized_ocr_number(text)
        if (
            confidence >= 25.0
            and numeric is not None
            and center_x >= 0.12 * width
            and 0.14 * height <= center_y <= 0.45 * height
        ):
            annual_values.append((center_x, center_y, numeric))
    if len(annual_values) < 2:
        raise ValueError("FactSet annual EPS bar values could not be verified")

    resolved: dict[int, float] = {}
    for year in (release.year, release.year + 1):
        label_positions = year_labels.get(year) or []
        if not label_positions:
            raise ValueError(f"FactSet CY{year} label could not be verified")
        label_x = max(label_positions)
        value_x, _value_y, value = min(
            annual_values, key=lambda item: abs(item[0] - label_x)
        )
        if abs(value_x - label_x) > 0.045 * width:
            raise ValueError(f"FactSet CY{year} bar could not be verified")
        resolved[year] = value
    ratio = resolved[release.year + 1] / resolved[release.year]
    if not 0.30 <= ratio <= 3.0:
        raise ValueError("FactSet current/next-year EPS relationship failed validation")
    observed_at = collected_at or datetime.now(timezone.utc).isoformat()
    return [
        {
            "period_end": f"{year:04d}-12-31",
            "period_type": "annual",
            "earnings_basis": "operating",
            "value_status": "mixed" if year == release.year else "estimate",
            "eps": float(resolved[year]),
            "source": FACTSET_EARNINGS_SOURCE,
            "source_ref": str(source_ref),
            "source_release_date": release.isoformat(),
            "collected_at": observed_at,
            "error_msg": None,
        }
        for year in (release.year, release.year + 1)
    ]


def _run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    binary = args[0]
    if shutil.which(binary) is None:
        raise RuntimeError(f"Required PDF extraction binary is unavailable: {binary}")
    try:
        return subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "").strip()[:500]
        raise RuntimeError(f"{binary} failed: {message}") from exc


def extract_factset_annual_eps_rows(
    pdf_bytes: bytes,
    *,
    release_date: str | date,
    source_ref: str,
    collected_at: str | None = None,
    render_dpi: int = 400,
) -> list[dict[str, object]]:
    """Extract verified annual EPS bars from one date-stamped public report."""

    if not bytes(pdf_bytes).startswith(b"%PDF-"):
        raise ValueError("FactSet report payload is not a PDF")
    with tempfile.TemporaryDirectory(prefix="factset-eps-") as directory:
        root = Path(directory)
        pdf_path = root / "report.pdf"
        text_path = root / "report.txt"
        image_prefix = root / "eps-chart"
        image_path = root / "eps-chart.png"
        pdf_path.write_bytes(pdf_bytes)
        _run_tool(["pdftotext", "-layout", str(pdf_path), str(text_path)])
        page_number = locate_factset_eps_chart_page(
            text_path.read_text(encoding="utf-8", errors="replace")
        )
        _run_tool(
            [
                "pdftoppm",
                "-f",
                str(page_number),
                "-l",
                str(page_number),
                "-singlefile",
                "-png",
                "-r",
                str(int(render_dpi)),
                str(pdf_path),
                str(image_prefix),
            ]
        )
        if not image_path.exists():
            raise RuntimeError("FactSet EPS chart render was not created")
        with Image.open(image_path) as image:
            image_width, image_height = image.size
        ocr = _run_tool(
            ["tesseract", str(image_path), "stdout", "--psm", "11", "tsv"]
        )
        try:
            return parse_factset_annual_eps_tsv(
                ocr.stdout,
                image_width=image_width,
                image_height=image_height,
                release_date=release_date,
                source_ref=source_ref,
                collected_at=collected_at,
            )
        except ValueError as first_error:
            alternate = _run_tool(
                ["tesseract", str(image_path), "stdout", "--psm", "6", "tsv"]
            )
            alternate_lines = alternate.stdout.splitlines()
            combined = ocr.stdout.rstrip() + "\n" + "\n".join(alternate_lines[1:])
            try:
                return parse_factset_annual_eps_tsv(
                    combined,
                    image_width=image_width,
                    image_height=image_height,
                    release_date=release_date,
                    source_ref=source_ref,
                    collected_at=collected_at,
                )
            except ValueError:
                raise first_error


def _open_meta_db(
    db_factory: Any,
    *,
    host: str,
    user: str,
    password: str,
    port: int,
) -> MySQLClient:
    db = db_factory(host, user, password, port)
    db.use_db(DB_META)
    schema = VALUATION_SCHEMAS["sp500_index_earnings"]
    db.execute(schema)
    sync_table_schema(db, "sp500_index_earnings", schema, DB_META)
    return db


def _upsert_rows(db: MySQLClient, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    db.executemany(
        """
        INSERT INTO sp500_index_earnings (
          period_end, period_type, earnings_basis, value_status, eps, source,
          source_ref, source_release_date, collected_at, error_msg
        ) VALUES (
          %(period_end)s, %(period_type)s, %(earnings_basis)s, %(value_status)s, %(eps)s, %(source)s,
          %(source_ref)s, %(source_release_date)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          eps = VALUES(eps), source_ref = VALUES(source_ref),
          collected_at = VALUES(collected_at), error_msg = VALUES(error_msg)
        """,
        rows,
    )


def collect_and_store_factset_sp500_eps_vintages(
    *,
    start_date: str | date = "2018-01-01",
    end_date: str | date | None = None,
    collected_at: str | None = None,
    report_discoverer: Callable[
        [Iterable[tuple[int, int]]],
        tuple[tuple[FactSetEarningsReport, ...], tuple[str, ...]],
    ] = discover_factset_monthly_reports,
    pdf_fetcher: Callable[[str], bytes] = _fetch_pdf,
    extractor: Callable[..., list[dict[str, object]]] = extract_factset_annual_eps_rows,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    max_workers: int = 1,
) -> dict[str, object]:
    """Backfill missing monthly PIT reports and refresh the latest requested month."""

    start = _coerce_date(start_date, field="start_date")
    end = _coerce_date(end_date or date.today(), field="end_date")
    if start > end:
        raise ValueError("start_date cannot be after end_date")
    observed_at = collected_at or datetime.now(timezone.utc).isoformat()
    db = _open_meta_db(
        db_factory, host=host, user=user, password=password, port=port
    )
    try:
        existing_rows = db.query(
            """
            SELECT source_release_date, COUNT(*) AS row_count,
                   SUM(CASE
                         WHEN YEAR(period_end) = YEAR(source_release_date)
                          AND value_status = 'mixed' THEN 1 ELSE 0
                       END) AS current_year_rows,
                   SUM(CASE
                         WHEN YEAR(period_end) = YEAR(source_release_date) + 1
                          AND value_status = 'estimate' THEN 1 ELSE 0
                       END) AS next_year_rows
            FROM sp500_index_earnings
            WHERE source = %s
              AND period_type = 'annual'
              AND source_release_date >= %s
              AND source_release_date <= %s
            GROUP BY source_release_date
            ORDER BY source_release_date
            """,
            (FACTSET_EARNINGS_SOURCE, start.isoformat(), end.isoformat()),
        )
        complete_dates = {
            _coerce_date(row.get("source_release_date"), field="source_release_date")
            for row in existing_rows
            if row.get("source_release_date") is not None
            and int(row.get("row_count") or 0) >= 2
            and int(row.get("current_year_rows") or 0) >= 1
            and int(row.get("next_year_rows") or 0) >= 1
        }
        existing_months = {(item.year, item.month) for item in complete_dates}
        requested_months = _month_range(start, end)
        months_to_discover = tuple(
            key
            for key in requested_months
            if key not in existing_months or key == (end.year, end.month)
        )
        reports, missing_months = report_discoverer(months_to_discover)
        reports_to_extract = tuple(
            report
            for report in reports
            if (
                report.release_date not in complete_dates
                or (report.release_date.year, report.release_date.month)
                == (end.year, end.month)
            )
        )

        rows: list[dict[str, object]] = []
        failures: list[str] = []

        def extract(report: FactSetEarningsReport) -> list[dict[str, object]]:
            candidate_urls = candidate_factset_download_urls(report.source_ref)
            errors: list[str] = []
            for download_url in candidate_urls:
                try:
                    payload = pdf_fetcher(download_url)
                except Exception as exc:
                    errors.append(f"{type(exc).__name__}:{str(exc)[:120]}")
                    continue
                # All download candidates address the same portal asset. Retrying
                # OCR against another CNAME cannot repair a chart parse failure.
                return extractor(
                    payload,
                    release_date=report.release_date,
                    source_ref=report.source_ref,
                    collected_at=observed_at,
                )
            raise RuntimeError("all official asset URLs failed: " + " | ".join(errors))

        with ThreadPoolExecutor(max_workers=max(1, int(max_workers))) as executor:
            futures = {
                executor.submit(extract, report): report
                for report in reports_to_extract
            }
            for future in as_completed(futures):
                report = futures[future]
                try:
                    extracted = future.result()
                    if len(extracted) != 2:
                        raise ValueError("expected current and next calendar-year rows")
                    rows.extend(extracted)
                except Exception as exc:
                    failures.append(
                        f"{report.release_date.isoformat()}:{type(exc).__name__}:{str(exc)[:240]}"
                    )
        if rows:
            db.begin()
            try:
                _upsert_rows(db, rows)
                db.commit()
            except Exception:
                db.rollback()
                raise
        coverage_rows = db.query(
            """
            SELECT COUNT(DISTINCT source_release_date) AS release_count,
                   MIN(source_release_date) AS first_release_date,
                   MAX(source_release_date) AS latest_release_date
            FROM sp500_index_earnings
            WHERE source = %s
              AND period_type = 'annual'
              AND earnings_basis = 'operating'
              AND value_status = 'estimate'
              AND eps > 0
            """,
            (FACTSET_EARNINGS_SOURCE,),
        )
    finally:
        db.close()
    coverage = coverage_rows[0] if coverage_rows else {}
    release_count = int(coverage.get("release_count") or 0)
    warnings = [*missing_months, *failures]
    coverage_status = (
        "READY"
        if release_count >= MINIMUM_MODEL_VINTAGE_MONTHS and not warnings
        else "LIMITED"
    )
    return {
        "status": "success" if not warnings else "partial_success",
        "rows_written": len(rows),
        "rows": len(rows),
        "source": FACTSET_EARNINGS_SOURCE,
        "source_ref": FACTSET_EARNINGS_TOPIC_URL,
        "coverage_status": coverage_status,
        "release_count": release_count,
        "first_release_date": str(coverage.get("first_release_date") or "")[:10] or None,
        "latest_release_date": str(coverage.get("latest_release_date") or "")[:10] or None,
        "missing_months": list(missing_months),
        "failed_reports": failures,
        "warnings": warnings,
    }
