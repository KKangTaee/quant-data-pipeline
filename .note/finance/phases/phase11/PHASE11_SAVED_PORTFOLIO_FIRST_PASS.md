# Phase 11 Saved Portfolio First Pass

## 목적

- `Compare & Portfolio Builder`에서 만든 weighted portfolio를
  저장 가능한 first-class workflow object로 승격한다.
- 사용자가
  - 현재 compare 결과를 저장하고
  - 나중에 compare 화면으로 다시 불러오고
  - 저장된 포트폴리오를 바로 재실행할 수 있는
  first-pass workflow를 연다.

## 이번 pass에서 구현된 것

### 1. Saved portfolio store

- 새 저장 파일:
  - `.note/finance/saved/SAVED_PORTFOLIOS.jsonl`
- 새 runtime 모듈:
  - `app/web/runtime/portfolio_store.py`
- 지원 기능:
  - saved portfolio 저장
  - saved portfolio 목록 조회
  - saved portfolio 삭제

저장 레코드는 다음 두 축으로 나뉜다.

- `compare_context`
  - `selected_strategies`
  - `start/end`
  - `timeframe`
  - `option`
  - `strategy_overrides`
- `portfolio_context`
  - `strategy_names`
  - `weights_percent`
  - `normalized_weights`
  - `date_policy`

즉 saved portfolio는
“현재 weighted result 화면만 저장”하는 것이 아니라,
**compare 입력 계약 + weighted portfolio 계약을 함께 저장하는 구조**
로 잡았다.

### 2. Save current weighted portfolio

- 위치:
  - `Backtest > Compare & Portfolio Builder > Saved Portfolios > Save Current Weighted Portfolio`
- 전제:
  - compare 실행 완료
  - weighted portfolio build 완료
- 저장 항목:
  - portfolio name
  - description
  - compare context
  - current weighted configuration

### 3. Load saved portfolio into compare

- 위치:
  - `Saved Portfolios > Load Into Compare`
- 동작:
  - `Compare & Portfolio Builder` 패널로 이동
  - selected strategies prefill
  - compare start/end/timeframe/option prefill
  - strategy-specific override prefill
  - weight/date-policy prefill 대기 상태 저장

즉 사용자는 저장된 포트폴리오를 바로 compare 화면으로 가져와
수정한 뒤 다시 실행할 수 있다.

### 4. Run saved portfolio

- 위치:
  - `Saved Portfolios > Run Saved Portfolio`
- 동작:
  - 저장된 compare context로 각 전략을 다시 실행
  - 저장된 weight/date-policy로 weighted portfolio를 다시 구성
  - compare bundles / weighted bundle을 session state에 다시 올림
  - compare history + weighted portfolio history에 context를 남김

즉 이 버튼은
**compare부터 weighted portfolio result까지 end-to-end rerun**
을 수행한다.

### 5. Weighted portfolio meta/readout 보강

- `Weighted Portfolio Result`에 `Meta` 탭 추가
- 추가 노출 항목:
  - `portfolio_name`
  - `portfolio_id`
  - `portfolio_source_kind`
  - `date_policy`
  - `selected_strategies`
  - `input_weights_percent`

또한 contribution summary에는
- `Configured Weight (%)`
- `Normalized Weight`
를 같이 보여주도록 정리했다.

### 6. History linkage

- saved portfolio에서 다시 실행된 weighted run은 history context에
  - `saved_portfolio_id`
  - `saved_portfolio_name`
  를 남긴다.
- 따라서 later batch review 시
  “이 weighted portfolio run이 어떤 saved portfolio definition에서 나온 것인지”
  추적 가능하다.

## 이번 pass에서 의도적으로 남긴 것

- saved portfolio in-place edit / overwrite UI
- focused compare drilldown -> portfolio save direct bridge
- portfolio 전용 benchmark / drawdown 비교 surface
- rebalance-level change summary
- strategy-level exposure summary 확장

즉 이번 구현은
**saved portfolio contract + load/rerun workflow first pass**
까지를 완료 기준으로 삼았다.

## 현재 의미

Phase 11의 첫 구현 기준으로 보면,
이제 백테스트 surface는

1. strategy compare
2. weighted portfolio build
3. saved portfolio save
4. saved portfolio load / rerun

까지 이어지는 연구 workflow를 갖추게 되었다.

아직 full productization은 아니지만,
이제부터는 단발성 compare 화면이 아니라
**반복 가능한 portfolio workflow surface**
로 읽는 것이 맞다.
