# Fundamental Source Migration P2 Market Movers EDGAR Annual

## 이걸 하는 이유?

Market Movers 선택 종목 조사 패널은 사용자가 급등/급락 종목을 실제로 조사하는 화면이다. annual financial summary가 조용히 broad yfinance table을 읽으면 최신 EDGAR annual filing이 있어도 출처와 기준일을 오해할 수 있으므로, annual은 EDGAR statement shadow를 우선 사용하고 fallback일 때만 legacy yfinance임을 표시한다.

## Scope

- `build_market_mover_research_snapshot` annual financials를 EDGAR statement shadow first로 전환
- EDGAR annual row가 없을 때만 broad yfinance legacy fallback 사용
- quarterly financials는 10-Q / 10-Q/A statement shadow row만 제한적으로 표시
- 10-K / FY row는 quarterly value로 표시하지 않고 보정 필요 상태로 남김
- Market Movers 기본 지표 card detail에 source / available_at / form / accession evidence 표시

## Non-Scope

- UI에서 SEC 또는 yfinance 직접 fetch
- quarterly synthetic Q4 구현
- AI 요약, 원인 판정, 투자 신호 추가
- DB schema 변경 또는 table drop

## Completion Criteria

- annual EDGAR row가 있으면 legacy broad loader를 호출하지 않는다.
- EDGAR annual missing case는 legacy fallback임을 payload에 남긴다.
- quarterly 10-K/FY row는 분기 지표처럼 표시하지 않는다.
- Browser QA에서 selected-symbol research snapshot source strip이 desktop/narrow viewport에서 확인된다.
