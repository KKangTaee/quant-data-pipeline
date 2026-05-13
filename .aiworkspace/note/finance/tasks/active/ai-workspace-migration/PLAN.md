# PLAN - AI Workspace Migration

Status: Active
Last Updated: 2026-05-13

## 이걸 하는 이유?

기존 구조는 `.note/finance`와 `plugins/quant-finance-workflow`가 루트에 분리되어 있어, AI 작업 문서와 Codex plugin source가 같은 운영 체계 안에 있다는 점이 잘 드러나지 않았다.

이 작업은 AI / Codex 작업용 문서와 도구를 `.aiworkspace/` 아래로 모아, 사람이 봐도 “여기는 AI 작업 workspace”라는 의미가 바로 보이게 만드는 구조 정리다.

완료되면 finance 문서, task 기록, registry, saved setup, repo-local skill/plugin 원본이 한 상위 폴더 아래에서 관리되고, root는 제품 코드와 AI workspace가 명확히 분리된다.

## 작업 단위

| 단계 | 목표 | 상태 |
|---|---|---|
| 1차 | `.aiworkspace/note/finance`와 `.aiworkspace/plugins/quant-finance-workflow`로 이동 | completed |
| 2차 | 코드 / 문서 / skill 경로 갱신 | completed |
| 3차 | 검증과 global skill mirror 동기화 | completed |
| 4차 | 커밋과 남은 artifact 확인 | completed |

## 종료 조건

- `.note/finance`와 root `plugins/quant-finance-workflow`가 canonical 경로로 남지 않는다.
- 코드와 문서의 active path가 `.aiworkspace/note/finance`, `.aiworkspace/plugins/quant-finance-workflow`를 가리킨다.
- app runtime, helper scripts, skill validation이 새 경로에서 동작한다.
- 로컬 run history / generated artifact는 commit에 섞이지 않는다.
