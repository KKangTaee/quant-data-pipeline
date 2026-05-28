# Plan

## 이걸 하는 이유?

Coverage 1000/2000 전체 earnings를 한 번에 수집하면 provider throttling과 UI blocking 위험이 크다. 3차에서는 broader universe를 작은 batch로 나눠 저빈도 수집하는 경로를 만든다.

## Scope

- `symbol_source`에 S&P 500 universe batch, Top1000 batch, Top2000 batch mode를 추가한다.
- `batch_offset`, `max_symbols`, `request_sleep_sec`로 안전하게 이어서 수집할 수 있게 한다.
- Ingestion UI에서 batch mode와 Nasdaq cross-check를 선택할 수 있게 한다.

## Done Criteria

- latest movers 외에도 universe batch symbol set을 resolver로 만들 수 있다.
- Ingestion UI에서 low-frequency earnings collection을 작은 batch로 실행할 수 있다.
- service contract tests가 batch slicing을 검증한다.
