# Master Merge Resolution Plan

## 이걸 하는 이유?

`codex/backtest-dev`의 Sentiment 3차 기준선과 `master`의 Futures Macro 장중 관측·재가격화
변경을 한쪽 손실 없이 통합해야 다음 개발이 일관된 제품·문서 기준선에서 이어질 수 있다.

## Scope

- `ROADMAP.md` 충돌을 문서 역할과 양쪽 구현 사실에 따라 수동 통합한다.
- incoming Futures Macro 코드·React bundle·테스트와 durable 문서의 일관성을 검토한다.
- registry, saved setup, run history, QA 이미지와 local artifact는 병합 commit에서 제외한다.

## Stop Condition

- unresolved conflict와 conflict marker가 0건이다.
- Futures Macro focused Python tests, Python compile, React production build와 diff 검증이 통과한다.
- Roadmap, task state pointer, architecture/flow/runbook이 통합 코드와 일치한다.
- coherent한 merge commit이 생성된다.
