# Today Contributor Performance Cards V1 Runs

## 2026-07-22 Design Investigation And TDD Handoff

- `app/services/today.py` contributor selection과 `{symbol, value, tone}` projection을 확인했다.
- `app/services/portfolio_monitoring/read_model.py` item row와 lane `flow_adjusted_index` 계약을 확인했다.
- actual default group은 active 5개이며 Today는 top positive 2 / bottom negative 2를 표시한다.
- Tasks 1–3 산출물은 flow-adjusted item return, Today projection/sorting, React/fallback card contract의 regression tests와 `aa1ed843d`, `4dfa735d3`, `4e4be633f`, `185885f33` 구현 커밋을 포함한다. Task 4는 구현을 임의로 되돌려 RED를 재현하지 않고 아래 전체 GREEN 회귀를 fresh 실행했다.

## 2026-07-22 Fresh Closeout Regression

```bash
.venv/bin/python -m pytest \
  tests/test_today_home.py \
  tests/test_portfolio_monitoring_read_model.py \
  tests/test_portfolio_monitoring_page.py \
  -q
```

- Result: `64 passed, 3 warnings, 2 subtests passed in 1.50s`.
- Warnings: installed `edgar` package의 기존 deprecation warning 3건이며 task failure/error는 없다.

```bash
.venv/bin/python -m py_compile \
  app/services/portfolio_monitoring/read_model.py \
  app/services/today.py \
  app/web/today_page.py
git diff --check
```

- Result: exit 0, output 없음.

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --run
npm run typecheck
npm run build
```

- Result: Vitest `1 file / 5 tests passed`; TypeScript exit 0; Vite `172 modules transformed`, production build exit 0.

## 2026-07-22 Browser QA

```bash
.venv/bin/streamlit run app/web/streamlit_app.py \
  --server.port 8517 \
  --server.headless true
```

- URL: `http://localhost:8517/`
- 1280: title/scope/footer와 네 카드의 symbol/return/contribution 확인, contributor card 2열, contributor/우선 확인 outer 2열, document/body horizontal overflow 0, clipped value 0.
- 760: contributor card 2열 유지, contributor section과 `우선 확인` 세로 적층, horizontal overflow 0, clipped value 0.
- 420: contributor card 1열, outer section 세로 적층, horizontal overflow 0, clipped value 0.
- Browser console error: 0건.
- Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/today-contributor-performance-cards-v1-browser-qa.png` (760 representative viewport, generated/untracked).

## 2026-07-22 Scope Review

- `git status --short`, `git diff --stat`, 지정 구현 파일 `git diff`를 fresh 확인했다.
- task commit range에는 Today service/read model/page/component/tests/task docs만 포함되며 DB·ingestion·provider·registry·saved·run-history·Portfolio Monitoring page UI는 포함되지 않는다.
- 기존 registry 수정, saved/run-history JSONL, `.superpowers/`, 기존 QA 이미지와 이번 screenshot은 unstaged로 보존한다.
