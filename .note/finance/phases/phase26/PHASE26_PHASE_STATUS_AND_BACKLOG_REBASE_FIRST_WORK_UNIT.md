# Phase 26 Phase Status And Backlog Rebase First Work Unit

## 이 문서는 무엇인가

이 문서는 Phase 26의 첫 번째 작업 단위다.

목표는 오래된 phase 상태와 backlog를 현재 제품 상태 기준으로 다시 읽는 것이다.
이 작업은 코드를 바로 바꾸기보다, 다음 phase를 안전하게 열기 위한 판단표를 만드는 작업이다.

## 쉽게 말하면

예전에 남겨둔 "나중에 봐야 함" 목록을 지금 다시 펼쳐서
정말 지금 막는 문제인지, 나중에 봐도 되는 옵션인지, 기록으로만 남겨도 되는 과거 메모인지 구분한다.

## 왜 필요한가

- Phase 25까지 오면서 제품 구조가 많이 커졌다.
- 그런데 과거 phase에는 아직 `manual_qa_pending`, `practical_closeout`, `remaining backlog` 표현이 남아 있다.
- 이 상태에서 바로 Phase 27 구현으로 들어가면 예전 backlog와 새 roadmap이 충돌할 수 있다.

## 이번 작업에서 만들 판단 기준

| 구분 | 뜻 | 다음 처리 |
|---|---|---|
| Immediate blocker | 다음 phase를 시작하기 전에 해결해야 하는 문제 | Phase 26에서 처리하거나 Phase 27 시작 전 고정 |
| 다음 phase에서 다룰 주제 | 다음 phase에서 실제로 검토하거나 구현할 수 있는 문제 | Phase 27~30 중 해당 phase에 명시 |
| Future option | 지금 막지는 않지만 나중에 선택할 수 있는 개선 후보 | roadmap에 과도하게 크게 쓰지 않고 phase 문서에 보관 |
| Legacy note | 현재 구현 판단에는 직접 영향을 주지 않는 과거 기록 | index / archive 문서에서 찾을 수 있게만 유지 |

## 우선 볼 phase

| Phase | 왜 다시 보는가 |
|---|---|
| Phase 8 | quarterly family expansion이 현재 Phase 23 이후 상태와 어떻게 연결되는지 확인 |
| Phase 9 | strict coverage / promotion gate가 현재 Real-Money / Pre-Live 구조와 충돌하지 않는지 확인 |
| Phase 12~15 | real-money, deployment readiness, gate calibration 표현이 현재 Pre-Live / final approval 경계와 섞이지 않는지 확인 |
| Phase 18 | remaining structural backlog가 Phase 28 parity 작업으로 넘어갈지 future option으로 남길지 확인 |

## 이번 작업의 산출물

- Phase 상태 / backlog 재분류표
- Phase 27~30에서 다룰 주제 목록
- Live Readiness / Final Approval을 Phase 30 이후로 두는 boundary note

결과 문서:

- `.note/finance/phases/phase26/PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`

## 아직 하지 않는 것

- 예전 phase 전체 manual QA 재실행
- deep backtest rerun
- 신규 전략 구현
- 투자 후보 최종 승인

## 한 줄 정리

이번 작업은 과거 backlog를 없애는 작업이 아니라,
현재 제품 방향에 맞게 다시 이름 붙이고 올바른 다음 phase로 보내는 작업이다.
