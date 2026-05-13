# PLAN - Product Research Plugin Split

Status: Active
Last Updated: 2026-05-14

## Goal

제품 방향 리서치용 skill과 helper script를 기존 `quant-finance-workflow` plugin에서 분리해, 별도 `quant-finance-product-research` plugin으로 관리한다.

## 이걸 하는 이유?

`quant-finance-workflow` 안에 구현, 문서 sync, 통합 검토, runbook, product research까지 모두 들어가면 plugin 경계가 다시 커진다. 사용자가 앞으로 리서치용 플러그인을 별도로 사용할 계획이 있으므로, 지금 source-of-truth를 분리해두는 편이 장기 관리에 더 안전하다.

분리 후 역할은 다음과 같다.

| Plugin | Role |
| --- | --- |
| `quant-finance-workflow` | finance 작업 분류, 구현 domain skill, 문서 sync, 통합 검토, runbook |
| `quant-finance-product-research` | 제품 방향 리서치 실행, product audit, benchmark research, feature opportunity, research bundle helper |

## Scope

- 새 plugin root `.aiworkspace/plugins/quant-finance-product-research/` 생성
- product research 관련 4개 skill 이동
- product research helper script 2개 이동
- 기존 plugin manifest에서 product research 표현 제거
- marketplace에 새 plugin entry 추가
- `AGENTS.md`, `.aiworkspace/README.md`, `docs/ROADMAP.md` 경계 갱신
- global `~/.codex/skills` mirror가 새 repo-local source와 일치하는지 확인

## Out Of Scope

- skill 이름 변경
- research output 본문 수정
- 별도 plugin 배포/릴리즈
- `docs/ROADMAP.md`에 research recommendation을 구현 계획으로 승격
- `BacktestReportPack` 구현

## Done Criteria

- product research skill과 helper script가 새 plugin 아래에 있다.
- 기존 `quant-finance-workflow` plugin은 product research skill/script를 더 이상 소유하지 않는다.
- marketplace에 두 plugin이 모두 등록되어 있다.
- JSON validation, skill quick validation, script py_compile, research bundle check, mirror diff, `git diff --check`를 통과한다.
