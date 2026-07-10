# Final Review Investment Report Redesign V1 Notes

- 현재 헤더는 `판단 상태`, `Monitoring 후보`, `Handoff Ready`를 중복 또는 기술 용어로 표시한다.
- `Level2 open`은 사용자에게 의미가 불분명하므로 `확인 필요 N개`로 바꾼다.
- `final_decision_input`은 관측값 없이 투자 매력도를 자동 감점해서는 안 된다.
- 투자 매력도는 측정된 performance / risk evidence, 근거 신뢰도는 데이터와 미측정 공백, Monitoring 준비도는 blocker와 추적 조건을 소유한다.
- open REVIEW 개수, gate review-required, blocker는 투자 매력도 cap이 아니라 신뢰도 또는 route constraint로 분리한다.
- REVIEW trace는 관측값, 판단 기준, 근거 source, 기준일, score policy를 제공하고 값이 없으면 `context_only`로 명시한다.
- 첫 화면 본문은 `총평 → 강점과 약점 → 저장 전 확인 질문` 순서로 읽고, Level2 역할별 기술 분류는 후속 근거 섹션에 둔다.
- 저장 전 확인 질문은 최종 판단 기록, 점수 해석, REVIEW 확인, Monitoring 조건의 네 목적을 구분한다.
- 조건부 시나리오는 상관관계와 거시 체제가 변할 수 있다는 전제 아래 표현한다.
- 참고 근거: Federal Reserve의 주식-채권 상관 변화와 인플레이션 유형 연구, NBER의 변동성 관리 연구, BIS의 다요인 stress framework.
- Federal Reserve Clarida speech: 주식-채권 상관은 장기간 고정되지 않고 통화정책 / 인플레이션 체제와 함께 부호가 바뀔 수 있다. https://www.federalreserve.gov/newsevents/speech/clarida20191112a.htm
- Federal Reserve FEDS 2025-002: 인플레이션 민감도는 성장과의 관계에 따라 `good` / `bad` inflation으로 다르게 나타날 수 있다. https://www.federalreserve.gov/econres/feds/good-inflation-bad-inflation-implications-for-risky-asset-prices.htm
- NBER W22208: 변동성 기반 위험 조절은 여러 factor에서 조건부 성과 차이를 보이므로 volatility / tail 패턴을 별도로 본다. https://www.nber.org/papers/w22208
- NBER momentum 연구는 momentum 효과와 경로 의존성을 별도로 다루므로 추세장 결과를 횡보 / 반전 구간으로 일반화하지 않는다. https://www.nber.org/papers/w8734
