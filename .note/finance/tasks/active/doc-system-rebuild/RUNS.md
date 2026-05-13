# RUNS - Finance Documentation System Rebuild

Status: Active
Last Updated: 2026-05-12

## 2026-05-12 - Inventory

Command:

```bash
find .note/finance -maxdepth 2 -type f | sort
```

Result:

- 기존 root docs, `docs/architecture` / `docs/flows`, `docs/data`, `operations`, `research`, `support_tracks`, `phases`, `registries`, `saved`, `run_history` 확인
- `registries/`와 `saved/`는 보존 대상으로 확인

## 2026-05-12 - Skeleton Creation

Command:

```bash
mkdir -p .note/finance/docs/architecture .note/finance/docs/flows .note/finance/docs/data .note/finance/docs/runbooks .note/finance/phases/active .note/finance/phases/done .note/finance/tasks/active/practical-validation-v2 .note/finance/tasks/done .note/finance/agent
```

Result:

- 새 docs / phases / tasks / agent skeleton 생성
- 기존 문서 삭제 없음

## 2026-05-12 - First Work Verification

Command:

```bash
find .note/finance -maxdepth 3 -type d | sort
find .note/finance -maxdepth 3 -type f | sort
git status --short
git diff --stat
```

Result:

- 새 `docs/`, `phases/active`, `phases/done`, `tasks/active`, `tasks/done`, `agent` 파일 생성 확인
- `registries/`와 `saved/` 파일 목록 유지 확인
- `git diff --check` 통과
- 기존 dirty artifact는 그대로 남아 있으며 stage 대상에서 제외 예정

## 2026-05-12 - AGENTS Rewrite

Command:

```bash
sed -n '1,260p' AGENTS.md
sed -n '1,220p' .note/finance/docs/INDEX.md
sed -n '1,220p' .note/finance/docs/PROJECT_MAP.md
```

Result:

- 기존 `AGENTS.md`의 핵심 운영 규칙을 새 `.note/finance/docs/` read order 기준으로 축약
- legacy `.note/finance/code_analysis/`는 `.note/finance/docs/architecture/`, `.note/finance/docs/flows/`, `.note/finance/docs/runbooks/`, active Practical Validation task 문서로 흡수 완료
- legacy `.note/finance/data_architecture/`는 `.note/finance/docs/data/`로 흡수 완료
- registry / saved 보존, generated artifact 커밋 금지, UX/workflow 승인 규칙 유지

## 2026-05-12 - Backtest Reports 1차 Migration

Command:

```bash
git mv .note/finance/backtest_reports/README.md .note/finance/reports/backtests/README.md
git mv .note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md .note/finance/reports/backtests/INDEX.md
git mv .note/finance/backtest_reports/strategies .note/finance/reports/backtests/strategies
git mv .note/finance/backtest_reports/phase* .note/finance/reports/backtests/archive/legacy_phase/
```

Result:

- 기존 83개 backtest report 파일을 삭제하지 않고 새 `.note/finance/reports/backtests/` 아래로 이동
- `strategies/`는 active strategy hub/log 영역으로 유지
- 기존 phase13~phase24 report는 `archive/legacy_phase/`에 임시 보관
- 새 `README.md`, `INDEX.md`, `TEMPLATE.md`, `LEGACY_MIGRATION.md`로 report 운영 기준 작성
- legacy report의 세부 재분류와 삭제 판단은 후속 단계로 분리

## 2026-05-12 - Backtest Reports 2차 Validation Classification

Command:

```bash
git mv .note/finance/reports/backtests/archive/legacy_phase/phase23/PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md .note/finance/reports/backtests/validation/runtime/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md .note/finance/reports/backtests/validation/runtime/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md .note/finance/reports/backtests/validation/ui_replay/
```

Result:

- `phase23` quarterly contract smoke validation report를 runtime validation으로 이동
- `phase24` Global Relative Strength core runtime smoke report를 runtime validation으로 이동
- `phase24` Global Relative Strength UI replay smoke report를 UI replay validation으로 이동
- `phase23`, `phase24` archive README는 색인 역할만 하던 문서라 제거하고 `validation/README.md`에 핵심 설명을 반영
- 남은 legacy archive는 `phase13`~`phase22`

## 2026-05-12 - Backtest Reports 3차 Legacy Archive Cleanup

