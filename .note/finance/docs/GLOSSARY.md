# Finance Glossary

Status: Active
Last Verified: 2026-05-12

| Term | Meaning | Notes |
|---|---|---|
| Backtest Analysis | 후보 전략이나 saved mix를 실행 / 비교해 selection source를 만드는 단계 | Backtest workflow의 첫 단계 |
| Practical Validation | 후보 source를 실전 투입 전 12개 진단으로 검증하는 단계 | 투자 승인 단계가 아님 |
| Final Review | Practical Validation 결과를 보고 select / hold / reject / re-review 판단을 남기는 단계 | 현재 Backtest workflow의 마지막 판단 화면 |
| Selected Portfolio Dashboard | Final Review에서 selected 된 포트폴리오를 운영 관점으로 보는 Operations 화면 | live approval / order 기능 없음 |
| Selection Source | Backtest Analysis에서 Practical Validation으로 보내는 후보 입력 | JSONL registry에 저장될 수 있음 |
| Diagnostic | Practical Validation의 개별 검증 항목 | 현재 12개 domain |
| Actual Evidence | provider, FRED, DB snapshot 등 목적에 맞는 실제 근거 | 가장 신뢰도 높은 진단 근거 |
| Bridge Evidence | 원래 목적은 다르지만 실제 DB에 있어 보조 근거로 쓸 수 있는 데이터 | 예: price history ADV, asset profile AUM |
| Proxy Evidence | ticker 이름, benchmark 움직임처럼 추정에 가까운 근거 | 통과처럼 보이지 않게 origin을 표시해야 함 |
| NOT_RUN | 데이터나 구현이 없어 진단을 실행하지 못한 상태 | pass가 아님 |
| REVIEW | 근거가 부분적이거나 사람이 확인해야 하는 상태 | 반드시 실패는 아님 |
| BLOCKED | 가격 부재, 실행 경계 위반 등 검증을 계속하면 위험한 상태 | Final Review에서 강한 blocker로 취급 |
| Provider Snapshot | ETF issuer / FRED / DB bridge에서 수집해 DB에 저장한 기준일 데이터 | Practical Validation은 loader로 읽음 |
| Holdings Look-through | ETF 내부 구성 종목과 exposure를 들여다보는 것 | wrapper ticker만 보는 것보다 강한 검증 |
| Operability | ETF 비용, 규모, 유동성, spread, NAV 괴리 등 실제 운용 가능성 | P2 핵심 진단 |
| Main Worktree | phase 설계, 작업 분해, 통합을 담당하는 세션 | 이 세션은 `codex/phase` |
| Sub Worktree | Main이 분리한 개별 task를 수행하는 세션 | 후보 탐색, UX polish 등 |
| Phase | 여러 task를 묶는 상위 개발 단위 | `.note/finance/phases/active/` |
| Task | 실제 구현, 조사, 문서 정리를 수행하는 실행 단위 | `.note/finance/tasks/active/` |
