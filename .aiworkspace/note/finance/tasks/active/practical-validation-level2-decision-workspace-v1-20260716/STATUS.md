# Status

Status: In Progress - Step 1 Selection IA Follow-up
Last Updated: 2026-07-17

## 전체 Roadmap

- [x] 1차 Validation Truth / Finding Contract
- [x] 2차 Level2 Decision Workspace Read Model
- [x] 3차 One-Shell UI / Intent Integration
- [x] 4차 QA / Docs / Closeout
- [x] 사용자 피드백 기반 계약 / 상호작용 / 설명 보정
- [ ] Step 1 선택 정보 구조 compact follow-up

## 2026-07-17 Step 1 Selection IA Follow-up

- [x] 현재 hero / 후보 card grid / profile grid 구조와 context ownership 확인
- [x] visual companion으로 가로 strip / compact selector / 세로 list 3안 비교
- [x] 사용자 B안 `선택 요약 + 컴팩트 컨트롤` 승인
- [x] 760px profile 2열 줄바꿈과 마지막 option full-span 승인
- [x] approved design을 `DESIGN.md` acceptance criteria 33~40으로 기록
- [ ] detailed implementation plan 승인
- [ ] TDD 구현, Browser QA, docs closeout

## Current Progress

- [x] single-component construction applicability와 closure resolution-class truth contract
- [x] callable handler가 있는 resolve-now action contract
- [x] pure `practical_validation_decision_workspace_v1` read model
- [x] root issue dedup, measured caution, verified / handoff 분리
- [x] four-step React one-shell과 same-read-model Streamlit fallback
- [x] Python intent validation / replay / provider action / save boundary
- [x] final focused 124 tests, React 175 modules build, target py_compile, diff-check
- [x] current eligible GRS read-only projection과 8505 restart / HTTP health
- [x] canonical docs와 active task / root handoff sync
- [x] desktop / 760px Browser QA, overflow 확인, screenshot
- [x] correction Task 5: Level2-owned caution / evidence-state contract
- [x] correction Task 6: 후보/검증 정책 분리와 fragment 재검증
- [x] correction Task 7: 사용자 설명 계약과 범주별 상세 검증 UI
- [x] correction Task 8: 누락 검증과 audit 집계 경계 강화
- [x] correction Task 9: latest GRS read-only projection, handoff lane
  regression TDD, focused 124 tests, React build, py_compile, diff-check,
  HTTP health, docs sync

## Current Position

초기 1~3차 구현 뒤 실화면에서 확인된 후보/검증 정책 혼합, 전체 탭 rerun,
raw 기술 근거, 반복 action lifecycle을 보정했다. 이어서 실제 공식 provider
수집기와 Final Review의 Level2 handoff 소비 계약을 구현했고, 지정 후보가
개발 차단 없이 Final Review 이동 가능 상태가 되는 것을 Browser QA로 확인했다.

## Next Action

별도 승인 전에는 dynamic historical universe / delisting provider를 추가하지
않는다. 후속 제품 검토는 필요할 때 현재 task의 `RISKS.md`에서 이어간다.

## Implementation Commits

- `a2352f01` Practical Validation 검증 의미 계약 보정
- `0e180f93` Practical Validation 판단 워크스페이스 모델 도입
- `b661e83a` Practical Validation Level2 원셸 UI 전환
- `8be7ba2e` Practical Validation Level2 보정 설계 반영
- `96571a15` Practical Validation Level2 주의 종결 계약 보정
- `d26fccb6` Practical Validation 후보 선택과 부분 재검증 개선
- `e3797e9f` Practical Validation 검증 설명과 상세 근거 개선
- `4ac2a83a` Practical Validation 미검증 항목과 집계 기준 보강
- `d968b6a4` Practical Validation Final Review 인계 분류 보정
- `6b0629be` Practical Validation 후보와 검증 관점 배치 개선
- `bfafdc5c` Practical Validation 해결 작업 재노출 수정
- `96e15fc2` Practical Validation 해결 생명주기 경계 강화
- `f9cc47a9` ETF 공식 보유종목 수집 어댑터 보강
- `ebe29cd6` Final Review Level2 인계 판단 화면 보강
- `c95765a3` ETF 채권 보유종목 식별자 충돌 수정
- `c038c938` Practical Validation 인계 UX 보정 설계 반영
- `f94b4f50` Practical Validation 재검증 화면 유지 보정
- `1003488d` Practical Validation Final Review 인계 요약 개선
- `3fe41c2a` Final Review 인계 한계 판단 기록 추가
- `f88daf01` Practical Validation 재검증 렌더 경계 설계 반영
- `9d7b6cdc` Practical Validation 재검증 렌더 경계 분리
- `6cf1db11` Practical Validation component ready 경고 제거

