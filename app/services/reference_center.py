from __future__ import annotations

from copy import deepcopy
from typing import Any


REFERENCE_DESTINATIONS = {
    "overview",
    "institutional_portfolios",
    "ingestion",
    "backtest_analysis",
    "practical_validation",
    "final_review",
    "portfolio_monitoring",
}

REQUIRED_CURRENT_SURFACES = {
    "Overview",
    "Institutional Portfolios",
    "Ingestion",
    "Backtest Analysis",
    "Practical Validation",
    "Final Review",
    "Portfolio Monitoring",
}

FORBIDDEN_USER_LABELS = {
    "Futures Monitor",
    "Macro Thermometer",
    "Candidate Review",
    "Portfolio Proposal",
    "Selected Portfolio Dashboard",
    "Main Worktree",
    "Sub Worktree",
    "Fixture",
}

REFERENCE_FILTERS = [
    {"id": "all", "label": "전체"},
    {"id": "journey", "label": "사용 흐름"},
    {"id": "concept", "label": "상태·용어"},
    {"id": "playbook", "label": "문제 해결"},
]

REFERENCE_EMPTY_STATE = {
    "title": "검색 결과가 없습니다",
    "description": "검색어를 줄이거나 아래 사용자 흐름에서 다시 시작해 보세요.",
    "suggestions": ["시장 맥락", "기관 보유", "데이터 준비", "NOT_RUN", "최종 판단", "모니터링"],
}


