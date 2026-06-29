# Overview Primary Tab Soft Remove V1 Plan

## Goal

`Workspace > Overview`의 primary tab에서 `Futures Monitor`와 `Sector / Industry`를 제거한다.

## 이걸 하는 이유?

사용자가 두 화면을 직접 만든 뒤에도 어떤 확실한 판단을 얻는지 선명하지 않다고 판단했다. Overview는 시장 맥락을 빠르게 읽는 첫 화면이어야 하므로, 사용 가치가 불명확한 별도 탭을 계속 polish하기보다 `Market Context` 중심으로 좁힌다.

## Scope

- `OVERVIEW_DEEP_TAB_OPTIONS`에서 `Futures Monitor`, `Sector / Industry` 제거.
- 기존 session / deep-link 값이 제거된 탭을 가리키면 `Market Context`로 fallback.
- Overview IA guide와 durable docs의 primary tab 목록 정렬.
- Focused contract test, compile, diff hygiene, Browser QA 수행.

## Non-Goals

- futures / sector service, collector, loader, DB schema 삭제.
- `Market Context` 내부 futures / sector evidence 계산 변경.
- provider fetch, registry / saved JSONL write, validation gate, monitoring signal, trading semantics 추가.

## Stop Condition

- Overview selector가 `Market Context`, `Market Movers`, `Sentiment`, `Events`만 노출한다.
- 기존 `Futures Monitor` / `Sector / Industry` 세션 값은 `Market Context`로 돌아간다.
- 문서가 top-level Overview 탭 정리 상태와 맞는다.
