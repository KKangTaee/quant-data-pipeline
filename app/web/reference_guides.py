from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from html import escape
from textwrap import dedent
from typing import Any

import pandas as pd
import streamlit as st


GUIDE_ROUTE_OPTIONS = [
    "단일 후보",
    "여러 후보 묶음",
    "저장된 비중 조합",
    "보류 / 재검토",
]


def _route_cards() -> dict[str, dict[str, Any]]:
    return {
        "단일 후보": {
            "headline": "전략 하나를 끝까지 검토",
            "summary": "후보 1개를 Clean V2 selection source로 저장하고 Practical Validation을 거쳐 Final Review가 직접 읽는 경로입니다.",
            "goal": "후보 1개를 Practical Validation 결과로 만든 뒤 Final Review에서 최종 판단합니다.",
            "sequence": "Backtest Analysis -> Practical Validation -> Final Review",
            "caution": "Review Note / Pre-Live / Proposal 저장은 더 이상 필수 경로가 아닙니다.",
            "records": "Portfolio Selection Source, Practical Validation Result, Final Decision V2",
            "dot": [
                ("analysis", "1\\nBacktest Analysis", "run"),
                ("validation", "2\\nPractical Validation", "gate"),
                ("final", "3\\nFinal Review V2", "final"),
                ("dashboard", "4\\nSelected Dashboard", "compare"),
            ],
            "edges": [
                ("analysis", "validation", "selection source"),
                ("validation", "final", "validation result"),
                ("final", "dashboard", "selected decision"),
            ],
        },
        "여러 후보 묶음": {
            "headline": "여러 후보를 하나의 portfolio source로 묶기",
            "summary": "Compare에서 후보들을 비교하고 target weight가 있는 Clean V2 source로 저장하는 경로입니다.",
            "goal": "여러 전략의 역할과 target weight를 Backtest Analysis에서 정한 뒤 Practical Validation으로 보냅니다.",
            "sequence": "Backtest Analysis compare / weight builder -> Practical Validation -> Final Review",
            "caution": "Portfolio Proposal의 legacy weight builder는 compatibility 경로입니다. 새 조합 실험은 Backtest Analysis가 맡습니다.",
            "records": "Portfolio Selection Source, Practical Validation Result, Final Decision V2",
            "dot": [
                ("compare", "1A\\nCompare", "compare"),
                ("weights", "1B\\nRole + Weight", "proposal"),
                ("validation", "2\\nPractical Validation", "gate"),
                ("final", "3\\nFinal Review V2", "final"),
                ("dashboard", "4\\nSelected Dashboard", "compare"),
            ],
            "edges": [
                ("compare", "weights", "비중 구성"),
                ("weights", "validation", "Clean V2 source"),
                ("validation", "final", "검증 결과"),
                ("final", "dashboard", "선정 row"),
            ],
        },
        "저장된 비중 조합": {
            "headline": "이미 저장된 weight setup을 workflow 기록으로 연결",
            "summary": "Compare에서 저장한 mix를 재실행한 뒤 Practical Validation source로 연결합니다.",
            "goal": "Saved Portfolio에 저장된 재사용 weight setup을 다시 검토해 Clean V2 source로 연결합니다.",
            "sequence": "저장된 비중 조합 선택 -> Mix 재실행 및 검증 -> Practical Validation -> Final Review",
            "caution": "Saved Portfolio는 후보 registry가 아닙니다. Candidate Review / legacy Proposal 저장을 필수로 거치지 않습니다.",
            "records": "Saved Portfolio, Portfolio Selection Source, Practical Validation Result, Final Decision V2",
            "dot": [
                ("saved", "1A\\nSaved Weight Setup", "compare"),
                ("replay", "1B\\nMix Replay", "gate"),
                ("validation", "2\\nPractical Validation", "gate"),
                ("final", "3\\nFinal Review V2", "final"),
                ("dashboard", "4\\nSelected Dashboard", "compare"),
            ],
            "edges": [
                ("saved", "replay", "replay"),
                ("replay", "validation", "Clean V2 source"),
                ("validation", "final", "검증 결과"),
                ("final", "dashboard", "선정 row"),
            ],
        },
        "보류 / 재검토": {
            "headline": "멈춰야 할 이유를 원인 화면으로 되돌림",
            "summary": "hold, blocked, evidence 부족, re-review가 나오면 Final Review 직행이 아니라 원인 화면으로 돌아갑니다.",
            "goal": "진행이 막혔을 때 최종 선정으로 밀고 가지 않고 원인 화면으로 돌아갑니다.",
            "sequence": "막힘 원인 확인 -> 소유 화면으로 복귀 -> 데이터 / 근거 / 구성 보강 -> 같은 기준으로 재검토",
            "caution": "hold, blocked, evidence 부족 상태는 최종 선정이 아니라 보류 또는 재검토로 남깁니다.",
            "records": "Practical Validation Result 또는 Final Decision V2에 보류 / 재검토 사유 기록",
            "dot": [
                ("source", "1\\n원인 화면", "stop"),
                ("validation", "2\\nValidation Gap", "gate"),
                ("review", "3\\nHOLD / RE_REVIEW", "final"),
                ("repair", "1\\n설정 / 데이터 보강", "compare"),
            ],
            "edges": [
                ("source", "validation", "재검증"),
                ("validation", "review", "보류 판단"),
                ("review", "repair", "원인 해결"),
                ("repair", "source", "다시 실행"),
            ],
        },
    }


