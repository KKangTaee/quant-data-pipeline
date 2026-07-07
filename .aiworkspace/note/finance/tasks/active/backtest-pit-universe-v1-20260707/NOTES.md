# Notes

## Design Notes

- Market cap remains the universe ranking basis because large-cap equity indices generally use market-cap or float-adjusted market-cap families.
- Liquidity is an eligibility / operability layer, not the primary size ranking criterion.
- The first implementation is a DB-built approximate PIT universe. It is materially better than current Top-N replay but not identical to official historical Russell / S&P membership.
