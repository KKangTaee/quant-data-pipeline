from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any


GLOSSARY_META_SECTION_TITLES = {"목적", "사용 원칙"}


REFERENCE_CONCEPT_DICTIONARY: list[dict[str, Any]] = [
    {
        "term": "NOT_RUN",
        "category": "Status / Gate",
        "plain_meaning": "검증이 실행되지 않았거나 필요한 evidence가 아직 없습니다.",
        "owner_screen": "Practical Validation / Final Review",
        "progress_implication": "pass가 아니라 evidence missing / not executed",
        "where_to_fix": "Ingestion, Backtest source, provider snapshot, selected-route preflight를 확인합니다.",
        "source": "Practical Validation module planner / selected-route gate",
        "keywords": ["not run", "missing evidence", "required module", "validation replay"],
    },
    {
        "term": "REVIEW",
        "category": "Status / Gate",
        "plain_meaning": "진행은 가능할 수 있지만 해석과 보강 조건을 남겨야 합니다.",
        "owner_screen": "Practical Validation / Final Review / Portfolio Monitoring",
        "progress_implication": "기본적으로 open review item이며 hard blocker와 분리합니다.",
        "where_to_fix": "해당 audit row의 owner screen과 evidence source를 확인합니다.",
        "source": "Practical Validation audits / Final Review open review items",
        "keywords": ["open review", "warning", "보강", "interpretation"],
    },
    {
        "term": "BLOCKED",
        "category": "Status / Gate",
        "plain_meaning": "현재 조건에서는 다음 단계로 넘기면 안 되는 hard blocker입니다.",
        "owner_screen": "Backtest Analysis / Practical Validation / Final Review",
        "progress_implication": "selected-route progression is stopped until fixed",
        "where_to_fix": "데이터, source contract, component weight, benchmark parity, cost evidence를 원인 화면에서 보강합니다.",
        "source": "Backtest source / validation gate / selected-route gate",
        "keywords": ["hard blocker", "stop", "needs input", "gate"],
    },
    {
        "term": "Data Trust",
        "category": "Data Quality",
        "plain_meaning": "결과가 어떤 데이터 freshness와 coverage 조건에서 만들어졌는지 보여주는 신뢰도 신호입니다.",
        "owner_screen": "Backtest Analysis",
        "progress_implication": "warning 또는 blocked이면 Practical Validation에 넘기기 전 원인을 설명해야 합니다.",
        "where_to_fix": "Workspace > Ingestion > 실행 기록 / 결과에서 source 상태와 실패 원인을 확인합니다.",
        "source": "Backtest result metadata / loader freshness checks",
        "keywords": ["freshness", "coverage", "source status", "data quality"],
    },
    {
        "term": "Provider Coverage",
        "category": "Provider Evidence",
        "plain_meaning": "ETF holdings, exposure, issuer/provider snapshot이 실제/partial/proxy 중 어떤 근거인지 나타냅니다.",
        "owner_screen": "Practical Validation / Portfolio Monitoring",
        "progress_implication": "partial or proxy coverage is review evidence, not pass.",
        "where_to_fix": "Ingestion provider snapshot job과 Provider Data Gaps를 확인합니다.",
        "source": "ETF provider snapshot DB tables / Provider Data Gaps",
        "keywords": ["look-through", "holdings", "exposure", "provider snapshot", "proxy"],
    },
    {
        "term": "Portfolio Monitoring Scenario",
        "category": "Operations",
        "plain_meaning": "selected decision strategy slot을 사용자가 지정한 start/latest mode와 balance로 다시 보는 session replay입니다.",
        "owner_screen": "Operations > Portfolio Monitoring",
        "progress_implication": "사후 관찰 근거이며 새 최종 판단이나 주문 지시가 아닙니다.",
        "where_to_fix": "scenario stale state, slot signature, latest market date를 확인합니다.",
        "source": "SELECTED_DASHBOARD_PORTFOLIOS.jsonl + session replay result",
        "keywords": ["scenario stale", "slot signature", "latest market date", "read-only replay"],
    },
    {
        "term": "Selected-route Gate",
        "category": "Final Review",
        "plain_meaning": "Final Review에서 모니터링 후보로 저장할 수 있는지 판정하는 마지막 gate입니다.",
        "owner_screen": "Backtest > Final Review",
        "progress_implication": "gate가 막히면 `SELECT_FOR_PRACTICAL_PORTFOLIO` 저장으로 진행하지 않습니다.",
        "where_to_fix": "Final Review의 blocker row와 Practical Validation evidence owner를 확인합니다.",
        "source": "Final Review evidence read model",
        "keywords": ["selection gate", "selected route", "final decision", "monitoring candidate"],
    },
    {
        "term": "Promotion Policy Signal",
        "category": "Backtest Analysis",
        "plain_meaning": "Backtest 결과가 후보 source로 넘길 만한지 보여주는 handoff policy 신호입니다.",
        "owner_screen": "Backtest > Backtest Analysis",
        "progress_implication": "후보 생성 참고 신호이며 Final Review selected decision을 대체하지 않습니다.",
        "where_to_fix": "Backtest result의 성과, benchmark, guardrail, Data Trust를 함께 확인합니다.",
        "source": "Backtest result metadata",
        "keywords": ["promotion", "handoff", "candidate", "shortlist"],
    },
    {
        "term": "Saved Portfolio",
        "category": "Saved Setup",
        "plain_meaning": "Portfolio Mix Builder에서 저장한 재사용 weight setup입니다.",
        "owner_screen": "Backtest > Portfolio Mix Builder",
        "progress_implication": "workflow registry나 Final Review selected decision이 아니라 replay 가능한 setup입니다.",
        "where_to_fix": "저장된 Mix를 다시 실행해 current selection source로 연결합니다.",
        "source": "SAVED_PORTFOLIOS.jsonl / saved setup files",
        "keywords": ["saved mix", "weight setup", "replay", "portfolio mix"],
    },
]