def _decision_gate_rows() -> list[dict[str, str]]:
    return [
        {
            "gate": "Backtest Analysis에서 source로 보낼 수 있는가",
            "go": "성과, Data Trust, benchmark, Real-Money signal을 함께 설명할 수 있음",
            "review": "warning은 있지만 원인과 다음 검증 항목을 명시할 수 있음",
            "stop": "실행 실패, source 식별 불가, hard blocker가 원인 화면에서 해결되지 않음",
            "screen": "Backtest Analysis",
        },
        {
            "gate": "Practical Validation을 통과할 수 있는가",
            "go": "BLOCKED가 없고 profile-aware Practical Diagnostics의 REVIEW / NOT_RUN 의미를 설명할 수 있음",
            "review": "NOT_RUN 또는 REVIEW domain이 남아 있지만 Final Review에서 보류 / 재검토 / 선정 판단 근거로 다룰 수 있음",
            "stop": "component 없음, 비중 합계 오류, Data Trust blocked, deployment blocked, 프로필과 충돌하는 큰 leveraged / inverse exposure",
            "screen": "Practical Validation",
        },
        {
            "gate": "Final Review에서 최종 판단을 저장할 수 있는가",
            "go": "Validation, robustness, paper observation 기준이 Ready이고 판단 사유가 있음",
            "review": "선정은 어렵지만 HOLD / RE_REVIEW / REJECT 사유를 남길 수 있음",
            "stop": "선정하려는데 final evidence blocker가 남아 있거나 판단 사유가 비어 있음",
            "screen": "Final Review",
        },
        {
            "gate": "Selected Portfolio Dashboard에서 관찰 대상으로 볼 수 있는가",
            "go": "Final Decision V2가 SELECT_FOR_PRACTICAL_PORTFOLIO이고 active component / 비중 기준이 정상",
            "review": "선정 row는 있지만 drift, blocker, 최신 성과 재확인이 필요",
            "stop": "Final Review 선정 row가 없거나 live approval / order로 오해되는 운영 행위",
            "screen": "Operations > Selected Portfolio Dashboard",
        },
    ]


def _stage_timeline_rows() -> list[dict[str, str]]:
    return [
        {
            "step": "1",
            "phase": "분석",
            "screen": "Backtest Analysis",
            "title": "후보 source 만들기",
            "check": "Single Strategy, Compare, 저장 mix replay에서 성과 / Data Trust / 비중 근거를 확인합니다.",
            "output": "Portfolio Selection Source",
        },
        {
            "step": "2",
            "phase": "실전 검증",
            "screen": "Practical Validation",
            "title": "프로필 기반 실전 진단",
            "check": "검증 프로필과 5개 답변을 기준으로 Input Evidence와 12개 Practical Diagnostics를 분리해서 봅니다.",
            "output": "Practical Validation Result",
        },
        {
            "step": "3",
            "phase": "최종 판단",
            "screen": "Final Review",
            "title": "최종 판단과 사유 기록",
            "check": "Validation, robustness, paper observation 기준을 보고 선정 / 보류 / 거절 / 재검토를 기록합니다.",
            "output": "Final Selection Decision V2",
        },
        {
            "step": "4",
            "phase": "사후 관찰",
            "screen": "Operations > Selected Portfolio Dashboard",
            "title": "선정 row 읽기",
            "check": "Final Review에서 선정된 V2 decision을 read-only로 읽고 drift / recheck signal을 확인합니다.",
            "output": "Selected Portfolio Dashboard",
        },
    ]


def _route_stage_status() -> dict[str, dict[str, str]]:
    return {
        "단일 후보": {
            "1": "필수",
            "2": "필수",
            "3": "필수",
            "4": "선정 후",
        },
        "여러 후보 묶음": {
            "1": "필수",
            "2": "필수",
            "3": "필수",
            "4": "선정 후",
        },
        "저장된 비중 조합": {
            "1": "재실행",
            "2": "필수",
            "3": "필수",
            "4": "선정 후",
        },
        "보류 / 재검토": {
            "1": "점검",
            "2": "보강",
            "3": "보류",
            "4": "대기",
        },
    }


