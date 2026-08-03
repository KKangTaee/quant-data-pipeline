# Inflation Policy Functional Recovery Status

State: active
Roadmap: 1/5 recovery stages complete
Last Updated: 2026-08-03

## Current

- 사용자 재현 6개 증상과 actual DB 상태를 기준으로 기존 완료 기록을 재감사했다.
- 기존 집중 baseline은 Python 190건, React 11건 통과했지만 actual reverse click과
  production materialization contract를 포함하지 않았음을 확인했다.
- 승인된 복구 설계와 5차 roadmap을 기록했다.
- reverse command result를 payload 저장 전 JSON-safe하게 정규화했다.
- React가 snapshot 전체 상태가 아니라 inflation/policy component별 상태로 확률을
  표시하도록 복구했다.
- actual DB reverse command 결과가 `datetime`을 문자열로 변환하고 JSON 직렬화되는지
  확인했다. joint path 부재로 결과 자체는 정확히 `NOT_AVAILABLE`이다.

## Next

- 2차 Core PCE Q4/Q4 rolling-origin과 공식 benchmark source를 구현한다.
- `next_release_scenarios`를 snapshot serializer에 연결한다.
