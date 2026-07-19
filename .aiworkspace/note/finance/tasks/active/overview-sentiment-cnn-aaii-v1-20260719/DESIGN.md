# Design

- CNN은 시장 행동 심리, AAII는 개인투자자 인식 심리로 분리한다.
- 두 source의 점수를 합성하지 않고 방향과 문장형 교차 판정만 만든다.
- CNN 구성요소는 별도 투표가 아니라 CNN headline의 내부 근거와 확신도로 사용한다.
- AAII 방향은 Bull-Bear Spread `+10pp / -10pp` 경계를 사용하고 세 응답의 장기평균 차이는 설명 근거로 사용한다.
- React payload를 v2 두 축 계약으로 정리하고 기존 refresh/reload Python dispatch boundary는 유지한다.
- CNN 0~100, AAII 응답 0~100%, AAII Spread pp를 실제 날짜 간격의 별도 그래프로 표시한다.
- 원본 row와 갱신 세부는 접힌 상세 근거로 내리고 첫 화면은 현재 판단과 확인 조건에 집중한다.

Authoritative spec: `docs/superpowers/specs/2026-07-19-overview-sentiment-cnn-aaii-v1-design.md`
