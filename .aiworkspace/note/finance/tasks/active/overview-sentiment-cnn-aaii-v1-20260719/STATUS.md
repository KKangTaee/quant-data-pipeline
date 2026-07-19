# Status

- 상태: 전체 잠정 로드맵 `1/4차` 구현·QA 완료, 실제 UI 선택 checkpoint 제시
- 완료 범위: 합성점수 없는 CNN 시장 행동 / AAII 투자자 인식 두 축, 문장형 교차 판정, source별 상세 근거, 세 단위별 이력 그래프, 예측이 아닌 확인 조건
- 판정 계약: AAII Bull-Bear Spread `>= +10pp`는 낙관, `<= -10pp`는 비관, 그 사이는 중립이며 결측은 판단 불가다. CNN 구성요소는 CNN headline 내부 근거로만 사용한다.
- UI 계약: 동등한 두 source card 뒤에 교차 판정을 두고, CNN 구성요소와 AAII 장기평균 비교를 한 번씩만 표시한다. CNN 0~100 일간, AAII 응답률 주간, AAII spread pp 주간 그래프를 분리한다.
- 검증: focused sentiment unittest 15개, React production build, `git diff --check`, actual desktop/420px Browser QA, 세 그래프 탭, 가로 overflow 0, console error 0을 확인했다.
- 미진행: 신규 source / DB schema / ingestion 변경, 검증된 1주·1개월 예측, monitoring / validation / trading signal.
- 다음 차수: 2차 장기 이력·발표 당시 값의 축적과 품질 점검. 사용자 UI 선택 피드백은 1차 polish로 반영할 수 있다.