def _route_checkpoint_rows() -> dict[str, list[dict[str, str]]]:
    return {
        "단일 후보": [
            {
                "checkpoint": "단일 전략 결과가 설명 가능한가",
                "detail": "성과, 손실, benchmark, Data Trust를 같은 화면에서 읽고 후보로 볼 이유를 말할 수 있어야 합니다.",
                "screen": "Backtest Analysis > Single Strategy",
            },
            {
                "checkpoint": "Practical Validation source로 저장됐는가",
                "detail": "후보는 Review Note가 아니라 Clean V2 selection source로 넘어가야 다음 검증에서 같은 계약으로 읽힙니다.",
                "screen": "Backtest Analysis > Practical Validation Handoff",
            },
            {
                "checkpoint": "실전 검증 blocker가 없는가",
                "detail": "Practical Validation에서 Input Evidence, asset allocation, concentration, stress coverage, leverage / inverse, cost, sensitivity / overfit 상태를 함께 확인합니다.",
                "screen": "Practical Validation",
            },
            {
                "checkpoint": "최종 판단을 한 번만 남기는가",
                "detail": "선정 / 보류 / 거절 / 재검토와 최종 메모는 Final Review V2 decision에만 남깁니다.",
                "screen": "Final Review",
            },
        ],
        "여러 후보 묶음": [
            {
                "checkpoint": "후보마다 같은 기준으로 검토했는가",
                "detail": "각 후보는 최소한 성과, Data Trust, Real-Money signal, benchmark 기준이 비교 가능해야 합니다.",
                "screen": "Backtest Analysis > Compare",
            },
            {
                "checkpoint": "역할이 겹치지 않는가",
                "detail": "성장, 방어, 현금성, 리밸런싱 보조처럼 mix 안의 역할을 분리해야 합니다.",
                "screen": "Backtest Analysis > Compare Weight Builder",
            },
            {
                "checkpoint": "비중 합계와 이유가 명확한가",
                "detail": "target weight가 100%로 맞고, 각 weight reason이 Practical Validation과 Final Review에서 재사용 가능해야 합니다.",
                "screen": "Practical Validation",
            },
            {
                "checkpoint": "묶음 전체의 risk를 확인했는가",
                "detail": "좋은 후보 여러 개라도 함께 묶었을 때 집중도, 손실, 관찰 기준이 달라질 수 있습니다.",
                "screen": "Final Review",
            },
        ],
        "저장된 비중 조합": [
            {
                "checkpoint": "저장된 mix가 재현되는가",
                "detail": "Saved Portfolio는 workflow 기록이 아니라 weight setup이므로 `Mix 재실행 및 검증` 결과부터 확인합니다.",
                "screen": "Compare & Portfolio Builder > 저장된 비중 조합",
            },
            {
                "checkpoint": "개별 5단계 검증으로 오해하지 않는가",
                "detail": "5단계 Compare 보드는 개별 전략 후보용이고, 저장 mix는 Portfolio Mix 검증 보드에서 판단합니다.",
                "screen": "저장된 비중 조합 > Portfolio Mix 검증 보드",
            },
            {
                "checkpoint": "Practical Validation으로 직접 보내는가",
                "detail": "저장 mix는 개별 current candidate가 아니므로 Candidate Review / legacy Proposal을 필수로 거치지 않습니다.",
                "screen": "저장된 비중 조합",
            },
            {
                "checkpoint": "Final Review에서 V2 검증 결과로 읽히는가",
                "detail": "최종 검토는 Saved Portfolio 원본이 아니라 Practical Validation Result를 기준으로 진행합니다.",
                "screen": "Final Review",
            },
        ],
        "보류 / 재검토": [
            {
                "checkpoint": "막힘 원인이 어느 화면 소유인지 찾았는가",
                "detail": "데이터 문제, Real-Money blocker, 비교 근거 부족, 구성 / 비중 문제를 분리해야 합니다.",
                "screen": "Backtest Analysis / Practical Validation",
            },
            {
                "checkpoint": "Final Review 직행을 멈췄는가",
                "detail": "hold, blocked, insufficient evidence 상태에서는 최종 선정보다 보류나 재검토 기록이 맞습니다.",
                "screen": "Final Review",
            },
            {
                "checkpoint": "되돌아갈 화면이 명확한가",
                "detail": "데이터면 ingestion / 실행 설정, 상대 근거면 Compare, 비중이면 Backtest Analysis의 weight builder로 돌아갑니다.",
                "screen": "해당 원인 화면",
            },
            {
                "checkpoint": "재검토 후 같은 기준으로 다시 읽는가",
                "detail": "수정 후에도 1~4 단계 기준을 바꾸지 않고 같은 통과 기준으로 다시 판단합니다.",
                "screen": "Portfolio Flow",
            },
        ],
    }


def _concept_rows() -> list[dict[str, str]]:
    return [
        {
            "개념": "Real-Money",
            "제품 안에서의 의미": "개별 backtest 결과에 붙는 실전 검토 신호",
            "사용자가 볼 곳": "Backtest Analysis 결과",
        },
        {
            "개념": "Backtest Analysis",
            "제품 안에서의 의미": "Single Strategy, Compare, 저장 mix replay로 후보 source를 만드는 1단계",
            "사용자가 볼 곳": "Backtest > Backtest Analysis",
        },
        {
            "개념": "Practical Validation",
            "제품 안에서의 의미": "선택된 source의 구성, 비중, Data Trust, blocker를 확인하는 2단계",
            "사용자가 볼 곳": "Backtest > Practical Validation",
        },
        {
            "개념": "Final Review",
            "제품 안에서의 의미": "선정 / 보류 / 거절 / 재검토와 최종 사유를 기록하는 마지막 판단 화면",
            "사용자가 볼 곳": "Backtest > Final Review",
        },
        {
            "개념": "Selected Portfolio Dashboard",
            "제품 안에서의 의미": "Final Review V2에서 선정된 포트폴리오를 읽어보는 read-only 운영 화면",
            "사용자가 볼 곳": "Operations > Selected Portfolio Dashboard",
        },
        {
            "개념": "Legacy Candidate / Proposal",
            "제품 안에서의 의미": "기존 JSONL과 화면을 읽기 위한 호환 경로. 새 main flow의 필수 단계는 아닙니다.",
            "사용자가 볼 곳": "Backtest legacy compatibility surfaces",
        },
    ]


