# Runs

## 2026-07-17 Design Audit

- finance canonical docs와 Backtest UI ownership 문서 확인
- current Level1 Streamlit surface와 supported strategy entry 확인
- browser에서 current Single Strategy / Portfolio Mix 흐름 확인
- visual companion으로 entry, single, Mix, result, advanced settings, strategy catalog,
  saved Mix 대안 비교
- 사용자 승인 결정을 `DESIGN.md`에 통합

구현 command, test result, Browser QA 결과는 detailed PLAN 실행부터 차수별로
추가한다.

## 2026-07-17 Detailed Plan Audit

- `writing-plans` 절차로 5차 / 9 Task 구현 계획 작성
- 32개 acceptance criteria를 truth, read model, Single, Mix, closeout Task에 배치
- 108개 Markdown code fence 균형 확인
- placeholder / undefined fixture / 보호 파일 검사 명령 self-review 완료
- `git diff --check`와 staged protected-path audit은 계획 commit 직전에 fresh 실행

## 2026-07-18 Execution Baseline

- `.venv`에는 pytest가 없어 `uv run --with pytest`로 repository 변경 없이 runner 주입
- existing boundary + service baseline: 845 passed, 11 failed, 35 subtests passed
- 기존 실패 범위: Sentiment React contract 1건, 이전 Practical Validation / Final Review
  source contract 10건; Level1 소유 파일 변경 전 baseline debt로 기록

## 2026-07-18 Task 1 RED -> GREEN

- RED: 새 `backtest_analysis_decision_workspace` service import 부재로 collection 실패
- GREEN: `3 passed`
- compile: strategy catalog / decision workspace service 통과
- `git diff --check`: 통과

## 2026-07-18 Task 2 RED -> GREEN

- RED: readiness projection / root dedup import 부재로 collection 실패
- GREEN focused: `6 passed`
- existing handoff regression: `3 passed, 829 deselected`
- target compile / `git diff --check`: 통과

## 2026-07-18 Task 3 RED -> GREEN

- RED 1: complete workspace builder import 부재로 collection 실패
- GREEN 1: decision / KPI / error projection 포함 `8 passed`
- RED 2: date가 포함된 configuration / meta / saved Mix JSON 직렬화 실패
- GREEN 2: JSON-ready projection 보강 후 `9 passed`
- target compile / `git diff --check`: 통과

## 2026-07-18 Task 4 RED -> GREEN

- RED: Level1 React source 부재로 boundary test 2건 실패
- React production build: Vite 5.4.21, 175 modules transformed, 성공
- GREEN boundary: `2 passed, 24 deselected`
- ResizeObserver / two-surface / intent-only / 760px contract 확인
- build / node_modules는 `.gitignore` 적용, stage 제외

## 2026-07-18 Task 5 RED -> GREEN

- RED: adapter / fragment / stale marker / fingerprint stamp 부재 4건 실패
- 추가 RED: failed execution이 이전 성공 bundle을 지우는 회귀 재현
- 추가 RED: legacy `Advanced Inputs` / `Promotion Policy Signal` label 재현
- GREEN focused + boundary: `41 passed`
- existing single / latest run / history regression: `4 passed, 828 deselected`
- target py_compile / import smoke / `git diff --check`: 통과

## 2026-07-18 Task 6 RED -> GREEN

- RED: explicit handoff handler 부재 2건과 decision-first 상세 근거 분리 부재 1건 실패
- GREEN focused decision / boundary: `44 passed`
- 관련 service contract: `4 passed, 828 deselected`
- 계획 선택 회귀: `20 passed, 856 deselected`
- React production build: Vite 5.4.21, 175 modules transformed, 성공
- target py_compile / `git diff --check`: 통과
- stale 결과는 삭제·숨김 없이 참고용 상세 근거로 유지하고 Level2 인계만 차단

## 2026-07-18 Task 7 RED -> GREEN

- RED: pure Mix role / weight, legacy role inference, Mix read-model 계약 3건 실패
- GREEN pure contract: `3 passed`
- Mix / saved portfolio 관련 회귀: `12 passed, 837 deselected`
- web-owned weighted Mix Gate를 pure service로 이동하고 직접 caller를 public API로 전환
- weighted bundle / saved replay에 component roles를 추가하되 legacy role-less record는 추론으로 호환
- target py_compile / `git diff --check`: 통과
