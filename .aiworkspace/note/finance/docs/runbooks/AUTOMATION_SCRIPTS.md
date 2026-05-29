# Automation Scripts Guide

## 목적

이 문서는 finance 작업을 돕는 repo-local helper script와 persistence helper의 역할을 정리한다.
새 script를 만들거나 기존 script 사용 기준을 바꿀 때 갱신한다.

## 현재 핵심 script

| Script | 역할 |
|---|---|
| `.aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py` | 새 phase 문서 bundle 생성 |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | phase / docs / logs / generated artifact hygiene 점검 |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | `app/services` / `app/runtime` Streamlit-free boundary, `app.web` import 금지, staged artifact guard 점검 |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py` | current candidate registry list / show / validate / append |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py` | pre-live candidate registry template / draft-from-current / list / show / validate / append |
| `app/jobs/overview_automation.py` | 브라우저 없이 Overview Market Intelligence 수집 job을 cadence / market-hours / lock 기준으로 실행하는 run-once CLI |

## Phase bundle bootstrap

사용 시점:

- 새 finance phase를 열 때
- plan, TODO, completion summary, next-phase preparation, test checklist의 기본 골격이 필요할 때

역할:

- phase plan
- current chapter TODO
- completion summary draft
- next phase preparation draft
- test checklist draft

를 한 번에 만든다.

생성 위치:

- `.aiworkspace/note/finance/phases/active/phase<N>/`

Template source:

- `.aiworkspace/note/finance/docs/runbooks/templates/PHASE_PLAN_TEMPLATE.md`
- `.aiworkspace/note/finance/docs/runbooks/templates/PHASE_TEST_CHECKLIST_TEMPLATE.md`

주의:

- 생성 후에는 반드시 사용자-facing 설명으로 다시 다듬는다.
- phase plan에는 기존의 분리형 요약 / 완료 효과 섹션을 강제하지 않는다.
- 대신 `이걸 하는 이유?` 섹션에서 문제 / 지금 필요한 이유 / 끝났을 때의 구체적 가치를 쉽게 설명한다.
- checklist는 용어 정리보다 실제 확인 위치와 확인 행동을 우선한다.

## Refinement hygiene helper

사용 시점:

- 의미 있는 finance refinement / 문서 sync 이후
- phase closeout 전
- commit 전 문서 누락을 빠르게 확인하고 싶을 때

역할:

- changed path 분류
- phase docs 변경 여부 확인
- root logs 확인
- generated artifact unstaged 여부 확인
- registry / index / report 관련 누락 가능성 확인

주의:

- support tool이지 절대 blocker는 아니다.
- generated JSONL은 보통 commit하지 않는다.
- script output이 broad하게 권고해도 실제 diff 성격에 맞게 판단한다.

## UI / engine boundary helper

사용 시점:

- `app/services`를 추가하거나 수정한 뒤
- UI-engine boundary phase / task closeout 전
- commit 전 service가 Streamlit UI 책임을 다시 들고 오지 않았는지 확인할 때

대표 명령:

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py --json
```

Hard fail:

- `app/services/*.py`, `app/runtime/*.py`의 `streamlit` import
- `app/services/*.py`, `app/runtime/*.py`의 `st.*` 접근
- `app/services/*.py`, `app/runtime/*.py`의 `app.web.*` import
- staged generated / registry / saved / run-history / local artifact

기준:

- `app/web`은 Streamlit 화면, form, session state, user feedback을 맡는다.
- `app/services`와 `app/runtime`은 Streamlit-free layer이므로 UI helper를 역참조하지 않는다.

## Current candidate registry helper

사용 시점:

- current strongest candidate나 near-miss 후보를 machine-readable하게 확인할 때
- registry JSONL 형식이 깨지지 않았는지 확인할 때
- current candidate summary와 registry를 맞춰 볼 때

대표 명령:

```bash
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate
```

## Pre-Live candidate registry helper

사용 시점:

- Real-Money 검증 신호 이후 후보를 watchlist / paper tracking / hold / reject / re-review로 기록할 때
- `.aiworkspace/note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` 형식이 깨지지 않았는지 확인할 때
- current candidate와 pre-live 운영 상태를 분리해서 관리할 때

대표 명령:

```bash
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py template
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current value_current_anchor_top14_psr
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py list
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate
```

역할 분리:

- `manage_current_candidate_registry.py`는 후보 자체의 기준점을 관리한다.
- `manage_pre_live_candidate_registry.py`는 그 후보를 실전 전 어떻게 관찰하거나 보류할지 관리한다.
- `draft-from-current`는 current candidate를 Pre-Live 기록 초안으로 바꾼다.
  기본값은 출력만 하며, `--append`를 붙일 때만 실제 registry에 저장한다.

## Overview scheduled refresh helper

사용 시점:

- Streamlit 브라우저를 켜지 않고 Overview Market Movers / Events 데이터를 주기적으로 갱신할 때
- cron, macOS launchd, Codex automation 같은 외부 scheduler가 5분 단위로 호출할 run-once entry point가 필요할 때
- 실제 provider 호출 없이 어떤 job이 due인지 먼저 확인하고 싶을 때

대표 명령:

```bash
uv run python -m app.jobs.overview_automation --profile standard --dry-run
uv run python -m app.jobs.overview_automation --profile standard
uv run python -m app.jobs.overview_automation --profile safe
uv run python -m app.jobs.overview_automation --profile events
```

운영 기준:

- `standard`는 S&P 500 / Top1000 / Top2000 intraday snapshot과 S&P 500 universe, FOMC, macro, earnings refresh를 평가한다.
- `safe`는 Top1000 / Top2000 intraday snapshot을 제외해 무료 provider 압력을 낮춘다.
- `events`는 FOMC / macro / earnings calendar만 평가한다.
- Intraday snapshot은 기본적으로 미국 정규장 시간에만 실행된다.
- 실행 결과는 각 ingestion job result로 `.aiworkspace/note/finance/run_history/WEB_APP_RUN_HISTORY.jsonl`에 남고, Data Health가 그 기록을 읽는다.

## 새 script를 추가할 때 기록 기준

새 helper script가 아래 중 하나에 해당하면 이 문서를 갱신한다.

- phase 운영을 자동화한다.
- candidate registry나 saved portfolio 같은 durable persistence를 읽거나 쓴다.
- backtest report, index, hygiene, generated artifact 관리에 영향을 준다.
- future agent가 반복적으로 호출해야 하는 workflow helper다.

일회성 실험 script나 local scratch script는 이 문서에 올리지 않는다.

## 관련 문서

- [Finance Registries](../../registries/README.md)
- [Runbook README](./README.md)
- [BACKTEST_RUNTIME_FLOW.md](../architecture/BACKTEST_RUNTIME_FLOW.md)
- [Finance Documentation Index](../INDEX.md)
