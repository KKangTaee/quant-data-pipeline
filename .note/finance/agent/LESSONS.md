# Finance Codex Lessons

Status: Active
Last Verified: 2026-05-12

이 문서는 작업 후 회고와 다음 작업 방식 개선점을 남긴다.

## 2026-05-12 - Documentation Rebuild Start

- 문서가 많아질수록 Codex가 더 똑똑해지는 것이 아니라, 읽는 순서와 기록 위치가 흐려지면 오히려 작업 효율이 떨어진다.
- 앞으로 장기 지식은 `docs/`, 진행 중 기록은 `tasks/` 또는 `phases/`, 반복 실수는 `agent/`로 분리한다.
- 기존 대형 문서를 유지하는 것보다 다음 세션이 바로 읽을 수 있는 작은 기준 문서가 더 중요하다.

## 2026-05-13 - Legacy Deletion Needs Runtime Reference Check

- 폴더 이름이 `research`나 `operations`라고 해서 모두 순수 문서인 것은 아니다.
- 삭제 전에 앱 코드가 직접 읽는 reference data와 화면에 노출되는 경로를 먼저 확인해야 한다.
- `Reference > Guides`처럼 문서 경로만 보여주는 화면과 `Reference > Glossary`처럼 md를 실제 읽는 화면은 다르게 다뤄야 한다.
- registry guide는 여러 개의 오래된 guide 문서보다 `registries/README.md` 하나에 current / legacy boundary를 짧게 모으는 편이 다음 세션에 덜 헷갈린다.
