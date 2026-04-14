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
  - single / compare strict annual form에서
    `Weighting Contract`, `Risk-Off Contract`, `Defensive Sleeve Tickers` 위치와 뜻을 더 직접적으로 읽을 수 있게 보강
  - strict annual advanced inputs를 `Overlay`와 `Portfolio Handling & Defensive Rules`로 분리해
    overlay trigger와 post-overlay handling contract를 구조적으로 구분
  - `Risk-Off Contract` 설명에서
    `보수 모드` / `full risk-off` 표현을 줄이고,
    "factor 포트폴리오 전체를 멈추고 현금 또는 방어 ETF로 전환" 언어로 다시 정리

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
- `completed` phase19 checklist 피드백 기준 UI 설명 / glossary 보강
- `completed` active phase checklist를 checkbox 기반 검수 형식으로 정리
- `completed` tooltip 가독성과 always-on contract 설명을 추가로 보강
