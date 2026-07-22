# Today U.S. Market Session Status V1 Plan

Status: Design Approved
Roadmap: 0/3 implementation stages complete
Last Updated: 2026-07-22

## 이걸 하는 이유?

Today의 시장 판단은 저장된 시장 근거와 포트폴리오를 보여주지만, 사용자가 지금 미국 정규장이 열리기 전인지 진행 중인지 이미 끝났는지는 별도로 계산해야 한다. 첫 화면에서 현재 장 상태와 다음 전환 시간을 바로 보여 주어 시장 자료를 읽는 시간 맥락을 줄인다.

## Goal

Today 상단에서 미국 정규장의 `개장 전 / 장 진행 중 / 정규장 마감 / 휴장` 상태, 뉴욕·한국 현재 시각, 양쪽 시간대의 개장·마감 시각, 다음 전환까지 남은 시간을 확인할 수 있게 한다.

## Scope

- 미국 정규장 09:30–16:00 ET 기준 상태 판정
- 주말, 공식 휴장일, 공식 조기폐장일 반영
- `America/New_York`과 `Asia/Seoul`을 사용한 DST-safe 시간 변환
- React 안에서 갱신되는 현재 시각과 카운트다운
- Today hero 인접 영역의 compact market-session strip
- Python service, typed payload, React presentation, Browser QA

## Out Of Scope

- 프리마켓과 애프터마켓
- 장중 가격, 지수, 거래량 수집
- 거래소별 종목 상태, 거래정지, 서킷브레이커
- broker별 주문 가능 시간
- provider/API 직접 호출

## Tentative Roadmap

1. `1/3차` — 시간·휴장 판정 계약과 RED/GREEN 테스트
2. `2/3차` — Today payload·React 실시간 표시 통합
3. `3/3차` — desktop/mobile Browser QA와 문서 정렬

## Stop Condition

대표 DST/주말/휴일/조기폐장 시나리오가 자동 테스트를 통과하고, actual Today 화면에서 양쪽 시각과 상태·일정·카운트다운이 반응형으로 표시되며 기존 Today 판단·포트폴리오·navigation 계약이 회귀하지 않으면 완료한다.
