"""Parse and persist official FOMC SEP distributions without participant mapping."""

from __future__ import annotations

import hashlib
import json
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
FOMC_HISTORICAL_URL = f"{FED_BASE_URL}/monetarypolicy/fomchistorical{{year}}.htm"
SEP_PARSER_VERSION = "fomc_sep_v2"
DECISION_PARSER_VERSION = "fomc_decision_v2"

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
    text = (
        text.replace("–", "-")
        .replace("—", "-")
        .replace("‑", "-")
        .replace("−", "-")
    )
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
    match = re.search(
        r"(\d{8})(?:[a-z]\d*)?(?=\.htm(?:l)?(?:$|\?))",
        str(source_url),
        flags=re.IGNORECASE,
    )
    if match is None:
        raise ValueError("Federal Reserve source URL has no release date")
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


def _mixed_fraction(value: str) -> float:
    text = _clean_text(value)
    whole_match = re.fullmatch(r"(\d+)-(\d+)/(\d+)", text)
    if whole_match is not None:
        return int(whole_match.group(1)) + int(whole_match.group(2)) / int(
            whole_match.group(3)
        )
    fraction_match = re.fullmatch(r"(\d+)/(\d+)", text)
    if fraction_match is not None:
        return int(fraction_match.group(1)) / int(fraction_match.group(2))
    return float(text)


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
        if heading is None:
            # Historical accessible SEP pages place the table heading directly
            # before the data-table container instead of nesting it inside.
            heading = container.find_previous(["h3", "h4", "h5"])
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
    normalized_heading = heading.casefold()
    if not (
        normalized_heading.startswith("table 1.")
        or normalized_heading.startswith("advance release of table 1")
    ):
        return []
    header_rows = table.select("thead tr")
    if not header_rows:
        return []
    periods: list[str] = []
    for cell in header_rows[-1].find_all(["th", "td"], recursive=False):
        label = _clean_text(cell.get_text(" "))
        try:
            _target_period(label)
        except ValueError:
            continue
        periods.append(label)
    if not periods or len(periods) % 3 != 0:
        raise ValueError("SEP summary header must contain three target-period groups")
    period_count = len(periods) // 3
    expected_periods = [_target_period(item) for item in periods[:period_count]]
    if any(
        [_target_period(item) for item in periods[index * period_count : (index + 1) * period_count]]
        != expected_periods
        for index in range(1, 3)
    ):
        raise ValueError("SEP summary target-period groups must match")

    rows: list[dict[str, object]] = []
    group_labels = ("median", "central_tendency", "range")
    for tr in table.select("tbody tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        if len(cells) < len(periods) + 1:
            continue
        variable = _variable_from_text(cells[0].get_text(" "))
        if variable is None:
            continue
        values = cells[1 : len(periods) + 1]
        for group_index, group_label in enumerate(group_labels):
            for period_index in range(period_count):
                value_text = _clean_text(
                    values[group_index * period_count + period_index].get_text(" ")
                )
                if not value_text:
                    continue
                target = _target_period(
                    periods[group_index * period_count + period_index]
                )
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
    period_specs = [
        (
            _target_period(cell.get_text(" ")),
            int(str(cell.get("colspan") or "1")),
        )
        for cell in first_cells[1:]
    ]
    projection_cells = header_rows[-1].find_all(["th", "td"], recursive=False)
    projections = [_clean_text(cell.get_text(" ")) for cell in projection_cells]
    if len(projections) != sum(width for _target, width in period_specs):
        raise ValueError(f"SEP histogram header mismatch: {heading}")

    selected_columns: list[tuple[str, int]] = []
    offset = 0
    for target, width in period_specs:
        group = projections[offset : offset + width]
        matches = [
            group_offset
            for group_offset, label in enumerate(group)
            if label.casefold().startswith(release_month.casefold())
        ]
        if len(matches) != 1:
            raise ValueError(f"SEP histogram current-release column missing: {heading}")
        selected_columns.append((target, offset + matches[0]))
        offset += width

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


def _expected_participant_count(
    soup: BeautifulSoup,
    *,
    release_month: str,
) -> int | None:
    page_text = _clean_text(soup.get_text(" ")).casefold()
    matches = list(
        re.finditer(r"([a-z]+|\d+) participants submitted information", page_text)
    )
    if not matches:
        return None
    current = [
        match
        for match in matches
        if release_month.casefold() in page_text[match.end() : match.end() + 160]
    ]
    match = current[-1] if current else matches[-1]
    token = match.group(1)
    return int(token) if token.isdigit() else _NUMBER_WORDS.get(token)


def _validate_current_totals(
    rows: Sequence[Mapping[str, object]],
    *,
    expected: int | None,
    current_period: str,
) -> None:
    if expected is None:
        dot_total = sum(
            int(row["participant_count"])
            for row in rows
            if row["distribution_kind"] == "DOT"
            and row["target_period"] == current_period
        )
        expected = dot_total or None
    if expected is None:
        raise ValueError("SEP participant total could not be established")

    totals: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        if row["target_period"] != current_period or row["distribution_kind"] == "SUMMARY":
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


def discover_historical_fomc_projection_urls(history_html: str) -> list[str]:
    """Derive official accessible SEP URLs from historical SEP compilation links."""

    soup = BeautifulSoup(history_html, "html.parser")
    release_dates = {
        match.group(1)
        for anchor in soup.find_all("a", href=True)
        if (
            match := re.search(
                r"/monetarypolicy/files/FOMC(\d{8})SEPcompilation\.pdf$",
                str(anchor.get("href")),
                flags=re.IGNORECASE,
            )
        )
    }
    return [
        f"{FED_BASE_URL}/monetarypolicy/fomcprojtabl{release_date}.htm"
        for release_date in sorted(release_dates)
    ]


def discover_fomc_statement_urls(calendar_html: str) -> list[str]:
    """Return dated official FOMC statement pages, oldest first."""

    soup = BeautifulSoup(calendar_html, "html.parser")
    calendar_layout = bool(soup.select(".fomc-meeting"))
    historical_layout = bool(
        re.search(r"\bMeeting\s*-\s*20\d{2}\b", _clean_text(soup.get_text(" ")))
    )
    urls: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href"))
        if re.search(
            r"/newsevents/pressreleases/monetary\d{8}a\.htm(?:l)?$",
            href,
            flags=re.IGNORECASE,
        ) is None:
            continue
        if calendar_layout:
            parent_text = _clean_text(anchor.parent.get_text(" ")).casefold()
            if _clean_text(anchor.get_text(" ")).casefold() != "html" or not (
                parent_text.startswith("statement:")
                or parent_text.startswith("statement :")
            ):
                continue
        elif historical_layout:
            if _clean_text(anchor.get_text(" ")).casefold() != "statement":
                continue
            panel = anchor.find_parent(class_=lambda value: value and "panel" in value)
            heading = panel.find(["h3", "h4", "h5"]) if panel is not None else None
            heading_text = _clean_text(heading.get_text(" ")) if heading is not None else ""
            if re.search(r"\bMeeting\s*-\s*20\d{2}\b", heading_text) is None:
                continue
        urls.add(urljoin(FED_BASE_URL, href))
    return sorted(urls, key=lambda url: (_source_date(url), url))


def _preferred_action(
    dissent_text: str,
    *,
    target_after: tuple[float, float] | None = None,
) -> tuple[str, int]:
    normalized = _clean_text(dissent_text).casefold()
    if "did not support inclusion of an easing bias" in normalized:
        return "HOLD_NO_EASING_BIAS", 0
    if "raise" in normalized or "increase" in normalized:
        direction = "HIKE"
    elif "lower" in normalized or "reduce" in normalized:
        direction = "CUT"
    elif "maintain" in normalized or "no change" in normalized:
        return "HOLD", 0
    else:
        raise ValueError("FOMC dissent direction was not recognized")
    change = re.search(
        r"by\s+(\d+(?:-\d+/\d+|/\d+)?|\d+(?:\.\d+)?)\s+percentage point",
        normalized,
    )
    if change is not None:
        basis_points = round(_mixed_fraction(change.group(1)) * 100)
        return f"{direction}_{basis_points}", basis_points
    basis_point_change = re.search(r"by\s+(\d+)\s+basis points?", normalized)
    if basis_point_change is not None:
        basis_points = int(basis_point_change.group(1))
        return f"{direction}_{basis_points}", basis_points
    preferred_range = re.search(
        r"(?:at|to)\s+(\d+(?:-\d+/\d+|/\d+|\.\d+)?)\s+to\s+"
        r"(\d+(?:-\d+/\d+|/\d+|\.\d+)?)\s+percent",
        normalized,
    )
    if preferred_range is None or target_after is None:
        raise ValueError("FOMC dissent change size was not found")
    preferred_midpoint = (
        _mixed_fraction(preferred_range.group(1))
        + _mixed_fraction(preferred_range.group(2))
    ) / 2.0
    actual_midpoint = (float(target_after[0]) + float(target_after[1])) / 2.0
    basis_points = round(abs(preferred_midpoint - actual_midpoint) * 100)
    if basis_points <= 0:
        raise ValueError("FOMC dissent change size was not found")
    return f"{direction}_{basis_points}", basis_points


def _split_member_names(value: str) -> list[str]:
    text = _clean_text(value).strip(" .;")
    text = re.sub(
        r",\s*(?:Vice\s+)?Chair(?:man)?\s*,\s*",
        "; ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r",\s*(?:Vice\s+)?Chair(?:man)?(?=\s*;|$)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    if ";" in text:
        items = [item.strip() for item in text.split(";")]
    else:
        items = re.sub(r",?\s+and\s+", ", ", text).split(",")
    names: list[str] = []
    for item in items:
        name = re.sub(r"^and\s+", "", item.strip(), flags=re.IGNORECASE)
        if name:
            names.append(name)
    return names


def _vote_for_names(paragraphs: Sequence[str]) -> list[str]:
    for paragraph in paragraphs:
        if re.search(
            r"voting for the (?:FOMC\s+)?monetary policy action",
            paragraph,
            flags=re.IGNORECASE,
        ) is None:
            continue
        segment = re.split(
            r"\.\s+Voting against",
            paragraph,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]
        match = re.search(
            r"Voting for the (?:FOMC\s+)?monetary policy action "
            r"(?:were|was):?\s+(.+)$",
            segment,
            flags=re.IGNORECASE,
        )
        if match is not None:
            return _split_member_names(match.group(1))
    return []


def _parse_dissents(
    paragraphs: Sequence[str],
    *,
    target_after: tuple[float, float] | None = None,
) -> list[dict[str, object]]:
    dissent_text = ""
    for paragraph in paragraphs:
        match = re.search(r"Voting against", paragraph, flags=re.IGNORECASE)
        if match is not None:
            dissent_text = paragraph[match.start() :]
            break
    if not dissent_text:
        return []
    body = re.sub(
        r"^Voting against (?:the monetary policy action|this action|the action) "
        r"(?:were|was):?\s+",
        "",
        dissent_text,
        flags=re.IGNORECASE,
    ).strip(" .")
    groups = re.split(r";\s+and\s+", body, flags=re.IGNORECASE)
    dissents: list[dict[str, object]] = []
    for group in groups:
        match = re.fullmatch(
            r"(.+?),\s+(?:each of whom|who)\s+(.+)",
            group.strip(" ."),
            re.IGNORECASE,
        )
        if match is None:
            raise ValueError("FOMC dissent group was not recognized")
        names = _split_member_names(match.group(1))
        preference_text = _clean_text(match.group(2)).strip(" .")
        action, change_bps = _preferred_action(
            preference_text,
            target_after=target_after,
        )
        dissents.extend(
            {
                "member_name": name,
                "preferred_action": action,
                "change_bps": change_bps,
                "preference_text": preference_text,
            }
            for name in names
        )
    return dissents


def parse_fomc_policy_decision(
    html: str,
    *,
    source_url: str,
    released_at: str,
    prior_range: tuple[float, float] | None,
    collected_at: str,
) -> dict[str, object]:
    """Parse the range, vote, and explicit dissent direction from one statement."""

    soup = BeautifulSoup(html, "html.parser")
    statement_text = _clean_text(soup.get_text(" "))
    paragraphs = [
        _clean_text(paragraph.get_text(" "))
        for paragraph in soup.find_all("p")
        if _clean_text(paragraph.get_text(" "))
    ]
    target_match = re.search(
        r"target range for the federal funds rate[^.]{0,180}?"
        r"(?:at|to)\s+"
        r"(\d+(?:-\d+/\d+|/\d+|\.\d+)?)\s+to\s+"
        r"(\d+(?:-\d+/\d+|/\d+|\.\d+)?)\s+percent",
        statement_text,
        flags=re.IGNORECASE,
    )
    if target_match is None:
        raise ValueError("FOMC target range was not found")
    target_after = (
        _mixed_fraction(target_match.group(1)),
        _mixed_fraction(target_match.group(2)),
    )

    vote_match = re.search(
        r"approved the following statement for release by a\s+(\d+)-(\d+)\s+vote",
        statement_text,
        flags=re.IGNORECASE,
    )
    dissents = _parse_dissents(paragraphs, target_after=target_after)
    if vote_match is not None:
        vote_for = int(vote_match.group(1))
        vote_against = int(vote_match.group(2))
    else:
        vote_for = len(_vote_for_names(paragraphs))
        vote_against = len(dissents)
        if vote_for == 0:
            raise ValueError("FOMC statement vote was not found")
    if len(dissents) != vote_against:
        raise ValueError(
            f"FOMC dissent count mismatch: {len(dissents)} != {vote_against}"
        )

    before_lower, before_upper = prior_range or (None, None)
    return {
        "meeting_date": _source_date(source_url).isoformat(),
        "released_at": _sql_datetime(released_at, field="released_at"),
        "target_lower_before_pct": before_lower,
        "target_upper_before_pct": before_upper,
        "target_lower_after_pct": target_after[0],
        "target_upper_after_pct": target_after[1],
        "vote_total_count": vote_for + vote_against,
        "vote_for_count": vote_for,
        "vote_against_count": vote_against,
        "dissents_json": json.dumps(
            dissents,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        "statement_hash": hashlib.sha256(statement_text.encode("utf-8")).hexdigest(),
        "source": "federal_reserve_fomc",
        "source_ref": source_url,
        "parser_version": DECISION_PARSER_VERSION,
        "coverage_status": "READY" if prior_range is not None else "PARTIAL",
        "collected_at": _sql_datetime(collected_at, field="collected_at"),
    }


def _fetch_official_html(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "quant-data-pipeline/1.0 research@example.com"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _extract_released_at(html: str, *, source_url: str) -> str:
    """Resolve an official Federal Reserve release clock to aware UTC."""

    page_text = _clean_text(BeautifulSoup(html, "html.parser").get_text(" "))
    match = re.search(
        r"For release at\s+(\d{1,2}):(\d{2})\s+([ap])\.m\.?,?\s*"
        r"(?:EDT|EST|ET)",
        page_text,
        flags=re.IGNORECASE,
    )
    if match is None:
        raise ValueError(f"Official Federal Reserve release time was not found: {source_url}")
    hour = int(match.group(1)) % 12
    if match.group(3).casefold() == "p":
        hour += 12
    source_date = _source_date(source_url)
    dated_release = re.search(
        r"For release at.+?(?:EDT|EST|ET),\s*"
        r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
        page_text,
        flags=re.IGNORECASE,
    )
    local_date = (
        datetime.strptime(dated_release.group(1), "%B %d, %Y")
        if dated_release is not None
        else datetime.combine(source_date, datetime.min.time())
    )
    local = local_date.replace(
        hour=hour,
        minute=int(match.group(2)),
        tzinfo=ZoneInfo("America/New_York"),
    )
    if local.date() != source_date:
        raise ValueError("Federal Reserve page timestamp does not match its dated URL")
    return local.astimezone(timezone.utc).isoformat()


def _projection_release_url(source_url: str) -> str:
    release_date = _source_date(source_url).strftime("%Y%m%d")
    return (
        f"{FED_BASE_URL}/newsevents/pressreleases/"
        f"monetary{release_date}b.htm"
    )


def _projection_released_at(
    html: str,
    *,
    source_url: str,
    fetcher: Callable[[str], str],
) -> str:
    """Use the accessible page clock, then its official SEP release page."""

    try:
        return _extract_released_at(html, source_url=source_url)
    except ValueError as exc:
        if "release time was not found" not in str(exc):
            raise
    release_url = _projection_release_url(source_url)
    release_page = fetcher(release_url)
    return _extract_released_at(release_page, source_url=release_url)


def _historical_pages(
    fetcher: Callable[[str], str],
    *,
    historical_start_year: int | None,
    current_urls: Sequence[str],
) -> list[str]:
    if historical_start_year is None or not current_urls:
        return []
    earliest_current_year = min(_source_date(url).year for url in current_urls)
    if historical_start_year >= earliest_current_year:
        return []
    return [
        fetcher(FOMC_HISTORICAL_URL.format(year=year))
        for year in range(int(historical_start_year), earliest_current_year)
    ]


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
    _validate_current_totals(
        rows,
        expected=_expected_participant_count(soup, release_month=release_month),
        current_period=str(_source_date(source_url).year),
    )
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


def upsert_fomc_policy_decisions(
    rows: Iterable[Mapping[str, object]],
    *,
    db: object,
) -> int:
    """Idempotently persist official policy decisions by meeting date."""

    prepared = [dict(row) for row in rows]
    if not prepared:
        return 0
    sql = """
    INSERT INTO fomc_policy_decision (
      meeting_date, released_at, target_lower_before_pct, target_upper_before_pct,
      target_lower_after_pct, target_upper_after_pct, vote_total_count,
      vote_for_count, vote_against_count, dissents_json, statement_hash,
      source, source_ref, parser_version, coverage_status, collected_at
    ) VALUES (
      %(meeting_date)s, %(released_at)s, %(target_lower_before_pct)s,
      %(target_upper_before_pct)s, %(target_lower_after_pct)s,
      %(target_upper_after_pct)s, %(vote_total_count)s, %(vote_for_count)s,
      %(vote_against_count)s, %(dissents_json)s, %(statement_hash)s,
      %(source)s, %(source_ref)s, %(parser_version)s, %(coverage_status)s,
      %(collected_at)s
    )
    ON DUPLICATE KEY UPDATE
      released_at = VALUES(released_at),
      target_lower_before_pct = VALUES(target_lower_before_pct),
      target_upper_before_pct = VALUES(target_upper_before_pct),
      target_lower_after_pct = VALUES(target_lower_after_pct),
      target_upper_after_pct = VALUES(target_upper_after_pct),
      vote_total_count = VALUES(vote_total_count),
      vote_for_count = VALUES(vote_for_count),
      vote_against_count = VALUES(vote_against_count),
      dissents_json = VALUES(dissents_json),
      statement_hash = VALUES(statement_hash),
      source_ref = VALUES(source_ref),
      parser_version = VALUES(parser_version),
      coverage_status = VALUES(coverage_status),
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
    historical_start_year: int | None = 2016,
) -> dict[str, int]:
    """Discover official accessible SEP pages and persist their anonymous bins."""

    fetcher = fetch_html or _fetch_official_html
    calendar_html = fetcher(calendar_url)
    current_statement_urls = discover_fomc_statement_urls(calendar_html)
    current_projection_urls = discover_fomc_projection_urls(calendar_html)
    current_urls = current_statement_urls or current_projection_urls
    history_pages = _historical_pages(
        fetcher,
        historical_start_year=historical_start_year,
        current_urls=current_urls,
    )
    source_urls = sorted(
        {
            *current_projection_urls,
            *(
                url
                for page in history_pages
                for url in discover_historical_fomc_projection_urls(page)
            ),
        },
        key=lambda url: (_source_date(url), url),
    )
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
                released_at=_projection_released_at(
                    page,
                    source_url=source_url,
                    fetcher=fetcher,
                ),
                collected_at=observed_at,
            )
            stored += upsert_fomc_sep_distributions(rows, db=db)
    finally:
        if owns_connection:
            db.close()
    return {"releases": len(source_urls), "stored": stored}


def collect_and_store_fomc_policy_history(
    *,
    calendar_url: str = FOMC_CALENDAR_URL,
    connection: object | None = None,
    fetch_html: Callable[[str], str] | None = None,
    collected_at: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    historical_start_year: int | None = 2016,
) -> dict[str, int]:
    """Collect statements oldest-first so prior ranges never come from the future."""

    fetcher = fetch_html or _fetch_official_html
    calendar_html = fetcher(calendar_url)
    current_statement_urls = discover_fomc_statement_urls(calendar_html)
    history_pages = _historical_pages(
        fetcher,
        historical_start_year=historical_start_year,
        current_urls=current_statement_urls,
    )
    statement_urls = sorted(
        {
            *current_statement_urls,
            *(
                url
                for page in history_pages
                for url in discover_fomc_statement_urls(page)
            ),
        },
        key=lambda url: (_source_date(url), url),
    )
    if not statement_urls:
        raise ValueError("No official FOMC statement pages were discovered")
    observed_at = collected_at or datetime.now(timezone.utc).isoformat()

    owns_connection = connection is None
    db = connection or MySQLClient(host, user, password, port)
    prior_range: tuple[float, float] | None = None
    stored = 0
    try:
        db.use_db(DB_META)
        schema = INFLATION_POLICY_SCHEMAS["fomc_policy_decision"]
        db.execute(schema)
        sync_table_schema(db, "fomc_policy_decision", schema, DB_META)
        for source_url in statement_urls:
            page = fetcher(source_url)
            row = parse_fomc_policy_decision(
                page,
                source_url=source_url,
                released_at=_extract_released_at(page, source_url=source_url),
                prior_range=prior_range,
                collected_at=observed_at,
            )
            stored += upsert_fomc_policy_decisions([row], db=db)
            prior_range = (
                float(row["target_lower_after_pct"]),
                float(row["target_upper_after_pct"]),
            )
    finally:
        if owns_connection:
            db.close()
    return {"meetings": stored, "stored": stored}
