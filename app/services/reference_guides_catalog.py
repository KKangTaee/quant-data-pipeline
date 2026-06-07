from __future__ import annotations

from copy import deepcopy

REFERENCE_TASK_CARDS: list[dict[str, str]] = [
    {
        "key": "market_context",
        "title": "시장 / 데이터 상태 보기",
        "owner_screen": "Workspace > Overview",
        "summary": "Market Movers, Futures Monitor, Macro Thermometer, events, sentiment를 먼저 확인합니다.",
        "safe_action": "Overview refresh 버튼은 bounded action facade를 통해 실행합니다.",
        "does_not_do": "trade signal, validation PASS, monitoring signal을 만들지 않습니다.",
        "next_step": "데이터가 비어 있거나 오래됐으면 데이터 갱신 / 복구 guide로 이동합니다.",
    },
    {
        "key": "data_freshness",
        "title": "데이터 갱신 / 복구",
        "owner_screen": "Workspace > Ingestion / Operations > System / Data Health",
        "summary": "가격, provider snapshot, sentiment, futures, macro 수집 상태와 실패 로그를 확인합니다.",
        "safe_action": "Ingestion 또는 Data Health가 소유한 job / artifact를 확인합니다.",
        "does_not_do": "Reference에서 provider fetch, DB write, registry write를 직접 실행하지 않습니다.",
        "next_step": "수집 후 Overview나 Backtest 화면에서 latest stored data 기준으로 다시 읽습니다.",
    },
    {
        "key": "candidate_creation",
        "title": "후보 만들기",
        "owner_screen": "Backtest > Backtest Analysis",
        "summary": "Single Strategy, Portfolio Mix Builder, saved mix replay로 selection source를 만듭니다.",
        "safe_action": "성과, benchmark, Data Trust, promotion policy signal을 같은 화면에서 확인합니다.",
        "does_not_do": "최종 선정, live approval, monitoring policy를 결정하지 않습니다.",
        "next_step": "source가 설명 가능하면 Practical Validation으로 넘깁니다.",
    },
    {
        "key": "evidence_review",
        "title": "검증 / 최종 판단",
        "owner_screen": "Backtest > Practical Validation / Backtest > Final Review",
        "summary": "검증 근거, blocker, open review item, selected-route gate를 확인합니다.",
        "safe_action": "NOT_RUN / REVIEW / BLOCKED의 owner screen을 찾아 보강합니다.",
        "does_not_do": "보류 / 거절 / 재검토 상태를 억지로 selected 후보로 저장하지 않습니다.",
        "next_step": "gate-passed result만 Final Review에서 모니터링 후보로 저장할 수 있습니다.",
    },
    {
        "key": "portfolio_monitoring",
        "title": "선정 후 모니터링",
        "owner_screen": "Operations > Portfolio Monitoring",
        "summary": "Final Review selected row를 dashboard portfolio slot으로 읽고 scenario update를 확인합니다.",
        "safe_action": "사용자가 지정한 start/latest mode와 balance 기준으로 read-only replay를 봅니다.",
        "does_not_do": "broker order, account sync, live approval, auto rebalance를 만들지 않습니다.",
        "next_step": "scenario가 stale이면 monitoring playbook에서 slot signature와 latest market date를 확인합니다.",
    },
    {
        "key": "troubleshooting",
        "title": "문제 해결",
        "owner_screen": "Reference > Guides",
        "summary": "stale data, NOT_RUN, Final Review 후보 미노출, monitoring stale scenario를 증상별로 봅니다.",
        "safe_action": "증상, first check, owner screen, stop condition을 먼저 분리합니다.",
        "does_not_do": "Reference에서 job 실행이나 저장소 수정을 대신하지 않습니다.",
        "next_step": "문제 owner screen으로 이동해 같은 기준으로 다시 확인합니다.",
    },
]


