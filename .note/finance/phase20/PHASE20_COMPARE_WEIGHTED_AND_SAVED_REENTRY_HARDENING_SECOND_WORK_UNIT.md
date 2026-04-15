# Phase 20 Compare Weighted And Saved Re-entry Hardening Second Work Unit

## 이 문서는 무엇인가
- `Phase 20` 두 번째 실제 구현 단위로,
  compare -> weighted portfolio -> saved portfolio 흐름을 더 자연스럽게 만든 작업을 정리한 문서다.

## 목적
- compare 결과가 "그냥 표"가 아니라 다음 행동으로 이어지는 작업 단위처럼 보이게 만든다.
- weighted portfolio와 saved portfolio에서도 현재 compare source 맥락이 이어지게 만든다.
- 저장된 포트폴리오를 다시 열었을 때 다음 행동이 더 직접적으로 보이게 만든다.

## 쉽게 말하면
- 이제는
  - 어디서 온 compare인지
  - 이 compare 결과를 다음에 어떻게 저장하고 다시 쓸지
  - 저장된 포트폴리오를 열었을 때 무엇을 누르면 되는지
  가 더 잘 보이게 만든 작업이다.

## 왜 필요한가
- `Phase 20`의 핵심은 후보를 다시 쓰는 흐름을 정리하는 것이다.
- current candidate를 compare로 다시 보내는 것만으로는 부족하고,
  그 compare 결과가 weighted portfolio와 saved portfolio까지 자연스럽게 이어져야
  operator workflow가 실제로 완성된다.

## 이 작업이 끝나면 좋은 점
- compare 결과가 어떤 후보 묶음에서 왔는지 더 바로 알 수 있다.
- weighted portfolio를 만들 때 지금 보고 있는 compare bundle의 출처와 다음 행동이 더 분명해진다.
- saved portfolio를 다시 열었을 때
  `Edit In Compare`와 `Replay Saved Portfolio` 같은 행동이 더 직관적으로 읽힌다.

## 이번 작업에서 한 일
- compare source context를 session state로 유지하도록 보강했다.
  - current candidate bundle에서 온 경우
  - saved portfolio에서 다시 들어온 경우
  를 구분한다.
- `Weighted Portfolio Builder` 위에
  `Current Compare Bundle` 요약 surface를 추가했다.
  - source
  - label
  - selected strategies
  - registry ids / stored weights
  를 같이 볼 수 있다.
- weighted portfolio meta에도 compare source context를 남기도록 연결했다.
- saved portfolio 저장 시 source context를 같이 저장하도록 보강했다.
- saved portfolio surface를 더 직접적인 operator 용어로 바꿨다.
  - `Load Into Compare` -> `Edit In Compare`
  - `Run Saved Portfolio` -> `Replay Saved Portfolio`
- saved portfolio detail에
  `Source & Next Step` 탭을 추가했다.

## 검증
- `python3 -m py_compile app/web/pages/backtest.py`
- `.venv/bin/python` import smoke
- current candidate registry helper smoke
- refinement hygiene script

## 남은 확인
- manual UI validation으로
  - current candidate -> compare
  - compare -> weighted
  - weighted -> save
  - saved -> edit / replay
  흐름을 실제로 다시 확인하면 된다.

## 한 줄 정리
- 이번 작업은 **compare 결과가 weighted/saved workflow로 이어지는 실제 작업 단위처럼 느껴지도록 맥락과 다음 행동을 붙이는 hardening**이다.
