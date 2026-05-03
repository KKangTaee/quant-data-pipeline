# Finance Skill Split - 2026-05-03

## 목적

finance 작업에서 `finance-doc-sync`가 구현 / phase 운영 / 문서 동기화를 모두 떠맡는 것을 줄이고,
작업 종류별로 더 작은 스킬을 먼저 호출하도록 정리한다.

## 새로 만든 local Codex skill

| Skill | 위치 | 역할 |
|---|---|---|
| `finance-backtest-web-workflow` | `/Users/taeho/.codex/skills/finance-backtest-web-workflow/SKILL.md` | `app/web/backtest_*.py`, Candidate Review, Portfolio Proposal, History, Candidate Library, Streamlit state / runtime registry UI 구현 |
| `finance-phase-management` | `/Users/taeho/.codex/skills/finance-phase-management/SKILL.md` | phase open / TODO / checklist / roadmap status / manual QA / closeout 관리 |

## 기존 skill 역할 조정

`finance-doc-sync`는 계속 사용하되, 구현 메인 스킬이 아니라 마무리 동기화 스킬로 둔다.

권장 순서:

1. Backtest UI 구현: `finance-backtest-web-workflow`
2. Phase 운영: `finance-phase-management`
3. DB / factor / core strategy 구현: 기존 domain skill
4. 마지막 문서 정렬: `finance-doc-sync`

## 기대 효과

- Backtest UI 구현 때 필요한 파일 경계와 Streamlit / JSONL 주의사항을 먼저 읽는다.
- Phase closeout 때는 phase status와 QA 문서에 집중한다.
- `finance-doc-sync`는 모든 작업을 직접 판단하는 넓은 스킬이 아니라, 마지막 consistency check로 동작한다.
