# Risks

- canonical cleanup은 authoritative XLS capture에만 허용해야 한다.
- immutable PIT rows를 canonical cleanup 대상으로 포함하면 안 된다.
- cleanup과 UPSERT가 한 transaction이 아니면 중간 실패 시 AAII recent window가 비어 보일 수 있다.
- official workbook fetch가 성공하기 전에 기존 canonical rows를 삭제하면 안 된다.

