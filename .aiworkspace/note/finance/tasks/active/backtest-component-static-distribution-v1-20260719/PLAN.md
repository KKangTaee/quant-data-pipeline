# Backtest Component Static Distribution V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Backtest 계열 React 컴포넌트 12개의 정적 산출물을 Overview와 동일한 `component_static/` 경로로 빌드하고 Git에 포함해 clean checkout에서 별도 npm build 없이 로드한다.

**Architecture:** 각 Vite package는 `frontend/component_static/`을 단일 출력 root로 사용하고, 각 Python wrapper는 그 안의 `index.html` 존재 여부로 component availability를 판정한다. 공통 repository contract test가 12개 package의 config, loader, entry/asset 완전성을 검사하며 기존 UI payload와 이벤트 계약은 유지한다.

**Tech Stack:** Python 3.12, unittest/pytest, Streamlit custom components, React, TypeScript, Vite, npm, Git

## Global Constraints

- 대상은 `app/web/components/*/frontend/package.json`이 존재하는 현재 12개 컴포넌트로 고정한다.
- UI 디자인, payload, event, registry, DB, 계산 로직을 변경하지 않는다.
- canonical 정적 경로는 `frontend/component_static/` 하나만 사용한다.
- loader는 `component_static/index.html`이 존재할 때만 React component를 선언한다.
- `node_modules/`, Vite cache, source map 임시 파일은 Git에 포함하지 않는다.
- qweb 또는 다른 app launcher를 만들지 않는다.

---

### Task 1: 공통 component_static 배포 계약을 테스트로 고정

**Files:**
- Create: `tests/test_component_static_distribution.py`

**Interfaces:**
- Consumes: 저장소의 12개 component directory와 각 `component.py`, `frontend/vite.config.ts`.
- Produces: config/loader 계약과 생성된 entry/assets 완전성을 검사하는 repository test 2개.

- [x] **Step 1: config/loader 계약 실패 테스트 작성**

`BACKTEST_COMPONENT_PACKAGES`에 아래 12개 이름을 명시하고 각 package에 대해 Vite source에 `outDir: "component_static"`, wrapper source에 `/ "component_static"`과 `/ "index.html"`이 있는지 검사한다.

```python
def test_backtest_component_packages_use_component_static_contract() -> None:
    for component_name in BACKTEST_COMPONENT_PACKAGES:
        root = COMPONENT_ROOT / component_name
        vite_source = (root / "frontend/vite.config.ts").read_text(encoding="utf-8")
        wrapper_source = (root / "component.py").read_text(encoding="utf-8")
        assert 'outDir: "component_static"' in vite_source, component_name
        assert '/ "component_static"' in wrapper_source, component_name
        assert '/ "index.html"' in wrapper_source, component_name
        assert '/ "build"' not in wrapper_source, component_name
```

- [x] **Step 2: RED 확인**

Run:

```bash
uv run --with pytest python -m pytest tests/test_component_static_distribution.py::test_backtest_component_packages_use_component_static_contract -q
```

Expected: FAIL. 첫 번째 package의 Vite outDir 또는 wrapper path가 아직 `build`라고 보고한다.

- [x] **Step 3: 생성 산출물 완전성 테스트 작성**

각 `component_static/index.html`을 읽고 상대 `src`/`href` asset을 추출한 뒤 실제 파일 존재를 검사한다. 절대 `/assets/` 참조도 금지한다.

```python
def test_backtest_component_static_entries_reference_existing_assets() -> None:
    for component_name in BACKTEST_COMPONENT_PACKAGES:
        static_root = COMPONENT_ROOT / component_name / "frontend/component_static"
        entry = static_root / "index.html"
        assert entry.is_file(), component_name
        html = entry.read_text(encoding="utf-8")
        assert 'src="/assets/' not in html
        assert 'href="/assets/' not in html
        references = re.findall(r'(?:src|href)="\./([^"?#]+)', html)
        assert references, component_name
        for reference in references:
            assert (static_root / reference).is_file(), f"{component_name}: {reference}"
```

- [x] **Step 4: 테스트 파일 문법 확인**

Run:

```bash
.venv/bin/python -m py_compile tests/test_component_static_distribution.py
```

Expected: exit 0.

- [x] **Step 5: Task 1 커밋**

```bash
git add tests/test_component_static_distribution.py
git commit -m "Backtest 정적 컴포넌트 배포 계약 테스트 추가"
```

---

### Task 2: 12개 loader와 Vite output을 component_static으로 전환

**Files:**
- Modify: `app/web/components/backtest_analysis_decision_workspace/component.py`
- Modify: `app/web/components/backtest_analysis_result_workspace/component.py`
- Modify: `app/web/components/backtest_factor_readiness_panel/component.py`
- Modify: `app/web/components/backtest_handoff_action/component.py`
- Modify: `app/web/components/backtest_policy_signal_board/component.py`
- Modify: `app/web/components/backtest_price_freshness_preflight/component.py`
- Modify: `app/web/components/backtest_price_refresh_action/component.py`
- Modify: `app/web/components/backtest_workflow_shell/component.py`
- Modify: `app/web/components/final_review_investment_report/component.py`
- Modify: `app/web/components/practical_validation_data_action_board/component.py`
- Modify: `app/web/components/practical_validation_decision_workspace/component.py`
- Modify: `app/web/components/practical_validation_fix_queue/component.py`
- Modify: 각 component의 `frontend/vite.config.ts` 12개
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 1의 `BACKTEST_COMPONENT_PACKAGES`와 새 path contract.
- Produces: 모든 component가 `component_static/index.html`을 canonical entry로 읽는 Python/Vite source.

- [x] **Step 1: Vite 설정 변경**

12개 설정의 build block을 아래 계약으로 통일한다.

```ts
build: {
  outDir: "component_static",
  emptyOutDir: true,
},
```

- [x] **Step 2: Python wrapper 변경**

12개 wrapper가 아래 형태를 사용하게 한다. 기존 render 함수와 props는 그대로 둔다.

```python
_FRONTEND_STATIC_DIR = Path(__file__).parent / "frontend" / "component_static"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_STATIC_DIR))
    if (_FRONTEND_STATIC_DIR / "index.html").exists()
    else None
)
```

- [x] **Step 3: GREEN config/loader 계약 확인**

Run:

```bash
uv run --with pytest python -m pytest tests/test_component_static_distribution.py::test_backtest_component_packages_use_component_static_contract -q
```

Expected: `1 passed`.

- [x] **Step 4: 기존 service contract fixture 경로 변경**

`tests/test_service_contracts.py`의 Backtest component build 참조를 모두 `frontend/component_static/index.html`, `frontend/component_static/assets`로 바꾼다. source/UI assertion은 변경하지 않는다.

- [x] **Step 5: Python 문법과 focused source contract 확인**

Run:

```bash
.venv/bin/python -m py_compile app/web/components/*/component.py tests/test_component_static_distribution.py tests/test_service_contracts.py
uv run --with pytest python -m pytest tests/test_service_contracts.py -k "react_component or workflow_shell" -q
```

Expected: compile exit 0, selected tests all pass or only 아직 생성되지 않은 `component_static` entry 때문에 실패.

- [x] **Step 6: Task 2 source 커밋**

```bash
git add app/web/components/*/component.py app/web/components/*/frontend/vite.config.ts tests/test_service_contracts.py
git commit -m "Backtest 컴포넌트 정적 경로 통일"
```

---

### Task 3: 전체 frontend를 빌드하고 정적 산출물을 Git 배포 대상으로 전환

**Files:**
- Delete: 기존 추적 `app/web/components/*/frontend/build/**`
- Create: `app/web/components/*/frontend/component_static/index.html`
- Create: `app/web/components/*/frontend/component_static/assets/*.js`
- Create: `app/web/components/*/frontend/component_static/assets/*.css`

**Interfaces:**
- Consumes: Task 2의 Vite `component_static` output contract.
- Produces: Streamlit이 checkout 직후 읽을 수 있는 12개 완전한 정적 bundle.

- [x] **Step 1: 12개 package clean install/build**

Run:

```bash
for frontend in app/web/components/*/frontend; do
  if test -f "$frontend/package.json"; then
    (cd "$frontend" && npm ci && npm run build)
  fi
done
```

Expected: 12개 package 모두 Vite build exit 0, 각 `component_static/index.html` 생성.

- [x] **Step 2: 산출물 완전성 GREEN 확인**

Run:

```bash
uv run --with pytest python -m pytest tests/test_component_static_distribution.py -q
```

Expected: Git worktree에서 path/asset 계약과 Git tracking 계약 `3 passed`.

- [x] **Step 3: 과거 build 산출물 제거 및 새 산출물 stage**

```bash
git ls-files -z 'app/web/components/*/frontend/build/**' | xargs -0 git rm
git add app/web/components/*/frontend/component_static
```

Expected: 기존 9개 tracked build tree 삭제, 12개 component_static tree 추가. `node_modules`는 stage되지 않는다.

- [x] **Step 4: 전체 focused regression 실행**

Run:

```bash
uv run --with pytest python -m pytest tests/test_component_static_distribution.py -q
uv run --with pytest python -m pytest tests/test_service_contracts.py -k "react_component or workflow_shell" -q
git diff --cached --check
```

Expected: selected tests all pass, diff check exit 0.

- [x] **Step 5: Task 3 산출물 커밋**

```bash
git add app/web/components tests/test_component_static_distribution.py tests/test_service_contracts.py
git commit -m "Backtest React 정적 산출물 Git 배포 전환"
```

---

### Task 4: clean archive, Browser QA, 문서 closeout

**Files:**
- Create: `backtest-component-static-distribution-qa.png` (generated, commit하지 않음)
- Create: task `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: task `STATUS.md`, `PLAN.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md` 또는 관련 architecture doc 중 실제로 stale한 최소 문서
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: Task 3의 committed component_static bundles.
- Produces: clean-checkout 증거, 실제 React 화면 QA, durable packaging decision.

- [x] **Step 1: Git 추적 계약 검사**

Run:

```bash
git ls-files 'app/web/components/*/frontend/component_static/**'
git ls-files 'app/web/components/*/frontend/build/**'
```

Expected: 12개 component의 index/assets만 첫 명령에 나오고 두 번째 명령은 비어 있다.

- [x] **Step 2: clean archive 검증**

현재 HEAD를 임시 디렉터리에 archive하고 12개 entry/assets 완전성 테스트를 저장소 virtual environment로 실행한다.

```bash
archive_dir=$(mktemp -d)
git archive HEAD | tar -x -C "$archive_dir"
(cd "$archive_dir" && uv run --no-project --with pytest python -m pytest \
  tests/test_component_static_distribution.py::test_backtest_component_packages_use_component_static_contract \
  tests/test_component_static_distribution.py::test_backtest_component_static_entries_reference_existing_assets \
  -q)
```

Expected: Git metadata가 필요 없는 clean archive 계약 `2 passed`. 별도 npm build를 실행하지 않는다.

- [x] **Step 3: Streamlit actual Browser QA**

충돌하지 않는 임시 port에서 Streamlit을 재시작하고 Backtest 페이지를 열어 React workflow shell과 Level1 workspace가 표시되는지 확인한다. desktop screenshot을 `backtest-component-static-distribution-qa.png`로 저장한다.

Expected: fallback의 잘린 legacy header가 아니라 React shell과 workspace가 렌더링된다.

- [x] **Step 4: task와 durable docs 동기화**

실행 명령/결과는 `RUNS.md`, 결정은 `NOTES.md`, 잔여 위험은 `RISKS.md`, 전체 3차 완료 상태는 `STATUS.md`에 기록한다. root logs에는 3~5줄 milestone과 “빌드 산출물을 Git으로 배포한다”는 결론만 남긴다.

- [x] **Step 5: closeout 검증과 커밋**

Run:

```bash
git diff --check
git status --short
uv run --with pytest python -m pytest tests/test_component_static_distribution.py -q
```

Expected: 테스트 통과, QA PNG 외 예상하지 않은 generated artifact 없음.

```bash
git add .aiworkspace/note/finance
git commit -m "Backtest 정적 컴포넌트 배포 전환 문서화"
```