def _storage_rows() -> list[dict[str, str]]:
    return [
        {
            "기록": "Portfolio Selection Source",
            "담는 내용": "Backtest Analysis에서 선택한 단일 / 비교 / mix 후보 source",
            "생성 화면": "Backtest Analysis",
        },
        {
            "기록": "Practical Validation Result",
            "담는 내용": "구성, 비중, Data Trust, blocker, paper observation preview",
            "생성 화면": "Practical Validation",
        },
        {
            "기록": "Saved Portfolio",
            "담는 내용": "Compare에서 저장한 재사용 weight setup",
            "생성 화면": "Compare & Portfolio Builder",
        },
        {
            "기록": "Final Selection Decision V2",
            "담는 내용": "선정 / 보류 / 거절 / 재검토 최종 판단. Dashboard는 이 기록을 읽기만 합니다.",
            "생성 화면": "Final Review",
        },
        {
            "기록": "Legacy Candidate / Proposal Registries",
            "담는 내용": "기존 Candidate Review, Pre-Live, Portfolio Proposal, Paper Ledger, Final Decision V1 기록",
            "생성 화면": "Legacy compatibility",
        },
    ]


def _document_reference_rows() -> list[dict[str, str]]:
    return [
        {
            "상황": "현재 finance 전체 구조를 잡고 싶을 때",
            "문서": ".note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md",
            "역할": "finance package의 현재 제품 표면, data / strategy / review layer 요약",
        },
        {
            "상황": "과거 walkthrough 실습 맥락을 참고할 때",
            "문서": ".note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md",
            "역할": "초기 1~11 실습 세션의 질문 / 후보 예시 / Guide 보조 기능 기록",
        },
        {
            "상황": "Backtest 화면이 어떤 순서로 동작하는지 볼 때",
            "문서": ".note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md",
            "역할": "Backtest Analysis / Practical Validation / Final Review V2 UI 흐름",
        },
        {
            "상황": "legacy 포트폴리오 초안 저장소를 이해할 때",
            "문서": ".note/finance/operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md",
            "역할": "기존 portfolio proposal draft가 무엇이고 Clean V2와 어떻게 구분되는지 설명",
        },
        {
            "상황": "과거 paper tracking ledger 기록을 해석할 때",
            "문서": ".note/finance/operations/PAPER_PORTFOLIO_TRACKING_LEDGER_GUIDE.md",
            "역할": "Phase33 ledger의 호환성 / 관찰 기록 의미 설명",
        },
        {
            "상황": "최종 판단 기록을 확인할 때",
            "문서": ".note/finance/operations/FINAL_PORTFOLIO_SELECTION_DECISIONS_GUIDE.md",
            "역할": "Final Review에서 저장한 선정 / 보류 / 거절 / 재검토 판단 기록 사용법. 현재 dashboard는 V2 decision을 우선 읽습니다.",
        },
        {
            "상황": "최종 선정 포트폴리오 운영 대시보드를 확인할 때",
            "문서": ".note/finance/phases/phase36/PHASE36_FINAL_SELECTED_PORTFOLIO_MONITORING_AND_REBALANCE_OPERATIONS_PLAN.md",
            "역할": "Operations > Selected Portfolio Dashboard가 Final Review selected row를 read-only로 읽는 방식 설명",
        },
        {
            "상황": "용어가 헷갈릴 때",
            "문서": ".note/finance/FINANCE_TERM_GLOSSARY.md",
            "역할": "Real-Money, Pre-Live, Candidate Registry 같은 반복 용어 설명",
        },
        {
            "상황": "프로젝트의 큰 phase 위치를 확인할 때",
            "문서": ".note/finance/MASTER_PHASE_ROADMAP.md",
            "역할": "전체 phase 흐름, 현재 방향, 이후 작업 축",
        },
        {
            "상황": "최신 문서 목록을 훑고 싶을 때",
            "문서": ".note/finance/FINANCE_DOC_INDEX.md",
            "역할": "finance 문서의 상위 index",
        },
    ]


def _registry_detail_rows() -> list[dict[str, str]]:
    return [
        {
            "흐름 단계": "1단계 Backtest Analysis",
            "파일": "PORTFOLIO_SELECTION_SOURCES.jsonl",
            "담는 데이터": "단일 전략, Compare 후보, 저장 mix replay를 Clean V2 source로 변환한 기록",
            "화면 위치": "Backtest > Backtest Analysis",
            "읽는 법": "실전 후보 검증의 입력 source입니다. live approval이나 주문 지시가 아닙니다.",
        },
        {
            "흐름 단계": "2단계 Practical Validation",
            "파일": "PRACTICAL_VALIDATION_RESULTS.jsonl",
            "담는 데이터": "구성 / 비중 / Data Trust / blocker / robustness preview / paper observation preview",
            "화면 위치": "Backtest > Practical Validation",
            "읽는 법": "Final Review V2가 우선 읽는 검증 결과입니다.",
        },
        {
            "흐름 단계": "3단계 Final Review",
            "파일": "FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl",
            "담는 데이터": "선정 / 보류 / 거절 / 재검토 최종 판단, operator reason, inline paper observation",
            "화면 위치": "Backtest > Final Review / Operations > Selected Portfolio Dashboard",
            "읽는 법": "Selected Portfolio Dashboard의 source-of-truth입니다.",
        },
        {
            "흐름 단계": "4단계 사후 관찰",
            "파일": "SELECTED_PORTFOLIO_MONITORING_LOG.jsonl",
            "담는 데이터": "선정 이후 별도 monitoring snapshot을 저장할 때 쓰는 Clean V2 보조 ledger",
            "화면 위치": "Operations > Selected Portfolio Dashboard",
            "읽는 법": "현재 dashboard의 필수 입력은 아니며, selected row 관찰 보조 기록입니다.",
        },
        {
            "흐름 단계": "Legacy compatibility",
            "파일": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
            "담는 데이터": "기존 Final Review V1 판단 기록",
            "화면 위치": "Backtest legacy compatibility",
            "읽는 법": "새 dashboard source-of-truth는 V2 파일입니다. V1은 과거 기록 해석용입니다.",
        },
    ]


