# Phase 5 Next Phase Preparation

## 목적

- Phase 5 첫 챕터 종료 이후,
  다음에 어떤 workstream이 가장 자연스럽게 이어지는지 정리한다.
- 새 phase를 성급히 열기보다,
  다음 후보와 준비 포인트를 명시해 둔다.

## 현재 출발점

Phase 5 first chapter 종료 시점 기준으로:
- strict annual family baseline 비교 기준이 정리되었다
- compare strict family advanced-input parity가 구현되었다
- first overlay(`month-end MA200 trend filter + cash fallback`)가 single / compare / history에 연결되었다
- overlay on/off 비교 결과가 문서화되었다
- stale / missing symbol heuristic classification이 붙었다
- selection interpretation이 실사용 가능한 수준으로 강화되었다
- strict managed preset은 historical-backtest semantics로 정리되었다
- Phase 5 manual test checklist까지 작성되었다

즉 다음 단계는
기본 strict family를 다시 만드는 것이 아니라,
**overlay 확장 / quarterly 확장 / strategy-library 비교 심화**
쪽으로 넘어가는 것이 자연스럽다.

## 다음 단계 후보

### 후보 1. Second Overlay Implementation

가장 자연스러운 다음 챕터 후보다.

현재 문서 기준 추천 후보:
- `Market Regime Overlay`

핵심 작업:
- signal 정의
- benchmark / regime input 정의
- cash / defensive 대응 방식 결정
- runtime first pass
- compare on/off validation

### 후보 2. Quarterly Strict Family Implementation

이미 review 문서는 준비되어 있고,
다음은 실제 code/runtime/UI로 올릴지 결정하는 단계다.

핵심 작업:
- quarterly strict quality / value / multi-factor 범위 확정
- coverage / runtime / freshness audit
- public candidate vs research-only path 판단

### 후보 3. Strategy Library Comparative Research Expansion

overlay를 더 늘리기 전에,
strict family 자체의 comparative research를 더 깊게 갈 수도 있다.

핵심 작업:
- quality / value / quality+value comparative report 고도화
- focused drilldown / interpretation polish
- canonical benchmark / preset guide 정리
- saved comparison read path 강화

### 후보 4. Project Operating-Model Refresh

Phase 5 closeout 시점은
project-level 운영 지침을 다시 점검하기에도 좋은 타이밍이다.

핵심 작업:
- `AGENTS.md` 재점검
- skills / references / 문서 흐름 점검
- 현재 자주 쓰는 실행 경로와 stale한 지침 구분
- phase closeout / checklist / doc-sync 규칙 보강

이 작업은 새 strategy 기능이라기보다,
다음 phase 진입 전 **개발 운영 모델 리프레시**에 가깝다.

## 추천 순서

현재 기준 추천 순서는 아래다.

1. `Project Operating-Model Refresh`
2. `Second Overlay Implementation`
3. `Quarterly Strict Family Implementation`

이유:
- 지금은 기능보다 문서/지침/skills/reference를 다시 정리하기에 매우 좋은 phase 경계다
- 그 다음 second overlay로 넘어가면,
  구현 방향과 문서 기준이 더 흔들리지 않는다
- quarterly strict family는 범위가 더 크고,
  overlay보다 데이터/coverage 부담이 커서 한 단계 뒤가 자연스럽다

## 지금 시점에서 확인할 것

- skill/지침/참조 문서가 현재 코드와 충분히 맞는지
- stale해진 phase 문구가 없는지
- 실제로 자주 쓰는 workflow가 문서/skill에 반영돼 있는지
- 다음 major chapter를
  `overlay`
  로 먼저 열지,
  `quarterly`
  로 먼저 열지

## 현재 상태

- Phase 5 first chapter closeout:
  - `completed`
- next-step candidate 정리:
  - `completed`
- next major chapter formal opening:
  - `not_opened`

즉 다음 chapter/phase는
사용자 확인 후 여는 것이 맞다.
