# Phase 17 Concentration-Aware Weighting Implementation Third Slice

## 목적

- strict annual family의 세 번째 structural downside lever로
  `concentration-aware weighting`을 실제 코드에 연결한다.
- 목표는 새 전략 family를 여는 것이 아니라,
  기존 `Value / Quality / Quality + Value` strict annual 후보에서
  equal-weight top-N 구조를 조금 더 부드럽게 만들어
  same-gate lower-MDD practical candidate 가능성을 실험하는 것이다.

## 이번 slice에서 구현된 것

- strict annual core strategy 로직인
  `finance.strategy.quality_snapshot_equal_weight(...)`
  가 `weighting_mode`를 받도록 확장됐다.
- current contract:
  - `equal_weight`
  - `rank_tapered`
- 현재 동작은:
  - `equal_weight`
    - 기존과 동일하게 선택된 종목을 균등 비중으로 보유
  - `rank_tapered`
    - top-ranked 종목에 조금 더 높은 비중,
      하위 ranked 종목에 조금 더 낮은 비중을 주는
      mild taper를 적용
- current first slice의 taper는
  optimizer나 volatility targeting이 아니라
  strict annual current architecture에 맞는
  bounded rank-based weighting이다.

## 코드 경로

- strategy:
  - `finance/strategy.py`
- DB-backed strict annual sample/runtime bridge:
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
- Streamlit form / payload / prefill:
  - `app/web/pages/backtest.py`

## UI surface

- Single Strategy
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- Compare
  - 위 strict annual 3 family compare override

표시 이름은:
- `Weighting Contract`
  - `Equal Weight`
  - `Rank-Tapered`

Glossary / help wording 기준 개념은:
- `Concentration-Aware Weighting`
- `Rank-Tapered Weighting`

## 결과 surface에 남는 것

- input params / meta:
  - `weighting_mode`
- row-level execution trace:
  - `Weighting Mode`
  - `Next Weight`
- runtime warning:
  - `rank_tapered` 선택 시
    selected holding이 pure equal-weight 대신
    mild rank taper로 배분된다는 안내가 같이 표시된다.

## 검증

- `py_compile`
  - `finance/sample.py`
  - `finance/strategy.py`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`
- import smoke
  - `.venv/bin/python` 기준
    - `finance.strategy`
    - `finance.sample`
    - `app.web.runtime.backtest`
    - `app.web.pages.backtest`
    import 통과
- representative rerun은
  current `Value` / `Quality + Value` anchor에 바로 적용해
  별도 report로 기록했다.

## 현재 해석

- 이 slice는
  `same-gate lower-MDD`를 보장하는 결과 문서가 아니라,
  equal-weight top-N 자체를 구조적으로 바꿔볼 수 있게 만든
  third implementation slice다.
- representative rerun 기준으로는
  기능적으로는 정상 작동했고 gate도 유지됐지만,
  current anchor를 대체하는 lower-MDD exact rescue는 아직 못 만들었다.

## 다음 작업

- representative rerun 결과를
  linked report와 strategy hub / backtest log에 반영
- current 3개 structural lever 결과를 모아
  Phase 17 closeout 또는 next structural lever 우선순위를 재정리
