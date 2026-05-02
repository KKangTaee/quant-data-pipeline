# Phase 12 GTAA Score Weight And Risk-Off First Pass

## 목적

- GTAA의 상대강도 점수 계산을 고정 계약이 아니라 사용자가 조절할 수 있게 만든다.
- GTAA의 위험구간 대응도 고정 `MA200 + cash fallback`에서 조금 더 유연하게 만든다.

쉬운 뜻:

- 이제 GTAA는 단순히 "그대로 돌려보는 전략"이 아니라,
  사용자가
  - `1M / 3M / 6M / 12M` 가중치
  - trend filter window
  - 방어 채권 fallback
  - market regime filter
  - crash guardrail
  를 직접 조절해볼 수 있는 상태가 되었다.

## 이번에 추가된 GTAA 입력

### 1. Score Horizons

기본값:

- 기본 선택은 `1M / 3M / 6M / 12M`
- 선택된 horizon은 모두 동일 비중으로 처리

의미:

- 예전 GTAA는 `1M / 3M / 6M / 12M` 평균이 고정이었다.
- 이제는 예를 들어:
  - `1M, 3M`만 남겨서 단기/중기 모멘텀만 보거나
  - `3M, 6M, 12M`만 남겨서 더 느린 momentum만 보게 만들 수 있다.
- 선택한 horizon은 모두 동일 비중으로 들어간다.
- 그래서:
  - 지금은 "가중치를 튜닝하는 실험"보다
  - "어떤 horizon 조합이 더 robust한가"를 먼저 보기 좋은 구조다.

### 2. Trend Filter Window

- 기본값: `200`

의미:

- 예전엔 사실상 `MA200` 고정이었다.
- 이제는 `MA150`, `MA250`처럼 바꿔서
  GTAA가 trend filter에 얼마나 민감한지 직접 확인할 수 있다.

### 3. Fallback Mode

- `Cash Only`
- `Defensive Bond Preference`

의미:

- `Cash Only`
  - 현재처럼 위험구간이나 후보 부족 시 현금으로 남는다.
- `Defensive Bond Preference`
  - `TLT`, `IEF`, `LQD` 같은 방어 채권 후보를 먼저 채워보고,
    그래도 못 채우는 슬롯만 현금으로 둔다.

### 4. Defensive Tickers

- 기본값: `TLT,IEF,LQD`

의미:

- stronger bond preference를 켰을 때,
  어떤 ETF들을 "방어 채권 후보"로 볼지 정한다.

### 5. Market Regime Overlay

- `Enable`
- `GTAA Market Regime Window`
- `GTAA Market Regime Benchmark`

의미:

- benchmark가 자기 이동평균 아래에 있으면 risk-off로 본다.
- 이때 GTAA는
  - 현금으로 가거나
  - defensive bond preference를 사용한다.

### 6. Crash Guardrail

- `Enable Crash Guardrail`
- `Crash Drawdown Threshold (%)`
- `Crash Lookback (months)`

의미:

- benchmark가 최근 고점 대비 일정 비율 이상 빠지면
  별도의 crash-side risk-off를 켠다.
- 예:
  - 최근 12개월 고점 대비 `15%` 이상 하락하면
    GTAA를 위험구간으로 간주

## 구현 범위

### Single Strategy

- GTAA single form에서 위 입력을 직접 조절 가능

### Compare

- Compare > GTAA advanced input에서도 같은 계약을 조절 가능

### History / Prefill

- 저장된 run의
  - score weights
  - risk-off mode
  - defensive tickers
  - market regime
  - crash guardrail
  이 다시 form / compare로 돌아오도록 연결

## 현재 구현 해석

이건 first pass다.

즉:

- score weights와 risk-off contract를 이제 실험할 수 있다.
- 하지만 아직 이것이 "최적"이라고 확정한 것은 아니다.
- 다음 단계는:
  - 어떤 weight 조합이 더 robust한지
  - defensive fallback이 실제로 MDD를 얼마나 낮추는지
  - market regime / crash guardrail이 overfit 없이 도움 되는지
  를 backtest로 검증하는 것이다.

## smoke 확인

다음 계약으로 smoke를 확인했다.

- interval = `1`
- score weights:
  - `1M = 2.0`
  - `3M = 1.0`
  - `6M = 1.0`
  - `12M = 0.5`
- trend filter window = `150`
- fallback mode = `defensive_bond_preference`
- defensive tickers = `TLT,IEF,LQD`
- market regime enabled = `True`
- market regime benchmark = `SPY`
- market regime window = `200`
- crash guardrail enabled = `True`
- crash threshold = `15%`
- crash lookback = `12 months`

결과:

- runtime 실행 성공
- meta에 새 GTAA 계약 값이 기록됨
- result rows에
  - `Defensive Fallback Count`
  - `Regime State`
  - `Crash Guardrail Triggered`
  - `Risk-Off Reason`
  이 노출됨

## 다음 액션 제안

1. GTAA 상위 preset 4개 기준으로
   - score weight sensitivity
   - risk-off mode 비교
2. defensive tickers를
   - `TLT,IEF,LQD`
   - `TLT,IEF,LQD,GLD`
   같은 식으로 바꿔보기
3. regime / crash guardrail을 켰을 때
   CAGR보다 MDD 개선이 실제로 의미 있는지 비교
