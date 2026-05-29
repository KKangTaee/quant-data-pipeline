# Concentration / Overlap / Exposure Contract V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Proxy-only evidence appears ready | 실전투자 가능성 판단이 과신됨 | provider missing / partial coverage를 `NEEDS_INPUT` 또는 `REVIEW`로 고정 |
| Contract duplicates existing diagnostics | 화면이 반복적으로 보일 수 있음 | contract는 summary / ownership layer, diagnostics는 detail layer로 둔다 |
| Selected-route gate changes too early | 11-5 scope를 침범 | 11-2는 gate-ready contract만 만들고 gate enforcement는 하지 않는다 |
