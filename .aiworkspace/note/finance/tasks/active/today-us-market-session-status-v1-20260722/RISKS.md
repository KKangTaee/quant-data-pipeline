# Today U.S. Market Session Status V1 Risks

- official holiday calendar coverage 부족이나 holiday/early-close loader 비정상 상태는 `일정 자료 부족`으로 fail-closed 처리한다. actual current/next-year row는 확인했다.
- DST 경계는 `ZoneInfo` 기반이며 대표 DST 시나리오 자동 테스트를 통과했다.
- 기존 FOMC next-event query는 변경하지 않고 session calendar를 별도 loader로 읽는다.
- React는 Python이 제공한 UTC schedule만 소비하며 휴일 규칙을 직접 계산하지 않는다.
- `LIMITED` schedule은 합성된 평일 경계를 신뢰하지 않고 `STALE`로 표시해 휴장일에 잘못 `장 진행 중`이라고 단정하는 경로를 막는다.
- 긴급 휴장·거래정지는 official calendar collector가 반영하기 전까지 V1에서 실시간 판정할 수 없다. 이 경계는 의도적으로 남아 있다.
