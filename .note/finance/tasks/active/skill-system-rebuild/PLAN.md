# PLAN - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## 이걸 하는 이유?

문서 구조가 `.note/finance/docs/`, `tasks/active/`, `phases/active/`, `reports/backtests/` 중심으로 바뀌었지만 기존 finance skill 일부는 여전히 legacy root 문서와 `phase<N>` 구조를 참조하고 있었다.

이 작업은 Codex가 오래된 문서 경로를 읽거나, phase 중심 workflow로 되돌아가는 일을 막기 위해 skill의 경로, 책임, plugin 경계를 새 구조에 맞게 정리한다.

완료되면 Codex는 작업 시작 시 필요한 skill만 짧게 로드하고, 상세 기준은 repo 문서와 reference로 찾는 구조에 가까워진다.

## 작업 단위

| 단계 | 목표 | 상태 |
|---|---|---|
| 1차 | stale 문서 경로 보정, legacy phase skill 제거 | completed |
| 2차 | workflow / domain skill 책임 재정의 | pending |
| 3차 | SKILL.md 슬림화와 references 분리 | pending |
| 4차 | validation, plugin placeholder 정리, 실제 trigger 점검 | pending |

## 종료 조건

- finance skill에서 legacy finance 문서 경로 참조가 사라진다.
- task / workflow 중심 skill 구조가 정리된다.
- SKILL.md는 핵심 절차와 reference 안내만 담고, 긴 설명은 references로 이동한다.
- repo-local plugin은 검증된 skill 묶음만 담도록 정리된다.
