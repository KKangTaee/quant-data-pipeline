# Daily Market Update Short-Window Acceleration (2026-04-04)

## 목적

- `Profile Filtered Stocks + ETFs` 기준의 대형 managed universe refresh에서
  `1d` 또는 아주 짧은 기간 refresh가 지나치게 오래 걸리는 문제를 줄인다.
- 이전 rate-limit 완화 작업을 되돌리지 않고,
  **짧은 daily refresh에만 더 빠른 실행 계약**을 적용한다.

## 문제 요약

사용자 관찰:
- `Daily Market Update`
- source: `Profile Filtered Stocks + ETFs`
- symbol count: 약 `10,669`
- `1d` refresh도 약 `2,384 sec`가 걸림

핵심 의문:
- `20y`는 오래 걸리는 것이 이해되지만,
  `1d`는 수집량이 적으니 훨씬 빨라야 하지 않는가?

## 쉽게 말한 원인

이번 병목은 DB write가 아니라 **provider fetch 호출 횟수**였다.

즉:
- `1d`라고 해서 각 batch가 거의 공짜가 되지 않는다.
- `yfinance`는 batch 하나를 호출할 때마다 기본적인 네트워크/파싱 비용이 크다.
- 그래서 symbol 수가 `10,000+`이면,
  실제 시간은 행 수보다 **batch 수와 batch당 fetch latency**에 더 크게 좌우된다.

쉽게 말하면:
- `1d`와 `20y`의 "받아오는 행 수"는 다르지만,
- 둘 다 `10,669`개 심볼을 같은 방식으로 잘라 fetch하면
  provider 입장에서는 여전히 **엄청 많은 batch 작업**을 처리해야 한다.

## 실제 확인값

문제 run:
- source: `Profile Filtered Stocks + ETFs`
- symbols requested: `10,669`
- duration: `2,384.155 sec`
- execution profile: `managed_fast`

Timing breakdown:
- `fetch_sec = 2367.96`
- `delete_sec = 2.663`
- `upsert_sec = 2.758`
- `inter_batch_sleep_sec = 9.752`
- `batch_count = 178`
- `rate_limited_symbols = 0`
- `cooldown_events = 0`

해석:
- 거의 모든 시간이 `fetch`에 쓰였다.
- DB delete / upsert는 병목이 아니다.
- 최근 실제 run에서는 rate-limit 개입도 거의 없었다.

## 구현 방향

### 무엇을 바꿨는가

새 execution profile:
- `managed_refresh_short`

설정:
- `chunk_size = 70`
- `sleep = 0.01`
- `max_workers = 2`
- `max_retry = 2`
- `retry_backoff = 1.0`
- `rate_limit_cooldown_sec = 10.0`
- `cooldown_chunk_size = 40`
- `degrade_to_single_worker_on_rate_limit = True`

### 언제 이 profile을 쓰는가

다음 조건에서만 자동 선택한다.
- source가 managed profile source일 것
  - `Profile Filtered Stocks`
  - `Profile Filtered ETFs`
  - `Profile Filtered Stocks + ETFs`
- interval이 `1d`일 것
- 그리고 window가 짧을 것
  - `period = 1d`
  - 또는 explicit `start/end` 범위가 대략 `10일 이하`

즉:
- 짧은 daily refresh만 빠르게
- 긴 기간(`1mo`, `20y`)이나 raw sweep은 기존 profile 유지

## 왜 이런 방식이 필요한가

### 쉬운 설명

이 변경은 "전체 시스템을 더 공격적으로" 바꾸는 것이 아니다.

대신:
- **짧고 자주 도는 일일 refresh**
- **길고 무거운 historical fetch**
를 다른 문제로 보고 분리한 것이다.

### 왜 필요한가

- 매일 돌리는 refresh가 `30분+`이면 운영성이 나빠진다.
- 그렇다고 모든 fetch를 무조건 병렬화하면,
  지난번처럼 rate-limit 문제가 다시 터질 수 있다.
- 그래서 이번에는:
  - 짧은 refresh에만
  - 제한된 2-worker 병렬화와
  - 더 짧은 sleep을 주고
  - rate-limit이 보이면 즉시 single-worker / smaller chunk로 후퇴하게 했다.

## 튜닝 검증

같은 managed symbol 샘플 `240`개, 같은 짧은 daily window 기준 비교:

기존 `managed_fast`:
- elapsed: `40.221 sec`
- batch count: `4`
- rate-limit: `0`

실험 조합:
- `60x2`
  - elapsed: `36.365 sec`
  - rate-limit: `0`
- `70x2`
  - elapsed: `23.886 sec`
  - rate-limit: `0`

판단:
- `100x2`는 기대만큼 좋지 않았다.
- `70x2`가 같은 조건에서 가장 균형이 좋았다.
- 그래서 `managed_refresh_short`는 `70x2` 기반으로 확정했다.

## 기대 효과

이 변경은 특히 아래 경로에 의미가 크다.
- `Daily Market Update`
- source: `Profile Filtered Stocks + ETFs`
- period: `1d`
- 또는 최근 며칠만 재수집하는 짧은 explicit range

즉:
- "오늘치 / 최근 며칠치만 빠르게 따라잡는 운영 refresh"를 개선하는 목적이다.

## 남은 한계

- 여전히 provider가 느리면 wall time은 크게 영향을 받는다.
- `10,000+` symbols 전체 refresh는 짧은 기간이라도 여전히 큰 작업이다.
- 이번 변경은 "1d refresh가 20y와 거의 같은 체감"을 줄이는 쪽이지,
  broad universe refresh를 완전히 instant하게 만드는 것은 아니다.
- 완전한 high-throughput 병렬 fetch는 아직 보류했다.
  이유:
  - yfinance rate-limit risk
  - provider output diagnostics 안정성

## 운영 해석 가이드

- `1d` 또는 최근 며칠 refresh:
  - 이제 `managed_refresh_short`를 타는 것이 정상
- 긴 historical fetch:
  - 여전히 `managed_fast` 또는 `raw_heavy`를 타는 것이 정상

즉:
- `1d`가 빨라져야 하는 요구는 맞고
- 이번 변경은 그 요구를 **short-window 전용 profile 분리**로 해결한 것이다.
