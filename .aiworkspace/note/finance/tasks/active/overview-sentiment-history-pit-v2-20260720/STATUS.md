# Status

- 상태: `2차` 구현·실수집 완료, 시작점 정렬·source별 최신값 노출 후속 완료, 최신 Browser QA는 URL policy로 미실행
- 전체 roadmap: `2/4차` 완료
- 2차 세부 흐름: 감사, 저장 계약, PIT 이중 저장, 자동 수집, known-at 조회, 장기 그래프, 실제 QA 완료
- 승인 방향: canonical 최신값과 immutable 수집 당시 기록의 이중 저장
- UI 방향: 기본 6M 유지, `6M / 1Y / 전체`가 CNN·AAII의 늦은 시작일을 공통 시작점으로 사용하고 x축 종료는 두 source 중 최신 날짜까지 확장한다. 각 선은 자기 source의 마지막 관측일에서 끝나며 보간하지 않는다.
- 예측 경계: 충분한 PIT 축적과 chronological validation 전까지 1W·1M 공개 금지
- 구현 계획: `docs/superpowers/plans/2026-07-20-overview-sentiment-history-pit-v2.md`
- 실제 첫 PIT 수집: CNN `2026-07-20 09:17:44 UTC`, AAII `2026-07-20 09:17:45 UTC`; source별 chronological capture는 현재 각 1개
- AAII canonical 보강: 공식 workbook `1987-07-24~2026-07-16`, 네 series 각 `2,032`주. CNN canonical은 `2025-06-04~2026-07-20`; 현재 정렬 x-domain은 `2025-06-04~2026-07-20`이고 AAII 선은 `2026-07-16`에서 끝난다.
- 다음 작업: `3차` 독립 데이터 후보 검토. 1W·1M은 충분한 PIT 축적 후 `4차` chronological validation을 통과할 때만 공개 여부를 다시 결정
