# Phase 20 Candidate Consolidation And Operator Workflow Hardening Plan

## 이 문서는 무엇인가
- `Phase 20`에서 무엇을 정리할지, 왜 지금 필요한지, 어떤 순서로 진행할지를 설명하는 kickoff 문서다.

## 목적
- strongest / near-miss candidate를 다시 보기 쉬운 형태로 정리한다.
- `Compare -> Weighted Portfolio -> Saved Portfolio` 흐름을 실제 operator workflow로 다듬는다.
- 다음 `Phase 21` 자동화와 `Phase 22` deep validation 전에 후보 관리 동선을 안정화한다.

## 쉽게 말하면
- 지금은 좋은 후보를 이미 찾았지만,
  다시 꺼내 보고, 비교하고, 저장하고, 조합하는 흐름이 아직 조금 산만하다.
- `Phase 20`은
  **좋은 후보를 "찾는 일"보다, 그 후보를 "다시 쓰기 쉽게 만드는 일"**
  에 가깝다.
- 즉:
  - 후보를 다시 찾기 위해 문서를 많이 뒤지는 문제
  - compare 결과를 weighted portfolio로 넘기는 흐름의 어색함
  - saved portfolio를 다시 실행하거나 수정할 때 느껴지는 끊김
  을 줄이는 단계다.

## 왜 필요한가
- 지금 strongest candidate와 near-miss는 이미 여러 문서에 잘 남아 있다.
- 하지만 실제 작업 흐름에서는
  - 어떤 후보를 지금 보고 있는지
  - 어떤 후보 조합을 전에 비교했는지
  - 어떤 weighted portfolio를 저장해뒀는지
  를 다시 따라가는 비용이 아직 있다.
- 이 상태에서 바로 `Phase 21` 자동화나 `Phase 22` deep validation으로 가면,
  좋은 후보를 관리하는 흐름이 덜 정리된 상태에서 연구만 더 쌓이게 될 수 있다.
- 그래서 먼저 operator workflow를 단단하게 만드는 것이 자연스럽다.

## 이 phase가 끝나면 좋은 점
- strongest / near-miss candidate를 더 빠르게 다시 찾을 수 있다.
- compare 결과를 weighted portfolio와 saved portfolio로 넘기는 흐름이 더 자연스러워진다.
- 문서, 히스토리, 저장된 포트폴리오가 서로 더 잘 연결된다.
- 이후 자동화와 deep validation도 어떤 대상을 관리하고 검증하는지 더 분명해진다.

## 이 phase에서 다루는 대상
- strict annual current candidate organization
- `Backtest > Compare & Portfolio Builder`
- `Saved Portfolio` 재진입 흐름
- candidate summary / bundle 문서화
- operator가 현재 후보를 다시 보는 workflow

## 현재 구현 우선순위
1. current candidate inventory와 workflow friction 정리
   - 쉽게 말하면:
     - 지금 후보를 다시 보려면 어디서 막히는지 먼저 정리한다.
   - 왜 먼저 하는가:
     - 실제 불편 지점을 먼저 잡아야 불필요한 UI 변경을 줄일 수 있다.
   - 기대 효과:
     - 이후 구현이 "막연한 개선"이 아니라 구체적인 불편 해결로 이어진다.
2. candidate bundle / re-entry flow 정리
   - 쉽게 말하면:
     - strongest candidate와 near-miss를 다시 compare나 weighted portfolio로 이어가기 쉽게 만든다.
   - 왜 필요한가:
     - 지금은 문서와 UI가 분리되어 있어, 다시 실행할 때 생각보다 많은 단계를 거친다.
   - 기대 효과:
     - operator가 후보를 다시 보고 비교하는 시간이 줄어든다.
3. saved portfolio usability hardening
   - 쉽게 말하면:
     - 저장된 포트폴리오를 다시 실행하거나 수정하는 흐름을 덜 헷갈리게 만든다.
   - 왜 필요한가:
     - compare 결과를 저장했다가 나중에 다시 이어가는 경험이 `Phase 20`의 핵심이기 때문이다.
   - 기대 효과:
     - 후보 관리가 문서 중심에서 UI workflow 중심으로 더 이동한다.

## 이 문서에서 자주 쓰는 용어
- `Current Candidate`
  - 지금 다시 보기 좋은 strongest candidate 또는 near-miss 후보
- `Candidate Bundle`
  - 다시 비교하거나 저장할 수 있도록 묶어둔 후보 세트
- `Operator Workflow`
  - 사용자가 후보를 열고, 비교하고, 저장하고, 다시 실행하는 실제 사용 흐름
- `Re-entry Flow`
  - 한 번 저장하거나 기록으로 남긴 결과를 다시 불러와 다음 작업으로 이어가는 흐름
- `Saved Portfolio`
  - compare 결과를 바탕으로 저장해둔 weighted portfolio 실행 단위

## 이번 phase의 운영 원칙
- workflow-first
  - 후보를 더 찾기보다, 현재 후보를 다시 쓰는 흐름을 먼저 정리한다.
- bounded implementation
  - 큰 구조 재설계보다 operator-facing 동선 정리에 집중한다.
- minimal validation
  - `py_compile`, import smoke, targeted UI 확인 위주로 간다.
- deep rerun 보류
  - broad integrated rerun은 `Phase 22` 전까지 다시 크게 열지 않는다.

## 이번 phase의 주요 작업 단위
- 첫 번째 작업:
  - 현재 candidate / compare / saved portfolio 흐름을 inventory처럼 정리하고,
    어디서 다시 보기 어렵고 어디서 흐름이 끊기는지 문서로 고정한다.
- 두 번째 작업:
  - strongest candidate를 compare / weighted portfolio 쪽으로 다시 넣는 동선을 더 짧고 분명하게 만든다.
- 세 번째 작업:
  - saved portfolio에서 다시 실행, 다시 비교, 다시 수정하는 재진입 흐름을 더 자연스럽게 만든다.

## 다음에 확인할 것
- current candidate summary가 실제 UI 동선과 더 잘 연결되는가
- compare 결과에서 weighted / saved portfolio로 넘어갈 때 불필요한 단계가 줄었는가
- saved portfolio를 다시 열었을 때 "다음에 무엇을 해야 하는지"가 더 분명해졌는가

## 현재 상태
- `practical closeout / manual_validation_pending`

## 현재 상태 요약
- first work unit에서 current candidate를 compare로 바로 다시 보내는 입구를 열었다.
- second work unit에서 compare source context를 weighted portfolio와 saved portfolio까지 이어,
  지금 보고 있는 compare bundle의 출처와 다음 행동이 더 직접적으로 보이게 만들었다.
- 즉 `Phase 20`은
  current candidate -> compare -> weighted portfolio -> saved portfolio
  재진입 흐름을 실제 operator workflow 기준으로 더 자연스럽게 읽히게 만든 상태다.

## 한 줄 정리
- `Phase 20`은 **좋은 후보를 더 많이 찾는 phase가 아니라, 지금 찾은 좋은 후보를 더 쉽게 다시 쓰게 만드는 phase**다.
