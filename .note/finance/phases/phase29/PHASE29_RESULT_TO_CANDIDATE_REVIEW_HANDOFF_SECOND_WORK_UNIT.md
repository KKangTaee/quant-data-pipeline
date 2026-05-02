# Phase 29 Result To Candidate Review Handoff Second Work Unit

## 이 문서는 무엇인가

Phase 29의 두 번째 작업 단위 기록이다.
`Latest Backtest Run`과 `History` 결과를 `Candidate Review`의 후보 검토 초안으로 넘기는 흐름을 추가한 내용을 정리한다.

## 쉽게 말하면

백테스트 결과를 보고 "이거 후보로 볼 만한가?"라고 생각할 때,
바로 registry에 저장하지 않고 먼저 후보 검토 초안으로 읽을 수 있게 했다.

## 왜 필요한가

좋은 백테스트 결과가 나왔다고 해서 바로 current candidate가 되는 것은 아니다.
먼저 아래를 확인해야 한다.

- 이 결과가 current candidate 후보인지
- near-miss / watchlist 후보인지
- 단순 scenario 후보인지
- 데이터 신뢰성이나 Real-Money signal이 충분한지

그래서 이번 작업은 저장이 아니라 **후보 검토 초안**을 만드는 데 집중했다.

## 구현한 것

1. `Latest Backtest Run`에 `Candidate Review Handoff` 접힘 영역을 추가했다.
2. `Review As Candidate Draft` 버튼으로 최신 실행 결과를 `Candidate Review`로 보낼 수 있게 했다.
3. `History > Selected History Run > Actions For This History Run`에도 같은 버튼을 추가했다.
4. `Candidate Review > Candidate Intake Draft` 탭을 추가했다.
5. 후보 검토 초안에는 다음 정보를 담는다.
   - source kind
   - strategy key / strategy name
   - suggested record type
   - suggested next step
   - result snapshot
   - Real-Money signal
   - data trust snapshot
   - settings snapshot

## 중요한 경계

- 이 기능은 `CURRENT_CANDIDATE_REGISTRY.jsonl`에 자동 저장하지 않는다.
- suggested record type은 자동 승격 결과가 아니라 사람이 볼 초안 분류다.
- Candidate Intake Draft는 투자 추천이나 live approval이 아니다.
- 실제 후보 등록 / near-miss 기록 / Pre-Live 저장은 별도 검토 후 진행한다.

## 수정한 코드

- `app/web/pages/backtest.py`

## 검증

- `python3 -m py_compile app/web/pages/backtest.py`
- `.venv` import smoke로 candidate review draft helper 동작 확인

## 다음 작업

다음 작업은 후보 검토 초안을 실제 current candidate registry에 어떻게 반영할지,
또는 별도 review note로 남길지 결정하는 것이다.
자동 저장보다 사용자 확인과 문서/registry 기준 정리가 먼저다.