def _runtime_artifact_rows() -> list[dict[str, str]]:
    return [
        {
            "파일": "BACKTEST_RUN_HISTORY.jsonl",
            "폴더": ".note/finance/run_history/",
            "담는 데이터": "Backtest 실행 payload, 결과 요약, replay에 필요한 실행 기록",
            "화면 위치": "Operations > Backtest Run History",
        },
        {
            "파일": "WEB_APP_RUN_HISTORY.jsonl",
            "폴더": ".note/finance/run_history/",
            "담는 데이터": "웹 앱 로컬 실행 / 운영 로그 성격의 runtime artifact",
            "화면 위치": "로컬 운영 보조 기록",
        },
        {
            "파일": "SAVED_PORTFOLIOS.jsonl",
            "폴더": ".note/finance/saved/",
            "담는 데이터": "Compare에서 만든 재사용 가능한 portfolio mix setup",
            "화면 위치": "Backtest > Compare & Portfolio Builder > 저장된 비중 조합",
        },
    ]


def _reference_path_lines() -> list[str]:
    return [
        ".note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md",
        ".note/finance/FINANCE_DOC_INDEX.md",
        ".note/finance/MASTER_PHASE_ROADMAP.md",
        ".note/finance/FINANCE_TERM_GLOSSARY.md",
        ".note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md",
        ".note/finance/operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md",
        ".note/finance/operations/PAPER_PORTFOLIO_TRACKING_LEDGER_GUIDE.md",
        ".note/finance/operations/FINAL_PORTFOLIO_SELECTION_DECISIONS_GUIDE.md",
        ".note/finance/phases/phase36/PHASE36_FINAL_SELECTED_PORTFOLIO_MONITORING_AND_REBALANCE_OPERATIONS_PLAN.md",
        ".note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md",
        ".note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl",
        ".note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl",
        ".note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl",
        ".note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl",
        ".note/finance/saved/SAVED_PORTFOLIO_MIXES.jsonl",
        ".note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl",
        ".note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl",
        ".note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
        ".note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
        ".note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl",
        ".note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
        ".note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl",
        ".note/finance/run_history/WEB_APP_RUN_HISTORY.jsonl",
        ".note/finance/saved/SAVED_PORTFOLIOS.jsonl",
        ".note/finance/WORK_PROGRESS.md",
        ".note/finance/QUESTION_AND_ANALYSIS_LOG.md",
    ]


def _detail_step_rows() -> list[dict[str, str]]:
    return [
        {
            "단계": row["step"],
            "화면": row["screen"],
            "목적": row["title"],
            "확인할 것": row["check"],
        }
        for row in _stage_timeline_rows()
    ]


def _render_page_style() -> None:
    st.html(
        """
        <style>
          .qg-hero {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            padding: 1.1rem 1.2rem;
            background: linear-gradient(135deg, #f8fafc 0%, #eef4f8 100%);
            margin: 0.25rem 0 1rem;
          }
          .qg-hero-label {
            color: #4b5563;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
          }
          .qg-hero-title {
            color: #111827;
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 0.35rem;
          }
          .qg-hero-copy {
            color: #374151;
            font-size: 0.98rem;
            line-height: 1.55;
            max-width: 920px;
          }
          .qg-status-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.85rem;
          }
          .qg-chip {
            border: 1px solid #cbd5e1;
            border-radius: 999px;
            background: #ffffff;
            color: #334155;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 0.28rem 0.62rem;
          }
          .qg-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 0.7rem;
            margin: 0.7rem 0 1rem;
          }
          .qg-card {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            background: #ffffff;
            padding: 0.85rem;
          }
          .qg-card-kicker {
            color: #64748b;
            font-size: 0.76rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
          }
          .qg-card-title {
            color: #111827;
            font-size: 1rem;
            font-weight: 800;
            line-height: 1.35;
            margin-bottom: 0.3rem;
          }
          .qg-card-copy {
            color: #374151;
            font-size: 0.86rem;
            line-height: 1.45;
          }
          .qg-route-summary {
            border-left: 4px solid #2f6f9f;
            padding: 0.2rem 0 0.2rem 0.8rem;
            margin: 0.2rem 0 0.8rem;
          }
          .qg-route-summary strong {
            display: block;
            color: #111827;
            font-size: 1.05rem;
            margin-bottom: 0.15rem;
          }
          .qg-route-summary span {
            color: #4b5563;
            font-size: 0.9rem;
            line-height: 1.45;
          }
          .qg-check-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.7rem;
            margin: 0.45rem 0 1rem;
          }
          .qg-check-card {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            background: #ffffff;
            padding: 0.85rem;
          }
          .qg-check-screen {
            color: #64748b;
            font-size: 0.74rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
          }
          .qg-check-title {
            color: #111827;
            font-size: 0.95rem;
            font-weight: 800;
            line-height: 1.35;
            margin-bottom: 0.3rem;
          }
          .qg-check-detail {
            color: #374151;
            font-size: 0.84rem;
            line-height: 1.45;
          }
          .qg-timeline {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
            gap: 0.65rem;
            margin: 0.55rem 0 1.05rem;
          }
          .qg-stage-card {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            background: #ffffff;
            padding: 0.78rem;
            min-height: 190px;
          }
          .qg-stage-card.qg-stage-muted {
            background: #f8fafc;
          }
          .qg-stage-card.qg-stage-skip {
            background: #f8fafc;
            color: #64748b;
          }
          .qg-stage-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.45rem;
            margin-bottom: 0.48rem;
          }
          .qg-stage-num {
            width: 1.9rem;
            height: 1.9rem;
            border-radius: 999px;
            background: #2f6f9f;
            color: #ffffff;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.84rem;
            font-weight: 800;
            flex: 0 0 auto;
          }
          .qg-stage-pill {
            border: 1px solid #cbd5e1;
            border-radius: 999px;
            background: #ffffff;
            color: #334155;
            font-size: 0.7rem;
            font-weight: 800;
            padding: 0.18rem 0.42rem;
            white-space: nowrap;
          }
          .qg-stage-pill.required {
            border-color: #8fc5a3;
            color: #246746;
            background: #effaf3;
          }
          .qg-stage-pill.active {
            border-color: #8bb9d8;
            color: #2f6f9f;
            background: #eef7fc;
          }
          .qg-stage-pill.warn {
            border-color: #e5c36a;
            color: #835b16;
            background: #fff8e7;
          }
          .qg-stage-pill.muted {
            border-color: #cbd5e1;
            color: #64748b;
            background: #f8fafc;
          }
          .qg-stage-phase {
            color: #64748b;
            font-size: 0.72rem;
            font-weight: 800;
            margin-bottom: 0.16rem;
          }
          .qg-stage-title {
            color: #111827;
            font-size: 0.94rem;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 0.26rem;
          }
          .qg-stage-screen {
            color: #2f6f9f;
            font-size: 0.78rem;
            font-weight: 800;
            margin-bottom: 0.36rem;
          }
          .qg-stage-copy {
            color: #374151;
            font-size: 0.8rem;
            line-height: 1.42;
          }
          .qg-stage-output {
            border-top: 1px solid #e5e7eb;
            color: #64748b;
            font-size: 0.76rem;
            font-weight: 700;
            margin-top: 0.55rem;
            padding-top: 0.45rem;
          }
        </style>
        """
    )


