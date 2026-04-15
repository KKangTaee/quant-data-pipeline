# Phase 20 Current Candidate Compare Re-entry First Work Unit

## 이 문서는 무엇인가
- `Phase 20`의 첫 실제 구현 단위로,
  current candidate를 `Compare & Portfolio Builder`로 다시 보내는 UI 동선을 정리한 문서다.

## 목적
- strongest candidate와 near-miss를 문서에서만 다시 찾는 흐름을 줄인다.
- `Compare & Portfolio Builder` 안에서 current candidate를 바로 다시 불러오게 만든다.
- 이후 `weighted portfolio`와 `saved portfolio` 흐름으로 이어질 준비를 만든다.

## 쉽게 말하면
- 지금까지는 좋은 후보를 찾아도,
  다시 비교하려면 문서를 열고 설정을 손으로 다시 맞추는 경우가 많았다.
- 이번 작업은
  **"좋은 후보를 다시 compare로 보내는 첫 번째 바로가기"**
  를 만든 것이다.

## 왜 필요한가
- `Phase 20`의 핵심은 후보를 더 찾는 것이 아니라,
  이미 찾은 후보를 더 쉽게 다시 쓰는 것이다.
- current candidate가 문서에만 머물면
  compare / weighted / saved workflow가 실제 작업 흐름으로 이어지기 어렵다.
- 그래서 먼저 current candidate를 compare로 다시 보내는 재진입 동선을 여는 것이 자연스럽다.

## 이 작업이 끝나면 좋은 점
- current anchor와 near-miss를 더 빠르게 compare로 다시 보낼 수 있다.
- `Compare & Portfolio Builder`가 단순 비교 화면이 아니라
  current candidate 재진입 화면으로도 쓰이기 시작한다.
- 다음 작업에서 weighted portfolio와 saved portfolio까지 이어 붙이기 쉬워진다.

## 이번 작업에서 한 일
- `Compare & Portfolio Builder` 상단에
  `Current Candidate Re-entry` surface를 추가했다.
- quick action 두 가지를 제공한다.
  - `Load Current Anchors`
  - `Load Lower-MDD Near Misses`
- 필요하면 후보를 직접 골라
  `Load Selected Candidates Into Compare`
  로 보낼 수 있게 했다.
- current candidate registry를 읽어
  family / role / title / CAGR / MDD / gate 상태를 표로 다시 보여주게 했다.
- 같은 family 후보를 한 번에 둘 이상 compare로 보내지 않도록 validation을 넣었다.

## 현재 구현 범위
- 현재 compare re-entry 대상은
  current candidate registry의 strict annual current 후보들이다.
- 즉 지금은:
  - `Value`
  - `Quality`
  - `Quality + Value`
  strict annual current candidate / near-miss 기준으로 동작한다.

## 검증
- `python3 -m py_compile app/web/pages/backtest.py`
- `.venv/bin/python` import smoke
- current candidate registry load / compare-prefill helper smoke

## 다음 작업
- compare에서 weighted portfolio builder로 넘어가는 흐름을 더 자연스럽게 만든다.
- saved portfolio를 다시 열었을 때
  compare re-entry와 rerun 행동이 더 직접적으로 보이게 만든다.

## 한 줄 정리
- 이번 작업은 **문서에 있는 current candidate를 UI compare 흐름으로 다시 끌고 오는 첫 번째 operator workflow hardening**이다.
