# Phase 4 Quality UI Input Draft

## 목적
이 문서는 `Quality Snapshot Strategy`를 Backtest UI에 올릴 때
어떤 입력을 기본으로 보여주고,
어떤 입력은 advanced로 숨기고,
어떤 입력은 first-pass에서 완전히 고정할지 정리한다.

## 기본 입력

first-pass에서 사용자에게 바로 보여주는 입력:

1. `Universe Mode`
2. `Preset` 또는 `Manual Tickers`
3. `Start Date`
4. `End Date`
5. `Top N`

이 조합이면:
- 어떤 종목군을 볼지
- 어떤 기간을 볼지
- quality score 상위 몇 개를 고를지
를 바로 조절할 수 있다.

## Advanced Inputs

first-pass에서 advanced로만 노출하는 입력:

1. `Timeframe`
   - 현재는 `1d`만 지원
2. `Option`
   - 현재는 `month_end`만 지원
3. `Factor Frequency`
   - 현재는 `annual`만 지원
4. `Quality Factors`
   - 기본값:
     - `roe`
     - `gross_margin`
     - `operating_margin`
     - `debt_ratio`
5. `Snapshot Mode`
   - 현재는 `broad_research`만 지원

## Hidden Defaults

first-pass에서 UI에 직접 노출하지 않는 값:

1. `rebalance_freq = monthly`
2. `rebalance_interval = 1`
3. `lower_is_better_factors = ['debt_ratio']`
4. weighting rule = `equal_weight`

즉 사용자는 first-pass에서
quality ranking과 selection만 집중해서 볼 수 있고,
리밸런싱/score 해석의 세부 rule은 숨겨둔다.

## Data Requirements Guidance

Quality Snapshot Strategy를 실제로 실행하려면
UI에서 아래 전제를 같이 보여주는 것이 좋다.

1. 가격 데이터
   - `finance_price.nyse_price_history`
   - 일반적으로 `Daily Market Update` 또는 별도 OHLCV 수집이 필요하다
2. factor snapshot 데이터
   - `finance_fundamental.nyse_factors`
   - 일반적으로 `Weekly Fundamental Refresh`가 필요하다
3. detailed statement ledger
   - 현재 public quality strategy는 직접 사용하지 않는다
   - 즉 `Extended Statement Refresh`는 first-pass 필수 조건이 아니다

추가로 first-pass는:
- `broad_research` mode
- `annual` factor snapshot
- stock-oriented universe

기준으로 설명하는 편이 안전하다.

## 결론

Quality Snapshot Strategy의 first-pass UI는
`전략 입력이 많아 보이지 않게 유지하면서도`
quality factor 전략의 핵심 조절값은 열어두는 방향으로 정리한다.
