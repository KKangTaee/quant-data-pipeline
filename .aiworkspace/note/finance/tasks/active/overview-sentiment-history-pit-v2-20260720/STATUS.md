# Status

- 상태: `2차` 구현·실수집·Browser QA 완료
- 전체 roadmap: `2/4차` 완료
- 2차 세부 흐름: 감사, 저장 계약, PIT 이중 저장, 자동 수집, known-at 조회, 장기 그래프, 실제 QA 완료
- 승인 방향: canonical 최신값과 immutable 수집 당시 기록의 이중 저장
- UI 방향: 기본 6M 유지, 공통 `6M / 1Y / 전체`, 실제 coverage와 PIT 시작일을 compact evidence로 표시
- 예측 경계: 충분한 PIT 축적과 chronological validation 전까지 1W·1M 공개 금지
- 구현 계획: `docs/superpowers/plans/2026-07-20-overview-sentiment-history-pit-v2.md`
- 실제 첫 PIT 수집: CNN `2026-07-20 09:17:44 UTC`, AAII `2026-07-20 09:17:45 UTC`; source별 chronological capture는 현재 각 1개
- 다음 작업: `3차` 독립 데이터 후보 검토. 1W·1M은 충분한 PIT 축적 후 `4차` chronological validation을 통과할 때만 공개 여부를 다시 결정
