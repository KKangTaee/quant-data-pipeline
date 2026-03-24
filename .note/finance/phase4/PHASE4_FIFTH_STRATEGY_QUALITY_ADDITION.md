# Phase 4 Fifth Strategy Quality Addition

## 목적
이 문서는 `Quality Snapshot Strategy`를
Backtest 탭의 다섯 번째 공개 전략으로 연결한 first-pass 구현 기록이다.

## 연결한 것

### 1. Single Strategy selector
- `Backtest` 탭의 single-strategy selector에
  `Quality Snapshot`을 추가했다.

### 2. Form
- quality 전략 전용 form을 추가했다.
- basic input:
  - universe
  - start/end
  - top N
- advanced input:
  - factor selection
  - factor freq
  - snapshot mode
- 추가 가이드:
  - 필요한 수집 경로(`Daily Market Update` + `Weekly Fundamental Refresh`)
  - 현재 모드가 `broad_research`라는 점
  - `Extended Statement Refresh`는 first-pass 필수 조건이 아니라는 점
  을 form 안에서 바로 확인할 수 있게 했다.

### 3. Runtime 연결
- `run_quality_snapshot_backtest_from_db(...)`
  를 form submit에 연결했다.

### 4. History / Prefill
- backtest history에 quality meta를 저장하도록 확장했다.
- `Load Into Form`과 `Run Again` 경로도 quality strategy를 지원하도록 확장했다.

### 5. Compare 연결
- compare strategy options에도 `Quality Snapshot`을 포함시켰다.
- first-pass에서는 quality 전용 override로
  - `top_n`
  - `quality_factors`
  정도만 조절 가능하게 열었다.

## 현재 성격

이 전략은:
- first factor / fundamental strategy
- `broad_research` mode
- research-oriented snapshot strategy

즉 strict PIT quality strategy로 설명하는 것은 아직 맞지 않다.

## 결론

Backtest UI는 이제:
- 4개 price-only 전략
- 1개 factor / fundamental 전략

까지 포함하는 상태가 되었다.
