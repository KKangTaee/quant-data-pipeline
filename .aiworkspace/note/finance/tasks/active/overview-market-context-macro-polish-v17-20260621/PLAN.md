# Overview Market Context Macro Polish V17 Plan

Status: Active
Date: 2026-06-21

## Why

`Workspace > Overview > Market Context`의 `Macro 조건 후 결과 변화`가 V16에서 구조는 정리됐지만, GLD / 금리선물 조건이 무엇을 뜻하는지 기본 사용자가 바로 읽기 어렵고 `현재 Macro 배경 참고`의 텍스트 위계가 다시 prototype-like로 보인다.

## Scope

- Macro sample narrowing bar에서 기본 유사 맥락, GLD 조건, 금리선물 조건의 의미를 사용자 문장으로 표시한다.
- T10Y3M / VIXCLS / BAA10Y 참고 배경은 한글 상태, 값, broad 표본 내 같은 상태 비율을 먼저 보이게 한다.
- 긴 source / condition 원문은 기존 `Macro 조건 상세` disclosure에 유지한다.

## Non-Goals

- Macro hard condition 추가 또는 임계값 변경
- provider / FRED / yfinance direct fetch 추가
- DB schema, loader, registry / saved JSONL, run_history 변경
- Backtest / Practical Validation / Final Review / Operations logic 연결
- prediction / recommendation / signal wording 추가

## Verification

- Focused service contract tests
- `git diff --check`
- `py_compile` for touched UI/service files where relevant
- Browser QA screenshot of Market Context Macro section
