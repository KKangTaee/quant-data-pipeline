# Finance Canonical Docs Alignment V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `INDEX.md`, `PRODUCT_DIRECTION.md`, `PROJECT_MAP.md`, `ROADMAP.md`를 현재 Finance Console과 일치하는 역할 분리형 canonical 문서로 개편한다.

**Architecture:** INDEX는 문서 router, Product Direction은 제품 목적과 사용자 가치, Project Map은 code/runtime/storage ownership, Roadmap은 현재 상태와 다음 결정을 각각 단독 소유한다. 완료 task의 상세 기록은 기존 task·phase·root handoff에 보존하고 canonical 문서에서 반복하지 않는다.

**Tech Stack:** Markdown, Python 3.12+, Streamlit route contract, local path/link validation, Git

## Global Constraints

- current top navigation은 `Research / Portfolio / Data / Help`다.
- current top-level surface는 `Today / Market Research / Institutional Holdings / Portfolio Lab / Portfolio Monitoring / Data Operations / Reference Center`다.
- Practical Validation과 Final Review는 Portfolio Lab 내부 stage다.
- implemented fact, paused work, verification-only work와 future decision을 분리한다.
- 제품 code, UI, DB schema, runtime behavior와 provider contract를 변경하지 않는다.
- 완료 task / phase 기록은 삭제하거나 이동하지 않는다.
- `registries/`, `saved/`, `run_history/`와 generated QA artifact를 변경하거나 stage하지 않는다.
- detailed algorithm, payload와 UX history는 architecture / flow / data / task 문서로 연결한다.
- user-facing old navigation `Workspace >`, `Operations >`, `Backtest >`, `Reference >`를 네 canonical 문서에서 제거한다.

---

## 이걸 하는 이유?

현재 네 문서는 최신 구현과 과거 작업 이력을 동시에 소유해, 처음 읽는 사람과 AI가
제품 목적, 실제 화면, code ownership과 다음 결정을 빠르게 구분하기 어렵다.
특히 ROADMAP은 1,291줄의 완료 작업 changelog가 되었고 INDEX도 task link 124개를
직접 나열한다. 이번 개편은 상세 이력을 보존하면서 첫 읽기 경로만 안정된 구조로
되돌린다.

## Files And Responsibilities

### Modify

- `.aiworkspace/note/finance/docs/INDEX.md`
  - 문서 체계의 stable discovery router
