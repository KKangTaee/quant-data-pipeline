# Daily Market Update Rate-Limit Implementation (2026-03-28)

## 목적

- `Daily Market Update`가 broad NYSE universe에서 `yfinance` rate limit에 쉽게 걸리던 문제를
  first-pass 구현으로 완화한다.
- 목표는 무조건적인 병렬 속도보다,
  **중간부터 연쇄 실패하지 않고 끝까지 실행 가능한 운영 경로**를 만드는 것이다.

## 구현 범위

### 1차. safer default + conservative batching + richer diagnostics

- `Daily Market Update` UI 기본 source를
  - `NYSE Stocks + ETFs`
  에서
  - `Profile Filtered Stocks + ETFs`
  로 변경했다.
- UI에서 raw NYSE source를 고르면,
  routine refresh보다 broad operator sweep에 가깝다는 안내를 표시한다.
- `store_ohlcv_to_mysql(...)` 기본 OHLCV write tuning을 더 보수적으로 변경했다.
  - smaller chunk
  - single worker
  - bounded retry
  - sleep + jitter
- `yf.download(...)` 호출 시 provider stdout/stderr를 캡처해서,
  batch 단위로 다음을 구분하도록 보강했다.
  - `rate_limited_symbols`
  - `provider_no_data_symbols`
  - `provider_message_batches`

### 2차. rate-limit cooldown / circuit-breaker + raw heavy profile

- OHLCV 수집에 execution profile 개념을 추가했다.
  - `managed_safe`
  - `raw_heavy`
- `managed_safe`
  - profile-filtered routine refresh용
  - moderate chunk + cooldown
- `raw_heavy`
  - raw NYSE broad sweep용
  - smaller chunk
  - single-worker
  - longer cooldown
- batch window 실행 중 rate-limit이 감지되면:
  - cooldown
  - smaller next chunk
  - single-worker 유지
  로 이어지는 first-pass 대응을 넣었다.
- progress callback에도 `rate_limit_cooldown` 이벤트를 추가했다.

### 3차. noisy-symbol filtering + operator replay support

- raw NYSE source에서
  preferred / unit / special share class 같은 non-plain symbol을
  optional checkbox로 제외할 수 있게 했다.
- 현재 기준 plain symbol 규칙:
  - `^[A-Z]{1,5}$`
- UI result summary에 `OHLCV Diagnostics` expander를 추가했다.
  - rate-limited count
  - provider no-data count
  - filtered symbol count
  - cooldown event count
  - rerun payload
- job result details에도 아래를 남긴다.
  - `execution_profile`
  - `write_settings`
  - `excluded_symbols`
  - `cooldown_events`
  - `rerun_missing_payload`
  - `rerun_rate_limited_payload`

## 코드 변경 위치

- UI / operator flow
  - [streamlit_app.py](/Users/taeho/Project/quant-data-pipeline/app/web/streamlit_app.py)
- job wrapper / execution profile
  - [ingestion_jobs.py](/Users/taeho/Project/quant-data-pipeline/app/jobs/ingestion_jobs.py)
- symbol filtering helper
  - [symbol_sources.py](/Users/taeho/Project/quant-data-pipeline/app/jobs/symbol_sources.py)
- yfinance write path / cooldown / diagnostics
  - [data.py](/Users/taeho/Project/quant-data-pipeline/finance/data/data.py)

## 현재 동작 요약

- `Daily Market Update` 기본 실행은 managed universe 중심으로 돈다.
- raw NYSE source는 여전히 선택 가능하지만,
  더 보수적인 `raw_heavy` profile을 사용한다.
- raw source에서 non-plain symbol exclusion을 켜면,
  noisy special symbol을 먼저 줄일 수 있다.
- stale/no-data/rate-limit은 이제 결과 detail에서 분리해서 볼 수 있다.
- rate-limit이 감지되면 batch 사이에 cooldown이 들어간다.

## 검증

### smoke

- `.venv/bin/python` 기준 execution profile resolve 확인
  - `managed_safe`
  - `raw_heavy`
- non-plain filter helper 확인
  - `SPY, AAM.U, BRK.B, MSFT, AGM.A, QQQ`
  - 결과:
    - filtered: `SPY, MSFT, QQQ`
    - excluded: `AAM.U, BRK.B, AGM.A`
- small daily update smoke 확인
  - symbols: `AAPL, MSFT`
  - result:
    - `success`
    - execution profile / write settings / excluded symbol metadata 확인
- provider no-data diagnostics 확인
  - symbols: `AAPL, BADBAD`
  - result:
    - `partial_success`
    - `missing_symbols = ['BADBAD']`
    - `provider_no_data_symbols = ['BADBAD']`

## 남은 한계

- provider 메시지 분류는 still heuristic이다.
  - `yfinance`가 공식 structured error channel을 주지 않기 때문
- single-worker safe mode로 기운 상태라,
  absolute throughput은 공격적 병렬 방식보다 느릴 수 있다.
- 하지만 broad run에서 중간부터 전부 깨지는 패턴을 줄이는 것이
  현재 운영 목표에는 더 중요하다.

## 바로 볼 테스트 포인트

1. `Ingestion > Daily Market Update`
2. 기본 source가 `Profile Filtered Stocks + ETFs`인지 확인
3. raw NYSE source 선택 시
   - non-plain symbol filter checkbox
   - `raw_heavy` 안내 문구
   가 보이는지 확인
4. 실행 결과의 `OHLCV Diagnostics`에서
   - rerun payload
   - provider message excerpt
   - cooldown event
   를 확인
