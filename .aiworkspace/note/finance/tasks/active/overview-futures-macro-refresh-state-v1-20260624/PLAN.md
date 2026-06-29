# Overview Futures Macro Refresh State V1 Plan

## Goal

`Workspace > Overview > Futures Macro` 탭에서 저장된 선물 일봉 최신일과 화면 snapshot이 어긋나지 않게 한다.

## 이걸 하는 이유?

사용자가 `선물 매크로` 탭이 계속 `2026-06-23` 기준으로 머무는 것처럼 보인다고 보고했다. DB 수집 최신일, snapshot cache, 탭 내 갱신 경로를 분리해 확인하고, DB가 갱신됐는데 화면 cache가 stale하게 남는 경로를 줄인다.

## Scope

- DB 최신 1D candle marker가 바뀌면 futures macro snapshot cache key도 바뀌게 한다.
- `선물 매크로` 탭 상단에 `일봉 매크로 갱신`과 `최신 데이터 다시 읽기` 컨트롤을 노출한다.
- 기존 `Market Context` 기본 진입은 무거운 futures macro validation을 다시 포함하지 않는다.

## Out Of Scope

- futures daily collector provider 교체.
- OS scheduler / automation cadence 변경.
- DB schema / registry / saved JSONL 변경.
- trading signal, validation gate, monitoring signal 추가.