def _normalize_search_text(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _item(
    *,
    item_id: str,
    kind: str,
    category: str,
    title: str,
    summary: str,
    aliases: list[str],
    keywords: list[str],
    related_surfaces: list[str],
    meaning: str,
    impact: str,
    next_action: str,
    related_item_ids: list[str],
    destination: str | None,
) -> dict[str, Any]:
    item = {
        "id": item_id,
        "kind": kind,
        "category": category,
        "title": title,
        "summary": summary,
        "aliases": aliases,
        "keywords": keywords,
        "related_surfaces": related_surfaces,
        "meaning": meaning,
        "impact": impact,
        "next_action": next_action,
        "related_item_ids": related_item_ids,
        "destination": destination,
    }
    item["search_text"] = _normalize_search_text(
        " ".join(
            [
                title,
                summary,
                *aliases,
                *keywords,
                *related_surfaces,
                meaning,
                impact,
                next_action,
            ]
        )
    )
    return item


REFERENCE_CENTER_ITEMS: list[dict[str, Any]] = [
    _item(
        item_id="journey.market_understanding",
        kind="journey",
        category="시장 이해",
        title="지금 시장을 어떻게 읽는가?",
        summary="시장 맥락, 주요 움직임, 선물·거시, 심리, 이벤트를 한 흐름으로 읽습니다.",
        aliases=["시장 이해", "market understanding", "오늘 시장"],
        keywords=["overview", "market context", "market movers", "futures macro", "sentiment", "events"],
        related_surfaces=["Overview"],
        meaning="Overview의 다섯 관점을 함께 보며 현재 시장의 방향과 자료 한계를 구분하는 시작 흐름입니다.",
        impact="한 지표만으로 결론 내리지 않고 가격, 거시, 심리, 이벤트가 같은 이야기를 하는지 확인할 수 있습니다.",
        next_action="Overview에서 Market Context를 먼저 읽고 필요한 보조 관점으로 이동합니다.",
        related_item_ids=[
            "feature.market_context",
            "feature.market_movers",
            "feature.futures_macro",
            "feature.sentiment",
            "feature.events",
            "feature.economic_cycle",
        ],
        destination="overview",
    ),
    _item(
        item_id="journey.institutional_portfolios",
        kind="journey",
        category="기관 보유",
        title="기관의 13F 보유를 어떻게 해석하는가?",
        summary="기관 선택, 최신 보고기간, 전체 보유와 개별 종목 맥락을 순서대로 확인합니다.",
        aliases=["기관 포트폴리오", "13f", "institutional holdings"],
        keywords=["manager", "holdings", "cusip", "portfolio", "security"],
        related_surfaces=["Institutional Portfolios"],
        meaning="공개 13F 보고서를 기관 포트폴리오와 개별 보유 종목 관점으로 읽는 흐름입니다.",
        impact="보고기간과 mapping coverage를 놓치지 않고 보유 비중과 변화의 의미를 해석할 수 있습니다.",
        next_action="Institutional Portfolios에서 기관과 보고기간을 확인한 뒤 보유 종목을 탐색합니다.",
        related_item_ids=["concept.provider_coverage", "concept.data_trust"],
        destination="institutional_portfolios",
    ),
    _item(
        item_id="journey.data_preparation",
        kind="journey",
        category="데이터 준비",
        title="필요한 데이터를 어디서 준비하는가?",
        summary="분석에 필요한 데이터의 목적과 owning collection surface를 확인합니다.",
        aliases=["데이터 준비", "수집", "ingestion"],
        keywords=["provider", "coverage", "refresh", "collect", "자료"],
        related_surfaces=["Ingestion"],
        meaning="부족하거나 오래된 분석 입력을 해당 데이터 소유 화면에서 준비하는 흐름입니다.",
        impact="Reference에서 작업을 실행하지 않고 실제 수집 화면과 다음 확인 단계를 찾을 수 있습니다.",
        next_action="Ingestion에서 필요한 데이터 종류와 대상 범위를 확인한 뒤 명시적으로 수집합니다.",
        related_item_ids=["concept.data_trust", "concept.provider_coverage", "playbook.ingestion_data_missing"],
        destination="ingestion",
    ),
    _item(
        item_id="journey.candidate_creation",
        kind="journey",
        category="후보 생성",
        title="전략·mix 후보를 어떻게 만드는가?",
        summary="전략 실행 결과를 비교하고 다음 검증 단계로 보낼 후보를 만듭니다.",
        aliases=["후보 만들기", "전략 후보", "portfolio mix"],
        keywords=["backtest", "analysis", "strategy", "mix", "candidate"],
        related_surfaces=["Backtest Analysis"],
        meaning="Backtest Analysis에서 단일 전략과 포트폴리오 mix 결과를 읽고 후보 source를 만드는 흐름입니다.",
        impact="연구 결과와 검증·최종 판단 기록을 혼동하지 않고 다음 단계 입력을 준비할 수 있습니다.",
        next_action="Backtest Analysis에서 결과와 Data Trust를 확인한 뒤 Practical Validation으로 보냅니다.",
        related_item_ids=["concept.data_trust", "concept.saved_portfolio"],
        destination="backtest_analysis",
    ),
    _item(
        item_id="journey.validation_decision",
        kind="journey",
        category="검증과 판단",
        title="무엇을 검증하고 최종 판단하는가?",
        summary="실전성 근거를 검증하고 별도 최종 검토에서 모니터링 후보 여부를 판단합니다.",
        aliases=["검증", "최종 판단", "validation decision"],
        keywords=["practical validation", "final review", "gate", "evidence"],
        related_surfaces=["Practical Validation", "Final Review"],
        meaning="Practical Validation의 검증 근거와 Final Review의 사용자 판단을 분리해 진행하는 흐름입니다.",
        impact="NOT_RUN이나 REVIEW를 통과로 오해하지 않고 blocker와 최종 판단을 구분할 수 있습니다.",
        next_action="Practical Validation의 blocker를 해결한 뒤 Final Review에서 판단 근거를 남깁니다.",
        related_item_ids=[
            "status.not_run",
            "status.review",
            "status.blocked",
            "concept.selected_route_gate",
            "playbook.practical_validation_not_run",
            "playbook.final_review_candidate_missing",
        ],
        destination="practical_validation",
    ),
    _item(
        item_id="journey.monitoring",
        kind="journey",
        category="선정 후 추적",
        title="선정 후 무엇을 추적하는가?",
        summary="Final Review에서 선정한 후보의 성과와 가정 변화를 읽기 전용으로 추적합니다.",
        aliases=["모니터링", "선정 후", "portfolio monitoring"],
        keywords=["scenario", "tracking", "selected", "recheck"],
        related_surfaces=["Portfolio Monitoring"],
        meaning="선정 당시 근거와 현재 시나리오를 비교해 계속 관찰할 항목을 찾는 흐름입니다.",
        impact="모니터링을 새 승인이나 주문 지시로 오해하지 않고 변화와 재검토 조건에 집중할 수 있습니다.",
        next_action="Portfolio Monitoring에서 선택 포트폴리오와 최신 시나리오 상태를 확인합니다.",
        related_item_ids=["concept.monitoring_scenario", "playbook.monitoring_scenario_stale"],
        destination="portfolio_monitoring",
    ),
    _item(
        item_id="feature.market_context",
        kind="concept",
        category="Overview 기능",
        title="Market Context",
        summary="시장 가격, 거시 조건, 자료 신뢰도를 합쳐 오늘의 맥락을 읽는 화면입니다.",
        aliases=["시장 맥락", "오늘의 시장 맥락"],
        keywords=["overview", "brief", "macro", "context"],
        related_surfaces=["Overview"],
        meaning="여러 시장 근거가 현재 환경을 어떻게 설명하는지 요약하는 Overview 관점입니다.",
        impact="개별 신호를 독립적인 매매 결론으로 오해하지 않고 공통 맥락에서 읽게 합니다.",
        next_action="핵심 결론과 자료 제한을 읽고 필요하면 Economic Cycle이나 다른 Overview 관점을 확인합니다.",
        related_item_ids=["feature.economic_cycle", "feature.market_movers", "concept.data_trust"],
        destination="overview",
    ),
    _item(
        item_id="feature.market_movers",
        kind="concept",
        category="Overview 기능",
        title="Market Movers",
        summary="기간별 주요 상승·하락과 시장 참여 범위를 확인합니다.",
        aliases=["시장 움직임", "상승 하락", "movers"],
        keywords=["daily", "weekly", "monthly", "yearly", "ranking"],
        related_surfaces=["Overview"],
        meaning="선택 기간에 어떤 자산과 섹터가 시장 움직임을 주도했는지 보여주는 관점입니다.",
        impact="헤드라인 지수만 보지 않고 움직임의 리더와 확산 정도를 함께 읽을 수 있습니다.",
        next_action="원하는 기간을 선택하고 상위 움직임과 breadth 근거를 비교합니다.",
        related_item_ids=["journey.market_understanding", "feature.market_context"],
        destination="overview",
    ),
    _item(
        item_id="feature.futures_macro",
        kind="concept",
        category="Overview 기능",
        title="Futures Macro",
        summary="주요 선물의 현재 흐름과 과거 유사 패턴 기반 조건부 전망을 분리해 읽습니다.",
        aliases=["선물 거시", "futures", "macro futures"],
        keywords=["1d", "5d", "20d", "pattern", "outlook"],
        related_surfaces=["Overview"],
        meaning="저장된 선물 가격으로 현재 관측과 검증 상태가 분리된 전망을 보여주는 관점입니다.",
        impact="현재 가격 움직임과 아직 잠정적인 미래 통계를 같은 확정도로 읽는 실수를 줄입니다.",
        next_action="관측 기간과 전망 validation 상태를 함께 확인합니다.",
        related_item_ids=["journey.market_understanding", "concept.data_trust"],
        destination="overview",
    ),
    _item(
        item_id="feature.sentiment",
        kind="concept",
        category="Overview 기능",
        title="Sentiment",
        summary="CNN과 AAII 등 서로 다른 시장 심리 근거를 균형 있게 읽습니다.",
        aliases=["시장 심리", "투자자 심리"],
        keywords=["cnn", "aaii", "fear greed", "survey"],
        related_surfaces=["Overview"],
        meaning="가격 기반 심리와 설문 기반 심리를 분리해 현재 위험선호를 참고하는 관점입니다.",
        impact="심리 한 종류를 gate나 미래 수익률 예측으로 과대 해석하지 않게 합니다.",
        next_action="각 지표의 기준 시점과 출처를 확인하고 Market Context와 함께 읽습니다.",
        related_item_ids=["journey.market_understanding", "feature.market_context"],
        destination="overview",
    ),
    _item(
        item_id="feature.events",
        kind="concept",
        category="Overview 기능",
        title="Events",
        summary="최근 발표와 예정된 주요 거시 이벤트를 시장 맥락의 보조 근거로 봅니다.",
        aliases=["이벤트", "경제 일정", "macro events"],
        keywords=["cpi", "ppi", "fomc", "calendar", "release"],
        related_surfaces=["Overview"],
        meaning="주요 경제 발표의 최근 결과와 다음 일정을 구분해 보여주는 관점입니다.",
        impact="예정값과 확정 발표값을 혼동하지 않고 변동성 맥락을 준비할 수 있습니다.",
        next_action="최근 발표와 upcoming 항목을 구분하고 자료 제한을 확인합니다.",
        related_item_ids=["journey.market_understanding", "feature.market_context"],
        destination="overview",
    ),
    _item(
        item_id="feature.economic_cycle",
        kind="concept",
        category="Overview 기능",
        title="Economic Cycle",
        summary="발표 당시 이용 가능했던 거시 자료로 미국 경기 국면을 잠정 또는 검증 상태와 함께 읽습니다.",
        aliases=["경제 사이클", "경기 국면", "economic regime"],
        keywords=["pit", "vintage", "probability", "expansion", "slowdown"],
        related_surfaces=["Overview"],
        meaning="시점별로 이용 가능했던 자료를 사용해 경기 국면과 자산별 확인 포인트를 보여주는 기능입니다.",
        impact="현재 수정된 데이터가 과거에도 알려졌다고 가정하는 오류를 줄이고 validation 상태를 구분합니다.",
        next_action="국면 확률, 검증 상태, 자산별 실제 가격 근거를 함께 확인합니다.",
        related_item_ids=["feature.market_context", "concept.data_trust"],
        destination="overview",
    ),
    _item(
        item_id="status.not_run",
        kind="concept",
        category="검증 상태",
        title="NOT_RUN",
        summary="검증이 통과한 것이 아니라 실행되지 않았거나 필요한 근거가 없는 상태입니다.",
        aliases=["미실행", "not run"],
        keywords=["validation", "evidence", "missing", "replay"],
        related_surfaces=["Practical Validation"],
        meaning="검증 계산이나 replay를 수행할 입력·근거가 준비되지 않았음을 뜻합니다.",
        impact="PASS로 계산할 수 없으며 Final Review 진입을 막는 원인이 될 수 있습니다.",
        next_action="해당 row의 자료 소유 화면과 재실행 조건을 확인합니다.",
        related_item_ids=["status.blocked", "playbook.practical_validation_not_run", "concept.provider_coverage"],
        destination="practical_validation",
    ),
    _item(
        item_id="status.review",
        kind="concept",
        category="검증 상태",
        title="REVIEW",
        summary="자동 통과로 확정할 수 없어 사람이 근거와 한계를 읽어야 하는 상태입니다.",
        aliases=["검토 필요", "review"],
        keywords=["validation", "evidence", "partial", "proxy"],
        related_surfaces=["Practical Validation", "Final Review"],
        meaning="자료가 부분적이거나 기준이 판단을 요구해 추가 검토가 필요한 상태입니다.",
        impact="자동 blocker와는 다르지만 근거를 읽지 않고 통과로 처리할 수 없습니다.",
        next_action="현재 근거, 허용 가능한 한계, 보강 가능 여부를 확인합니다.",
        related_item_ids=["status.not_run", "status.blocked", "concept.provider_coverage"],
        destination="practical_validation",
    ),
    _item(
        item_id="status.blocked",
        kind="concept",
        category="검증 상태",
        title="BLOCKED",
        summary="필수 조건이 충족되지 않아 다음 단계로 진행할 수 없는 상태입니다.",
        aliases=["차단", "blocked"],
        keywords=["gate", "required", "stop", "validation"],
        related_surfaces=["Practical Validation", "Final Review"],
        meaning="필수 자료, 검증, route 조건 중 하나가 명시적으로 다음 행동을 막는 상태입니다.",
        impact="원인을 해결하고 검증을 다시 실행하기 전까지 최종 선정 경로를 열 수 없습니다.",
        next_action="blocker 소유 화면과 해결 조건을 확인한 뒤 검증을 다시 수행합니다.",
        related_item_ids=["status.not_run", "status.review", "concept.selected_route_gate"],
        destination="practical_validation",
    ),
    _item(
        item_id="concept.data_trust",
        kind="concept",
        category="자료 의미",
        title="Data Trust",
        summary="분석 결과를 해석할 수 있을 만큼 입력 자료가 충분하고 신뢰 가능한지 보여줍니다.",
        aliases=["자료 신뢰", "데이터 신뢰도"],
        keywords=["coverage", "freshness", "source", "quality"],
        related_surfaces=["Overview", "Backtest Analysis", "Practical Validation"],
        meaning="coverage, freshness, source 경계를 합쳐 결과 해석 가능 범위를 설명하는 개념입니다.",
        impact="성과 숫자가 있어도 입력 자료가 부족하면 후보 판단의 확신을 낮추게 합니다.",
        next_action="부족한 자료 유형과 owning surface를 확인하고 필요한 경우 보강합니다.",
        related_item_ids=["concept.provider_coverage", "journey.data_preparation"],
        destination="ingestion",
    ),
    _item(
        item_id="concept.provider_coverage",
        kind="concept",
        category="자료 의미",
        title="Provider Coverage",
        summary="필요한 기간과 대상 중 실제 provider 자료가 어느 범위까지 있는지 뜻합니다.",
        aliases=["공급자 커버리지", "자료 범위"],
        keywords=["partial", "proxy", "missing", "provider"],
        related_surfaces=["Institutional Portfolios", "Ingestion", "Practical Validation"],
        meaning="직접 자료, 부분 자료, proxy, 결측을 구분하는 coverage 개념입니다.",
        impact="partial이나 proxy는 자동 실패가 아닐 수 있지만 판단 근거의 제한으로 남습니다.",
        next_action="필요 범위와 현재 범위를 비교하고 보강 가능한 결측만 수집합니다.",
        related_item_ids=["concept.data_trust", "status.review", "playbook.ingestion_data_missing"],
        destination="ingestion",
    ),
    _item(
        item_id="concept.selected_route_gate",
        kind="concept",
        category="최종 판단",
        title="Selected-route Gate",
        summary="검증된 후보가 Portfolio Monitoring 선정 경로로 넘어갈 수 있는지 확인하는 gate입니다.",
        aliases=["선정 경로 gate", "selected route"],
        keywords=["final review", "selection", "monitoring", "gate"],
        related_surfaces=["Final Review"],
        meaning="Practical Validation과 Final Review 필수 조건을 통과한 후보만 선정 기록으로 저장하게 합니다.",
        impact="blocked 상태에서는 모니터링 후보 저장을 진행하지 않습니다.",
        next_action="Final Review에서 gate 근거와 남은 blocker를 확인합니다.",
        related_item_ids=["journey.validation_decision", "status.blocked", "playbook.final_review_candidate_missing"],
        destination="final_review",
    ),
    _item(
        item_id="concept.saved_portfolio",
        kind="concept",
        category="후보 구성",
        title="Saved Portfolio",
        summary="다시 불러와 사용할 수 있도록 저장한 포트폴리오 구성 setup입니다.",
        aliases=["저장 포트폴리오", "saved setup"],
        keywords=["mix", "replay", "weights", "configuration"],
        related_surfaces=["Backtest Analysis"],
        meaning="전략과 비중 구성을 재사용하기 위한 setup이며 검증 또는 최종 선정 기록이 아닙니다.",
        impact="저장됐다는 이유만으로 Practical Validation이나 Final Review를 통과한 것으로 볼 수 없습니다.",
        next_action="필요하면 setup을 다시 실행하고 검증 source로 보내 별도 검증합니다.",
        related_item_ids=["journey.candidate_creation", "journey.validation_decision"],
        destination="backtest_analysis",
    ),
    _item(
        item_id="concept.monitoring_scenario",
        kind="concept",
        category="선정 후 추적",
        title="Portfolio Monitoring Scenario",
        summary="선정 포트폴리오의 기준과 현재 성과를 같은 계약으로 다시 계산한 관찰 시나리오입니다.",
        aliases=["모니터링 시나리오", "scenario replay"],
        keywords=["stale", "tracking", "recheck", "baseline"],
        related_surfaces=["Portfolio Monitoring"],
        meaning="선정 당시의 구성과 관찰 조건을 기준으로 현재 변화를 읽는 read-only 시나리오입니다.",
        impact="구성이나 기준이 바뀌면 stale이 될 수 있으며 새 최종 승인이나 주문을 만들지 않습니다.",
        next_action="시나리오 기준과 최신 계산 시점을 확인하고 stale이면 갱신 조건을 검토합니다.",
        related_item_ids=["journey.monitoring", "playbook.monitoring_scenario_stale"],
        destination="portfolio_monitoring",
    ),
    _item(
        item_id="playbook.ingestion_data_missing",
        kind="playbook",
        category="데이터 문제 해결",
        title="필요한 분석 데이터가 비어 있을 때",
        summary="결측 자료의 종류와 owning collection surface를 찾아 필요한 범위만 준비합니다.",
        aliases=["데이터 없음", "자료 부족", "missing data"],
        keywords=["ingestion", "coverage", "collect", "refresh"],
        related_surfaces=["Ingestion"],
        meaning="분석 화면의 결측 원인을 데이터 종류, 대상, 기간으로 좁혀 해결하는 절차입니다.",
        impact="무관한 전체 수집을 피하고 필요한 입력만 보강할 수 있습니다.",
        next_action="결측 대상과 기간을 확인하고 Ingestion에서 해당 수집만 실행한 뒤 원래 화면으로 돌아갑니다.",
        related_item_ids=["journey.data_preparation", "concept.provider_coverage", "concept.data_trust"],
        destination="ingestion",
    ),
    _item(
        item_id="playbook.practical_validation_not_run",
        kind="playbook",
        category="검증 문제 해결",
        title="Practical Validation이 NOT_RUN일 때",
        summary="실행되지 않은 검증의 입력, replay, provider evidence를 순서대로 확인합니다.",
        aliases=["검증 미실행", "not_run 해결"],
        keywords=["validation", "replay", "evidence", "blocked"],
        related_surfaces=["Practical Validation"],
        meaning="NOT_RUN의 원인을 단순 통과가 아니라 실행 조건 부족으로 해석하고 해결하는 절차입니다.",
        impact="필수 검증이 비어 있는 채 Final Review로 넘어가는 오류를 막습니다.",
        next_action="현재 source, replay 실행 여부, provider coverage를 확인하고 검증을 다시 실행합니다.",
        related_item_ids=["status.not_run", "concept.provider_coverage", "journey.validation_decision"],
        destination="practical_validation",
    ),
    _item(
        item_id="playbook.final_review_candidate_missing",
        kind="playbook",
        category="최종 판단 문제 해결",
        title="Final Review에 후보가 보이지 않을 때",
        summary="최신 Practical Validation 결과와 selected-route 조건을 확인합니다.",
        aliases=["최종 검토 후보 없음", "후보 미표시"],
        keywords=["final review", "candidate missing", "gate", "validation"],
        related_surfaces=["Final Review"],
        meaning="Final Review 목록에 오르기 위한 최신 검증과 route 조건을 역순으로 확인하는 절차입니다.",
        impact="오래된 검증이나 blocked 후보가 최종 판단 대상으로 잘못 나타나는 것을 방지합니다.",
        next_action="Practical Validation의 최신 저장 결과와 Selected-route Gate를 확인합니다.",
        related_item_ids=["concept.selected_route_gate", "status.blocked", "journey.validation_decision"],
        destination="final_review",
    ),
    _item(
        item_id="playbook.monitoring_scenario_stale",
        kind="playbook",
        category="모니터링 문제 해결",
        title="모니터링 시나리오가 stale일 때",
        summary="선정 기록, 전략 구성, 기준 기간이 현재 시나리오와 일치하는지 확인합니다.",
        aliases=["stale scenario", "시나리오 오래됨"],
        keywords=["monitoring", "replay", "signature", "update"],
        related_surfaces=["Portfolio Monitoring"],
        meaning="시나리오가 선정 기준이나 최신 관찰 시점과 달라졌을 때 원인을 찾는 절차입니다.",
        impact="오래된 계산을 현재 모니터링 결과로 오해하지 않게 합니다.",
        next_action="선정 row, 전략 slot signature, 기준 기간을 비교하고 필요한 시나리오 갱신을 수행합니다.",
        related_item_ids=["concept.monitoring_scenario", "journey.monitoring"],
        destination="portfolio_monitoring",
    ),
]


def get_reference_center_items() -> list[dict[str, Any]]:
    return deepcopy(REFERENCE_CENTER_ITEMS)


def get_reference_item(item_id: str) -> dict[str, Any] | None:
    normalized_item_id = str(item_id or "").strip()
    for item in REFERENCE_CENTER_ITEMS:
        if item["id"] == normalized_item_id:
            return deepcopy(item)
    return None


def validate_initial_reference_item(item_id: object) -> str | None:
    normalized_item_id = str(item_id or "").strip()
    return normalized_item_id if get_reference_item(normalized_item_id) is not None else None


def validate_reference_destination(destination: object) -> str | None:
    normalized_destination = str(destination or "").strip()
    return normalized_destination if normalized_destination in REFERENCE_DESTINATIONS else None


def build_reference_center_payload(initial_item_id: object = None) -> dict[str, Any]:
    normalized_initial = str(initial_item_id or "").strip()
    valid_initial = validate_initial_reference_item(normalized_initial)
    return {
        "schema_version": "reference_center_v1",
        "component": "ReferenceCenterWorkbench",
        "filters": deepcopy(REFERENCE_FILTERS),
        "journeys": [item["id"] for item in REFERENCE_CENTER_ITEMS if item["kind"] == "journey"],
        "items": get_reference_center_items(),
        "initial_item_id": valid_initial,
        "invalid_initial_item": bool(normalized_initial and valid_initial is None),
        "empty_state": deepcopy(REFERENCE_EMPTY_STATE),
    }


def _duplicate_ids(items: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicate_ids: set[str] = set()
    for item in items:
        item_id = str(item.get("id") or "").strip()
        if item_id in seen:
            duplicate_ids.add(item_id)
        seen.add(item_id)
    return sorted(duplicate_ids)


def build_reference_center_drift_report() -> dict[str, Any]:
    items = get_reference_center_items()
    item_ids = {str(item.get("id") or "").strip() for item in items}
    current_surfaces = {
        str(surface).strip()
        for item in items
        for surface in list(item.get("related_surfaces") or [])
        if str(surface or "").strip()
    }
    forbidden_user_labels: list[dict[str, str]] = []
    invalid_related_item_ids: list[dict[str, str]] = []
    invalid_destinations: list[dict[str, str]] = []
    invalid_items: list[dict[str, str]] = []
    required_fields = ("id", "category", "title", "summary", "meaning", "impact", "next_action")

    for item in items:
        item_id = str(item.get("id") or "").strip()
        for field in required_fields:
            if not str(item.get(field) or "").strip():
                invalid_items.append({"item_id": item_id, "field": field})
        if item.get("kind") not in {"journey", "concept", "playbook"}:
            invalid_items.append({"item_id": item_id, "field": "kind"})

        destination = item.get("destination")
        if destination is not None and validate_reference_destination(destination) is None:
            invalid_destinations.append({"item_id": item_id, "destination": str(destination)})

        for related_item_id in list(item.get("related_item_ids") or []):
            normalized_related_id = str(related_item_id or "").strip()
            if normalized_related_id not in item_ids:
                invalid_related_item_ids.append(
                    {"item_id": item_id, "related_item_id": normalized_related_id}
                )

        user_copy = " ".join(
            str(value)
            for key, value in item.items()
            if key not in {"id", "search_text"}
        ).lower()
        for label in FORBIDDEN_USER_LABELS:
            if label.lower() in user_copy:
                forbidden_user_labels.append({"item_id": item_id, "label": label})

    issue_lists = {
        "missing_current_surfaces": sorted(REQUIRED_CURRENT_SURFACES - current_surfaces),
        "forbidden_user_labels": forbidden_user_labels,
        "duplicate_ids": _duplicate_ids(items),
        "invalid_related_item_ids": invalid_related_item_ids,
        "invalid_destinations": invalid_destinations,
        "invalid_items": invalid_items,
    }
    has_issues = any(issue_lists.values())
    return {
        "status": "REVIEW" if has_issues else "PASS",
        "metrics": {
            "item_count": len(items),
            "journey_count": sum(1 for item in items if item.get("kind") == "journey"),
            "concept_count": sum(1 for item in items if item.get("kind") == "concept"),
            "playbook_count": sum(1 for item in items if item.get("kind") == "playbook"),
            "surface_count": len(current_surfaces),
        },
        **issue_lists,
    }
