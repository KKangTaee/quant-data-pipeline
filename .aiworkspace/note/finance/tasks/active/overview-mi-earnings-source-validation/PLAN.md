# Plan

## 이걸 하는 이유?

2차에서는 earnings row를 provider estimate로 표시했다. 3차에서는 yfinance estimate를 그대로 믿는 대신 무료 alternate source와 cross-check할 수 있는 경로를 만들고, official/company IR parser는 종목별 구현이 필요하다는 한계를 명확히 남긴다.

## Scope

- yfinance earnings calendar row에 persisted `source_type`, `validation_status`, `event_status`를 저장한다.
- Nasdaq earnings calendar free endpoint를 날짜 단위 alternate provider cross-check로 사용한다.
- cross-check 결과에 따라 `cross_checked`, `not_confirmed`, `estimate_only`를 저장한다.
- company IR source는 범용 parser로 붙이지 않고 `company_ir_calendar` future official source candidate로 fallback order에 기록한다.

## Done Criteria

- earnings row가 DB에 `provider_estimate`와 validation status를 저장한다.
- Nasdaq cross-check가 가능한 경우 confidence가 상향되고 raw payload에 source validation 근거가 남는다.
- service contract tests가 yfinance-only와 Nasdaq cross-check case를 검증한다.