REFERENCE_JOURNEYS: list[dict[str, str]] = [
    {
        "key": "daily_market_context",
        "title": "Daily Market Context",
        "when_to_use": "시장 배경, 선물, sentiment, event를 먼저 보고 싶을 때",
        "screens": "Workspace > Overview",
        "records": "market DB tables, overview run history, local run artifacts",
        "go_review_stop": "Go: latest stored context visible / Review: stale but explainable / Stop: missing source or failed refresh",
        "boundary": "context-only evidence이며 Practical Validation PASS나 trade signal을 만들지 않습니다.",
    },
    {
        "key": "data_freshness_repair",
        "title": "Data Freshness Repair",
        "when_to_use": "차트나 validation evidence가 비어 있거나 stale일 때",
        "screens": "Workspace > Ingestion -> Operations > System / Data Health",
        "records": "MySQL finance tables, failure CSV, run artifacts, WEB_APP_RUN_HISTORY.jsonl",
        "go_review_stop": "Go: latest stored row confirmed / Review: provider stale or partial / Stop: job failure or source contract missing",
        "boundary": "UI가 provider/FRED를 직접 fetch하지 않고 ingestion/job boundary를 통해 확인합니다.",
    },
    {
        "key": "candidate_creation",
        "title": "Candidate Creation",
        "when_to_use": "전략 실행이나 mix 후보를 검증 source로 만들 때",
        "screens": "Backtest > Backtest Analysis",
        "records": "PORTFOLIO_SELECTION_SOURCES.jsonl, BACKTEST_RUN_HISTORY.jsonl",
        "go_review_stop": "Go: result + Data Trust + benchmark 설명 가능 / Review: warning 원인 명확 / Stop: run failure or source missing",
        "boundary": "Backtest Analysis는 최종 판단이나 live readiness를 소유하지 않습니다.",
    },
    {
        "key": "portfolio_selection",
        "title": "후보를 모니터링 후보로 보내기",
        "when_to_use": "후보 source를 Practical Validation과 Final Review까지 끝까지 볼 때",
        "screens": "Backtest Analysis -> Practical Validation -> Final Review -> Operations > Portfolio Monitoring",
        "records": "PORTFOLIO_SELECTION_SOURCES.jsonl -> PRACTICAL_VALIDATION_RESULTS.jsonl -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
        "go_review_stop": "Go: selected-route gate pass / Review: open review item / Stop: hard blocker or missing reason",
        "boundary": "monitoring 후보 선정은 broker order, live approval, auto rebalance가 아닙니다.",
    },
    {
        "key": "evidence_review",
        "title": "Evidence Review",
        "when_to_use": "Practical Validation / Final Review의 status와 blocker를 해석할 때",
        "screens": "Backtest > Practical Validation -> Backtest > Final Review",
        "records": "PRACTICAL_VALIDATION_RESULTS.jsonl, FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
        "go_review_stop": "Go: no selected-route blocker / Review: non-critical review item / Stop: critical NOT_RUN, NEEDS_INPUT, BLOCKED",
        "boundary": "NOT_RUN은 pass가 아니며, missing evidence는 보강 필요 상태로 표시합니다.",
    },
    {
        "key": "monitoring_after_selection",
        "title": "Monitoring After Selection",
        "when_to_use": "Final Review에서 선정된 row를 이후 성과 관찰 대상으로 볼 때",
        "screens": "Operations > Portfolio Monitoring",
        "records": "SELECTED_DASHBOARD_PORTFOLIOS.jsonl, optional SELECTED_PORTFOLIO_MONITORING_LOG.jsonl",
        "go_review_stop": "Go: scenario current / Review: stale replay or provider gap / Stop: selected decision missing",
        "boundary": "Portfolio Monitoring은 read-only scenario view이며 broker order, account sync, auto rebalance를 만들지 않습니다.",
    },
]


