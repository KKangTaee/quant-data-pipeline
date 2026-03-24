# Phase 4 Factor / Fundamental Entry TODO

## 목적
이 문서는 Phase 4의 다음 챕터를
`price-only UI에서 factor / fundamental 전략 UI로 넘어가기 위한 준비 작업`
관점에서 관리한다.

상위 계획 문서:
- `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md`

선행 문서:
- `.note/finance/phase3/PHASE3_FACTOR_FUNDAMENTAL_RUNTIME_CONNECTIONS.md`
- `.note/finance/phase3/PHASE3_RUNTIME_STRATEGY_INPUT_CONTRACT.md`
- `.note/finance/phase3/PHASE3_UI_USER_INPUT_SET_DRAFT.md`

---

## 큰 TODO 보드

### A. Chapter Setup
상태:
- `completed`

세부 작업:
- `[completed]` 현재 price-only UI 챕터 종료 상태 정리
  - 첫 UI 챕터가 어디까지 구현되었는지 정리
- `[completed]` factor/fundamental 진입 챕터를 별도 보드로 분리
  - 다음 선택과 구현이 섞이지 않도록 새 보드로 분리

완료 기준:
- 다음 챕터의 범위와 출발점이 명확해야 함

---

### B. Runtime Entry Boundary
상태:
- `completed`

세부 작업:
- `[completed]` snapshot-first runtime 연결 기준 재정리
  - loader -> runtime connection -> strategy 3단 구조를 Phase 4 관점에서 재정리
- `[completed]` first public factor/fundamental runtime wrapper 형태 초안
  - UI가 직접 호출할 첫 wrapper의 입력/출력 형태를 고정
- `[completed]` strict PIT vs broad research 기본 모드 결정 보조 문서화
  - product-facing default와 research helper 역할을 구분
- `[completed]` broad-research first-pass wrapper 구현
  - quality snapshot 전략의 first public runtime path를 실제 코드로 열기
- `[completed]` statement-driven prototype runtime 구현
  - strict statement snapshot 기반 sample-universe prototype wrapper를 추가

완료 기준:
- UI가 호출할 첫 factor/fundamental runtime 경계가 문서상 고정되어 있어야 함

---

### C. First Strategy Candidate
상태:
- `completed`

세부 작업:
- `[completed]` 첫 전략 후보군 정리
  - value / quality / multi-factor 중 현실적인 first candidate 정리
- `[completed]` 사용자 선택용 옵션 문서 작성
  - 어떤 전략부터 올릴지 선택 가능하도록 장단점 정리
- `[completed]` 선택된 전략 기준 snapshot 컬럼 계약 확정
  - 실제로 어떤 컬럼이 필요할지 고정
- `[completed]` statement-driven sample-universe prototype 구현
  - strict statement snapshot으로 quality ranking이 실제로 돌아가는지 first-pass 검증
- `[completed]` statement -> fundamentals -> factors reusable mapping 정리
  - prototype 계산 로직을 data-layer reusable helper로 이동
- `[completed]` strict statement quality loader 정리
  - prototype/runtime가 직접 builder를 조합하지 않도록 loader read boundary 추가
- `[completed]` statement-driven shadow backfill first-pass
  - public broad tables를 건드리지 않고 shadow fundamentals/factors write path를 추가
- `[completed]` statement-driven shares/valuation fallback first-pass
  - shadow path에서 broad fundamentals nearest-period shares fallback을 연결

완료 기준:
- 첫 factor/fundamental 전략 후보가 사용자와 합의 가능한 상태여야 함

---

### D. UI Input Draft
상태:
- `completed`

세부 작업:
- `[completed]` snapshot 전략용 최소 입력 세트 초안
  - rebalance freq / universe / as-of mode / ranking 관련 입력 정리
- `[completed]` advanced input과 기본 input 경계 정리
  - first-pass에서 숨길 입력과 열 입력 구분

완료 기준:
- 첫 factor/fundamental 전략 UI form의 범위가 과하지 않게 정리되어 있어야 함

---

### E. First UI Exposure
상태:
- `completed`

