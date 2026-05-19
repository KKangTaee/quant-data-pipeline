# UI Engine Boundary Foundation Plan

Status: Active
Created: 2026-05-19

## 이걸 하는 이유?

현재 목표는 Streamlit을 다른 UI framework로 바꾸는 것이 아니다.
먼저 같은 Python 코드 안에서 UI와 engine의 책임을 분리해, 나중에 어떤 UI를 쓰더라도 backtest / validation / data runtime을 재사용할 수 있게 만드는 것이다.

현재 결합은 `app/web` 화면 코드가 직접 runtime dispatch, Streamlit session state, registry 저장, validation 계산 일부를 함께 처리하는 데서 생긴다.
이 상태에서는 UI agent와 engine agent가 같은 파일을 동시에 고칠 가능성이 높고, UI 수정이 backtest 동작을 깨뜨렸는지 빠르게 확인하기 어렵다.

이 phase가 끝나면 Streamlit 화면은 유지하되, 핵심 실행 로직은 `app/services/*`의 Streamlit-free service contract를 통해 호출하는 방향으로 이동한다.

## Scope

포함한다.

- 현재 Backtest / Practical Validation / Final Review / Selected Dashboard 코드 흐름 audit
- `app/services`를 UI-engine boundary로 정의
- Single Backtest execution service 첫 분리
- Compare / Weighted Portfolio service 분리 계획
- Practical Validation calculation / persistence / UI handoff 분리 계획
- Final Review / Selected Dashboard read model 후보 정의
- phase/task 문서와 검증 기준 정리

포함하지 않는다.

- React / Next.js / FastAPI 구현
- Streamlit 화면 UX 변경
- DB schema 변경
- provider ingestion collector 변경
- strategy simulation 로직 변경
- registry JSONL 재작성
- live trading, broker order, auto rebalance

## Target Architecture

```text
Streamlit UI
  -> app/services/*
  -> app/web/runtime/* or finance/*
  -> finance/loaders/*
  -> finance/sample.py / finance/engine.py / finance/strategy.py
  -> finance/performance.py
  -> result / evidence / read model
  -> UI state or append-only registry
```

`app/services`는 Streamlit을 import하지 않는다.
`app/web`은 화면, form, session state, routing, feedback을 담당한다.
`finance/*`는 data, loader, strategy, transform, performance 책임을 유지한다.

## Phase Tasks

| Order | Task | Goal | Status |
| --- | --- | --- | --- |
| 1 | `ui-engine-boundary-audit` | 파일별 책임과 결합 지점을 확정한다 | Complete |
| 2 | `backtest-execution-service-boundary` | Single Strategy 실행 dispatch를 service로 분리한다 | Complete |
| 3 | `compare-service-boundary` | Compare / weighted portfolio 실행 경계를 service 후보로 분리한다 | Complete |
| 4 | `practical-validation-service-boundary` | diagnostics calculation, persistence, UI handoff를 분리한다 | Complete |
| 5 | `evidence-read-model-boundary` | Final Review / Selected Dashboard가 공유할 read model을 정의한다 | Complete |

## First Implementation Slice

첫 구현은 `backtest-execution-service-boundary`로 제한한다.

예상 파일:

- create: `app/services/backtest_execution.py`
- modify: `app/web/backtest_single_runner.py`
- optional tests or smoke scripts under existing test pattern if available

유지할 것:

- 기존 Streamlit 화면 동작
- 기존 result bundle shape
- 기존 `st.session_state` key
- 기존 run history append 위치
- 기존 `BacktestInputError`, `BacktestDataError` 사용자-facing error category

처음부터 옮기지 않을 것:

- Compare 실행
- Practical Validation 실행
- registry write contract 전체
- FastAPI / API endpoint
- frontend framework

## Done Criteria

- phase 문서와 첫 audit task 문서가 생성되어 있다.
- 첫 audit task가 주요 결합 지점과 다음 구현 순서를 기록한다.
- service boundary 원칙이 phase 문서에 고정되어 있다.
- 첫 service extraction task를 시작할 수 있을 만큼 target file, risk, validation이 명확하다.
- 이후 구현 task는 `finance-backtest-web-workflow`와 필요 시 `finance-integration-review` 기준으로 진행한다.