Command:

```bash
git mv .note/finance/reports/backtests/archive/legacy_phase/phase13/*.md .note/finance/reports/backtests/runs/2026/strategy_search/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase14/*.md .note/finance/reports/backtests/runs/2026/strategy_search/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase15/*.md .note/finance/reports/backtests/runs/2026/strategy_search/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase16/*.md .note/finance/reports/backtests/runs/2026/strategy_search/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase17/*.md .note/finance/reports/backtests/runs/2026/strategy_search/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase18/*.md .note/finance/reports/backtests/runs/2026/strategy_search/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md .note/finance/reports/backtests/validation/runtime/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase21/*ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md .note/finance/reports/backtests/candidates/point_in_time/strategy_candidates/
git mv .note/finance/reports/backtests/archive/legacy_phase/phase22/PHASE22_*.md .note/finance/reports/backtests/candidates/point_in_time/portfolio_candidates/
```

Result:

- phase13~phase18 원본성 전략 탐색 report 38개를 `runs/2026/strategy_search/`로 이동
- phase21 portfolio bridge validation report를 `validation/runtime/`으로 이동
- phase21 strategy anchor / alternative rerun report 3개를 `candidates/point_in_time/strategy_candidates/`로 이동
- phase22 portfolio baseline / weight alternative report 2개를 `candidates/point_in_time/portfolio_candidates/`로 이동
- phase별 README와 빈 archive 폴더 제거
- `.note/finance/reports/backtests/archive/legacy_phase/` 제거 완료

## 2026-05-13 - Code Analysis Migration

Result:

- 기존 `.note/finance/code_analysis/` current-state 문서를 `.note/finance/docs/architecture/`, `.note/finance/docs/flows/`, `.note/finance/docs/runbooks/`로 이동
- Practical Validation V2 상세 계획 문서를 `.note/finance/tasks/active/practical-validation-v2/`로 이동
- Portfolio Selection redesign guide는 현재 구현 기준의 `docs/flows/PORTFOLIO_SELECTION_FLOW.md`로 재작성
- legacy refinement guide는 `docs/architecture/BACKTEST_RUNTIME_FLOW.md`에 핵심 해석만 흡수
- 기존 `.note/finance/code_analysis/` 폴더 제거

## 2026-05-13 - Reference / Glossary App Path Check

Command:

```bash
rg -n "Path|read_text|open\(|\.md|REFERENCE|DOCUMENT|render_reference|st\.markdown" app/web/reference_guides.py
rg -n "read_text|open\(|Path\(" app/web | sort
```

Result:

- `Reference > Guides`는 md 본문을 읽지 않고 `app/web/reference_guides.py` 안의 guide text와 문서 경로 목록을 렌더링하는 구조로 확인
- `Reference > Glossary`는 `GLOSSARY_DOC_PATH.read_text()`로 glossary md를 실제 읽는 구조로 확인
- 삭제 전 안전장치로 `Guides` 문서 경로 목록을 새 `.note/finance/docs/` 기준으로 전환
- 기존 root glossary 본문을 `.note/finance/docs/GLOSSARY.md`로 승격하고, `Reference > Glossary` 읽기 경로를 새 문서로 전환

## 2026-05-13 - Legacy Root / Operations / Research / Support Absorption

Command:

```bash
find .note/finance -maxdepth 2 -type f | sort
rg -n "practical_validation_stress_windows_v1|operations/|support_tracks/|FINANCE_COMPREHENSIVE_ANALYSIS|MASTER_PHASE_ROADMAP|FINANCE_DOC_INDEX|FINANCE_TERM_GLOSSARY" app finance .note/finance/docs .note/finance/tasks README.md
```

Result:

- root current-state docs는 `docs/INDEX.md`, `docs/PROJECT_MAP.md`, `docs/ROADMAP.md`, `docs/GLOSSARY.md`로 대체 가능한 것으로 분류
- operations registry guides는 `.note/finance/registries/README.md`에 current V2 / legacy compatibility 기준으로 흡수
- runtime artifact, external research, config externalization 원칙은 `docs/runbooks/README.md`에 축약
- `research/practical_validation_stress_windows_v1.json`은 런타임 reference data로 확인되어 `docs/data/practical_validation_stress_windows_v1.json`로 이동하고 코드 경로를 갱신
- Practical Validation investment diagnostics research는 active task `DESIGN.md`에 흡수된 기준으로 정리하고 legacy research doc 참조를 제거
- support track 문서는 `AGENTS.md`, runbook, agent gotchas / lessons로 핵심 운영 원칙만 흡수하고 상세 과거 plan은 3차 삭제 후보로 분류

