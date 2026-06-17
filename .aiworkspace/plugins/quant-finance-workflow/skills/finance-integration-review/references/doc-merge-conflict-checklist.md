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
| `docs/INDEX.md` | Current pointers and read order. Keep only one current active/latest pointer; preserve older incoming work as recent or retained context. |
| `docs/ROADMAP.md` | Product state and work sequence. Put recent work in chronological or track order; avoid dropping completed task scope and non-goals. |
| `WORK_PROGRESS.md` | Concise milestone log. Keep high-signal 3-5 line entries only; move detailed run output to task docs. |
| `QUESTION_AND_ANALYSIS_LOG.md` | Durable user request / interpreted goal / analysis / follow-up decisions. Do not paste raw conversation. |
| `tasks/active/README.md` | Retained task lookup. Add completed records without implying every folder is active. |
| `tasks/active/STATUS_MANIFEST.md` | Active state source of truth. Keep current active task / latest completed task consistent with README, Roadmap, and Index. |
| `phases/active/*` | Phase board state. Preserve owner, dependency, risk, and integration decisions; do not reopen completed phase work by accident. |

## Merge Rules

- Preserve both sides when they describe distinct completed work, decisions, risks, or verification.
- Do not preserve both sides in the same "current" slot. Pick the real current value, then move the other side to a recent / retained / reference section.
- Merge by topic and reading order, not by the conflict marker location.
- Keep chronological logs newest-first when the file already uses newest-first order.
- Keep track-oriented sections grouped by surface, such as Overview, Reference, Operations, Backtest, data, or workflow boundary.
- If both sides update "Latest completed task", choose the newest completed task that actually exists and has completed status; keep the other as a recent completed record.
- If one side says active work is `none` and another names an active task, verify against task `STATUS.md`, `STATUS_MANIFEST.md`, Roadmap, and root logs before deciding.
- Do not move temporary speculation, failed command output, or long analysis into `docs/`; keep that material in task or phase records.
- Do not rewrite or normalize `registries/`, `saved/`, run history, generated artifacts, or QA screenshots unless the user explicitly asked.

## Natural Reading Check

After editing, read each resolved document top-to-bottom and check:

- A section finishes its topic before switching to another topic.
- A reader can tell which work is current, latest completed, recent completed, retained, or follow-up.
- Cross-document pointers agree on current active phase, current active task, and latest completed task.
- Root logs summarize; task docs carry details.
- New text does not imply approval, live trading, broker order, provider fetch, registry write, or auto rebalance unless that behavior was actually implemented.

## Validation

- Run `rg -n "^(<<<<<<<|=======|>>>>>>>)" .aiworkspace/note/finance`.
- Run `git diff --name-only --diff-filter=U`.
- Run `git diff --check`.
- Use `rg -n "Latest completed task|Current active task|Current active phase"` across Index, Roadmap, task README, and manifest to catch stale pointers.
- Stage only the coherent merge result and leave `.DS_Store`, QA PNGs, run artifacts, temp CSVs, registries, and saved setups unstaged unless explicitly requested.
