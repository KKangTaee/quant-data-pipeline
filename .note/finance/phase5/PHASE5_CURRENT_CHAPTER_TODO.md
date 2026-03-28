# Phase 5 Current Chapter TODO

## 목적

이 문서는 Phase 5 첫 챕터를
strict factor strategy library 정리와
risk overlay 설계 관점에서 관리하기 위한 작업 보드다.

상위 계획 문서:
- `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md`

선행 문서:
- `.note/finance/phase4/PHASE4_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase4/PHASE4_COVERAGE1000_AND_VALUE_STRICT_CLOSEOUT.md`

---

## 현재 챕터 범위

현재 챕터의 목표:

1. strict factor baseline 전략을 비교 가능한 기준으로 정리한다
2. compare 화면의 strict factor advanced-input parity를 보강한다
3. risk overlay 요구사항과 구현 경계를 고정한다
4. first overlay candidate를 하나 선정한다
5. UI/runtime 노출 범위를 구현 가능한 수준으로 정리한다
6. strict managed preset을 실전형 운영 기준으로 재정의한다

---

## 큰 TODO 보드

### A. Baseline Strategy Library
상태:
- `completed`

세부 작업:
- `[completed]` strict family baseline 정리
  - `Quality`
  - `Value`
  - `Quality + Value`
- `[completed]` 비교 기준 preset / 기간 / top-N 초안 고정
- `[completed]` 현재 interpretation / compare gap 정리

완료 기준:
- overlay 추가 전 baseline 비교 기준이 문서로 고정되어 있어야 함

---

### B. Risk Overlay Requirement Definition
상태:
- `completed`

세부 작업:
- `[completed]` overlay 대상 전략 범위 확정
  - quality only / value only / multi-factor 포함 여부
- `[completed]` overlay signal 후보 정리
  - trend filter
  - market regime
  - drawdown / volatility guard
- `[completed]` cash / defensive asset / partial de-risk 방식 선택지 정리
- `[completed]` intramonth vs month-end-only decision 초안

완료 기준:
- first overlay rule을 선택할 수 있을 정도로 요구사항이 좁혀져 있어야 함

---

### C. Compare Advanced-Input Parity
상태:
- `completed`

세부 작업:
- `[completed]` compare에서 strict factor 전략별 advanced input override 범위 정리
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- `[completed]` 공통 입력과 전략별 입력 분리
  - 공통:
    - `timeframe`
    - `option`
  - 전략별:
    - factor set
    - `top_n`
    - 향후 overlay input
- `[completed]` compare prefill / override schema 영향 정리

완료 기준:
- compare 화면에서 strict factor 전략도 strategy-specific advanced input을 조절할 수 있어야 함

---

### D. First Overlay Candidate
상태:
- `completed`

세부 작업:
- `[completed]` first overlay 추천안 확정
  - 현재 추천: `Trend Filter Overlay`
- `[completed]` input contract 초안
  - benchmark 여부
  - MA window
  - cash / defensive asset choice
- `[completed]` result schema 영향 정리
  - overlay event 기록 방식

완료 기준:
- 구현 가능한 first overlay candidate 1개가 확정되어 있어야 함

---

### E. Quarterly Strict Family Expansion Candidate
상태:
- `completed`

세부 작업:
- `[completed]` quarterly strict family가 실제로 필요한 전략 범위 정리
  - quality only / value only / multi-factor 포함 여부
- `[completed]` quarterly statement shadow coverage audit
- `[completed]` annual 대비 runtime / freshness / point-in-time 차이 정리
- `[completed]` public candidate로 바로 열지, research-only path로 둘지 판단

완료 기준:
- quarterly strict family를 언제 어떤 범위로 열지 판단할 수 있을 정도의 근거가 정리되어 있어야 함

---

### H. Overlay On/Off Validation
상태:
- `completed`

세부 작업:
- `[completed]` canonical compare preset 기준 overlay on/off 수치 수집
- `[completed]` wide preset sanity check 수집
- `[completed]` quality / value / multi-factor별 성격 차이 정리

완료 기준:
- first overlay를
  public candidate / research toggle 관점에서 해석할 수 있는 결과가 문서화되어 있어야 함

---

### I. Stale Reason Classification And Selection Interpretation
상태:
- `completed`

세부 작업:
- `[completed]` strict preflight stale / missing reason heuristic 추가
- `[completed]` reason summary와 classification table UI 노출
- `[completed]` selection history interpretation summary 추가
- `[completed]` overlay rejection frequency 시각화 추가

완료 기준:
- stale / missing 경고와
  overlay / cash fallback 해석이
  사용자가 읽을 수 있는 수준으로 정리되어 있어야 함

---

### F. Runtime / UI Handoff Preparation
상태:
- `completed`

세부 작업:
- `[completed]` runtime wrapper 경계 초안
- `[completed]` UI advanced input 노출 범위 초안
- `[completed]` compare / history 연동 포인트 정리

완료 기준:
- overlay first-pass 구현이 바로 가능한 handoff 수준이어야 함

---

### G. Historical Managed Universe Policy
상태:
- `completed`

세부 작업:
- `[completed]` strict preset은 run-level static universe를 유지한다는 정책 고정
- `[completed]` selected end date freshness는 preflight 경고 용도라는 점 명문화
- `[completed]` single / compare strict preset을 historical semantics로 되돌림
- `[completed]` UI tooltip / preflight에 historical-backtest 설명 추가
- `[completed]` stale reason classification first pass 구현

완료 기준:
- historical backtest에서
  preset universe를 run-level에서 임의 교체하지 않는 원칙이 고정되어 있어야 함

---

## 현재 작업 중 항목

현재 `in_progress`:
- `없음`

바로 다음 체크 대상:
- `overlay-enabled strict family 사용자 검증`
- `selection interpretation / stale classification UX 확인`
- `next chapter에서 second overlay 착수 여부 확정`
- `quarterly strict family를 실제로 열 시점 결정`

---

## 현재 진척도

- Phase 5 first chapter:
  - 약 `90%`

판단 근거:
- baseline comparative research와 compare advanced-input parity가 구현되었고,
- month-end trend filter overlay first pass가
  strict family single / compare / history / interpretation 경로까지 연결되었으며,
- quarterly / second-overlay review 문서도 함께 정리되었다.
- 또한 overlay on/off validation과
  stale reason classification / selection interpretation 보강까지 끝난 상태다.
- 또한 strict managed preset은
  historical backtest 기준의 static-universe semantics로 정리되었다.