Verification:

```bash
.venv/bin/python -m py_compile app/web/backtest_practical_validation_helpers.py app/web/reference_guides.py app/web/streamlit_app.py
.venv/bin/python - <<'PY'
from app.web.backtest_practical_validation_helpers import _load_static_stress_windows
windows = _load_static_stress_windows()
print(len(windows))
print(windows[0].get("id"))
PY
git diff --check
python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

Result:

- compile 통과
- stress window loader가 새 위치에서 14개 window를 읽고 첫 id `dotcom_bust_2000_2002`를 반환
- `git diff --check` 통과
- hygiene helper 통과. run history / `.DS_Store` / `.playwright-mcp/`는 generated artifact로 unstaged 유지

## 2026-05-13 - Legacy Tree Removal

Command:

```bash
git rm -r \
  .note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md \
  .note/finance/FINANCE_DOC_INDEX.md \
  .note/finance/FINANCE_TERM_GLOSSARY.md \
  .note/finance/MASTER_PHASE_ROADMAP.md \
  .note/finance/archive \
  .note/finance/operations \
  .note/finance/research \
  .note/finance/support_tracks
git mv .note/finance/PHASE_PLAN_TEMPLATE.md .note/finance/docs/runbooks/templates/PHASE_PLAN_TEMPLATE.md
git mv .note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md .note/finance/docs/runbooks/templates/PHASE_TEST_CHECKLIST_TEMPLATE.md
git rm -r .note/finance/phases/phase[0-9]*
```

Result:

- 새 docs 구조로 대체된 root current-state docs 제거
- 2차에서 흡수 완료한 `archive/`, `operations/`, `research/`, `support_tracks/` 제거
- phase bootstrap templates는 삭제하지 않고 `docs/runbooks/templates/`로 이동
- `plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py`가 새 template 경로를 읽도록 갱신
- registry helper와 related skill reference에 남은 old `backtest_reports/strategies` 경로를 새 `reports/backtests/strategies` 경로로 보정
- legacy `phases/phase1` ~ `phases/phase36` 상세 문서 제거
- phase helper 생성 위치를 `.note/finance/phases/active/phase<N>/`로 갱신
- `AGENTS.md`의 migration 중 legacy reference 문구를 제거 완료

Verification:

```bash
.venv/bin/python -m py_compile app/web/backtest_practical_validation_helpers.py app/web/reference_guides.py app/web/streamlit_app.py plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py
python3 plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase 999 --title "Template Path Smoke" --dry-run
.venv/bin/python - <<'PY'
from app.web.backtest_practical_validation_helpers import _load_static_stress_windows
windows = _load_static_stress_windows()
print(len(windows))
print(windows[0].get("id"))
PY
find .note/finance -maxdepth 2 -type d | sort
rg -n "\.note/finance/phases/phase[0-9]|\.note/finance/backtest_reports|FINANCE_DOC_INDEX|FINANCE_COMPREHENSIVE_ANALYSIS|MASTER_PHASE_ROADMAP|FINANCE_TERM_GLOSSARY|\.note/finance/operations|\.note/finance/research|\.note/finance/support_tracks|\.note/finance/archive" README.md AGENTS.md app finance plugins .note/finance/docs .note/finance/agent .note/finance/tasks/active/practical-validation-v2 .note/finance/phases/README.md
git diff --check
python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

Result:

- compile 통과
- phase bootstrap dry-run이 `.note/finance/phases/active/phase999/` 아래 output path를 반환
- stress window loader가 14개 window를 새 `docs/data/` 위치에서 정상 로드
- `.note/finance` 2-depth 구조에서 legacy `archive/`, `operations/`, `research/`, `support_tracks/`, numbered phase dirs 제거 확인
- active app / docs / helper 영역에서 old root docs, old operations / research / support path, old backtest report path 참조 없음
- `git diff --check` 통과
- hygiene helper 통과. 삭제된 legacy docs는 `other_docs`로 분류되고 root logs는 갱신됨
