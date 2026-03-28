# Phase 7 Next Phase Preparation

## 목적

- Phase 7 종료 이후,
  다음 major phase를 어떤 방향으로 여는 것이 가장 자연스러운지 정리한다.
- quarterly data foundation repair 이후,
  이제 무엇을 product / strategy 방향으로 확장해야 하는지 연결해 둔다.

## Phase 7 종료 시점의 출발점

현재 확보된 상태:
- quarterly raw statement ledger / shadow coverage longer-history recovery
- statement PIT inspection helpers
- weekend/holiday-aware freshness preflight
- quarterly prototype UI preview / inspection surface
- `Quality Snapshot (Strict Quarterly Prototype)`이 다시 `2016` 부근부터 active

즉 다음 phase는
data foundation을 다시 파는 phase라기보다,
**복구된 quarterly foundation 위에서 strategy family를 확장하고 비교 가능한 연구 경로로 올리는 phase**
가 더 자연스럽다.

## 가장 자연스러운 다음 방향

### 후보 1. Quarterly Strategy Family Expansion And Promotion Readiness

가장 추천되는 다음 phase 방향이다.

핵심 문제:
- 현재 quarterly 쪽은 `Quality Snapshot` prototype 하나만 존재한다
- `Value`, `Quality + Value` quarterly path는 아직 없다
- compare / portfolio builder 기준으로 quarterly strict family는 아직 library화되어 있지 않다

핵심 작업:
- `Value Snapshot (Strict Quarterly Prototype)` 추가
- `Quality + Value Snapshot (Strict Quarterly Prototype)` 추가
- quarterly family의 compare / interpretation / history 연결
- quarterly family canonical preset / coverage semantics 정리
- research-only 유지 vs public candidate 진입 기준 문서화

이 방향은
Phase 7에서 복구한 foundation을 실제 strategy library 확장으로 연결하는 phase다.

### 후보 2. Statement PIT Audit And Ledger Tooling Further Expansion

가능은 있지만 우선순위는 낮다.

예:
- 더 강한 filing/acceptance audit UI
- raw ledger diff / anomaly inspection tooling
- issuer-level PIT diagnostics

이유:
- 현재 foundation blocker는 이미 first pass로 많이 완화되었다
- 이제는 strategy-facing 확장으로 넘어가는 쪽이 product value가 더 크다

### 후보 3. Quarterly Public Promotion Decision Only

이건 너무 이르다.

이유:
- 현재 quarterly는 아직 strategy family가 충분히 갖춰지지 않았고
- 비교/검증 표본도 부족하다
- promotion decision은 최소한 quarterly value / multi-factor까지 열린 뒤 하는 편이 맞다

## 추천 방향

Phase 8은 아래 방향으로 여는 것이 가장 합리적이다.

- `Quarterly Strategy Family Expansion And Promotion Readiness`

의도:
- quarterly strict path를 단일 prototype에서 family 수준으로 확장
- annual strict family와 비교 가능한 research path를 만들기
- 이후 promotion 여부를 더 정확하게 판단할 수 있게 하기

## 추천 첫 작업

1. quarterly strict family scope fixed
2. quarterly value prototype first pass
3. quarterly quality+value prototype first pass
4. quarterly compare / interpretation / history connection
5. quarterly family validation checklist and promotion criteria draft

즉 다음 phase의 첫 단계는
단순 coverage 재확인이 아니라
**quarterly strict strategy library build-out**
에 가깝다.

## 현재 상태

- Phase 7 closeout:
  - `implementation_completed`
  - `manual_validation_deferred`
- next-phase candidate evaluation:
  - `completed`
- recommended Phase 8 direction:
  - `Quarterly Strategy Family Expansion And Promotion Readiness`
- next phase formal opening:
  - `ready`
