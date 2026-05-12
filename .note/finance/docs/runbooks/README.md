# Finance Runbooks

Status: Active
Last Verified: 2026-05-12

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
find .note/finance -maxdepth 3 -type d | sort
find .note/finance -maxdepth 3 -type f | sort
```

## Commit Hygiene

- `registries/*.jsonl`, `run_history/*.jsonl`, runtime artifact, temp CSV는 명시 요청 없이는 커밋하지 않는다.
- `.DS_Store`와 `.playwright-mcp/`는 커밋하지 않는다.
- 문서 재구성처럼 큰 변경은 삭제 전후 구조 확인 결과를 최종 응답에 요약한다.
