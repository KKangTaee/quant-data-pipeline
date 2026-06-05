# Overview Market Sentiment V1 Status

- 2026-06-05: 분석 완료. Overview 새 Sentiment 탭 + existing `macro_series_observation` 공유 방식을 user-approved 1차 범위로 확정.
- 2026-06-05: 구현 시작. TDD로 collector / ingestion job / Overview read model을 먼저 검증한다.
- 2026-06-05: 1차 구현 완료. CNN / AAII 수집, `macro_series_observation` UPSERT, Ingestion job, Overview Sentiment tab, Data Health target, Browser QA를 완료했다.
- 2026-06-05: 실제 수집 smoke 성공. CNN 260 rows, AAII 88 rows, 총 348 rows 저장; service snapshot은 `OK`, CNN 54.7 / AAII bearish 37.0% / bull-bear spread -0.7pp.
- 2026-06-05: 사용자 리뷰 후속 UX 개선 완료. Sentiment 탭 상단에 혼합 중립 / 데이터 신뢰도 / 단계별 분석 체크 / CNN 드라이버 분해 / 다음 확인 경로를 추가해 단순 prototype card 노출을 해석 중심 workflow로 바꿨다.
