# Design

## User Flow

```text
시장 브리프
-> 다음 맥락 체크
-> 참고: 과거 유사 맥락
   -> coverage 충분: 5D / 20D / 60D 참고 분포
   -> coverage 부족: 부족 ticker / rows / 보강 action 안내
-> 보조 갱신
   -> 부족 ETF 가격 이력 보강
-> 근거: 자료 기준 / 출처 상태
   -> 접힌 summary에서 정상 / 확인 / 부족 / 주요 source 확인
```

## Implementation Boundary

- `app/services/overview_market_context_analog.py`
  - coverage rows를 검사해 부족 자산을 `coverage_gaps`로 노출한다.
  - 부족 자산이 있으면 `overview_historical_analog_ohlcv` repair action metadata를 만든다.
- `app/jobs/overview_actions.py`
  - Overview UI에서 직접 ingestion job을 부르지 않도록 bounded facade를 둔다.
  - facade는 기존 `run_collect_ohlcv(..., execution_profile="managed_safe")`만 호출한다.
- `app/web/overview_dashboard.py`
  - 보조 갱신 expander 안에 explicit button을 둔다.
  - click 전에는 수집을 실행하지 않는다.
- `app/web/overview_ui_components.py`
  - 부족 상태는 gap panel로 보여준다.
  - source confidence는 접힌 summary에 status strip을 추가한다.

## Data Boundary

이 작업은 `finance_price.nyse_price_history`에 쓰는 기존 OHLCV collection path를 재사용한다. 새 table, schema, provider, loader 계약은 추가하지 않는다. Historical analog 자체는 계속 Overview context-only 참고 정보이며, 결과가 future movement guarantee나 trading signal이 아니다.
