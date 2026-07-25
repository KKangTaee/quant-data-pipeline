# Risks

Last Updated: 2026-07-25

## Open Risks

- 사용자가 대화에 제공한 API key는 chat history에 노출되었으므로 설정 완료 후 rotation이
  권장된다.
- weekday target은 미국 공휴일을 구분하지 않는다. provider에 신규 release가 없어도 PIT
  cutoff 날짜로 materialize될 수 있다는 의미를 UI가 과장하지 않아야 한다.
- shared Git exclude는 로컬 보호이고 다른 clone에 전파되지 않으므로 tracked
  `.gitignore`도 함께 필요하다.
- actual refresh는 provider/network 및 17-series 응답 상태에 의존한다.
- 기존 unrelated dirty files가 많으므로 stage/commit 대상을 명시적으로 제한해야 한다.

## Mitigations

- secret-aware local write와 tracked diff scan을 수행한다.
- `override=False`, last-good preservation, persisted postcondition을 tests로 고정한다.
- monthly history count/checksum을 actual refresh 전후 비교한다.
- generated artifact와 unrelated files를 stage하지 않는다.
