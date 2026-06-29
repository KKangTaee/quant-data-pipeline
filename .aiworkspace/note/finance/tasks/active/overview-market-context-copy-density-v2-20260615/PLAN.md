# Overview Market Context Copy Density V2

Status: Active
Date: 2026-06-15
Worktree: `sub-dev`

## 이걸 하는 이유?

`Workspace > Overview > Market Context` 1차 작업으로 큰 카드 안에 묶여 있던 시장 맥락을 cockpit과 reading-flow 단락으로 나눴다. 다만 상단 요약이 `현재 맥락: ...` 한 줄로 압축되어 있어 사람이 시장 상황을 문장으로 읽기 어렵고, 하단 단락도 타이포 위계가 충분히 분리되지 않아 여전히 정보 덩어리처럼 보인다.

이번 2차는 기존 DB-backed context-only 경계를 유지하면서, 상단 요약을 2~3문장형 브리프로 풀고 읽기 단락의 글자 크기 / 행간 / 색 대비 / 밀도를 정리한다.

## Scope

- 상단 `오늘의 시장 맥락` 요약을 짧은 문장형 브리프로 변경한다.
- `시장 브리프`, `해석할 때 같이 볼 변수`, `과거 유사 맥락 참고`, `자료 기준 / 출처 상태`의 읽기 위계를 더 명확하게 만든다.
- 서비스 / 렌더러 계약 테스트를 먼저 갱신한다.
- Browser QA로 desktop/mobile에서 overflow와 first-view readability를 확인한다.

## Out Of Scope

- 새 provider, DB schema, registry / saved JSONL write.
- Overview 렌더 중 external fetch.
- 실행 job / row / status 중심 진단 패널 추가.
- Backtest validation, Final Review, Operations monitoring, trading signal 연결.
- deep drill-in interaction, dashboard editor, 사용자 설정 저장.

## Completion Criteria

- 상단 요약이 `현재 맥락:` 한 줄 계약에 의존하지 않고 2~3문장형으로 표시된다.
- reading-flow 단락이 카드 안 카드처럼 보이지 않고, 섹션 제목 / 본문 / 보조 근거 위계가 분리된다.
- focused unittest, py_compile, diff check가 통과한다.
- Browser QA screenshot을 남긴다.

