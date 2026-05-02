# Phase 8 Quarterly Strategy Family Expansion And Promotion Readiness Plan

## 목적

- Phase 7에서 복구한 quarterly statement/PIT foundation 위에
  quarterly strict strategy family를 실제 연구 가능한 전략군으로 확장한다.
- annual strict family와 비교 가능한 quarterly research path를 만든다.
- quarterly family가 여전히 research-only에 머물지,
  아니면 일부 경로를 다음 public candidate로 올릴 수 있는지 판단할 준비를 한다.

## 왜 이 phase가 필요한가

현재 quarterly 쪽은 다음 상태다.

- data foundation:
  - repaired
- quality quarterly prototype:
  - available
- value quarterly prototype:
  - absent
- quality+value quarterly prototype:
  - absent
- compare / portfolio builder quarterly integration:
  - absent

즉 Phase 7까지는
quarterly path가 “돌아갈 수 있는지”를 복구한 단계였고,
Phase 8은
**그 path를 strategy family 수준으로 확장하는 단계**
다.

## 이번 phase의 핵심 질문

1. quarterly strict value family를 어떤 factor set으로 정의할 것인가
2. quarterly quality+value path는 annual strict family와 어떤 수준까지 parity를 가져갈 것인가
3. quarterly strict family를 compare / history / interpretation에 어느 범위까지 연결할 것인가
4. quarterly family는 여전히 research-only로 둘지, promotion criteria를 둘지

## 범위 안

### A. quarterly strategy family scope 고정

- quarterly quality / value / quality+value family 역할 정의
- prototype naming / UI exposure / compare exposure 정책 정리

### B. quarterly value prototype 구현

- runtime wrapper
- single strategy UI
- interpretation / selection history 연동
- first validation

### C. quarterly quality+value prototype 구현

- runtime wrapper
- single strategy UI
- interpretation / selection history 연동
- first validation

### D. quarterly compare / research surface 확장

- compare 지원 범위 검토
- history / prefill / drilldown에 quarterly context 연결
- annual vs quarterly comparative research path 초안

### E. quarterly promotion readiness 판단

- research-only 유지 기준
- public candidate 진입 기준 초안
- validation checklist 작성

## 범위 밖

- intramonth event engine
- third overlay / new risk engine
- full public promotion 확정
- quarterly broad universe 대규모 operatorization

## 추천 구현 순서

1. quarterly family scope / naming / role decision
2. quarterly value prototype first pass
3. quarterly quality+value prototype first pass
4. quarterly interpretation / history parity
5. quarterly compare integration decision and first pass
6. quarterly validation rerun
7. promotion readiness criteria draft
8. docs / checklist / next-step sync

## 완료 기준

Phase 8 current chapter는 최소 아래가 충족되면 closeout-ready로 본다.

- quarterly value prototype가 single strategy에서 실행 가능함
- quarterly quality+value prototype가 single strategy에서 실행 가능함
- quarterly family의 interpretation / history surface가 정리되어 있음
- compare integration 여부가 문서와 코드 기준으로 정리되어 있음
- phase-specific manual test checklist가 작성되어 있음

## 현재 상태

- phase direction:
  - `opened`
- current chapter focus:
  - `quarterly strategy family build-out first`
  - `promotion readiness second`
- current implementation state:
  - `quarterly family first pass implemented`
  - `manual validation pending`
