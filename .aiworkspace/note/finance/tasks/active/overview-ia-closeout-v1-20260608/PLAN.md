# Plan

## 이걸 하는 이유?

1차~4차로 Overview 상단과 주요 deep tabs가 summary-first 흐름을 갖췄지만, 사용자는 아직 전체 Overview가 어떤 순서로 읽히는지 한 번에 알기 어렵다.
5차는 새 데이터 / provider / workflow를 추가하지 않고, cockpit 다음에 compact IA guide를 두어 `market context -> data repair -> transitional candidate ops` 경계를 명확히 닫는다.

## Scope

- Add a compact `Overview Map` / IA closeout guide below the macro cockpit and before deep tabs.
- Keep `Candidate Ops` accessible but label it as transitional / backtest-owned context.
- Keep Overview context-only language visible.
- Reuse static read-model metadata only; no provider fetch, schema change, persistence, registry, or saved JSONL write.

## Out Of Scope

- Removing or moving `Candidate Ops`.
- Backtest Candidate Review / Practical Validation / Final Review changes.
- Ingestion action queue execution.
- New provider / DB schema / registry / saved JSONL write.
- React / API frontend migration.

## Completion

- Contract tests cover guide placement, CSS, and model boundary language.
- Streamlit Browser QA confirms the guide appears below the cockpit.
- Durable docs and root handoff logs are updated briefly.