## 2026-07-16 Follow-up Status

- [x] 선택 후보 반복 요약을 후보 목록 아래에서 one-shell header `검증 대상`으로 이동
- [x] 데스크톱 검증 관점 5개를 3 + 가운데 정렬 2로 재배치하고 760px 1열 유지
- [x] provider action pending 상태와 provider -> replay 순서 고정
- [x] 실행된 provider 보강 뒤 replay / decision-result cache 무효화
- [x] 이미 시도한 source 탐색과 미지원 parser를 `engineering_required`로 전환
- [x] 완료된 actual partial-month replay를 Monitoring handoff로 종결
- [x] 장기 replay gap / discovery 예외 / candidate source code-review 보정
- [x] 지정 후보 actual replay / provider plan / decision workspace read-only 재검증
- [x] fresh focused 154 tests, React 175 modules build, target py_compile, diff-check
- [x] final code review Critical / Important 잔여 0건
- [x] desktop / 760px Browser interaction / overflow / screenshot QA

지정 후보 `GTAA U3/U5 + GRS Compact Monitoring Candidate 20260608`의
최신 재검증은 verified 27, resolve-now 0, engineering blocker 0,
accepted limit 1, monitoring transfer 1이며 save-and-move가 활성화됐다.
COMT/EFA/IWD/IWM/IWN/LQD/TIP/VNQ는 기존 DB snapshot 경로로 공식
holdings/exposure를 읽는다. Final Review는 eligible row에서 Level2 handoff를
`최종 판단 입력 / 인수한 검증 한계 / Monitoring 이관 조건`으로 분리한다.

## 2026-07-17 Atomic Revalidation / Actionable Handoff Correction

- [x] component `on_change` callback이 replay / profile / Level2 resolution intent를
  projection 전에 소비하고 별도 fragment rerun을 호출하지 않음
- [x] Level2 handoff를 root-dedup compact summary로 표시하고 0건 lane을 숨김
- [x] Final Review accepted limit마다 `한계를 인수하고 계속` 또는
  `Level2로 되돌리기`를 선택하도록 하고 Python이 route 일관성을 검증
- [x] normalized 선택을
  `decision_brief_snapshot.accepted_limit_acknowledgements`에 append-only 저장
- [x] fresh focused 188 tests, Practical 175-module build, Final Review
  177-module build, target py_compile, diff-check
- [x] correction desktop / 760px Browser QA: 당시 8506 Browser policy 차단분을
  Task 17~18의 current 8505 build replay/overflow/screenshot QA로 대체함

callback-only correction의 남은 화면 수명주기 문제는 아래 stable boundary
closeout에서 해결하고 current build로 재검증했다.

## 2026-07-17 Stable Context / Refresh Surface Closeout

- [x] 후보/검증 기준 `context`를 replay fragment 밖의 별도 component로 고정
- [x] replay/결과/해결/save `decision`만 fragment에서 갱신
- [x] context는 source/profile, decision은 replay/resolution/save intent만 허용
- [x] React 미가용 fallback도 같은 두 surface 경계 사용
- [x] desktop 실제 replay 중 context + pending shell 동시 유지와 PASS 교체 확인
- [x] 760px outer 760/760, context/decision iframe 717/717 overflow 0 확인
- [x] current build console error와 component-ready warning 0건
- [x] fresh focused/completion 134 tests, Practical 175-module build, Final Review
  177-module build, target py_compile, diff-check

Task 13의 callback-only 보정은 두 번째 명시적 rerun만 제거했고 custom component
전체가 하나의 fragment에 남는 문제를 놓쳤다. Task 17은 실제 mount 경계를
나눴으며, 지정 후보는 verified 27, Level2 caution 7, resolve-now/engineering 0,
accepted limit 1, monitoring transfer 1의 이동 가능 상태를 유지한다.
