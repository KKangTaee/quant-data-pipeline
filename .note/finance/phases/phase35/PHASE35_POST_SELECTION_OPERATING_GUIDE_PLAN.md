# Phase 35 Post-Selection Guide Plan

## 이 문서는 무엇인가

Phase 35에서 만들 `Post-Selection Guide`의 목적, 범위, 작업 단위를 정리하는 계획 문서다.

2026-05-04 사용자 피드백 이후,
Phase35는 별도 저장소에 운영 가이드를 다시 저장하는 흐름이 아니라
Final Review의 최종 판단 기록을 읽어 마지막 투자 가능성 / 운영 전 지침을 확인하는 흐름으로 보정했다.

## 목적

- Phase 34 final review record 중 최종 선정된 후보를 Phase 35 입력으로 읽는다.
- 최종 판단을 사용자가 이해하기 쉬운 말로 보여준다.
  - 투자 가능 후보
  - 투자하면 안 됨
  - 내용 부족 / 관찰 필요
  - 재검토 필요
- 선정 후보의 리밸런싱, 축소, 중단, 재검토 기준을 preview로 확인한다.
- Final Review 기록과 live approval / broker order / 자동매매를 계속 분리한다.

## 쉽게 말하면

Phase 34가 "이 후보를 최종 실전 후보로 고를까?"를 기록하는 단계였다면,
Phase 35는 "그 기록을 보고 정말 투자 후보로 읽을 수 있는가?"를 마지막으로 확인하는 단계다.

다만 이번 phase도 주문 실행이나 자동매매가 아니다.
실제 돈을 넣기 전, 사람이 따라갈 운영 전 기준을 화면에서 확인하는 단계다.

## 왜 필요한가

- 최종 후보를 선정해도 사용자는 마지막에 "그래서 투자 가능인가?"를 한 번에 읽어야 한다.
- 보류 / 거절 / 재검토 기록까지 모두 같은 후보처럼 보이면 사용자가 흐름을 오해한다.
- 리밸런싱, 축소, 중단, 재검토 기준이 없으면 선정 이후 판단이 흔들릴 수 있다.
- 그러나 Final Review에서 이미 최종 판단을 저장했으므로, Phase35가 또 저장 단계를 만드는 것은 과하다.

## 이 phase가 끝나면 좋은 점

- 사용자는 최종 선정된 포트폴리오 후보를 마지막 투자 지침 형태로 읽을 수 있다.
- 투자 가능 / 투자하면 안 됨 / 내용 부족 / 재검토 필요가 한 화면에서 구분된다.
- Phase35가 새 registry를 만들지 않아 저장 UX가 반복되지 않는다.
- Phase36 이후 live approval 또는 monitoring 확장으로 가더라도, 운영 전 기준과 실행 경계가 먼저 고정된다.

## 이 phase에서 다루는 대상

- `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
  - `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
  - 신규 row: `phase35_handoff.handoff_route = READY_FOR_FINAL_INVESTMENT_GUIDE`
  - 기존 QA row: `READY_FOR_POST_SELECTION_OPERATING_GUIDE`도 읽기 호환
- `Backtest > Final Review`에서 저장된 최종 검토 결과
- Phase 35 final guide surface
  - 구현 위치: `Backtest > Post-Selection Guide`

## 이 phase에서 다루지 않는 것

- 별도 post-selection registry 저장
- broker 주문 실행
- 자동매매
- live approval 최종 승인
- 실제 체결 비용 / 슬리피지 엔진
- paper PnL 시계열 자동 계산 엔진
- optimizer / 신규 포트폴리오 생성 엔진

## 구현 우선순위와 완료 상태

1. Final investment guide 계약 정의
   - 쉽게 말하면: Final Review 판단을 투자 가능 / 투자하면 안 됨 / 내용 부족 / 재검토 필요로 읽는다.
   - 왜 먼저 하는가: 저장소나 버튼보다 최종 판단의 의미가 먼저 명확해야 한다.
   - 기대 효과: Phase35가 "또 저장"이 아니라 "최종 확인"으로 읽힌다.
   - 상태: 완료
2. Selected final decision 입력 surface 정의
   - 쉽게 말하면: Phase34에서 선정된 record만 최종 지침 확인 대상으로 읽는다.
   - 왜 필요한가: 보류 / 거절 / 재검토 record는 투자 가능 후보가 아니기 때문이다.
   - 기대 효과: 사용자가 최종 후보와 제외 대상을 혼동하지 않는다.
   - 상태: 완료
3. Final guide preview UI 구현
   - 쉽게 말하면: 리밸런싱, 축소, 중단, 재검토 기준을 화면에서 확인한다.
   - 왜 필요한가: 최종 후보 선정 이후 사용자가 따라갈 운영 전 기준이 필요하다.
   - 기대 효과: 실전 포트폴리오 후보가 "선정 기록"에서 "운영 전 확인 가능한 후보"로 한 단계 더 구체화된다.
   - 상태: 완료
4. No-extra-save handoff와 QA 정리
   - 쉽게 말하면: 추가 저장 버튼과 saved guide review를 제거하고 문서를 맞춘다.
   - 왜 필요한가: 반복 저장 UX가 사용 흐름을 흐리기 때문이다.
   - 기대 효과: Final Review가 원본 기록, Phase35가 마지막 확인 화면이라는 경계가 선명해진다.
   - 상태: 완료

## 이 문서에서 자주 쓰는 용어

- `Post-Selection Guide`: Final Review 이후 최종 투자 가능성과 운영 전 기준을 확인하는 화면이다.
- `Selected Final Review Record`: Phase34에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 기록된 final review record다.
- `Final Investment Guide`: 최종 판단, component, target weight, 운영 전 기준을 묶어 읽는 preview다. 별도 저장물이 아니다.
- `Live Approval Boundary`: 이 화면이 실제 주문 승인이나 자동매매가 아님을 구분하는 경계다.

## 이번 phase의 운영 원칙

- Phase35는 최종 확인 phase이지 주문 실행 phase가 아니다.
- Phase35는 별도 `.jsonl` 저장소를 만들지 않는다.
- Final Review의 final decision registry가 최종 판단 원본이다.
- UI는 `Backtest > Post-Selection Guide`로 분리하고, Portfolio Proposal 탭으로 다시 확장하지 않는다.
- Phase34~35에서 사용자가 문제 제기한 "반복 저장 UX"가 재발하지 않게 한다.

## 한 줄 정리

Phase 35는 최종 선정된 포트폴리오 후보를 바로 주문으로 보내지 않고,
투자 가능성 / 투자 불가 / 내용 부족 / 재검토 필요와 운영 전 기준을 마지막으로 확인하는 단계다.
