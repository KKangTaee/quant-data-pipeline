# Status

Status: Complete
Last Updated: 2026-07-17

## 전체 Roadmap

- [x] 1차 Validation Truth / Finding Contract
- [x] 2차 Level2 Decision Workspace Read Model
- [x] 3차 One-Shell UI / Intent Integration
- [x] 4차 QA / Docs / Closeout
- [x] 사용자 피드백 기반 계약 / 상호작용 / 설명 보정

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
