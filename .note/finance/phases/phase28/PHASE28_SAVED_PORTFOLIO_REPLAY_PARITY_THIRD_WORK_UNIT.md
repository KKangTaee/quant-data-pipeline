# Phase 28 Saved Portfolio Replay Parity Third Work Unit

## 어떤 문서인가

Phase 28의 세 번째 작업 단위 기록이다.
이번 작업은 저장된 포트폴리오를 다시 불러오거나 재실행할 때
전략별 설정과 weight가 충분히 남아 있는지 확인하기 쉽게 만든 작업이다.

## 쉽게 말하면

`Saved Portfolio`는 단순 결과 저장물이 아니다.
Compare에서 고른 전략들, 각 전략의 세부 설정, weighted portfolio 비중, date alignment를 다시 재현하기 위한 저장본이다.

이번 작업은 사용자가 저장 포트폴리오를 선택했을 때,
“이 저장본은 다시 불러오거나 재실행하기에 충분한 정보를 갖고 있나?”
를 먼저 표로 볼 수 있게 만든다.

## 왜 필요한가

Phase 28의 목적은 strategy family별 차이와 재진입 흐름을 흔들리지 않게 만드는 것이다.
History에서 단일 실행을 다시 열 수 있어도,
Saved Portfolio에서 strategy override나 weight가 빠지면
compare -> weighted portfolio -> saved replay 흐름은 신뢰하기 어렵다.

그래서 saved portfolio도 history처럼 재진입 가능성을 먼저 읽을 수 있어야 한다.

## 이번 작업에서 한 일

- `Backtest > Compare & Portfolio Builder > Saved Portfolios`에서 저장 포트폴리오를 선택하면
  `Saved Portfolio Replay / Load Parity Snapshot`을 보여준다.
- 표는 아래 항목을 확인한다.
  - Compare 공용 입력
  - 전략 목록
  - Weight / Date Alignment
  - Strategy Override Map
  - 전략별 핵심 override 저장 상태
- `Strategy Override Summary` 접힘 영역을 추가해 strategy별 override를 사람이 읽기 쉬운 표로 줄여 보여준다.
- saved portfolio replay로 남는 history context에는 `weights_percent`도 함께 남긴다.

## 기대 효과

- `Load Saved Setup Into Compare`를 누르기 전에 어떤 값이 다시 채워질지 볼 수 있다.
- `Replay Saved Portfolio`를 누르기 전에 전략별 override와 weight가 맞는지 확인할 수 있다.
- annual strict, quarterly prototype, GRS, GTAA 등 서로 다른 전략 family가 저장 포트폴리오 안에서 어떻게 섞였는지 읽기 쉬워진다.

## 주의할 점

- 이 표는 투자 판단표가 아니다.
- 저장 포트폴리오의 재현 가능성과 UI 복원 가능성을 확인하는 QA 표다.
- 정확한 전체 payload는 `Compare Context`나 `Raw Record` 탭에서 확인한다.

## 확인 위치

- UI:
  - `Backtest > Compare & Portfolio Builder > Saved Portfolios`
  - 저장 포트폴리오 선택
  - `Saved Portfolio Replay / Load Parity Snapshot`
- 코드:
  - `app/web/pages/backtest.py`

## 한 줄 정리

Phase 28 세 번째 작업은 saved portfolio를 다시 열거나 재실행할 때
전략별 설정과 weight가 충분히 남아 있는지 화면에서 먼저 확인하게 만든 작업이다.
