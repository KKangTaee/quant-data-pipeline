# RUNS - Product Research Output Contract

Status: Active
Last Updated: 2026-05-13

## Commands

- `git status --short`
  - Result: unrelated run history, registry JSONL, and `.DS_Store` changes already existed and were left untouched.
- `sed -n '1,240p' AGENTS.md`
  - Result: current rules still described legacy `research/` as removed.
- `sed -n '1,220p' .aiworkspace/note/finance/docs/INDEX.md`
  - Result: work records did not yet include product direction research.
- `sed -n '1,240p' .aiworkspace/note/finance/docs/PROJECT_MAP.md`
  - Result: top-level structure did not yet include `.aiworkspace/note/finance/research/`.
- `rsync -a ... /Users/taeho/.codex/skills/...`
  - Result: updated global mirrors for `finance-task-intake`, `finance-product-audit`, `finance-benchmark-research`, and `finance-feature-opportunity`.
- `.venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py .aiworkspace/plugins/quant-finance-workflow/skills/finance-task-intake`
  - Result: skill is valid.
- `.venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py .aiworkspace/plugins/quant-finance-workflow/skills/finance-product-audit`
  - Result: skill is valid.
- `.venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py .aiworkspace/plugins/quant-finance-workflow/skills/finance-benchmark-research`
  - Result: skill is valid.
- `.venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py .aiworkspace/plugins/quant-finance-workflow/skills/finance-feature-opportunity`
  - Result: skill is valid.
- `git diff --check`
  - Result: passed.
