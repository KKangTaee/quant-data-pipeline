# Daily Market Update Rate-Limit Analysis (2026-03-28)

## 목적

- `Daily Market Update`를 `NYSE Stocks + ETFs` 전체 심볼로 돌릴 때
  `yfinance` rate limit 때문에 수집이 중간부터 불안정해지는 문제를 재현하고,
  구현 전에 현실적인 최적화 방향을 고정한다.

## 요청 배경

- 현재 `Daily Market Update`는 broad symbol source로
  `NYSE Stocks + ETFs`를 선택할 수 있다.
- 이 소스는 양이 매우 크고,
  실제 실행 시
  `Too Many Requests. Rate limited. Try after a while.`
  가 발생하면서 이후 배치도 연쇄적으로 깨질 수 있다.
- 목표는:
  - rate limit 재현
  - 현재 코드 구조에서 왜 연쇄 실패가 생기는지 파악
  - first-pass 최적화 방향 제안

## 현재 코드 경로

- UI source:
  - [streamlit_app.py](/Users/taeho/Project/quant-data-pipeline/app/web/streamlit_app.py)
- job wrapper:
  - [ingestion_jobs.py](/Users/taeho/Project/quant-data-pipeline/app/jobs/ingestion_jobs.py)
  - `run_daily_market_update(...)`
- symbol resolver:
  - [symbol_sources.py](/Users/taeho/Project/quant-data-pipeline/app/jobs/symbol_sources.py)
- yfinance OHLCV writer:
  - [data.py](/Users/taeho/Project/quant-data-pipeline/finance/data/data.py)
  - `store_ohlcv_to_mysql(...)`
  - `get_ohlcv(...)`

현재 주요 기본값:
- `chunk_size = 100`
- `max_workers = 4`
- `max_retry = 2`
- `retry_backoff = 0.8`
- `yf.download(..., threads=False)`를 배치 단위로 호출

즉 실질적으로는:
- `100`개 심볼씩 배치
- 최대 `4`개 배치를 병렬
- 전체 소스가 크면 provider를 꽤 공격적으로 두드리는 구조다

## 재현 결과

### 1. 소스 규모 자체가 크다

`NYSE Stocks + ETFs` 현재 심볼 수:
- `11,736`

이는 현재 코드 기준으로:
- 약 `118` 배치 (`100`개씩)

### 2. raw source 안에 noisy symbol이 꽤 많다

심볼 구조 간단 점검:
- 전체: `11,736`
- plain uppercase `1~5`자: `11,302`
- non-plain: `434`

non-plain 예시:
- `AAM.U`
- `ABRpD`
- `AGM.A`
- `AKO.B`

이런 심볼은:
- preferred
- unit
- 특수 share class
- provider 호환성이 낮은 raw symbol

일 가능성이 높고,
`yfinance`에서 404 / no-data를 많이 만든다.

비교:
- `Profile Filtered Stocks + ETFs`
  - 전체: `10,669`
  - non-plain: `18`

즉 raw `NYSE Stocks + ETFs`는
managed/profile-filtered universe보다
provider-noise가 훨씬 크다.

### 3. full-source 실제 실행에서 rate limit이 매우 이르게 발생했다

실제 재현:
- source: `NYSE Stocks + ETFs`
- period: `1mo`
- interval: `1d`

관찰:
- 실행 초반부터 `YFRateLimitError('Too Many Requests...')`가 나타남
- 동시에 no-data / possibly-delisted 메시지가 대량으로 섞여 나옴
- provider가 rate-limit 상태에 들어간 뒤에는
  이후 진행되는 배치도 연쇄적으로 깨지는 패턴이 관찰됨

즉 문제는:
1. source 규모가 큼
2. noisy symbol이 많음
3. 병렬/배치 구조가 공격적임
4. once rate-limited, cooldown 없이 계속 때리기 때문에 이후 배치도 악화

### 4. 작은 샘플에서도 기본 설정은 취약했다

샘플:
- raw source 상위 `300`개 심볼
- `period=1mo`
- `interval=1d`

기본 유사 설정:
- `chunk_size=100`
- `max_workers=4`
- `max_retry=2`
- `retry_backoff=0.8`

관찰:
- visible output 상으로 많은 심볼이 `YFRateLimitError`에 걸림
- 그런데 최종 stats에서는:
  - `batch_error_count = 0`
  - `rate_limit_batch_count = 0`
  로 남음

이 의미는 중요하다.

현재 코드는:
- `yf.download(...)`가 예외를 던질 때만 `batch_errors`로 기록한다
- 하지만 실제 `yfinance`는
  - 일부 실패 심볼을 stderr/no-data 형태로 내보내고
  - 함수 자체는 DataFrame을 반환해버릴 수 있다

즉 현재 수집기는
**실제 rate limit이 발생해도 job-level diagnostics에 제대로 잡지 못하는 경우가 있다.**

### 5. batch-size만 줄여도 충분하지 않았다

보수 실험:
- `chunk_size=25`
- `max_workers=1`
- `max_retry=4`
- `retry_backoff=3.0`

관찰:
- 직전 rate-limit 상태를 이어받으면서
  작은 배치에서도 계속 `Too Many Requests`가 반복됨

해석:
- 단순히 batch-size를 줄이는 것만으로는 부족하다
- **rate limit 감지 후 전역 cooldown / circuit breaker**가 필요하다

## 핵심 원인 정리

### 원인 1. source universe가 너무 지저분하다

- raw `NYSE Stocks + ETFs`에는
  provider 호환성이 낮은 특수 심볼이 적지 않다
