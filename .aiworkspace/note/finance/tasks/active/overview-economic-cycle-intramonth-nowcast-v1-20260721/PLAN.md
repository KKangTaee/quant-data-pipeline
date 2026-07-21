# Overview Economic Cycle Intramonth Nowcast V1 Plan

Status: Design approved — implementation pending
Last Updated: 2026-07-21

## 이걸 하는 이유?

월말 PIT 경제사이클은 당시 공개 데이터에 대한 보존 가능한 기준점이지만, 현월에 새로
공개된 고용·금융·정책 정보를 설명하지 못한다. 과거 월말 기록을 훼손하지 않으면서
현재 입수정보가 추정을 어느 방향으로 움직였는지 별도의 잠정 계산으로 보여준다.

## Roadmap

1. 증분 FRED/ALFRED vintage 수집과 자동화 경계
2. 종료월 canonical rollover, 월말 불변 `intramonth_nowcast` materialization과 loader/service 계약
3. 월말→월중 변화 UI와 production bundle
4. actual data, PIT/불변성 검증, desktop/420px Browser QA, 문서 closeout

## Scope Boundary

- In scope: economic-cycle vintage DB, pipeline snapshot, Overview service/React, scheduled backend job
- Out of scope: NBER 공식 판정, 월중 검증 승격, 데이터 보간, trading signal, visible job panel

## Stop Condition

기존 과거 월말 snapshot이 불변이고 새로 종료된 달의 canonical row와 날짜별 월중
결과만 추가되며, 화면에서 두 기준을 명확히 구분하고 자동 회귀와 실제 Browser QA를
통과하면 완료한다.

## Authoritative Documents

- Design: `docs/superpowers/specs/2026-07-21-economic-cycle-intramonth-nowcast-design.md`
- Implementation plan: design review 승인 후 작성
