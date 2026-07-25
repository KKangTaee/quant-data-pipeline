# Economic Cycle Manual Refresh V1 Plan

Status: Design Review
Last Updated: 2026-07-25

## 이걸 하는 이유?

경제사이클 월중 흐름은 DB에 저장된 마지막 결과만 읽기 때문에 2026-07-21에 머물러
있고, 브라우저나 데스크톱을 다시 열어도 자동으로 최신화되지 않는다. 사용자는
background scheduler 대신 최신화 필요 여부를 직접 확인하고 버튼으로 수집·계산하는
명시적인 흐름을 원한다.

## Goal

로컬 FRED credential을 안전하게 주입하고, 경제사이클 화면에서 최신 계산 가능일과
저장 기준일을 비교한 뒤 기존 combined refresh pipeline을 수동 실행하는 기능을 만든다.

## Scope

- 세 worktree root `.env`와 Git 제외 보호
- UI/CLI 공용 local environment loader
- 경제사이클 freshness read-model
- nonce 기반 manual refresh event와 DB postcondition
- compact React 및 fallback Streamlit action
- 실제 FRED 수집, data-integrity 검증, Browser QA
- 관련 runbook/project map/root handoff 동기화

## Non-Goals

- launchd, cron, heartbeat, 진입 시 자동 provider fetch
- raw run/job/row 진단 패널
- 기존 월말 history rewrite
- API key의 tracked 문서 또는 log 기록

## Stop Condition

- 설계 명세가 사용자 검토를 통과한다.
- 구현 계획에 따라 1~3차가 완료된다.
- focused Python/React 검증과 actual DB postcondition이 통과한다.
- desktop/420px Browser QA screenshot을 만들되 commit하지 않는다.
- secret와 generated artifact를 제외한 coherent implementation이 commit된다.

## Roadmap

### 1차 — Local secret and runtime boundary

- [ ] `.env` shared/tracked Git protection
- [ ] main-dev/sub-dev/backtest-dev local credential storage
- [ ] process env precedence를 보존하는 loader 및 tests

### 2차 — Freshness and manual action

- [ ] weekday target freshness contract
- [ ] combined refresh action wrapper와 persisted postcondition
- [ ] React event/fallback action, cache/rerun behavior

### 3차 — Actual refresh and closeout

- [ ] real FRED refresh와 monthly history invariant 검증
- [ ] React build, focused regression, Browser QA
- [ ] finance durable docs와 root handoff sync

## Current Step

전체 roadmap `0/3차`다. 현재는 승인된 대화 설계를 written spec으로 고정하고 사용자의
명세 검토를 기다리는 단계다. 이번 단계에서는 `.env` 저장이나 code/database 변경을
수행하지 않는다.

## Canonical Design

`docs/superpowers/specs/2026-07-25-economic-cycle-manual-refresh-design.md`
