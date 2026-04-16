# Phase 21 Research Automation And Experiment Persistence Plan

## 이 문서는 무엇인가
- `Phase 21`에서 어떤 자동화와 persistence를 먼저 만들지, 왜 지금 필요한지, 어떤 순서로 진행할지를 정리한 kickoff 문서다.

## 목적
- 반복되는 phase 문서 생성과 closeout 정리 작업을 자동화한다.
- current candidate를 machine-readable persistence로 남긴다.
- plugin / skill / hygiene workflow가 current candidate와 phase 문서를 더 안정적으로 다시 읽게 만든다.

## 쉽게 말하면
- 지금은 좋은 후보와 phase 문서가 잘 쌓이고 있지만,
  여전히 손으로 반복하는 일이 많다.
- `Phase 21`은
  **반복 작업을 줄이고, 다음 세션에서도 같은 흐름을 다시 타기 쉽게 만드는 단계**
  다.
- 즉:
  - 새 phase 문서 묶음을 손으로 만드는 문제
  - current candidate가 Markdown에만 있어 script가 쓰기 어려운 문제
  - hygiene / plugin workflow가 current candidate persistence를 잘 모르는 문제
  를 줄이는 phase다.

## 왜 필요한가
- `Phase 19`, `Phase 20`을 거치며 문서 구조와 operator workflow는 더 분명해졌다.
- 하지만 지금도 automation 관점에서는:
  - phase 문서를 열 때 반복 입력이 많고
  - current candidate를 machine-readable source로 다시 참조하기 어렵고
  - plugin/skill이 읽는 정보와 사람이 읽는 문서가 완전히 겹치지 않는다.
- 이 상태에서 바로 deep validation으로 가면,
  실험 수가 늘어날수록 정리 비용이 다시 커질 수 있다.

## 이 phase가 끝나면 좋은 점
- 새 phase 문서를 더 빠르게 열 수 있다.
- current candidate를 script와 plugin이 더 직접적으로 다시 읽을 수 있다.
- hygiene script가 candidate registry까지 같이 점검할 수 있다.
- `Phase 22` 이후 반복 rerun과 documentation sync가 더 안정적으로 이어질 준비가 된다.

## 이 phase에서 다루는 대상
- repo-local plugin scripts
- current candidate machine-readable persistence
- phase 문서 bootstrap workflow
- refinement hygiene workflow
- plugin / skill reference docs

## 현재 구현 우선순위
1. phase bundle automation
   - 쉽게 말하면:
     - 새 phase 문서 묶음을 한 번에 여는 script를 만든다.
   - 왜 먼저 하는가:
     - 최근 phase 운영 규칙과 template가 고정되었기 때문에 가장 먼저 자동화 효과가 나는 지점이다.
   - 기대 효과:
     - 다음 phase kickoff가 더 빠르고 일정해진다.
2. current candidate registry persistence
   - 쉽게 말하면:
     - current candidate를 JSONL registry로도 남긴다.
   - 왜 필요한가:
     - future automation과 plugin workflow가 strongest candidate를 다시 읽을 source가 필요하기 때문이다.
   - 기대 효과:
     - current candidate summary와 automation layer가 더 자연스럽게 연결된다.
3. workflow doc / hygiene integration
   - 쉽게 말하면:
     - 새 script와 registry를 existing skill, plugin, hygiene 흐름과 연결한다.
   - 왜 필요한가:
     - script만 있고 운영 문서가 안 맞으면 다음 세션에서 다시 잊히기 쉽기 때문이다.
   - 기대 효과:
     - 실제 반복 작업에서 더 자연스럽게 재사용된다.

## 이 문서에서 자주 쓰는 용어
- `Phase Bundle`
  - phase plan, TODO, completion, next-phase, checklist 문서 묶음
- `Current Candidate Registry`
  - current candidate를 JSONL로 남긴 machine-readable persistence 파일
- `Experiment Persistence`
  - 한 번 정한 후보나 scenario를 다음 세션에서도 다시 읽을 수 있게 남겨두는 것
- `Hygiene`
  - 문서, index, root logs, registry, generated artifact 상태를 함께 점검하는 작업

## 이번 phase의 운영 원칙
- practical automation first
  - 과한 자동화보다 지금 바로 쓰는 반복 작업부터 줄인다.
- bounded implementation
  - phase 문서 bootstrap, current candidate persistence, hygiene integration에 집중한다.
- minimal validation
  - script smoke test, list/validate command, hygiene check까지 수행한다.
- UI 변경 최소화
  - 이번 phase는 app surface보다 repo-local workflow automation을 우선한다.

## 이번 phase의 주요 작업 단위
- 첫 번째 작업:
  - phase bundle을 자동 생성하는 script를 추가한다.
- 두 번째 작업:
  - current candidate registry를 만들고 관리 script를 추가한다.
- 세 번째 작업:
  - hygiene script, plugin/skill docs, index/log를 새 workflow에 맞게 정리한다.

## 다음에 확인할 것
- phase bundle script가 실제로 다음 phase kickoff에서 시간을 줄이는가
- current candidate registry가 future plugin / automation source로 충분한가
- deep validation 전에 scenario persistence를 더 넓게 확장할 필요가 있는가

## 한 줄 정리
- `Phase 21`은 **반복되는 phase 문서 작업과 current candidate 관리를 자동화해서, 다음 연구가 더 재현 가능하게 이어지도록 만드는 phase**다.
