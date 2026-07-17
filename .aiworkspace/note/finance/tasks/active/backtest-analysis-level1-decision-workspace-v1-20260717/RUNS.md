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
