# DESIGN - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## 기준

Notion의 `문서 작성의 팁 - 스킬과 플러그인` 방향을 따른다.

- `SKILL.md`: 언제 쓰는지, 무엇을 먼저 읽는지, 어떤 순서로 작업하는지만 둔다.
- `references/`: 긴 설명, schema, 체크리스트, 상세 사례를 둔다.
- `scripts/`: 반복 실행되는 검증 / 변환 / 생성 코드를 둔다.
- plugin은 자동 실행 엔진이 아니라 안정된 skill / MCP / assets 묶음이다.

## 목표 구조

| 유형 | 역할 |
|---|---|
| workflow skill | 작업 분류, active task 운영, root handoff log 관리 |
| domain implementation skill | Backtest UI, DB, factor, strategy 같은 실제 구현 도메인 담당 |
| doc sync skill | 구현 후 문서 alignment, root log, report index 확인 |
| repo-local plugin | 검증된 finance workflow skill과 helper script 묶음 |

## 1차 결정

- `finance-phase-management`는 legacy `phase<N>` 구조를 전제로 하므로 삭제한다.
- phase 기능이 필요하면 새 workflow skill에서 optional integration layer로 다룬다.
- 기존 domain skill은 삭제하지 않고 새 docs 경로만 먼저 보정한다.

## 2차 결정

- 새 workflow skill은 `finance-task-management`로 둔다.
- 이 skill은 task 분류, active task 문서 운영, root handoff log 관리, domain skill routing만 맡는다.
- Backtest UI / DB / factor / strategy skill은 실제 구현 도메인을 맡고, task 상태나 closeout 문서 운영을 직접 소유하지 않는다.
- `finance-doc-sync`는 구현 후 문서 정렬과 cross-document alignment용으로 유지한다.

## 3차 결정

- 프로젝트 전용 finance skill의 원본은 repo-local `.aiworkspace/plugins/quant-finance-workflow/skills/`에 둔다.
- `~/.codex/skills/finance-*`는 현재 Codex runtime에서 읽는 설치본 / mirror로 취급한다.
- 각 skill의 `SKILL.md`에는 trigger, first reads, 핵심 workflow만 둔다.
- 긴 file ownership, domain rule, update matrix, done condition은 `references/`로 분리한다.
- 4차에서는 plugin metadata의 남은 placeholder와 실제 trigger / 설치 흐름을 점검한다.
