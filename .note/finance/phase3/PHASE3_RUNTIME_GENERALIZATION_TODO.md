# Phase 3 Runtime Generalization TODO

## 목적
이 문서는 Phase 3의 다음 실행 챕터를
runtime 일반화와 Phase 4 handoff 준비 관점에서 관리하기 위한 작업 보드다.

상위 계획 문서:
- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`

선행 문서:
- `.note/finance/phase3/PHASE3_CHAPTER1_COMPLETION_SUMMARY.md`

---

## 현재 챕터 범위

현재 챕터의 목표:

1. DB-backed runtime 경로를 sample helper 수준에서 engine/runtime 공통 경로로 확장한다
2. 전략 실행 계층이 loader 경계에 더 자연스럽게 올라가도록 정리한다
3. Phase 4 UI에서 호출 가능한 최소 runtime entrypoint를 준비한다

---

## 큰 TODO 보드

### A. Runtime Path Generalization
상태:
- `completed`

세부 작업:
- `[completed]` engine 기준 DB-backed runtime entrypoint 정리
  - sample helper가 아니라 engine 쪽 공개 진입점 기준으로 실행 경로를 표준화
- `[completed]` loader -> strategy input adapter 재사용성 점검
  - price loader 출력이 여러 price-only 전략에서 공통으로 재사용 가능한지 검토
- `[completed]` legacy direct-fetch path와 DB-backed path 역할 분리
  - 기존 외부 직접조회 예시와 DB 기반 경로의 책임을 문서/코드에서 더 명확히 분리

완료 기준:
- 전략 실행 시 어떤 경로를 써야 하는지 혼란이 줄고, DB-backed runtime이 공통 경로로 설명 가능해야 함

---

### B. Strategy Runtime Alignment
상태:
- `completed`

세부 작업:
- `[completed]` price-only 전략 공통 실행 패턴 정리
  - Equal Weight 외 다른 price-only 전략도 같은 loader/runtime 계약을 탈 수 있게 정리
- `[completed]` future factor/fundamental 전략 연결 포인트 정리
  - factors / fundamentals loader가 전략 runtime에 어떻게 연결될지 경계 정리
- `[completed]` strategy input contract 문서 보강
  - runtime이 기대하는 입력 형태를 다음 단계에서 바로 쓸 수 있게 명시

완료 기준:
- 다음 전략 확장 작업이 sample별 ad hoc 연결이 아니라 공통 runtime 규칙 위에서 진행 가능해야 함

---

### C. Validation Harness
상태:
- `completed`

세부 작업:
- `[completed]` repeatable DB-backed smoke scenario 정리
  - 최소 검증에 사용할 심볼 세트 / 기간 / 기대 확인 포인트를 고정
- `[completed]` loader/runtime 검증 예시 정리
  - 이후 UI 연결 전에도 빠르게 재검증 가능한 예시 경로 문서화
- `[completed]` 후속 warning/cleanup backlog 분리
  - 예: `transform.py` warning, deeper yfinance optimization 등을 별도 후속 항목으로 분리

완료 기준:
- 변경 후 재검증 절차가 문서 기준으로 간단히 반복 가능해야 함

---

### D. Phase 4 Handoff Preparation
상태:
- `completed`

세부 작업:
- `[completed]` UI 호출용 최소 runtime function 후보 정의
  - 웹 UI에서 바로 호출 가능한 최소 backtest 실행 함수 후보 정리
- `[completed]` user-facing input set 초안 정리
  - tickers / universe / period / rebalance / strategy selection 중 최소 입력 집합 정리
- `[completed]` 결과 반환 형태 초안 정리
  - UI가 기대할 결과 DataFrame / 요약 지표 / 차트 입력 구조 초안 정리

완료 기준:
- 다음 Phase 4에서 전략 실행 UI를 붙일 때, 호출 경로와 입력/출력 계약이 이미 어느 정도 고정되어 있어야 함

---

## 현재 작업 중 항목

현재 `in_progress`:
- `없음`

바로 다음 체크 대상:
- `Phase 3 runtime generalization chapter completion review`

---

## 현재 진척도

- Phase 3 runtime generalization chapter:
  - 약 `100%`

판단 근거:
- engine 기준 DB-backed runtime entrypoint refinement는 시작되었고
- DB-backed sample warmup 정렬 문제와 sample parity 검증이 해결되었고
- direct-fetch path vs DB-backed path 역할 분리도 정리되었지만
- price-only 전략 공통 runtime 시작 패턴도 정리되었지만
- factor/fundamental 전략 연결 포인트도 정리되었지만
- strategy input contract도 정리되었지만
- repeatable smoke scenarios도 정리되었지만
- loader/runtime 예시 정리도 끝났고
- cleanup backlog 분리도 끝났지만
- UI runtime function 후보도 정리됐지만
- user-facing input set도 정리됐지만
- result bundle/output contract도 정리되었다
