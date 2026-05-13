# NOTES - Product Research Plugin Split

## Split Decision

사용자는 product research 기능을 앞으로 별도로 발전시킬 계획이 있으므로, 기존 workflow plugin 안에 두면 관리가 복잡해질 수 있다고 판단했다.

이 판단은 타당하다. `quant-finance-workflow`는 finance 코드/문서 운영을 위한 기본 작업 plugin이고, product research는 외부 리서치, feature 후보, 추천안, research bundle 관리처럼 다른 성격의 workflow를 가진다.

## New Boundary

`quant-finance-workflow`:

- `finance-task-intake`
- `finance-doc-sync`
- `finance-integration-review`
- `finance-runbook-maintainer`
- `finance-backtest-web-workflow`
- `finance-db-pipeline`
- `finance-factor-pipeline`
- `finance-strategy-implementation`

`quant-finance-product-research`:

- `finance-product-research-workflow`
- `finance-product-audit`
- `finance-benchmark-research`
- `finance-feature-opportunity`
- `bootstrap_product_research_bundle.py`
- `check_product_research_bundle.py`

## Compatibility

Skill names are not changed. Codex runtime still sees the same global `~/.codex/skills/finance-*` mirror names, but repo-local source-of-truth is now split by plugin.

This keeps current usage stable while improving source management.
