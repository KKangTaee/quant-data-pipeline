# Today U.S. Market Session Status V1 Risks

- official holiday calendar coverage가 없으면 평일 휴장을 확정할 수 없다. UI에서 calendar quality를 명시해야 한다.
- 고정 UTC offset을 사용하면 DST 전환기에 KST 시각이 틀린다. `ZoneInfo` 기반 경계만 사용한다.
- 기존 FOMC next-event query를 broad query로 바꾸면 Today의 다음 일정 의미가 바뀔 수 있다. session calendar는 별도 경계로 읽는다.
- React가 휴일 규칙을 직접 계산하면 Python/DB와 의미가 갈라진다. React는 제공된 UTC schedule만 소비한다.
- 긴급 휴장·거래정지는 official calendar collector가 반영하기 전까지 V1에서 실시간 판정할 수 없다.
