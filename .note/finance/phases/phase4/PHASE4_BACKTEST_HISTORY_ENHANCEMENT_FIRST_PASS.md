# Phase 4 Backtest History Enhancement First Pass

## 목적
이 문서는 Phase 4 Backtest 탭의
`Persistent Backtest History`를
단순 조회 테이블에서
필터/검색/상세 drilldown이 가능한 first-pass 기록면으로 확장한 결과를 정리한다.

## 추가된 기능

### 1. Run Kind Filter

사용자는 이제 history를 실행 종류별로 걸러볼 수 있다.

- `single_strategy`
- `strategy_compare`
- `weighted_portfolio`

의미:

- 단일 전략 실험과 비교/결합 실험을 분리해서 볼 수 있다

### 2. Search

검색 대상:

- strategy 이름
- ticker
- preset 이름
- compare / weighted의 selected strategies

의미:

- 특정 실험이나 특정 유니버스를 더 빠르게 다시 찾을 수 있다

### 3. History Drilldown

필터된 history 중 하나를 선택하면
아래 3개 탭으로 다시 확인할 수 있다.

- `Summary`
- `Input & Context`
- `Raw Record`

의미:

- summary metric만 보는 수준을 넘어서
  당시 어떤 입력과 context로 실행했는지 다시 추적할 수 있다

## 구현 파일

- `app/web/pages/backtest.py`

## 현재 동작 방식

history는 계속 JSONL 파일에 append되는 구조를 유지한다.

- 저장 경로:
  - `.note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`
- UI는 최근 최대 `100`개 record를 로드해
  filter / search / drilldown을 제공한다

## 검증

확인한 것:

- history row builder가 정상적으로 table용 DataFrame을 생성함
- run kind / strategy / ticker / selected strategies가 search text에 반영됨
- filtered history가 없을 때 빈 결과 메시지가 정상 표시됨
- selected record drilldown에서
  - summary
  - input/context
  - raw record
  를 각각 확인 가능

## 현재 한계

- filter 결과를 다시 실행(run again)하는 버튼은 아직 없음
- summary가 비어 있는 compare record는 drilldown에서 raw/context 중심으로 확인해야 함
- date range 필터나 metric 기준 정렬은 아직 없음

## 다음 자연스러운 확장

- `run again` action
- date range / strategy metric filter
- selected history와 현재 화면 결과 비교
