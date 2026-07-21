# Portfolio Monitoring Initial Setting Correction V1 Notes

- 기존 Position Events V1 설계는 `최초 수량 정정`에서 시작일과 entry close를 고정한다고 명시한다.
- 추가매수·일부매도 editor는 이미 거래일 변경과 exact-date close refill을 지원한다.
- 최초 등록은 requested date와 effective market date를 분리하므로 정정도 같은 날짜 의미를 유지해야 한다.
- group curve는 item의 requested/effective start를 직접 참조하는 구간이 있어 projected initial contract로 함께 전환해야 한다.
- legacy initial correction row와 command/effect identity는 호환 경계로 유지한다.
