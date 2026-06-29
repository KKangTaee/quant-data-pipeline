# Overview Market Context Macro Intersection V18 Plan

Status: Active
Date: 2026-06-22

## Why

`Macro 조건 후 결과 변화`가 `기본 유사 맥락 -> GLD 조건 -> 금리선물 조건`처럼 보이면 사용자가 조건 순서에 따라 결과가 바뀌는 것으로 이해할 수 있다.
실제 최종 표본은 GLD 조건과 금리선물 조건의 교집합으로 읽혀야 한다.

## Scope

- Broad anchor 전체에서 GLD 같은 상태 count와 금리선물 같은 상태 count를 각각 계산한다.
- 최종 조건 표본은 두 조건의 교집합 count로 표시한다.
- UI는 sequential funnel 대신 `기본 / GLD / 금리선물 / 둘 다` 구조로 표시한다.

## Non-Goals

- GLD / Rate Pressure bucket 기준 변경
- 새 Macro hard condition 추가
- provider / DB schema / loader / registry / saved JSONL 변경
- prediction / recommendation / signal wording 추가

## Verification

- Focused RED/GREEN tests for service counts and HTML display.
- Full service contract tests.
- Browser QA screenshot.
