# Practical Validation Commercial UX V1

Status: Complete
Started: 2026-05-30
Completed: 2026-05-31

## 이걸 하는 이유?

Practical Validation의 module gate와 evidence board 구조는 정리됐지만, 화면은 여전히 raw dataframe과 기본 Streamlit container가 많아 분석 콘솔처럼 보인다.
사용자는 Final Review 이동 가능 여부, 무엇을 먼저 보강해야 하는지, 근거 보드는 어떤 의미인지 빠르게 읽어야 한다.

이번 작업은 검증 계약을 바꾸지 않고 표시 계층을 summary-first 구조로 개편해 상용 제품에 가까운 UX로 다듬는다.

## Scope

- Practical Validation 전용 visual helper / CSS 추가
- Practical Validation 전용 product shell component를 분리해 기존 Streamlit container 중심 화면에서 벗어남
- Final Review Gate blocker를 fix queue 중심으로 표시
- Evidence board를 탭 / summary-first 구조로 재배치
- Provider gap 보강 액션을 action center로 표시
- 기존 dataframe / raw JSON은 상세 접힘 영역으로 낮춤
- 선택 후보 확인에 Backtest Analysis summary / equity curve / result table snapshot 표시
- 최신 runtime replay 결과는 현재 세션에서 실행한 뒤에만 표시
- 저장-only는 audit trail로 유지하고 Final Review 후보 노출은 Gate 통과 result로 제한
- Step 1~7 본문 경계 surface와 7-step rail 표시
- focused compile, service contract, boundary, browser QA 실행

## Out Of Scope

- validation module 판정 정책 변경
- Final Review selected-route gate 변경
- provider / macro collector 변경
- registry JSONL 재작성
- broker order, live approval, auto rebalance 기능 추가
