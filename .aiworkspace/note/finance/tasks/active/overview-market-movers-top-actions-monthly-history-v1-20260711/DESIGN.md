# Design

## 화면 구조

```text
Market Movers 상단
├─ 필터
├─ 자료 상태
└─ 갱신 action
   ├─ 가격 이력 갱신
   ├─ 유니버스 기준 갱신
   ├─ 화면 새로고침
   └─ 보조 설명 · 버튼 밖 한 줄
```

## Monthly 상태 분류

```text
refreshable gap
└─ 가격 이력 갱신 action 유지

provider available history short
├─ ranking에서는 기존대로 제외
├─ limited_price_history issue 누적
└─ 같은 기간 재수집 action은 숨기고 짧은 이력 안내
```

## Source / storage / consumer

- source: yfinance OHLCV full period window
- raw ledger: `finance_price.nyse_price_history`
- issue evidence: `finance_meta.market_data_issue(issue_type=limited_price_history)`
- consumer: `app/jobs/overview_actions.py` EOD preflight -> Market Movers React payload/UI

과거 가격을 합성하지 않으며, 실제 provider가 제공한 first/latest date와 row count만 compact evidence로 저장한다.
