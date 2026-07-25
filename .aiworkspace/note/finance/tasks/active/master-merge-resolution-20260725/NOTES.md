# Master Merge Resolution 2026-07-25 Notes

## Decisions

- Incoming `master` merge commit 시각이 현재 branch HEAD보다 늦으므로 같은 날짜 root log는
  incoming 완료 기록을 먼저 읽도록 정렬했다.
- Market Research Header System은 Editorial Navigation을 대체하지 않고 그 위에 쌓인 최신
  module-header 계약이므로 INDEX에서 latest/previous로 구분했다.
- Project Map은 incoming의 common header 소유권과 current branch의 DB-only freshness
  service 소유권이 독립적이므로 둘 다 보존했다.
- Economic Cycle의 `.cycle-hero`와 broad mobile `h2` override는 incoming 공통
  `ResearchHeader` DOM에서 더 이상 정확한 owner가 아니므로 제거했다. 수동 최신화 bar와
  action selector는 현재 DOM에서 사용되므로 유지했다.
- 최초 Browser QA의 `localhost:8501`은 `sub-dev` cwd에서 실행 중인 별도 Streamlit
  프로세스였다. main-dev source의 headline은 정상임을 Python에서 확인하고, main-dev
  전용 `8511` 프로세스로 actual QA를 다시 수행했다. 제품 코드 수정은 필요하지 않았다.

## Unrelated Local State

- `.aiworkspace/note/finance/run_history/*.jsonl`
- `.aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl`
- `.superpowers/`
- repository root의 QA PNG/JPG

위 항목은 이번 merge stage/commit에서 제외한다.
