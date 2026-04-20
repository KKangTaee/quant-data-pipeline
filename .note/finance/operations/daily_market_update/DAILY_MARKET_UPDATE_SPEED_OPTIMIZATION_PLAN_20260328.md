# Daily Market Update Speed Optimization Plan (2026-03-28)

## 배경

- Daily Market Update rate-limit 안정화 1차 구현은 완료됐다.
- 사용자 검증 기준으로 broad managed run이 약 `2400 sec` 수준으로 성공했다.
- 즉 현재 상태는:
  - **안 깨지고 끝까지 도는 것**에는 성공
  - 하지만 **운영 체감 속도는 여전히 느린 상태**

이번 라운드 목표는:
- 안정성은 유지
- managed universe routine refresh는 더 빠르게
- raw NYSE broad sweep은 계속 보수적으로

## 최적화 방향

### 1. 실행 breakdown 측정

먼저 수집 시간의 구성을 결과 detail에서 직접 보이게 만든다.

추가할 항목:
- total fetch time
- total delete time
- total upsert time
- total retry sleep time
- total cooldown sleep time
- inter-batch sleep time
- batch count
- avg fetch time per batch
- avg rows per written batch

목적:
- “느리다”를 느낌이 아니라 수치로 분해
- 이후 profile tuning 전/후 비교 가능

### 2. managed safe speed-up

현재 managed default는 rate-limit 안전 쪽으로 너무 보수적이다.

따라서 profile-filtered source에는 별도 faster profile을 둔다.

예상 방향:
- `managed_fast`
  - larger chunk
  - shorter base sleep
  - still single-worker
  - shorter cooldown
- `managed_safe`
  - manual / narrower / less predictable source에 유지
- `raw_heavy`
  - raw NYSE source에 유지

핵심:
- provider output capture가 global stderr/stdout 기반이라
  무작정 multi-worker로 다시 올리기보다
  **single-worker + larger chunk + smaller idle sleep** 쪽이 현실적이다.

### 3. source별 execution profile 분리

현재는 source에 따라 사실상 두 성격이 섞여 있다.

최종 방향:
- `Profile Filtered Stocks + ETFs`
  - `managed_fast`
- `Profile Filtered Stocks`
  - `managed_safe`
- `Profile Filtered ETFs`
  - `managed_safe`
- `Manual`
  - `managed_safe`
- raw `NYSE Stocks / ETFs / Stocks + ETFs`
  - `raw_heavy`

즉:
- 실사용 managed universe는 더 빠르게
- broad raw source는 여전히 보수적으로

## 구현 순서

1. breakdown timing/diagnostics 추가
2. `managed_fast` profile 도입
3. source별 execution profile routing 적용
4. smoke validation
5. 문서/로그 동기화

## 검증 기준

- `Daily Market Update` 결과 detail에서 timing breakdown이 보인다
- source mode에 따라 execution profile이 달라진다
- `Profile Filtered Stocks + ETFs`는 이전보다 더 빠른 profile을 사용한다
- raw NYSE source는 여전히 `raw_heavy`를 사용한다
- 기존 no-data / rate-limit diagnostics는 유지된다

## 비고

- 이번 라운드는 absolute 최속화보다
  **안정성을 거의 유지한 채 managed run 체감 속도를 개선하는 것**이 목적이다.
- 더 공격적인 병렬화는
  provider message capture 방식 자체를 바꾸기 전에는
  다시 rate-limit risk를 키울 수 있다.
