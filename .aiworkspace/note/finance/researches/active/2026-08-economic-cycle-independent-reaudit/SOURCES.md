# Sources

Accessed: 2026-08-03

## Local Evidence

- `finance/economic_cycle_catalog.py`
- `finance/economic_cycle_features.py`
- `finance/economic_cycle_labels.py`
- `finance/economic_cycle_model.py`
- `finance/economic_cycle_validation.py`
- `finance/economic_cycle_pipeline.py`
- `finance/loaders/economic_cycle.py`
- `app/services/overview/economic_cycle.py`
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- `finance_meta.economic_cycle_model_artifact`: read-only exact model inspection
- `finance_meta.economic_cycle_snapshot`: read-only current / replay inspection
- `finance_meta.macro_series_vintage_observation`: read-only PIT reconstruction

## Reproductions

- 2026-08-03 current / intramonth snapshot payload read
- 1959-2026 feature panel rebuilt with current loader and label code
- 121 stored replay months compared with rule-defined phase
- exact artifact validation metrics and baseline metrics decoded
- economic-cycle test set: 172 passed, 3 unrelated dependency deprecation warnings

## Official / Primary References

- NBER, Business Cycle Dating:
  https://www.nber.org/research/business-cycle-dating
- NBER, Business Cycle Dating Procedure FAQ:
  https://www.nber.org/research/business-cycle-dating/business-cycle-dating-procedure-frequently-asked-questions
- Federal Reserve Bank of Chicago, Background on the CFNAI:
  https://www.chicagofed.org/-/media/publications/cfnai/background/cfnai-background-pdf.pdf
- OECD, System of Composite Leading Indicators:
  https://www.oecd.org/content/dam/oecd/en/data/methods/OECD-System-of-Composite-Leading-Indicators.pdf
- Federal Reserve Bank of Philadelphia, ADS Business Conditions Index:
  https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/ads
- Federal Reserve Bank of New York, Weekly Economic Index:
  https://www.newyorkfed.org/research/policy/weekly-economic-index
