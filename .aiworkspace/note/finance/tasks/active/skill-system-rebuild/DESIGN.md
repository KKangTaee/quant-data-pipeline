# DESIGN - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## 기준

Notion의 `문서 작성의 팁 - 스킬과 플러그인` 방향을 따른다.

- `SKILL.md`: 언제 쓰는지, 무엇을 먼저 읽는지, 어떤 순서로 작업하는지만 둔다.
- `references/`: 긴 설명, schema, 체크리스트, 상세 사례를 둔다.
- `scripts/`: 반복 실행되는 검증 / 변환 / 생성 코드를 둔다.
- plugin은 자동 실행 엔진이 아니라 안정된 skill / MCP / assets 묶음이다.

## 최종 목표 구조

공통 workflow skill:

| Skill | 역할 |
|---|---|
| `finance-task-intake` | 요청을 보고 phase인지 task인지, 코드 구현인지 문서 작업인지 분류하고 읽어야 할 문서와 active task 위치를 결정 |
| `finance-doc-sync` | 새 docs 구조 기준으로 durable documentation alignment만 담당 |
| `finance-integration-review` | merge conflict, worktree 통합, parallel/sub 결과 통합, staged diff, 검증 기준 확인 |
| `finance-runbook-maintainer` | 반복 명령 / 운영 절차 / helper script 사용법을 `docs/runbooks/`로 정리 |

구현 domain skill:

| Skill | 역할 |
|---|---|
| `finance-backtest-web-workflow` | Backtest / Practical Validation / Final Review / Selected Dashboard UI |
| `finance-db-pipeline` | ingestion, DB schema, provider connector, loader source boundary |
| `finance-strategy-implementation` | strategy / engine / transform / performance |
| `finance-factor-pipeline` | factor, financial statements, PIT accounting logic |

repo-local plugin은 위 8개 skill과 helper script를 묶는 source bundle이다.

## 1차 결정

- `finance-phase-management`는 legacy `phase<N>` 구조를 전제로 하므로 삭제한다.
- phase 기능이 필요하면 새 workflow skill에서 optional integration layer로 다룬다.
- 기존 domain skill은 삭제하지 않고 새 docs 경로만 먼저 보정한다.

## 2차 결정

- 초기에는 workflow skill을 `finance-task-management`로 두었지만, 최종 구조에서는 요청 접수 / 분류 역할을 더 정확히 나타내는 `finance-task-intake`로 바꾼다.
- Backtest UI / DB / factor / strategy skill은 실제 구현 도메인을 맡고, task intake나 closeout 문서 운영을 직접 소유하지 않는다.
- `finance-doc-sync`는 구현 후 문서 정렬과 cross-document alignment용으로 유지하되, task intake / integration / runbook 책임은 분리한다.

## 3차 결정

- 프로젝트 전용 finance skill의 원본은 repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`에 둔다.
- `~/.codex/skills/finance-*`는 현재 Codex runtime에서 읽는 설치본 / mirror로 취급한다.
- 각 skill의 `SKILL.md`에는 trigger, first reads, 핵심 workflow만 둔다.
- 긴 file ownership, domain rule, update matrix, done condition은 `references/`로 분리한다.
- 4차에서는 plugin metadata의 남은 placeholder와 실제 trigger / 설치 흐름을 점검한다.

## 5차 보정 결정

- 사용자가 원래 의도한 skill taxonomy는 4개 workflow skill + 4개 implementation skill이다.
- `finance-backtest-candidate-refinement`는 후보 탐색 / 후보 리서치 성격이 강하고 main-dev worktree의 공통 skill로 유지할 필요가 없으므로 제거한다.
- `finance-integration-review`와 `finance-runbook-maintainer`를 추가해 `finance-task-intake`와 `finance-doc-sync`가 너무 넓어지지 않게 한다.
