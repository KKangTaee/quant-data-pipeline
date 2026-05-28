# Risks

- Some old validation rows may not carry enough runtime metadata to prove cost application. The audit should surface that as `REVIEW` or `NEEDS_INPUT`.
- This task does not improve the underlying strategy simulator; it only makes existing realism evidence visible.
- Weighted portfolio / saved mix source rows can lose component-level cost application detail. The audit will therefore be conservative until component metadata is carried through more completely.
