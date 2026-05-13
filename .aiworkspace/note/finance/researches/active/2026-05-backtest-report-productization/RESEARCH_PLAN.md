# 2026-05 Backtest Report Productization Research Plan

## 이걸 하는 이유?

현재 finance 프로젝트는 Backtest Analysis, Practical Validation, Final Review, Selected Portfolio Dashboard까지 이어지는 evidence-first workflow를 갖추고 있다. 다만 백테스트 결과가 아직 "제품화된 전략 리포트"로 안정적으로 묶여 있지는 않다.

지금의 결과 화면과 Markdown report 구조는 개발/검토에는 유용하지만, 앞으로 사용자가 여러 전략을 비교하고, 근거를 다시 열람하고, 선택 결정을 공유하려면 백테스트 결과를 재사용 가능한 report artifact로 다루는 설계가 필요하다.

이번 리서치의 목적은 다음 결정을 돕는 것이다.

| 질문 | 판단 기준 |
| --- | --- |
| 백테스트 결과 리포트는 어떤 역할이어야 하는가? | 단순 성과 표시인지, 전략 채택 근거와 검증 상태를 담는 evidence artifact인지 |
| 현재 프로젝트는 어디까지 준비되어 있는가? | result bundle, run history, reports/backtests, validation/final review 연결 수준 |
| 유사 제품은 결과를 어떻게 보여주는가? | tear sheet, metric table, equity/drawdown chart, trade/order/log, export/share 패턴 |
| 다음에 무엇을 먼저 만들 것인가? | report contract, Markdown draft, viewer, export 중 리스크 대비 가치 |

## Scope

포함한다.

- 현재 `reports/backtests`와 Backtest UI 결과 표시 구조 audit
- 외부 backtesting/reporting 제품과 open-source tear sheet 패턴 비교
- 백테스트 결과/전략 리포트 UI 패턴 정리
- 기능 후보와 추천 구현 순서 정리

포함하지 않는다.

- 실제 report generator 구현
- Next.js 화면 구현
- PDF/HTML export 구현
- live trading, broker order, 자동 rebalance 설계
- 기존 registry/run history schema 변경

## Method

1. Local project audit
   - durable docs, report templates, result display, runtime history, selected dashboard replay 구조를 확인한다.
   - 사용자-facing / 내부 ops / mixed surface를 분류한다.
2. External benchmark
   - 공식 문서와 공식 repository를 우선한다.
   - 2026-05-14 기준으로 웹에서 확인한 source에 evidence label을 남긴다.
3. Opportunity synthesis
   - impact / effort / risk / confidence / product fit 기준으로 후보를 점수화한다.
   - 바로 구현할 slice와 parking lot을 분리한다.

## Outputs

| File | Role |
| --- | --- |
| `CURRENT_PROJECT_AUDIT.md` | 현재 report/backtest 기능, 강점, 약점 |
| `BENCHMARKS.md` | 유사 제품/라이브러리 벤치마크 |
| `UI_PATTERNS.md` | 백테스트 결과 리포트 UX/UI 패턴 |
| `FEATURE_CANDIDATES.md` | 추가 기능 후보와 우선순위 |
| `RECOMMENDATION.md` | 최종 추천 방향과 1차 구현 범위 |
| `SOURCES.md` | 웹/로컬 출처와 evidence label |
| `RISKS.md` | 미확인 사항과 후속 검증 |

## Working Assumptions

- 이 프로젝트의 핵심 제품 가치는 "전략을 자동 매매하는 것"이 아니라 "검증 가능한 근거로 전략 후보를 판단하는 것"이다.
- 백테스트 리포트는 registry나 saved setup의 source-of-truth를 대체하지 않는다.
- 먼저 하나의 안정적인 report artifact contract를 만든 뒤, Markdown/Streamlit/Next.js/HTML/PDF 표현을 붙이는 순서가 안전하다.
- Streamlit은 결과 생성과 내부 검토에는 계속 유용하지만, 공유 가능한 제품 리포트 화면은 별도 read-only surface 후보가 될 수 있다.
