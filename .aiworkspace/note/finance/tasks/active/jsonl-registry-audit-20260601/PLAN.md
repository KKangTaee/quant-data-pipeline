# JSONL Registry Audit 2026-06-01

Status: Dry-run complete

## Goal

DB를 건드리지 않고 `.aiworkspace/note/finance/**/*.jsonl`을 전수 파싱해 최신 Portfolio Selection / Selected Dashboard 흐름 기준으로 keep / migrate / archive / delete 후보를 분류한다.

## 이걸 하는 이유?

현재 registry에는 V1, V2, legacy compatibility, saved setup, local run history가 섞여 있다. 바로 삭제하거나 재작성하면 GRS 4개 selected decision의 Dashboard 노출이나 saved setup을 깨뜨릴 수 있으므로, 먼저 read-only inventory와 정리안을 확정한다.

## Scope

- 포함: `.aiworkspace/note/finance/**/*.jsonl`
- 제외: DB, provider/raw data, broker/account/order/live approval/auto rebalance
- 승인 전 금지: archive/delete/rewrite
- 승인 전 허용: read-only parse, code consumer scan, integrity/read-model check, dry-run report 작성

## Stop Condition

- 모든 JSONL parse 결과와 code consumer를 문서화한다.
- row/file별 dry-run classification을 작성한다.
- GRS 4개 selected decision과 Selected Dashboard assignment 유지 여부를 검증한다.
- 승인 전에는 JSONL 파일을 변경하지 않는다.
