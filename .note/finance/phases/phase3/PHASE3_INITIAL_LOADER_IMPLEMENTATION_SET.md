# Phase 3 Initial Loader Implementation Set

## 목적
이 문서는 Phase 3에서
실제 코드로 가장 먼저 구현할 loader 묶음을 확정하기 위한 문서다.

관련 문서:
- `.note/finance/phases/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
- `.note/finance/phases/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase3/PHASE3_STRICT_STATEMENT_LOADER_SCOPE.md`
- `.note/finance/phases/phase3/PHASE3_BROAD_STATEMENT_LOADER_POLICY.md`

---

## 1. 기본 결론

Phase 3의 1차 구현 loader 세트는
"가장 빨리 DB-backed strategy runtime을 여는 최소 경로"
를 기준으로 잡는다.

따라서 1차 구현 우선순위는
가격 기반 전략을 먼저 실행할 수 있는 loader들에 둔다.

이유:
1. 현재 `finance/strategy.py`의 기존 전략들은 가격 기반이다
2. 현재 `finance/engine.py`도 `OHLCV -> transform -> strategy` 흐름에 맞춰져 있다
3. loader 계층의 첫 검증은 가장 단순하고 재현 가능한 경로가 좋다

---

## 2. 1차 즉시 구현 대상

Phase 3 첫 구현 세트:

1. `load_universe(...)`
2. `load_price_history(...)`
3. `load_price_matrix(...)`

이 세 함수는
가장 먼저 실제 코드로 구현하는 것을 권장한다.

### 2-1. `load_universe(...)`

이유:
- 수동 심볼 입력과 DB 유니버스를 같은 계약으로 통합해야 함
- 이후 모든 loader의 symbol resolution 진입점이 됨

### 2-2. `load_price_history(...)`

이유:
- 현재 전략/엔진 구조가 long-form 또는 ticker별 OHLCV dict로 가공되기 쉬움
- 가장 직접적으로 `nyse_price_history`를 runtime에 연결할 수 있음

### 2-3. `load_price_matrix(...)`

이유:
- 향후 momentum / cross-sectional 비교 / matrix 계산에 바로 필요
- price loader 계층을 long-form + matrix 두 축으로 안정화할 수 있음

---

## 3. 1차 바로 다음 구현 후보

첫 세트 다음 우선순위:

1. `load_fundamentals(...)`
2. `load_factors(...)`

이 둘은
"가격 기반 첫 전략 경로가 열린 뒤"
추가 구현하는 것이 적절하다.

이유:
- 현재 첫 DB-backed strategy 후보는 가격 기반 전략이 더 단순함
- fundamentals / factors는 다음 단계 전략 확장에 더 적합함

---

## 4. 문서화는 끝났지만 구현은 뒤로 미루는 대상

이번 챕터에서 정책은 고정했지만,
코드 구현은 뒤로 미루는 대상:

1. `load_statement_values(...)`
2. `load_statement_snapshot_strict(...)`

이유:
- statement loader는 중요하지만
  첫 DB-backed strategy 경로를 여는 최소 세트는 아님
- strict/broad 정책과 PIT 규칙이 먼저 고정되어 있어야 해서
  이번에 문서화부터 선행한 상태
- 구현 시 복잡도가 price loader보다 높음

즉:
- statement loader는 "Phase 3에서 반드시 구현할 대상"이지만
- "첫 구현 세트"는 아니다

---

## 5. 1차 구현 제외 이유

### statements를 첫 세트에서 제외한 이유

1. 기존 전략이 statement loader를 바로 요구하지 않는다
2. strict PIT loader는 구현과 검증 비용이 높다
3. 첫 성공 경로는 짧고 분명해야 한다

### factors / fundamentals를 첫 세트에서 제외하지는 않지만 뒤로 둔 이유

1. DB-backed 전략 첫 성공 경로에는 없어도 된다
2. 이후 cross-sectional 전략 확장용으로 바로 이어서 붙일 수 있다

---

## 6. 1차 구현 세트와 전략 연결

가장 먼저 연결할 수 있는 전략 유형:
- Equal Weight
- Dual Momentum
- GTAA 계열
- Risk Parity Trend

공통점:
- 모두 가격 기반 변환 흐름으로 시작 가능

즉 첫 loader 세트는
"현재 전략 코드와의 접점이 가장 좋은 세트"
로 선택한 것이다.

---

## 7. 구현 순서 권장

권장 순서:

1. `load_universe(...)`
2. `load_price_history(...)`
3. `load_price_matrix(...)`
4. runtime adapter helper
5. 첫 DB-backed 가격 전략 연결
6. `load_fundamentals(...)`
7. `load_factors(...)`
8. `load_statement_values(...)`
9. `load_statement_snapshot_strict(...)`

---

## 8. 완료 기준

이 문서 기준으로 1차 구현 세트가 확정되었다고 보기 위한 기준:

1. "지금 바로 구현할 loader"와 "다음으로 미룰 loader"가 구분되어 있어야 한다
2. 첫 전략 실행과 직접 연결되는 loader가 무엇인지 분명해야 한다
3. statements 관련 loader가 중요하지만 첫 세트는 아니라는 판단 근거가 남아 있어야 한다

---

## 결론

Phase 3의 첫 loader 구현 세트는
`universe + price_history + price_matrix`
로 고정한다.

이는 현재 코드베이스의 전략 구조와 가장 잘 맞고,
가장 빠르게 DB-backed 첫 전략 실행 경로를 여는 선택이다.

fundamentals / factors / statements는
그 다음 단계에서 붙이는 것이 더 안정적이다.
