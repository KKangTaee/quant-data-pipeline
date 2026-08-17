# Futures Macro Repricing Radar V1 Risks

- continuous futures는 실제 만기곡선·carry를 표현하지 않으므로 미래 기대를 직접 예측한다고 설명할 수 없다.
- family 간 구성 종목이 겹치므로 confirmation을 독립 표본처럼 세면 신뢰도를 과장한다.
- 가장 강한 family 기반 해석은 유력 가설이지 인과 판정이 아니다.
- forecast backend를 보존하므로 향후 코드 작업자가 숨겨진 artifact를 다시 primary UI에 연결하지 않도록 durable flow 문서에 경계를 남긴다.
- 전체 `tests/test_service_contracts.py`는 이번 변경과 무관한 `PracticalValidationServiceContractTests.test_market_sentiment_overlay_is_context_only_for_practical_validation`의 기존 기대값 불일치(`OK` vs `REVIEW`)로 green이 아니다. Futures Macro 관련 회귀와 source contract는 별도 green이다.
