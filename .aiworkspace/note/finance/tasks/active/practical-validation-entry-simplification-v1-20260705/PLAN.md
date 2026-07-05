# Practical Validation Entry Simplification V1

Status: Active
Created: 2026-07-05
Owner: backtest-dev

## Goal

`Backtest > Practical Validation` 첫 진입 화면에서 검증 workflow와 직접 관련 없는 상단 요소를 줄이고, 현재 검은 HTML/CSS 카드 톤을 흰색 직선형 surface로 정리한다.

## 이걸 하는 이유?

사용자는 Practical Validation에 들어오자마자 “이 후보가 Final Review로 넘어갈 수 있는가?”를 확인해야 한다. 현재 첫 화면은 Reference help, context-only 시장 심리 overlay, 애매한 command title, 검은 둥근 카드가 먼저 보여 실제 검증 판단 흐름보다 부가 설명과 장식이 더 강하게 보인다.

## Scope

- Practical Validation 기본 진입에서 `Reference help`를 제거한다.
- Practical Validation 기본 진입에서 context-only `시장 심리 Context Overlay`를 제거한다.
- command center 제목과 설명을 Final Review 이동 전 검증 상태 중심으로 바꾼다.
- Practical Validation HTML/CSS helper의 검은 카드 톤을 흰색 / 연한 border / 직선 corner로 바꾼다.
- Browser QA로 Practical Validation 첫 화면과 Flow 3 Fix Queue를 확인한다.

## Out Of Scope

- sentiment service / loader 삭제
- Final Review / Portfolio Monitoring sentiment context 변경
- validation gate / threshold / provider collection / registry JSONL 변경
- React Fix Queue component의 구조 변경
- live approval / broker order / auto rebalance semantics

## Completion

- RED/GREEN focused boundary tests
- py_compile
- Backtest boundary tests
- Browser QA screenshot
- durable task/doc log update
- commit
