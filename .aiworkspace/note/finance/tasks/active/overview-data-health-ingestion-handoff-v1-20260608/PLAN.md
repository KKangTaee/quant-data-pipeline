# Overview Data Health Ingestion Handoff V1 Plan

Status: Active
Created: 2026-06-08

## 이걸 하는 이유?

1차 Cockpit은 Overview 첫 화면에서 macro / market context를 요약했다.
2차는 그 요약과 Data Health가 보여주는 stale / due / partial / missing / failed 상태를 실제 사용자가 다음에 확인할 Ingestion 위치로 이어준다.

## 전체 흐름

| 차수 | 목적 | 완료 조건 |
| --- | --- | --- |
| 1차 | Overview Macro Context Cockpit V1 | 기존 DB-backed context 요약 band 완료 |
| 2차 | Data Health -> Ingestion Handoff V1 | 우선순위 data-health item과 정확한 Ingestion/Overview 수집 위치를 read-only로 안내 |
| 3차 | Breadth / Events visual expansion | heatmap / macro week view 후보 중 승인 범위 구현 |
| 4차 | Source / provider hardening | source confidence catalog 또는 futures provider policy 정리 |
| 5차 | Overview IA closeout | Candidate Ops 등 후속 IA 후보를 승인 기반으로 정리 |

## 2차 Scope

- `build_collection_ops_snapshot` 결과에서 handoff read model을 만든다.
- Data Health 탭 상단에 priority-ranked handoff lane을 표시한다.
- 각 row는 status, freshness, reason, next action, target surface, source boundary를 드러낸다.
- Overview는 collection job 실행 소유자가 아니며, 기존 action facade / Ingestion surface만 안내한다.

## Out Of Scope

- 새 provider / DB schema / registry / saved JSONL write.
- Overview render 중 external provider / FRED / crawler direct fetch.
- 실제 Ingestion Action Queue persistence, prefill, background execution.
- Market breadth heatmap, macro week view, Candidate Ops IA 변경.
- Practical Validation PASS/BLOCKER, Final Review decision, monitoring signal, trading action.

## Verification Plan

- focused service contract tests with RED/GREEN.
- related `py_compile`.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`.
- `git diff --check`.
- Streamlit Browser QA screenshot.
