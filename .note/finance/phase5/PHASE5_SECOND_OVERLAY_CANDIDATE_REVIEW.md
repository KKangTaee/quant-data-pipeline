# Phase 5 Second Overlay Candidate Review

## 목적

- first overlay 이후 어떤 두 번째 overlay가 자연스러운지 후보를 좁힌다.

## 후보

### 1. Market Regime Overlay

- 예:
  - benchmark close vs MA200
  - broad market regime 악화 시 exposure 축소

장점:
- user explanation이 비교적 쉽다
- per-symbol trend filter보다 더 상위의 방어 로직을 줄 수 있다

주의:
- benchmark 정의를 추가로 고정해야 한다

### 2. Drawdown / Volatility Guard

- 예:
  - realized vol threshold
  - trailing drawdown guard

장점:
- factor family 전체에 공통 risk budget 개념을 붙이기 좋다

주의:
- parameter tuning과 해석 부담이 크다
- stop-like 동작은 사용자 기대와 실제 구현 간 오해가 생기기 쉽다

## 현재 추천

second overlay 우선순위는 아래 순서가 적절하다.

1. `Market Regime Overlay`
2. `Drawdown / Volatility Guard`

## 다음 착수 기준

second overlay를 실제 구현 후보로 끌어올리기 전에
아래가 먼저 정리되는 편이 좋다.

1. first overlay on/off 비교 결과가 정리되어 있을 것
2. selection interpretation에서
   cash fallback / overlay rejection을 충분히 읽을 수 있을 것
3. stale preflight 진단이
   운영상 설명 가능한 수준일 것

## 현재 추천안의 더 구체적인 형태

다음 착수 후보는 아래가 가장 자연스럽다.

- `Market Regime Overlay`
  - benchmark:
    - 우선 `SPY` 또는 broad market proxy를 검토
  - first rule:
    - benchmark `Close < MA200`이면
      strict factor selection의 gross exposure를 줄이거나 cash 비중을 늘림
  - 위치:
    - per-symbol trend filter 위의 portfolio-level guard

## 이유

- first overlay가 per-symbol trend filter이므로
  second overlay는 portfolio-level 판단으로 가는 편이 구조적으로 자연스럽다
- benchmark regime 쪽이 drawdown/vol guard보다 설명과 운영이 더 단순하다

## 결론

- second overlay는 지금 구현하지 않는다
- 다만 다음 후보 우선순위는
  `Market Regime Overlay -> Drawdown / Volatility Guard`
  로 정리해 둔다.
- 다음 챕터에서 실제로 열 후보는
  우선 `Market Regime Overlay`다.
