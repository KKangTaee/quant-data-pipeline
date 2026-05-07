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
            "summary": "후보 1개를 Current Candidate와 Pre-Live 기록으로 남기고 Final Review가 직접 읽는 경로입니다.",
            "goal": "후보 1개를 Current Candidate와 Pre-Live 기록으로 남기고 Final Review에서 직접 읽게 합니다.",
            "sequence": "Single Strategy 또는 Compare 결과 확인 -> Candidate Review 저장 -> Portfolio Proposal 단일 후보 평가 -> Final Review",
            "caution": "단일 후보는 proposal draft를 새로 저장하지 않습니다. Portfolio Proposal에서는 direct candidate로 읽습니다.",
            "records": "Review Note, Current Candidate, Pre-Live, Final Decision",
            "dot": [
                ("single", "1-2\\nRun + Data Trust", "run"),
                ("realmoney", "3-4\\nSignal / Blocker", "gate"),
                ("compare", "5\\nCompare Evidence", "compare"),
                ("candidate", "6\\nReview + Registry", "candidate"),
                ("direct", "7\\nDirect Candidate", "proposal"),
                ("final", "8-10\\nValidation + Decision", "final"),
            ],
            "edges": [
                ("single", "realmoney", "signal"),
                ("realmoney", "compare", "not hold"),
                ("compare", "candidate", "PASS / CONDITIONAL"),
                ("candidate", "direct", "PORTFOLIO_PROPOSAL_READY"),
                ("direct", "final", "검증"),
            ],
        },
        "여러 후보 묶음": {
            "headline": "여러 후보를 하나의 proposal로 묶기",
            "summary": "여러 current candidate를 목적, 역할, target weight가 있는 포트폴리오 초안으로 저장하는 경로입니다.",
            "goal": "여러 current candidate를 목적, 역할, target weight가 있는 portfolio proposal로 묶습니다.",
            "sequence": "후보별 실행 / 비교 -> Candidate Review에서 후보 저장 -> Portfolio Proposal에서 역할 / 비중 설계 -> Final Review",
            "caution": "Portfolio Proposal은 후보를 새로 만드는 화면이 아니라, 이미 저장된 후보를 묶는 화면입니다.",
            "records": "Current Candidate, Pre-Live, Portfolio Proposal, Final Decision",
            "dot": [
                ("candidates", "1-6\\nCandidate Pool", "candidate"),
                ("roles", "7A\\nRole + Weight Logic", "proposal"),
                ("draft", "7B\\nSave Proposal Draft", "proposal"),
                ("validation", "8\\nRisk / Validation", "gate"),
                ("final", "9-10\\nObservation + Decision", "final"),
            ],
            "edges": [
                ("candidates", "roles", "2개 이상"),
                ("roles", "draft", "weight=100%"),
                ("draft", "validation", "proposal ready"),
                ("validation", "final", "hard blocker 없음"),
            ],
        },
        "저장된 비중 조합": {
            "headline": "이미 저장된 weight setup을 workflow 기록으로 연결",
            "summary": "Compare에서 저장한 mix를 replay한 뒤 Candidate Review가 아니라 Portfolio Proposal 초안으로 연결합니다.",
            "goal": "Saved Portfolio에 저장된 재사용 weight setup을 다시 검토해 proposal로 연결합니다.",
            "sequence": "저장 조합 replay -> 결과 확인 -> Use This Mix In Portfolio Proposal -> Final Review",
            "caution": "Saved Portfolio는 후보 registry가 아닙니다. Candidate Review를 거치지 않고 proposal registry에 연결합니다.",
            "records": "Saved Portfolio, Portfolio Proposal, Final Decision",
            "dot": [
                ("saved", "5A\\nSaved Weight Setup", "compare"),
                ("replay", "5B\\nReplay / Mix Board", "gate"),
                ("proposal", "7\\nAttach To Proposal", "proposal"),
                ("final", "8-10\\nValidation + Decision", "final"),
            ],
            "edges": [
                ("saved", "replay", "replay"),
                ("replay", "proposal", "NOT RECORDED"),
                ("proposal", "final", "proposal saved"),
            ],
        },
        "보류 / 재검토": {
            "headline": "멈춰야 할 이유를 원인 화면으로 되돌림",
            "summary": "hold, blocked, evidence 부족, re-review가 나오면 Final Review 직행이 아니라 원인 화면으로 돌아갑니다.",
            "goal": "진행이 막혔을 때 최종 선정으로 밀고 가지 않고 원인 화면으로 돌아갑니다.",
            "sequence": "막힘 원인 확인 -> 소유 화면으로 복귀 -> 데이터 / 근거 / 구성 보강 -> 같은 기준으로 재검토",
            "caution": "hold, blocked, evidence 부족 상태는 최종 선정이 아니라 보류 또는 재검토로 남깁니다.",
            "records": "필요할 때만 Review Note 또는 Final Decision에 보류 사유 기록",
            "dot": [
                ("hold", "3-4\\nHold / Blocker", "stop"),
                ("compare", "5\\nCompare Evidence", "compare"),
                ("candidate", "6\\nPackaging Evidence", "candidate"),
                ("proposal", "7\\nProposal Repair", "proposal"),
                ("review", "8-9\\nHOLD / RE_REVIEW", "final"),
            ],
            "edges": [
                ("hold", "compare", "blocker 해결"),
                ("compare", "candidate", "근거 확보"),
                ("candidate", "proposal", "route ready"),
                ("proposal", "review", "검증"),
                ("review", "hold", "재검토 루프"),
            ],
        },
    }


