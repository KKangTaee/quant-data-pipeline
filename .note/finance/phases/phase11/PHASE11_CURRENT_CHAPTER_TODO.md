# Phase 11 Current Chapter TODO

## 상태 기준

- `pending`
- `in_progress`
- `completed`

## 1. Chapter Setup

- `completed` Phase 11 활성화
  - Phase 10 practical closeout 이후 실제 active phase로 전환
- `completed` productization 우선순위 재확인
  - validation contract hardening은 Phase 10에 남기고,
    Phase 11은 workflow/productization에 집중
- `completed` first-pass 시작점 고정
  - `saved portfolio contract + load/rerun workflow`를 첫 구현 범위로 선택

## 2. Saved Portfolio Model

- `completed` saved portfolio persistence contract first pass
  - `compare_context`
  - `portfolio_context`
  - `source_context`
- `completed` saved portfolio store 추가
  - `.note/finance/saved/SAVED_PORTFOLIOS.jsonl`
  - `app/web/runtime/portfolio_store.py`
- `completed` create / load / delete 기본 CRUD

## 3. Compare-To-Portfolio Bridge

- `completed` current compare + weighted result -> saved portfolio 저장
- `completed` saved portfolio -> compare prefill bridge
- `completed` saved portfolio -> end-to-end rerun bridge
- `pending` focused drilldown -> save direct bridge
  - current first-pass closeout 범위 밖 backlog로 남긴다

## 4. Portfolio UX First Pass

- `completed` saved portfolio list / detail surface
- `completed` `Load Into Compare` / `Run Saved Portfolio` / `Delete` action
- `completed` weighted portfolio `Meta` 탭 추가
- `pending` in-place edit / overwrite UX
  - later polish backlog

## 5. Richer Portfolio Readouts

- `completed` weighted portfolio meta/context surface 보강
- `completed` contribution summary에 configured vs normalized weight 동시 노출
- `pending` strategy-level exposure summary
- `pending` rebalance-level change summary
- `pending` benchmark / drawdown portfolio readout 강화
  - current first-pass closeout 이후 backlog

## 6. Workflow Surface

- `completed` saved portfolio와 history run 연결 정보 저장
  - `saved_portfolio_id`
  - `saved_portfolio_name`
- `completed` saved portfolio first-pass 구현 요약 문서 작성
- `pending` saved run / saved portfolio 역할 차이 문구 polish
  - later wording backlog

## 7. Documentation And Validation

- `completed` first-pass 구현 요약 문서 추가
  - `PHASE11_SAVED_PORTFOLIO_FIRST_PASS.md`
- `completed` Phase 11 checklist refresh
- `completed` roadmap / index / logs sync
- `completed` practical closeout 문서 작성
  - `PHASE11_COMPLETION_SUMMARY.md`
  - `PHASE11_NEXT_PHASE_PREPARATION.md`

## 현재 메모

- Phase 11 first pass는 practical closeout 처리한다.
- 이번 phase의 핵심 목표였던
  “weighted portfolio를 저장 가능한 workflow object로 승격하는 것”
  은 달성되었다.
- 남은 항목은 여전히 가치가 있지만,
  current phase closeout blocker는 아니며 later backlog로 남긴다.
- active phase는 이제 `Phase 12 real-money strategy promotion`으로 넘어간다.
