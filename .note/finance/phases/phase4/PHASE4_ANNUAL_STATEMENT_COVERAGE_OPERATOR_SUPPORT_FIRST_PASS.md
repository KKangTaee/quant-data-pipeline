# Phase 4 - Annual Statement Coverage Operator Support First Pass

## 목적

`Quality Snapshot (Strict Annual)`을 sample universe 밖으로 넓히려면
`Extended Statement Refresh`를 더 큰 annual universe에도 운영 가능하게 만들어야 한다.

이번 단계의 목적은 실제 wider-universe annual coverage 확장에 들어가기 전에,
statement ingestion job이 large run에서도 진행 상태를 보여주고
operator가 멈춘 것처럼 오해하지 않도록 보강하는 것이다.

## 구현 내용

### 1. statement collector progress event 추가

파일:
- `finance/data/financial_statements.py`

변경:
- `upsert_financial_statements(...)`에 `progress_callback` 추가
- batch 단위 write가 끝날 때마다 `batch_progress` 이벤트 emit

현재 이벤트 payload 핵심:
- `processed_symbols`
- `total_symbols`
- `batch_index`
- `total_batches`
- `inserted_values`
- `upserted_labels`
- `upserted_filings`
- `failed_symbols_count`
- `freq`
- `period`
- `periods`

### 2. ingestion job runner로 progress 전달

파일:
- `app/jobs/ingestion_jobs.py`

변경:
- `run_collect_financial_statements(...)`가 `progress_callback`을 받도록 확장
- `run_extended_statement_refresh(...)`도 동일하게 callback passthrough
- result details에 `upserted_filings` 추가

### 3. Streamlit live progress 연결

파일:
- `app/web/streamlit_app.py`

변경:
- 아래 action도 live progress 지원 대상으로 포함
  - `extended_statement_refresh`
  - `collect_financial_statements`
- large run일 때 progress bar + caption 표시
- 현재 caption에는 아래 누적 수치가 함께 보인다
  - processed symbols
  - batch index
  - values
  - labels
  - filings
  - failed count

## 검증

검증 명령:

```bash
python3 -m py_compile \
  finance/data/financial_statements.py \
  app/jobs/ingestion_jobs.py \
  app/web/streamlit_app.py
```

sample run:

```python
run_collect_financial_statements(
    ["AAPL", "MSFT", "GOOG"],
    freq="annual",
    periods=1,
    period="annual",
    progress_callback=cb,
)
```

결과:
- `status = success`
- `rows_written = 575`
- `upserted_labels = 573`
- `upserted_filings = 309`
- progress event 1회 확인:
  - `processed_symbols = 3 / 3`
  - `batch_index = 1 / 1`

## 현재 의미

- 아직 wider-universe annual coverage 자체를 실행한 것은 아니다
- 하지만 이제 `Extended Statement Refresh`와 manual statement ingestion은
  large run에서 최소한의 live progress를 보여줄 수 있다
- 따라서 다음 단계인 annual statement coverage 확대를
  운영 관점에서 훨씬 안전하게 진행할 수 있게 되었다

## 다음 단계

1. wider-universe annual coverage scope 결정
2. annual extended statement refresh 실행
3. annual shadow fundamentals/factors rebuild
4. strict annual usable universe 재확인
