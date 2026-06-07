# Notes

Status: Active
Last Updated: 2026-06-07

## Findings

- 현재 durable docs에는 필요한 정보가 대부분 들어 있지만, layer boundary와 product-surface boundary가 여러 문서에 흩어져 있다.
- `docs/architecture/README.md`, `docs/data/README.md`, `docs/flows/README.md`가 각각 다른 각도로 경계를 설명하므로 중심 boundary 문서가 필요하다.
- `SELECTED_DASHBOARD_PORTFOLIOS.jsonl` 같은 legacy file / helper name은 유지하되 사용자-facing 설명은 `Operations > Portfolio Monitoring`으로 정리해야 한다.
- `macro_series_observation`은 FRED macro뿐 아니라 CNN / AAII sentiment context series도 담는 현재 상태다.

## Decisions

- 새 장기 기준 문서는 `.aiworkspace/note/finance/docs/architecture/SYSTEM_BOUNDARIES.md`에 둔다.
- `docs/data/`는 저장 의미와 table semantics, `docs/architecture/`는 code ownership과 layer boundary, `docs/flows/`는 사용자 stage 흐름으로 분리해 설명한다.
- `.note/`는 이번 작업에서 보존 / unstaged local legacy artifact로만 둔다.
