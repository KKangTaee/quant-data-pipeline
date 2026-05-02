# Phase 29 Next Phase Preparation

## 목적

이 문서는 Phase 29 이후 Phase 30으로 넘어갈 때 어떤 질문을 다뤄야 하는지 미리 정리하는 handoff 문서다.

현재는 Phase 29 closeout 후 Phase 30으로 넘어가기 전 준비 문서다.
Phase 30을 바로 기능 구현으로 열기보다, 먼저 사용 흐름과 리팩토링 경계를 정리한다.

## 현재 handoff 상태

- Phase 29는 complete / manual_qa_completed 상태다.
- 첫 작업 단위로 `Backtest > Candidate Review` panel을 추가했다.
- 두 번째 작업 단위로 Latest Backtest Run / History 결과를 `Candidate Intake Draft`로 넘기는 길을 만들었다.
- 세 번째 작업 단위로 `Candidate Intake Draft`를 `Candidate Review Note`로 저장하는 길을 만들었다.
- 네 번째 작업 단위로 `Candidate Review Note`를 current candidate registry row 초안으로 변환하고,
  명시적 append 버튼으로만 registry에 기록하는 길을 만들었다.
- 사용자 QA까지 완료되어 Phase 29는 닫혔다.
- 다만 다음 단계는 Phase 30 기능 구현 직행이 아니라,
  `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 Phase 29 이후 기준으로 재정렬하고
  `backtest.py` 리팩토링 경계를 먼저 검토하는 것이다.

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
4. Phase 29 이후 새로 생긴 Candidate Draft / Review Note / Registry Draft가 전체 운영 흐름에서 언제 필요한지 사용자가 충분히 이해하고 있는가
5. `backtest.py`에 집중된 UI / state / persistence helper를 어떤 제품 흐름 단위로 나눌 것인가

## Phase 30 준비 작업에서 먼저 할 일

쉽게 말하면:

- Phase 30 구현 전에 제품 사용 지도와 코드 경계를 먼저 정리한다.

주요 작업 후보:

1. `테스트에서 상용화 후보 검토까지 사용하는 흐름` 재작성
   - `Backtest Run -> Candidate Draft -> Candidate Review Note -> Current Candidate Registry -> Compare / Pre-Live -> Portfolio Proposal -> Live Readiness`를 기준 흐름으로 고정한다.
   - 각 단계마다 왜 필요한지, 언제 쓰는지, 생략 가능한 경우를 설명한다.
2. `backtest.py` 리팩토링 경계 계획
   - Candidate Review, Pre-Live Review, History, Compare / Weighted / Saved Portfolio, Single Strategy latest result, registry persistence helper를 어떤 모듈로 분리할지 정한다.
   - 즉시 대규모 리팩토링을 시작하기보다, Phase 30 구현을 방해하지 않는 순서로 점진 분리 계획을 만든다.
3. Phase 30 scope 재확인
   - 사용자가 흐름을 충분히 이해한 상태에서 portfolio proposal / pre-live monitoring surface를 어디까지 만들지 확정한다.

## Phase 30에서 실제로 할 작업

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

Phase 29가 후보 검토 workflow를 정리했으므로,
Phase 30은 그 후보들을 묶어 포트폴리오 제안으로 관리하는 흐름이 자연스럽다.
다만 현재는 기능 확장보다 사용 흐름 재정렬과 리팩토링 경계 확인을 먼저 하는 것이 안전하다.

## handoff 메모

- Phase 30은 live approval이 아니다.
- Phase 30은 portfolio proposal과 monitoring surface를 만드는 phase다.
- Live Readiness / Final Approval은 Phase 30 이후 별도 phase 후보로 둔다.
