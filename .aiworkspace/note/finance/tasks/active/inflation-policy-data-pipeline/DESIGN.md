# Inflation Policy Data Pipeline Design

## Source And Storage Boundary

- FRED/ALFRED: revision-aware macro/rates observations
- BEA: PCE component breadth by stored release
- Federal Reserve: anonymous SEP distributions and policy decisions
- New York Fed: ACM term premium collected vintage only
- MySQL `finance_meta`: raw normalized rows, artifacts, snapshots and resistance definitions

Every new model read filters `released_at <= as_of_at`. A null `released_at` is ineligible and
does not fall back to realtime or observation dates.

## Schema Unit

The first implementation unit adds six result/definition tables and a nullable released-at
column to the shared macro vintage table. Table business keys preserve release/as-of identity.

