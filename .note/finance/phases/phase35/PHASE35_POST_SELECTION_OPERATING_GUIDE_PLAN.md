# Phase 35 Post-Selection Operating Guide Plan

## 이 문서는 무엇인가

Phase 35에서 만들 `Post-Selection Operating Guide`의 목적, 범위, 작업 단위를 정리하는 계획 문서다.

Phase 34에서 최종 검토 결과를 기록할 수 있게 되었으므로,
이제는 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 선정된 후보를 실제 운영 전 어떤 규칙으로 관리할지 정리한다.

2026-05-04 기준 구현은 완료됐고,
사용자는 `PHASE35_TEST_CHECKLIST.md`로 manual QA를 진행하면 된다.

## 목적

- Phase 34 final review record 중 최종 선정된 후보를 Phase 35 운영 입력으로 읽는다.
- 선정 이후 리밸런싱, 중단, 축소, 재검토 기준을 사용자가 따라갈 수 있는 가이드로 만든다.
- 선정 기록과 live approval / broker order / 자동매매를 계속 분리한다.

## 쉽게 말하면

Phase 34가 "이 후보를 최종 실전 후보로 고를까?"를 기록하는 단계였다면,
Phase 35는 "고른 뒤에는 언제 사고, 언제 줄이고, 언제 멈추고, 언제 다시 볼까?"를 정리하는 단계다.

다만 이번 phase도 주문 실행이나 자동매매가 아니다.
실제 돈을 넣기 전, 사람이 따라갈 운영 규칙을 문서화하고 UI에서 읽을 수 있게 만드는 단계다.

## 왜 필요한가

- 최종 후보를 선정해도 운영 규칙이 없으면 실전 포트폴리오로 쓰기 어렵다.
- 리밸런싱 기준, 중단 기준, 재검토 기준이 없으면 사용자가 감정적으로 판단할 가능성이 커진다.
- Phase 34의 `SELECT_FOR_PRACTICAL_PORTFOLIO`도 live approval이 아니므로, 그 다음에 운영 guide가 필요하다.
- final review record의 `operator_constraints`, `selected_components`, `paper_tracking_snapshot`을 실제 운영 기준으로 풀어 써야 한다.

## 이 phase가 끝나면 좋은 점

- 사용자는 최종 선정된 포트폴리오 후보를 운영 가이드 형태로 다시 읽을 수 있다.
- 선정 이후에도 어떤 상황에서 보류 / 축소 / 중단 / 재검토로 돌아갈지 알 수 있다.
- Phase 36 이후 live approval 또는 paper/live monitoring 확장으로 가더라도, 운영 기준이 먼저 고정된다.

## 이 phase에서 다루는 대상

- `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
  - `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
  - `phase35_handoff.handoff_route = READY_FOR_POST_SELECTION_OPERATING_GUIDE`
- `Backtest > Final Review`에서 저장된 최종 검토 결과
- Phase 35 운영 가이드 surface
  - 구현 위치: `Backtest > Post-Selection Guide`
- Phase 35 운영 policy 문서 / runtime helper

## 이 phase에서 다루지 않는 것

- broker 주문 실행
- 자동매매
- live approval 최종 승인
- 실제 체결 비용 / 슬리피지 엔진
- paper PnL 시계열 자동 계산 엔진
- optimizer / 신규 포트폴리오 생성 엔진

## 구현 우선순위와 완료 상태

1. Post-selection operating policy 계약 정의
   - 쉽게 말하면: 선정된 후보를 어떤 규칙으로 운영할지 row / guide 기준을 먼저 정한다.
   - 왜 먼저 하는가: policy 없이 UI부터 만들면 또 버튼과 저장소가 늘어나는 흐름이 될 수 있다.
   - 기대 효과: Phase35가 live approval과 섞이지 않고 운영 가이드로 읽힌다.
   - 상태: 완료
2. Selected final decision 입력 surface 정의
   - 쉽게 말하면: Phase34에서 선정된 record만 골라 Phase35 입력으로 읽는다.
   - 왜 필요한가: 보류 / 거절 / 재검토 record는 운영 guide 대상이 아니기 때문이다.
   - 기대 효과: 사용자가 운영 guide를 만들 대상과 제외 대상을 혼동하지 않는다.
   - 상태: 완료
