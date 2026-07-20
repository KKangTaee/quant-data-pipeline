# Market Movers Hybrid Visual System V1 Plan

Status: Design Review
Last Updated: 2026-07-20

## 이걸 하는 이유?

기능이 연결된 Market Movers one-shell을 시장맥락·선물매크로와 같은 Overview visual family로 통일해, 사용자가 화면 구조를 다시 학습하지 않고 움직임·확산·선택 종목 근거를 읽도록 한다.

## Roadmap

- [x] 1차 A안 visual specification과 범위 확정
- [ ] 2차 React DOM/CSS TDD 구현과 production build
- [ ] 3차 actual Browser QA, responsive 보정, 문서 closeout

## Stop Condition

- `DESIGN.md`의 acceptance criteria를 자동 테스트와 actual Browser QA로 확인한다.
- 기능 payload/event 계약과 기존 selected state가 바뀌지 않는다.
- generated QA image와 사용자 registry/saved/run-history artifact를 commit하지 않는다.

## Out Of Scope

- conditional outlook와 예측 수치
- DB/service/read-model 변경
- raw run/job/row diagnostics 중심 UI
