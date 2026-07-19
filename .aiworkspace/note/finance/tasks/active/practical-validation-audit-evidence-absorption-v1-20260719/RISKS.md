# Risks

## Closed Risks

- replay failure에서 actual period가 없으면 compact projection은 `-`를 반환한다.
- validation/replay ids와 limiting symbols는 `overflow-wrap: anywhere`와 760px 단일 열로 검증했다.
- page boundary test로 raw renderer만 제거하고 builder/save/handoff에 source/replay/validation 전달은 보존했다.
- source와 generated production asset은 같은 implementation commit에 포함한다.

## Out Of Scope

- Registry row shape / migration
- Replay engine / validation threshold 변경
- JSON download / audit export workflow
- Final Review / Monitoring UI 변경
- Provider / DB schema 변경
