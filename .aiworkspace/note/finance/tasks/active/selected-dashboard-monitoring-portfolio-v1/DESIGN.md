# Design

## Read / Write Boundary

- Final Review selected 후보 pool은 `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에서 읽는다.
- 사용자 dashboard portfolio는 `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`에 저장한다.
- delete는 `deleted_at`을 남기는 soft delete로 처리한다.
- Monitoring scenario, drift input, alert preview는 session context로만 유지하며 자동 저장하지 않는다.

## User Flow

1. `나의 포트폴리오`: 생성 / 선택 / 삭제.
2. `포트폴리오 전략 선택`: Final Review 통과 후보를 현재 포트폴리오에 추가 / 제거.
3. `모니터 시나리오`: 각 selected 전략의 가상 기간 / 초기자산 성과 재계산.
4. `Monitoring Signals`: 성과 약화, benchmark 열위, provider stale, trigger breach, drift를 운영 상태로 번역.
5. `전환 비교`: 같은 포트폴리오 안 selected 전략끼리 비교.
6. `근거 / Open Issues`: Final Review 근거와 후속 보강 항목 확인.
7. `Optional Preflight`: Deployment Readiness를 보조 확인으로 유지.

## Implementation Notes

- `app/runtime/final_selected_portfolios.py`에 dashboard portfolio CRUD helper와 read model을 추가한다.
- `app/web/final_selected_portfolio_dashboard.py`는 selected row 직접 선택이 아니라 dashboard portfolio 선택을 먼저 받는다.
- 기존 `build_selected_portfolio_performance_recheck`, drift, review signal, open issue, deployment preflight read model은 재사용한다.
- tests는 저장 모델, duplicate 방지, soft delete, no-live-boundary, selected pool mapping을 확인한다.
