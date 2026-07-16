# Economic Cycle Gold / Dollar Price Confirmation V1 Notes

- `GC=F` local daily coverage: 2021-06-01 through 2026-07-16, 1,294 rows at discovery time.
- Existing `UUP` proxy stops at 2026-06-26 and is not selected as the primary dollar source.
- `DX-Y.NYB` provider probe returned 124 daily rows for the latest six months and maps to ICE DX futures context.
- Gold was negative over 5/21/63 sessions at discovery; dollar was negative over 5 sessions but positive over 21/63 sessions. The UI must show these windows rather than flattening them into one claim.
- Actual read model on 2026-07-17 uses economic date 2026-06-30 and price date 2026-07-16.
- Gold is macro `우호` but price `하락 확인`: 1w -3.1%, 1m -4.9%, 3m -15.9%, therefore `배경과 가격 불일치`.
- Dollar is macro `부담` but price `상승 확인`: 1w -0.2%, 1m +1.1%, 3m +2.7%, therefore `배경과 가격 불일치`.
- The dollar label is determined by 1m and 3m confirmation; the negative 1w move remains visible rather than being discarded.
