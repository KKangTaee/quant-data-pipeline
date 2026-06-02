# Notes

- Existing dashboard already has recheck, comparison, drift, review signal, open issue, provider evidence, and deployment preflight read models.
- Main missing layer is a user-owned monitoring portfolio container that groups selected Final Review rows.
- Existing `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl` is saved mix setup state, so dashboard portfolio state should use a separate file.
- New saved state is `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`; it stores portfolio name / description / selected decision references only and does not rewrite Final Decision V2 rows.
- Browser QA used the current empty selected-pool state, so runtime tests cover add / duplicate / remove / soft delete behavior until a real selected V2 row exists for end-to-end strategy add / scenario execution QA.