REFERENCE_CONCEPTS: list[dict[str, str]] = [
    {
        "term": "NOT_RUN",
        "plain_meaning": "검증이 실행되지 않았거나 필요한 evidence가 아직 없습니다.",
        "owner_screen": "Practical Validation / Final Review",
        "progress_implication": "pass가 아니라 evidence missing / not executed",
        "where_to_fix": "Ingestion, Backtest source, provider snapshot, selected-route preflight를 확인합니다.",
    },
    {
        "term": "REVIEW",
        "plain_meaning": "진행은 가능할 수 있지만 해석과 보강 조건을 남겨야 합니다.",
        "owner_screen": "Practical Validation / Final Review / Portfolio Monitoring",
        "progress_implication": "기본적으로 open review item이며 hard blocker와 분리합니다.",
        "where_to_fix": "해당 audit row의 owner screen과 evidence source를 확인합니다.",
    },
    {
        "term": "BLOCKED",
        "plain_meaning": "현재 조건에서는 다음 단계로 넘기면 안 되는 hard blocker입니다.",
        "owner_screen": "Backtest Analysis / Practical Validation / Final Review",
        "progress_implication": "selected-route progression is stopped until fixed",
        "where_to_fix": "데이터, source contract, component weight, benchmark parity, cost evidence를 원인 화면에서 보강합니다.",
    },
    {
        "term": "Data Trust",
        "plain_meaning": "결과가 어떤 데이터 freshness와 coverage 조건에서 만들어졌는지 보여주는 신뢰도 신호입니다.",
        "owner_screen": "Backtest Analysis",
        "progress_implication": "warning 또는 blocked이면 Practical Validation에 넘기기 전 원인을 설명해야 합니다.",
        "where_to_fix": "Workspace > Ingestion과 System / Data Health에서 source 상태를 확인합니다.",
    },
    {
        "term": "Provider Coverage",
        "plain_meaning": "ETF holdings, exposure, issuer/provider snapshot이 실제/partial/proxy 중 어떤 근거인지 나타냅니다.",
        "owner_screen": "Practical Validation / Portfolio Monitoring",
        "progress_implication": "partial or proxy coverage is review evidence, not pass.",
        "where_to_fix": "Ingestion provider snapshot job과 Provider Data Gaps를 확인합니다.",
    },
    {
        "term": "Portfolio Monitoring Scenario",
        "plain_meaning": "selected decision strategy slot을 사용자가 지정한 start/latest mode와 balance로 다시 보는 session replay입니다.",
        "owner_screen": "Operations > Portfolio Monitoring",
        "progress_implication": "사후 관찰 근거이며 새 최종 판단이나 주문 지시가 아닙니다.",
        "where_to_fix": "scenario stale state, slot signature, latest market date를 확인합니다.",
    },
]


REFERENCE_RECORDS: list[dict[str, str]] = [
    {
        "record": "PORTFOLIO_SELECTION_SOURCES.jsonl",
        "kind": "workflow registry",
        "owner": "Backtest > Backtest Analysis",
        "meaning": "Practical Validation이 읽는 current selection source",
        "commit_policy": "append-only workflow registry이며 명시 요청 없이 재작성하지 않음",
    },
    {
        "record": "PRACTICAL_VALIDATION_RESULTS.jsonl",
        "kind": "workflow registry",
        "owner": "Backtest > Practical Validation",
        "meaning": "Final Review가 읽는 compact validation evidence",
        "commit_policy": "append-only workflow registry이며 raw holdings/provider response를 대체하지 않음",
    },
    {
        "record": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
        "kind": "workflow registry",
        "owner": "Backtest > Final Review",
        "meaning": "Portfolio Monitoring 후보 선정 판단",
        "commit_policy": "append-only workflow registry이며 live approval record가 아님",
    },
    {
        "record": "SELECTED_DASHBOARD_PORTFOLIOS.jsonl",
        "kind": "saved setup",
        "owner": "Operations > Portfolio Monitoring",
        "meaning": "사용자가 만든 dashboard portfolio setup과 selected decision strategy slot",
        "commit_policy": "사용자 saved setup이므로 명시 요청 없이 정리 / 삭제하지 않음",
    },
    {
        "record": "BACKTEST_RUN_HISTORY.jsonl",
        "kind": "run history",
        "owner": "Operations > Archive: Backtest Runs",
        "meaning": "로컬 backtest 실행 기록과 replay helper input",
        "commit_policy": "generated/local artifact로 보통 커밋하지 않음",
    },
    {
        "record": "run_artifacts/",
        "kind": "generated artifact",
        "owner": "Operations > System / Data Health",
        "meaning": "job failure CSV, diagnostics, local operation evidence",
        "commit_policy": "generated/local artifact로 보통 커밋하지 않음",
    },
]


