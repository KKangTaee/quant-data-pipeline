# Phase 4 Annual Coverage Operatorization Presets First Pass

## 목적

- strict annual maintenance를 실제 operator flow에 더 가깝게 만든다.
- annual coverage를 다시 돌릴 때
  Backtest preset과 Ingestion preset이 서로 같은 universe를 가리키도록 정리한다.

## 구현한 것

파일:
- `app/web/streamlit_app.py`

반영 내용:
- symbol preset dropdown에 아래를 추가
  - `US Statement Coverage 100`
  - `US Statement Coverage 300`
- `Extended Statement Refresh` 안내에
  strict annual coverage preset 사용 가능 문구 추가
- `Financial Statement Ingestion` 안내에도
  같은 preset 사용 가능 문구 추가

즉 operator는 이제
strict annual 검증에 쓰는 universe를
Backtest와 Ingestion 양쪽에서 같은 이름으로 다시 선택할 수 있다.

## shadow rebuild 재검증

strict annual shadow semantics를
`first_available_for_period_end` 기준으로 고친 뒤,
`US Statement Coverage 300` annual shadow를 다시 rebuilt 했다.

결과:
- fundamentals rows: `3286`
- factors rows: `3286`
- covered symbols: `297 / 300`
- median annual rows per covered symbol: `12`
- `12+` annual rows:
  - `247`
- `8+` annual rows:
  - `264`
- missing symbols:
  - `MRSH`
  - `AU`
  - `CUK`

## 현재 의미

- annual coverage 운영화는 이제
  live progress만 있는 상태를 넘어,
  actual strict annual preset universe를 재사용하는 단계까지 올라왔다.
- 즉 strict annual path는
  수집 preset
  -> annual shadow rebuild
  -> backtest preset
  흐름으로 연결된 상태다.