def _decision_gate_rows() -> list[dict[str, str]]:
    return [
        {
            "gate": "Compare로 가도 되는가",
            "go": "Promotion이 hold가 아니고 Deployment가 blocked가 아님",
            "review": "warning은 있지만 원인과 보강 항목을 설명할 수 있음",
            "stop": "price freshness error, benchmark 부재, hard blocker",
            "screen": "Backtest 결과 > Real-Money",
        },
        {
            "gate": "Candidate로 남겨도 되는가",
            "go": "Compare PASS 또는 CONDITIONAL, 상대 근거와 Data Trust 해석 가능",
            "review": "상대 성과 약점은 있지만 포트폴리오 역할이 명확함",
            "stop": "비교 실패, Real-Money signal 공백, 상대 근거 없음",
            "screen": "Compare & Portfolio Builder",
        },
        {
            "gate": "Proposal로 묶어도 되는가",
            "go": "Current Candidate와 Pre-Live 운영 기록이 있고 route가 proposal ready",
            "review": "후보 수는 충분하지만 역할 / 비중 근거 보강 필요",
            "stop": "Pre-Live record 없음, active 후보 hold/reject, source 식별 불가",
            "screen": "Candidate Review / Portfolio Proposal",
        },
        {
            "gate": "Final Review를 기록해도 되는가",
            "go": "Validation, robustness, paper observation 기준이 해석 가능",
            "review": "관찰 기간 또는 제약 조건을 남기고 HOLD 기록 가능",
            "stop": "hard blocker가 남아 있거나 최종 판단 이유가 비어 있음",
            "screen": "Final Review",
        },
    ]


