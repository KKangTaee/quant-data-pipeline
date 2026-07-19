# Notes

- 현재 구현은 CNN headline, CNN 구성요소, AAII 설문을 세 방향처럼 비교해 CNN을 사실상 두 번 반영한다.
- 현재 AAII 방향 helper는 bearish 비중과 spread를 함께 강하게 제한해 `spread +12pp`도 중립으로 판정할 수 있다.
- CNN 일간, AAII 주간, AAII spread pp를 하나의 공통 y축과 ordinal date index에 표시해 단위와 시간 간격이 왜곡된다.
- 저장 이력은 현재 심리 설명에는 사용할 수 있지만 검증된 1주·1개월 예측을 제공하기에는 부족하다.
- worktree에 있던 다른 미추적 research, `.superpowers/`, QA PNG는 사용자/기존 작업으로 보고 이번 task에서 수정하지 않는다.
- 서비스의 두 축 판정과 설명을 `app/services/overview/sentiment.py`가 소유하고, `sentiment_react_workbench_v2`는 화면 계약만 구성한다.
- React는 source card, 교차 판정, 상세 근거, 그래프 탭, 확인 조건을 표시하며 refresh / reload 요청은 기존 Python dispatch boundary를 유지한다.
- 그래프 x축은 ordinal index가 아니라 관측일 timestamp 비율을 사용해 일간 CNN과 주간 AAII의 실제 시간 간격을 각각 보존한다.
- UI 선택 checkpoint는 카드 밀도, 교차 판정 강조, 그래프 탭 위치를 조정 가능한 축으로 사용자에게 제시했다.
- 독립 리뷰에서 발견한 해석 불일치를 수정했다. AAII 방향·세 응답 결측은 모두 confidence `Review`에 반영하고, CNN 차트 색대역은 서비스 판정의 `25 / 45 / 55 / 75` 경계와 맞춘다.
- CNN·AAII source card에 각 latest/previous 기준일을 표시해 일간 CNN과 주간 AAII가 같은 기준일처럼 보이지 않게 한다.
- 이력 그래프는 서로 다른 시점이 두 개 이상일 때만 그리며 AAII 응답의 Bullish/Neutral/Bearish 세 row를 세 개 시점으로 세지 않는다.
