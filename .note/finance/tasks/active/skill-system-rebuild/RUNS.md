# RUNS - Skill System Rebuild

Status: Active
Last Updated: 2026-05-13

## 1차 stale path scan

Command:

```bash
rg -n "FINANCE_COMPREHENSIVE_ANALYSIS|FINANCE_DOC_INDEX|MASTER_PHASE_ROADMAP|FINANCE_TERM_GLOSSARY|code_analysis|data_architecture|backtest_reports|operations/|research/|support_tracks|phases/phase|phase<N>|phase\\*/|finance-phase-management" /Users/taeho/.codex/skills/finance-* plugins/quant-finance-workflow/skills/finance-backtest-candidate-refinement
```

Result:

- 수정 전 legacy path가 여러 finance skill에 남아 있었다.
- 수정 후 출력 없음.

## 1차 skill inventory

Result after removal:

```text
/Users/taeho/.codex/skills/finance-backtest-web-workflow/SKILL.md
/Users/taeho/.codex/skills/finance-db-pipeline/SKILL.md
/Users/taeho/.codex/skills/finance-doc-sync/SKILL.md
/Users/taeho/.codex/skills/finance-factor-pipeline/SKILL.md
/Users/taeho/.codex/skills/finance-strategy-implementation/SKILL.md
/Users/taeho/.codex/skills/quant-strategy-creation/SKILL.md
```

## 1차 skill validation

Command:

```bash
for d in /Users/taeho/.codex/skills/finance-backtest-web-workflow \
  /Users/taeho/.codex/skills/finance-db-pipeline \
  /Users/taeho/.codex/skills/finance-doc-sync \
  /Users/taeho/.codex/skills/finance-factor-pipeline \
  /Users/taeho/.codex/skills/finance-strategy-implementation; do
  .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d"
done
```

Result:

- 5개 finance skill 모두 `Skill is valid!`
- system Python은 `yaml` module이 없어 실패했으므로 repo `.venv/bin/python`으로 검증했다.
