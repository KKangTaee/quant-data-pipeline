# Phase 3 Minimal Validation Path

## 목적
이 문서는 Phase 3 첫 loader 구현이
성공했는지 최소한으로 검증하는 경로를 정의한다.

관련 문서:
- `.note/finance/phases/phase3/PHASE3_FIRST_DB_BACKED_STRATEGY_CANDIDATE.md`
- `.note/finance/phases/phase3/PHASE3_FIRST_LOADER_IMPLEMENTATION_ORDER.md`

---

## 1. 기본 결론

Phase 3 첫 검증 경로는
아래 흐름으로 고정한다.

1. `load_universe(...)`
2. `load_price_history(...)`
3. runtime adapter
4. `EqualWeightStrategy`
5. 결과 DataFrame 확인

---

## 2. 최소 입력 예시

첫 검증 입력 예시:

- `symbols = ["AAPL", "MSFT", "GOOG"]`
- `start = "2024-01-01"`
- `end = "2024-12-31"`
- `timeframe = "1d"`

비고:
- 현재 로컬 DB 기준으로 위 예시 심볼은 실제 적재가 확인된 상태다
- 초기 검증은 manual symbols가 가장 단순하다
- universe source는 그 다음 검증에서 붙여도 된다

---

## 3. 성공 기준

아래가 모두 만족되면 최소 경로 성공으로 본다.

1. loader가 빈 DataFrame 없이 가격 row를 반환한다
2. adapter가 ticker별 dict 형태로 변환한다
3. `EqualWeightStrategy`가 예외 없이 실행된다
4. 결과 DataFrame에 최소 아래 컬럼이 존재한다
   - `Date`
   - `Ticker`
   - `Total Balance`
   - `Total Return`
5. 결과 row 수가 0보다 크다

---

## 4. 실패 시 우선 점검 항목

1. symbol resolution이 올바른가
2. price loader의 날짜 범위 필터가 올바른가
3. 컬럼명이 기존 전략 기대 형식과 맞는가
4. adapter에서 `date -> Date`, `close -> Close` 변환이 누락되지 않았는가

---

## 결론

Phase 3의 최소 검증 경로는
"DB price loader -> adapter -> EqualWeightStrategy"
로 고정한다.

이 경로가 통과하면
DB-backed runtime의 첫 성공 경로가 열린 것으로 본다.
