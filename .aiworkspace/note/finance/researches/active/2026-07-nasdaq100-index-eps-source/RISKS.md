# Risks

Status: Active Risks Identified
Last Updated: 2026-07-14

| Risk | Impact | Mitigation |
|---|---|---|
| QQQ proxy와 공식 NDX aggregate 차이 | 공식 P/E처럼 오인 가능 | `public_filing_reconstructed_proxy` 표시, 공식 Nasdaq P/E 명칭 금지, calibration 공개 |
| N-PORT 분기 cadence | 월별 weight가 실제 rebalance/flow를 완전히 반영하지 못함 | 분기 anchor 사이 price drift, special rebalance event 반영 |
| CUSIP/ISIN -> ticker/CIK mapping 누락 | aggregate earnings coverage 저하 | security master와 coverage threshold, unmapped weight 표시 |
| ADR ratio/복수 클래스 | per-share EPS가 거래 증권 단위와 불일치 | issuer-level aggregation 또는 명시적 ADR/class conversion table |
| foreign issuer filing cadence/tag 차이 | TTM actual stale/missing | 20-F/6-K/IFRS taxonomy 별 resolver와 staleness 표시 |
| SEC period-end와 filing availability 차이 | look-ahead 가능 | filing_date/accepted_at 기준 적용, reconstructed/PIT 구분 |
| GuruFocus aggregate methodology 비공개 | S&P/Shiller와 P/E 의미가 다를 수 있음 | source quality 분리, quarterly EPS 교차검증, provider 문의 |
| release-vintage 미제공 | strict PIT 해석 불가 | `과거 시점 재구성`, descriptive history로 제한 |
| API license/retention 제한 | DB 저장/화면 표시 불가 가능성 | 구현 전 Data API Agreement 확인 |
| Free plan Economic Data 권한 불명확 | 무료라고 가정하고 구현하면 collector가 401/403 또는 upgrade gate에 막힘 | free token으로 6778/5870 1회 smoke 후 source 승인 |
| no-account public chart scraping | 약관 위반, schema 변경, 원천/방법론 불명확으로 장기 DB 신뢰성 훼손 | Trendonify/VCP는 제외하고 World PE Ratio도 사람용 교차검증으로만 제한 |
| NDX EPS와 QQQ-unit EPS 혼용 | scenario price가 수십 배 왜곡됨 | direct P/E를 공통 multiple로 쓰고 QQQ EPS는 `QQQ price / P-E`로만 파생; indicator 5870은 NDX identity check 전용 |
| provider별 current P/E 불일치 | 평균·표준편차와 valuation label이 source 선택에 따라 크게 변경 | source contract를 고정하고 12개월 overlap/revision diff를 승인 기준으로 사용 |
| 일반 membership과 API/redistribution 권한 혼동 | 내부 앱 또는 외부 공유가 약관을 벗어날 수 있음 | internal-only 범위를 문서화하고 provider 서면 확인 |
| PE/EPS revision | 과거 결과가 재수집 때 바뀔 수 있음 | collected_at/source_version 저장, revision diff 기록 |
| NDX/P-E date mismatch | derived EPS 오류 | same-date 또는 bounded prior-date join만 허용 |
| P/E zero/null/outlier | log distribution 실패 | positive finite filter와 explicit missing quality |
| FOMC GDP+PCE 설명력 제한 | NDX 실적 성장 과대/과소 추정 | 거시 자체 시나리오/비컨센서스 문구 유지 |
| enterprise provider 비용 | 장기 운영비 증가 | GuruFocus V1 후 실제 품질을 측정하고 upgrade 판단 |
