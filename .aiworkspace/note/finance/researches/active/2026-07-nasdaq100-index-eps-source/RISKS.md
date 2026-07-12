# Risks

Status: Active Risks Identified
Last Updated: 2026-07-12

| Risk | Impact | Mitigation |
|---|---|---|
| GuruFocus aggregate methodology 비공개 | S&P/Shiller와 P/E 의미가 다를 수 있음 | source quality 분리, quarterly EPS 교차검증, provider 문의 |
| release-vintage 미제공 | strict PIT 해석 불가 | `과거 시점 재구성`, descriptive history로 제한 |
| API license/retention 제한 | DB 저장/화면 표시 불가 가능성 | 구현 전 Data API Agreement 확인 |
| PE/EPS revision | 과거 결과가 재수집 때 바뀔 수 있음 | collected_at/source_version 저장, revision diff 기록 |
| NDX/P-E date mismatch | derived EPS 오류 | same-date 또는 bounded prior-date join만 허용 |
| P/E zero/null/outlier | log distribution 실패 | positive finite filter와 explicit missing quality |
| FOMC GDP+PCE 설명력 제한 | NDX 실적 성장 과대/과소 추정 | 거시 자체 시나리오/비컨센서스 문구 유지 |
| enterprise provider 비용 | 장기 운영비 증가 | GuruFocus V1 후 실제 품질을 측정하고 upgrade 판단 |
