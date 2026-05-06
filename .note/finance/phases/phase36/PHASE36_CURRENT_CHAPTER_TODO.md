# Phase 36 Current Chapter TODO

## 진행 상태

- `implementation_complete`

## 검증 상태

- `manual_qa_pending`

## 현재 목표

Phase36의 첫 목표는 Final Review에서 선정된 포트폴리오를 Operations 화면에서 다시 읽는 것이다.

```text
Backtest > Final Review
  -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl
  -> Operations > Selected Portfolio Dashboard
```

이 대시보드는 read-only다.
새 final decision row, 새 proposal row, 주문 row를 만들지 않는다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase36 전체 목표 | 최종 선정 포트폴리오 운영 대시보드 시작 | `implementation_complete` |
| 첫 번째 작업 | selected final decision row read model / Operations page 구현 | `completed` |
| 두 번째 작업 | current weight 수동 입력 기반 drift 계약 정리 | `completed` |
| 세 번째 작업 | drift / rebalance_needed read-only 자동 판단 | `completed` |
| 네 번째 작업 | current value / shares x price 기반 current weight 입력 계약 추가 | `completed` |
| 문서 / QA | phase 문서, roadmap, code analysis, checklist 동기화 | `completed` |

## 완료한 내용

- Phase36 문서 bundle을 만들었다.
- `app/web/runtime/final_selected_portfolios.py`를 추가해 Final Review selected decision row를 dashboard row로 변환한다.
- `app/web/final_selected_portfolio_dashboard.py`를 추가해 `Operations > Selected Portfolio Dashboard`를 렌더링한다.
- `app/web/final_selected_portfolio_dashboard_helpers.py`를 추가해 table / component / evidence display helper를 분리했다.
- `app/web/streamlit_app.py`의 Operations navigation에 `Selected Portfolio Dashboard` page를 추가했다.
- dashboard는 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이 없거나 selected row가 없어도 empty state로 처리한다.
- dashboard는 `normal`, `watch`, `rebalance_needed`, `re_review_needed`, `blocked` status 체계를 가진다.
- `Current Weight / Drift Check`를 추가해 component별 현재 비중을 수동 입력하고 target weight와의 drift를 계산한다.
- drift threshold 이상이면 `REBALANCE_NEEDED`, watch threshold 이상이면 `DRIFT_WATCH`, 입력 합계가 100% 근처가 아니면 `DRIFT_INPUT_INCOMPLETE`로 read-only 판정한다.
- current value 입력을 추가해 component별 평가금액과 cash / outside value로 현재 비중을 계산한다.
- shares x price 입력을 추가해 보유 수량과 현재가로 현재 비중을 계산한다.
- shares x price 입력에서는 선택적으로 DB latest close를 불러와 현재가 입력을 보조한다.
- 이 drift check는 실제 account holding 자동 연결 없이 operator 입력값으로 동작한다.

## 중요한 경계

- Phase36은 Final Review 뒤에 또 다른 저장 결정을 만들지 않는다.
- `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`은 Final Review의 최종 판단 원본이다.
- Phase36은 이 파일 중 `SELECT_FOR_PRACTICAL_PORTFOLIO` row만 운영 대상으로 읽는다.
- live approval, broker order, 자동매매 버튼은 disabled로 유지한다.
- DB latest close는 입력 보조 기능으로만 쓰며, account holding 자동 연결, 주문 초안은 이번 phase 범위 밖이다.

## 검증 TODO

- `completed` phase kickoff plan 작성
- `completed` selected portfolio dashboard code 구현
- `completed` roadmap / doc index / code analysis sync
- `completed` py_compile
- `completed` runtime helper smoke
- `completed` hygiene helper
- `completed` drift helper smoke
- `completed` value / holding input helper smoke
- `pending` user manual QA

## 현재 판단

Phase36 구현은 implementation_complete / manual_qa_pending 상태다.
사용자는 `PHASE36_TEST_CHECKLIST.md` 기준으로 `Operations > Selected Portfolio Dashboard`를 확인하면 된다.
