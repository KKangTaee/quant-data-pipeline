# Final Review Investment Report Redesign V1 Plan

## 이걸 하는 이유?

현재 투자 검토서는 기술적인 상태와 반복되는 판단 label이 상단에 과도하게 노출되고, Level2 REVIEW가 근거가 불분명한 감점처럼 보인다. 사용자는 최종 후보의 투자 매력, 근거 신뢰도, Monitoring 준비 상태를 구분해 이해하고, 어떤 시장 조건에서 강하거나 약할 수 있는지 확인한 뒤 다음 행동을 결정할 수 있어야 한다.

## 개발 차수

1. 외부 `Investment Report` 카드와 중복 상태를 제거하고 상단 헤더를 정리한다.
2. 투자 매력도, 근거 신뢰도, Monitoring 준비도를 분리하고 REVIEW의 자동 감점과 근거 추적 방식을 바로잡는다.
3. 본문을 총평, 강점 / 약점, 확인 질문 중심으로 재구성한다.
4. 저장 evidence로 판단 가능한 보편 패턴 10종과 지원 수준 계약을 정의한다.
5. 규칙 기반 패턴 가이드 프로토타입과 Monitoring 방향 UI를 구현한다.
6. 하단 상세 탭을 정리하고 전체 QA와 문서 동기화를 완료한다.

## 범위

- `app/services/backtest_evidence_read_model.py`
- `app/web/backtest_final_review/page.py`
- `app/web/components/final_review_investment_report/`
- `tests/test_service_contracts.py`
- 관련 finance flow / roadmap / root handoff 문서

## 제외 범위

- Practical Validation 재검증
- provider fetch 또는 DB 수집
- registry / saved JSONL rewrite
- 자유 생성형 투자 조언
- live approval, broker order, auto rebalance

## 완료 조건

- 상단에서 한 번의 판단 상태와 사용자가 이해할 수 있는 확인 필요 수만 보인다.
- 측정되지 않은 REVIEW는 투자 매력도를 자동 감점하지 않고 근거 신뢰도 또는 준비 상태로 분리된다.
- 각 REVIEW 항목에서 관측값, 기준, source, as-of, score effect를 확인할 수 있다.
- 총평, 강점 / 약점, 확인 질문, 조건부 Monitoring 가이드가 일관된 정보 구조로 표시된다.
- 패턴 가이드는 충분 / 참고 / 판단 보류 상태를 명시하며 근거보다 강한 결론을 만들지 않는다.
- focused tests, React build, py_compile, diff check, Browser QA를 통과한다.
