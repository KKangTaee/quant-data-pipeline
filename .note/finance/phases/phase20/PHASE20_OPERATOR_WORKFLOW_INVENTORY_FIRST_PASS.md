# Phase 20 Operator Workflow Inventory First Pass

## 이 문서는 무엇인가
- `Phase 20` 첫 번째 작업으로, 현재 후보 관리 흐름에서 어디가 불편한지 정리한 inventory 문서다.

## 목적
- `Value`, `Quality`, `Quality + Value` current candidate를 다시 보는 실제 경로를 정리한다.
- compare / weighted portfolio / saved portfolio 흐름에서 끊기는 지점을 고정한다.
- 다음 UI 개선이 어떤 문제를 풀어야 하는지 먼저 분명히 만든다.

## 쉽게 말하면
- 지금 기능이 없는 것이 아니라,
  **있는 기능을 다시 이어 쓸 때 약간씩 헷갈리는 부분이 남아 있다.**
- 이 문서는 "어디를 더 편하게 만들어야 하는가"를 먼저 정리하는 문서다.

## 왜 필요한가
- 후보는 문서로 잘 정리돼 있지만,
  실제로는 문서와 UI를 오가며 다시 실행해야 할 때가 많다.
- 이 상태에서 바로 UI를 바꾸면,
  보기에는 달라졌지만 실제 불편은 그대로 남을 수 있다.
- 그래서 먼저 현재 operator workflow의 불편 지점을 정리하는 것이 필요하다.

## 현재 기준으로 보이는 핵심 friction

### 1. current candidate는 잘 정리되어 있지만 UI 재진입 동선이 길다
- 현재 strongest / near-miss candidate는
  - strategy hub
  - one-pager
  - current candidates summary
  에 잘 정리돼 있다.
- 하지만 문서에서 바로 compare / weighted portfolio로 이어지는 흐름은 아직 약하다.

### 2. compare 결과를 저장 가능한 작업 단위로 인식하기 어렵다
- compare는 결과를 보여주지만,
  "이 후보 조합을 다음에 다시 보겠다"는 작업 단위로 느껴지기에는 아직 조금 부족하다.
- 즉 비교 결과가 결과 표에 가깝고,
  후보 묶음(candidate bundle)처럼 느껴지지는 않는다.

### 3. saved portfolio는 기능은 있지만 재진입 경험이 더 좋아질 수 있다
- 저장, 다시 실행, 다시 비교라는 큰 흐름은 있다.
- 다만 사용자가 저장된 포트폴리오를 다시 열었을 때
  - 무엇을 볼 수 있는지
  - 다음에 무엇을 눌러야 하는지
  - compare 흐름으로 어떻게 다시 이어지는지
  가 더 직접적으로 보이면 좋다.

## 첫 번째 작업 이후 바로 이어갈 우선순위

### 우선순위 1. current candidate를 compare 쪽으로 다시 보내는 흐름
- strongest candidate를 다시 비교하는 일이 가장 자주 발생할 가능성이 높다.
- 그래서 문서의 current candidate를 UI compare 흐름과 더 잘 연결하는 것이 첫 개선 후보다.

### 우선순위 2. weighted portfolio 결과를 저장 가능한 작업 단위로 더 분명하게 보이기
- weighted portfolio 결과가 단순 결과가 아니라
  "나중에 다시 볼 포트폴리오 조합"이라는 점이 더 잘 드러나야 한다.

### 우선순위 3. saved portfolio 재진입 흐름 개선
- 저장된 포트폴리오를 다시 열었을 때,
  rerun / inspect / load-into-compare 같은 다음 행동이 더 분명히 보여야 한다.

## 기대 효과
- 다음 UI 개선이 막연한 polish가 아니라 실제 불편 해결로 이어진다.
- current candidate summary와 compare/saved workflow가 더 자연스럽게 이어질 준비가 된다.

## 한 줄 정리
- `Phase 20` 첫 작업은 **지금 어디서 실제로 불편한지 먼저 고정해서, 이후 개선이 정확한 문제 해결이 되게 만드는 것**이다.