def _render_hero(runtime_marker: str | None, git_sha: str | None) -> None:
    runtime_text = escape(runtime_marker or "-")
    git_text = escape(git_sha or "-")
    st.html(
        f"""
        <section class="qg-hero">
          <div class="qg-hero-label">Portfolio Selection Guide</div>
          <div class="qg-hero-title">실전 후보 포트폴리오를 찾는 운영 가이드</div>
          <div class="qg-hero-copy">
            이 화면은 문서 목록이 아니라 의사결정 안내입니다. 먼저 현재 진행 상황을 고르고,
            그 경로에서 어떤 화면을 지나고 어느 조건에서 멈춰야 하는지 확인합니다.
          </div>
          <div class="qg-status-strip">
            <span class="qg-chip">Current workflow: Backtest Analysis -> Practical Validation -> Final Review</span>
            <span class="qg-chip">Operations follow-up: Selected Portfolio Dashboard</span>
            <span class="qg-chip">Runtime {runtime_text}</span>
            <span class="qg-chip">Git {git_text}</span>
          </div>
        </section>
        """
    )


def _render_orientation_cards(selected_route: str, route: dict[str, Any]) -> None:
    rows = [
        ("선택한 목표", route["headline"], route["goal"]),
        ("진행 순서", "어떤 화면을 어떤 순서로 지나는가", route["sequence"]),
        ("건너뛰거나 조심할 단계", "단계 ownership 확인", route["caution"]),
        ("생성 / 참조 기록", route["records"], "저장소는 서로 덮어쓰지 않고 단계별 판단을 따로 남깁니다."),
    ]
    st.markdown("### 선택한 경로 요약")
    st.caption("아래 요약은 선택한 진행 상황이 어떤 화면을 지나고, 어떤 기록을 만들거나 읽는지 먼저 보여줍니다.")
    card_html = []
    for kicker, title, copy in rows:
        card_html.append(
            f"""
            <div class="qg-card">
              <div class="qg-card-kicker">{escape(kicker)}</div>
              <div class="qg-card-title">{escape(title)}</div>
              <div class="qg-card-copy">{escape(copy)}</div>
            </div>
            """
        )
    st.html(f'<div class="qg-card-grid">{"".join(card_html)}</div>')

    st.caption(
        f"`{selected_route}` 기준으로 보고 있습니다. 다른 상황이면 위 선택 버튼에서 경로를 바꿔 확인합니다."
    )


def _dot_for_route(route: dict[str, Any]) -> str:
    palette = {
        "run": ("#e8f1f8", "#2f6f9f"),
        "gate": ("#fff7df", "#9a6a1d"),
        "compare": ("#edf7ed", "#4f7c45"),
        "candidate": ("#eaf6ef", "#2f7d57"),
        "proposal": ("#f7f0e3", "#9a6a1d"),
        "final": ("#eef0f6", "#5f6477"),
        "stop": ("#fff1e6", "#b45309"),
    }
    lines = [
        "digraph G {",
        "  graph [rankdir=LR, bgcolor=\"transparent\", pad=\"0.2\", nodesep=\"0.45\", ranksep=\"0.75\", splines=ortho];",
        "  node [shape=rect, style=\"rounded,filled\", fontname=\"Arial\", fontsize=12, margin=\"0.16,0.10\", penwidth=1.7];",
        "  edge [fontname=\"Arial\", fontsize=10, color=\"#64748b\", fontcolor=\"#475569\", arrowsize=0.7, penwidth=1.5];",
    ]
    for node_id, label, tone in route["dot"]:
        fill, border = palette.get(tone, palette["run"])
        shape = "diamond" if tone in {"gate", "stop"} else "rect"
        lines.append(
            f'  {node_id} [label="{label}", fillcolor="{fill}", color="{border}", shape={shape}];'
        )
    for src, dst, label in route["edges"]:
        lines.append(f'  {src} -> {dst} [label="{label}"];')
    lines.append("}")
    return "\n".join(lines)


