# Design

승인된 명세: `docs/superpowers/specs/2026-07-18-sp500-actual-eps-registration-design.md`

실행 계획: `docs/superpowers/plans/2026-07-18-sp500-actual-eps-registration.md`

흐름은 `S&P 공식 XLSX -> Workspace Ingestion -> canonical parser/importer -> finance_meta.sp500_index_earnings -> PIT loader -> Economic Cycle`이다. Shiller proxy는 공식 actual로 분류하지 않는다.
