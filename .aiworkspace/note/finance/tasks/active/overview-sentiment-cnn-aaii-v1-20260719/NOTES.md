# Notes

- 현재 구현은 CNN headline, CNN 구성요소, AAII 설문을 세 방향처럼 비교해 CNN을 사실상 두 번 반영한다.
- 현재 AAII 방향 helper는 bearish 비중과 spread를 함께 강하게 제한해 `spread +12pp`도 중립으로 판정할 수 있다.
- CNN 일간, AAII 주간, AAII spread pp를 하나의 공통 y축과 ordinal date index에 표시해 단위와 시간 간격이 왜곡된다.
- 저장 이력은 현재 심리 설명에는 사용할 수 있지만 검증된 1주·1개월 예측을 제공하기에는 부족하다.
- worktree에 있던 다른 미추적 research, `.superpowers/`, QA PNG는 사용자/기존 작업으로 보고 이번 task에서 수정하지 않는다.