def get_reference_concept_dictionary() -> list[dict[str, Any]]:
    return deepcopy(REFERENCE_CONCEPT_DICTIONARY)


def _concept_search_text(row: dict[str, Any]) -> str:
    values: list[str] = []
    for value in row.values():
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return " ".join(values).lower()


def search_reference_concepts(
    concepts: list[dict[str, Any]],
    query: str,
) -> list[dict[str, Any]]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return deepcopy(concepts)

    terms = [term for term in normalized_query.split() if term]
    matched: list[dict[str, Any]] = []
    for row in concepts:
        haystack = _concept_search_text(row)
        if all(term in haystack for term in terms):
            matched.append(deepcopy(row))
    return matched


def load_glossary_sections_from_markdown(
    path: Path,
    *,
    meta_section_titles: set[str] | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not path.exists():
        return [], []

    text = path.read_text(encoding="utf-8")
    sections: list[dict[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections.append(
                    {
                        "title": current_title,
                        "body": "\n".join(current_lines).strip(),
                    }
                )
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append(
            {
                "title": current_title,
                "body": "\n".join(current_lines).strip(),
            }
        )

    meta_titles = meta_section_titles or GLOSSARY_META_SECTION_TITLES
    meta_sections = [section for section in sections if section["title"] in meta_titles]
    term_sections = [section for section in sections if section["title"] not in meta_titles]
    return meta_sections, term_sections


def search_glossary_sections(
    sections: list[dict[str, str]],
    query: str,
    *,
    search_body: bool,
) -> list[dict[str, str]]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return deepcopy(sections)

    matched: list[dict[str, str]] = []
    for section in sections:
        title = str(section.get("title") or "")
        body = str(section.get("body") or "")
        title_hit = normalized_query in title.lower()
        body_hit = search_body and normalized_query in body.lower()
        if title_hit or body_hit:
            matched.append(deepcopy(section))
    return matched
