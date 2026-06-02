# Investability Decision Foundation Plan

Status: Implementation Complete
Created: 2026-05-28

## 이걸 하는 이유?

현재 제품은 Backtest Analysis에서 후보를 만들고, Practical Validation에서 검증하고, Final Review에서 판단한 뒤, Selected Portfolio Dashboard에서 사후 확인하는 큰 흐름을 이미 갖고 있다.
하지만 실전 투자 판단 보조 도구로 쓰기에는 아직 기준선이 약하다.

특히 사용자가 지적한 것처럼, 의미 없는 JSONL 저장이 다시 늘어나거나, `NOT_RUN` / proxy evidence가 통과처럼 읽히거나, 무료 API / crawler / DB 저장 경계가 흐려지면 백테스트 결과가 실제 투자 검토 근거처럼 보이는 위험이 커진다.

이 phase는 새로운 기능을 마구 붙이는 작업이 아니다.
앞으로 개발할 기능들이 같은 원칙을 따르도록 `저장 정책`, `검증 gate`, `데이터 수집 경계`, `사용자-facing 용어`, `task 순서`를 먼저 고정하는 기준선이다.

## Phase Goal

Backtest 중심 탐색 도구를 "실전 검토 가능한 포트폴리오 후보를 선별하고 관리하는 의사결정 workflow"로 강화한다.

구체적으로는 아래 상태를 만든다.

- 후보의 source chain과 검증 근거를 한 화면에서 설명할 수 있다.
- critical gap이 남아 있으면 `모니터링 후보`로 선정되지 않는다.
- full provider / holdings / macro raw data는 DB에 두고, JSONL에는 compact evidence만 남긴다.
- 새 저장 기능은 source-of-truth일 때만 추가한다.
- 무료 API / 공식 source를 우선 사용하고, 없을 때만 ingestion layer에서 crawler를 통해 DB에 저장한다.
- Final Review와 Selected Dashboard는 live approval, broker order, auto rebalance가 아님을 계속 유지한다.

## Scope

포함한다.

- Phase 0 기준 정책 문서화
- Evidence Packet / gate / provenance / robustness / monitoring으로 이어지는 task board 정리
- 기존 `investability-evidence-packet-v1` 구현을 이 phase의 첫 landed slice로 편입
- 저장 정책과 데이터 수집 정책을 후속 task의 acceptance criteria로 고정
- Roadmap / root handoff log / active phase index 동기화

포함하지 않는다.

- 새 DB schema 구현
- 새 JSONL registry 생성
- provider crawler 구현
- strategy backtest logic 변경
- React / Next.js / FastAPI 전환
- broker 연결, 자동 주문, auto rebalance
- 사용자 free-form memo 저장 기능

## Operating Principles

| Principle | Policy |
| --- | --- |
| Evidence first | 수익률보다 source chain, data trust, provider coverage, benchmark parity, robustness, assumptions를 먼저 본다 |
| No memo sprawl | 사용자 메모용 JSONL이나 단계별 반복 저장을 만들지 않는다 |
| Compact JSONL | workflow registry에는 판단에 필요한 compact evidence만 저장한다 |
| DB-backed data | raw provider response, holdings row, macro series, full coverage data는 DB에 둔다 |
| Free-source first | 필요한 데이터는 무료 API / 공식 source를 먼저 찾고, 없으면 ingestion crawler + DB 저장으로 처리한다 |
| UI no direct fetch | Streamlit UI는 provider / FRED / web을 직접 호출하지 않고 service / loader를 통해 읽는다 |
| `NOT_RUN` is not pass | 실행하지 못한 검증은 통과가 아니라 데이터 또는 구현 공백이다 |
| No live trading boundary | 선정은 Selected Dashboard 모니터링 후보 또는 tracking 대상이지 live approval이 아니다 |

## Development Flow

| Phase Slice | Goal | Status |
| --- | --- | --- |
| Phase 0 | 저장 / 검증 / 데이터 수집 / UX 용어 기준 확정 | Complete |
| Phase 1 | Final Review Investability Evidence Packet V1 | Complete |
| Phase 2 | Validation Gate Hardening V1 | Complete |
| Phase 3 | Data Provenance / Storage Governance V1 | Complete |
| Phase 4 | Look-through Exposure Board V1 | Complete |
| Phase 5 | Robustness Lab V1 | Complete |
| Phase 6 | Selected Monitoring Timeline V1 | Complete |
| Phase 7 | Decision Dossier / Report V1 | Complete |

## Done Criteria

- Phase docs describe why the work exists, what is in/out, and how future tasks are ordered.
- Storage policy states when JSONL is allowed and when DB is required.
- Validation gate policy states how hard blockers, critical `NOT_RUN`, proxy-only evidence, paper observation gaps, and benchmark/provider gaps are handled.
- Data acquisition policy states free API / official source first, crawler only through ingestion, DB as durable source, UI no direct fetch.
- Task board identifies owners, dependencies, conflict files, and verification standards.
- Durable docs point future workers to this phase board.

## Closeout Result

The planned implementation slices are complete as of 2026-05-28.
The phase remains in `phases/active/` for discoverability, but its implementation track is closed.

Carry-forward decisions:

- Whether `structured-waiver-policy-v1` should exist at all.
- Whether selected decisions should eventually require an as-of provider snapshot id.
- Whether Practical Validation V2 P2 should be closed out or extended before P3.
