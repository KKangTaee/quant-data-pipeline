# Portfolio Monitoring Position Events V1 Notes

## Confirmed Decisions

- 실제 체결 단가는 사용자가 입력하고 해당일 DB 종가는 참고값으로만 표시한다.
- 추가매수는 외부 입금, 일부매도는 외부 출금이다.
- 매도대금은 group 내부 cash로 유지하지 않는다.
- 원본과 정정 근거를 보존하는 append-only event revision chain을 사용한다.
- 거래 수정·취소도 물리 삭제나 payload 덮어쓰기를 하지 않는다.
- 일부매도 후 최소 1주를 유지하며 전량매도는 existing tracking-end flow에 남긴다.
- UI는 direct stock fixed-shares item detail의 실제 보유내역 action으로 제공한다.

## Current-State Discovery

- 최초 등록은 direct stock/ETF에 fixed shares를 허용한다.
- 현재 command는 group create/rename, item add/end/reopen만 소유한다.
- current item table은 starting funding/entry와 end fields만 가지며 trade/lot/cashflow row가 없다.
- direct-security lane은 최초 units, split, dividend cash와 daily close만으로 계산한다.
