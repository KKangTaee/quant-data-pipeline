from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from html import escape
from textwrap import dedent
from typing import Any

import pandas as pd
import streamlit as st

from app.services.reference_guides_catalog import get_reference_center_catalog


GUIDE_ROUTE_OPTIONS = [
    "단일 후보",
    "여러 후보 묶음",
    "저장된 Mix",
    "보류 / 재검토",
]

REFERENCE_VIEW_OPTIONS = [
    "Reference Center",
    "Portfolio Selection Journey",
]


def _route_cards() -> dict[str, dict[str, Any]]:
    return {
        "단일 후보": {
            "headline": "전략 하나를 끝까지 검토",
            "summary": "후보 1개를 current selection source로 저장하고 Practical Validation을 거쳐 Final Review가 직접 읽는 경로입니다.",
            "goal": "후보 1개를 Practical Validation 결과로 만든 뒤 Final Review에서 모니터링 후보 여부를 판단합니다.",
            "sequence": "Backtest Analysis -> Practical Validation -> Final Review",
            "caution": "Review Note / Pre-Live / Proposal 저장은 더 이상 필수 경로가 아닙니다.",
            "records": "Portfolio Selection Source, Practical Validation Result, Final Decision",
            "dot": [
                ("analysis", "1\\nBacktest Analysis", "run"),
                ("validation", "2\\nPractical Validation", "gate"),
                ("final", "3\\nFinal Review", "final"),
                ("dashboard", "4\\nPortfolio Monitoring", "compare"),
            ],
            "edges": [
                ("analysis", "validation", "selection source"),
                ("validation", "final", "validation result"),
                ("final", "dashboard", "selected decision"),
            ],
        },
        "여러 후보 묶음": {
            "headline": "여러 후보를 하나의 portfolio source로 묶기",
            "summary": "Portfolio Mix Builder에서 여러 component를 실행하고 target weight가 있는 하나의 current selection source로 저장하는 경로입니다.",
            "goal": "여러 전략의 역할과 target weight를 Backtest Analysis에서 정한 뒤 mix 후보로 Practical Validation에 보냅니다.",
            "sequence": "Backtest Analysis Portfolio Mix Builder -> Practical Validation -> Final Review",
            "caution": "Portfolio Proposal의 legacy weight builder는 compatibility 경로입니다. 새 조합 실험은 Backtest Analysis가 맡습니다.",
            "records": "Portfolio Selection Source, Practical Validation Result, Final Decision",
            "dot": [
                ("compare", "1A\\nComponents", "compare"),
                ("weights", "1B\\nMix Weight", "proposal"),
                ("validation", "2\\nPractical Validation", "gate"),
                ("final", "3\\nFinal Review", "final"),
                ("dashboard", "4\\nPortfolio Monitoring", "compare"),
            ],
            "edges": [
                ("compare", "weights", "비중 구성"),
                ("weights", "validation", "current selection source"),
                ("validation", "final", "검증 결과"),
                ("final", "dashboard", "모니터링 후보 row"),
            ],
        },
        "저장된 Mix": {
            "headline": "이미 저장된 weight setup을 workflow 기록으로 연결",
            "summary": "Portfolio Mix Builder에서 저장한 mix를 재실행한 뒤 Practical Validation source로 연결합니다.",
            "goal": "Saved Portfolio에 저장된 재사용 weight setup을 다시 검토해 current selection source로 연결합니다.",
            "sequence": "저장된 Mix 선택 -> Mix 재실행 및 검증 -> Practical Validation -> Final Review",
            "caution": "Saved Portfolio는 후보 registry가 아닙니다. Candidate Review / legacy Proposal 저장을 필수로 거치지 않습니다.",
            "records": "Saved Portfolio, Portfolio Selection Source, Practical Validation Result, Final Decision",
            "dot": [
                ("saved", "1A\\nSaved Weight Setup", "compare"),
                ("replay", "1B\\nMix Replay", "gate"),
                ("validation", "2\\nPractical Validation", "gate"),
                ("final", "3\\nFinal Review", "final"),
                ("dashboard", "4\\nPortfolio Monitoring", "compare"),
            ],
            "edges": [
                ("saved", "replay", "replay"),
                ("replay", "validation", "current selection source"),
                ("validation", "final", "검증 결과"),
                ("final", "dashboard", "모니터링 후보 row"),
            ],
        },
        "보류 / 재검토": {
            "headline": "멈춰야 할 이유를 원인 화면으로 되돌림",
            "summary": "hold, blocked, evidence 부족, re-review가 나오면 Final Review 직행이 아니라 원인 화면으로 돌아갑니다.",
            "goal": "진행이 막혔을 때 모니터링 후보 선정으로 밀고 가지 않고 원인 화면으로 돌아갑니다.",
            "sequence": "막힘 원인 확인 -> 소유 화면으로 복귀 -> 데이터 / 근거 / 구성 보강 -> 같은 기준으로 재검토",
            "caution": "hold, blocked, evidence 부족 상태는 모니터링 후보 선정이 아니라 보류 또는 재검토로 남깁니다.",
            "records": "Practical Validation Result 또는 Final Decision에 보류 / 재검토 사유 기록",
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
            "go": "성과, Data Trust, benchmark, promotion policy signal을 함께 설명할 수 있음",
            "review": "warning은 있지만 원인과 다음 검증 항목을 명시할 수 있음",
            "stop": "실행 실패, source 식별 불가, hard blocker가 원인 화면에서 해결되지 않음",
            "screen": "Backtest Analysis",
        },
        {
            "gate": "Practical Validation을 통과할 수 있는가",
            "go": "BLOCKED가 없고 profile-aware Practical Diagnostics의 REVIEW / NOT_RUN 의미를 설명할 수 있음",
            "review": "NOT_RUN 또는 REVIEW domain이 남아 있지만 Final Review에서 보강 필요 상태와 모니터링 후보 가능 여부의 근거로 다룰 수 있음",
            "stop": "component 없음, 비중 합계 오류, Data Trust blocked, deployment blocked, 프로필과 충돌하는 큰 leveraged / inverse exposure",
            "screen": "Practical Validation",
        },
        {
            "gate": "Final Review에서 모니터링 후보 저장을 할 수 있는가",
            "go": "Validation, robustness, paper observation 기준이 Ready이고 판단 사유가 있음",
            "review": "모니터링 후보 선정은 어렵고 보강 필요 상태로 확인됨",
            "stop": "모니터링 후보로 저장하려는데 final evidence blocker가 남아 있거나 판단 사유가 비어 있음",
            "screen": "Final Review",
        },
        {
            "gate": "Portfolio Monitoring에서 관찰 대상으로 볼 수 있는가",
            "go": "Final Decision이 SELECT_FOR_PRACTICAL_PORTFOLIO이고 active component / 비중 기준이 정상",
            "review": "모니터링 후보 row는 있지만 drift, blocker, 최신 성과 재확인이 필요",
            "stop": "Final Review 모니터링 후보 row가 없거나 live approval / order로 오해되는 운영 행위",
            "screen": "Operations > Portfolio Monitoring",
        },
    ]


