# RUNS - Product Research Plugin Split

## 2026-05-14

- `sed -n '1,220p' /Users/taeho/.codex/skills/finance-task-intake/SKILL.md`
  - Result: confirmed current routing mentions product research workflow.
- `sed -n '1,220p' /Users/taeho/.codex/skills/.system/plugin-creator/SKILL.md`
  - Result: confirmed plugin root must keep `.codex-plugin/plugin.json` and marketplace entries need policy/category.
- `sed -n '1,220p' /Users/taeho/.codex/skills/.system/skill-creator/SKILL.md`
  - Result: confirmed skill source should stay concise and validate with quick_validate.
- `find .aiworkspace/plugins -maxdepth 4 -type f | sort`
  - Result: confirmed product research skills/scripts were still inside `quant-finance-workflow` before split.
- `git mv ...`
  - Result: moved 4 product research skills and 2 product research scripts to `.aiworkspace/plugins/quant-finance-product-research/`.
- `rg -n "quant-finance-workflow/scripts/(bootstrap_product_research_bundle|check_product_research_bundle)|quant-finance-workflow/skills/finance-(product-research-workflow|product-audit|benchmark-research|feature-opportunity)" AGENTS.md .aiworkspace/README.md .aiworkspace/note/finance/docs .aiworkspace/plugins -g '*.md' -g '*.json' -g '*.py' -g '*.yaml'`
  - Result: no current docs/plugin stale source paths found.
- `rsync -a --delete ...`
  - Result: synced `finance-product-research-workflow`, `finance-product-audit`, `finance-benchmark-research`, `finance-feature-opportunity` from the new plugin source to `~/.codex/skills`; synced `finance-task-intake` from workflow plugin source.
- `diff -qr ...`
  - Result: repo-local source and global mirror match for changed skills.
- `for d in .aiworkspace/plugins/quant-finance-workflow/skills/finance-* .aiworkspace/plugins/quant-finance-product-research/skills/finance-*; do .venv/bin/python /Users/taeho/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1; done`
  - Result: all 12 finance skills are valid.
- `.venv/bin/python -m py_compile .aiworkspace/plugins/quant-finance-product-research/scripts/bootstrap_product_research_bundle.py .aiworkspace/plugins/quant-finance-product-research/scripts/check_product_research_bundle.py`
  - Result: passed.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-product-research/scripts/bootstrap_product_research_bundle.py --title "Example Product Research" --research-id 2026-05-example-product-research --focus "Dry-run only." --dry-run`
  - Result: printed expected bundle file plan without writing files.
- `.venv/bin/python .aiworkspace/plugins/quant-finance-product-research/scripts/check_product_research_bundle.py --all-active`
  - Result: passed. `2026-05-backtest-report-productization` had no issues; `2026-05-ui-platform-research` kept non-fatal evidence-label warnings from the earlier format.
- `python3 -m json.tool .aiworkspace/plugins/quant-finance-workflow/.codex-plugin/plugin.json >/dev/null && python3 -m json.tool .aiworkspace/plugins/quant-finance-product-research/.codex-plugin/plugin.json >/dev/null && python3 -m json.tool .agents/plugins/marketplace.json >/dev/null`
  - Result: passed.
- `git diff --check`
  - Result: passed.
