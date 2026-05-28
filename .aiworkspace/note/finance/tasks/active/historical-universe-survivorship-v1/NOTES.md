# Notes

## 2026-05-28

- Current listing snapshot은 앞으로의 lifecycle 관찰에는 유용하지만 과거 backtest 기간 전체 survivorship control을 증명하지는 않는다.
- PASS 기준은 requested period를 덮는 historical listing / delisting feed / computed snapshot lifecycle evidence다.
- Workflow JSONL에는 compact audit evidence만 남기고 lifecycle source row는 DB에 둔다.
