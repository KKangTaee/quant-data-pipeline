# Portfolio Monitoring Tracking End Reopen V1 Notes

## Decisions

- 복구는 새 항목 생성이 아니라 동일 항목의 종료 취소다.
- 종료 후 생긴 동일 source 활성 항목 및 활성 10개 한도는 복구 시에도 차단한다.
- 과거 종료 command audit은 유지한다.

## Implementation

- `CommandType.REOPEN_ITEM`과 idempotent `execute_reopen_item`을 추가했다.
- MySQL repository는 종료 필드 세 개를 `NULL`로, status를 `active`로 원상 복구한다.
- Python bridge와 React는 ended item에만 취소 action을 노출한다.
