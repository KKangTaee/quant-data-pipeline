# Finance Code Analysis

## 목적

이 폴더는 `finance` 코드가 어떤 흐름으로 연결되는지 설명하는 개발자용 지도다.
`FINANCE_COMPREHENSIVE_ANALYSIS.md`가 전체 시스템의 큰 그림이라면,
이 폴더는 실제 코드를 고치거나 새 전략 / 새 script를 추가할 때 보는 실행 흐름 문서다.

## 읽는 순서

| 상황 | 먼저 볼 문서 |
|---|---|
| 어떤 스크립트가 어떤 책임을 갖는지 빠르게 확인 | `SCRIPT_STRUCTURE_MAP.md` |
| backtest 실행이 어디서 시작해 어디서 끝나는지 확인 | `BACKTEST_RUNTIME_FLOW.md` |
| DB / loader / ingestion 흐름 확인 | `DATA_DB_PIPELINE_FLOW.md` |
| Streamlit Backtest UI, compare, history, saved replay 확인 | `WEB_BACKTEST_UI_FLOW.md` |
| Backtest 후보 선정 workflow를 3단계 구조로 재설계할 때 | `BACKTEST_PORTFOLIO_SELECTION_WORKFLOW_REDESIGN_GUIDE.md` |
| 새 전략 family를 추가하거나 기존 전략 연결을 바꿀 때 | `STRATEGY_IMPLEMENTATION_FLOW.md` |
| repo-local helper script나 automation 갱신 | `AUTOMATION_SCRIPTS_GUIDE.md` |

## 기록 원칙

이 폴더는 구현 히스토리 저장소가 아니다.
여기에는 현재 코드를 이해하거나 수정할 때 계속 필요한 구조만 남긴다.

기록한다:

- 새 script가 생기거나 기존 script의 책임이 바뀐 경우
- render / helper / runtime처럼 module boundary를 새로 나눈 경우
- 실행 흐름이 바뀐 경우
- 새 strategy family가 추가된 경우
- 새 DB table, loader, persistence 경로가 생긴 경우
- Backtest UI의 single / compare / history / saved replay 계약이 바뀐 경우
- repo-local helper script가 생기거나 사용 기준이 바뀐 경우

기록하지 않는다:

- 단순 문구 수정
- 작은 UI label 변경
- 일회성 backtest 결과
- phase 진행 내역 자체
- 후보 성과 해석이나 투자 판단

## 다른 문서와의 역할 분리

| 문서 | 역할 |
|---|---|
| `FINANCE_COMPREHENSIVE_ANALYSIS.md` | finance 전체 시스템 구조와 현재 구현 상태의 큰 지도 |
| `SCRIPT_STRUCTURE_MAP.md` | 코드 수정 전 빠르게 보는 script별 책임 지도 |
| `code_analysis/*` | 실제 코드 수정자가 보는 개발자용 흐름 지도 |
| `WORK_PROGRESS.md` | 최근 작업 진행 로그 |
| `QUESTION_AND_ANALYSIS_LOG.md` | 사용자 질문과 설계 판단의 durable summary |
| `phases/phase*/` | phase별 계획, TODO, QA, closeout |
| `backtest_reports/` | 반복 가능한 backtest 결과와 후보 검토 |

## 코드 변경 후 갱신 기준

코드 변경 후 아래 질문 중 하나라도 `yes`면 이 폴더의 문서를 확인한다.

- 새 코드 경로가 기존 flow 문서에 없는가?
- 새 script가 생겼거나 기존 script의 책임 / 위치가 바뀌었는가?
- 다음 사람이 같은 파일을 고치려면 실행 순서를 다시 찾아야 하는가?
- 새 strategy family가 single / compare / history / saved replay 중 일부에 연결됐는가?
- 새 ingestion / DB / loader 경로가 생겼는가?
- 새 helper script가 phase 운영이나 candidate registry 운영에 영향을 주는가?

모든 답이 `no`면 이 폴더를 억지로 수정하지 않는다.

## 기존 참고 문서

`BACKTEST_REFINEMENT_CODE_FLOW_GUIDE.md`는 기존 backtest refinement 중심 안내 문서다.
이 폴더의 문서는 그 문서를 대체하기보다,
앞으로 코드 흐름별로 더 명확히 쪼개 관리하기 위한 기준점이다.