- 이런 심볼은
  - 404
  - no-data
  - possibly-delisted
  를 많이 만들고,
  batch 효율을 떨어뜨린다

### 원인 2. 병렬 구조가 provider에 공격적이다

- `100`개 x `4` 병렬은
  large-universe daily refresh에는 꽤 공격적이다
- 특히 `yfinance`는 공식 bulk market-data API가 아니기 때문에
  보수적으로 다루는 편이 맞다

### 원인 3. rate-limit 이후 cooldown이 없다

- 한 번 provider가 막기 시작하면
  이후 요청도 연쇄적으로 실패할 수 있다
- 현재는 이 상황에서:
  - 전체 속도를 낮추거나
  - 잠시 쉬거나
  - batch를 다시 작게 나누는
  전역 대응이 없다

### 원인 4. rate-limit 진단이 job 결과에 충분히 반영되지 않는다

- 현재 `batch_errors`는 예외 기반이다
- 하지만 `yfinance`는
  심볼별 실패를 stderr/no-data 형태로 남기고
  call 자체는 성공으로 끝낼 수 있다
- 그래서 operator는:
  - 실제론 rate-limit이 났는데
  - 결과 요약에는 clean하게 보이는
  misleading 상태를 볼 수 있다

## 최적화 방향 제안

### 방향 A. source hygiene 먼저

가장 빠른 1차 개선:
- raw `NYSE Stocks + ETFs`를 그대로 두더라도
  broad daily update에서는 아래를 우선 검토

1. `Profile Filtered Stocks + ETFs`를 기본값으로 승격
2. raw `NYSE Stocks + ETFs`는 operator/heavy mode로 내림
3. raw source에서 최소한 아래를 optional filter로 제공
   - preferred / unit / special share class 제외
   - non-plain symbol 제외

사용자 아이디어였던:
- “스팩/특수 기업은 수집 안 하면 괜찮지 않나?”

에 대한 판단:
- **맞다.**
- 최소한 특수 심볼군을 먼저 빼는 것만으로도
  request waste와 noisy no-data를 꽤 줄일 수 있다

### 방향 B. provider-throttle safe mode 도입

현재 기본값을 더 보수적으로 바꾸는 방향:

- `chunk_size`
  - `100 -> 25~40`
- `max_workers`
  - `4 -> 1~2`
- `retry_backoff`
  - `0.8 -> 3~10`
- batch 사이 jitter sleep 추가
  - 예: `1.0 ~ 2.5s`

이건 수집 속도는 다소 느려지지만,
“중간부터 전부 깨지는 것”보다는 낫다.

### 방향 C. rate-limit circuit breaker 추가

이게 핵심이다.

필요 동작:
1. `Too Many Requests` 징후 감지
2. 감지되면
   - 전체 executor를 계속 밀지 말고
   - 일정 시간 cooldown
3. cooldown 후
   - batch size 축소
   - worker 축소
   - 재시도

즉:
- first rate-limit 이후에도 같은 속도로 계속 때리는 구조를 끊어야 한다

### 방향 D. diagnostics 강화

현재는 job-level result가 실제 provider 문제를 충분히 못 담는다.

필요 개선:
- per-batch stderr / provider failure capture
- `rate_limited_symbols`
- `provider_no_data_symbols`
- `likely_delisted_or_incompatible_symbols`
- `batch_rate_limit_count`

즉 operator가 최종 result만 봐도
- “정말 delisted가 많은 건지”
- “provider가 막은 건지”
를 구분할 수 있어야 한다

### 방향 E. broad daily update와 managed refresh를 분리

실무적으로는 아래처럼 나누는 편이 좋다.

1. `Managed Daily Refresh`
- 기본 추천
- `Profile Filtered Stocks + ETFs`
- 안정성 우선

2. `Raw Exchange Sweep`
- operator/heavy mode
- `NYSE Stocks + ETFs`
- 느리지만 보수적으로
- rate-limit guard 필수

즉 하나의 Daily Market Update 안에
운영 목적이 다른 두 모드를 섞어두지 않는 편이 좋다

## 추천 구현 순서

### 1차 구현

1. `Daily Market Update` 기본 source를
   `Profile Filtered Stocks + ETFs`로 재검토
2. `store_ohlcv_to_mysql(...)` 기본값 보수화
   - smaller chunk
   - fewer workers
   - batch sleep/jitter
3. visible rate-limit도 result details에 잡히게 diagnostics 보강

### 2차 구현

4. rate-limit circuit breaker 추가
5. raw source heavy mode 분리
6. non-plain / preferred / unit symbol filter 옵션 추가

### 3차 구현

7. symbol classification
   - plain common stock / ETF
   - preferred
   - unit/right/warrant
   - likely incompatible
8. operator-friendly rerun payload / failed-batch replay 지원

## 현재 추천 결론

지금 당장 가장 합리적인 first pass는:

1. **source 자체를 조금 더 관리형으로 줄인다**
2. **기본 batch/concurrency를 보수적으로 낮춘다**
3. **rate-limit 감지 + cooldown을 넣는다**
4. **provider no-data와 rate-limit을 job 결과에서 분리해서 보여준다**

특히 이 순서가 좋은 이유는:
- 문제를 단순히 “retry 더 많이”로 해결하려 하지 않고
- source hygiene
- provider throttling
- diagnostics
를 같이 고치기 때문이다

## 메모

- 이번 문서는 구현 전 방향 고정 문서다
- 아직 코드 최적화는 시작하지 않았다
- 다음 단계는:
  - 이 문서 방향을 기준으로
  - first-pass 구현 범위를 좁히고
  - 실제 코드 변경에 들어가는 것이다
