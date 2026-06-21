# Overview Market Context Macro Labels V15 Plan

Status: Active
Date: 2026-06-21

## Why

`Macro 조건 후 결과 변화`가 V14에서 broad result와 conditioned result를 분리했지만, `Macro 추가 조건` 반복 라벨과 `같은 상태` 문구만으로는 사용자가 `81회 -> 37회 -> 6회` 표본 축소 의미를 바로 이해하기 어렵다.

## Scope

- `app/web/overview_ui_components.py`
- `tests/test_service_contracts.py`
- task / roadmap / project map / root handoff docs after implementation

## Goals

1. Macro sample flow labels should name the actual stage: broad basis, GLD condition, rate-pressure futures condition.
2. Sample counts should say what pool they came from, e.g. broad anchors -> GLD-like anchors -> rate-pressure-like anchors.
3. Current Macro backdrop preview should explain `same state` as a count within the broad anchor pool.
4. T10Y3M, VIXCLS, and BAA10Y should show concise Korean explanations.

## Boundaries

- No new provider fetch, DB schema, loader, hard condition, registry / saved JSONL write, validation gate, monitoring signal, or recommendation/trade wording.
- FRED / events / sentiment remain reference / deferred unless already approved elsewhere.
