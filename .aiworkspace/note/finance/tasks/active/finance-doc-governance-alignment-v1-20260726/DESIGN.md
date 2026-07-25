# Finance Document Governance Alignment V1 Design

## 이걸 하는 이유?

핵심 문서 네 개는 현재 역할 중심으로 재구성되었지만, 작업 지침·스킬·phase 자동화·상태 포인터는 과거의
“모든 작업에서 INDEX, ROADMAP, root log를 함께 갱신한다”는 패턴을 아직 요구한다.
이 상태에서는 새 문서 역할이 다시 흐려지고, AI와 사람이 서로 다른 위치를 현재 상태의 기준으로 읽게 된다.

이번 작업은 문서 본문을 다시 개편하는 작업이 아니라, 앞으로 문서를 수정하는 규칙과 상태 판정 방식을
현재 문서 구조에 맞추는 운영 계약 정렬이다.

## 현재 문제

1. `AGENTS.md`와 `finance-task-intake`의 시작 읽기 순서가 `PRODUCT_DIRECTION.md`를 빠뜨린다.
2. `finance-doc-sync`는 평범한 task closeout에도 INDEX, ROADMAP, root log 갱신을 사실상 요구한다.
3. `finance-integration-review`는 INDEX와 ROADMAP을 완료 이력 저장소처럼 병합하도록 안내한다.
4. phase bootstrap과 hygiene checker가 과거 `phase<N>` 및 `CURRENT_CHAPTER_TODO` 구조를 전제로 한다.
5. task manifest와 root handoff pointer가 Roadmap의 `Active / Paused / Verification-Only` 상태와 다르다.
6. 일부 테스트가 집중 flow 문서가 아니라 ROADMAP 또는 root log의 특정 문구를 제품 계약으로 사용한다.

## 설계 원칙

### 1. 문서 역할에 따라 갱신한다

| 변경 유형 | 기본 소유 문서 |
|---|---|
| 제품 약속, 사용자 여정, 원칙, non-goal | `PRODUCT_DIRECTION.md` |
| 현재 코드·화면·저장소 소유 경계 | `PROJECT_MAP.md`와 상세 architecture/flow/data 문서 |
| 현재 baseline, Active/Paused/Verification-Only, 다음 결정 | `ROADMAP.md` |
| 문서 탐색 구조와 읽기 순서 | `INDEX.md` |
| 실행 과정과 완료 이력 | task/phase 문서 |
| 짧은 인수인계 | root handoff log |

평범한 task closeout은 task 문서만 갱신하는 것이 정상이다. canonical 문서가 실제로 바뀌지 않았다면
“갱신 없음”을 정상 결과로 기록한다.

### 2. 상태 판단 우선순위를 고정한다

- 구현 및 소유 사실: 실제 코드 > 해당 영역의 집중 durable doc > task status
- workflow 상태: 명시적 사용자 결정 > 정규화된 task/phase `STATUS.md` > compact manifest > Roadmap 요약 > root log
- 제품 우선순위: 명시적 사용자 결정 > Roadmap
- root log는 상태 권위가 아니라 handoff pointer다.

새로 만들거나 이번 작업에서 손대는 task/phase `STATUS.md`에는
`State: active | paused | verification_only | complete | blocked` 중 하나를 사용한다.
기존 `Status:` 문서는 즉시 일괄 이관하지 않고, 이후 해당 task를 다시 수정할 때 점진적으로 정렬한다.

### 3. phase 구조를 현재 계약으로 통일한다

새 phase bundle은 아래 여섯 파일만 만든다.

```text
phases/active/<phase-id>/
  PLAN.md
  DESIGN.md
  TASKS.md
  STATUS.md
  RISKS.md
  INTEGRATION.md
```

phase 생성은 명시적으로 요청된 phase-managed work에만 사용한다. 실제 실행 상세는 active task에 둔다.
과거 `PHASE<N>_*`, `CURRENT_CHAPTER_TODO`, completion/next-phase skeleton은 더 만들지 않는다.

### 4. 자동 검사는 잘못된 갱신을 강제하지 않는다

- phase 문서 변경만으로 `CURRENT_CHAPTER_TODO`, INDEX, root log를 요구하지 않는다.
- INDEX는 문서 탐색 구조가 달라질 때만 검토 대상으로 본다.
- root log는 고신호 handoff가 필요한 경우에만 갱신하며, durable doc 변경의 필수 짝이 아니다.
- generated artifact와 strategy report/registry 안전 검사는 보존한다.
- hygiene checker는 현재처럼 advisory 도구로 유지한다.

## 상태 정렬 범위

현재 Roadmap 기준 상태를 task pointer에 반영한다.

- Active: 없음
- Paused: `overview-sentiment-cnn-aaii-v1-20260719`
- Verification-Only:
  - `portfolio-monitoring-chart-zoom-pan-v1-20260719`
  - `market-movers-chart-navigation-polish-v1-20260721`

기존 완료 이력과 폴더는 보존한다. 491개 task 상태 문서의 일괄 마이그레이션, root log 전체 압축,
retained task/phase 이동은 이번 범위가 아니다.

## 검증 전략

1. phase bootstrap과 hygiene 분류/체크를 import 가능한 순수 함수 수준에서 테스트한다.
2. 새 phase bundle의 경로와 여섯 파일 계약을 실패 테스트로 먼저 고정한다.
3. 일반 task/phase 문서 변경이 INDEX와 root log 경고를 만들지 않는지 검증한다.
4. 잘못된 service contract 테스트는 집중 flow/task 문서를 읽도록 교정한다.
5. 변경한 skill source와 runtime mirror를 각각 `quick_validate.py`로 검증하고 서로 동일한지 확인한다.
6. `git diff --check`, Python compile, targeted unittest를 실행한다.

## 제외 범위

- Finance UI 또는 서비스 로직 변경
- registry, saved portfolio, run history, QA 이미지 변경
- 모든 과거 task/phase 상태의 일괄 변환
- root handoff log의 전면 압축
- `main-dev`와의 branch 통합
