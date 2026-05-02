# Phase 5 Managed Universe Freshness Backfill First Pass

> Status: superseded / rolled back as current behavior.
> This document remains as an experiment record only. The current codebase does **not** use run-level freshness replacement for strict managed presets.

## 목적

- strict managed preset을 단순 static symbol list가 아니라
  **선택한 end date 기준으로 실제로 usable한 universe**에 더 가깝게 만들기
- stale symbol을 경고만 하는 상태에서 한 단계 더 나아가,
  managed preset 단계에서 제외 / 보충까지 수행하기

## 구현 범위

이번 first pass에서 구현한 것은 아래다.

1. `freshness-aware managed preset resolution`
2. `backfill-to-target`
3. `exclusion / replacement reporting`

이번 단계에서 아직 구현하지 않은 것은 아래다.

- stale reason classification
  - `local_ingestion_gap`
  - `source_gap`
  - `likely_delisted_or_symbol_changed`
  - `confirmed_delisted`

## 구현 위치

주요 변경 파일:

- `app/web/pages/backtest.py`
- `app/web/runtime/backtest.py`
- `app/web/runtime/history.py`

## 동작 방식

strict managed preset (`100/300/500/1000`)을 고를 때:

1. asset profile에서 target보다 넓은 candidate pool을 읽는다
2. selected end date 기준으로 per-symbol latest daily price를 검사한다
3. top target 구간 안에서 stale / missing symbol을 제외한다
4. 뒤 순위 symbol 중 freshness를 통과하는 종목으로 target count를 다시 채운다

즉 정책은:

- `drop-only` 아님
- **`backfill-to-target`**

## UI 반영

single strict family form에서:

- ticker preview는 이제 static preset list가 아니라
  freshness-aware resolved universe를 기준으로 보여준다
- `Price Freshness Preflight` 위에
  managed preset resolution summary가 같이 보인다
- exclusion / replacement가 발생하면
  `Managed Preset Resolution` expander에서
  다음을 확인할 수 있다
  - target
  - resolved
  - candidates scanned
  - excluded
  - replacements
  - first excluded symbols
  - first replacement symbols

compare strict family form에서도:

- preset preview가 동일한 freshness-aware resolution을 사용한다
- compare override 실행도 resolved universe를 기준으로 동작한다

## metadata / history 반영

single strict family 실행 후:

- bundle meta에 `managed_universe_resolution`이 저장된다
- history record에도 같은 정보가 남는다
- `Latest Backtest Run > Meta > Execution Context`에서
  policy / target / resolved / excluded / replacements를 확인할 수 있다

## 검증 결과

기준:

- end date: `2026-03-20`
- timeframe: `1d`

결과:

- `US Statement Coverage 300`
  - `policy = freshness_backfill_to_target`
  - `status = ok`
  - `300 / 300`
  - exclusion / replacement 없음

- `US Statement Coverage 1000`
  - `policy = freshness_backfill_to_target`
  - `status = adjusted`
  - `1000 / 1000`
  - excluded: `5`
  - replacements: `5`
  - first excluded:
    - `CMA`
    - `DAY`
    - `CFLT`
    - `CADE`
    - `BCpC`
  - first replacements:
    - `GTLB`
    - `RUSHA`
    - `CACC`
    - `REZI`
    - `ADT`

## 해석

- 이제 `Coverage 1000`은 “이름만 1000”이 아니라,
  selected end date 기준으로 **실제로 usable한 1000-name preset**에 더 가까워졌다
- stale symbol이 남아 있어도
  managed preset 단계에서 먼저 걸러지므로
  preflight warning과 actual execution 결과의 괴리가 줄어든다
- 다만 이 단계는 어디까지나 freshness 운영 개선이며,
  stale 원인이 상폐인지 source gap인지까지 판정해주지는 않는다

## 다음 단계

가장 자연스러운 후속 작업:

1. stale reason classification
2. replacement / exclusion reporting을 compare result/meta에도 더 명확히 노출
3. 필요하면 strict managed preset build policy를
   runtime helper / loader boundary로 승격

## 이후 결정

- 이후 검토에서,
  selected end date 기준 stale 여부로 run 전체 universe를 미리 교체하는 것은
  historical backtest 타당성에 맞지 않는다고 판단했다.
- 현재 코드 기준 strict preset은 다시
  - run-level static universe
  - rebalance-date availability filtering
  으로 돌아가 있다.
- 따라서 이 문서는
  **현행 동작 설명이 아니라 실험 기록**으로만 봐야 한다.
