# Risks

- Streamlit session state에 legacy label `Compare & Portfolio Builder` 또는 `전략 비교`가 남아 있을 수 있으므로 normalize가 필요하다.
- Saved mix replay와 current mix handoff가 서로 다른 기준을 쓰면 사용자가 같은 mix를 다르게 해석할 수 있다.
- 개별 전략 비교 상세를 완전히 제거하면 weight를 정하기 위한 참고 근거가 부족하므로, 상세 table/chart는 유지하되 handoff action만 mix 기준으로 낮춰야 한다.
- 남은 제품 리스크: 후보 간 read-only 비교 도구는 아직 별도 구현하지 않았다. 현재 작업은 mix 생성 흐름을 명확히 한 1차 정리이며, "통과 후보끼리 비교"는 후속 Candidate Comparison 기능으로 분리하는 편이 안전하다.
