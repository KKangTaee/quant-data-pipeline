from __future__ import annotations

from typing import Any


def load_overview_ia_closeout_model() -> dict[str, Any]:
    return {
        "schema_version": "overview_ia_closeout_v1",
        "title": "Deep Tab 읽는 순서",
        "detail": "먼저 cockpit에서 요약을 보고, 필요한 owning deep tab으로 들어가 세부 근거를 확인합니다.",
        "sections": [
            {
                "id": "market_context",
                "title": "Market Context",
                "status": "PRIMARY",
                "tone": "primary",
                "owner": "Workspace > Overview",
                "tabs": ["Market Movers", "Sentiment", "Events"],
                "detail": "움직임, sentiment, 가까운 macro / earnings context를 확인하는 구역입니다. Futures / sector evidence는 별도 primary tab이 아니라 Market Context 안의 보조 근거로 읽습니다.",
                "next_step": "cockpit의 다음 확인 카드가 가리키는 탭부터 봅니다.",
            },
            {
                "id": "data_repair",
                "title": "Data Repair",
                "status": "EXTERNAL",
                "tone": "warning",
                "owner": "Workspace > Ingestion > 실행 기록 / 결과",
                "tabs": [],
                "detail": "Overview 최상위 탭에서는 제외하고, Market Context의 자료 기준 / 보강 흐름과 Operations / Ingestion에서 확인합니다.",
                "next_step": "자료 보강이 필요하면 Market Context의 보강 버튼을 먼저 보고, 상세 진단은 Operations 또는 Ingestion에서 확인합니다.",
            },
        ],
        "boundary_note": (
            "Overview Map은 context-only 안내입니다. trading action, Practical Validation PASS/BLOCKER, "
            "Final Review decision, monitoring action, registry row, saved setup row, broker order, auto rebalance를 생성하지 않습니다."
        ),
    }


__all__ = ["load_overview_ia_closeout_model"]
