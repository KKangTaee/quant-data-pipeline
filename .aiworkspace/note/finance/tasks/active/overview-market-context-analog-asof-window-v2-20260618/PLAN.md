# Overview Market Context Analog As-Of Window V2

Status: Complete
Date: 2026-06-18
Worktree: `sub-dev`

## 이걸 하는 이유?

`Workspace > Overview > Market Context > 참고: 과거 유사 맥락`은 기존에는 최신 sector leadership과 5D 상대강도만 기준으로 읽었다.
사용자는 시간이 지난 뒤에도 특정 기준 시점의 맥락을 다시 보고, 현재 패턴도 단일 오늘 값이 아니라 5D / 20D / monthly window로 바꿔 읽을 수 있어야 한다.

## Scope

- 기존 DB price history와 current sector / industry metadata만 사용한다.
- Historical analog read model에 `as_of_date`와 `pattern_window`를 추가한다.
- `pattern_window`는 5D / 20D / monthly를 지원한다.
- 기준일 선택 시 해당 날짜 이하의 DB 가격 row만 사용한다.
- 기존 상승 비율 / 중간값 / 최선 / 최악 / 표본 수 table은 유지한다.
- UI에 기준 시점과 패턴 기간 controls를 추가한다.
- context-only 문구를 유지한다.

## Out Of Scope

- 새 provider, 새 DB schema, 새 loader / persistence path.
- historical PIT sector universe snapshot 저장소 구현.
- registry / saved JSONL write.
- UI render 중 provider / FRED / yfinance 직접 fetch.
- macro-conditioned analog, rates / gold / futures / events / sentiment 결합 scoring.
- Backtest Analysis, Practical Validation, Final Review, Operations core logic.
- trade signal, broker order, auto rebalance, validation or monitoring signal.

## Completion Criteria

- historical analog가 기준 시점과 패턴 기간을 명확히 표시한다.
- 가능한 범위의 as-of replay가 기존 DB 자료만으로 동작한다.
- full PIT replay 한계와 필요한 후속 storage/read path가 문서화된다.
- 기존 distribution table이 유지된다.
- `current_as_of`, `requested_as_of`, `data_window`가 선택한 기준 시점과 모순되지 않는다.
- Browser QA에서 latest / 과거 기준 / 계산 불가 기준 표시를 확인한다.
- coherent commit을 만든다.