def _render_css_flow_fallback(route: dict[str, Any]) -> None:
    cards = []
    for index, (node_id, label, tone) in enumerate(route["dot"]):
        del node_id
        step_label = escape(label.replace("\\n", " / "))
        cards.append(
            f'<span class="qg-chip">{step_label}</span>'
        )
        if index < len(route["dot"]) - 1:
            cards.append('<span class="qg-chip">-&gt;</span>')
    st.html(f'<div class="qg-status-strip">{"".join(cards)}</div>')


def _render_flow_visual(selected_route: str, route: dict[str, Any]) -> None:
    st.markdown("### Portfolio Flow")
    st.html(
        f"""
        <div class="qg-route-summary">
          <strong>{escape(route["headline"])}</strong>
          <span>{escape(route["summary"])}</span>
        </div>
        """
    )
    try:
        st.graphviz_chart(_dot_for_route(route), width="stretch", height=360)
    except Exception:
        _render_css_flow_fallback(route)
        st.caption("현재 환경에서 GraphViz 렌더링을 사용할 수 없어 compact visual fallback으로 표시했습니다.")
    st.caption(
        f"`{selected_route}` flow는 live approval이나 주문 지시가 아니라, Final Review에 도달하기 전의 검토 경로입니다."
    )


def _status_pill_tone(status: str) -> str:
    if status in {"필수", "핵심"}:
        return "required"
    if status in {"권장", "반복", "직행", "복귀", "보강", "재실행", "선정 후"}:
        return "active"
    if status in {"선행", "점검", "보류", "대기"}:
        return "warn"
    return "muted"


def _render_route_checkpoints(selected_route: str) -> None:
    st.markdown(f"### {selected_route} 핵심 체크포인트")
    st.caption(
        "전체 1~4 단계 중 이 진행 상황에서 특히 놓치면 안 되는 판단 지점만 모아 보여줍니다."
    )
    checkpoint_cards = []
    for row in _route_checkpoint_rows()[selected_route]:
        checkpoint_cards.append(
            f"""
            <div class="qg-check-card">
              <div class="qg-check-screen">{escape(row["screen"])}</div>
              <div class="qg-check-title">{escape(row["checkpoint"])}</div>
              <div class="qg-check-detail">{escape(row["detail"])}</div>
            </div>
            """
        )
    st.html(f'<div class="qg-check-grid">{"".join(checkpoint_cards)}</div>')


def _render_stage_timeline(selected_route: str) -> None:
    st.markdown("### 전체 1~4 단계에서 현재 위치")
    st.caption(
        f"`{selected_route}` 기준으로 전체 workflow의 어느 단계를 지나고, 무엇을 반복하거나 생략하는지 먼저 확인합니다."
    )
    status_by_step = _route_stage_status()[selected_route]
    cards = []
    for row in _stage_timeline_rows():
        status = status_by_step.get(row["step"], "조건부")
        tone = _status_pill_tone(status)
        card_tone = "qg-stage-skip" if status == "생략" else ("qg-stage-muted" if tone in {"warn", "muted"} else "")
        cards.append(
            f"""
            <div class="qg-stage-card {card_tone}">
              <div class="qg-stage-head">
                <span class="qg-stage-num">{escape(row["step"])}</span>
                <span class="qg-stage-pill {tone}">{escape(status)}</span>
              </div>
              <div class="qg-stage-phase">{escape(row["phase"])}</div>
              <div class="qg-stage-title">{escape(row["title"])}</div>
              <div class="qg-stage-screen">{escape(row["screen"])}</div>
              <div class="qg-stage-copy">{escape(row["check"])}</div>
              <div class="qg-stage-output">산출물: {escape(row["output"])}</div>
            </div>
            """
        )
    st.html(f'<div class="qg-timeline">{"".join(cards)}</div>')

    with st.expander("단계 상태 라벨 읽는 법", expanded=False):
        st.markdown(
            """
            - `필수`: 이 경로에서 통과 기준으로 반드시 확인합니다.
            - `반복`: 여러 후보를 만들기 위해 같은 판단을 후보별로 반복합니다.
            - `직행`: 별도 proposal draft 저장 없이 다음 검토 화면에서 직접 읽습니다.
            - `재실행`: 저장된 setup을 현재 데이터 / 설정으로 다시 열어 검증합니다.
            - `선정 후`: Final Review에서 선정된 row가 있을 때 읽습니다.
            - `선행`: saved mix가 만들어지기 전 이미 지나간 단계로 봅니다.
            - `생략`: 이 경로에서는 일부러 건너뛰는 단계입니다.
            - `보류 / 대기`: 막힘을 해결하기 전에는 최종 선정으로 해석하지 않습니다.
            """
        )


def _render_decision_gates() -> None:
    st.markdown("### Decision Gates")
    st.caption("단계 번호보다 사용자가 실제로 묻는 질문을 기준으로 Go / Review / Stop을 구분합니다.")
    rows = _decision_gate_rows()
    for row in rows:
        with st.container(border=True):
            st.markdown(f"#### {row['gate']}")
            cols = st.columns(3)
            cols[0].success(f"Go: {row['go']}")
            cols[1].warning(f"Review: {row['review']}")
            cols[2].error(f"Stop: {row['stop']}")
            st.caption(f"확인 위치: {row['screen']}")