def _stage_timeline_rows() -> list[dict[str, str]]:
    return [
        {
            "step": "1",
            "phase": "준비",
            "screen": "Data / Ingestion",
            "title": "데이터 신뢰 확인",
            "check": "가격, benchmark, factor, profile이 최신인지 확인합니다.",
            "output": "실행 가능한 데이터 상태",
        },
        {
            "step": "2",
            "phase": "실행",
            "screen": "Single Strategy",
            "title": "전략 하나 실행",
            "check": "기간, universe, 전략 옵션, 비용 조건을 같은 계약으로 고정합니다.",
            "output": "latest result bundle",
        },
        {
            "step": "3",
            "phase": "판정",
            "screen": "Result / Real-Money",
            "title": "성과와 실전 신호 확인",
            "check": "CAGR, MDD, benchmark, Data Trust, promotion 신호를 같이 봅니다.",
            "output": "compare 진입 후보",
        },
        {
            "step": "4",
            "phase": "판정",
            "screen": "Real-Money",
            "title": "Hold / Blocker 해결",
            "check": "hard blocker, stale data, deployment blocked 여부를 먼저 해결합니다.",
            "output": "진행 / 보류 / 재검토",
        },
        {
            "step": "5",
            "phase": "비교",
            "screen": "Compare",
            "title": "상대 근거 만들기",
            "check": "같은 기간과 입력으로 여러 전략 또는 mix를 비교합니다.",
            "output": "상대 성과와 역할 근거",
        },
        {
            "step": "6",
            "phase": "후보화",
            "screen": "Candidate Review",
            "title": "후보 기록 남기기",
            "check": "Review Note, registry, Pre-Live 운영 상태를 저장합니다.",
            "output": "Current Candidate / Pre-Live record",
        },
        {
            "step": "7",
            "phase": "구성",
            "screen": "Portfolio Proposal",
            "title": "단일 직행 또는 묶음 설계",
            "check": "단일 후보는 direct로 읽고, 여러 후보는 역할과 target weight를 명시합니다.",
            "output": "direct candidate 또는 proposal draft",
        },
        {
            "step": "8",
            "phase": "검증",
            "screen": "Final Review",
            "title": "Validation 기준 확인",
            "check": "portfolio risk, validation pack, blocker, component evidence를 확인합니다.",
            "output": "검증 가능 / 보강 필요",
        },
        {
            "step": "9",
            "phase": "검증",
            "screen": "Final Review",
            "title": "Robustness / Paper 관찰",
            "check": "stress, sensitivity, paper observation 기준을 최종 판단 근거로 정리합니다.",
            "output": "최종 판단 근거",
        },
        {
            "step": "10",
            "phase": "완료",
            "screen": "Final Review",
            "title": "최종 판단 기록",
            "check": "선정, 보류, 거절, 재검토 중 하나를 이유와 함께 저장합니다.",
            "output": "Final Selection Decision",
        },
    ]


def _route_stage_status() -> dict[str, dict[str, str]]:
    return {
        "단일 후보": {
            "1": "필수",
            "2": "필수",
            "3": "필수",
            "4": "필수",
            "5": "권장",
            "6": "필수",
            "7": "직행",
            "8": "필수",
            "9": "필수",
            "10": "필수",
        },
        "여러 후보 묶음": {
            "1": "반복",
            "2": "반복",
            "3": "반복",
            "4": "반복",
            "5": "필수",
            "6": "필수",
            "7": "필수",
            "8": "필수",
            "9": "필수",
            "10": "필수",
        },
        "저장된 비중 조합": {
            "1": "선행",
            "2": "선행",
            "3": "선행",
            "4": "선행",
            "5": "필수",
            "6": "생략",
            "7": "필수",
            "8": "필수",
            "9": "필수",
            "10": "필수",
        },
        "보류 / 재검토": {
            "1": "점검",
            "2": "점검",
            "3": "점검",
            "4": "핵심",
            "5": "복귀",
            "6": "보강",
            "7": "보강",
            "8": "보류",
            "9": "보류",
            "10": "대기",
        },
    }


