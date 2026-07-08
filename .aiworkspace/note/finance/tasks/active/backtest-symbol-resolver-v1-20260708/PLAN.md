# Backtest Symbol Resolver V1 Plan

## Goal

Backtest Quality / Value Factor Readiness에서 stale/missing price ticker가 단순 가격 누락인지, ticker change 가능성인지 공용으로 진단하고 사용자가 명시적으로 repair를 적용할 수 있게 한다.

## 이걸 하는 이유?

기존 흐름은 `BK` 같은 과거 ticker가 최신 가격을 반환하지 않을 때 같은 ticker로 가격 수집을 반복한다. 실제 사용자는 가격이 빠진 것인지 ticker가 바뀐 것인지 판단해야 하므로, Factor Readiness가 먼저 identity issue 후보를 보여주고 버튼으로 `후보 적용 -> resolved ticker 가격 수집 -> readiness 재검사` 경로를 제공해야 한다.

## Scope

- `codex/sub-dev`의 `4b698eb6` 커밋은 그대로 병합하지 않고, alias 후보/active 적용 아이디어만 재사용한다.
- `market_symbol_alias` 새 테이블 대신 기존 `finance_meta.nyse_symbol_lifecycle`의 `event_type=ticker_change`, `related_symbol`, `related_cik`를 중심으로 구현한다.
- BK -> BNY는 fixture / QA 케이스로만 사용한다.
- 1차는 current 기준 Factor Readiness / price refresh에 집중한다. PIT effective-date split 자동화는 후속 차수로 남긴다.

## 2~5차 Roadmap

### 1차 - Common Resolver V1

- 완료: lifecycle 기반 ticker-change 후보 / active repair / resolved ticker price refresh를 연결했다.
- 완료 조건: focused tests, Browser QA, docs sync, commit.

### 2차 - Source Evidence Scoring

- 목적: 후보가 왜 믿을 만한지, 왜 낮은 신뢰도인지 Factor Readiness와 저장 evidence에 구조적으로 남긴다.
- 변경 화면 / 파일 범위: `finance/loaders/symbol_resolver.py`, `finance/data/symbol_resolver.py`, `app/web/backtest_common.py`, related tests.
- 완료 조건: official/source evidence, same CIK, coverage status, resolved price freshness가 confidence factors로 분해되고 low-confidence 후보는 apply action에서 제외된다.
- 다음 차수 연결: 3차 PIT split contract가 같은 confidence/evidence payload를 재사용한다.

### 3차 - PIT Effective-Date Split Contract

- 목적: current refresh를 넘어서 old ticker / new ticker 기간 분리를 runtime이 읽을 수 있는 metadata contract로 준비한다.
- 변경 화면 / 파일 범위: resolver pure helper, price refresh plan metadata, tests.
- 완료 조건: source ticker를 rewrite하지 않으면서 `source_range`, `resolved_range`, `effective_date`, `split_status`가 plan/details에 남는다.
- 다음 차수 연결: 4차 UI가 이 split boundary를 사용자-facing 근거로 보여준다.

### 4차 - Readiness UX / Action Feedback Polish

- 목적: 사용자가 `가격 업데이트`와 `티커 변경 반영`을 혼동하지 않고, 적용 후 어떤 일을 다시 해야 하는지 알게 한다.
- 변경 화면 / 파일 범위: Factor Readiness model / React panel copy or layout / post-run result feedback / Browser QA.
- 완료 조건: ticker-change check에 후보쌍, 신뢰도, 기간 경계, 적용 후 재실행 안내가 명확히 표시되고 Browser QA를 남긴다.
- 다음 차수 연결: 5차에서 전체 문서와 회귀 QA를 닫는다.

### 5차 - Closeout Docs / Regression QA

- 목적: durable docs, roadmap/index/root logs, active task 상태를 2~5차 완료 기준으로 맞춘다.
- 변경 화면 / 파일 범위: `.aiworkspace/note/finance/docs/`, active task docs, focused test suite.
- 완료 조건: code diff 없이 docs/QA closeout commit을 만들고, 남은 후속 범위를 명확히 남긴다.

## Stop Condition

- Factor Readiness model이 ticker change 후보를 가격 refresh보다 우선 표시한다.
- apply action이 lifecycle row를 active repair로 저장할 수 있다.
- Backtest price refresh가 active resolver를 읽으면 old ticker 대신 resolved ticker를 수집 대상으로 사용한다.
- 2차~5차 각각 focused tests / py_compile / diff check / 필요 시 Browser QA를 실행하고 커밋한다.
