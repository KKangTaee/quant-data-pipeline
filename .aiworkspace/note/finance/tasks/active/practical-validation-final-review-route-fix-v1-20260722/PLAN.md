# Practical Validation Final Review Route Fix V1 Plan

## 이걸 하는 이유?

사용자는 `저장하고 Final Review로 이동` 한 번으로 validation 저장과 다음 단계 이동을 함께 끝낼 것으로 기대한다. 현재는 저장만 완료되고 화면이 남아 반복 클릭과 중복 append를 유도하므로 실제 사용자 workflow가 종결되지 않는다.

## 목표

- 한 번의 클릭이 같은 validation을 최대 한 번만 저장한다.
- 저장 성공 후 root workflow shell이 Final Review stage를 연다.
- 인계한 validation을 Final Review의 현재 active 후보로 연다.

## 잠정 차수

1. fragment intent / full-app rerun 경계 교정
2. validation idempotency / Final Review active 후보 인계
3. 자동 회귀 / 실제 Browser QA / 문서 closeout / commit

## 소유 파일

- `app/web/backtest_practical_validation/page.py`
- 필요 시 Practical Validation persistence runtime helper
- `app/web/backtest_final_review/page.py`
- `tests/test_backtest_practical_validation_decision_workspace.py`
- `tests/test_service_contracts.py` 또는 더 좁은 owning test module
- 이 active task와 finance root handoff docs

## 중단 조건

- 저장 1회와 Final Review 도달을 같은 실제 interaction에서 검증하지 못하면 완료로 처리하지 않는다.
- registry 기존 행을 삭제해야만 통과하는 수정은 채택하지 않는다.
- replay/provider/Gate 의미 변경이 필요해지면 현재 승인 범위를 벗어나므로 사용자에게 다시 알린다.
