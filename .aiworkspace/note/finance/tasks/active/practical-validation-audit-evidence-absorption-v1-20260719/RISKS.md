# Risks

## Active Risks

- replay failure payload는 actual period가 없을 수 있다. compact projection은 `-`로 안전하게 표현해야 한다.
- long validation/replay ids와 limiting symbol list가 760px overflow를 만들 수 있다.
- raw disclosure 제거 과정에서 source/replay/validation object의 save/handoff 전달까지 제거하지 않도록 page boundary test가 필요하다.
- build asset hash가 변경되므로 source와 generated production asset을 같은 implementation commit에 포함한다.

## Out Of Scope

- Registry row shape / migration
- Replay engine / validation threshold 변경
- JSON download / audit export workflow
- Final Review / Monitoring UI 변경
- Provider / DB schema 변경
