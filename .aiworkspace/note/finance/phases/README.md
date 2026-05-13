# Finance Phase Documents

## 목적

이 폴더는 finance 프로젝트의 phase별 계획, 작업 단위, QA checklist, completion / next-phase handoff 문서를 모아 둔다.

기존 `phase1` ~ `phase36` 상세 문서는 현재 구현과 맞지 않는 legacy history로 보고 제거했다.
앞으로 새 phase는 `active/`에서 관리하고, closeout 후 필요한 요약만 `done/`으로 이동한다.

## 구조

| 경로 | 역할 |
|---|---|
| `active/` | 현재 진행 중인 phase 계획과 통합 기록 |
| `done/` | 완료된 phase의 최소 요약 / handoff |
| `../docs/ROADMAP.md` | 전체 phase / task 방향과 현재 active work |
| `../docs/INDEX.md` | finance 문서 전체 index |
| `../docs/runbooks/templates/` | phase plan / checklist template source |

## 새 phase를 만들 때

새 phase bundle은 아래 helper가 이 폴더 아래에 생성한다.

```bash
python3 .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase <N> --title "<Phase Title>"
```

생성 위치는 `.aiworkspace/note/finance/phases/active/phase<N>/`이다.

## 관리 기준

- phase 진행 문서는 가능한 한 `phases/active/<phase-name>/`에 둔다.
- phase 밖에서 반복 사용되는 운영 지식은 `../docs/`에 둔다.
- backtest 결과나 후보 분석이 phase를 넘어 재사용되면 `../reports/backtests/`에 둔다.
- 코드 구조 설명은 `../docs/architecture/`, 데이터 / DB 의미는 `../docs/data/`에 둔다.
- legacy phase 세부 history가 필요하면 Git history에서 복구한다.
