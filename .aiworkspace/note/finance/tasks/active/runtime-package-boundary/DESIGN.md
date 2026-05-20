# Runtime Package Boundary Design

Status: Complete
Created: 2026-05-20

## Before

```text
app/services/*
  -> app.web.runtime.*

app/web/*
  -> app.web.runtime.*
```

문제는 `runtime`이 UI 폴더 아래 있어서, service layer가 web package를 import하는 것처럼 보인다는 점이다.

## 5-01 Target

```text
app/services/*
  -> app.runtime.*

app/web/*
  -> app.runtime.*
```

`app/runtime`은 Streamlit-free runtime / repository layer로 둔다.
`app/web`은 화면 render와 session state / button action만 맡는다.

## Migration Rule

- 모든 Python import를 새 경로로 전환한다.
- 기존 JSONL 파일 위치와 schema version constant는 유지한다.
- old compatibility wrapper는 이번 slice에서는 만들지 않는다. repo 내부 사용처를 모두 전환해 stale path를 남기지 않는 것이 목적이다.

## 5-02 Target

```text
app/runtime/final_selected_portfolios.py
  -> app/runtime/candidate_library.py

app/web/backtest_candidate_library.py
  -> app/runtime/candidate_library.py
```

Candidate Library의 table row, replay payload, replay dispatch helper는 Streamlit-free이므로 runtime package에 둔다.
