# Daily Market Update Speed Optimization Implementation (2026-03-28)

## 목적

- rate-limit 안정화를 유지하면서,
  managed universe 중심의 `Daily Market Update` 실행 시간을 줄인다.
- 이번 라운드 구현 범위는 다음 세 가지다.
  1. execution breakdown 측정
  2. managed safe speed-up
  3. source별 execution profile 분리

## 구현 내용

### 1. execution breakdown 측정

`store_ohlcv_to_mysql(...)` 결과 stats에 timing breakdown을 추가했다.

추가 항목:
- `fetch_sec`
- `delete_sec`
- `upsert_sec`
- `retry_sleep_sec`
- `cooldown_sleep_sec`
- `inter_batch_sleep_sec`
- `batch_count`
- `written_batch_count`
- `avg_fetch_sec_per_batch`
- `avg_rows_per_written_batch`

또한 Streamlit 결과 UI의 `OHLCV Diagnostics`에서도 이 값을 바로 보게 했다.

의미:
- 느린 실행을
  - provider fetch
  - DB delete
  - DB upsert
  - retry/cooldown sleep
로 분해해서 볼 수 있다.

### 2. managed safe speed-up

새 execution profile:
- `managed_fast`

설정:
- `chunk_size = 60`
- `sleep = 0.05`
- `max_workers = 1`
- `max_retry = 2`
- `retry_backoff = 1.0`
- `rate_limit_cooldown_sec = 12.0`
- `cooldown_chunk_size = 30`

핵심 판단:
- provider output capture가 stdout/stderr 기반이라
  multi-worker를 다시 공격적으로 올리기보다
  **single-worker 유지 + larger chunk + smaller idle sleep**
  조합이 더 안전하다.

### 3. source별 execution profile 분리

`Daily Market Update` UI는 이제 source에 따라 profile을 다르게 선택한다.

- `Profile Filtered Stocks + ETFs`
  - `managed_fast`
- `Profile Filtered Stocks`
  - `managed_safe`
- `Profile Filtered ETFs`
  - `managed_safe`
- `Manual`
  - `managed_safe`
- `NYSE Stocks`
  - `raw_heavy`
- `NYSE ETFs`
  - `raw_heavy`
- `NYSE Stocks + ETFs`
  - `raw_heavy`

즉:
- broad raw source는 여전히 보수적으로
- managed broad source는 더 빠르게

## UI 반영

- `Daily Market Update` 카드에서 source에 따라 execution profile caption이 달라진다.
- `OHLCV Diagnostics`에서 timing breakdown을 바로 볼 수 있다.

## 코드 위치

- profile / result detail
  - [ingestion_jobs.py](/Users/taeho/Project/quant-data-pipeline/app/jobs/ingestion_jobs.py)
- timing breakdown
  - [data.py](/Users/taeho/Project/quant-data-pipeline/finance/data/data.py)
- source별 profile routing / diagnostics rendering
  - [streamlit_app.py](/Users/taeho/Project/quant-data-pipeline/app/web/streamlit_app.py)

## smoke 검증

- execution profile resolve:
  - `managed_fast`
  - `managed_safe`
  - `raw_heavy`
  모두 정상 확인
- `run_daily_market_update(['AAPL','MSFT'], execution_profile='managed_fast')`
  - `success`
  - `execution_profile = managed_fast`
  - `timing_breakdown` populated

예시:
- `fetch_sec = 2.405`
- `delete_sec = 0.001`
- `upsert_sec = 0.001`
- `inter_batch_sleep_sec = 0.057`
- `batch_count = 1`

## 테스트 포인트

1. `Daily Market Update` 기본 source가 `Profile Filtered Stocks + ETFs`일 때
   - `managed_fast` 안내 문구가 보이는지
2. raw `NYSE Stocks + ETFs` 선택 시
   - `raw_heavy` 안내 문구가 보이는지
3. 실행 후 `OHLCV Diagnostics`에서
   - Timing Breakdown이 보이는지
4. 다음 broad managed run에서
   - 이전 약 `2400 sec` 대비 체감 개선이 있는지

## 해석 가이드

- `fetch_sec`가 대부분이면
  - provider fetch가 병목
- `cooldown_sleep_sec`가 크면
  - 아직 rate-limit 개입이 크다
- `delete_sec` / `upsert_sec`가 크면
  - DB write 쪽도 같이 봐야 한다
