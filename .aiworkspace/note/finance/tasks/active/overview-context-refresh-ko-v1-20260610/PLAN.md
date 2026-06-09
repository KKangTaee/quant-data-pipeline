# Overview Context Refresh / Korean Copy V1 Plan

## Why

Overview 상단 cockpit이 market context 상태를 잘 보여주지만 핵심 안내가 영어 중심이라 빠르게 이해하기 어렵고, stale / due 상태를 발견해도 cockpit 범위 데이터를 한 번에 수동 갱신하는入口가 없다.

## Scope

- 1차: `Market context needs review`, `Overview Map`, 다음 deep tab 안내를 한국어 중심 copy로 정리한다.
- 1차: 기존 `app/jobs/overview_actions.py` boundary 안에서 Overview market context 수동 일괄 갱신 버튼을 추가한다.
- 1차 제외: 새 provider, DB schema, registry / saved JSONL write, unattended scheduler, action queue persistence, validation / monitoring / trading semantics.

## Tentative Follow-Up

- 2차: 일괄 갱신 결과를 source별 retry / partial failure UX로 정교화한다.
- 3차: 운영 시간 / cadence 기반 scheduler hardening을 별도 승인 후 검토한다.
- 4차: runbook / Reference companion에 반복 갱신 절차를 연결한다.
- 5차: Overview IA polish와 refresh status copy를 정리한다.