def _render_reference_drawer() -> None:
    st.markdown("### Reference Drawer")
    st.caption("상세 설명, 저장소 의미, 운영 경계는 필요할 때만 펼쳐 확인합니다.")
    tabs = st.tabs(["핵심 개념", "상세 단계", "기록 저장소", "운영 경계", "문서 / 경로"])
    with tabs[0]:
        st.dataframe(pd.DataFrame(_concept_rows()), width="stretch", hide_index=True)
    with tabs[1]:
        st.dataframe(pd.DataFrame(_detail_step_rows()), width="stretch", hide_index=True)
        with st.expander("1~4단계 전체를 어떻게 읽나", expanded=False):
            st.markdown(
                """
                - `1`: Backtest Analysis에서 단일 / Compare / 저장 mix 후보 source를 만든다.
                - `2`: Practical Validation에서 검증 프로필, Input Evidence, 12개 Practical Diagnostics를 확인한다.
                - `3`: Final Review에서 최종 판단과 이유를 V2 decision으로 남긴다.
                - `4`: Selected Portfolio Dashboard에서 선정 row를 read-only로 관찰한다.
                """
            )
    with tabs[2]:
        st.dataframe(pd.DataFrame(_storage_rows()), width="stretch", hide_index=True)
        st.info(
            "Saved Portfolio는 재사용 setup이고, Clean V2 source는 검증 입력입니다. "
            "저장된 비중 조합은 Candidate Review나 legacy Proposal을 필수로 거치지 않고 Practical Validation으로 연결합니다. "
            "Selected Portfolio Dashboard는 새 저장소가 아니라 Final Selection Decision V2를 읽는 운영 화면입니다."
        )
    with tabs[3]:
        st.warning(
            "`SELECT_FOR_PRACTICAL_PORTFOLIO`는 실전 후보 선정 신호이지 live approval, broker order, 자동매매 지시가 아닙니다."
        )
        st.markdown(
            """
            - `Real-Money`는 검증 신호입니다.
            - `Backtest Analysis`는 후보 source를 만드는 1단계입니다.
            - `Practical Validation`은 source를 profile-aware practical diagnostics 결과로 구조화하는 2단계입니다.
            - `Final Review`는 현재 workflow의 마지막 판단 기록입니다.
            - `Selected Portfolio Dashboard`는 Final Review V2 selected row를 Operations에서 다시 읽는 화면입니다.
            - `Candidate Review / Portfolio Proposal`은 기존 기록을 읽기 위한 legacy compatibility 경로입니다.
            - `Live Approval / Order`는 현재 제품 범위 밖입니다.
            """
        )
    with tabs[4]:
        st.dataframe(pd.DataFrame(_document_reference_rows()), width="stretch", hide_index=True)
        with st.expander("JSONL 저장소와 전체 경로", expanded=False):
            st.markdown("#### 후보 검토 JSONL")
            st.dataframe(pd.DataFrame(_registry_detail_rows()), width="stretch", hide_index=True)
            st.markdown("#### 실행 / 재사용 JSONL")
            st.dataframe(pd.DataFrame(_runtime_artifact_rows()), width="stretch", hide_index=True)
            st.code("\n".join(_reference_path_lines()), language="text")


def _render_runtime_reference(
    loaded_at: datetime | None,
    render_runtime_snapshot: Callable[[], None] | None,
) -> None:
    with st.expander("System status", expanded=False):
        if render_runtime_snapshot is not None:
            render_runtime_snapshot()
            return
        if loaded_at is not None:
            st.caption(f"Loaded at: {loaded_at:%Y-%m-%d %H:%M:%S}")


def render_reference_guides_page(
    *,
    runtime_marker: str | None = None,
    loaded_at: datetime | None = None,
    git_sha: str | None = None,
    render_runtime_snapshot: Callable[[], None] | None = None,
) -> None:
    """Render the product-facing reference guide for portfolio selection workflows."""

    _render_page_style()
    st.title("Guides")
    st.caption("포트폴리오 후보 선정 흐름을 빠르게 고르고, 다음 화면과 멈춤 기준을 확인하는 안내 화면입니다.")
    _render_hero(runtime_marker, git_sha)

    routes = _route_cards()
    state_key = "reference_guides_primary_route"
    if st.session_state.get(state_key) not in GUIDE_ROUTE_OPTIONS:
        st.session_state[state_key] = GUIDE_ROUTE_OPTIONS[0]

    if hasattr(st, "segmented_control"):
        st.segmented_control(
            "현재 진행 상황 선택",
            options=GUIDE_ROUTE_OPTIONS,
            selection_mode="single",
            required=True,
            key=state_key,
            width="stretch",
        )
        selected_route = str(st.session_state.get(state_key) or GUIDE_ROUTE_OPTIONS[0])
    else:
        selected_route = st.radio(
            "현재 진행 상황 선택",
            options=GUIDE_ROUTE_OPTIONS,
            horizontal=True,
            key=state_key,
        )

    route = routes[selected_route]
    _render_stage_timeline(selected_route)
    _render_orientation_cards(selected_route, route)
    _render_flow_visual(selected_route, route)
    _render_route_checkpoints(selected_route)
    _render_decision_gates()
    _render_reference_drawer()
    _render_runtime_reference(loaded_at, render_runtime_snapshot)
