# Overview Market Interest Analyst Source Board

## 이걸 하는 이유?

사용자는 애널리스트 관심 영역이 실제 단서와 원문 링크를 구분하지 못해 “그냥 URL 열기”처럼 보인다고 지적했다. 이번 작업은 선택 종목 1개를 버튼으로 조회했을 때, 어떤 출처가 구조화되어 화면에 표시됐고 어떤 출처는 원문 교차확인만 가능한지 명확히 보여주는 UX 개선이다.

## 범위

- Overview > Market Movers > 시장 관심 > 애널리스트 관심.
- yfinance/Yahoo는 세션 전용 구조화 단서로 표시한다.
- MarketWatch, WSJ Markets, Nasdaq은 자동 수집 없이 원문 교차확인 상태로 표시한다.
- 전체 기업 일괄 분석, 추천/점수화/매수매도 신호, article/report body 저장, 신규 DB schema, 크롤러 추가는 제외한다.

## 단계

1. 읽기 모델에 출처별 상태 카드(`source_cards`)를 추가한다.
2. 화면에서 `출처별 확인 상태` 보드를 항상 보이게 한다.
3. 기존 action/target/의견 분포 테이블은 보드 아래 증거로 유지한다.
4. 검증 후 generated QA 스크린샷은 커밋하지 않는다.

## 완료 조건

- 애널리스트 관심 첫 화면에서 구조화 조회와 원문 교차확인 출처가 구분된다.
- MarketWatch/WSJ/Nasdaq은 크롤링이 아니라 원문 확인 상태임이 보인다.
- 기존 selected-symbol explicit-button 흐름과 보수적 product boundary가 유지된다.
