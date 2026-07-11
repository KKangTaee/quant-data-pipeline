# Design

Status: Active
Last Updated: 2026-07-11

## Current Problem

- `세부 audit에서 연결`은 내부 adapter 상태지만 사용자 action처럼 보인다.
- `관측`, `판단 근거`, raw English label과 raw status가 기술 계약을 그대로 노출한다.
- 빈 값은 정성 판단, 기간 밖, 미실행 검증, source row 계약 공백이 섞여 있다.
- 현재 provider collection plan은 missing symbol 중심이라 stale-only snapshot의 보강 가능성을 충분히 표현하지 않는다.

## Ownership

- `app/services/backtest_evidence_read_model.py`: trace 분류, 사용자 copy, 개선 action, refreshable summary.
- `app/web/components/final_review_investment_report/`: presentation과 navigation intent.
- `app/web/backtest_final_review/page.py`: React intent 수신, 후보 context를 보존한 Practical Validation route.
- `app/services/backtest_practical_validation.py`: 기존 provider collection plan과 실행 경계.

## Intended Flow

```text
stored validation evidence
  -> Python trace adapter / action taxonomy
  -> React readable review card
  -> refreshable gap exists: Practical Validation Flow4 navigation intent
  -> Python collection action in Level2
  -> Flow2 revalidation + new saved evidence
  -> Final Review report confirmation
```

## Action Taxonomy

- `refreshable_data`: 기존 Python 수집 경계에서 보강 가능.
- `source_discovery`: verified provider source map 탐색 필요.
- `rerun_required`: 저장 evidence 갱신을 위해 Level2 재검증 필요.
- `period_outside`: 현재 backtest 기간 밖이라 갱신으로 해결 불가.
- `implementation_gap`: strategy-specific 검증 runner 또는 adapter 개발 필요.
- `user_decision`: 자동 수치 판정이 아닌 사용자 판단 항목.
- `inherited_limit`: 이미 근거 신뢰도에 반영된 Level2 제한.
