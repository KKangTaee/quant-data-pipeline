# Plan

## 이걸 하는 이유?

Overview Market Intelligence 1차 구현은 실제로 사용할 수 있는 prototype 상태까지 왔다. 하지만 정식 기능으로 보기에는 earnings source 신뢰도, event lifecycle, 자동/반자동 refresh 기준, UI 검수 기준, 운영 acceptance gate가 아직 분리돼 있지 않다.

이 task는 바로 구현에 들어가기 전에 prototype을 production-ready 기능으로 끌어올리기 위한 phase와 task 구조를 다시 작성한다.

## Scope

- 정식화까지 몇 차 개발이 필요한지 판단한다.
- 새 productionization phase 문서 bundle을 작성한다.
- 각 task의 목적, 변경 파일, 검증 기준, dependency를 정리한다.
- 코드 구현은 하지 않는다.

## Done Criteria

- `.aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization/` 아래 phase 문서가 생성된다.
- `TASKS.md`에서 차수별 작업 순서와 acceptance gate를 확인할 수 있다.
- root handoff log에 다음 개발 phase 위치와 첫 task가 기록된다.
