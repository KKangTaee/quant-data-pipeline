# Phase 22 Next Phase Preparation

## 현재 상태

- `Phase 22`는 사용자 manual checklist QA까지 완료되어
  `phase complete / manual_validation_completed` 상태로 닫혔다.
- 이 문서는 Phase 22 이후 다음 main phase를 열기 위한 handoff 문서다.

## 중요한 경계

`Phase 22`는 투자 포트폴리오를 고르는 phase가 아니다.

이번 phase에서 `Value / Quality / Quality + Value` 조합을 본 이유는
이 3개가 최종 투자 조합이라서가 아니라,
이미 같은 validation frame에서 확인된 대표 전략들이라
portfolio 구성 / 저장 / replay / 비교 workflow를 검증하기 좋은 fixture였기 때문이다.

따라서 Phase 22 이후 기본 방향은
portfolio weight 분석을 계속 넓히는 것이 아니라,
아직 product 기능으로 덜 성숙한 부분으로 돌아가는 것이다.

단, 사용자가 QA 중 특정 portfolio 분석이나 백테스트 비교를 명시적으로 요청하면
그 분석은 수행한다.
다만 그 경우에도 기본 phase 방향이 투자 분석으로 바뀐 것은 아니며,
`사용자 요청 분석`으로 별도 기록한다.

## Phase 22가 끝날 때 물어볼 질문

1. portfolio workflow가 source / weight / date alignment / replay를 재현 가능하게 다루는가
   - 답: 그렇다. baseline report와 saved replay evidence로 확인했다.
2. Phase 22 문서가 "개발 검증"과 "투자 분석"을 명확히 구분하는가
   - 답: 그렇다. checklist QA에서 확인 완료됐다.
3. manual checklist가 완료되어 Phase 22를 닫을 수 있는가
   - 답: 그렇다. 사용자 QA가 완료됐다.
4. 다음 main phase를 `Quarterly And Alternate Cadence Productionization`으로 열어도 되는가
   - 답: 그렇다. portfolio optimization 확대보다 cadence productization이 다음 기본 방향이다.

## 현재 예상되는 다음 방향

- Phase 22 manual QA가 완료되었으므로,
  다음 main phase는 `Phase 23 Quarterly And Alternate Cadence Productionization`으로 여는 것이 자연스럽다.
- 이유는 portfolio 기능을 더 분석하기 전에,
  아직 prototype 성격이 남아 있는 quarterly / alternate cadence를
  실제 백테스트 제품 기능으로 올리는 것이 더 중요한 개발 과제이기 때문이다.
- 현재 weight alternative rerun에서는
  equal-third fixture baseline을 교체해야 할 만큼의 기능상 이유가 나오지 않았다.
- 따라서 Phase 22 closeout 후에는
  portfolio optimization을 계속 넓히기보다,
  quarterly / alternate cadence runtime, UI, report, history 흐름을 production 수준으로 올리는 편이 맞다.

## 다음 phase에서 확정할 것

- 사용자가 Phase 22 QA 중 추가 portfolio 분석을 요청하면,
  narrow rerun이나 comparison report를 만들 수 있다.
- 그러나 기본 로드맵 기준으로는
  Phase 22 안에서 broad weight search,
  diversified component optimization,
  live portfolio candidate selection을 더 열지 않는다.
- Phase 23의 정확한 scope는
  quarterly prototype을 어디까지 productionize할지,
  alternate cadence를 어떤 UI / report contract로 연결할지에 맞춰 다시 확정한다.