def _route_checkpoint_rows() -> dict[str, list[dict[str, str]]]:
    return {
        "단일 후보": [
            {
                "checkpoint": "단일 전략 결과가 설명 가능한가",
                "detail": "성과, 손실, benchmark, Data Trust를 같은 화면에서 읽고 후보로 볼 이유를 말할 수 있어야 합니다.",
                "screen": "Single Strategy / Result",
            },
            {
                "checkpoint": "Real-Money blocker가 없는가",
                "detail": "hold나 blocked가 남아 있으면 Candidate Review보다 원인 해결이 먼저입니다.",
                "screen": "Result > Real-Money",
            },
            {
                "checkpoint": "후보 기록이 남았는가",
                "detail": "Review Note, Current Candidate, Pre-Live 운영 상태가 있어야 Final Review 입력으로 읽기 쉽습니다.",
                "screen": "Candidate Review",
            },
            {
                "checkpoint": "Proposal 저장을 반복하지 않는가",
                "detail": "단일 후보는 Portfolio Proposal에서 direct candidate로 평가하고, 다중 proposal draft 저장을 억지로 만들지 않습니다.",
                "screen": "Portfolio Proposal / Final Review",
            },
        ],
        "여러 후보 묶음": [
            {
                "checkpoint": "후보마다 같은 기준으로 검토했는가",
                "detail": "각 후보는 최소한 성과, Data Trust, Real-Money, Candidate Review 근거가 비교 가능해야 합니다.",
                "screen": "Single Strategy / Compare / Candidate Review",
            },
            {
                "checkpoint": "역할이 겹치지 않는가",
                "detail": "성장, 방어, 현금성, 리밸런싱 보조처럼 proposal 안의 역할을 분리해야 합니다.",
                "screen": "Portfolio Proposal",
            },
            {
                "checkpoint": "비중 합계와 이유가 명확한가",
                "detail": "target weight가 100%로 맞고, 각 weight reason이 최종 판단에서 재사용 가능해야 합니다.",
                "screen": "Portfolio Proposal",
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
                "detail": "Saved Portfolio는 workflow 기록이 아니라 weight setup이므로 replay 결과부터 확인합니다.",
                "screen": "Compare & Portfolio Builder",
            },
            {
                "checkpoint": "Candidate Review를 억지로 거치지 않는가",
                "detail": "저장 mix는 개별 current candidate가 아니므로 Use This Mix In Portfolio Proposal로 연결합니다.",
                "screen": "Saved Mix Replay",
            },
            {
                "checkpoint": "proposal 목적과 weight 이유가 보강됐는가",
                "detail": "저장 setup을 그대로 쓰더라도 proposal objective, role, risk constraint는 새로 해석해야 합니다.",
                "screen": "Portfolio Proposal",
            },
            {
                "checkpoint": "Final Review에서 proposal로 읽히는가",
                "detail": "최종 검토는 Saved Portfolio가 아니라 저장된 Portfolio Proposal registry row를 기준으로 진행합니다.",
                "screen": "Final Review",
            },
        ],
        "보류 / 재검토": [
            {
                "checkpoint": "막힘 원인이 어느 화면 소유인지 찾았는가",
                "detail": "데이터 문제, Real-Money blocker, 비교 근거 부족, proposal 구성 부족을 분리해야 합니다.",
                "screen": "Result / Compare / Candidate Review / Proposal",
            },
            {
                "checkpoint": "Final Review 직행을 멈췄는가",
                "detail": "hold, blocked, insufficient evidence 상태에서는 최종 선정보다 보류나 재검토 기록이 맞습니다.",
                "screen": "Final Review",
            },
            {
                "checkpoint": "되돌아갈 화면이 명확한가",
                "detail": "데이터면 Ingestion, 상대 근거면 Compare, 후보 근거면 Candidate Review, 비중이면 Proposal로 돌아갑니다.",
                "screen": "해당 원인 화면",
            },
            {
                "checkpoint": "재검토 후 같은 기준으로 다시 읽는가",
                "detail": "수정 후에도 1~10 단계 기준을 바꾸지 않고 같은 통과 기준으로 다시 판단합니다.",
                "screen": "Portfolio Flow",
            },
        ],
    }