def _stage_timeline_rows() -> list[dict[str, str]]:
    return [
        {
            "step": "1",
            "phase": "분석",
            "screen": "Backtest Analysis",
            "title": "후보 source 만들기",
            "check": "Single Strategy, Portfolio Mix Builder, 저장 mix replay에서 성과 / Data Trust / 비중 근거를 확인합니다.",
            "output": "Portfolio Selection Source",
        },
        {
            "step": "2",
            "phase": "검증 근거",
            "screen": "Practical Validation",
            "title": "프로필 기반 검증 근거 진단",
            "check": "검증 프로필과 5개 답변을 기준으로 Input Evidence와 12개 Practical Diagnostics를 분리해서 봅니다.",
            "output": "Practical Validation Result",
        },
        {
            "step": "3",
            "phase": "최종 판단",
            "screen": "Final Review",
            "title": "모니터링 후보 저장",
            "check": "Validation, robustness, paper observation 기준을 보고 selected-route gate까지 통과한 후보만 모니터링 후보로 저장합니다.",
            "output": "Final Selection Decision",
        },
        {
            "step": "4",
            "phase": "사후 관찰",
            "screen": "Operations > Portfolio Monitoring",
            "title": "모니터링 후보 row 읽기",
            "check": "Final Review에서 저장된 current decision을 read-only로 읽고 drift / recheck signal을 확인합니다.",
            "output": "Portfolio Monitoring",
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
        "저장된 Mix": {
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
                "detail": "후보는 Review Note가 아니라 current selection source로 넘어가야 다음 검증에서 같은 계약으로 읽힙니다.",
                "screen": "Backtest Analysis > Practical Validation Handoff",
            },
            {
                "checkpoint": "검증 근거 blocker가 없는가",
                "detail": "Practical Validation에서 Input Evidence, asset allocation, concentration, stress coverage, leverage / inverse, cost, sensitivity / overfit 상태를 함께 확인합니다.",
                "screen": "Practical Validation",
            },
            {
                "checkpoint": "최종 판단을 한 번만 남기는가",
                "detail": "모니터링 후보 저장과 최종 메모는 Final Review decision에만 남깁니다. 보류 / 거절 / 재검토는 상태 안내입니다.",
                "screen": "Final Review",
            },
        ],
        "여러 후보 묶음": [
            {
                "checkpoint": "후보마다 같은 기준으로 검토했는가",
                "detail": "각 component는 최소한 성과, Data Trust, promotion policy signal, benchmark 기준을 확인할 수 있어야 합니다.",
                "screen": "Backtest Analysis > Portfolio Mix Builder",
            },
            {
                "checkpoint": "역할이 겹치지 않는가",
                "detail": "성장, 방어, 현금성, 리밸런싱 보조처럼 mix 안의 역할을 분리해야 합니다.",
                "screen": "Backtest Analysis > Portfolio Mix Builder > Mix Weight",
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
        "저장된 Mix": [
            {
                "checkpoint": "저장된 mix가 재현되는가",
                "detail": "Saved Portfolio는 workflow 기록이 아니라 weight setup이므로 `Mix 재실행 및 검증` 결과부터 확인합니다.",
                "screen": "Portfolio Mix Builder > 저장된 Mix",
            },
            {
                "checkpoint": "개별 후보 검증으로 오해하지 않는가",
                "detail": "저장 mix는 component 개별 후보가 아니라 mix 전체 기준의 Portfolio Mix 검증 보드에서 판단합니다.",
                "screen": "저장된 Mix > Portfolio Mix 검증 보드",
            },
            {
                "checkpoint": "Practical Validation으로 직접 보내는가",
                "detail": "저장 mix는 개별 current candidate가 아니므로 Candidate Review / legacy Proposal을 필수로 거치지 않습니다.",
                "screen": "저장된 Mix",
            },
            {
                "checkpoint": "Final Review에서 current 검증 결과로 읽히는가",
                "detail": "최종 검토는 Saved Portfolio 원본이 아니라 Practical Validation Result를 기준으로 진행합니다.",
                "screen": "Final Review",
            },
        ],
        "보류 / 재검토": [
            {
                "checkpoint": "막힘 원인이 어느 화면 소유인지 찾았는가",
                "detail": "데이터 문제, promotion policy blocker, 비교 근거 부족, 구성 / 비중 문제를 분리해야 합니다.",
                "screen": "Backtest Analysis / Practical Validation",
            },
            {
                "checkpoint": "Final Review 직행을 멈췄는가",
                "detail": "hold, blocked, insufficient evidence 상태에서는 모니터링 후보 선정보다 보류나 재검토 기록이 맞습니다.",
                "screen": "Final Review",
            },
            {
                "checkpoint": "되돌아갈 화면이 명확한가",
                "detail": "데이터면 ingestion / 실행 설정, component 근거면 Portfolio Mix Builder, 비중이면 Backtest Analysis의 weight builder로 돌아갑니다.",
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
            "개념": "Promotion Policy Signal",
            "제품 안에서의 의미": "개별 backtest 결과에 붙는 후보 handoff policy 신호",
            "사용자가 볼 곳": "Backtest Analysis 결과",
        },
        {
            "개념": "Backtest Analysis",
            "제품 안에서의 의미": "Single Strategy, Portfolio Mix Builder, 저장 mix replay로 후보 source를 만드는 1단계",
            "사용자가 볼 곳": "Backtest > Backtest Analysis",
        },
        {
            "개념": "Practical Validation",
            "제품 안에서의 의미": "선택된 source의 구성, 비중, Data Trust, blocker를 확인하는 2단계",
            "사용자가 볼 곳": "Backtest > Practical Validation",
        },
        {
            "개념": "Final Review",
            "제품 안에서의 의미": "selected-route gate까지 통과한 후보를 Portfolio Monitoring 후보로 저장하는 마지막 판단 화면",
            "사용자가 볼 곳": "Backtest > Final Review",
        },
        {
            "개념": "Portfolio Monitoring",
            "제품 안에서의 의미": "Final Review에서 저장된 모니터링 후보 포트폴리오를 읽어보는 read-only 운영 화면",
            "사용자가 볼 곳": "Operations > Portfolio Monitoring",
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
            "담는 내용": "Backtest Analysis에서 선택한 단일 / Portfolio Mix 후보 source",
            "생성 화면": "Backtest Analysis",
        },
        {
            "기록": "Practical Validation Result",
            "담는 내용": "구성, 비중, Data Trust, blocker, paper observation preview",
            "생성 화면": "Practical Validation",
        },
        {
            "기록": "Saved Portfolio",
            "담는 내용": "Portfolio Mix Builder에서 저장한 재사용 weight setup",
            "생성 화면": "Portfolio Mix Builder",
        },
        {
            "기록": "Final Selection Decision",
            "담는 내용": "모니터링 후보 선정 판단. Dashboard는 이 기록을 읽기만 합니다.",
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
            "상황": "현재 제품 방향과 만들지 않을 범위를 확인할 때",
            "문서": ".aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md",
            "역할": "finance console의 제품 목표, 핵심 원칙, no-live-trading 경계",
        },
        {
            "상황": "현재 finance 전체 구조를 잡고 싶을 때",
            "문서": ".aiworkspace/note/finance/docs/PROJECT_MAP.md",
            "역할": "finance package의 현재 제품 표면, 주요 entrypoint, data / strategy / review layer 요약",
        },
        {
            "상황": "후보 생성부터 선정 후 관찰까지 사용자 흐름을 볼 때",
            "문서": ".aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md",
            "역할": "Backtest Analysis -> Practical Validation -> Final Review -> Portfolio Monitoring 흐름과 stage ownership",
        },
        {
            "상황": "Backtest 화면이 어떤 순서로 동작하는지 볼 때",
            "문서": ".aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md",
            "역할": "Backtest Analysis / Practical Validation / Final Review / Operations 보조 화면 흐름",
        },
        {
            "상황": "저장소, JSONL, DB, generated artifact 경계를 확인할 때",
            "문서": ".aiworkspace/note/finance/docs/data/README.md",
            "역할": "registry / saved / run history / provider snapshot의 보존 경계와 데이터 의미",
        },
        {
            "상황": "로컬 실행, 검증 명령, 커밋 hygiene를 확인할 때",
            "문서": ".aiworkspace/note/finance/docs/runbooks/README.md",
            "역할": "Streamlit 실행, focused check, generated artifact 제외 기준",
        },
        {
            "상황": "모니터링 후보 포트폴리오 운영 대시보드를 확인할 때",
            "문서": ".aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md",
            "역할": "Portfolio Monitoring이 Final Review selected row를 read-only로 읽는 운영 경계",
        },
        {
            "상황": "용어가 헷갈릴 때",
            "문서": ".aiworkspace/note/finance/docs/GLOSSARY.md",
            "역할": "Promotion Policy Signal, Pre-Live, Candidate Registry 같은 반복 용어 설명",
        },
        {
            "상황": "프로젝트의 큰 phase 위치를 확인할 때",
            "문서": ".aiworkspace/note/finance/docs/ROADMAP.md",
            "역할": "전체 phase 흐름, 현재 방향, 이후 작업 축",
        },
        {
            "상황": "최신 문서 목록을 훑고 싶을 때",
            "문서": ".aiworkspace/note/finance/docs/INDEX.md",
            "역할": "finance 문서의 상위 index",
        },
    ]


def _registry_detail_rows() -> list[dict[str, str]]:
    return [
        {
            "흐름 단계": "1단계 Backtest Analysis",
            "파일": "PORTFOLIO_SELECTION_SOURCES.jsonl",
            "담는 데이터": "단일 전략 후보, Portfolio Mix 후보, 저장 mix replay를 current selection source로 변환한 기록",
            "화면 위치": "Backtest > Backtest Analysis",
            "읽는 법": "후보 검증 근거의 입력 source입니다. live approval이나 주문 지시가 아닙니다.",
        },
        {
            "흐름 단계": "2단계 Practical Validation",
            "파일": "PRACTICAL_VALIDATION_RESULTS.jsonl",
            "담는 데이터": "구성 / 비중 / Data Trust / blocker / robustness preview / paper observation preview",
            "화면 위치": "Backtest > Practical Validation",
            "읽는 법": "Final Review가 우선 읽는 검증 결과입니다.",
        },
        {
            "흐름 단계": "3단계 Final Review",
            "파일": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
            "담는 데이터": "모니터링 후보 선정 판단, operator reason, inline paper observation",
            "화면 위치": "Backtest > Final Review / Operations > Portfolio Monitoring",
            "읽는 법": "Portfolio Monitoring의 source-of-truth입니다.",
        },
        {
            "흐름 단계": "4단계 사후 관찰",
            "파일": "SELECTED_PORTFOLIO_MONITORING_LOG.jsonl",
            "담는 데이터": "모니터링 후보 선정 후 별도 monitoring snapshot을 저장할 때 쓰는 current workflow 보조 ledger",
            "화면 위치": "Operations > Portfolio Monitoring",
            "읽는 법": "현재 dashboard의 필수 입력은 아니며, selected row 관찰 보조 기록입니다.",
        },
        {
            "흐름 단계": "Legacy compatibility",
            "파일": "FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl",
            "담는 데이터": "기존 Final Review V1 판단 기록",
            "화면 위치": "Backtest legacy compatibility",
            "읽는 법": "새 dashboard source-of-truth는 FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl입니다. V1은 과거 기록 해석용입니다.",
        },
    ]


def _runtime_artifact_rows() -> list[dict[str, str]]:
    return [
        {
            "파일": "BACKTEST_RUN_HISTORY.jsonl",
            "폴더": ".aiworkspace/note/finance/run_history/",
            "담는 데이터": "Backtest 실행 payload, 결과 요약, replay에 필요한 실행 기록",
            "화면 위치": "Operations > Backtest Run History",
        },
        {
            "파일": "WEB_APP_RUN_HISTORY.jsonl",
            "폴더": ".aiworkspace/note/finance/run_history/",
            "담는 데이터": "웹 앱 로컬 실행 / 운영 로그 성격의 runtime artifact",
            "화면 위치": "로컬 운영 보조 기록",
        },
        {
            "파일": "SAVED_PORTFOLIOS.jsonl",
            "폴더": ".aiworkspace/note/finance/saved/",
            "담는 데이터": "Portfolio Mix Builder에서 만든 재사용 가능한 portfolio mix setup",
            "화면 위치": "Backtest > Portfolio Mix Builder > 저장된 Mix",
        },
    ]


def _reference_path_lines() -> list[str]:
    return [
        ".aiworkspace/note/finance/docs/INDEX.md",
        ".aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md",
        ".aiworkspace/note/finance/docs/ROADMAP.md",
        ".aiworkspace/note/finance/docs/PROJECT_MAP.md",
        ".aiworkspace/note/finance/docs/GLOSSARY.md",
        ".aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md",
        ".aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md",
        ".aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md",
        ".aiworkspace/note/finance/docs/data/README.md",
        ".aiworkspace/note/finance/docs/runbooks/README.md",
        ".aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl",
        ".aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl",
        ".aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
        ".aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl",
        ".aiworkspace/note/finance/saved/SAVED_PORTFOLIO_MIXES.jsonl",
        ".aiworkspace/note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl",
        ".aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl",
        ".aiworkspace/note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
        ".aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
        ".aiworkspace/note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl",
        ".aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl",
        ".aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl",
        ".aiworkspace/note/finance/run_history/WEB_APP_RUN_HISTORY.jsonl",
        ".aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl",
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
          .qg-center-band {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            background: #ffffff;
            padding: 1rem 1.1rem;
            margin: 0.35rem 0 1rem;
          }
          .qg-center-title {
            color: #111827;
            font-size: 1.35rem;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 0.25rem;
          }
          .qg-center-copy {
            color: #374151;
            font-size: 0.94rem;
            line-height: 1.5;
            max-width: 980px;
          }
          .qg-task-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 0.72rem;
            margin: 0.65rem 0 1rem;
          }
          .qg-task-card {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            background: #ffffff;
            padding: 0.86rem;
            min-height: 210px;
          }
          .qg-task-owner {
            color: #2f6f9f;
            font-size: 0.73rem;
            font-weight: 800;
            line-height: 1.35;
            margin-bottom: 0.3rem;
          }
          .qg-task-title {
            color: #111827;
            font-size: 1rem;
            font-weight: 800;
            line-height: 1.35;
            margin-bottom: 0.28rem;
          }
          .qg-task-copy {
            color: #374151;
            font-size: 0.82rem;
            line-height: 1.44;
            margin-bottom: 0.45rem;
          }
          .qg-task-boundary {
            border-top: 1px solid #e5e7eb;
            color: #64748b;
            font-size: 0.76rem;
            font-weight: 700;
            line-height: 1.4;
            padding-top: 0.42rem;
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
          <div class="qg-hero-title">모니터링 후보 포트폴리오를 찾는 운영 가이드</div>
          <div class="qg-hero-copy">
            이 화면은 문서 목록이 아니라 의사결정 안내입니다. 먼저 현재 진행 상황을 고르고,
            그 경로에서 어떤 화면을 지나고 어느 조건에서 멈춰야 하는지 확인합니다.
          </div>
          <div class="qg-status-strip">
            <span class="qg-chip">Current workflow: Backtest Analysis -> Practical Validation -> Final Review</span>
            <span class="qg-chip">Operations follow-up: Portfolio Monitoring</span>
            <span class="qg-chip">Runtime {runtime_text}</span>
            <span class="qg-chip">Git {git_text}</span>
          </div>
        </section>
        """
    )


def _render_reference_center_hero(runtime_marker: str | None, git_sha: str | None) -> None:
    runtime_text = escape(runtime_marker or "-")
    git_text = escape(git_sha or "-")
    st.html(
        f"""
        <section class="qg-center-band">
          <div class="qg-card-kicker">Reference Center</div>
          <div class="qg-center-title">제품 전체 운영 기준을 빠르게 찾는 안내 화면</div>
          <div class="qg-center-copy">
            데이터가 최신인지, 어떤 화면에서 후보를 만들지, 검증 상태가 무엇을 막는지,
            선정 후 모니터링을 어떻게 읽을지 작업 기준으로 확인합니다.
          </div>
          <div class="qg-status-strip">
            <span class="qg-chip">Read-only guide</span>
            <span class="qg-chip">No provider fetch</span>
            <span class="qg-chip">No broker order</span>
            <span class="qg-chip">Runtime {runtime_text}</span>
            <span class="qg-chip">Git {git_text}</span>
          </div>
        </section>
        """
    )


def _render_task_cards(catalog: dict[str, list[dict[str, str]]]) -> None:
    st.markdown("### 먼저 고를 작업")
    st.caption("현재 막힌 지점이나 확인하려는 흐름을 기준으로 owner screen과 안전한 다음 행동을 찾습니다.")
    cards: list[str] = []
    for row in catalog["task_cards"]:
        cards.append(
            f"""
            <div class="qg-task-card">
              <div class="qg-task-owner">{escape(row["owner_screen"])}</div>
              <div class="qg-task-title">{escape(row["title"])}</div>
              <div class="qg-task-copy">{escape(row["summary"])}</div>
              <div class="qg-task-copy"><strong>Safe action:</strong> {escape(row["safe_action"])}</div>
              <div class="qg-task-boundary">{escape(row["does_not_do"])}</div>
            </div>
            """
        )
    st.html(f'<div class="qg-task-grid">{"".join(cards)}</div>')


def _render_current_product_flow(catalog: dict[str, list[dict[str, Any]]]) -> None:
    st.markdown("### 현재 제품 흐름")
    st.caption("Reference는 아래 화면의 owner와 기록 경계를 설명합니다. 직접 실행하거나 저장하지는 않습니다.")
    st.dataframe(
        pd.DataFrame(catalog["journeys"])[
            ["title", "when_to_use", "screens", "records", "go_review_stop", "boundary"]
        ],
        width="stretch",
        hide_index=True,
    )
    _render_journey_detail(catalog)


def _render_journey_detail(catalog: dict[str, list[dict[str, Any]]]) -> None:
    st.markdown("#### Journey 상세 보기")
    st.caption("선택한 흐름에서 어떤 순서로 확인하고, 어떤 실패 상태에서 멈춰야 하는지 봅니다.")
    options = [row["title"] for row in catalog["journeys"]]
    selected = st.selectbox(
        "Journey 선택",
        options=options,
        key="reference_guides_journey_detail",
    )
    journey = next(row for row in catalog["journeys"] if row["title"] == selected)
    with st.container(border=True):
        st.markdown(f"##### {journey['title']}")
        st.caption(f"Owner screens: {journey['screens']}")
        st.markdown(f"**언제 쓰나:** {journey['when_to_use']}")
        st.markdown(f"**기록:** {journey['records']}")
        st.warning(f"Boundary: {journey['boundary']}")

        step_rows = list(journey.get("steps") or [])
        if step_rows:
            st.markdown("##### 확인 순서")
            st.dataframe(
                pd.DataFrame(step_rows)[
                    ["order", "owner_screen", "check", "safe_next", "downstream", "stop_condition"]
                ],
                width="stretch",
                hide_index=True,
            )

        failure_rows = list(journey.get("failure_states") or [])
        if failure_rows:
            st.markdown("##### 자주 막히는 상태")
            st.dataframe(
                pd.DataFrame(failure_rows)[
                    ["state", "owner_screen", "first_check", "safe_next", "stop_condition"]
                ],
                width="stretch",
                hide_index=True,
            )


def _render_status_lookup(catalog: dict[str, list[dict[str, Any]]]) -> None:
    st.markdown("### 자주 막히는 상태 / 용어")
    query = st.text_input(
        "상태 / 용어 검색",
        placeholder="예: NOT_RUN, BLOCKED, Data Trust, Provider Coverage",
        key="reference_guides_status_query",
    )
    rows = catalog["concepts"]
    if query.strip():
        needle = query.strip().lower()
        rows = [
            row
            for row in rows
            if needle
            in " ".join(str(value) for value in row.values()).lower()
        ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    if not rows:
        st.info("검색 결과가 없습니다. Glossary와 문서 / 경로 drawer도 함께 확인하세요.")


def _render_records_map(catalog: dict[str, list[dict[str, Any]]]) -> None:
    st.markdown("### 기록 / 저장 경계")
    st.caption("어떤 화면이 무엇을 만들고 다시 읽는지 확인합니다. Reference는 이 기록을 수정하지 않습니다.")
    st.dataframe(pd.DataFrame(catalog["records"]), width="stretch", hide_index=True)


def _render_troubleshooting_playbooks(catalog: dict[str, list[dict[str, Any]]]) -> None:
    st.markdown("### 문제 해결 Playbook")
    options = [row["title"] for row in catalog["playbooks"]]
    selected = st.selectbox(
        "문제 상황 선택",
        options=options,
        key="reference_guides_playbook",
    )
    playbook = next(row for row in catalog["playbooks"] if row["title"] == selected)
    with st.container(border=True):
        st.markdown(f"#### {playbook['title']}")
        st.caption(f"Owner: {playbook['owner_screen']}")
        st.markdown(f"**증상:** {playbook['symptom']}")
        st.markdown(f"**First check:** {playbook['first_check']}")
        st.markdown(f"**Safe action:** {playbook['safe_action']}")
        st.warning(f"Stop condition: {playbook['stop_condition']}")
        check_rows = list(playbook.get("check_steps") or [])
        if check_rows:
            st.markdown("##### 확인 순서")
            st.dataframe(
                pd.DataFrame(check_rows)[["order", "owner_screen", "check", "pass_signal"]],
                width="stretch",
                hide_index=True,
            )
        evidence_locations = list(playbook.get("evidence_locations") or [])
        if evidence_locations:
            st.markdown("##### Evidence 위치")
            st.code("\n".join(evidence_locations), language="text")


def _render_reference_center() -> None:
    catalog = get_reference_center_catalog()
    st.info(
        "Reference는 읽기 전용 안내 화면입니다. 데이터 수집, registry 저장, provider fetch, broker order, "
        "auto rebalance는 각 owner screen에서만 다룹니다."
    )
    _render_task_cards(catalog)
    tabs = st.tabs(["제품 흐름", "상태 / 용어", "기록 경계", "문제 해결"])
    with tabs[0]:
        _render_current_product_flow(catalog)
    with tabs[1]:
        _render_status_lookup(catalog)
    with tabs[2]:
        _render_records_map(catalog)
    with tabs[3]:
        _render_troubleshooting_playbooks(catalog)


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
            - `보류 / 대기`: 막힘을 해결하기 전에는 모니터링 후보 선정으로 해석하지 않습니다.
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
                - `1`: Backtest Analysis에서 단일 / Portfolio Mix / 저장 mix 후보 source를 만든다.
                - `2`: Practical Validation에서 검증 프로필, Input Evidence, 12개 Practical Diagnostics를 확인한다.
                - `3`: Final Review에서 모니터링 후보 선정과 이유를 current decision으로 남긴다.
                - `4`: Portfolio Monitoring에서 모니터링 후보 row를 read-only로 관찰한다.
                """
            )
    with tabs[2]:
        st.dataframe(pd.DataFrame(_storage_rows()), width="stretch", hide_index=True)
        st.info(
            "Saved Portfolio는 재사용 setup이고, current selection source는 검증 입력입니다. "
            "저장된 Mix는 Candidate Review나 legacy Proposal을 필수로 거치지 않고 Practical Validation으로 연결합니다. "
            "Portfolio Monitoring은 새 저장소가 아니라 Final Selection Decision을 읽는 운영 화면입니다."
        )
    with tabs[3]:
        st.warning(
            "`SELECT_FOR_PRACTICAL_PORTFOLIO`는 Portfolio Monitoring 후보 선정 신호이지 live approval, broker order, 자동매매 지시가 아닙니다."
        )
        st.markdown(
            """
            - `Promotion Policy Signal`은 후보 handoff policy 신호입니다.
            - `Backtest Analysis`는 후보 source를 만드는 1단계입니다.
            - `Practical Validation`은 source를 profile-aware practical diagnostics 결과로 구조화하는 2단계입니다.
            - `Final Review`는 현재 workflow의 마지막 판단 기록입니다.
            - `Portfolio Monitoring`은 Final Review selected row를 Operations에서 다시 읽는 화면입니다.
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
    """Render the product-facing Reference guide for the finance console."""

    _render_page_style()
    st.title("Guides")
    st.caption("제품 전체 운영 흐름, 상태 해석, 기록 경계, 문제 해결 기준을 빠르게 찾는 안내 화면입니다.")
    _render_reference_center_hero(runtime_marker, git_sha)

    mode_key = "reference_guides_view_mode"
    if st.session_state.get(mode_key) not in REFERENCE_VIEW_OPTIONS:
        st.session_state[mode_key] = REFERENCE_VIEW_OPTIONS[0]

    if hasattr(st, "segmented_control"):
        st.segmented_control(
            "Reference 보기",
            options=REFERENCE_VIEW_OPTIONS,
            selection_mode="single",
            required=True,
            key=mode_key,
            width="stretch",
        )
        selected_mode = str(st.session_state.get(mode_key) or REFERENCE_VIEW_OPTIONS[0])
    else:
        selected_mode = st.radio(
            "Reference 보기",
            options=REFERENCE_VIEW_OPTIONS,
            horizontal=True,
            key=mode_key,
        )

    if selected_mode == "Reference Center":
        _render_reference_center()
        _render_runtime_reference(loaded_at, render_runtime_snapshot)
        return

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
