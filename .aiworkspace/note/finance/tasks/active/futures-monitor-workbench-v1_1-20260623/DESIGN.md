# Futures Monitor Workbench V1.1 Design

## Target Reading Flow

```text
Workbench context bar
  -> 자료 갱신 module
  -> Compact watch strip
  -> Macro Context brief / weekly flow
  -> 근거 해석 / 원본 데이터 disclosure
       1. 현재 근거 상태
       2. 과거 점검 요약
       3. 자료 관리
       4. 원본 표
  -> Chart workspace
  -> Provider diagnostics disclosure
```

## Ownership

| Area | Owns | Does Not Own |
|---|---|---|
| Context bar | 관찰 범위, 차트 범위, 자료 상태, 다음 상태 | button wording, provider run rows, raw candle timestamps |
| 자료 갱신 module | 1분봉 refresh, daily macro refresh, screen reload, manual/60s mode | macro evidence interpretation, raw job table as primary content |
| Watch strip | symbol-level state, 15m/60m movement, age | page-level refresh action, provider run diagnostics |
| Evidence disclosure | current macro evidence state, current-scenario validation summary | trading recommendation, validation gate, raw table-first interpretation |
| Raw disclosure | score table, component table, daily symbol table, scenario / relationship / sensitivity source tables | primary reading flow |

## Wording Rules

- Guide titles like `근거를 어떻게 읽을까` become current-state titles like `현재 근거 상태`.
- Empty states are category-specific: `충돌 신호 없음`, `자료 부족 없음`, `약한 근거 없음`.
- Evidence item text uses current-state wording: `현재 ...입니다`, `...을 강화합니다`, `...은 제한적입니다`.
- Context bar `다음 행동` repeats no button label such as `선택 선물 1분봉 갱신`; it reports `갱신 필요`, `자료 양호`, or `확인 필요`.

## Data Boundary

The change reuses existing stored futures OHLCV, macro score, evidence groups, and validation snapshots. Refresh buttons still call the existing Overview action facade from explicit user actions only. No schema, loader, provider, registry, saved setup, or direct render-time provider fetch changes are included.