3. Operating guide preview / record UI 구현
   - 쉽게 말하면: 리밸런싱, 축소, 중단, 재검토 기준을 화면에서 확인한다.
   - 왜 필요한가: 최종 후보 선정 이후 사용자가 따라갈 실제 운영 기준이 필요하다.
   - 기대 효과: 실전 포트폴리오 후보가 "선정 기록"에서 "운영 가능한 후보"로 한 단계 더 구체화된다.
   - 상태: 완료
4. Saved operating guide review와 다음 phase handoff
   - 쉽게 말하면: 만든 운영 가이드를 다시 열어 보고, 이후 live approval 또는 monitoring 확장으로 넘길 준비를 한다.
   - 왜 필요한가: 운영 기준은 한 번 만든 뒤 다시 확인할 수 있어야 한다.
   - 기대 효과: Phase35 이후 작업이 가이드 없는 승인/주문 흐름으로 뛰지 않는다.
   - 상태: 완료

## 이 문서에서 자주 쓰는 용어

- `Post-Selection Operating Guide`: 최종 선정 후보를 어떻게 운영할지 정리한 가이드다.
- `Selected Final Review Record`: Phase34에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 기록된 final review record다.
- `Operating Policy`: 리밸런싱, 중단, 축소, 재검토 같은 운영 규칙 묶음이다.
- `Live Approval Boundary`: 운영 가이드가 실제 주문 승인이나 자동매매가 아님을 구분하는 경계다.

## 이번 phase의 운영 원칙

- Phase35는 운영 기준을 만드는 phase이지 주문 실행 phase가 아니다.
- 저장소는 `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`로 분리한다.
- 새 저장소는 append-only로 만들고, final decision registry를 덮어쓰지 않는다.
- UI는 `Backtest > Post-Selection Guide`로 분리하고, Portfolio Proposal 탭으로 다시 확장하지 않는다.
- Phase34에서 사용자가 문제 제기한 "반복 저장 UX"가 재발하지 않게 한다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업. Operating policy 계약 정의

- selected final review record에서 어떤 값을 읽을지 정한다.
- 운영 가이드가 최소한 포함해야 할 리밸런싱, 중단, 축소, 재검토 기준을 정한다.
- 새 registry가 필요한지, 아니면 final decision row의 guide snapshot으로 충분한지 판단한다.

### 두 번째 작업. Phase35 input selector / readiness 기준

- `SELECT_FOR_PRACTICAL_PORTFOLIO`와 `READY_FOR_POST_SELECTION_OPERATING_GUIDE` record만 Phase35 대상으로 읽는다.
- 보류 / 거절 / 재검토 record는 review backlog로 분리한다.
- 운영 가이드 작성 가능 / 보강 필요 / 차단 상태를 route로 보여준다.

### 세 번째 작업. Operating guide preview / record surface

- 사용자가 selected component, target weight, rebalancing cadence, stop / reduce / re-review trigger를 확인한다.
- guide가 live approval이나 order instruction이 아님을 화면에서 계속 보여준다.
- 저장 또는 기록 액션이 필요하면 한 번의 명확한 action으로 제한한다.

### 네 번째 작업. Saved guide review / 다음 handoff 정리

- 저장 또는 생성된 operating guide를 다시 읽는 surface를 만든다.
- Phase36 이후 후보 방향을 문서화한다.
- Phase35 checklist를 작성해 사용자 manual QA로 넘긴다.

## 다음에 확인할 것

- Phase34 QA에서 생성된 final decision record가 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에 있는지
- `SELECT_FOR_PRACTICAL_PORTFOLIO` record가 없을 때 Phase35가 어떻게 안내해야 하는지
- 운영 guide를 별도 registry로 남길지, final decision registry의 확장 snapshot으로 충분한지

## 한 줄 정리

Phase 35는 최종 선정된 포트폴리오 후보를 바로 주문으로 보내지 않고,
사람이 따라갈 리밸런싱 / 중단 / 축소 / 재검토 운영 기준으로 바꾸는 단계다.
