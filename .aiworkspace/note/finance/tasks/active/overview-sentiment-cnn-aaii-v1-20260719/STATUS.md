# Status

- 상태: 전체 잠정 로드맵 `1/4차` 기능 구현·QA 완료, 후속 시각 개편 spec 승인 및 상세 구현 계획 작성
- 완료 범위: 합성점수 없는 CNN 시장 행동 / AAII 투자자 인식 두 축, 문장형 교차 판정, source별 상세 근거, 세 단위별 이력 그래프, 예측이 아닌 확인 조건
- 판정 계약: AAII Bull-Bear Spread `>= +10pp`는 낙관, `<= -10pp`는 비관, 그 사이는 중립이며 결측은 판단 불가다. CNN 구성요소는 CNN headline 내부 근거로만 사용한다.
- 승인된 시각 계약: 교차 판정은 Hero에서 한 번만 설명하고 CNN·AAII current evidence를 균형 있게 둔다. CNN graph는 고정하고 AAII 응답률/Spread를 한 panel의 tab으로 전환해 화면에는 graph 두 개만 동시에 표시한다. 모든 시계열은 원본 관측점을 직선으로 연결하며 source box 상단 colored rail은 제거한다.
- 검증: focused sentiment unittest 15개, React production build, `git diff --check`, actual desktop/420px Browser QA, 세 그래프 탭, 가로 overflow 0, console error 0을 확인했다.
- 미진행: 신규 source / DB schema / ingestion 변경, 검증된 1주·1개월 예측, monitoring / validation / trading signal.
- 다음 작업: `docs/superpowers/plans/2026-07-19-overview-sentiment-visual-redesign.md`를 Task 1~5 순서로 실행해 1차 polish를 마감한다. 그 이후 로드맵 2차는 장기 이력·발표 당시 값의 축적과 품질 점검이다.
