# 2026-05 UI Platform Research Plan

## 이걸 하는 이유?

현재 finance 프로젝트는 Streamlit 기반으로 빠르게 제품 흐름을 구현해 왔다. Backtest Analysis, Practical Validation, Final Review, Selected Portfolio Dashboard까지 핵심 workflow는 만들어졌지만, 향후 상용 수준의 UX, API 분리, 다중 사용자, 고급 차트, 비동기 job 처리까지 염두에 두면 Streamlit만으로 계속 확장하는 것이 맞는지 판단이 필요하다.

이번 리서치의 목적은 다음 결정을 돕는 것이다.

| 질문 | 판단 기준 |
| --- | --- |
| Streamlit을 계속 주 UI로 둘 것인가? | 현재 사용 목적이 내부 연구/운영 콘솔인지, 외부 사용자용 제품인지 |
| Python quant engine과 UI를 분리할 것인가? | 기존 runtime / registry / DB 경계를 API 계약으로 안정화할 수 있는지 |
| React / Next.js를 도입할 것인가? | 실제로 필요한 화면이 고급 interaction, deep link, responsive UI, product polish를 요구하는지 |
| 어떤 기능을 먼저 만들 것인가? | 현행 구조 변경 위험 대비 사용자 가치와 검증 가능성 |

## Scope

포함한다.

- 현재 `finance` 프로젝트의 웹 UX/UI 구조와 약점 분석
- Streamlit 유지, Streamlit custom component, Dash, FastAPI + Next.js/React 조합 비교
- 유사 quant / portfolio / data app 서비스의 기능 패턴과 UI 패턴
- 기능 후보, 우선순위, 추천 architecture direction

포함하지 않는다.

- 실제 프론트엔드 구현
- live trading, broker order, 자동 rebalance 기능 설계
- DB schema migration 상세안
- 특정 클라우드 배포 벤더 결정

## Method

1. Local project audit
   - durable docs와 app/web 구조를 확인한다.
   - Streamlit coupling, session state, runtime boundary, registry boundary를 확인한다.
2. External benchmark
   - 공식 문서/제품 페이지를 우선한다.
   - 최신성이 필요한 자료는 2026-05-14 기준으로 웹 확인한다.
3. Opportunity synthesis
   - impact / effort / risk / confidence / product fit 기준으로 후보를 점수화한다.
   - 즉시 실행할 수 있는 단계와 parking lot을 분리한다.

## Outputs

| File | Role |
| --- | --- |
| `CURRENT_PROJECT_AUDIT.md` | 현재 기능, 구조, 강점, 약점 |
| `BENCHMARKS.md` | 유사 서비스/프레임워크 벤치마크 |
| `UI_PATTERNS.md` | 기능 패턴과 UI 패턴 |
| `FEATURE_CANDIDATES.md` | 추가 기능 후보와 우선순위 |
| `RECOMMENDATION.md` | 최종 추천 방향과 단계별 실행안 |
| `SOURCES.md` | 웹/로컬 출처 |
| `RISKS.md` | 미확인 사항과 리스크 |

## Working Assumptions

- 이 프로젝트의 핵심 가치는 live trading이 아니라 evidence-first quant research workflow다.
- Quant engine, data ingestion, factor/backtest/validation logic은 Python에 남긴다.
- UI 플랫폼 변경은 기존 workflow를 한 번에 다시 쓰는 방식이 아니라, API boundary와 read-only pilot부터 시작한다.
- Streamlit은 당장 폐기 대상이 아니라 내부 ops / research console로 계속 가치가 있다.