def _concept_rows() -> list[dict[str, str]]:
    return [
        {
            "개념": "Real-Money",
            "제품 안에서의 의미": "개별 backtest 결과에 붙는 실전 검토 신호",
            "사용자가 볼 곳": "Backtest 결과 > Real-Money",
        },
        {
            "개념": "Candidate Review",
            "제품 안에서의 의미": "좋아 보이는 결과를 후보 기록으로 남길지 판단하는 packaging 화면",
            "사용자가 볼 곳": "Backtest > Candidate Review",
        },
        {
            "개념": "Portfolio Proposal",
            "제품 안에서의 의미": "여러 후보를 목적 / 역할 / 비중이 있는 포트폴리오 초안으로 묶는 화면",
            "사용자가 볼 곳": "Backtest > Portfolio Proposal",
        },
        {
            "개념": "Final Review",
            "제품 안에서의 의미": "선정 / 보류 / 거절 / 재검토를 기록하는 마지막 판단 화면",
            "사용자가 볼 곳": "Backtest > Final Review",
        },
        {
            "개념": "Selected Portfolio Dashboard",
            "제품 안에서의 의미": "Final Review에서 선정된 포트폴리오를 읽어보는 read-only 운영 화면",
            "사용자가 볼 곳": "Operations > Selected Portfolio Dashboard",
        },
    ]