- `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
  - product promise, user journey, principles, non-goals
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
  - layers, product surface entry points, workflow / storage ownership
- `.aiworkspace/note/finance/docs/ROADMAP.md`
  - current baseline, active / paused / verification-only state, decision queue
- `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/*`
  - 계획, 설계, 상태, 실행 결과와 위험
- `.aiworkspace/note/finance/WORK_PROGRESS.md`
  - 3~5줄 closeout pointer
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
  - user request, interpreted goal, result, follow-up

### Read-Only Sources Of Truth

- `README.md`
- `app/web/streamlit_app.py`
- `app/web/`, `app/services/`, `app/runtime/`, `app/jobs/`
- `finance/data/`, `finance/loaders/`, `finance/*.py`
- `.aiworkspace/note/finance/docs/architecture/`
- `.aiworkspace/note/finance/docs/flows/`
- `.aiworkspace/note/finance/docs/data/`
- `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- named current / paused / verification-only task `STATUS.md`

---

### Task 1: INDEX를 stable documentation router로 축소

**Files:**

- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RUNS.md`

**Interfaces:**

- Consumes: `DESIGN.md`의 canonical reading flow와 workspace boundary
- Produces: Tasks 2–4가 연결할 stable document discovery contract

- [x] **Step 1: 기존 INDEX rolling-history assertion 실행**

Run:

```bash
test "$(rg -o 'tasks/(active|done)/' .aiworkspace/note/finance/docs/INDEX.md | wc -l | tr -d ' ')" -gt 100
rg -q "## Current Phase State" .aiworkspace/note/finance/docs/INDEX.md
```

Expected: exit 0. INDEX가 task catalog와 phase-state dump를 포함한다.

- [x] **Step 2: INDEX를 다음 section으로 전면 재작성**

```text
# Finance Documentation Index
## Purpose
## Start Here
## Reading Paths
## Canonical Docs By Concern
## Current Work Pointers
## Workspace Boundaries
## Maintenance Rules
```

`Current Work Pointers`는 `ROADMAP.md`, task active index,
task / phase `STATUS_MANIFEST.md`만 연결하고 개별 완료 task를 나열하지 않는다.

- [x] **Step 3: INDEX 역할 assertion 실행**

Run:

```bash
test "$(wc -l < .aiworkspace/note/finance/docs/INDEX.md)" -le 110
test "$(rg -o 'tasks/(active|done)/' .aiworkspace/note/finance/docs/INDEX.md | wc -l | tr -d ' ')" -le 3
for heading in "Start Here" "Reading Paths" "Canonical Docs By Concern" "Current Work Pointers" "Workspace Boundaries" "Maintenance Rules"; do
  rg -q "^## $heading$" .aiworkspace/note/finance/docs/INDEX.md || exit 1
done
```

Expected: exit 0.

- [x] **Step 4: INDEX local link 검사**

Run:

```bash
uv run python - <<'PY'
from pathlib import Path
import re

path = Path(".aiworkspace/note/finance/docs/INDEX.md")
missing = []
for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
    if "://" in target or target.startswith("#"):
        continue
    resolved = (path.parent / target.split("#", 1)[0]).resolve()
    if not resolved.exists():
        missing.append(target)
assert not missing, missing
print("INDEX links OK")
PY
```

Expected: `INDEX links OK`.

- [x] **Step 5: 1차 commit**

```bash
git add \
  .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/STATUS.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RUNS.md
git commit -m "finance 문서 인덱스 재구성"
```

---

### Task 2: Product Direction을 현재 사용자 가치와 경계로 재작성

**Files:**

- Modify: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RUNS.md`

**Interfaces:**

- Consumes: current navigation and README product contract
- Produces: stable product promise and surface meaning for Roadmap / Project Map

- [ ] **Step 1: stale navigation assertion 실행**

Run:

```bash
rg -n "Workspace >|Operations >|Backtest >|Reference >" \
  .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md
```

Expected: old user-facing navigation expressions are found.

- [ ] **Step 2: Product Direction을 다음 section으로 전면 재작성**

```text
# Product Direction
## Product Promise
## Who It Is For
## User Journey
## Current Product Surfaces
## Product Principles
## Safety And Non-Goals
## Current Maturity And Known Limits
## Related Canonical Docs
```

`Current Product Surfaces`는 4개 navigation group과 7개 top-level surface를
사용자 완료 작업 기준으로 설명한다. `Portfolio Lab` 내부에 Backtest Analysis,
Practical Validation, Final Review를 둔다.

- [ ] **Step 3: current product contract assertion 실행**

Run:

```bash
for label in "Research" "Portfolio" "Data" "Help" "Today" "Market Research" \
  "Institutional Holdings" "Portfolio Lab" "Portfolio Monitoring" \
  "Data Operations" "Reference Center" "Practical Validation" "Final Review"; do
  rg -q "$label" .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md || exit 1
done
! rg -n "Workspace >|Operations >|Backtest >|Reference >" \
  .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md
```

Expected: exit 0.

- [ ] **Step 4: product boundary assertion 실행**

Run:

```bash
for boundary in "broker" "auto rebalance" "수익 보장" "DB-Backed" "Point-in-Time" "Context Is Not Approval"; do
  rg -qi "$boundary" .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md || exit 1
done
```

Expected: exit 0.

- [ ] **Step 5: 2차 commit**

```bash
git add \
  .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/STATUS.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/NOTES.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RUNS.md
git commit -m "finance 제품 방향 현재화"
```

---

### Task 3: Project Map을 ownership 중심 quick map으로 재작성

**Files:**

- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RUNS.md`

**Interfaces:**

- Consumes: Task 2 surface names, actual code tree, focused architecture / flow / data docs
- Produces: route / layer / workflow / storage ownership map used by developers and AI

- [ ] **Step 1: actual entry point inventory 확인**

Run:

```bash
rg --files app finance | sort > /tmp/finance-canonical-doc-paths.txt
rg -n "title=\"(Today|Market Research|Institutional Holdings|Portfolio Lab|Portfolio Monitoring|Data Operations|Reference Center)\"" \
  app/web/streamlit_app.py
```

Expected: 7개 `st.Page` title과 current code inventory가 확인된다.

- [ ] **Step 2: Project Map을 다음 section으로 전면 재작성**

```text
# Finance Project Map
## System At A Glance
## Layer Ownership
## Product Surface Entry Points
## Workflow Ownership
## Data And Storage Boundaries
## Where To Start By Change Type
## Detailed Documentation
```

surface entry table은 top-level route adapter, primary service/runtime owner,
React workbench와 downstream flow만 적는다. domain algorithm과 UX history는
focused docs link로 넘긴다.

- [ ] **Step 3: route / layer assertion 실행**

Run:

```bash
for label in "Today" "Market Research" "Institutional Holdings" "Portfolio Lab" \
  "Portfolio Monitoring" "Data Operations" "Reference Center"; do
  rg -q "$label" .aiworkspace/note/finance/docs/PROJECT_MAP.md || exit 1
done
for layer in "app/web" "app/services" "app/runtime" "app/jobs" \
  "finance/data" "finance/loaders" "finance/engine.py" "finance/strategy.py" \
  "finance/transform.py" "finance/performance.py"; do
  rg -q "$layer" .aiworkspace/note/finance/docs/PROJECT_MAP.md || exit 1
done
```

Expected: exit 0.

- [ ] **Step 4: Project Map local path 검사**

Run:

```bash
uv run python - <<'PY'
from pathlib import Path
import re

path = Path(".aiworkspace/note/finance/docs/PROJECT_MAP.md")
missing = []
for token in re.findall(r"`((?:app|finance|tests|\.aiworkspace)/[^`]+)`", path.read_text()):
    if any(char in token for char in ("*", "<", ">", " -> ")):
        continue
    candidate = Path(token.rstrip(".,;:"))
    if not candidate.exists():
        missing.append(token)
assert not missing, missing
print("PROJECT_MAP paths OK")
PY
```

Expected: `PROJECT_MAP paths OK`.

- [ ] **Step 5: Project Map scope / stale-name 검사**

Run:

```bash
test "$(wc -l < .aiworkspace/note/finance/docs/PROJECT_MAP.md)" -le 260
! rg -n "Workspace >|Operations >|Backtest >|Reference >" \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md
git diff --check -- .aiworkspace/note/finance/docs/PROJECT_MAP.md
```

Expected: exit 0.

- [ ] **Step 6: 3차 commit**

```bash
git add \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/STATUS.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/NOTES.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RUNS.md
git commit -m "finance 프로젝트 지도 간결화"
```

---

### Task 4: Roadmap을 current state와 decision queue로 재작성

**Files:**

- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RISKS.md`

**Interfaces:**

- Consumes: Tasks 1–3 stable roles and named task `STATUS.md`
- Produces: current baseline, paused / verification-only state, prioritized approval queue

- [ ] **Step 1: source statuses 재확인**

Run:

```bash
sed -n '1,120p' \
  .aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/STATUS.md
sed -n '1,120p' \
  .aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/STATUS.md
sed -n '1,120p' \
  .aiworkspace/note/finance/tasks/active/market-movers-chart-navigation-polish-v1-20260721/STATUS.md
```

Expected: Sentiment next work is paused; two named tasks are implementation-complete with Browser QA debt.

- [ ] **Step 2: Roadmap을 다음 section으로 전면 재작성**

```text
# Finance Roadmap
## Current Snapshot
## Implemented Baseline
## Current Work State
## Next Decision Queue
## Recommended Order
## Completion And Approval Rules
## Work Model
## Update Rules
```

`Current Work State`는 active, paused, verification-only를 분리한다.
`Next Decision Queue`는 correctness, product-value, maintenance 순으로
후보와 승인 필요 지점을 기록한다.

- [ ] **Step 3: roadmap size / history assertion 실행**

Run:

```bash
test "$(wc -l < .aiworkspace/note/finance/docs/ROADMAP.md)" -le 240
test "$(rg -o 'tasks/(active|done)/' .aiworkspace/note/finance/docs/ROADMAP.md | wc -l | tr -d ' ')" -le 12
for heading in "Current Snapshot" "Implemented Baseline" "Current Work State" \
  "Next Decision Queue" "Recommended Order" "Completion And Approval Rules" \
  "Work Model" "Update Rules"; do
  rg -q "^## $heading$" .aiworkspace/note/finance/docs/ROADMAP.md || exit 1
done
```

Expected: exit 0.

- [ ] **Step 4: state meaning assertion 실행**

Run:

```bash
for label in "Active" "Paused" "Verification-Only" "승인"; do
  rg -q "$label" .aiworkspace/note/finance/docs/ROADMAP.md || exit 1
done
! rg -n "Workspace >|Operations >|Backtest >|Reference >" \
  .aiworkspace/note/finance/docs/ROADMAP.md
```

Expected: exit 0.

- [ ] **Step 5: 4차 content commit**

```bash
git add \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726
git commit -m "finance 로드맵 현재 상태 중심 재작성"
```

---

### Task 5: Cross-Document Verification And Closeout

**Files:**

- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**

- Consumes: four rewritten canonical docs
- Produces: verified 4/4 closeout and root handoff

- [ ] **Step 1: 모든 canonical doc local link 검사**

Run:

```bash
uv run python - <<'PY'
from pathlib import Path
import re

docs = [
    Path(".aiworkspace/note/finance/docs/INDEX.md"),
    Path(".aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md"),
    Path(".aiworkspace/note/finance/docs/PROJECT_MAP.md"),
    Path(".aiworkspace/note/finance/docs/ROADMAP.md"),
]
missing = []
for path in docs:
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
        if "://" in target or target.startswith("#"):
            continue
        resolved = (path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            missing.append((str(path), target))
assert not missing, missing
print("canonical doc links OK")
PY
```

Expected: `canonical doc links OK`.

- [ ] **Step 2: navigation과 stale-name 교차 검사**

Run:

```bash
uv run python - <<'PY'
from pathlib import Path

app = Path("app/web/streamlit_app.py").read_text()
docs = "\n".join(
    Path(".aiworkspace/note/finance/docs", name).read_text()
    for name in ("INDEX.md", "PRODUCT_DIRECTION.md", "PROJECT_MAP.md", "ROADMAP.md")
)
for group in ("Research", "Portfolio", "Data", "Help"):
    assert f'"{group}"' in app
for title in (
    "Today",
    "Market Research",
    "Institutional Holdings",
    "Portfolio Lab",
    "Portfolio Monitoring",
    "Data Operations",
    "Reference Center",
):
    assert f'title="{title}"' in app
    assert title in docs
for stale in ("Workspace >", "Operations >", "Backtest >", "Reference >"):
    assert stale not in docs, stale
print("navigation contract OK")
PY
```

Expected: `navigation contract OK`.

- [ ] **Step 3: task closeout과 root handoff 기록**

기록할 상태:

```text
PLAN: 모든 checkbox 완료
STATUS: Completed, 전체 roadmap 4/4차
RUNS: line/link/path/navigation/state 검증 결과
NOTES: final responsibilities and maintenance contract
RISKS: blocker none, remaining follow-up boundaries
WORK_PROGRESS: 3~5줄 milestone과 task path
QUESTION_AND_ANALYSIS_LOG: request / interpreted goal / result / follow-up
```

- [ ] **Step 4: final hygiene / protected-path stage audit**

Run:

```bash
git diff --check
git status --short
git diff --cached --name-only
```

Expected:

```text
diff check exit 0
registry / saved / run_history / unrelated QA artifact not staged
canonical docs, this task docs, two root handoff logs only
```

- [ ] **Step 5: final closeout commit**

```bash
git add \
  .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/tasks/active/finance-canonical-docs-alignment-v1-20260726 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "finance 핵심 문서 정렬 완료"
```

## Done Criteria

- INDEX는 stable router이고 개별 완료 task catalog가 아니다.
- Product Direction은 제품 목적, 사용자 흐름과 non-goal을 설명한다.
- Project Map은 현재 code / runtime / storage ownership을 빠르게 찾게 한다.
- Roadmap은 current baseline, 실제 open state와 다음 승인 결정을 보여준다.
- 네 문서가 current navigation과 7개 top-level surface에 일치한다.
- local links, 주요 code path, Markdown structure와 stale-name 검사가 통과한다.
- 완료 이력과 product data는 삭제·이동·재작성하지 않는다.
