# Practical Validation Flow 3 Clarity V1

Status: Active
Created: 2026-07-06
Owner: backtest-dev

## Goal

`Backtest > Practical Validation` Flow 3를 `Final Review 이동 가능 여부`와 `먼저 해결할 일` 중심으로 간결하게 정리한다.

## 이걸 하는 이유?

사용자는 Flow 3에서 후보가 Final Review로 갈 수 있는지와 무엇부터 보강해야 하는지를 먼저 알아야 한다. 현재 화면은 source / profile / replay / readiness 번호 카드, control center 카드, 결론 alert, badge strip, React Fix Queue가 같은 상태를 반복해 보여서 읽기 우선순위가 흐려진다.

## Scope

- Flow 3에서 별도 validation control center를 제거하거나 접어 중복 요약을 없앤다.
- workspace read model 기반 결론 패널을 Flow 3의 단일 first-read surface로 만든다.
- React Fix Queue는 결론, 먼저 해결할 일, 근거 요약을 compact하게 보여준다.
- 상태별 흰색 기반 light gradient / tint를 적용하되 직선형 surface를 유지한다.
- Focused boundary tests, React build, Python compile, Browser QA를 실행한다.

## Out Of Scope

- validation gate / threshold / status policy 의미 변경
- Practical Validation registry / saved JSONL rewrite
- provider 수집, replay 실행 로직, Final Review handoff persistence 변경
- Flow 4 evidence board의 상세 정보 구조 개편
- live approval / broker order / auto rebalance semantics

## Completion

- RED/GREEN focused tests
- Practical Validation page / workspace panel compile
- Fix Queue React bundle rebuild
- relevant unit / contract tests
- Browser QA screenshot
- docs / root handoff update
- commit
