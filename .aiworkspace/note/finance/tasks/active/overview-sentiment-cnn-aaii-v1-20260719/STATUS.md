# Status

State: paused

- 상태: 전체 잠정 로드맵 `3/4차` 완료. 1차 기능·시각 polish, 2차 PIT 축적·공통기간 보정, 3차 실제 관측 기반 기간별 변화 구현·검증 완료
- 완료 범위: 합성점수 없는 CNN 시장 행동 / AAII 투자자 인식 두 축, Hero 교차 판정, 균형 current evidence, CNN 고정 + AAII 응답/Spread 전환의 동시 2 graph, 1W·1M 실제 관측 변화 card, confirm/reverse/persist 관찰 조건, 접힌 상세 근거
- 판정 계약: AAII Bull-Bear Spread `>= +10pp`는 낙관, `<= -10pp`는 비관, 그 사이는 중립이며 결측은 판단 불가다. CNN 구성요소는 CNN headline 내부 근거로만 사용한다.
- 승인된 시각 계약: 교차 판정은 Hero에서 한 번만 설명하고 CNN·AAII current evidence를 균형 있게 둔다. CNN graph는 첫 행 전체 폭에 고정하고 AAII 응답률/Spread를 둘째 행 전체 폭 panel의 tab으로 전환해 화면에는 graph 두 개만 동시에 표시한다. 모든 시계열은 원본 관측점을 직선으로 연결하며 source box 상단 colored rail은 제거한다.
- CNN 상세 근거 상태 계약: 서버가 제공하는 `danger / warning / neutral / positive` tone을 평점 badge에만 적용한다. 점수는 중립색을 유지하고 AAII 행에는 같은 badge를 적용하지 않는다.
- 검증: fresh sentiment-name regression은 기존 baseline 3건을 제외한 `40 passed`이며, 전체 43개 실행에는 시작 전과 같은 3건만 남는다. Python compile, React production build, `git diff --check`, actual desktop/420px Browser QA를 통과했다. 기간 card 값·날짜·관계 문장, desktop 2열/mobile 1열, page/main/component 가로 overflow 0과 console error/warn 0을 확인했다.
- 미진행: 신규 source / DB schema / ingestion 변경, 검증된 1주·1개월 예측, monitoring / validation / trading signal.
- 2차 최신 확인: AAII 공식 workbook canonical 이력은 `1987-07-24~2026-08-06` 2,035개, CNN canonical 이력은 `2025-06-04~2026-08-10` 298개다. immutable PIT는 2026-07-20 실제 수집 시점부터만 유효하며 현재 14 capture day다.
- 3차 결과: 1W는 CNN 5개 관측 간격·AAII Spread 1개 주간 간격, 1M은 CNN 20개 관측 간격·AAII Spread 4개 주간 간격의 시작값·현재값·변화량과 두 축 관계 전환을 실제 날짜로 표시한다. 기존 fail-closed outlook은 보존하며 확률은 계속 비공개다.
- 리뷰 보완: 같은 관측일의 중복 row는 `collected_at` 최신 버전을 선택하고 그 최신 값이 결측이면 이전 유효값으로 대체하지 않는다. payload도 시작·종료 날짜가 유효한 실제 순서가 아니면 해당 source를 공개하지 않으며 rolling fallback에는 CNN·AAII별 관측 부족 설명을 유지한다.
- 다음 작업: 미래 확률 요구가 유지되면 4차에서 target, 독립 episode, chronological point-in-time 검증과 publication gate를 먼저 승인한다. 승인 전에는 신규 source / DB / ingestion / estimator를 추가하지 않는다.
