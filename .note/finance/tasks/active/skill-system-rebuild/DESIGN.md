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
