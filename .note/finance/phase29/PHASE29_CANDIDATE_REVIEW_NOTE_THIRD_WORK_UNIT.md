# Phase 29 Candidate Review Note Third Work Unit

## 이 문서는 무엇인가

`Candidate Intake Draft`를 본 뒤 운영자가 남기는 판단 기록을
`Candidate Review Note`로 저장하는 세 번째 작업 단위를 정리한다.

## 쉽게 말하면

좋아 보이는 백테스트 결과가 있어도 바로 current candidate로 등록하지 않는다.
먼저 "이 결과를 후보로 볼지, near-miss로 둘지, 추가 데이터가 필요한지"를
사람이 읽을 수 있는 메모로 남기는 단계다.

## 왜 필요한가

- `Candidate Intake Draft`는 화면에서만 보이는 임시 초안이다.
- 초안을 보고 한 판단이 문서나 채팅에만 남으면 나중에 왜 보류했는지 추적하기 어렵다.
- 반대로 초안을 바로 `CURRENT_CANDIDATE_REGISTRY.jsonl`에 넣으면 후보 승격처럼 오해될 수 있다.

그래서 current candidate registry와 별도로
`.note/finance/CANDIDATE_REVIEW_NOTES.jsonl`에 검토 노트를 남긴다.

## 이 작업이 끝나면 좋은 점

- 최신 백테스트나 history run을 검토한 이유와 다음 행동이 남는다.
- 후보 등록 전 단계와 후보 등록 단계를 분리할 수 있다.
- `reject_for_now`, `needs_more_evidence`, `near_miss_review`처럼
  "아직 후보는 아니지만 왜 봤는지"를 잃어버리지 않는다.

## 구현한 것

1. `Candidate Review > Candidate Intake Draft` 아래에
   `Save As Candidate Review Note` 영역을 추가했다.
2. 운영자가 `Review Decision`, `Operator Reason`, `Next Action`, optional `Review Date`를 남길 수 있게 했다.
3. 저장 버튼은 `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl`에 append-only로 기록한다.
4. `Candidate Review > Review Notes` 탭을 추가해 저장된 검토 노트를 표와 JSON으로 확인할 수 있게 했다.
5. `Candidate Review` 상단 metric에 `Review Notes` 개수를 추가했다.
6. current candidate registry에 active 후보가 없어도,
   최신 run/history에서 만든 intake draft와 review note는 확인할 수 있게 했다.

## 중요한 경계

- Candidate Review Note는 투자 추천이 아니다.
- Candidate Review Note는 live trading 승인도 아니다.
- Candidate Review Note를 저장해도 `CURRENT_CANDIDATE_REGISTRY.jsonl`에는 자동 등록되지 않는다.
- Candidate Review Note는 "검토 판단과 다음 행동을 남기는 기록"이다.

## 확인할 위치

- `Backtest > Candidate Review > Candidate Intake Draft`
- `Backtest > Candidate Review > Review Notes`
- `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl`

## 다음에 남은 것

- Candidate Review Note를 실제 current candidate registry row 초안으로 변환하는 흐름은
  네 번째 작업 단위에서 추가했다.
- Phase 29 QA에서는 review note 저장과 registry append가 서로 다른 단계로 읽히는지 확인한다.
