# Recommendation

Date: 2026-08-03
Decision status: user approval required

## Recommended Product Contract

경제사이클 화면을 `현재 상태를 정확히 읽고, 어떤 조건에서 다음 국면을 감시할지
설명하는 화면`으로 바꾼다. 특정 월의 미래 국면과 확률은 기본 화면에서 제거한다.

### 1. Current Observed State

- phase vocabulary: 회복 / 확장 / 둔화 / 위축
- NBER recession: phase override가 아닌 별도 historical reference
- inputs: activity level, labor / income level, robust momentum, breadth, duration
- output: phase, boundary proximity, evidence coverage, 기준일

### 2. Recent Change

- 1개월: 최신 변화 감지
- 3개월: 변화의 방향과 breadth
- 6개월: 현재 국면을 지지하는 background trend
- 숫자만 나열하지 않고 무엇이 강화 / 약화됐는지 설명

### 3. Conditional Transition

- current phase 유지 근거
- 다음 인접 phase 전환 감시 조건
- 상태: 관찰 중 / 압력 누적 / 전환 확인
- confirmation: depth + diffusion + duration
- 반증 조건과 data freshness를 함께 표시

### 4. Graph

- 과거 actual trajectory와 현재 actual point
- 미래점, +1M / +2M 점선 path와 probability coordinate 제거
- transition pressure는 방향 band로만 표시

### 5. Asset Checkpoints

현행 계산, 카드 구조와 product role을 유지한다. 새 current / transition state가 필요한
최소 adapter만 두고 자산별 판단 로직을 재설계 범위에 포함하지 않는다.

## Validation Contract

- current state: PIT vintage replay, revision sensitivity, NBER chronology와의 timing 차이,
  CFNAI / ADS 같은 coincident reference와의 consistency
- transition monitor: peak / trough lead, false alarm, miss, detection delay, minimum
  persistence, extra cycle count
- UI: current phase와 plotted coordinate의 동일 입력 보장, 미래점 미노출,
  asset checkpoint regression

## Approval Question

현재 4분면을 공식 침체 판정이 아니라 `상대 성장순환`으로 정의하고, `침체`를 `위축`으로
바꾸며 NBER는 별도 reference로 분리하는 전제를 먼저 승인받아야 한다.
