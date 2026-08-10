# Design

- CNN은 시장 행동 심리, AAII는 개인투자자 인식 심리로 분리한다.
- 두 source의 점수를 합성하지 않고 방향과 문장형 교차 판정만 만든다.
- CNN 구성요소는 별도 투표가 아니라 CNN headline의 내부 근거와 확신도로 사용한다.
- AAII 방향은 Bull-Bear Spread `+10pp / -10pp` 경계를 사용하고 세 응답의 장기평균 차이는 설명 근거로 사용한다.
- React payload를 v2 두 축 계약으로 정리하고 기존 refresh/reload Python dispatch boundary는 유지한다.
- CNN 0~100, AAII 응답 0~100%, AAII Spread pp를 실제 날짜 간격의 별도 그래프로 표시한다.
- 원본 row와 갱신 세부는 접힌 상세 근거로 내리고 첫 화면은 현재 판단과 확인 조건에 집중한다.
- 시각 개편에서는 종합 판정을 Hero에서 한 번만 설명하고 CNN·AAII current evidence를 같은 밀도로 배치한다.
- 화면에는 CNN 고정 graph와 AAII 전환 graph만 동시에 표시한다. AAII는 `AAII 응답`과 `AAII Spread` tab을 전환한다.
- 모든 관측값은 spline 없이 실제 날짜 간격에 따라 직선으로 연결한다.
- source box 상단의 갈색·녹청색 라운드 장식선은 제거하고 label, 값, graph 색, badge로 출처를 구분한다.
- 1W·1M card는 검증 상태와 unavailable 계약을 먼저 제공하되, 검증된 estimator가 없으면 확률을 표시하지 않는다.
- 3차에서는 unavailable 전망 card를 저장된 실제 관측의 `기간별 심리 변화`로 교체한다. 1W는 CNN 5개 관측 간격·AAII 1개 주간 간격, 1M은 CNN 20개 관측 간격·AAII 4개 주간 간격을 사용한다.
- 각 source의 시작·종료 기준일을 따로 노출하고, 두 축의 시작 관계와 현재 관계가 유지됐는지 바뀌었는지를 기존 cross-read 규칙으로 설명한다.
- 동일 관측일의 중복 version은 `collected_at` 최신 row가 소유한다. 최신 version 값이 결측이거나 payload의 시작·종료 날짜가 유효하지 않으면 이전 값이나 날짜 없는 숫자로 대체하지 않고 해당 source를 unavailable로 닫는다.
- legacy outlook gate는 제거하지 않는다. 검증된 estimator가 없으면 확률은 계속 비공개이며 React 첫 화면에서만 전망 surface를 기간 변화 surface로 대체한다.

Authoritative spec: `docs/superpowers/specs/2026-07-19-overview-sentiment-cnn-aaii-v1-design.md`

Visual redesign spec: `docs/superpowers/specs/2026-07-19-overview-sentiment-visual-redesign-design.md`

CNN component status badge spec: `docs/superpowers/specs/2026-07-20-overview-sentiment-cnn-status-badges-design.md`

Period change 3차 spec: `docs/superpowers/specs/2026-08-11-overview-sentiment-period-change-v3-design.md`
