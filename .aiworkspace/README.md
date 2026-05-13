# AI Workspace

이 폴더는 Codex / AI 작업자가 프로젝트를 이해하고 일관되게 작업하기 위한 문서와 도구의 canonical workspace다.

애플리케이션 제품 코드는 루트의 `app/`, `finance/`에 남기고, AI 작업 운영 자산은 이 폴더 아래에 모은다.

## 구조

```text
.aiworkspace/
  note/
    finance/                 # finance 프로젝트 문서, task, report, registry, saved setup
  plugins/
    quant-finance-workflow/   # finance 전용 Codex plugin / skill / helper script 원본
```

## 역할

| Path | 역할 |
|---|---|
| `.aiworkspace/note/finance/docs/` | 오래 유지될 제품 / 구조 / 데이터 / 흐름 / runbook 문서 |
| `.aiworkspace/note/finance/tasks/` | active / done task의 계획, 상태, 실행 결과, 리스크 |
| `.aiworkspace/note/finance/phases/` | 여러 task를 묶는 phase 통합 계획 |
| `.aiworkspace/note/finance/reports/` | 사람이 읽는 backtest report, 전략 hub, validation report |
| `.aiworkspace/note/finance/registries/` | 제품 workflow가 읽고 쓰는 append-only JSONL registry |
| `.aiworkspace/note/finance/saved/` | 사용자가 저장한 reusable setup |
| `.aiworkspace/note/finance/run_history/` | 로컬 실행 이력. 보통 커밋하지 않음 |
| `.aiworkspace/plugins/quant-finance-workflow/` | 프로젝트 전용 Codex skill / script source |

## 운영 원칙

- 프로젝트 전용 skill의 원본은 `.aiworkspace/plugins/quant-finance-workflow/skills/`에 둔다.
- `~/.codex/skills/finance-*`는 현재 Codex runtime에서 읽는 mirror / 설치본으로 취급한다.
- 장기 지식은 `.aiworkspace/note/finance/docs/`에 둔다.
- 작업 중 상태와 시행착오는 `.aiworkspace/note/finance/tasks/active/`에 둔다.
- registry JSONL, run history, temp artifact는 구조상 이 폴더에 있어도 명시 요청 없이는 임의 재작성하거나 커밋하지 않는다.
