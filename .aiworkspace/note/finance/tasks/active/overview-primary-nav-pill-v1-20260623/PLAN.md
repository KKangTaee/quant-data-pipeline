# Overview Primary Nav Pill V1 Plan

## Goal

`Workspace > Overview`의 primary tab selector를 기본 Streamlit segmented control에서 compact product pill nav로 바꾼다.

## 이걸 하는 이유?

사용자가 현재 tab bar가 큰 4분할 form control처럼 보여 제품 내비게이션답지 않다고 지적했다. Overview는 시장 맥락을 빠르게 고르는 업무 화면이므로, 선택기는 더 작고 조용하며 현재 위치를 분명하게 보여줘야 한다.

## Scope

- Overview primary selector를 custom HTML/CSS pill nav로 렌더링.
- 기존 tab membership과 lazy dispatch는 유지.
- old selected value fallback은 유지.
- Browser QA로 실제 화면의 상단 nav가 compact하게 보이는지 확인.

## Non-Goals

- Market Context 내부 `근거 화면` 라벨 변경.
- futures / sector helper physical deletion.
- provider / DB / registry / saved JSONL 변경.
- trading, validation, monitoring, broker, auto rebalance semantics 추가.

## Tentative Roadmap

- 1차: compact pill nav 구현.
- 2차: mobile / narrow viewport density 확인.
- 3차: 필요하면 Market Context 내부 old source label 흡수 보정.
