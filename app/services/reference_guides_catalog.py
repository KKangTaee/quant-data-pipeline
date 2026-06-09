from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.reference_glossary_catalog import get_reference_concept_dictionary

REFERENCE_TASK_CARDS: list[dict[str, Any]] = [
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


REFERENCE_JOURNEYS: list[dict[str, Any]] = [
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
    {
        "key": "archive_recovery",
        "title": "Archive / Recovery",
        "when_to_use": "과거 run, candidate, failure artifact를 다시 열어 원인을 복원할 때",
        "screens": "Operations > Archive: Backtest Runs / Archive: Candidates / System / Data Health",
        "records": "BACKTEST_RUN_HISTORY.jsonl, CURRENT_CANDIDATE_REGISTRY.jsonl, PRE_LIVE_CANDIDATE_REGISTRY.jsonl, run_artifacts/",
        "go_review_stop": "Go: replay contract or artifact found / Review: compact snapshot only / Stop: missing source or generated artifact unavailable",
        "boundary": "archive는 recovery / inspection surface이며 새 selected decision이나 live operation을 만들지 않습니다.",
    },
]


REFERENCE_JOURNEY_DETAILS: dict[str, dict[str, Any]] = {
    "daily_market_context": {
        "steps": [
            {
                "order": "1",
                "owner_screen": "Workspace > Overview",
                "check": "Market Movers, Futures Monitor, Sentiment, Event Calendar의 latest stored 기준일을 확인합니다.",
                "safe_next": "stale badge가 있어도 latest stored context가 보이면 market context로만 읽습니다.",
                "downstream": "Backtest Analysis 전에 시장 배경으로 참고",
                "stop_condition": "provider / DB source가 비어 있으면 Overview 판단을 trade signal처럼 쓰지 않습니다.",
            },
            {
                "order": "2",
                "owner_screen": "Workspace > Overview",
                "check": "Refresh 결과가 실제 latest row를 갱신했는지, 아니면 stale-but-visible 상태인지 구분합니다.",
                "safe_next": "갱신 실패나 stale 원인은 Data Freshness Repair journey로 넘깁니다.",
                "downstream": "Workspace > Ingestion / System / Data Health",
                "stop_condition": "휴장 / 주말 / provider 지연은 UI 결함이 아니라 freshness 상태일 수 있습니다.",
            },
            {
                "order": "3",
                "owner_screen": "Backtest > Backtest Analysis",
                "check": "시장 배경을 후보 생성의 참고로만 사용하고, validation PASS 근거로 승격하지 않습니다.",
                "safe_next": "후보 자체의 Data Trust와 benchmark evidence를 별도로 확인합니다.",
                "downstream": "Candidate Creation",
                "stop_condition": "Overview context가 좋다는 이유만으로 selected-route 판단을 하지 않습니다.",
            },
        ],
        "failure_states": [
            {
                "state": "Futures / sentiment가 stale",
                "owner_screen": "Workspace > Overview / Workspace > Ingestion",
                "first_check": "latest stored timestamp, stale badge, run artifact",
                "safe_next": "Data Freshness Repair journey로 이동",
                "stop_condition": "stale context를 fresh signal처럼 해석하지 않음",
            },
            {
                "state": "Overview refresh 실패",
                "owner_screen": "Operations > System / Data Health",
                "first_check": "최근 web app run health와 failure artifact",
                "safe_next": "owner screen에서 실패 job 확인",
                "stop_condition": "Reference에서 refresh action을 대신 실행하지 않음",
            },
        ],
    },
    "data_freshness_repair": {
        "steps": [
            {
                "order": "1",
                "owner_screen": "Workspace > Ingestion",
                "check": "가격, futures, sentiment, provider snapshot 중 어떤 source가 비었는지 분리합니다.",
                "safe_next": "필요한 ingestion job과 최신 저장 row를 확인합니다.",
                "downstream": "DB / loader read path",
                "stop_condition": "Reference에서 provider fetch나 DB write를 직접 수행하지 않습니다.",
            },
            {
                "order": "2",
                "owner_screen": "Operations > System / Data Health",
                "check": "수집 성공 여부, failure CSV, run artifact, web app run health를 확인합니다.",
                "safe_next": "성공했는데 UI가 못 읽으면 loader / read model 경계 문제로 분리합니다.",
                "downstream": "owner screen 재확인",
                "stop_condition": "실패 artifact가 남아 있으면 downstream validation을 pass로 보지 않습니다.",
            },
            {
                "order": "3",
                "owner_screen": "Backtest / Practical Validation / Overview",
                "check": "수집 후 실제 화면이 latest stored data를 다시 읽는지 확인합니다.",
                "safe_next": "그래도 stale이면 해당 surface의 playbook으로 원인을 좁힙니다.",
                "downstream": "원래 막혔던 화면",
                "stop_condition": "run history만 성공이고 화면 evidence가 비어 있으면 완료로 보지 않습니다.",
            },
        ],
        "failure_states": [
            {
                "state": "Provider source 자체가 stale",
                "owner_screen": "Workspace > Ingestion",
                "first_check": "provider latest date와 source freshness",
                "safe_next": "stale-but-known으로 표시하고 downstream에는 REVIEW로 전달",
                "stop_condition": "provider가 최신 row를 주지 않으면 UI가 fresh로 승격하지 않음",
            },
            {
                "state": "UI가 최신 수집 결과를 못 읽음",
                "owner_screen": "Operations > System / Data Health",
                "first_check": "job success, DB latest row, loader read path, surface cache",
                "safe_next": "owner 화면에서 run artifact와 loader boundary를 확인",
                "stop_condition": "Reference는 수집 성공을 대신 보장하지 않음",
            },
            {
                "state": "Source contract missing",
                "owner_screen": "Backtest Analysis / Practical Validation",
                "first_check": "selection source id, replay contract, component weight",
                "safe_next": "후보 생성 화면으로 돌아가 source를 다시 저장",
                "stop_condition": "source가 없으면 validation / final review로 강제 진행하지 않음",
            },
        ],
    },
    "candidate_creation": {
        "steps": [
            {
                "order": "1",
                "owner_screen": "Backtest > Backtest Analysis",
                "check": "Single Strategy, Portfolio Mix Builder, saved mix replay 중 현재 후보 생성 방식을 고릅니다.",
                "safe_next": "성과 / benchmark / Data Trust를 함께 확인합니다.",
                "downstream": "Portfolio Selection Source",
                "stop_condition": "실행 실패나 source id 누락은 Practical Validation 입력이 아닙니다.",
            },
            {
                "order": "2",
                "owner_screen": "Backtest > Backtest Analysis",
                "check": "component role, target weight, weight reason이 mix source에 남는지 확인합니다.",
                "safe_next": "비중과 이유가 설명 가능하면 Practical Validation으로 이동합니다.",
                "downstream": "Practical Validation",
                "stop_condition": "weight 합계나 role reason이 비면 Final Review에서 blocker가 됩니다.",
            },
            {
                "order": "3",
                "owner_screen": "Backtest > Practical Validation",
                "check": "current selection source가 실제 검증 입력으로 보이는지 확인합니다.",
                "safe_next": "source가 보이면 profile과 evidence 검증으로 진행합니다.",
                "downstream": "Evidence Review",
                "stop_condition": "Candidate Review / legacy Proposal 저장만으로는 새 검증 source가 아닙니다.",
            },
        ],
        "failure_states": [
            {
                "state": "Run failure",
                "owner_screen": "Backtest > Backtest Analysis",
                "first_check": "input payload, DB price coverage, execution error",
                "safe_next": "실행 조건을 고친 뒤 같은 후보를 다시 실행",
                "stop_condition": "실패한 run을 source로 저장하지 않음",
            },
            {
                "state": "Mix weight incomplete",
                "owner_screen": "Backtest > Portfolio Mix Builder",
                "first_check": "target weight total, component role, weight reason",
                "safe_next": "weight builder에서 source contract를 보강",
                "stop_condition": "비중 근거가 없으면 selected-route blocker로 남음",
            },
        ],
    },
    "portfolio_selection": {
        "steps": [
            {
                "order": "1",
                "owner_screen": "Backtest > Practical Validation",
                "check": "source traits, profile, required / conditional / reference modules를 확인합니다.",
                "safe_next": "critical NOT_RUN / BLOCKED가 없을 때 결과를 저장합니다.",
                "downstream": "PRACTICAL_VALIDATION_RESULTS.jsonl",
                "stop_condition": "NOT_RUN을 pass로 해석하지 않습니다.",
            },
            {
                "order": "2",
                "owner_screen": "Backtest > Final Review",
                "check": "selected-route gate, open review items, operator reason을 확인합니다.",
                "safe_next": "gate-passed row만 모니터링 후보로 저장합니다.",
                "downstream": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
                "stop_condition": "hard blocker가 남으면 hold / reject / re-review로 남깁니다.",
            },
            {
                "order": "3",
                "owner_screen": "Operations > Portfolio Monitoring",
                "check": "Final Review selected row가 dashboard portfolio slot으로 읽히는지 확인합니다.",
                "safe_next": "scenario update는 Operations에서 명시 실행합니다.",
                "downstream": "Monitoring After Selection",
                "stop_condition": "선정 row는 주문 지시나 broker approval이 아닙니다.",
            },
        ],
        "failure_states": [
            {
                "state": "Final Review 후보 미노출",
                "owner_screen": "Backtest > Practical Validation / Final Review",
                "first_check": "can_save_and_move, selected-route preflight, gate-passed result",
                "safe_next": "원인 board로 돌아가 critical row 보강",
                "stop_condition": "gate 미통과 result를 강제 노출하지 않음",
            },
            {
                "state": "operator reason missing",
                "owner_screen": "Backtest > Final Review",
                "first_check": "decision reason, checklist, selected-route gate status",
                "safe_next": "Final Review에서 판단 사유 보강",
                "stop_condition": "사유 없는 selected decision 저장을 하지 않음",
            },
        ],
    },
    "evidence_review": {
        "steps": [
            {
                "order": "1",
                "owner_screen": "Backtest > Practical Validation",
                "check": "Input Evidence, Practical Diagnostics, Provider Action Center, Robustness Lab을 순서대로 봅니다.",
                "safe_next": "critical gap은 owner screen으로 되돌립니다.",
                "downstream": "Final Review Gate",
                "stop_condition": "missing evidence를 PASS로 승격하지 않습니다.",
            },
            {
                "order": "2",
                "owner_screen": "Backtest > Final Review",
                "check": "open review item과 selected-route blocker를 분리합니다.",
                "safe_next": "open review는 reason에 남기고 blocker는 진행 중단합니다.",
                "downstream": "Final Selection Decision",
                "stop_condition": "BLOCKED / NEEDS_INPUT은 selected-route 조건을 막습니다.",
            },
            {
                "order": "3",
                "owner_screen": "Reference > Guides",
                "check": "상태 의미가 헷갈리면 status lookup과 playbook을 다시 확인합니다.",
                "safe_next": "owner screen으로 돌아가 evidence를 보강합니다.",
                "downstream": "원인 화면",
                "stop_condition": "Reference 자체가 evidence source는 아닙니다.",
            },
        ],
        "failure_states": [
            {
                "state": "NOT_RUN remains critical",
                "owner_screen": "Backtest > Practical Validation",
                "first_check": "module requirement, replay status, provider coverage",
                "safe_next": "replay / provider collection / source correction",
                "stop_condition": "critical NOT_RUN은 pass가 아님",
            },
            {
                "state": "REVIEW item misunderstood as blocker",
                "owner_screen": "Backtest > Final Review",
                "first_check": "policy evidence route and severity",
                "safe_next": "open review item으로 남길지 blocker인지 분리",
                "stop_condition": "severity를 확인하지 않고 강제 진행하지 않음",
            },
        ],
    },
    "monitoring_after_selection": {
        "steps": [
            {
                "order": "1",
                "owner_screen": "Operations > Portfolio Monitoring",
                "check": "Final Review selected row가 strategy pool에 있고 dashboard portfolio slot에 연결됐는지 확인합니다.",
                "safe_next": "slot start/latest mode/balance/memo를 설정합니다.",
                "downstream": "SELECTED_DASHBOARD_PORTFOLIOS.jsonl",
                "stop_condition": "selected decision row가 없으면 monitoring 대상이 아닙니다.",
            },
            {
                "order": "2",
                "owner_screen": "Operations > Portfolio Monitoring",
                "check": "scenario signature가 active portfolio / slot / selected decision / period / balance와 맞는지 확인합니다.",
                "safe_next": "stale이면 scenario update를 명시 실행합니다.",
                "downstream": "session replay result",
                "stop_condition": "stale scenario를 current monitoring evidence로 쓰지 않습니다.",
            },
            {
                "order": "3",
                "owner_screen": "Operations > Portfolio Monitoring",
                "check": "Monitoring Signals, open issues, provider evidence, allocation boundary를 read-only로 해석합니다.",
                "safe_next": "보강 필요 사항은 원래 evidence owner로 되돌립니다.",
                "downstream": "Operations follow-up",
                "stop_condition": "allocation drift preview는 order / rebalance instruction이 아닙니다.",
            },
        ],
        "failure_states": [
            {
                "state": "Selected decision missing",
                "owner_screen": "Backtest > Final Review",
                "first_check": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl selected route",
                "safe_next": "Final Review selected-route gate부터 확인",
                "stop_condition": "saved dashboard setup만으로 monitoring 후보를 만들지 않음",
            },
            {
                "state": "Scenario stale",
                "owner_screen": "Operations > Portfolio Monitoring",
                "first_check": "slot signature, latest market date, replay result timestamp",
                "safe_next": "portfolio scenario update 명시 실행",
                "stop_condition": "stale scenario는 최신 성과 근거가 아님",
            },
        ],
    },
    "archive_recovery": {
        "steps": [
            {
                "order": "1",
                "owner_screen": "Operations > Archive: Backtest Runs",
                "check": "과거 실행 payload, result summary, replay 가능 여부를 확인합니다.",
                "safe_next": "필요하면 Backtest Analysis form으로 load / run again을 사용합니다.",
                "downstream": "Backtest Analysis",
                "stop_condition": "run history만으로 Final Review selected row를 만들지 않습니다.",
            },
            {
                "order": "2",
                "owner_screen": "Operations > Archive: Candidates",
                "check": "current / Pre-Live candidate compact snapshot과 replay contract를 확인합니다.",
                "safe_next": "source 재생성이 가능하면 현재 Backtest flow로 다시 넘깁니다.",
                "downstream": "Backtest Analysis / Practical Validation",
                "stop_condition": "legacy registry를 새 current source로 덮어쓰지 않습니다.",
            },
            {
                "order": "3",
                "owner_screen": "Operations > System / Data Health",
                "check": "failure CSV와 run artifact가 남아 있는지 확인합니다.",
                "safe_next": "data freshness 원인으로 분리하거나 owner job에서 재실행합니다.",
                "downstream": "Data Freshness Repair",
                "stop_condition": "generated artifact가 없으면 Reference에서 복원하지 않습니다.",
            },
        ],
        "failure_states": [
            {
                "state": "Compact snapshot only",
                "owner_screen": "Operations > Archive: Candidates",
                "first_check": "registry row와 replay contract coverage",
                "safe_next": "DB-backed replay 가능 여부 확인",
                "stop_condition": "compact snapshot을 full result artifact로 오해하지 않음",
            },
            {
                "state": "Missing generated artifact",
                "owner_screen": "Operations > System / Data Health",
                "first_check": "run_artifacts path and failure file existence",
                "safe_next": "가능하면 owner job 재실행",
                "stop_condition": "Reference에서 artifact를 새로 만들지 않음",
            },
        ],
    },
}


REFERENCE_RECORDS: list[dict[str, Any]] = [
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


REFERENCE_PLAYBOOKS: list[dict[str, Any]] = [
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
        "key": "ingestion_success_ui_stale",
        "title": "Ingestion은 성공했는데 UI가 갱신되지 않을 때",
        "symptom": "수집 job은 성공으로 보이지만 Overview / Backtest / Validation 화면이 예전 값을 계속 보여줍니다.",
        "owner_screen": "Workspace > Ingestion / Operations > System / Data Health / affected UI surface",
        "first_check": "job success만 보지 말고 DB latest row, loader read path, 화면의 기준일 / cache 상태를 함께 봅니다.",
        "safe_action": "affected UI surface를 다시 열고, System / Data Health에서 run artifact와 loader boundary를 확인합니다.",
        "stop_condition": "Reference에서 cache clear, DB rewrite, registry rewrite를 직접 수행하지 않습니다.",
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
        "key": "provider_snapshot_missing",
        "title": "Provider snapshot / look-through evidence가 없을 때",
        "symptom": "ETF holdings, exposure, provider coverage가 partial / proxy / missing으로 남아 validation이나 monitoring에서 REVIEW / NEEDS_INPUT이 됩니다.",
        "owner_screen": "Backtest > Practical Validation / Workspace > Ingestion / Operations > Portfolio Monitoring",
        "first_check": "Provider Data Gaps에서 수집 가능한 connector와 source mapping 필요 항목을 구분합니다.",
        "safe_action": "Practical Validation의 Provider Action Center 또는 Ingestion provider snapshot job을 owner screen에서 실행합니다.",
        "stop_condition": "partial / proxy evidence를 official provider PASS처럼 해석하지 않습니다.",
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
    {
        "key": "archive_recovery",
        "title": "Archive에서 과거 run / candidate를 복원해야 할 때",
        "symptom": "과거 backtest run, candidate, failure artifact를 다시 열어 현재 workflow로 이어야 합니다.",
        "owner_screen": "Operations > Archive: Backtest Runs / Operations > Archive: Candidates / Operations > System / Data Health",
        "first_check": "run history row, candidate replay contract, generated artifact 존재 여부를 확인합니다.",
        "safe_action": "가능하면 owner archive 화면에서 run again / load into form / candidate replay를 사용합니다.",
        "stop_condition": "archive record를 새 Final Review selected decision으로 직접 변환하지 않습니다.",
    },
]


REFERENCE_PLAYBOOK_DETAILS: dict[str, dict[str, Any]] = {
    "overview_futures_stale": {
        "check_steps": [
            {
                "order": "1",
                "check": "Futures Monitor의 latest stored candle time과 stale badge를 함께 봅니다.",
                "owner_screen": "Workspace > Overview",
                "pass_signal": "차트가 latest stored row를 보여주고 stale 이유가 표시됨",
            },
            {
                "order": "2",
                "check": "lookback window가 latest stored row를 포함하는지 확인합니다.",
                "owner_screen": "Workspace > Overview",
                "pass_signal": "window 밖 데이터가 Missing처럼 숨겨지지 않음",
            },
            {
                "order": "3",
                "check": "최근 futures ingestion run artifact와 provider 응답 상태를 확인합니다.",
                "owner_screen": "Workspace > Ingestion / System / Data Health",
                "pass_signal": "provider 지연 / 휴장 / 실패가 구분됨",
            },
        ],
        "evidence_locations": [
            "futures OHLCV DB table",
            "Workspace > Overview stale badge",
            "WEB_APP_RUN_HISTORY.jsonl",
            "run_artifacts/",
        ],
    },
    "ingestion_success_ui_stale": {
        "check_steps": [
            {
                "order": "1",
                "check": "성공한 job이 실제로 해당 ticker/source의 latest row를 만들었는지 확인합니다.",
                "owner_screen": "Workspace > Ingestion",
                "pass_signal": "DB latest market date / row count가 갱신됨",
            },
            {
                "order": "2",
                "check": "화면이 읽는 loader/source가 수집한 source와 같은지 확인합니다.",
                "owner_screen": "Operations > System / Data Health",
                "pass_signal": "loader read path와 source contract가 일치",
            },
            {
                "order": "3",
                "check": "affected UI가 latest stored 기준일을 다시 표시하는지 확인합니다.",
                "owner_screen": "affected UI surface",
                "pass_signal": "화면 기준일과 DB latest row가 일치",
            },
        ],
        "evidence_locations": [
            "MySQL finance tables",
            "WEB_APP_RUN_HISTORY.jsonl",
            "run_artifacts/",
            "affected UI date / freshness badge",
        ],
    },
    "NOT_RUN": {
        "check_steps": [
            {
                "order": "1",
                "check": "NOT_RUN module이 Required / Conditional / Reference 중 무엇인지 확인합니다.",
                "owner_screen": "Backtest > Practical Validation",
                "pass_signal": "gate effect와 owner board가 분리됨",
            },
            {
                "order": "2",
                "check": "runtime replay, provider coverage, source traits 중 어떤 evidence가 비었는지 확인합니다.",
                "owner_screen": "Backtest > Practical Validation",
                "pass_signal": "missing evidence source가 특정됨",
            },
            {
                "order": "3",
                "check": "수집 / replay / source 수정이 필요한 경우 owner screen에서 보강합니다.",
                "owner_screen": "Workspace > Ingestion / Backtest > Backtest Analysis",
                "pass_signal": "재검증 후 NOT_RUN이 PASS / REVIEW / BLOCKED로 재분류됨",
            },
        ],
        "evidence_locations": [
            "PRACTICAL_VALIDATION_RESULTS.jsonl",
            "Practical Validation module map",
            "Provider Data Gaps",
            "Portfolio Selection Source",
        ],
    },
    "provider_snapshot_missing": {
        "check_steps": [
            {
                "order": "1",
                "check": "Provider Data Gaps에서 holdings / exposure / operability 중 무엇이 비었는지 확인합니다.",
                "owner_screen": "Backtest > Practical Validation",
                "pass_signal": "수집 가능 gap과 connector mapping 필요 gap이 분리됨",
            },
            {
                "order": "2",
                "check": "official / bridge / proxy / missing evidence type과 freshness를 확인합니다.",
                "owner_screen": "Workspace > Ingestion / Provider snapshot",
                "pass_signal": "evidence source와 latest date가 표시됨",
            },
            {
                "order": "3",
                "check": "보강 후 Practical Validation이나 Portfolio Monitoring에서 provider evidence를 다시 읽습니다.",
                "owner_screen": "Backtest > Practical Validation / Operations > Portfolio Monitoring",
                "pass_signal": "coverage row가 PASS / REVIEW / NEEDS_INPUT으로 재분류됨",
            },
        ],
        "evidence_locations": [
            "ETF provider snapshot DB tables",
            "Provider Data Gaps",
            "PRACTICAL_VALIDATION_RESULTS.jsonl",
            "Portfolio Monitoring provider evidence table",
        ],
    },
    "final_review_source_missing": {
        "check_steps": [
            {
                "order": "1",
                "check": "Practical Validation result가 저장됐는지와 Final Review 이동 gate가 통과됐는지 확인합니다.",
                "owner_screen": "Backtest > Practical Validation",
                "pass_signal": "can_save_and_move / gate-passed 상태가 명확",
            },
            {
                "order": "2",
                "check": "selected-route blocker, critical NOT_RUN, NEEDS_INPUT row가 남아 있는지 봅니다.",
                "owner_screen": "Backtest > Final Review",
                "pass_signal": "후보 미노출 원인이 specific blocker로 표시됨",
            },
            {
                "order": "3",
                "check": "원인 board로 돌아가 source / provider / role / weight / replay evidence를 보강합니다.",
                "owner_screen": "Backtest > Practical Validation / Backtest > Backtest Analysis",
                "pass_signal": "보강 후 source picker에 표시 가능",
            },
        ],
        "evidence_locations": [
            "PRACTICAL_VALIDATION_RESULTS.jsonl",
            "Final Review source picker",
            "selected-route gate policy evidence",
        ],
    },
    "portfolio_monitoring_stale": {
        "check_steps": [
            {
                "order": "1",
                "check": "selected decision row가 strategy pool에 있고 dashboard portfolio slot에 연결됐는지 확인합니다.",
                "owner_screen": "Operations > Portfolio Monitoring",
                "pass_signal": "slot signature가 selected decision과 일치",
            },
            {
                "order": "2",
                "check": "latest-end mode, DB latest market date, scenario result timestamp가 맞는지 확인합니다.",
                "owner_screen": "Operations > Portfolio Monitoring",
                "pass_signal": "scenario current / stale 이유가 표시됨",
            },
            {
                "order": "3",
                "check": "필요하면 portfolio scenario update를 명시 실행하고, full refresh 여부를 선택합니다.",
                "owner_screen": "Operations > Portfolio Monitoring",
                "pass_signal": "portfolio-wide value / strategy performance가 새 signature로 계산됨",
            },
        ],
        "evidence_locations": [
            "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
            "SELECTED_DASHBOARD_PORTFOLIOS.jsonl",
            "Portfolio Monitoring scenario session result",
            "DB latest market date",
        ],
    },
    "archive_recovery": {
        "check_steps": [
            {
                "order": "1",
                "check": "Backtest Run History에서 원래 payload와 result summary를 확인합니다.",
                "owner_screen": "Operations > Archive: Backtest Runs",
                "pass_signal": "run again 또는 load into form 가능",
            },
            {
                "order": "2",
                "check": "Candidate Library에서 compact snapshot과 replay contract를 확인합니다.",
                "owner_screen": "Operations > Archive: Candidates",
                "pass_signal": "현재 Backtest Analysis source로 재생성 가능",
            },
            {
                "order": "3",
                "check": "failure artifact가 필요한 경우 System / Data Health에서 해당 파일 존재 여부를 확인합니다.",
                "owner_screen": "Operations > System / Data Health",
                "pass_signal": "failure CSV / run artifact가 확인됨",
            },
        ],
        "evidence_locations": [
            "BACKTEST_RUN_HISTORY.jsonl",
            "CURRENT_CANDIDATE_REGISTRY.jsonl",
            "PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
            "run_artifacts/",
        ],
    },
}


def _merge_catalog_details(
    rows: list[dict[str, Any]],
    details_by_key: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    merged_rows = deepcopy(rows)
    for row in merged_rows:
        key = str(row.get("key") or "")
        row.update(deepcopy(details_by_key.get(key, {})))
    return merged_rows


def get_reference_center_catalog() -> dict[str, list[dict[str, Any]]]:
    return {
        "task_cards": deepcopy(REFERENCE_TASK_CARDS),
        "journeys": _merge_catalog_details(REFERENCE_JOURNEYS, REFERENCE_JOURNEY_DETAILS),
        "concepts": get_reference_concept_dictionary(),
        "records": deepcopy(REFERENCE_RECORDS),
        "playbooks": _merge_catalog_details(REFERENCE_PLAYBOOKS, REFERENCE_PLAYBOOK_DETAILS),
    }
