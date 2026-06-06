# Overview Market Sentiment V1 Status

- 2026-06-05: 분석 완료. Overview 새 Sentiment 탭 + existing `macro_series_observation` 공유 방식을 user-approved 1차 범위로 확정.
- 2026-06-05: 구현 시작. TDD로 collector / ingestion job / Overview read model을 먼저 검증한다.
- 2026-06-05: 1차 구현 완료. CNN / AAII 수집, `macro_series_observation` UPSERT, Ingestion job, Overview Sentiment tab, Data Health target, Browser QA를 완료했다.
- 2026-06-05: 실제 수집 smoke 성공. CNN 260 rows, AAII 88 rows, 총 348 rows 저장; service snapshot은 `OK`, CNN 54.7 / AAII bearish 37.0% / bull-bear spread -0.7pp.
- 2026-06-05: 사용자 리뷰 후속 UX 개선 완료. Sentiment 탭 상단에 혼합 중립 / 데이터 신뢰도 / 단계별 분석 체크 / CNN 드라이버 분해 / 다음 확인 경로를 추가해 단순 prototype card 노출을 해석 중심 workflow로 바꿨다.
- 2026-06-05: 사용자 학습 UX 후속 완료. 6단계를 `지금 결론 / 왜 이렇게 보나 / 강한 신호 / 약한 신호 / 그래서 어떻게 보나 / 다음 확인`으로 재구성하고, CNN 7개 구성요소를 `보는 것 / 현재 읽기` 카드로 노출했다.
- 2026-06-06: 2차 구현 완료. `Backtest > Practical Validation`에 CNN / AAII 시장 심리 context overlay read model과 UI band를 추가하고, context-only / no-gate / no-registry-write boundary를 명시했다. Focused RED/GREEN, 전체 service contracts, py_compile, git diff check, Browser QA를 완료했다.
- 2026-06-07: 3차 구현 완료. 같은 DB-backed CNN / AAII market sentiment overlay를 `Backtest > Final Review` Decision Desk 아래와 `Operations > Portfolio Monitoring` 진입부에 read-only market backdrop으로 연결했다. selected-route gate, monitoring signal, saved setup, registry, live approval / order / auto rebalance 경계는 유지한다. Focused RED/GREEN, 전체 service contracts, py_compile, git diff check, Browser QA를 완료했다.