세부 작업:
- `[completed]` Quality Snapshot Strategy를 single-strategy UI에 노출
  - Backtest selector에 다섯 번째 전략으로 연결
- `[completed]` history / prefill 경로에 quality 메타 연결
  - 저장 / 재실행 / form reload 흐름에 quality 전략 반영
- `[completed]` compare mode에서 quality first-pass 노출
  - quality 전략을 compare에도 포함
- `[completed]` strict annual quality public candidate 노출
  - broad quality를 유지한 채 strict annual path를 single / compare / history 흐름에 연결

완료 기준:
- 사용자가 UI에서 Quality Snapshot Strategy를 실행할 수 있어야 함
- broad path와 strict annual candidate를 비교 가능한 상태여야 함

---

## 현재 작업 중 항목

현재 `in_progress`:
- `없음`

바로 다음 체크 대상:
- `wider-universe annual coverage scope 결정 및 실행`

현재 보조 판단:
- sample-universe strict path 기준
  - `annual`이 `quarterly`보다 더 usable함
  - `quarterly`는 동작하지만 first active date가 더 늦음
  - wider-universe annual run 전 operator support는 first-pass 수준으로 준비됨
  - first stage top-100 run은 완료되었고, `80/100` strict annual coverage를 확인함
  - missing coverage 대부분은 foreign issuer라서 next stage는 scope refinement가 필요함
  - stage 2 US top-300 run은 완료되었고, `297/300` strict annual coverage를 확인함

---

## 현재 진척도

- Phase 4 factor/fundamental entry chapter:
  - 약 `82%`

판단 근거:
- price-only UI 챕터는 실질적으로 완료되었고
- 다음 챕터 보드가 열렸으며
- snapshot-first runtime 연결 원칙을 Phase 4 기준으로 다시 가져올 준비가 되었지만
- first public quality path는 열렸지만
- 더 긴 history / stricter quality path로 가려면
  `nyse_financial_statement_values` coverage 자체가 충분한지 먼저 확인해야 하는 상태였고,
- sample universe 기준 feasibility test + targeted backfill은 완료되었지만,
- annual period-limit semantics fix와 targeted canonical refresh 이후,
  sample-universe annual strict path는 `2016` 시작 statement-driven quality backtest가 실제로 가능한 수준까지 올라왔다
- 다만 strict statement snapshot을 직접 사용한 sample-universe prototype은 실제로 구현 및 검증되었고,
- 또한 이 경로는 이제 `statement -> fundamentals -> factors` reusable mapping으로도 정리되어,
  future rebuild path의 코드 뼈대가 생긴 상태다
- shadow table 방향도 실제 코드와 sample-universe write/read validation까지 열려 있고,
  annual strict shadow rebuild 역시 `2011~2025` 구간을 다루게 되었기 때문에,
  annual strict path를 public candidate로 올리는 단계까지 진행되었다
- 따라서 다음 결정은 저장 전략 자체보다
  broad quality와 strict annual quality를 어떤 원칙으로 함께 둘지,
  wider universe coverage를 먼저 늘릴지,
  그리고 hybrid shares fallback을 어디까지 허용할지를 정하는 쪽으로 이동했다
- 또한 wider-universe annual coverage를 위한
  `Extended Statement Refresh` live progress/operator support도 추가되었기 때문에,
  다음 단계는 실제 annual coverage scope를 정하고 실행하는 쪽으로 더 가까워졌다
- stage 1 top-100 annual run도 성공했기 때문에,
  다음 실제 작업은 `Profile Filtered Stocks 전체`보다
  `EDGAR 친화적 narrower stock scope`를 정하는 쪽이 더 자연스럽다
- stage 2 US top-300 annual run 결과까지 반영하면,
  annual strict path는 이제 public candidate 전략의 신뢰도를 논의할 수 있을 정도의 wider coverage 근거를 가진다
- 그리고 그 wider coverage 근거를 바탕으로,
  strict annual quality의 public 역할과 기본 universe도
  `US Statement Coverage 300` / `US Statement Coverage 100`
  기준으로 재정의되었다
