# Backtest Policy Signal Gate V7-V11

Status: Active
Started: 2026-07-03

## 이걸 하는 이유?

Backtest Analysis의 `검증 신호 · Policy Signals` 영역은 2차 Practical Validation 진입 판단, 승격 판단, 실행 부담, 기술 상세를 한 화면에 섞어 보여준다. 사용자는 어떤 항목이 버튼을 막는지, 어떤 항목은 2차에서 확인하면 되는지 구분하기 어렵다.

이번 작업은 Backtest 결과 화면에서 2차 진입 게이트와 설명용 근거를 분리하고, Practical Validation으로 넘어갈 때 필요한 source snapshot을 더 명확하게 보존한다.

## 단계

| 단계 | 목적 | 완료 조건 |
|---|---|---|
| V7 | Policy Signal 분류 read-model 추가 | blocker / review / context rows를 Streamlit-free service에서 반환하고 테스트한다 |
| V8 | 2차 진입 게이트와 실전 승격 판단 분리 | Practical Validation entry gate가 promotion hold에 과도하게 묶이지 않도록 정책을 정리한다 |
| V9 | Policy Signal UI 축소 | nested tab UI를 compact evidence + expander 구조로 바꾼다 |
| V10 | Practical Validation source/handoff 문맥 정렬 | source snapshot에 entry gate와 review focus가 재사용 가능하게 남는다 |
| V11 | 문서 / 브라우저 QA / closeout | durable docs와 root handoff log를 최소 범위로 정렬하고 QA evidence를 남긴다 |

## 범위

- 포함: `app/services/backtest_handoff_readiness.py`, `app/web/backtest_result_display.py`, candidate handoff snapshot, 관련 tests, Backtest UI flow docs.
- 제외: strategy runtime 계산식 변경, DB schema 변경, provider 수집 경로 변경, registry / saved JSONL 재작성.
