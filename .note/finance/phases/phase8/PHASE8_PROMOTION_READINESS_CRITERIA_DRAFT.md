# Phase 8 Promotion Readiness Criteria Draft

## current position

- quarterly strict family는 아직 `research-only`
- 이번 draft의 목적은
  바로 public promotion을 결정하는 것이 아니라,
  나중에 무엇을 만족하면 승격 검토를 할 수 있는지 기준을 고정하는 것이다

## candidate family

- `Quality Snapshot (Strict Quarterly Prototype)`
- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

## minimum promotion criteria

### 1. coverage stability

- default managed preset에서 actual active start가 충분히 이르다
  - 최소한 annual comparison이 가능한 수준까지 history가 열려야 한다
- repeated rerun에서 active start drift가 과도하지 않다

### 2. runtime stability

- single strategy
- compare
- history rerun / prefill
- selection interpretation

위 4개 surface에서 반복적으로 에러 없이 동작해야 한다.

### 3. interpretation readability

- selection history
- interpretation summary
- preflight / shadow coverage preview

를 통해 늦은 active start와 factor availability를 사용자가 이해할 수 있어야 한다.

### 4. research value

- annual strict family와 비교했을 때
  quarterly family가 단순 duplicate가 아니라
  의미 있는 차이를 주는지 확인되어야 한다.

### 5. no misleading default

- default preset / default dates로 실행했을 때
  “사실상 대부분 cash-only” 같은 misleading path가 기본값이 되면 안 된다.

## current assessment

- `Quality Snapshot (Strict Quarterly Prototype)`:
  - research-ready
- `Value Snapshot (Strict Quarterly Prototype)`:
  - research-ready
- `Quality + Value Snapshot (Strict Quarterly Prototype)`:
  - research-ready
- public-candidate:
  - not yet

## next decision trigger

아래가 충족되면 public-candidate 검토를 다시 연다.

- user manual validation 통과
- compare repeatability 확인
- annual vs quarterly comparative readout 정리
- default preset 기준 active history가 충분히 이르다는 판단
