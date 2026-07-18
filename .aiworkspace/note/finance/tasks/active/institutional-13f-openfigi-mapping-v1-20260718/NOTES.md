# Institutional 13F OpenFIGI Mapping V1 Notes

## Current DB Evidence

- `institutional_13f_cusip_symbol_map`: 5,122 rows, 4,965 distinct CUSIPs, 3,945 symbols.
- all current rows use `source=asset_profile_name_match`.
- Duquesne latest accession: `0001536411-26-000004`, report period `2026-03-31`.
- Duquesne current raw exact join: 70 holdings, 5 mapped, no direct `holding_symbol` rows.
- CUSIP-only candidate audit:
  - exact issuer match: 5.
  - one symbol but issuer-name mismatch: 10.
  - multiple symbols: 1.
  - no candidate: 54.

## Legacy Mapping Quality Finding

현재 legacy name-match table에는 CUSIP-only로 사용하면 위험한 row가 있다.

- `58733R102` MercadoLibre holding에 legacy `AUR` candidate가 존재한다.
- `74743L100` Qnity holding에 legacy `AWI` candidate가 존재한다.
- `46137V357`에는 `RSP`, `RSPG`, `AVGO`가 함께 존재한다.

따라서 loader의 issuer exact-name guard를 단순 제거하면 안 된다. OpenFIGI accepted source precedence를 새로 두고 legacy source는 기존 exact-name fallback으로만 사용한다.

## Actual OpenFIGI Probe

- endpoint: OpenFIGI v3 mapping.
- authentication: none.
- filters: `exchCode=US`, `marketSecDes=Equity`.
- observed anonymous limit header: 25 requests.
- Duquesne: 68 distinct identifiers, 68 one-ticker results, 0 multi, 0 no-match.
- alphabetic identifiers require `ID_CINS`:
  - `N62509109` -> `NAMS`.
  - `H1467J104` -> `CB`.
- sample numeric mappings:
  - `632307104` -> `NTRA`.
  - `457669307` -> `INSM`.
  - `874039100` -> `TSM`.
  - `464286400` -> `EWZ`.
  - `46137V357` -> `RSP`.

## Scope Counts

- code/DB curated manager set: 12 managers.
- curated latest holdings: about 1,244 distinct identifiers.
- all latest managers: about 31,215 distinct identifiers.
- all stored holdings: about 33,654 distinct identifiers.

V1 initial backfill is curated managers. Full-universe expansion uses the same path after V1 correctness and provider pacing are verified.

## Implemented Contract

- `institutional_13f_identifier_resolution` is a current-state provider table separate from the legacy map.
- Incoming provider errors preserve the previous normal resolution while updating attempt evidence.
- Loader order is OpenFIGI mapped/ambiguous gate, grouped legacy exact issuer-name single symbol, then unresolved/service curated fallback.
- Reverse lookup unions provider mappings before legacy rows and deduplicates CUSIPs.
- Normal Institutional Portfolios render is DB-only; provider access occurs only through the explicit Ingestion action.

## Actual Backfill And Coverage

- curated managers: 12.
- identifiers requested/written: 1,244 / 1,244.
- result: 1,195 mapped, 49 unmapped, 0 ambiguous, 0 errors.
- API key: not used.
- Berkshire: 19/29 → 29/29 mapped, 98.6072% → 99.9999% mapped weight.
- Bridgewater: 86/993 → 985/993 mapped, 21.0227% → 99.8952% mapped weight.
- Duquesne: 5/70 → 70/70 mapped, 6.6579% → 99.9999% mapped weight.
- representative accepted mappings: NTRA, INSM, TSM, NAMS.
- prior unsafe legacy candidates are now owned by provider decisions: `58733R102→MELI`, `74743L100→Q`, `46137V357→RSP`.
