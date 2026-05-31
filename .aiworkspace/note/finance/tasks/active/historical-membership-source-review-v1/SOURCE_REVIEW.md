# Historical Membership Source Review V1

Status: Complete
Created: 2026-05-28

## Summary

완전한 historical universe membership을 무료 / 공식 source 하나로 바로 확보하는 경로는 확인되지 않았다.
가장 풍부한 corporate action source는 Nasdaq Daily List지만, 현재 확인 기준으로 구독 / 승인형 product다.

따라서 Phase 8의 다음 구현은 유료 Daily List가 아니라 무료 공식 current snapshot source를 DB에 적재해 forward lifecycle evidence를 쌓는 방향이 적절하다.

## Source Matrix

| Source | Access | Evidence Type | Strength | Limitation | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Nasdaq Daily List | Subscription / approval | new listing, delisting, symbol change, name change, dividends, historical corporate actions | 가장 강함. Nasdaq 설명상 historical corporate action data가 1999년부터 제공됨 | 월 구독 / secured FTP or website / agreement 필요. 무료 API 우선 원칙과 맞지 않음 | Phase 8 free-source path에서는 parking lot |
| Nasdaq Symbol Directory `nasdaqlisted.txt` | Public current file | current Nasdaq-listed securities | 공식 public current snapshot. 하루 중 주기적으로 갱신됨 | historical event feed가 아님. disappearance만으로 delisting proof 아님 | 다음 구현 1순위 |
| Nasdaq Symbol Directory `otherlisted.txt` | Public current file | current other-exchange listed securities | NYSE / NYSE Arca / NYSE American / CBOE 등 cross-exchange current snapshot을 보강할 수 있음 | historical event feed가 아님. exchange code 해석 필요 | 다음 구현 1순위에 포함 |
| SEC `company_tickers_exchange.json` | Public SEC file | current CIK / ticker / exchange association | CIK bridge와 exchange cross-check에 유용 | SEC 문서상 accuracy / scope를 보장하지 않음. historical membership이 아님 | 다음 구현 2순위 보조 source |
| SEC Submissions API | Public SEC API | CIK metadata, current ticker / exchange, former names, filing history | Form 25 / former names / CIK continuity 확인에 유용. API key 없음 | ticker change event feed가 아니며 complete membership source가 아님 | Form 25는 이미 사용. bulk / formerNames는 후속 |
| NYSE Listings Directory | Public web page | current NYSE listing directory | 현재 listing 확인 가능 | browser-oriented page. historical event feed가 아님. 기존 NYSE CSV flow가 이미 있음 | 기존 path 유지. 필요 시 보조 |

## Official Source References

| Source | URL | Review Note |
| --- | --- | --- |
| Nasdaq Daily List product description | `https://nasdaqtrader.com/Trader.aspx?id=DailyListPD` | Corporate actions are covered, but access is subscription / approval based |
| Nasdaq Daily List complete specification | `https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/dlcompletespec.pdf` | Confirms rich event fields such as delisting reason and symbol-change related fields |
| Nasdaq Symbol Directory definitions | `https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs` | Defines current public symbol directory files |
| Nasdaq current listed file | `https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt` | Public current Nasdaq-listed snapshot |
| Nasdaq current other-listed file | `https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt` | Public current other-exchange listed snapshot |
| SEC EDGAR API documentation | `https://www.sec.gov/edgar/sec-api-documentation` | Submissions API and bulk archive behavior |
| SEC company ticker exchange file | `https://www.sec.gov/files/company_tickers_exchange.json` | Current CIK / name / ticker / exchange association |

## Key Findings

1. Nasdaq Daily List is the best event source, but not the first implementation target.
   - It covers corporate action events such as new listings, delistings, symbol changes, and name changes.
   - It is sold as a monthly subscription with secured access and required forms.
   - It should not be treated as a free source.

2. Nasdaq Symbol Directory is free enough for current snapshot evidence.
   - `nasdaqlisted.txt` and `otherlisted.txt` are current symbol directory files.
   - They are updated during the day and include file creation time.
   - They can improve current listing coverage and start a forward snapshot record.

3. SEC is useful for identity, not complete membership.
   - `company_tickers_exchange.json` maps CIK, name, ticker, and exchange in a current association file.
   - SEC Submissions API gives company metadata, former names, current tickers / exchanges, and filing history.
   - SEC explicitly says the ticker association files are periodically updated but does not guarantee accuracy or scope.

4. Current snapshot ingestion must remain conservative.
   - A current listing row is `event_type=listing_observed`, `coverage_status=partial`.
   - Missing from a current file is not automatically delisting proof.
   - Future computed lifecycle evidence should require repeated snapshots and source contract.

## Recommended Next Implementation

Open `symbol-directory-snapshot-ingestion-v1`.

Scope:

- Add `finance/data/symbol_directory.py`.
- Fetch Nasdaq official public files:
  - `https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt`
  - `https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt`
- Normalize rows into `nyse_symbol_lifecycle` as:
  - `source_type=current_listing_snapshot`
  - `coverage_status=partial`
  - `event_type=listing_observed`
  - `event_date=file_creation_date or collection date`
- Store only DB lifecycle rows.
- Add loader / contract tests as needed.
- Do not mark survivorship PASS from these rows alone.

Expected value:

- Broader official current listing coverage than NYSE-only CSV.
- Foundation for future `computed_from_snapshots` evidence.
- No new JSONL / memo / preset storage.

## Parking Lot

- Nasdaq Daily List can be reconsidered only if the user accepts subscription / agreement handling.
- SEC `submissions.zip` can later make Form 25 and former-name collection more scalable.
- A future snapshot-diff task can compare repeated current snapshots, but absence needs conservative interpretation.
