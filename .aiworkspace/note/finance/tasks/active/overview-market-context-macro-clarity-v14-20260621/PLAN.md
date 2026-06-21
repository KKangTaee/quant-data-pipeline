# Overview Market Context Macro Clarity V14 Plan

Status: Active
Date: 2026-06-21

## Goal

`Workspace > Overview > Market Context`의 Macro 조건 비교가 broad analog 위에 어떤 macro 조건을 추가했고, 그 결과가 broad 대비 어떻게 달라졌는지 간결하게 읽히도록 정리한다.

## 이걸 하는 이유?

사용자는 `Macro 조건 비교`가 더 좋은 예측표인지, macro 지표를 어떻게 결합했는지, `GLD 중립권 37회` / `금리선물 mixed 6회`가 무엇을 의미하는지 파악하기 어려웠다. 이 영역은 설명 문단을 늘리는 방식이 아니라, 기본 기준 -> 추가 조건 -> 표본 축소 -> 결과 변화 -> 현재 macro 배경 -> 상세 원본 통계 순서로 자연스럽게 읽혀야 한다.

## Scope

- `Sector ETF vs SPY relative strength`는 Macro 추가 조건이 아니라 기본 유사 맥락 기준으로 분리한다.
- Macro 조건 비교는 broad 결과와 conditioned 결과의 차이를 먼저 보여준다.
- `T10Y3M`, `VIXCLS`, `BAA10Y`는 `참고 preview`가 아니라 현재 Macro 배경 상태로 표시한다.
- 기존 `Macro 조건 포함 핵심 자산` / 보조 자산 원본 표는 접힌 상세로 낮춘다.
- 핵심 자산 matrix는 median return 방향뿐 아니라 크기에 따라 색상 농도를 조절한다.
- 섹터 압력 지도 수익률은 소수점 둘째 자리까지 표시한다.

## Out Of Scope

- 새 provider / DB schema / loader / persistence path.
- FRED / Events / sentiment hard conditioning 추가.
- Events surprise / sentiment lag / multi-factor regime scoring 설계.
- Backtest / Practical Validation / Final Review / Operations core logic.
- trade signal, recommendation, validation gate, monitoring signal.

## Stop Condition

- RED/GREEN focused tests and full service contract tests pass.
- Browser QA confirms Market Context renders the revised Macro comparison, matrix gradient, and 2-decimal sector map.
- Durable docs and task records are aligned.
