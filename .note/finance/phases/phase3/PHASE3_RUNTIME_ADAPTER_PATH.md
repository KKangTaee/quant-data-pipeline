# Phase 3 Runtime Adapter Path

## 목적
이 문서는 Phase 3의 첫 DB-backed runtime path에서
loader 출력과 기존 전략 입력을 어떻게 연결할지 정리한다.

관련 문서:
- `.note/finance/phases/phase3/PHASE3_MINIMAL_VALIDATION_PATH.md`
- `.note/finance/phases/phase3/PHASE3_FIRST_DB_BACKED_STRATEGY_CANDIDATE.md`

---

## 기본 결론

Phase 3의 첫 runtime adapter는
loader의 long-form price history를
기존 전략이 기대하는 ticker-keyed OHLCV dict로 바꾼다.

즉:
- 입력: `load_price_history(...)` 결과
- 출력: `{symbol: DataFrame}` 형태

---

## 필요한 변환

기존 전략/transform 계층이 기대하는 핵심 형식:
- `Date`
- `Ticker`
- `Open`
- `High`
- `Low`
- `Close`
- `Adj Close`
- `Volume`
- `Dividends`
- `Stock Splits`

loader 출력은 기본적으로 lowercase long-form이므로,
adapter는 다음을 수행한다.

1. `symbol` 기준 그룹화
2. `date` 정렬
3. loader 컬럼명을 기존 전략 컬럼명으로 rename
4. `Ticker` 컬럼 복원

---

## Phase 3 1차 공개 함수

- `adapt_price_history_to_strategy_dfs(...)`
- `load_price_strategy_dfs(...)`

---

## 결론

Phase 3의 첫 runtime adapter는
"DB loader 출력 -> 기존 전략 입력" 사이의
좁고 명확한 브리지로 유지한다.
