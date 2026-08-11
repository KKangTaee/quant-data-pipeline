# Design

Approved design: [RTDSM history expansion](../../../../../../docs/superpowers/specs/2026-08-12-economic-cycle-rtdsm-history-design.md)

Implementation plan: [RTDSM history plan](../../../../../../docs/superpowers/plans/2026-08-12-economic-cycle-rtdsm-history.md)

`finance/data/philadelphia_rtdsm.py`가 공식 workbook download, 계약 검증, wide-to-long
normalization과 batch UPSERT를 소유한다. `finance/loaders/economic_cycle_realtime.py`는
RTDSM source만 읽는다. `finance/economic_cycle_realtime_history.py`는 DB row를 장기
4지표 state와 sample/parity audit로 바꾸며 production snapshot을 수정하지 않는다.
