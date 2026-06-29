from __future__ import annotations

from copy import deepcopy
from typing import Any


_ROWS: list[dict[str, Any]] = [
    {
        "key": "reference_help",
        "title": "Reference help",
        "korean_label": "도움말",
        "classification": "안내",
        "required_for_backtest_execution": False,
        "strategy_development_useful": True,
        "default_display": "접힘",
        "recommended_location": "전략 개발 참고",
        "reason": "화면 사용 순서와 경계를 확인할 때만 필요하며, 백테스트 실행 자체에는 필요하지 않습니다.",
    },
    {
        "key": "strategy_evidence_inventory",
        "title": "Strategy Evidence Inventory / Direction Panel",
        "korean_label": "전략 성숙도 / 다음 액션",
        "classification": "전략 상태판",
        "required_for_backtest_execution": False,
        "strategy_development_useful": True,
        "default_display": "숨김",
        "recommended_location": "Reference / 문서",
        "reason": "전체 catalog 전략의 maturity와 next action을 보는 참고 보드입니다.",
    },
    {
        "key": "strict_annual_etf_bridge",
        "title": "Strict Annual + GTAA / Equal Weight Bridge",
        "korean_label": "Strict Annual / ETF 후보군 연결 기준",
        "classification": "후보군 분류",
        "required_for_backtest_execution": False,
        "strategy_development_useful": True,
        "default_display": "숨김",
        "recommended_location": "Reference / 문서",
        "reason": "첫 evidence-mature 후보군의 해석 기준이며 실행 form은 별도로 존재합니다.",
    },
    {
        "key": "risk_on_momentum_governance",
        "title": "Risk-On Momentum 5D Governance",
        "korean_label": "Risk-On Momentum 5D 승격 조건",
        "classification": "governance 참고",
        "required_for_backtest_execution": False,
        "strategy_development_useful": True,
        "default_display": "숨김",
        "recommended_location": "전략 상세 / Reference",
        "reason": "Risk-On 전략을 validation / final / monitoring으로 승격하기 전 필요한 조건을 설명합니다.",
    },
    {
        "key": "etf_evidence_expansion",
        "title": "ETF Evidence Expansion",
        "korean_label": "ETF 전략 보강 필요 근거",
        "classification": "evidence gap 참고",
        "required_for_backtest_execution": False,
        "strategy_development_useful": True,
        "default_display": "숨김",
        "recommended_location": "Reference / 문서",
        "reason": "GRS / Risk Parity / Dual Momentum의 부족한 provider / cost / benchmark evidence를 정리합니다.",
    },
    {
        "key": "etf_current_anchor_workbench",
        "title": "ETF Current Anchor Workbench",
        "korean_label": "ETF 현재 근거 확인",
        "classification": "고급 readiness 확인",
        "required_for_backtest_execution": False,
        "strategy_development_useful": True,
        "default_display": "숨김",
        "recommended_location": "고급 전략 검토",
        "reason": "기존 run history / source handoff 기준의 readiness를 확인할 때만 필요합니다.",
    },
    {
        "key": "etf_rerun_matrix_workbench",
        "title": "ETF Rerun Matrix Workbench",
        "korean_label": "ETF 재실행 매트릭스",
        "classification": "고급 전략 실험",
        "required_for_backtest_execution": False,
        "strategy_development_useful": True,
        "default_display": "숨김",
        "recommended_location": "고급 전략 검토",
        "reason": "선택 ETF 전략의 scenario sensitivity를 session-only로 비교할 때만 사용합니다.",
    },
]


def build_backtest_analysis_research_board() -> dict[str, Any]:
    """Describe Backtest Analysis reference panels without loading workflow artifacts."""

    return deepcopy(
        {
            "board_id": "backtest_analysis_research_reference_board_v1",
            "title": "전략 개발 참고",
            "status": "기본 숨김",
            "primary_flow_priority": "strategy_execution_first",
            "default_visible": False,
            "summary": (
                "Backtest Analysis 기본 화면은 전략 실행, 비교, 후보 생성을 먼저 보여줍니다. "
                "아래 항목들은 전략 개발 참고 / evidence / governance 보드이므로 기본 화면에서는 숨깁니다."
            ),
            "rows": _ROWS,
            "writes_registry": False,
            "writes_saved_setup": False,
            "writes_run_history": False,
            "writes_generated_artifacts": False,
            "storage_boundary": (
                "이 보드는 배치와 의미만 설명합니다. registry, saved setup, run history, generated artifact, "
                "validation result, final decision, monitoring log를 쓰지 않습니다."
            ),
        }
    )


__all__ = ["build_backtest_analysis_research_board"]
