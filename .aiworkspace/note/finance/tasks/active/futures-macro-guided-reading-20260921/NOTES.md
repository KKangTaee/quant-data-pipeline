# 조사와 결정
- 참고 탭: sentiment #f3f6f8 container/white cards, events #f5f7fb/teal accents/category borders, economic cycle phase tints/condition-met·unmet badges. 색만으로 상태를 구분하지 않고 판정 텍스트 동반.
- 기존 reading은 pressure/relief 이외 조합이 generic fallback. 데이터가 유효한 혼합 조합에도 무엇이 엇갈리는지 설명해야 한다.
- 금융 의미 1차 source: https://www.cmegroup.com/trading/interest-rates/basics-of-us-treasury-futures.html (가격·수익률 역관계), https://www.cmegroup.com/trading/why-futures/welcome-to-cme-fx-futures.html (FX futures 계약).
- 자체 달러 대용지표와 주식 부담/완화 문장은 앱의 설명 규칙이며 검증된 미래 수익 예측 모델로 표시하지 않는다.
- 사용자 요청이 변경 범위와 목적을 명시하므로 추가 승인으로 중단하지 않고 bounded 개선으로 실행.
- 이전 비교는 현재 알려진 raw 이력으로 동일 정의의 과거 구간을 재계산한다. 그 당시 사용자가 본 immutable 판정을 재생하거나 수집 당시 가용성을 보장하는 PIT 백테스트가 아니다.
- 비교 범주가 같더라도 ES/NQ 방향이 뒤집히거나 보합인 지수가 바뀌면 CHANGED로 표시한다. 같은 조합은 범주와 자산별 부호가 모두 일치해야 한다.
- 0.01% 부호는 영향 크기와 다르다는 문구를 확인 카드 아래에도 표시. 현재의 혼합 조합을 확정 방향으로 축약하지 않고 실제 두 축 설명으로 제공.
- 문서 정렬: flows/README, PROJECT_MAP, PRODUCT_DIRECTION, ROADMAP의 next-check 약속을 실제 판정/관측 비교로 수정. 기존 runbook의 옛 1D/5D/20D primary UI·reload 설명도 현행으로 교정. INDEX/discovery와 DB 소유 경계 변경 없음.
