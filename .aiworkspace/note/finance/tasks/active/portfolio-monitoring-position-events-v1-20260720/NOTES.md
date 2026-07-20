# Portfolio Monitoring Position Events V1 Notes

## Confirmed Decisions

- 거래일 DB 종가를 execution price 기본값으로 자동 입력하고 사용자가 실제 체결가로 수정할 수 있다.
- 저장 시 입력 당시 reference close와 `db_close_default` / `manual_override` 구분을 함께 보존한다.
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

## Implemented Contract

- `monitoring_security_position_event`는 `create/replace/void` revision을 append-only로 저장하고 terminal revision만 계산에 반영한다.
- `position_events.py`가 eligibility, terminal chain integrity, split-first quantity sequence와 audit row를 소유한다.
- command layer는 optimistic expected revision과 command fingerprint로 duplicate/retry를 제어하고, 저장 직전 전체 후속 거래를 재검증한다.
- valuation lane은 추가매수 `수량 × 체결가 + 수수료`를 입금, 일부매도 `수량 × 체결가 - 수수료`를 출금으로 반영하며 매도 순대금이 0 이하인 입력을 거부한다.
- workspace schema는 `portfolio_monitoring_workspace_v2`다. group KPI는 gross contribution/withdrawal과 `current + withdrawal - contribution` 손익을 표시한다.
- React `보유내역`은 eligible item에서만 action을 보이고 거래 원장의 superseded/voided row를 감사 이력으로 유지한다.
- 거래 수정 중인 일부매도는 현재 수량만으로 화면에서 차단하지 않는다. 원거래가 이미 현재 수량에 반영됐으므로 서버가 수정 시점부터 후속 이력을 전체 재생해 최소 1주 규칙을 판정한다.
- 선택 종목 보유내역의 수량·현금흐름·평가금액은 그 종목의 `latest_usable_date` 기준으로 묶고 날짜를 표시한다. 그룹 합산 지표의 공통 기준일은 별도 계약이다.

## QA Finding

- Browser QA 첫 실행에서 Streamlit rerun이 내용은 같지만 identity가 다른 editor recovery object를 전달할 때 `awaiting_close` 상태가 다시 적용돼 DB 종가 기본값이 지워지는 문제를 재현했다.
- recovery payload 전체 필드로 만든 stable key가 바뀔 때만 복구하도록 수정했다. 이후 `$164` 자동 입력·`종가 기본값`, manual price 변경·`수동 체결가`를 실제 브라우저에서 확인했다.
- 최종 코드 리뷰에서 거래 수정의 화면 선검증과 선택 종목/그룹 기준일 혼합을 발견했다. replacement sell은 서버 전체 이력 검증으로 일원화하고 선택 종목 summary에 자체 기준일·평가금액을 추가했다.
