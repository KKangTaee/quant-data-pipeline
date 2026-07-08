# Status

Status: Completed
Date: 2026-07-09

## Completed

- 1차: AGENTS / finance docs read order와 최근 Practical Validation task context를 확인하고 active task 문서를 만들었다.
- 2차: `app/services/backtest_practical_validation_workspace.py`에 표시 전용 `data_action_board` read model을 추가했다. `immediate_collect`, `source_map_discovery`, `connector_needed`, `no_action`으로 분류하며 Final Review / Monitoring label은 PV 보강 보드에서 제외한다.
- 3차: `app/web/components/practical_validation_data_action_board/` React component를 추가했다. React는 props 렌더링만 맡고 provider/FRED/API/DB fetch, validation calculation, collection execution, registry/saved write는 하지 않는다.
- 4차: `app/web/backtest_practical_validation/page.py`에서 visible `단계별 검증 소유권` expander와 `수집 대상 근거` expander를 제거하고, evidence appendix를 `상세 근거 / 원자료`로 낮췄다.
- 5차: tests / compile / diff check / Browser QA / durable docs sync를 완료했다.

## Handoff

- 최신 Flow 4 visible order는 `카테고리별 검증 결과 -> 데이터 보강 대상 / 액션 -> 상세 근거 / 원자료`다.
- 기존 Python Provider / Data 보강 액션이 수집 실행 경계를 계속 소유한다.
- Generated screenshot과 run history artifact는 commit 대상이 아니다.
