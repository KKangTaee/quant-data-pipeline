# Risks

- Fresh end-to-end Practical Validation / Final Review verification may append local registry rows. If needed for proof, treat those JSONL changes as generated workflow artifacts and do not stage unless explicitly requested.
- Browser QA is only needed if UI layout changes materially. Pure service/runtime propagation can be verified with Python checks and focused service snippets.
- No registry or saved row migration was performed. Existing old rows can still lack these fields until they are replayed or rerun naturally.
- UI layout was not materially changed; compare/single forms now add hidden payload contract fields from defaults or prefilled overrides.
