# Finance Phase Documents

## 목적

이 폴더는 finance 프로젝트의 phase별 상위 계획, task board, 상태, risk, 통합 기록을 모아 둔다.

기존 `phase1` ~ `phase36` 상세 문서는 현재 구현과 맞지 않는 legacy history로 보고 제거했다.
앞으로 새 phase는 `active/`에서 관리하고, closeout 후 필요한 요약만 `done/`으로 이동한다.

## 구조

| 경로 | 역할 |
|---|---|
| `active/` | 현재 진행 중인 phase 계획과 통합 기록 |
| `done/` | 완료된 phase의 최소 요약 / handoff |
| `../docs/ROADMAP.md` | 현재 baseline, Active/Paused/Verification-Only, 다음 결정 |
| `../docs/INDEX.md` | finance 문서 탐색과 읽기 순서 |
| `../tasks/active/` | phase 안에서 실제로 실행하는 task 기록 |

## 새 phase를 만들 때

사용자가 phase-managed work를 명시적으로 요청하면 아래 helper로 bundle을 만든다.

```bash
.venv/bin/python \
  .aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py \
  --phase-id <semantic-kebab-id> \
  --title "<Phase Title>"
```

생성 위치는 `.aiworkspace/note/finance/phases/active/<phase-id>/`이다.

```text
PLAN.md
DESIGN.md
TASKS.md
STATUS.md
RISKS.md
INTEGRATION.md
```

## 관리 기준

- phase 진행 문서는 가능한 한 `phases/active/<phase-name>/`에 둔다.
- 실제 구현, 조사, 명령 결과는 `tasks/active/<task-name>/`에 둔다.
- phase `STATUS.md`는 `State: active | paused | verification_only | complete | blocked` 계약을 따른다.
- phase 밖에서 반복 사용되는 운영 지식은 `../docs/`에 둔다.
- backtest 결과나 후보 분석이 phase를 넘어 재사용되면 `../reports/backtests/`에 둔다.
- 코드 구조 설명은 `../docs/architecture/`, 데이터 / DB 의미는 `../docs/data/`에 둔다.
- legacy phase 세부 history가 필요하면 Git history에서 복구한다.
- phase closeout만으로 INDEX나 root log를 갱신하지 않는다. 각 문서 역할의 사실이 바뀐 경우에만 수정한다.
