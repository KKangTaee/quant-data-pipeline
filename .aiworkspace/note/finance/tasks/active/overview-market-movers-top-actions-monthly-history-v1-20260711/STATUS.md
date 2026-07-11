# Status

- 2026-07-11: 사용자 요청과 잠정 1~4차 범위를 정렬했다.
- 2026-07-11: S&P 500 Monthly 갱신 후 반복되는 대상은 FDXF/HONA로 확인했다.
- 2026-07-11: DB와 provider 1y probe 모두 FDXF 31 rows, HONA 1 row를 반환해 재수집 실패가 아니라 가용 이력이 짧은 상태임을 확인했다.
- 2026-07-11: 상단 action을 짧은 버튼과 외부 한 줄 설명으로 분리했다.
- 2026-07-11: full-window 수집 후에도 짧은 symbol은 `limited_price_history`로 기록하고 이후 같은 수집 action에서 제외하도록 구현했다.
- 2026-07-11: FDXF/HONA issue 2건을 backfill하고 Monthly 화면에서 `계산 가능 · 짧은 이력 제외`, 추가 수집 없음 상태를 확인했다.
- 상태: Complete. 잠정 1~4차 완료.
- 다음 작업: 없음. 이후 row count가 period threshold를 충족하면 기존 정상 계산 경로가 자동으로 우선한다.
