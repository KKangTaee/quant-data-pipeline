"""Parse and persist official FOMC SEP distributions without participant mapping."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Callable, Iterable, Mapping, Sequence
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, Tag

from .db.mysql import MySQLClient
from .db.schema import INFLATION_POLICY_SCHEMAS, sync_table_schema


FED_BASE_URL = "https://www.federalreserve.gov"
DB_META = "finance_meta"
FOMC_CALENDAR_URL = f"{FED_BASE_URL}/monetarypolicy/fomccalendars.htm"
SEP_PARSER_VERSION = "fomc_sep_v1"

_VARIABLE_LABELS = {
    "change in real gdp": "real_gdp",
    "unemployment rate": "unemployment_rate",
    "pce inflation": "pce",
    "core pce inflation": "core_pce",
    "federal funds rate": "federal_funds_rate",
}

_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def _clean_text(value: object) -> str:
    text = " ".join(str(value or "").replace("\xa0", " ").split()).strip()
    text = text.replace("–", "-").replace("—", "-")
    return re.sub(r"\s*-\s*", "-", text)


def _sql_datetime(value: str, *, field: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.strftime("%Y-%m-%d %H:%M:%S.%f")


def _source_date(source_url: str) -> date:
    match = re.search(r"(\d{8})(?=\.htm(?:l)?(?:$|\?))", str(source_url))
    if match is None:
        raise ValueError("Projection source URL has no release date")
    return datetime.strptime(match.group(1), "%Y%m%d").date()


def _target_period(value: str) -> str:
    normalized = _clean_text(value).casefold()
    if re.fullmatch(r"20\d{2}", normalized):
        return normalized
    if normalized == "longer run":
        return "longer_run"
    raise ValueError(f"Unsupported SEP target period: {value!r}")


def _count(value: object) -> int:
    text = _clean_text(value)
    if not text:
        return 0
    if not re.fullmatch(r"\d+", text):
        raise ValueError(f"Invalid participant count: {value!r}")
    return int(text)


def _number(value: object) -> float | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _range(value: object) -> tuple[float | None, float | None]:
    text = _clean_text(value)
    if not text:
        return None, None
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)-(-?\d+(?:\.\d+)?)", text)
    if match is not None:
        return float(match.group(1)), float(match.group(2))
    scalar = _number(text)
    return (scalar, scalar) if scalar is not None else (None, None)


def _variable_from_text(value: str) -> str | None:
    normalized = _clean_text(value).casefold()
    normalized = re.sub(r"\d+$", "", normalized).strip()
    for label, variable in sorted(
        _VARIABLE_LABELS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if normalized.startswith(label):
            return variable
    return None


def _base_row(
    *,
    source_url: str,
    released_at: str,
    collected_at: str,
    target_period: str,
    variable_name: str,
    distribution_kind: str,
    bin_label: str,
    bin_value_pct: float | None,
    bin_lower_pct: float | None,
    bin_upper_pct: float | None,
    participant_count: int,
) -> dict[str, object]:
    return {
        "meeting_date": _source_date(source_url).isoformat(),
        "released_at": _sql_datetime(released_at, field="released_at"),
        "target_period": target_period,
        "variable_name": variable_name,
        "distribution_kind": distribution_kind,
        "bin_label": bin_label,
        "bin_value_pct": bin_value_pct,
        "bin_lower_pct": bin_lower_pct,
        "bin_upper_pct": bin_upper_pct,
        "participant_count": int(participant_count),
        "units": "percent",
        "source": "federal_reserve_sep",
        "source_ref": source_url,
        "parser_version": SEP_PARSER_VERSION,
        "collected_at": _sql_datetime(collected_at, field="collected_at"),
    }


def _table_containers(soup: BeautifulSoup) -> list[tuple[str, Tag]]:
    found: list[tuple[str, Tag]] = []
    for container in soup.select("div.data-table"):
        heading = container.find(["h3", "h4", "h5"], class_="tablehead")
        table = container.find("table", recursive=False) or container.find("table")
        if heading is not None and isinstance(table, Tag):
            found.append((_clean_text(heading.get_text(" ")), table))
    return found


def _parse_summary(
    heading: str,
    table: Tag,
    *,
    source_url: str,
    released_at: str,
    collected_at: str,
) -> list[dict[str, object]]:
    if not heading.casefold().startswith("table 1."):
        return []
    header_rows = table.select("thead tr")
    if not header_rows:
        return []
    periods = [
        _clean_text(cell.get_text(" "))
        for cell in header_rows[-1].find_all(["th", "td"], recursive=False)
        if _clean_text(cell.get_text(" ")).casefold() in {"2026", "2027", "2028", "longer run"}
    ]
    if len(periods) != 12:
        raise ValueError("SEP summary header must contain 12 target-period cells")

    rows: list[dict[str, object]] = []
    group_labels = ("median", "central_tendency", "range")
    for tr in table.select("tbody tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        if len(cells) < 13:
            continue
        variable = _variable_from_text(cells[0].get_text(" "))
        if variable is None:
            continue
        values = cells[1:13]
        for group_index, group_label in enumerate(group_labels):
            for period_index in range(4):
                value_text = _clean_text(
                    values[group_index * 4 + period_index].get_text(" ")
                )
                if not value_text:
                    continue
                target = _target_period(periods[group_index * 4 + period_index])
                lower, upper = _range(value_text)
                value = _number(value_text) if group_label == "median" else None
                rows.append(
                    _base_row(
                        source_url=source_url,
                        released_at=released_at,
                        collected_at=collected_at,
                        target_period=target,
                        variable_name=variable,
                        distribution_kind="SUMMARY",
                        bin_label=group_label,
                        bin_value_pct=value,
                        bin_lower_pct=lower,
                        bin_upper_pct=upper,
                        participant_count=0,
                    )
                )
    return rows


def _parse_dots(
    heading: str,
    table: Tag,
    *,
    source_url: str,
    released_at: str,
    collected_at: str,
) -> list[dict[str, object]]:
    if not heading.casefold().startswith("figure 2."):
        return []
    header = table.select_one("thead tr")
    if header is None:
        return []
    header_cells = header.find_all(["th", "td"], recursive=False)
    periods = [_target_period(cell.get_text(" ")) for cell in header_cells[1:]]
    rows: list[dict[str, object]] = []
    for tr in table.select("tbody tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        if len(cells) < 2:
            continue
        value = _number(cells[0].get_text(" "))
        if value is None:
            continue
        for target, cell in zip(periods, cells[1:]):
            participant_count = _count(cell.get_text(" "))
            if participant_count == 0:
                continue
            rows.append(
                _base_row(
                    source_url=source_url,
                    released_at=released_at,
                    collected_at=collected_at,
                    target_period=target,
                    variable_name="federal_funds_rate",
                    distribution_kind="DOT",
                    bin_label=f"{value:.3f}",
                    bin_value_pct=value,
                    bin_lower_pct=value,
                    bin_upper_pct=value,
                    participant_count=participant_count,
                )
            )
    return rows


def _histogram_variable(heading: str) -> str | None:
    normalized = heading.casefold()
    if not normalized.startswith("figure 3."):
        return None
    if "core pce inflation" in normalized:
        return "core_pce"
    if "pce inflation" in normalized:
        return "pce"
    if "unemployment rate" in normalized:
        return "unemployment_rate"
    if "real gdp" in normalized:
        return "real_gdp"
    if "federal funds rate" in normalized or "appropriate target range" in normalized:
        return "federal_funds_rate"
    return None


def _parse_histogram(
    heading: str,
    table: Tag,
    *,
    release_month: str,
    source_url: str,
    released_at: str,
    collected_at: str,
) -> list[dict[str, object]]:
    variable = _histogram_variable(heading)
    if variable is None:
        return []
    header_rows = table.select("thead tr")
    if len(header_rows) < 2:
        return []
    first_cells = header_rows[0].find_all(["th", "td"], recursive=False)
    periods = [_target_period(cell.get_text(" ")) for cell in first_cells[1:]]
    projection_cells = header_rows[-1].find_all(["th", "td"], recursive=False)
    projections = [_clean_text(cell.get_text(" ")) for cell in projection_cells]
    if len(projections) != len(periods) * 2:
        raise ValueError(f"SEP histogram header mismatch: {heading}")

    selected_columns: list[tuple[str, int]] = []
    for index, target in enumerate(periods):
        pair = projections[index * 2 : index * 2 + 2]
        matches = [
            offset
            for offset, label in enumerate(pair)
            if label.casefold().startswith(release_month.casefold())
        ]
        if len(matches) != 1:
            raise ValueError(f"SEP histogram current-release column missing: {heading}")
        selected_columns.append((target, index * 2 + matches[0]))

    rows: list[dict[str, object]] = []
    for tr in table.select("tbody tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        if len(cells) < 2:
            continue
        bin_label = _clean_text(cells[0].get_text(" "))
        lower, upper = _range(bin_label)
        if lower is None or upper is None:
            continue
        values = cells[1:]
        for target, column in selected_columns:
            if column >= len(values):
                continue
            participant_count = _count(values[column].get_text(" "))
            if participant_count == 0:
                continue
            rows.append(
                _base_row(
                    source_url=source_url,
                    released_at=released_at,
                    collected_at=collected_at,
                    target_period=target,
                    variable_name=variable,
                    distribution_kind="HISTOGRAM",
                    bin_label=bin_label,
                    bin_value_pct=None,
                    bin_lower_pct=lower,
                    bin_upper_pct=upper,
                    participant_count=participant_count,
                )
            )
    return rows


def _expected_participant_count(soup: BeautifulSoup) -> int | None:
    page_text = _clean_text(soup.get_text(" ")).casefold()
    match = re.search(r"([a-z]+|\d+) participants submitted information", page_text)
    if match is None:
        return None
    token = match.group(1)
    return int(token) if token.isdigit() else _NUMBER_WORDS.get(token)


def _validate_current_totals(
    rows: Sequence[Mapping[str, object]],
    *,
    expected: int | None,
) -> None:
    if expected is None:
        dot_total = sum(
            int(row["participant_count"])
            for row in rows
            if row["distribution_kind"] == "DOT"
            and row["target_period"] == "2026"
        )
        expected = dot_total or None
    if expected is None:
        raise ValueError("SEP participant total could not be established")

    totals: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        if row["target_period"] != "2026" or row["distribution_kind"] == "SUMMARY":
            continue
        totals[(str(row["variable_name"]), str(row["distribution_kind"]))] += int(
            row["participant_count"]
        )
    for key, total in totals.items():
        if total != expected:
            raise ValueError(
                f"SEP participant total mismatch for {key[0]} {key[1]}: {total} != {expected}"
            )


def discover_fomc_projection_urls(calendar_html: str) -> list[str]:
    """Return dated official accessible SEP pages discovered from the calendar."""

    soup = BeautifulSoup(calendar_html, "html.parser")
    urls = {
        urljoin(FED_BASE_URL, str(anchor.get("href")))
        for anchor in soup.find_all("a", href=True)
        if re.search(
            r"/monetarypolicy/fomcprojtabl\d{8}\.htm(?:l)?$",
            str(anchor.get("href")),
            flags=re.IGNORECASE,
        )
    }
    return sorted(urls)


def _fetch_official_html(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "quant-data-pipeline/1.0 research@example.com"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _extract_released_at(html: str, *, source_url: str) -> str:
    """Resolve the official 2 p.m. ET SEP release to an aware UTC timestamp."""

    page_text = _clean_text(BeautifulSoup(html, "html.parser").get_text(" "))
    match = re.search(
        r"For release at\s+(\d{1,2}):(\d{2})\s+([ap])\.m\.,\s*"
        r"(?:EDT|EST|ET),\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
        page_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        raise ValueError(f"Official SEP release timestamp was not found: {source_url}")
    hour = int(match.group(1)) % 12
    if match.group(3).casefold() == "p":
        hour += 12
    local_date = datetime.strptime(match.group(4), "%B %d, %Y")
    local = local_date.replace(
        hour=hour,
        minute=int(match.group(2)),
        tzinfo=ZoneInfo("America/New_York"),
    )
    if local.date() != _source_date(source_url):
        raise ValueError("SEP page timestamp does not match its dated source URL")
    return local.astimezone(timezone.utc).isoformat()


def parse_fomc_sep_distributions(
    html: str,
    *,
    source_url: str,
    released_at: str,
    collected_at: str,
) -> list[dict[str, object]]:
    """Parse anonymous SEP tables selected by their official headings."""

    soup = BeautifulSoup(html, "html.parser")
    release_month = _source_date(source_url).strftime("%B")
    rows: list[dict[str, object]] = []
    for heading, table in _table_containers(soup):
        rows.extend(
            _parse_summary(
                heading,
                table,
                source_url=source_url,
                released_at=released_at,
                collected_at=collected_at,
            )
        )
        rows.extend(
            _parse_dots(
                heading,
                table,
                source_url=source_url,
                released_at=released_at,
                collected_at=collected_at,
            )
        )
        rows.extend(
            _parse_histogram(
                heading,
                table,
                release_month=release_month,
                source_url=source_url,
                released_at=released_at,
                collected_at=collected_at,
            )
        )
    if not any(row["distribution_kind"] == "DOT" for row in rows):
        raise ValueError("SEP exact rate-dot table was not found")
    if not any(row["variable_name"] == "core_pce" for row in rows):
        raise ValueError("SEP core PCE distribution was not found")
    _validate_current_totals(rows, expected=_expected_participant_count(soup))
    return sorted(
        rows,
        key=lambda row: (
            str(row["distribution_kind"]),
            str(row["variable_name"]),
            str(row["target_period"]),
            str(row["bin_label"]),
        ),
    )


def upsert_fomc_sep_distributions(
    rows: Iterable[Mapping[str, object]],
    *,
    db: object,
) -> int:
    """Idempotently persist anonymous bins by the release distribution key."""

    prepared = [dict(row) for row in rows]
    if not prepared:
        return 0
    sql = """
    INSERT INTO fomc_sep_distribution (
      meeting_date, released_at, target_period, variable_name,
      distribution_kind, bin_label, bin_value_pct, bin_lower_pct,
      bin_upper_pct, participant_count, units, source, source_ref,
      parser_version, collected_at
    ) VALUES (
      %(meeting_date)s, %(released_at)s, %(target_period)s, %(variable_name)s,
      %(distribution_kind)s, %(bin_label)s, %(bin_value_pct)s, %(bin_lower_pct)s,
      %(bin_upper_pct)s, %(participant_count)s, %(units)s, %(source)s, %(source_ref)s,
      %(parser_version)s, %(collected_at)s
    )
    ON DUPLICATE KEY UPDATE
      meeting_date = VALUES(meeting_date),
      bin_value_pct = VALUES(bin_value_pct),
      bin_lower_pct = VALUES(bin_lower_pct),
      bin_upper_pct = VALUES(bin_upper_pct),
      participant_count = VALUES(participant_count),
      source_ref = VALUES(source_ref),
      parser_version = VALUES(parser_version),
      collected_at = VALUES(collected_at)
    """
    db.executemany(sql, prepared)
    return len(prepared)


def collect_and_store_fomc_sep_distributions(
    *,
    calendar_url: str = FOMC_CALENDAR_URL,
    connection: object | None = None,
    fetch_html: Callable[[str], str] | None = None,
    collected_at: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, int]:
    """Discover official accessible SEP pages and persist their anonymous bins."""

    fetcher = fetch_html or _fetch_official_html
    source_urls = discover_fomc_projection_urls(fetcher(calendar_url))
    if not source_urls:
        raise ValueError("No official accessible SEP pages were discovered")
    observed_at = collected_at or datetime.now(timezone.utc).isoformat()

    owns_connection = connection is None
    db = connection or MySQLClient(host, user, password, port)
    stored = 0
    try:
        db.use_db(DB_META)
        schema = INFLATION_POLICY_SCHEMAS["fomc_sep_distribution"]
        db.execute(schema)
        sync_table_schema(db, "fomc_sep_distribution", schema, DB_META)
        for source_url in source_urls:
            page = fetcher(source_url)
            rows = parse_fomc_sep_distributions(
                page,
                source_url=source_url,
                released_at=_extract_released_at(page, source_url=source_url),
                collected_at=observed_at,
            )
            stored += upsert_fomc_sep_distributions(rows, db=db)
    finally:
        if owns_connection:
            db.close()
    return {"releases": len(source_urls), "stored": stored}
