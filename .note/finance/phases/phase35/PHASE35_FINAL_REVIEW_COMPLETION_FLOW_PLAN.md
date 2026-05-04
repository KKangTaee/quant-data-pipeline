# Phase 35 Final Review Completion Flow Plan

## 이 문서는 무엇인가

Phase 35에서 Backtest workflow의 마지막 단계를 어떻게 정리했는지 설명하는 계획 문서다.

2026-05-04 사용자 피드백 이후,
별도 후속 가이드 탭은 현재 제품 흐름에 비해 과한 단계로 판단했다.
따라서 Phase35는 `Portfolio Proposal -> Final Review -> 최종 판단 완료`로 흐름을 단순화한다.

## 목적

- Final Review를 현재 후보 선정 workflow의 마지막 active panel로 고정한다.
- 최종 판단 결과를 투자 가능 / 내용 부족 / 투자하면 안 됨 / 재검토 필요로 쉽게 읽게 한다.
- 추가 저장 UX를 만들지 않는다.
- live approval / broker order / 자동매매와 final decision을 계속 분리한다.

## 쉽게 말하면

Phase34가 Final Review 탭과 최종 판단 저장소를 만들었다면,
Phase35는 "여기서 끝내도 사용자가 이해할 수 있는가?"를 정리하는 phase다.

결론은 별도 마지막 탭을 더 만드는 것이 아니라,
Final Review 안에서 최종 판단 완료 상태를 분명하게 보여주는 것이다.

## 왜 필요한가

- 저장 버튼과 후속 단계가 계속 늘어나면 사용자가 어떤 기록이 원본인지 헷갈린다.
- 이미 Final Review가 validation, robustness, paper observation, operator judgment를 묶고 있다.
- 지금 단계에서 필요한 것은 추가 가이드 저장이 아니라 최종 판단의 의미를 명확히 표시하는 것이다.

## 이 phase가 끝나면 좋은 점

- 사용자는 Portfolio Proposal 이후 Final Review에서 최종 판단까지 끝낼 수 있다.
- 별도 후속 탭 없이 투자 가능 / 내용 부족 / 투자하면 안 됨 / 재검토 필요를 확인한다.
- 반복 저장 UX가 줄어든다.
- 실행 경계가 더 선명해진다.

## 이 phase에서 다루는 대상

- `Backtest > Final Review`
- `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
- `app/web/backtest_final_review.py`
- `app/web/backtest_final_review_helpers.py`
- `app/web/backtest_common.py`
- `app/web/pages/backtest.py`

## 이 phase에서 다루지 않는 것

- 별도 후속 가이드 panel
- 별도 후속 registry
- broker 주문 실행
- 자동매매
- live approval 최종 승인
- paper PnL 시계열 자동 계산
- optimizer / 신규 포트폴리오 생성 엔진

## 작업 단위

### 첫 번째 작업. Final Review 종료 상태 계약 정리

- Final decision route를 사용자-facing label로 읽는다.
- selected route는 `투자 가능 후보`로 읽는다.
- hold route는 `내용 부족 / 관찰 필요`로 읽는다.
- reject route는 `투자하면 안 됨`으로 읽는다.
- re-review route는 `재검토 필요`로 읽는다.

### 두 번째 작업. 별도 후속 가이드 workflow 제거

- Backtest workflow panel option에서 후속 가이드 panel을 제거한다.
- 후속 가이드 render module과 helper를 제거한다.
- `Final Review`에서 후속 panel 이동 버튼을 제거한다.

### 세 번째 작업. Final Review UI 완료 표시 보강

- saved final decision review에 `투자 가능성`을 표시한다.
- route panel title을 `Final Review Status`로 읽게 한다.
- `Live Approval / Order`는 disabled 상태로 유지한다.

### 네 번째 작업. 문서 / QA checklist 동기화

- phase35 TODO, checklist, completion summary를 새 흐름으로 고친다.
- code analysis, roadmap, doc index, operations guide를 새 흐름과 맞춘다.
- Post-Selection 관련 active 문서와 삭제된 파일 참조를 제거한다.

## 한 줄 정리

Phase 35는 별도 후속 가이드를 만드는 phase가 아니라,
Final Review에서 최종 판단이 완료되도록 Backtest workflow를 단순화한 phase다.
