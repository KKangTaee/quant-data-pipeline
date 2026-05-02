# Phase 5 Overlay Runtime First Pass

## 목적

- strict factor family 위에 first overlay를 실제 runtime/UI/history/result schema까지 연결한다.

## 구현 범위

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

## 구현 내용

### sample / preprocessing

- snapshot 전략용 price builder는
  overlay가 켜지면 MA 계산을 위한 warmup history를 더 앞에서 읽는다
- 현재 first pass는
  `trend_filter_window`가 주어지면
  `MA{window}`를 생성한 뒤 period filter를 적용한다

### strategy

- strict family core simulation은 여전히 factor ranking을 먼저 수행한다
- overlay가 켜지면
  raw top-N 후보 중
  `Close < MA{window}`인 종목만 추가로 제거한다
- 제거된 비중은 cash로 남는다

### runtime wrapper

- strict family public wrapper는 아래 input을 받는다
  - `trend_filter_enabled`
  - `trend_filter_window`
- result meta / history에도 같은 정보가 남는다

### interpretation

- selection history는 이제
  - raw selected
  - overlay rejected
  - final selected
  를 함께 보여준다
- compare focused strategy에서도 같은 해석 view를 볼 수 있다

## smoke validation

확인한 최소 smoke:

1. compare strict quality
   - `Big Tech Strict Trial`
   - overlay on
   - meta에 overlay 값 저장 확인
2. strict value single
   - overlay on
   - row-level `Overlay Rejected Ticker` 확인
3. strict quality+value single
   - overlay on
   - multi-factor path에서도 동일 schema 확인

## 현재 한계

- month-end only
- cash fallback only
- overlay benchmark / regime / vol target 없음
- public 차트에 overlay event marker를 직접 찍지는 않음

## 결론

- Phase 5 first overlay runtime은
  `month-end MA200 trend filter + cash fallback`
  으로 strict family 전반에 first-pass 연결되었다.
