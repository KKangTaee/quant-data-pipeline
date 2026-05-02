# Phase 3 UI User-Facing Input Set Draft

## 목적
이 문서는 Phase 4 전략 실행 UI가 사용자에게 직접 노출할
최소 입력 집합을 고정하기 위한 초안이다.

핵심 목표:
- 첫 UI에서 입력 항목을 과도하게 늘리지 않는다
- 현재 안정적으로 검증된 DB-backed price-only 전략 경로에 맞춘다
- 이후 factor / fundamental 전략 확장 시 어떤 입력이 추가될지 미리 구분한다

---

## 설계 원칙

### 1. first pass는 “전략 실행에 꼭 필요한 입력”만 노출한다

현재 검증된 경로는 DB-backed price-only 전략이다.

따라서 첫 UI는 아래 질문에만 답할 수 있으면 충분하다.

1. 어떤 전략을 실행할 것인가
2. 어떤 종목/유니버스를 대상으로 할 것인가
3. 어떤 기간을 백테스트할 것인가

그 외 항목은:
- sensible default로 숨기거나
- advanced 섹션으로 내리는 것이 좋다

### 2. 입력은 strategy-specific runtime wrapper와 자연스럽게 맞아야 한다

앞 단계에서 정한 방향은 다음과 같다.

- UI -> strategy-specific DB-backed runtime wrapper
- runtime wrapper -> result bundle

따라서 user-facing input도 wrapper 시그니처와 크게 어긋나면 안 된다.

### 3. product-facing UI 기본값은 DB-backed / strict-safe 쪽을 선호한다

첫 UI에서 direct-fetch path를 노출하지 않는다.

또한 future factor / fundamental 전략으로 확장할 때도
기본 product path는 가능한 한 strict PIT 쪽을 기본으로 보는 것이 맞다.

---

## Phase 4 first-pass 최소 입력 세트

### 필수 입력

#### 1. strategy

의미:
- 어떤 price-only 전략을 실행할지 선택

초기 후보:
- `equal_weight`
- `gtaa`
- `risk_parity_trend`
- `dual_momentum`

UI 형태:
- select box

#### 2. universe mode

의미:
- 종목 입력 방식을 선택

초기 후보:
- `manual_tickers`
- `saved_preset`

비고:
- 첫 UI에서는 `NYSE Stocks + ETFs` 전체 유니버스 실행까지 바로 열지 않는 것이 안전하다
- 첫 실행 경험은 소규모 manual/preset 중심이 적절하다

UI 형태:
- radio or segmented control

#### 3. tickers or preset name

의미:
- 실제 전략 대상 유니버스

`manual_tickers`일 때:
- comma-separated tickers

`saved_preset`일 때:
- preset select

비고:
- 둘 중 하나만 활성화되도록 해야 한다

#### 4. start date

의미:
- 표시/평가 기준 시작일

UI 형태:
- date input

비고:
- 내부 runtime은 warmup/history buffer를 별도로 확장할 수 있다
- user가 보는 값은 “백테스트 시작일”만 입력하면 된다

#### 5. end date

의미:
- 표시/평가 기준 종료일

UI 형태:
- date input

---

## first-pass 기본값으로 숨겨도 되는 입력

### 1. timeframe

현재 판단:
- 기본값 `1d`로 숨겨도 충분하다

이유:
- 현재 price-only DB-backed 경로 검증도 `1d` 기준이다
- UI first pass에서 intraday나 다중 timeframe을 동시에 다루지 않는다

### 2. option

예:
- `month_end`

현재 판단:
- 전략 기본값으로 숨기고 runtime wrapper 내부에서 처리하는 편이 좋다

이유:
- user가 알아야 할 개념이 아니라 실행 세부 구현에 가깝다

### 3. indicator warmup buffer

현재 판단:
- 절대 user-facing input으로 노출하지 않는다

이유:
- runtime 내부 구현 책임이다

### 4. DB/direct source mode

현재 판단:
- Phase 4 first pass에서는 노출하지 않는다

이유:
- product-facing 경로는 DB-backed로 고정하는 것이 맞다

---

## 고급 옵션으로 분리할 수 있는 입력

이 항목들은 첫 UI에서 바로 안 보여도 되지만,
advanced panel로 분리할 가능성은 있다.

### 1. rebalance option

예:
- `month_end`
- `month_start`

현재 판단:
- 전략별 의미가 다르므로 first pass에서는 숨김

### 2. interval

현재 판단:
- Equal Weight 계열 일부 전략에서는 노출할 수 있지만
  first pass에서는 strategy default 사용이 더 안전하다

### 3. strategy-specific params

예:
- momentum lookback
- threshold
- cash proxy

현재 판단:
- first pass에서는 고정값 또는 wrapper default
- 후속 phase에서 advanced tuning으로 확장

---

## 권장 UI 입력 그룹

### Group A. Strategy

- `strategy`

### Group B. Universe

- `universe_mode`
- `tickers` or `preset_name`

### Group C. Period

- `start_date`
- `end_date`

이 3그룹만 있으면 첫 실행 UI는 충분하다.

---

## 전략별 추가 입력 여부

### Equal Weight

필수 추가 입력:
- 없음

### GTAA

필수 추가 입력:
- 없음

비고:
- 내부적으로 trend/momentum 전처리를 수행

### Risk Parity Trend

필수 추가 입력:
- 없음

### Dual Momentum

필수 추가 입력:
- 없음

비고:
- cash proxy 등은 first pass에서 wrapper default 처리 권장

즉 첫 UI는
전략별로 추가 form이 거의 없는 상태로 시작할 수 있다.

---

## future factor / fundamental 전략 확장 시 추가될 입력

이 문서는 first-pass price-only UI 기준이다.

향후 factor / fundamental 전략이 들어오면 아래 입력이 추가될 수 있다.

### 1. rebalance frequency

예:
- monthly
- quarterly
- annual

### 2. snapshot mode

예:
- strict PIT
- broad research

### 3. factor set or ranking rule

예:
- value
- quality
- multi-factor

### 4. investability filter

예:
- missing row drop policy
- min market coverage

현재 판단:
- 이 입력들은 Phase 4 first pass 범위 밖이다

---

## 권장 최소 runtime wrapper 시그니처와의 대응

예상 wrapper 시그니처:

```python
run_equal_weight_backtest_from_db(
    tickers: list[str],
    start: str,
    end: str,
)
```

또는 약간 확장형:

```python
run_equal_weight_backtest_from_db(
    tickers: list[str],
    start: str,
    end: str,
    timeframe: str = "1d",
)
```

즉 UI 입력은 기본적으로:

- strategy
- tickers
- start
- end

네 개를 중심으로 보고,
나머지는 내부 default로 처리하는 것이 맞다.

---

## 현재 권장안

Phase 4 first pass user-facing input set:

1. `strategy`
2. `universe_mode`
3. `tickers` or `preset_name`
4. `start_date`
5. `end_date`

선택적 hidden/default:

6. `timeframe="1d"`
7. strategy-specific internal defaults

---

## 결론

현재 프로젝트 상태를 기준으로 보면,
첫 전략 실행 UI는 복잡한 parameter lab이 아니라
**“전략 + 유니버스 + 기간”** 만으로 충분하다.

즉 user-facing 최소 입력은
많아 보이지만 실제로는 아래 3축이다.

- 어떤 전략인가
- 어떤 종목인가
- 어떤 기간인가

이 단순성이 유지돼야 Phase 4 first pass가 안정적으로 올라간다.
