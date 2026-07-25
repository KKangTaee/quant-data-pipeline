# Design

- canonical truth: AAII official XLS `Reported Date`
- recent refresh scope: incoming complete XLS minimum~maximum date
- canonical action: incoming date set 외 AAII canonical row 삭제 후 UPSERT
- immutable action: 기존 source capture snapshot/batch append-only 유지
- HTML fallback: 현재 날짜 보정은 유지하되 canonical window 삭제 권한 없음
- cleanup: existing full-workbook atomic backfill 재사용

