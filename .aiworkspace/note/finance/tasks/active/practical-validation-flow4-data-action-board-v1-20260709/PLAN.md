# Practical Validation Flow4 Data Action Board V1

Status: Completed
Date: 2026-07-09

## 이걸 하는 이유?

Practical Validation Flow 4가 `단계별 검증 소유권`, `수집 대상 근거`, `근거 부록` expander를 나란히 보여주면 사용자는 지금 해결할 데이터 보강 항목과 Final Review / Monitoring에서 판단할 참고 항목을 구분하기 어렵다.

이번 작업은 Flow 4를 `카테고리별 검증 결과 -> 데이터 보강 대상 / 액션 -> 상세 근거 / 원자료` 순서로 읽게 하고, React는 표시 전용 보드만 맡기며 수집 / 실행 / 계산 / gate / 저장은 기존 Python service 경계에 남기는 데 목적이 있다.

## Tentative Roadmap

1. Context / contract 정리와 active task 기록 생성.
2. `app/services/backtest_practical_validation_workspace.py`에 `data_action_board` read model 추가.
3. 표시 전용 React component `practical_validation_data_action_board` 추가.
4. `app/web/backtest_practical_validation/page.py`에서 stage ownership expander와 `수집 대상 근거` expander를 제거하고 새 보드로 연결.
5. Focused unittest / compile / diff check / Browser QA / durable docs sync / commit.

## Scope

- 변경 화면: `Backtest > Practical Validation` Flow 4.
- 변경 코드 후보:
  - `app/services/backtest_practical_validation_workspace.py`
  - `app/web/backtest_practical_validation/page.py`
  - `app/web/backtest_practical_validation/components.py`
  - `app/web/components/practical_validation_data_action_board/`
  - `tests/test_service_contracts.py`
- 변경 문서 후보:
  - `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
  - `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
  - `.aiworkspace/note/finance/docs/ROADMAP.md`
  - `.aiworkspace/note/finance/docs/INDEX.md`
  - root handoff logs

## Out Of Scope

- provider / FRED / API / DB direct fetch를 React에 추가하지 않는다.
- 새 수집 엔진, DB schema, provider fetch path, registry / saved JSONL write를 만들지 않는다.
- validation threshold, replay 실행, Final Review gate / selected-route policy, live approval / broker order / auto rebalance 의미를 바꾸지 않는다.

## Completion

- Flow 4 user-facing UI에서 `단계별 검증 소유권`이 보이지 않는다.
- `수집 대상 근거`는 별도 expander가 아니라 데이터 보강 대상 보드 안의 compact evidence로 보인다.
- `근거 부록`은 삭제하지 않고 `상세 근거 / 원자료` 보조 영역으로 낮춘다.
- React component는 props만 렌더링하고 provider fetch / gate / write / replay를 수행하지 않는다.
- Focused tests, py_compile, git diff check, Browser QA를 수행하고 generated artifact는 stage하지 않는다.

## Result

- 1차~5차 완료.
- Browser QA screenshot: `practical-validation-flow4-data-action-board-v1-qa.png` generated artifact, not staged.
