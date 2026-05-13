# Finance Runbooks

Status: Active
Last Verified: 2026-05-13

## Local App

기존 Streamlit app은 보통 아래 방식으로 실행한다.

```bash
streamlit run app/web/streamlit_app.py
```

이미 실행 중인 포트가 있으면 다른 포트를 사용한다.

## Focused Checks

문서 변경:

```bash
git status --short
git diff --stat
```

Python UI/helper 변경:

```bash
.venv/bin/python -m py_compile app/web/backtest_practical_validation.py
```

문서 구조 확인:

```bash
find .aiworkspace/note/finance -maxdepth 3 -type d | sort
find .aiworkspace/note/finance -maxdepth 3 -type f | sort
```

## Commit Hygiene

- `registries/*.jsonl`, `run_history/*.jsonl`, runtime artifact, temp CSV는 명시 요청 없이는 커밋하지 않는다.
- `.DS_Store`와 `.playwright-mcp/`는 커밋하지 않는다.
- 문서 재구성처럼 큰 변경은 삭제 전후 구조 확인 결과를 최종 응답에 요약한다.

## Root Log Hygiene

Root log는 긴 작업 노트를 보관하는 곳이 아니라, 다음 세션이 현재 위치를 빠르게 찾는 handoff map이다.

| 문서 | root에 남길 내용 | 상세를 보낼 곳 |
|---|---|---|
| `.aiworkspace/note/finance/WORK_PROGRESS.md` | 작업 단위당 3~5줄의 milestone, 완료 내용, 다음 확인 위치 | active task `STATUS.md`, `RUNS.md`, `NOTES.md` |
| `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | 질문 주제, 해석한 목표, 결론, 후속 결정 | active task `NOTES.md` 또는 관련 `DESIGN.md` |

운영 기준:

- 실행 명령과 긴 출력은 root log가 아니라 `RUNS.md`에 남긴다.
- 긴 설계 판단, 대안 비교, 시행착오는 `NOTES.md`나 `DESIGN.md`에 남긴다.
- root log에는 "무엇을 결정 / 완료했고 어느 문서를 보면 되는지"만 남긴다.
- 질문 분석은 `User request`, `Interpreted goal`, `Analysis result`, `Follow-up` 구조를 유지하되, 각 항목을 짧게 쓴다.
- root log가 비대해질 것 같으면 먼저 active task 문서를 만들거나 기존 active task 문서로 상세를 넘긴다.

## Runtime Artifact Hygiene

Runtime artifact는 작업 중 상태를 재현하거나 디버깅하는 데는 쓸 수 있지만 장기 문서가 아니다.

기본적으로 커밋하지 않는다.

| Artifact | Policy |
|---|---|
| `.aiworkspace/note/finance/run_history/*.jsonl` | local run history. 명시 요청 없이는 commit 제외 |
| `.aiworkspace/note/finance/run_artifacts/` | local job / ingestion artifact. commit 제외 |
| `_tmp_*.csv`, failure CSV | 임시 산출물. 필요한 해석은 report나 task note에 요약 |
| `.DS_Store`, `.playwright-mcp/` | generated / local output. commit 제외 |
| `.aiworkspace/note/finance/saved/*.jsonl` | 사용자가 저장한 reusable setup. 삭제 금지, 임의 재작성 금지 |

중요한 backtest 결과를 남기려면 runtime artifact를 그대로 보존하지 말고
`.aiworkspace/note/finance/reports/backtests/` 아래 사람이 읽는 report나 strategy log에 요약한다.

## External Research / Browser Research

외부 리서치는 현재 구현 근거를 보강할 때만 장기 문서로 승격한다.

원칙:

- 공식 문서, provider 문서, 논문, 데이터 원천을 우선한다.
- 웹 조사 결과는 source URL과 확인 날짜를 남긴다.
- 투자 추천처럼 보이는 문구가 아니라 구현 판단, 데이터 출처, 검증 한계를 남긴다.
- 반복 가능한 결과는 backtest report나 active task 문서에 둔다.
- 오래 유지될 운영 기준만 `docs/`로 승격한다.

Market / provider research 결과를 앱 기능으로 쓰려면
`Ingestion -> DB -> Loader -> UI` 흐름으로 구현한다.
UI에서 provider / FRED / 웹페이지를 직접 fetch하지 않는다.

## Config / Constant Externalization

설정 외부화는 아래 순서로 검토한다.

1. DB credential이나 environment-specific 값
2. ingestion batch size, retry, sleep 같은 운영 파라미터
3. default lookback, period, provider source map 같은 재사용 설정
4. 단순 UI label이나 낮은 우선순위 표시 상수

단순히 코드 안에 상수가 있다는 이유만으로 config 파일을 늘리지 않는다.
반복 실행, 환경 차이, provider 변경 가능성이 있을 때 우선 외부화한다.

## Automation Helpers

Repo-local helper script 사용 기준은 [AUTOMATION_SCRIPTS.md](./AUTOMATION_SCRIPTS.md)를 본다.

## Templates

Phase helper가 사용하는 template은 아래에 둔다.

- [PHASE_PLAN_TEMPLATE.md](./templates/PHASE_PLAN_TEMPLATE.md)
- [PHASE_TEST_CHECKLIST_TEMPLATE.md](./templates/PHASE_TEST_CHECKLIST_TEMPLATE.md)

이 template은 root legacy 문서가 아니라 helper script가 읽는 source file이다.
