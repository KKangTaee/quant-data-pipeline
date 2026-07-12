# S&P 500 EPS Source Benchmark

Status: Active
Access date: 2026-07-12

## 조사 질문

그래프 2의 `현재 TTM EPS -> FOMC SEP 성장률 -> 예상 EPS -> 적정 SPX 밴드` 흐름을 S&P Global 자동 다운로드 없이 운영할 수 있는가?

## 결론

가능하다. 현재 범위는 시장 컨센서스 EPS를 직접 수집하는 기능이 아니라 현재 TTM EPS를 기준으로 SEP 성장률을 적용하는 자체 추정 모델이다. 따라서 무료 자동 수집 기준값은 Shiller 월별 earnings의 최신 완료 분기 값을 사용하고, S&P 공식 As-Reported EPS는 사용자가 확보한 파일이 있을 때 품질을 높이는 우선 소스로 둔다.

## 비교

| 소스 | 데이터 성격 | 자동화 | 비용/접근 | 프로젝트 적용 | 근거 수준 |
| --- | --- | --- | --- | --- | --- |
| Robert Shiller data | 월별 가격·earnings. 분기별 S&P 4분기 합계를 월별 선형 보간 | 가능 | 무료 공개 파일 | 그래프 1 및 그래프 2의 TTM proxy 기본값 | documented |
| S&P Dow Jones Indices Index Earnings | S&P 500 공식 분기별 실제/추정 index earnings | 현재 일반 서버 요청은 403, 정식 자동 전달은 라이선스 경로 검토 필요 | 공개 웹 파일 또는 라이선스 | 파일이 등록되면 가장 우선하는 actual EPS | observed/documented |
| LSEG I/B/E/S Global Aggregates | 지수 수준 bottom-up actual·consensus·forecast aggregates | API/파일/SFTP 등 제품 계약 범위에서 가능 | 유료 라이선스 | 향후 시장 컨센서스 NTM EPS 기능의 production-grade 후보 | documented |
| FactSet Earnings Insight / Estimates | S&P 500 forward 12-month EPS·P/E 및 컨센서스 분석 | 공개 보고서 파싱은 형식·URL 안정성이 낮음. 정식 feed는 제품 계약 필요 | 일부 공개 보고서, 정식 데이터 유료 | 보조 비교값 또는 유료 연동 후보. 현재 핵심 수집원으로는 부적합 | documented/inferred |

## 적용 원칙

1. `official_actual`: 사용자가 등록한 S&P 공식 actual 4분기 합계가 있으면 사용한다.
2. `shiller_ttm_proxy`: 공식 actual이 없으면 Shiller 최신 완료 분기 earnings를 사용한다.
3. `consensus_ntm`: LSEG/FactSet 계약이 생기면 SEP 자체 예상치와 별도 선으로 비교한다.
4. SEC 개별 기업 실적을 직접 합산하는 방식은 지수 divisor, 구성 종목 변경, share class, 가중 방식과 시점 정합성 문제로 S&P index EPS의 단순 대체재로 취급하지 않는다.

## 한계

- Shiller earnings는 월별로 보간되므로 S&P 공식 분기별 release vintage와 동일하지 않다.
- SEP 기반 EPS는 거시 시나리오 추정치이며 애널리스트 컨센서스 NTM EPS가 아니다.
- FactSet 공개 보고서 URL/본문 파싱은 지원 API 계약이 아니므로 운영 수집의 단일 의존점으로 두지 않는다.
