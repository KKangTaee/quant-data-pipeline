# Storage Governance Audit V1 Design

Status: Complete
Created: 2026-05-28

## Design Position

이번 task는 storage behavior를 바꾸는 구현 task가 아니라, 이후 구현을 제어하기 위한 governance task다.

핵심 결정은 다음과 같다.

1. 제품 주 흐름의 source chain은 `PORTFOLIO_SELECTION_SOURCES.jsonl -> PRACTICAL_VALIDATION_RESULTS.jsonl -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`로 제한한다.
2. `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 optional monitoring snapshot이며 자동 저장 대상이 아니다.
3. `SAVED_PORTFOLIO_MIXES.jsonl`와 `SAVED_PORTFOLIOS.jsonl`는 사용자가 명시적으로 저장한 reusable setup이다. validation evidence나 final decision을 대체하지 않는다.
4. legacy candidate / proposal / paper ledger registry는 호환성으로 유지하되 main flow의 새 의존성을 늘리지 않는다.
5. run history와 run artifacts는 local/debug artifact로 보고, 투자 판단 source-of-truth로 승격하지 않는다.
6. raw provider response, full holdings, full macro series, full price tables는 DB에 두고 JSONL에는 compact evidence만 둔다.

## Storage Classes

| Class | Meaning | Default Action |
|---|---|---|
| Main workflow registry | 다음 stage가 읽어야 하는 compact source / validation / decision record | Keep; append-only; compact evidence only |
| Explicit saved setup | 사용자가 나중에 다시 열거나 replay하려고 명시 저장한 설정 | Keep; not a validation or approval record |
| Optional monitoring log | 사용자가 직접 남긴 selected portfolio observation snapshot | Keep only as explicit action; no auto-save |
| Legacy compatibility registry | 과거 Candidate Review / Proposal / Paper flow 호환 기록 | Preserve; do not expand main-flow dependency |
| Local runtime artifact | 실행 이력, debug artifact, generated result JSON/CSV | Do not treat as durable product source |
| DB source-of-truth | provider / macro / holdings / prices / factors 원천 및 full evidence | Store through ingestion -> DB -> loader |

## Guardrails For Future Work

- 새 JSONL을 만들기 전에 `docs/data/STORAGE_GOVERNANCE.md`의 checklist를 통과해야 한다.
- 화면 입력값을 반복 memo로 저장하는 기능은 기본 거절한다.
- Final Review decision row에는 packet / gate policy의 compact snapshot만 둔다.
- Practical Validation result에는 diagnostic status, blocker, provenance summary처럼 stage handoff에 필요한 정보만 둔다.
- 웹 UI가 remote provider / FRED / crawler를 직접 fetch하지 않는다.
- 무료 API나 crawler는 `finance/data/*` ingestion과 DB persistence 경계를 통해서만 제품 흐름에 들어온다.

## Deferred Implementation Candidates

| Candidate | Why Deferred |
|---|---|
| legacy registry deprecation UI | 호환성 영향이 커서 별도 UX 승인 필요 |
| `SAVED_PORTFOLIOS.jsonl` rewrite-on-save migration | 사용자의 reusable setup 보존 정책과 충돌 위험이 있어 별도 task 필요 |
| storage lint / hygiene script hardening | 이번 task는 audit 기준 확정이 목적이며 구현 자동화는 다음 slice로 분리 가능 |
| DB-backed evidence coverage fields | `data-provenance-coverage-v1`에서 ingestion / loader 경계와 함께 다룬다 |
