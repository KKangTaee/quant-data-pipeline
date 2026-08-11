# Risks

- four-indicator long-history state may not agree sufficiently with the current eight-indicator
  state; the parity gate is therefore independent from sample support.
- RTDSM quarterly unemployment vintages are less fresh than monthly sources.
- workbook structure or metadata can change; parser validation must fail closed.
- full initial history contains many rows, so parser and writer must stream in bounded batches.
- sample gate passage is not model publication approval; chronological baseline and calibration
  gates still remain.
- actual parity failed. Lowering the threshold, inflating monthly rows as independent samples,
  or selecting an indicator combination after seeing the score would create label/model bias.
- the stored RTDSM ledger remains useful research data, but it must not be presented as a
  production forecast or current-cycle replacement while `NO_GO_PARITY` remains.
