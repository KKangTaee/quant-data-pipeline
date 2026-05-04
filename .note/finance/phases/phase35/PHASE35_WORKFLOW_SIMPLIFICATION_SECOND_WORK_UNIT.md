# Phase 35 Workflow Simplification Second Work Unit

## 목적

두 번째 작업은 별도 후속 가이드 workflow를 active Backtest flow에서 제거하는 것이다.

## 쉽게 말하면

기존에는 Final Review 뒤에 또 하나의 마지막 확인 탭을 만들려고 했지만,
현재 제품 단계에서는 과하다.
그래서 사용자 흐름을 아래처럼 줄였다.

```text
Portfolio Proposal -> Final Review -> 최종 판단 완료
```

## 왜 필요한가

- 저장과 확인 단계가 계속 늘어나면 사용자가 흐름을 신뢰하기 어렵다.
- Final Review가 최종 판단 원본이므로, 별도 후속 탭이 또 판단처럼 보이면 역할이 겹친다.
- 지금은 최종 후보 선정 기능을 기본적으로 완성하는 것이 우선이다.

## 구현한 내용

- Backtest workflow option에서 별도 후속 가이드 panel을 제거했다.
- `app/web/pages/backtest.py`의 후속 panel dispatch를 제거했다.
- `app/web/backtest_post_selection_guide.py`와 helper module을 제거했다.
- `Backtest > Final Review`가 마지막 active workflow panel이 되게 했다.

## 결과

Backtest workflow navigation은 아래 순서로 끝난다.

```text
Single Strategy
-> Compare & Portfolio Builder
-> Candidate Review
-> Portfolio Proposal
-> Final Review
```

History와 Candidate Library는 기존처럼 Operations 보조 도구로 유지한다.
