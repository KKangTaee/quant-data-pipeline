# Historical Membership Source Review V1 Runs

Status: Complete
Created: 2026-05-28

## Commands

```bash
curl -L --max-time 20 -A 'quant-data-pipeline research contact@example.com' -s 'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt' | sed -n '1,8p'
```

Result: public current file returned pipe-delimited Nasdaq-listed rows.

```bash
curl -L --max-time 20 -A 'quant-data-pipeline research contact@example.com' -s 'https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt' | sed -n '1,8p'
```

Result: public current file returned pipe-delimited other-exchange rows.

```bash
curl -L --max-time 20 -A 'quant-data-pipeline research contact@example.com' -s 'https://www.sec.gov/files/company_tickers_exchange.json' | head -c 600
```

Result: SEC current CIK / name / ticker / exchange JSON returned.

```bash
curl -L --max-time 20 -A 'quant-data-pipeline research contact@example.com' -s 'https://data.sec.gov/submissions/CIK0000320193.json' | head -c 900
```

Result: SEC submissions JSON returned current entity metadata.

```bash
git diff --check
```

Result: passed.
