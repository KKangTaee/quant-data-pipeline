# Finance Documentation Merge Conflict Checklist

Use this when merge or rebase conflicts touch `.aiworkspace/note/finance` Markdown documents.

## Goal

Preserve both branches' durable intent and make the final document read as one coherent document, not as two conflict hunks pasted together.

## Start

- Run `git status --short`, `git diff --name-only --diff-filter=U`, and `git ls-files -u`.
- For each conflicted file, inspect the worktree file and, when needed, `git show :1:path`, `git show :2:path`, and `git show :3:path`.
- Treat stage 2 as the current branch side and stage 3 as the incoming side during a merge.
- Identify unrelated dirty files and generated artifacts before staging anything.

## Document Roles

| File or area | Role in a merge |
|---|---|
| `docs/INDEX.md` | Document discovery, read order, and canonical paths. Do not preserve completed-task or current/latest history here. |
| `docs/PRODUCT_DIRECTION.md` | Approved product promise, user journey, surface roles, principles, and non-goals. |
| `docs/PROJECT_MAP.md` | Implemented code, screen, workflow, and storage ownership boundaries. |
| `docs/ROADMAP.md` | Current baseline, Active/Paused/Verification-Only state, next decisions, and priority. Do not merge completed-task chronology into it. |
| `WORK_PROGRESS.md` | Concise milestone log. Keep high-signal 3-5 line entries only; move detailed run output to task docs. |
| `QUESTION_AND_ANALYSIS_LOG.md` | Durable user request / interpreted goal / analysis / follow-up decisions. Do not paste raw conversation. |
| `tasks/active/README.md` | Retained task lookup. Distinguish Active, Paused, Verification-Only, and retained completed records. |
| `tasks/active/STATUS_MANIFEST.md` | Compact workflow-state pointer. Reconcile it with normalized task/phase status and explicit user decisions. |
| `phases/active/*` | Phase board state. Preserve owner, dependency, risk, and integration decisions; do not reopen completed phase work by accident. |

## Merge Rules

- Preserve both sides when they describe distinct completed work, decisions, risks, or verification.
- Do not preserve both sides in the same current-state slot. Resolve state by explicit user decision, normalized task/phase status, manifest, Roadmap, then root log.
- Resolve Product Direction conflicts from explicit approved user decisions; keep unapproved incoming ideas in research/task records.
- Resolve Project Map conflicts against the integrated code and focused architecture/flow/data docs.
- Merge by topic and reading order, not by the conflict marker location.
- Keep chronological logs newest-first when the file already uses newest-first order.
- Keep track-oriented sections grouped by surface, such as Overview, Reference, Operations, Backtest, data, or workflow boundary.
- Preserve completed work in task/phase history, not INDEX or ROADMAP.
- If one side says active work is `none` and another names an active task, resolve it using the state priority above; root logs are handoff evidence only.
- Do not move temporary speculation, failed command output, or long analysis into `docs/`; keep that material in task or phase records.
- Do not rewrite or normalize `registries/`, `saved/`, run history, generated artifacts, or QA screenshots unless the user explicitly asked.

## Natural Reading Check

After editing, read each resolved document top-to-bottom and check:

- A section finishes its topic before switching to another topic.
- A reader can distinguish current state, retained history, and follow-up without treating canonical docs as a changelog.
- Normalized task/phase status, compact manifest, and Roadmap summary agree on Active/Paused/Verification-Only work.
- Root logs summarize; task docs carry details.
- New text does not imply approval, live trading, broker order, provider fetch, registry write, or auto rebalance unless that behavior was actually implemented.

## Validation

- Run `rg -n "^(<<<<<<<|=======|>>>>>>>)" .aiworkspace/note/finance`.
- Run `git diff --name-only --diff-filter=U`.
- Run `git diff --check`.
- Use `rg -n "^State:|Active|Paused|Verification-Only"` across affected task/phase status, task README, manifest, and Roadmap to catch state drift.
- Stage only the coherent merge result and leave `.DS_Store`, QA PNGs, run artifacts, temp CSVs, registries, and saved setups unstaged unless explicitly requested.
