# Candidate Review Notes Guide

## 이 문서는 무엇인가

`.note/finance/CANDIDATE_REVIEW_NOTES.jsonl` 파일이 무엇을 저장하고,
`CURRENT_CANDIDATE_REGISTRY.jsonl`과 어떻게 다른지 설명한다.

## 쉽게 말하면

Candidate Review Note는 "이 백테스트 결과를 보고 사람이 어떤 판단을 했는가"를 남기는 메모다.

후보 자체를 등록하는 파일이 아니라,
후보 등록 전 단계에서 남기는 검토 기록이다.

## 왜 필요한가

- 좋은 백테스트 결과를 바로 current candidate로 등록하면 후보 승격처럼 보일 수 있다.
- 반대로 아무 기록도 남기지 않으면 왜 보류했는지, 왜 다시 봐야 하는지 사라진다.
- 그래서 검토 판단은 별도 파일에 남기고, 실제 후보 등록은 별도 기준으로 처리한다.

## 저장 위치

- `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl`

이 파일은 append-only 성격으로 사용한다.
새 판단이 생기면 기존 줄을 고치기보다 새 줄을 추가하는 방식이 기본이다.

## Current Candidate Registry와 차이

| 구분 | 파일 | 역할 |
|---|---|---|
| Candidate Review Note | `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl` | 초안을 본 뒤 남기는 판단 메모 |
| Current Candidate Registry | `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` | current anchor / near-miss / scenario 후보 자체 |
| Pre-Live Candidate Registry | `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | 후보의 pre-live 운영 상태와 다음 행동 |

## UI에서 쓰는 위치

- `Latest Backtest Run > Candidate Review Handoff > Review As Candidate Draft`
- `History > Selected History Run > Review As Candidate Draft`
- `Candidate Review > Candidate Intake Draft > Save Candidate Review Note`
- `Candidate Review > Review Notes`
- `Candidate Review > Review Notes > Prepare Current Candidate Registry Row`

## 저장되는 주요 값

- `review_decision`
  - 후보 등록 검토, near-miss 유지, scenario 유지, 추가 근거 필요, 지금은 reject 같은 판단
- `operator_reason`
  - 왜 그렇게 판단했는지
- `next_action`
  - 다음에 무엇을 확인할지
- `review_date`
  - 필요할 경우 다음 재검토 날짜
- `result_snapshot`
  - CAGR, MDD 등 실행 결과 요약
- `real_money_signal`
  - promotion, shortlist, deployment 신호
- `data_trust_snapshot`
  - 결과를 해석할 때 같이 봐야 할 데이터 신뢰성 정보

## 중요한 경계

- Candidate Review Note는 투자 추천이 아니다.
- Candidate Review Note는 live trading 승인이 아니다.
- Candidate Review Note를 저장해도 current candidate registry에 자동 등록되지 않는다.
- 실제 후보 등록은 별도 검토와 기준이 필요하다.

## 후보 registry로 남기는 경우

`Candidate Review > Review Notes`에서 저장된 note를 선택하면
`Prepare Current Candidate Registry Row` 영역에서 registry row 초안을 볼 수 있다.

이때 확인할 것:

- `Registry ID`
- `Record Type`
  - current candidate
  - near miss
  - scenario
- `Strategy Family`
- `Strategy Name`
- `Candidate Role`
- `Title`
- `Registry Notes`

`Append To Current Candidate Registry`를 눌러야만
`.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`에 append된다.

`Reject For Now` note는 기본적으로 registry append를 막는다.
