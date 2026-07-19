# Portfolio Monitoring Chart Zoom / Pan V1 Plan

Status: Design approved; written spec review pending
Last Updated: 2026-07-19

## 이걸 하는 이유?

선택한 미국 주식·ETF의 최신 120거래일을 한 화면에 모두 표시하면 candle과 line의 밀도가
높아진다. 사용자가 관심 기간을 확대하고 인접 기간으로 이동하면서도 기존 OHLCV hover를
유지할 수 있도록 client-side viewport를 추가한다.

## Scope

- 선택 direct stock/ETF 가격 차트의 client-side zoom/pan
- cursor-anchored wheel zoom, horizontal pointer drag, 버튼 zoom/reset
- line/candle 간 viewport 공유와 선택 종목 변경 시 초기화
- desktop pointer QA와 420px 버튼-only QA

## Out Of Scope

- 종합 가치곡선과 selected strategy 가치곡선의 zoom/pan
- DB/API 추가 조회, 120거래일 초과 history, 기간 selector
- 모바일 pinch 또는 touch drag
- intraday, indicator, drawing tool

## Tentative Roadmap

1. viewport pure helper와 경계 테스트
2. wheel/drag/control UI와 production bundle
3. regression, desktop/mobile Browser QA, durable 문서 정렬

## Stop Condition

최소 15거래일까지 확대되고, 커서 anchor와 pan clamp가 유지되며, drag와 hover가 충돌하지
않고, 전체 보기 복귀와 모바일 버튼 조작이 검증되면 완료한다.
