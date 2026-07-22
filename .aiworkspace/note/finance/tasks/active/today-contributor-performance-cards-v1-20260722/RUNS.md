# Today Contributor Performance Cards V1 Runs

## 2026-07-22 Design Investigation And TDD Handoff

- `app/services/today.py` contributor selection과 `{symbol, value, tone}` projection을 확인했다.
- `app/services/portfolio_monitoring/read_model.py` item row와 lane `flow_adjusted_index` 계약을 확인했다.
- actual default group은 active 5개이며 Today는 top positive 2 / bottom negative 2를 표시한다.
- Tasks 1–3 산출물은 flow-adjusted item return, Today projection/sorting, React/fallback card contract의 regression tests와 `aa1ed843d`, `4dfa735d3`, `4e4be633f`, `185885f33` 구현 커밋을 포함한다. Task 4는 구현을 임의로 되돌려 RED를 재현하지 않고 아래 전체 GREEN 회귀를 fresh 실행했다.

## 2026-07-22 Initial Closeout Regression

아래 결과는 최종 리뷰 전 최초 closeout 기록이다. exact-basis-date와 signed currency 보정 후의 최종 검증은 문서 하단의 `Final Review Correction`을 canonical closeout으로 본다.

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

## 2026-07-22 Final Review Correction

### Root Cause

- `_lane_total_return`이 날짜 인자 없이 전체 lane의 `flow_adjusted_index`에서 마지막 non-null을 골라 group 공통 `basis_date` 이후 값 또는 trailing-null 이전 값을 공통 기준일 return처럼 노출했다.
- 같은 helper를 사용한 `_project_selected_position`도 `latest_usable_date` row가 null일 때 이전 값을 재사용해 기존 exact-latest 의미를 깨뜨렸다.
- React는 일반 currency formatter를 contribution에도 사용해 양수 `+`가 없었고, Python fallback은 음수를 `$-401`로 표시했다.

### RED — Group Basis Date

```bash
.venv/bin/python -m pytest \
  tests/test_portfolio_monitoring_read_model.py::PortfolioMonitoringReadModelTests::test_item_rows_require_valid_flow_adjusted_index_on_group_basis_date \
  tests/test_portfolio_monitoring_read_model.py::PortfolioMonitoringReadModelTests::test_item_rows_do_not_use_observation_after_group_basis_date \
  -q
```

- Result: `2 failed, 3 warnings in 0.92s`.
- Exact failures: trailing-null basis row가 기대 `None` 대신 이전 값 `Decimal('-0.0008')`을 반환했고, group basis `2026-07-02` item이 기대 `Decimal('-0.0008')` 대신 미래 `2026-07-03` 값 `Decimal('-0.00154')`을 반환했다.

### RED — Selected Position Exact Latest

```bash
.venv/bin/python -m pytest \
  tests/test_portfolio_monitoring_read_model.py::PortfolioMonitoringReadModelTests::test_workspace_projects_only_selected_eligible_position \
  tests/test_portfolio_monitoring_read_model.py::PortfolioMonitoringReadModelTests::test_selected_position_requires_valid_index_on_its_latest_usable_date \
  -q
```

- Result: `1 failed, 1 passed, 3 warnings in 0.91s`.
- Valid-latest control은 `Decimal('-0.00154')`로 통과했고, trailing-null latest는 기대 `None` 대신 이전 값 `Decimal('-0.0008')`을 반환해 실패했다.

### RED — Signed Contribution

```bash
.venv/bin/python -m pytest \
  tests/test_today_home.py::TodayHomePageContractTests::test_today_page_reuses_overview_visual_tokens_and_read_only_loaders \
  tests/test_today_home.py::TodayHomePageContractTests::test_today_fallback_labels_missing_item_return_without_hiding_contribution \
  -q
```

- Result: `2 failed, 3 warnings in 1.51s`.
- React source는 `signedMoneyText(row.contribution_value)`를 사용하지 않았고 fallback HTML은 `+$11,915` 대신 `$11,915`, `-$401` 대신 `$-401`을 만들었다.

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --run
```

- Result: `1 failed, 5 passed`; 새 formatter가 없어 기대 `+$11,915`에 `undefined`가 반환됐다.

### Focused GREEN

- Group basis-date command: `2 passed, 3 warnings in 0.85s`.
- Selected-position command: `2 passed, 3 warnings in 0.84s`.
- Python signed-contribution command: `2 passed, 3 warnings in 1.49s`.
- React signed-contribution command: `1 file / 6 tests passed`.

### Final Fresh Regression And Build

```bash
.venv/bin/python -m pytest \
  tests/test_today_home.py \
  tests/test_portfolio_monitoring_read_model.py \
  tests/test_portfolio_monitoring_page.py \
  -q
```

- Result: `66 passed, 3 warnings, 2 subtests passed in 1.54s`.
- Warnings: installed `edgar` package의 기존 deprecation warning 3건이며 failure/error는 없다.

```bash
.venv/bin/python -m py_compile \
  app/services/portfolio_monitoring/read_model.py \
  app/services/today.py \
  app/web/today_page.py
git diff --check
```

- Result: 두 명령 모두 exit 0, output 없음.

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --run
npm run typecheck
npm run build
```

- Result: Vitest `1 file / 6 tests passed`; TypeScript exit 0; Vite `172 modules transformed`, production build exit 0.
- Build output: `index-BJTTBc_q.css` 11.05 kB, `index-VtxTQrZc.js` 337.98 kB, build `450ms`.

### Final Actual Browser QA

```bash
.venv/bin/streamlit run app/web/streamlit_app.py \
  --server.port 8517 \
  --server.headless true
```

- URL: `http://localhost:8517/`.
- Browser viewport capability requested `1280 / 760 / 420`; current Chrome 110% zoom에서 CSS inner width는 `1163 / 691 / 382`, component iframe width는 `994 / 649 / 340`으로 관측됐다.
- 1280: contributor card 2열, contributor/review outer 2열, top/component horizontal overflow 0, 네 contribution value clipping/scroll overflow 0.
- 760: contributor card 2열, contributor/review outer 1열 stack, top/component horizontal overflow 0, 네 contribution value clipping/scroll overflow 0.
- 420: contributor card 1열, outer 1열 stack, top/component horizontal overflow 0, 네 contribution value clipping/scroll overflow 0.
- 모든 viewport: `+$11,915`, `+$4,319`, `-$401`, `-$282`와 exact footer `종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 2026-07-21` 확인.
- Browser console error: `0`.
- Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/today-contributor-performance-cards-v1-browser-qa.png` (760 representative, 40,209 bytes, generated/untracked).

### Final Scope Review

- Code/test/bundle commit: `e96756526` (`수정: Today 성과 기여 기준일과 부호 정정`).
- 변경은 read-model exact-date helper/call sites, Today contribution formatter, React helper/source/test, focused Python tests, tracked `component_static`에 한정했다.
- group contribution, group curve, DB, ingestion, provider, position-event calculation, Portfolio Monitoring page UI, registry, saved portfolio, run-history는 변경하지 않았다.
- 기존 `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`, `.superpowers/`, QA screenshot은 stage하지 않았다.
