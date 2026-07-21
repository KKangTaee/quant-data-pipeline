# Portfolio Monitoring Migration And QA

Status: Active
Last Verified: 2026-07-21

## 언제 쓰는가

Portfolio Monitoring schema를 처음 배포하거나, default group·legacy dry-run·React Browser QA·rollback 준비 상태를 검증할 때 사용한다. 운영 그룹/종목을 임의 생성하는 절차가 아니다.

## 1. 사전 확인

```bash
git status --short
git diff --check
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring*.py'
```

- `finance_meta` 접속 설정과 기존 `monitoring_%` table 목록을 read-only로 확인한다.
- `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`의 legacy bytes와 SHA-256 checksum을 기록한다.
- registry/saved JSONL과 QA PNG가 stage되지 않았는지 확인한다.

## 2. 격리 schema 검증

먼저 `finance_meta_portfolio_monitoring_qa_YYYYMMDD` 같은 별도 QA database에 `PORTFOLIO_MONITORING_SCHEMAS`의 여섯 DDL을 적용한다. table/index/enum/JSON column을 확인한 뒤 동일 DDL을 다시 실행해 idempotency를 확인한다. QA database는 실제 사용자 group/item을 포함하지 않는다.

## 3. 운영 schema 적용

1. 운영 `finance_meta`의 table 목록을 다시 기록한다.
2. `MySQLMonitoringRepository.ensure_schema()`로 `CREATE TABLE IF NOT EXISTS` 여섯 개와 position-event optional column upgrade를 적용한다. 기존 table에는 `requested_start_date DATE NULL`, `effective_start_date DATE NULL`만 누락 시 각각 한 번 추가한다. 적용 전후 `monitoring_portfolio_group`, `monitoring_portfolio_item`, `monitoring_portfolio_command`, `monitoring_security_position_event` row count가 같아야 한다.
3. table/index/column을 read-only로 검증한다.
   - `uk_monitoring_calibration_fingerprint` 순서는 `algorithm_version, data_fingerprint, config_fingerprint, policy_version, horizon_sessions`여야 한다.
   - 두 optional date column이 nullable `DATE`인지 확인하고 `ensure_schema()`를 다시 호출했을 때 추가 `ALTER`가 없는지 확인한다.
   - 신규 배포 직후 event row가 없는 환경에서는 `monitoring_security_position_event` row count가 0으로 유지되어야 한다. 사용자 거래 interaction QA는 운영 DB가 아니라 격리 fixture에서 수행한다.
4. `ensure_default_group(repository)`를 두 번 호출하고 active default group이 정확히 하나인지 확인한다.

`ensure_schema`와 default group 생성은 column drop, table rename, 기존 row update를 하지 않는다. 실패 시 더 진행하지 않고 error와 적용된 table 목록을 기록한다.

## 4. Legacy dry-run

`build_legacy_import_plan`을 actual legacy source와 현재 Final Review candidate set에 실행한다. create/skip/block count와 source fingerprint를 확인하되, 사용자 승인 없는 운영 apply는 하지 않는다. dry-run 전후 checksum이 같아야 한다. apply가 필요하면 QA repository에서 먼저 두 번 실행해 두 번째 결과가 no-op인지 확인하고 provenance를 검산한다.

## 5. Rollback

- app rollback: 이전 코드 revision으로 되돌리되 새 table은 즉시 삭제하지 않는다. 이전 화면은 새 table을 읽지 않는다.
- data rollback: migration 전 DB backup/export가 있고 정확한 table target이 확인된 경우에만 DBA 승인 아래 explicit table 단위로 수행한다.
- legacy rollback은 불필요하다. 원본은 읽기 전용이며 checksum이 바뀌면 배포를 중단한다.
- broad database drop, workspace 삭제, registry/saved JSONL 재작성은 금지한다.

## 6. Browser QA

`Operations > Portfolio Monitoring`을 1440, 760, 420 px 너비에서 확인한다.

- default group 하나가 보이고 그룹 추가/이름 변경/선택 진입점이 명확하다.
- Context Drawer에 direct stock/ETF와 selected strategy가 분리되고 수량 방식은 정수만 받는다.
- 빈 그룹은 데이터 부족 경고를 만들지 않고 종목 추가 행동을 안내한다.
- 종목 fixture 검증에서는 invested/current/return/MDD/CAGR, 공통 curve, 개별 lane이 일치한다.
- direct-stock fixed-shares fixture에서는 현재/최초 수량, 누적 입금·출금, `최초 설정 정정`, 추가매수·일부매도, 거래 수정·취소가 보인다. 정정 창의 새 추적 시작일·새 최초 수량과 요청일/적용일/시작 종가/최초 투자금 변경 전·후를 확인한다. 주말 요청일은 다음 stored market date로 적용되고 저장 뒤 같은 종목을 유지한 채 개별/그룹 결과가 갱신되어야 한다.
- 거래일 exact DB close 기본값과 manual override label, partial sell 최소 1주 validation을 확인한다. 정정 적용일보다 이른 기존 거래와 새 최초 수량을 초과하는 매도는 저장이 차단되어야 한다.
- ETF, selected strategy와 fixed-notional item에는 position trade action이 없어야 한다.
- `지금 확인할 변화`, `강점`, `취약점`, `데이터 부족`, `현재 매크로 관찰`, `위험 검증과 진단 이력`을 확인한다.
- calibration이 현재 fingerprint의 `READY`가 아니면 확률이 숨겨지고 관찰 전용 설명이 보인다.
- horizontal overflow와 Streamlit component error가 없어야 한다.

Browser QA screenshot은 task RUNS에 절대경로를 남기되 generated artifact로 보고 unstaged 상태를 유지한다.

거래 interaction QA는 temporary Streamlit harness에서 수행한다. harness는 production MySQL과 registry/saved JSONL을 읽거나 쓰지 않고 `portfolio_monitoring_workspace_v2` fixture와 component event만 주고받는다.

## 7. Closeout

```bash
git diff --check
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
git status --short
```

실행 결과, actual macro coverage, 미실행 검증과 남은 `SUPPRESSED/LIMITED` 이유를 task `RUNS.md`와 `RISKS.md`에 기록한다.
