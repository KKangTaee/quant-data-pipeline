# Phase 27 Current Chapter TODO

## 진행 상태

- `complete`

## 검증 상태

- `manual_qa_completed`

## 현재 목표

Phase 27의 목표는 백테스트 결과의 숫자 자체를 개선하는 것이 아니다.
백테스트 실행 전후에 데이터 신뢰성, 계산 가능 기간, 제외 ticker, 결측 가격 행을 사용자가 바로 볼 수 있게 만드는 것이다.

## 1. Backtest Data Trust Summary

- `completed` runtime result window metadata 추가
  - result bundle에 실제 결과 시작일, 실제 결과 종료일, 결과 row 수를 남긴다.
- `completed` latest run 결과 상단 summary 추가
  - `Latest Backtest Run`에서 요청 종료일, 실제 결과 종료일, 가격 최신성, 제외 ticker 수를 보여준다.
- `completed` malformed / excluded detail surface 추가
  - 제외 ticker와 결측 가격 행을 `Data Quality Details`에서 확인할 수 있게 한다.

## 2. Global Relative Strength Preflight

- `completed` single strategy 실행 전 price freshness preflight 연결
  - GRS universe, cash ticker, benchmark ticker의 가격 최신성을 실행 전에 보여준다.
- `completed` runtime meta에 price freshness 저장
  - GRS 결과의 `Meta`와 `Data Trust Summary`에서 같은 정보를 확인할 수 있게 한다.

## 3. Phase 28로 넘기는 항목

- warning 문구 한글화 / 설명 정리 확대
  - stale / missing / malformed / excluded 의미를 더 일관되게 설명한다.
- compare / history / saved replay 확장 검토
  - 단일 실행뿐 아니라 비교 / 저장 / 재실행 흐름에서도 Data Trust Summary를 유지할지 확인한다.
- strict annual / quarterly preflight 표현 정리
  - 기존 strict family preflight를 Phase 27 용어와 맞춘다.

## 4. Validation

- `completed` `python3 -m py_compile app/web/runtime/backtest.py app/web/pages/backtest.py`
- `completed` `.venv` import smoke
- `completed` finance refinement hygiene check
- `completed` `git diff --check`
- `completed` Global Relative Strength manual UI validation
- `completed` generated history files unstaged 확인

## 5. Documentation Sync

- `completed` phase kickoff bundle 생성
- `completed` Phase 27 plan / TODO 작성
- `completed` first work-unit 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` code_analysis / data_architecture sync

## 현재 판단

Phase 27은 complete 상태다.
`Backtest Data Trust Summary + Global Relative Strength preflight`는 구현/문서 동기화/사용자 QA까지 완료됐다.
남은 확장 후보는 Phase 28의 strategy family parity 작업에서 다룬다.
