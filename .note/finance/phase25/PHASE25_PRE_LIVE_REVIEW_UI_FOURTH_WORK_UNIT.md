# Phase 25 Pre-Live Review UI Fourth Work Unit

## 이 문서는 무엇인가

이 문서는 `Phase 25`의 네 번째 작업 단위인
`Pre-Live Review UI`를 정리한다.

세 번째 작업에서 current candidate를 Pre-Live 기록 초안으로 바꾸는 helper를 만들었다면,
이번 작업은 같은 흐름을 Backtest 화면에서 직접 확인하고 저장할 수 있게 만든 단계다.

## 쉽게 말하면

터미널에서 helper 명령을 치지 않아도,
`Backtest > Pre-Live Review` 화면에서 후보를 고르고
`paper_tracking`, `watchlist`, `hold`, `reject`, `re_review` 중 하나로 저장할 수 있게 했다.

저장 전에는 JSON 초안만 보여주고,
사용자가 `Save Pre-Live Record`를 눌러야 실제 registry에 기록된다.

## 왜 필요한가

helper만 있으면 개발자나 agent는 쓸 수 있지만,
사용자가 QA하거나 운영 흐름을 이해하기에는 불편하다.

Pre-Live는 용어와 상태가 헷갈리기 쉬운 단계이므로,
화면에서 아래 내용이 같이 보여야 한다.

- 어떤 current candidate에서 왔는지
- Real-Money 신호가 무엇인지
- 기본 추천 Pre-Live 상태가 무엇인지
- 운영자가 이유와 다음 행동을 수정할 수 있는지
- 저장된 기록을 다시 볼 수 있는지

## 이번 작업에서 만든 것

Backtest panel에 `Pre-Live Review`를 추가했다.

화면 구성:

- `Create From Current Candidate`
  - current candidate 목록을 보여준다.
  - 후보를 하나 선택한다.
  - Real-Money 신호와 기본 추천 Pre-Live 상태를 보여준다.
  - `Operator Reason`, `Next Action`, `Review Date`를 확인하거나 수정한다.
  - 저장 전 JSON 초안을 보여준다.
  - `Save Pre-Live Record`를 눌러야 실제 registry에 저장한다.

- `Pre-Live Registry`
  - 이미 저장된 Pre-Live active record 목록을 보여준다.
  - 개별 record raw JSON을 inspect할 수 있다.

## 중요한 경계

- 이 UI는 live trading을 여는 화면이 아니다.
- `paper_tracking`도 실제 돈을 넣는다는 뜻이 아니다.
- 이 UI는 `Real-Money 검증 신호`를 보고 다음 운영 행동을 기록하는 화면이다.
- 저장 파일은 `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`이다.

## 이번 작업에서 하지 않은 것

- broker 주문
- 실전 투자 승인
- 자동 deployment readiness 판정
- paper tracking 성과 자동 갱신

이 작업은 "후보를 실전 전 운영 상태로 기록할 수 있는가"까지만 다룬다.

## QA에서 확인할 것

- `Backtest > Pre-Live Review` 패널이 보이는지
- current candidate 목록이 보이는지
- 후보를 선택하면 기본 추천 상태가 자연스럽게 나오는지
- 저장 전 JSON 초안이 보이는지
- `Save Pre-Live Record`를 누른 뒤 registry tab에서 record가 보이는지
- 저장된 record가 투자 승인처럼 보이지 않고 운영 기록으로 읽히는지

## 한 줄 정리

이번 작업은 Phase 25의 Pre-Live 운영 흐름을
터미널 helper에서 사용자-facing Backtest 화면으로 연결한 것이다.
