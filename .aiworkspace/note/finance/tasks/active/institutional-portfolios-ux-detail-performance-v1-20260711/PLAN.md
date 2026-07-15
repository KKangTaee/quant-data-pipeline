# Institutional Portfolios UX Detail / Performance V1

## Goal

`Workspace > Institutional Portfolios`를 실제 탐색 화면답게 개선한다. 포트폴리오 선택 / 탭 전환 시 스크롤이 흔들리지 않게 하고, 보유 종목 클릭 후 종목 정보, 가격 차트, 보유 기관 목록, 보유 기관 랭킹, 보고 기준일 이후 가정 성과를 한 흐름 안에서 볼 수 있게 한다.

## 이걸 하는 이유?

현재 화면은 도넛 / holdings / 보유 기관 조회가 각각 따로 움직여 사용자가 "이 종목을 누른 뒤 무엇을 판단할 수 있는지"가 약하다. 또한 이전 filing이 없는 경우 변화 항목이 0으로 보여 계산 오류처럼 보이고, 탭 / manager 변경 때 스크롤이 움직여 실제 사용성이 떨어진다.

## Scope

- React workbench의 탭 / manager rail 스크롤 안정화
- 도넛 우측 holding 클릭 후 selected security detail 제공
- 가격 DB 기반 일봉 / 주봉 / 월봉 chart payload 및 UI
- report period 이후 단순 buy-and-hold 가정 portfolio performance summary
- report period 기준 많이 보유된 종목의 기관 수 랭킹 tab
- 이전 filing 부재 시 변화 board의 비교 불가 메시지
- focused tests, py_compile, npm build, Browser QA, commit

## Out Of Scope

- SEC / 외부 사이트를 UI에서 직접 fetch
- 실시간 추천, 매수 / 매도 신호, broker 연동
- Dataroma / WhaleWisdom / Fintel scraping 구현
- 전 종목 가격 수집 자동 보정

## Stop Condition

테스트와 build가 통과하고, Browser QA에서 포트폴리오 선택 / holding 클릭 / 탭 전환 / 랭킹 tab이 동작하는 것을 확인한 뒤 coherent commit을 만든다.
