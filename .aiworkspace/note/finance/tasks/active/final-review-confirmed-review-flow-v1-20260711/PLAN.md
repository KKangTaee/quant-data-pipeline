# Final Review Confirmed Review Flow V1 Plan

## 이걸 하는 이유?

Final Review의 후보 selectbox는 표시 label을 identity로 사용하고, 선택 즉시 저장된 Practical Validation evidence를 다시 조합해 투자 검토서와 판단 영역을 렌더링한다. label 중복 시 다른 후보를 잡을 수 있고, 빠른 후보 전환은 검토서를 새로 검증한 결과처럼 오해하게 하거나 이전 검토서가 남은 듯한 UX를 만든다. 또한 Level2 REVIEW가 감점과 상세 탭에 묻혀 사용자가 Final Review에서 무엇을 확인하고 어디로 넘겨야 하는지 빠르게 알기 어렵다.

## 개발 차수

1. stable key 기반 후보 선택으로 바꾸고 visible Review Queue를 제거한다.
2. `최종 검토서 확인` 버튼으로 후보 확정 경계를 만들고 선택 변경 시 stale 안내를 표시한다.
3. Level2 REVIEW를 다섯 역할과 행동 결과가 드러나는 `Final Review 확인 필요` 섹션으로 바꾼다.
4. focused tests, React build, py_compile, diff check, Browser QA를 수행하고 문서를 동기화한다.

## 범위

- `app/web/backtest_final_review/page.py`
- `app/services/backtest_evidence_read_model.py`
- `app/web/components/final_review_investment_report/`
- `tests/test_service_contracts.py`
- 관련 finance flow / roadmap / root handoff 문서

## 제외 범위

- Practical Validation 재검증
- provider fetch 또는 DB 수집
- gate threshold / 저장 schema / registry rewrite
- live approval, broker order, auto rebalance

## 완료 조건

- label 중복과 무관하게 stable key로 정확한 후보를 선택한다.
- 확인 버튼 전에는 투자 검토서, Decision Cockpit, Final Decision Action을 렌더링하지 않는다.
- 선택 변경 후 이전 확정 후보 화면을 숨기고 stale 안내를 표시한다.
- Level2 REVIEW의 역할과 `점수 반영 / 저장 전 확인 / Monitoring 이관 / blocker` 행동이 명시된다.
- 요청된 자동 / Browser QA를 통과하고 generated artifact를 commit하지 않는다.
