# Portfolio Monitoring Tracking End Reopen V1 Design

Status: Approved
Date: 2026-07-19

## 이걸 하는 이유?

종료된 추적 항목은 현재 화면에서 과거 기록으로만 남고 다시 활성화할 방법이 없다. 사용자가 실수로 종료했거나 같은 계약을 계속 관찰하려는 경우, 새 항목을 중복 등록하지 않고 기존 추적 종료 자체를 취소할 수 있어야 한다.

## 승인된 방식: A — 추적 종료 취소

- 동일한 `monitoring_item_id`를 유지한다.
- 원래 요청/유효 시작일, 투자 방식, 투자금액/정수 수량, 진입 종가, 초기 자본을 유지한다.
- `tracking_end_requested_date`, `tracking_end_effective_date`, `exit_value`를 비운다.
- 상태를 `active`로 되돌린다.
- 화면과 계산은 원래 시작일부터 종료 없이 계속 보유한 것으로 다시 투영한다.
- 과거 `end_item` 명령은 command audit에 남지만 현재 항목의 종료 상태와 종료금액은 취소된다.

## 사용자 흐름

1. 사용자가 `추적 종료 종목` 목록에서 항목을 선택한다.
2. 선택 상세 하단의 `추적 종료 취소`를 누른다.
3. 종료 상태와 종료금액이 취소되고 전체 구간이 연속 추적으로 다시 계산된다는 확인 문구를 본다.
4. 성공 시 항목은 동일 ID로 `추적 중 종목`에 이동하고 기존 시작일 기준 지표와 그래프를 다시 보여준다.

## 명령 및 무결성

- 새 idempotent command/event: `reopen_item`.
- 종료 상태인 항목만 취소할 수 있다.
- 복구 시 그룹의 활성 항목 최대 10개 제한을 다시 검증한다.
- 종료 후 같은 source가 새 활성 항목으로 등록되었다면 중복 활성화를 막는다.
- DB schema는 바꾸지 않고 기존 nullable 종료 필드를 원상 복구한다.

## 완료 조건

- command/repository/page dispatch/UI 계약 테스트가 종료 취소 흐름을 고정한다.
- 종료된 동일 항목이 활성 상태로 복구되고 종료 필드가 모두 비워진다.
- 활성 10개 제한과 동일 source 중복 제한이 유지된다.
- React 화면에서 종료 항목에만 `추적 종료 취소`가 표시되고 확인 후 명령을 보낸다.
- Python 테스트, React 테스트/typecheck/build, 정적 asset 검증을 통과한다.

