# Portfolio Monitoring Initial Setting Correction V1 Status

Status: Written design pending user review

- 사용자가 `개별 추적 결과 > 최초 수량 정정`에서 최초 추적 시작일도 변경할 수 있어야 한다고 요청했다.
- 현재 추가매수·일부매도 거래일은 수정 가능하지만 initial correction은 시작일·시작 종가를 의도적으로 고정함을 확인했다.
- 사용자가 append-only 초기 계약 정정 확장 권장안을 승인했다.
- written design은 기존 command/event identity를 호환 유지하면서 requested/effective date와 entry close를 revision에 보존하는 방향이다.
- 다음 action은 사용자 written-spec 확인 후 detailed TDD implementation plan 작성이다.