REFERENCE_PLAYBOOKS: list[dict[str, str]] = [
    {
        "key": "overview_futures_stale",
        "title": "Overview / Futures data가 stale일 때",
        "symptom": "Refresh 후에도 Futures Monitor 차트가 비어 있거나 오래된 데이터로 보입니다.",
        "owner_screen": "Workspace > Overview / Workspace > Ingestion / Operations > System / Data Health",
        "first_check": "latest stored candle time, stale badge, selected lookback window, recent run artifact를 확인합니다.",
        "safe_action": "Overview refresh 또는 Ingestion futures job을 owner screen에서 다시 실행합니다.",
        "stop_condition": "provider가 latest row를 주지 않으면 UI는 latest stored stale context만 보여줄 수 있습니다.",
    },
    {
        "key": "NOT_RUN",
        "title": "Practical Validation에 NOT_RUN이 있을 때",
        "symptom": "검증 board에 NOT_RUN 또는 missing evidence row가 남아 있습니다.",
        "owner_screen": "Backtest > Practical Validation / Workspace > Ingestion",
        "first_check": "해당 module이 Required인지 Conditional인지, source traits와 provider coverage가 있는지 확인합니다.",
        "safe_action": "Provider Data Gaps나 Ingestion source job으로 보강 가능한 evidence를 먼저 수집합니다.",
        "stop_condition": "critical NOT_RUN은 pass로 해석하지 않고 Final Review selected-route blocker로 봅니다.",
    },
    {
        "key": "final_review_source_missing",
        "title": "Final Review 후보가 보이지 않을 때",
        "symptom": "Practical Validation을 저장했는데 Final Review source picker에서 후보가 보이지 않습니다.",
        "owner_screen": "Backtest > Practical Validation / Backtest > Final Review",
        "first_check": "selected-route preflight, can_save_and_move, gate-passed result 여부를 확인합니다.",
        "safe_action": "blocked / needs input row는 기록으로 남아도 Final Review 후보에서 숨겨질 수 있으므로 원인 board로 돌아갑니다.",
        "stop_condition": "Gate 미통과 result를 Final Review 후보로 강제 노출하지 않습니다.",
    },
    {
        "key": "portfolio_monitoring_stale",
        "title": "Portfolio Monitoring scenario가 stale일 때",
        "symptom": "선정된 전략 slot은 있지만 최신 scenario 값이 없거나 stale로 표시됩니다.",
        "owner_screen": "Operations > Portfolio Monitoring",
        "first_check": "selected decision row, slot signature, latest-end mode, DB latest market date를 확인합니다.",
        "safe_action": "portfolio scenario update를 owner screen에서 실행하고, 필요할 때만 전체 재실행을 선택합니다.",
        "stop_condition": "monitoring scenario는 live order나 자동 rebalance trigger가 아닙니다.",
    },
]


def get_reference_center_catalog() -> dict[str, list[dict[str, str]]]:
    return {
        "task_cards": deepcopy(REFERENCE_TASK_CARDS),
        "journeys": deepcopy(REFERENCE_JOURNEYS),
        "concepts": deepcopy(REFERENCE_CONCEPTS),
        "records": deepcopy(REFERENCE_RECORDS),
        "playbooks": deepcopy(REFERENCE_PLAYBOOKS),
    }
