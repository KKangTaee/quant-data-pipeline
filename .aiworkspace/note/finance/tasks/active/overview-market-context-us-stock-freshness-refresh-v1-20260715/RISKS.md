# Overview Market Context US Stock Freshness Refresh V1 Risks

Last Updated: 2026-07-15

## Resolved In V1

1. NYSE holiday/early-close/완료 session 계산은 공용 helper로 합쳤다.
2. Single action은 CIK 없이 profile/price를 먼저 보존하고 SEC만 identity gate 뒤에 실행한다.
3. Refresh 뒤에도 short listing, negative EPS, raw statement gap 같은 구조적 상태는 기존 분석 계약대로 유지한다.
4. Current React에는 single CTA만 남겼고 S&P와 legacy payload compatibility를 테스트로 보존했다.
5. 별도 run/job/row 진단 panel은 추가하지 않았다.

## Residual Risks / Follow-up Boundaries

1. Provider market cap은 authoritative market-cap market date 대신 `last_collected_at`을 제공하므로 V1 profile basis는 가격과 7일 정렬하는 operational proxy다.
2. SEC CIK가 없고 실제 statement gap도 있는 종목은 market data만 partial-success 후 SEC identity gap이 남는다. 자동 identity 복구는 별도 승인 범위다.
3. 저장소 monolithic unittest는 Streamlit singleton reimport 격리 오류 154건과 unrelated assertion 4건이 남아 있다. 이번 focused contract는 독립 실행에서 통과한다.
