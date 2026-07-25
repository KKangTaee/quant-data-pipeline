# Notes

- 2026-06-17 HTML `-2.8pp`와 2026-06-18 XLS `-2.7778pp`는 동일 주차다.
- 2026-07-08 HTML `-0.9pp`와 2026-07-09 XLS `-0.9302pp`도 동일 주차다.
- 공식 workbook 최근 날짜는 2026-06-04~2026-07-23 구간에서 모두 7일 간격이다.
- React chart는 canonical history rows를 그대로 전달하므로 DB 중복이 화면에 그대로 나타난다.
- 사용자 승인 범위는 기존 중복 정리와 동일 주차 정규화 회귀 방지다.
- 예방 로직은 네 AAII series가 동일한 날짜 집합을 가진 complete XLS capture일 때만 실행한다.
- 독립 리뷰 뒤 outer source/status/coverage, official source type/workbook provenance, ISO date와 연속 7일 cadence까지 삭제 권한 gate에 포함했다. 중간 주차가 함께 누락된 XLS-shaped capture는 canonical cleanup을 실행하지 않는다.
- Canonical cleanup은 immutable snapshot과 batch를 삭제하지 않는다. 발표 당시 재현/known-at read 경계는 그대로다.
- 실제 cleanup 뒤 canonical은 official workbook `1987-07-24~2026-07-23`, `2,033주 / 8,132행`이다.
