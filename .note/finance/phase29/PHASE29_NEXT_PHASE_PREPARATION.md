# Phase 29 Next Phase Preparation

## 목적

이 문서는 Phase 29 이후 Phase 30으로 넘어갈 때 어떤 질문을 다뤄야 하는지 미리 정리하는 handoff 문서다.

현재는 Phase 29 구현이 끝나고 사용자 QA를 기다리는 상태이므로, 이 문서는 임시 준비 문서다.
Phase 29 closeout 시점에 다시 갱신한다.

## 현재 handoff 상태

- Phase 29는 implementation_complete / manual_qa_pending 상태다.
- 첫 작업 단위로 `Backtest > Candidate Review` panel을 추가했다.
- 두 번째 작업 단위로 Latest Backtest Run / History 결과를 `Candidate Intake Draft`로 넘기는 길을 만들었다.
- 세 번째 작업 단위로 `Candidate Intake Draft`를 `Candidate Review Note`로 저장하는 길을 만들었다.
- 네 번째 작업 단위로 `Candidate Review Note`를 current candidate registry row 초안으로 변환하고,
  명시적 append 버튼으로만 registry에 기록하는 길을 만들었다.
- 현재는 사용자 QA 후 Phase 29를 닫고 Phase 30으로 넘길 수 있는지 확인하면 된다.

## Candidate Board future development note

- 현재 `Candidate Board`에 보이는 기존 후보는 자동 선별 결과가 아니라,
  이전 phase에서 문서화해 둔 후보를 registry에 seed처럼 남긴 샘플 후보군에 가깝다.
- Phase 29 QA에서는 이 목록을 투자 추천 목록이 아니라
  Candidate Review workflow가 잘 작동하는지 확인하기 위한 sample candidate set으로 본다.
- 추후 phase에서는 Candidate Board를 실제 후보 lifecycle board로 고도화해야 한다.
- 고도화 후보:
  - sample / seed 후보와 사용자가 직접 append한 후보를 화면에서 구분한다.
  - Single Strategy / History / Review Note에서 넘어온 후보의 source를 더 분명히 보여준다.
  - strict annual이 아닌 GTAA / GRS / future strategy 후보도 compare로 보낼 수 있도록
    `compare_prefill` 또는 변환 가능한 `contract`를 registry row에 안정적으로 남긴다.
  - 자동 후보 추천을 만들더라도 바로 board에 올리지 않고 review draft / review note를 거치게 한다.
  - 오래된 sample 후보를 archive하거나 status로 숨길 수 있게 한다.

## Phase 30으로 넘어가기 전에 더 중요한 질문

1. 후보 1개를 보는 것이 아니라 후보 묶음을 포트폴리오 제안으로 어떻게 만들 것인가
2. Pre-Live 기록과 portfolio proposal이 서로 어떻게 연결되어야 하는가
3. 포트폴리오 제안이 투자 승인처럼 보이지 않게 하려면 어떤 경계 문구와 상태값이 필요한가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 30은 후보 검토 결과를 포트폴리오 제안과 paper / pre-live monitoring surface로 연결하는 phase다.

주요 작업 후보:

1. Portfolio Proposal 후보 묶음 정의
   - 여러 candidate를 어떤 비중 / 목적 / 위험 역할로 묶을지 기록한다.
2. Proposal review surface
   - 포트폴리오 제안이 어떤 후보들로 구성되었고 어떤 데이터 / Real-Money / Pre-Live 상태를 갖는지 보여준다.
3. Pre-Live monitoring 연결
   - 후보 단위 Pre-Live 기록과 포트폴리오 단위 monitoring이 어떻게 이어질지 정한다.

## 추천 다음 방향

Phase 29가 후보 검토 workflow를 정리하면,
Phase 30은 그 후보들을 묶어 포트폴리오 제안으로 관리하는 흐름이 자연스럽다.

## handoff 메모

- Phase 30은 live approval이 아니다.
- Phase 30은 portfolio proposal과 monitoring surface를 만드는 phase다.
- Live Readiness / Final Approval은 Phase 30 이후 별도 phase 후보로 둔다.
