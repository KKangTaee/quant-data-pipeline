# Finance Phase Documents

## 목적

이 폴더는 finance 프로젝트의 phase별 계획, 작업 단위, QA checklist, completion / next-phase handoff 문서를 모아 둔다.

예전에는 numbered phase 폴더가 finance root에 직접 놓여 있었다. 지금부터는 root 문서를 가볍게 유지하기 위해 모든 phase 실행 문서를 이 폴더 아래의 `phaseN/`에 둔다.

## 구조

| 경로 | 역할 |
|---|---|
| `phase1/` ~ `phase31/` | phase별 계획, TODO, 작업 단위, QA, closeout 문서 |
| `../MASTER_PHASE_ROADMAP.md` | 전체 phase 순서와 현재 진행 상태 |
| `../FINANCE_DOC_INDEX.md` | phase 문서를 포함한 finance 문서 전체 index |
| `../PHASE_PLAN_TEMPLATE.md` | 새 phase plan 템플릿 |
| `../PHASE_TEST_CHECKLIST_TEMPLATE.md` | 새 phase QA checklist 템플릿 |

## 새 phase를 만들 때

새 phase bundle은 아래 helper가 이 폴더 아래에 생성한다.

```bash
python3 plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase <N> --title "<Phase Title>"
```

생성 위치는 `.note/finance/phases/phase<N>/`이다.

## 관리 기준

- phase 진행 문서는 `phases/phase*/`에 둔다.
- phase 밖에서 반복 사용되는 운영 문서는 `../operations/`에 둔다.
- backtest 결과나 후보 분석이 phase를 넘어 재사용되면 `../backtest_reports/`에 둔다.
- 코드 구조 설명은 `../code_analysis/`, 데이터 / DB 의미는 `../docs/data/`에 둔다.
