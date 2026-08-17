# Design

가격 proxy 계산식과 covered-sleeve coverage는 유지한다. 이미 계산된 row를 contribution sign으로 필터해 contributor/detractor 목록만 분리한다.

Popularity read model에는 원본 `total_reported_value`와 별도로 달러 표시 label을 추가한다. Workbench disclosure는 기존 영어 source caveat 상수를 바꾸지 않고, 한국어 사용자용 payload를 별도 상수에서 projection한다.

승인된 UI 변경 세 가지는 (1) 양·음 기여 분리, (2) 보고가액 의미 명시, (3) 한국어 13F 주의사항이다.