def _storage_rows() -> list[dict[str, str]]:
    return [
        {
            "기록": "Current Candidate Registry",
            "담는 내용": "다시 열어 볼 후보 정의",
            "생성 화면": "Candidate Review",
        },
        {
            "기록": "Pre-Live Candidate Registry",
            "담는 내용": "paper / watchlist / hold 같은 운영 상태",
            "생성 화면": "Candidate Review",
        },
        {
            "기록": "Saved Portfolio",
            "담는 내용": "Compare에서 저장한 재사용 weight setup",
            "생성 화면": "Compare & Portfolio Builder",
        },
        {
            "기록": "Portfolio Proposal Registry",
            "담는 내용": "목적 / 역할 / 비중이 있는 proposal draft",
            "생성 화면": "Portfolio Proposal",
        },
        {
            "기록": "Final Selection Decision",
            "담는 내용": "선정 / 보류 / 거절 / 재검토 최종 판단. Dashboard는 이 기록을 읽기만 합니다.",
            "생성 화면": "Final Review / Operations read-only",
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
            "역할": "Single / Compare / Candidate Review / Portfolio Proposal / Final Review UI 흐름",
        },
        {
            "상황": "포트폴리오 초안 저장소를 이해할 때",
            "문서": ".note/finance/operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md",
            "역할": "여러 후보를 묶은 portfolio proposal draft가 무엇이고 언제 저장되는지 설명",
        },
        {
            "상황": "과거 paper tracking ledger 기록을 해석할 때",
            "문서": ".note/finance/operations/PAPER_PORTFOLIO_TRACKING_LEDGER_GUIDE.md",
            "역할": "Phase33 ledger의 호환성 / 관찰 기록 의미 설명",
        },
        {
            "상황": "최종 판단 기록을 확인할 때",
            "문서": ".note/finance/operations/FINAL_PORTFOLIO_SELECTION_DECISIONS_GUIDE.md",
            "역할": "Final Review에서 저장한 선정 / 보류 / 거절 / 재검토 판단 기록 사용법",
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
            "흐름 단계": "6단계 Candidate Packaging",
            "파일": "CANDIDATE_REVIEW_NOTES.jsonl",
            "담는 데이터": "후보 초안을 보고 사람이 남긴 Review Decision, 이유, 다음 행동",
            "화면 위치": "Backtest > Candidate Review > 1. Draft 확인 / Review Note 저장",
            "읽는 법": "저장 전 검토 메모입니다. 후보 자체를 확정한 registry는 아닙니다.",
        },
        {
            "흐름 단계": "6단계 Candidate Packaging",
            "파일": "CURRENT_CANDIDATE_REGISTRY.jsonl",
            "담는 데이터": "명시적으로 남긴 current candidate, near-miss, scenario, stop 후보 row",
            "화면 위치": "Backtest > Candidate Review > 2. Registry 저장 / Operations > Candidate Library",
            "읽는 법": "이 프로그램이 다시 열어 볼 후보 정의 목록입니다.",
        },
        {
            "흐름 단계": "6단계 Candidate Packaging",
            "파일": "PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
            "담는 데이터": "후보를 paper tracking, watchlist, hold, re-review 중 어떤 운영 상태로 둘지 남긴 기록",
            "화면 위치": "Backtest > Candidate Review > 3. 운영 기록 저장 및 Portfolio Proposal 이동",
            "읽는 법": "실제 돈을 넣기 전 관찰 / 보류 상태 기록입니다.",
        },
        {
            "흐름 단계": "7단계 Portfolio Proposal",
            "파일": "PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
            "담는 데이터": "여러 후보를 묶은 목적, 역할, target weight, 비중 근거, blocker가 있는 proposal draft",
            "화면 위치": "Backtest > Portfolio Proposal",
            "읽는 법": "포트폴리오 구성 초안입니다. live approval이나 주문 지시가 아닙니다.",
        },
        {
            "흐름 단계": "8단계 Final Review 검증",
            "파일": "PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl",
            "담는 데이터": "과거 Phase33에서 만든 paper tracking 관찰 조건과 trigger 기록",
            "화면 위치": "Backtest > Portfolio Proposal / Final Review 호환 영역",
            "읽는 법": "현재 main flow에서는 Final Review의 inline paper observation 기준으로 흡수해서 읽습니다.",
        },
        {
            "흐름 단계": "9~10단계 Final Review",
            "파일": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
            "담는 데이터": "실전 후보 선정, 관찰 보류, 거절, 재검토 판단과 이유",
            "화면 위치": "Backtest > Final Review / Operations > Selected Portfolio Dashboard",
            "읽는 법": "최종 판단 원본입니다. Dashboard는 selected row를 read-only로 보여줍니다.",
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
            "화면 위치": "Backtest > Compare & Portfolio Builder > 저장 Mix 다시 열기",
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
            <span class="qg-chip">Current workflow: Portfolio Proposal -> Final Review</span>
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
    if status in {"권장", "반복", "직행", "복귀", "보강"}:
        return "active"
    if status in {"선행", "점검", "보류", "대기"}:
        return "warn"
    return "muted"


def _render_route_checkpoints(selected_route: str) -> None:
    st.markdown(f"### {selected_route} 핵심 체크포인트")
    st.caption(
        "전체 1~10 단계 중 이 진행 상황에서 특히 놓치면 안 되는 판단 지점만 모아 보여줍니다."
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
    st.markdown("### 전체 1~10 단계에서 현재 위치")
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
        with st.expander("1~10단계 전체를 어떻게 읽나", expanded=False):
            st.markdown(
                """
                - `1-5`: 데이터, 단일 전략, Real-Money, Compare로 후보 근거를 만든다.
                - `6`: Candidate Review에서 후보로 남길지와 Pre-Live 운영 상태를 기록한다.
                - `7`: 단일 후보는 direct candidate로 읽고, 여러 후보는 proposal draft로 묶는다.
                - `8-10`: Final Review에서 검증 근거와 최종 판단을 남기고 다시 확인한다.
                """
            )
    with tabs[2]:
        st.dataframe(pd.DataFrame(_storage_rows()), width="stretch", hide_index=True)
        st.info(
            "Saved Portfolio는 재사용 setup이고, Portfolio Proposal은 workflow 기록입니다. "
            "저장된 비중 조합은 Candidate Review가 아니라 Portfolio Proposal로 연결합니다. "
            "Selected Portfolio Dashboard는 새 저장소가 아니라 Final Selection Decision을 읽는 운영 화면입니다."
        )
    with tabs[3]:
        st.warning(
            "`SELECT_FOR_PRACTICAL_PORTFOLIO`는 실전 후보 선정 신호이지 live approval, broker order, 자동매매 지시가 아닙니다."
        )
        st.markdown(
            """
            - `Real-Money`는 검증 신호입니다.
            - `Candidate Review`는 후보 기록입니다.
            - `Portfolio Proposal`은 후보 묶음 초안입니다.
            - `Final Review`는 현재 workflow의 마지막 판단 기록입니다.
            - `Selected Portfolio Dashboard`는 Final Review selected row를 Operations에서 다시 읽는 화면입니다.
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
