# Phase 19 Current Chapter TODO

## 상태
- `practical closeout / manual_validation_pending`

## 1. Structural Contract Expansion

- `completed` rejected-slot handling explicit contract first slice
  - strict annual single / compare에서 두 개 checkbox 대신 명시적 mode contract로 노출
  - mode를 payload / runtime input params에도 같이 기록
- `completed` legacy compatibility bridge
  - old boolean payload만 있어도 explicit mode를 복원
  - new mode payload에서도 legacy booleans를 계속 함께 남김
- `completed` next contract cleanup candidate shortlist
  - risk-off / weighting / interpretation cleanup을 다음 slice로 선택

## 2. Interpretation Cleanup

- `completed` trend filter help 문구를 explicit handling contract 기준으로 정리
- `completed` runtime warning을 explicit handling mode 기준으로 통일
- `completed` history / selection interpretation 문구를 더 operator-friendly하게 정리
  - selection history에 `Rejected Slot Handling` / `Filled Count`를 노출
  - interpretation summary에 `Filled Events` / `Cash-Retained Events`를 추가
- `completed` risk-off / weighting interpretation cleanup
  - selection history에 `Weighting Contract` / `Risk-Off Contract` / `Risk-Off Reasons`를 노출
  - interpretation summary에 `Defensive Sleeve Activations`를 추가

## 3. Validation

- `completed` `py_compile`
- `completed` `.venv` import smoke
- `completed` manual UI validation checklist 문서 생성
- `pending` manual UI validation actual run
  - single strict annual 3 family
  - compare strict annual 3 family
  - history prefill / load-into-form

## 4. Documentation Sync

- `completed` phase19 kickoff / first slice 문서 생성
- `completed` phase19 history / interpretation cleanup second slice 문서 생성
- `completed` phase19 risk-off / weighting interpretation cleanup third slice 문서 생성
- `completed` phase19 kickoff plan을 쉬운 설명 중심으로 재작성
- `completed` future phase plan 작성 규칙에 쉬운 설명 섹션을 반영
- `completed` future phase에서 재사용할 phase plan template 문서 생성
- `completed` phase19 completion / next-phase / checklist 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` finance comprehensive analysis sync
