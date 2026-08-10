# Inflation Policy Workbench Design

State: approved
Last Updated: 2026-08-02

## User Flow

```text
물가·정책 경로 선택
  -> 현재 결론과 다음 Core PCE 조건
  -> 연말 Core PCE 5상태·중요 수준
  -> 다음 회의·연말 정책 경로
  -> 10년물 자동/사용자 저항 기준과 주도 요인
  -> 목표 구간 선택·사용자 기준 저장
  -> 검증된 joint path가 있을 때만 조건부 역산 결과
  -> 근거·신선도·과거 기준 확인
```

## Ownership

- `finance/loaders/inflation_policy.py`: 저장 snapshot, 기준, exact artifact의 DB-only PIT 조회
- `app/services/overview/inflation_policy.py`: snapshot을 JSON-safe UI read model로 투영
- `app/services/overview/inflation_policy_commands.py`: USER 기준 저장과 bounded reverse 실행
- `app/web/overview/market_context_helpers.py`: 독립 payload 합성과 once-only command bridge
- `economic_cycle_workbench`: 내부 선택기, 순방향/역산 입력·표시만 소유

React는 확률을 계산하거나 DB에 쓰지 않는다. Python Overview service는 provider나
기존 경제 사이클 service를 호출하지 않는다.

## Safety Contract

- 전체 publication이 `READY`가 아니면 숫자 확률을 현재 확정치처럼 표시하지 않는다.
- 실제 reverse snapshot이 `NOT_AVAILABLE`이면 추정 숫자 대신 저장된 이유를 표시한다.
- AUTO 기준은 읽기 전용이며 USER 기준으로 복사한 뒤에만 저장한다.
- 10년물 변화와 인상 횟수의 25bp 기계적 매핑을 만들지 않는다.
- 주식 스트레스와 침체는 각각 4차·5차 전까지 `NOT_AVAILABLE`로 유지한다.
