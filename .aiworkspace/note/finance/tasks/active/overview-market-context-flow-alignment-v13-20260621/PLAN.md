# Overview Market Context Flow Alignment V13 Plan

Status: Active
Date: 2026-06-21

## Goal

`Workspace > Overview > Market Context`가 상단 시장맥락과 `참고: 과거 유사 맥락`을 같은 기준 섹터로 읽고, 전체 흐름 요약 화면답게 guide / prototype-like detail을 줄이도록 정리한다.

## 이걸 하는 이유?

사용자는 Market Context에서 전체 시장 흐름을 빠르게 파악하려고 한다. 현재 화면은 상단 섹터 압력 지도와 historical analog의 기준 섹터가 달라질 수 있고, 11개 섹터 중 일부만 보이며, 과거 유사맥락은 guide label과 상세 table/card가 많아 overview라기보다 prototype/debug view처럼 읽힌다.

## Scope

- Historical analog 기준 섹터를 상단 Market Context sector leadership snapshot과 정렬한다.
- Sector pressure map은 canonical 11개 섹터를 균일한 tile로 보여준다.
- Historical analog는 `먼저 볼 점` / `주의할 점`을 제거하고 유사 맥락 계산 흐름에 흡수한다.
- Core asset comparison에 target sector ETF, SPY, QQQ, TLT, GLD를 함께 보여준다.
- 상세 통계와 macro conditioned detail은 기본 흐름보다 낮춘다.

## Out Of Scope

- 새 provider / DB schema / loader / persistence path.
- UI render 중 external fetch.
- FRED / events / sentiment hard conditioning.
- Backtest / Practical Validation / Final Review / Operations core logic.
- trade signal, recommendation, validation gate, monitoring signal.

## Stop Condition

- Focused RED/GREEN tests and full service contract tests pass.
- Browser QA confirms latest / selected as-of and pattern controls still render.
- Task docs and durable roadmap/index/project map are aligned.
