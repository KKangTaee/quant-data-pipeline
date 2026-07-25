# Notes

## 2026-07-25 — Approved Direction

- User approved the recommended `Task-oriented Hybrid`.
- The UI should organize collection around consumer goals, not collector names.
- Backend actions are preserved unless a later implementation finding justifies explicit deletion.

## Product Decisions

- Streamlit remains appropriate for this internal operator surface in V1.
- No new raw status dashboard is added.
- No automatic multi-step execution is added.
- No scheduler or background worker is added.
- Raw logs / failure CSV / result JSON remain backend artifacts, not default product UI.
- History defaults to Data Operations actions and does not mix generic app jobs.

## Key Design Constraint

Moving an action to Advanced is not the same as deprecating its backend.
Compatibility actions remain replay-only and are not promoted to active execution.

## 2026-07-26 — Advanced Tools Functional Audit

### Confirmed Contracts

- active action 30개는 workflow ownership, `sections.py` renderer literal,
  `dispatcher.py` route, `JOB_GUIDE`와 `next_action`을 모두 가진다.
- 26개 `db_write` action은 모두 `st.button(...)` 분기 안에서만
  `_schedule_job(...)`을 호출한다. initial render나 expander open만으로
  collection job이 예약되는 경로는 발견하지 않았다.
- 동시에 한 job만 `pending -> running`으로 승격하는 기존 contract가 유지된다.
- 4개 diagnosis action은 finance data row를 쓰지 않고 normalized result를
  만든다. 단, job history / result artifact persistence는 기존 공통 실행
  경계에서 유지된다.

### Important Semantics

- `read_only`는 “DB의 finance data row를 쓰지 않는다”는 뜻이지
  “네트워크 호출이 없다”는 뜻은 아니다.
- Price Stale Diagnosis는 provider freshness probe를 수행한다.
- Statement Coverage Diagnosis와 PIT Inspection은 선택 범위에서 live EDGAR
  source sample을 읽을 수 있다.
- Statement Universe Coverage QA는 DB-backed coverage inspection이다.

### Findings

- 이전 action focus가 섹션 이동 뒤에도 남던 문제는 이번 구현에서 해소했다.
- Streamlit expander는 닫혀 있어도 body를 평가하므로 operational section의
  여러 form과 DB-backed preflight가 첫 진입 비용에 포함된다. collection은
  시작하지 않지만 느린 첫 화면이나 DB 장애 노출 가능성이 있다.
- `sections.py`가 `_bind_page_globals()`로 `page.py` namespace를 동적으로
  복사하는 구조는 현재 action 누락을 만들지는 않았지만 dependency drift를
  정적 분석하기 어렵게 한다.
- 실제 provider/DB write collection은 QA에서 실행하지 않았으므로
  외부 provider의 현재 가용성, rate limit, 실제 저장 성공은 이번 UI audit의
  검증 범위가 아니다.
