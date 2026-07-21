# Portfolio Monitoring Initial Setting Correction V1 Notes

- 기존 Position Events V1 설계는 `최초 수량 정정`에서 시작일과 entry close를 고정한다고 명시한다.
- 추가매수·일부매도 editor는 이미 거래일 변경과 exact-date close refill을 지원한다.
- 최초 등록은 requested date와 effective market date를 분리하므로 정정도 같은 날짜 의미를 유지해야 한다.
- group curve는 item의 requested/effective start를 직접 참조하는 구간이 있어 projected initial contract로 함께 전환해야 한다.
- legacy initial correction row와 command/effect identity는 호환 경계로 유지한다.
- 유효 초기 계약을 history loader보다 먼저 투영해야 원본 item보다 이른 시작일 정정도 DB 가격 범위에 포함된다.
- 초기 설정 정정 resolver는 item/event chain lock 안에서 다시 실행해 preview와 저장 사이 가격·거래 상태 변화를 검증한다.
- UI save readiness는 item id, requested date, quantity가 모두 최신 `READY` projection과 일치할 때만 성립한다. 수량 변경도 새 initial-capital preview 조회를 요구한다.
- 실제 QA DB에는 기존 event가 0건이었고 optional column만 추가됐다. 사용자 item row와 JSONL은 수정하지 않았다.
