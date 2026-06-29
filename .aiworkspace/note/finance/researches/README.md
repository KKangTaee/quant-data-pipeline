# Finance Research Workspace

Status: Active
Last Verified: 2026-06-02

## Purpose

이 폴더는 `finance` 제품 방향, 벤치마킹, 기능 후보, 전략적 의사결정 근거를 조사하는 작업장이다.

`tasks/active/`가 실행 작업 기록이라면, `researches/active/`는 실제 조사 산출물의 본문을 담는다.

## Structure

```text
.aiworkspace/note/finance/researches/
  active/<research-id>/
    RESEARCH_PLAN.md
    CURRENT_PROJECT_AUDIT.md
    BENCHMARKS.md
    UI_PATTERNS.md
    FEATURE_CANDIDATES.md
    RECOMMENDATION.md
    SOURCES.md
    RISKS.md
  done/<research-id>/
```

## Active Researches

| Research | Focus |
| --- | --- |
| `active/2026-06-futures-monitor-ui-benchmark/` | Workspace > Overview > Futures Monitor를 완성형 제품 UI로 재설계하기 위한 TradingView / Koyfin / IBKR / Datadog / Grafana / Stripe / Linear / Toss Securities 벤치마킹과 구현 가이드 |
| `active/2026-06-market-context-visual-benchmark/` | Overview > Market Context를 카드 중심이 아닌 금융 UI pattern으로 재정리하기 위한 Koyfin / TradingView / OpenBB / Bloomberg 벤치마킹과 layout 선택지 |
| `active/2026-06-market-movers-redesign-v2-benchmark/` | Overview > Market Movers를 metric-card / prototype pattern에서 market-board형 변동 종목 UX로 재설계하기 위한 Toss Securities / Upbit / StockAnalysis / TradingView / Finviz benchmark |
| `active/2026-06-sub-dev-overview-macro-base/` | sub-dev worktree에서 Overview / Ingestion / Operations 데이터 분석, 매크로 context, 시각화 개선 후보를 개발 착수 전 정리하기 위한 제품 audit / benchmark / 기능 후보 가이드 |
| `active/backtest-direction-reset-research-20260612/` | Backtest Analysis와 strategy maturity 흐름을 panel 확장 중심이 아니라 실행, replay, validation handoff 중심으로 재정의하는 제품 방향 reset research |
| `active/2026-06-backtest-strategy-direction/` | Backtest 전략군의 성숙도, 장단점, 약점 matrix, 3차 구현 세션 handoff를 정리하는 내부 방향성 research |
| `active/2026-06-reference-guides-revamp/` | Reference > Guides를 현재 finance console 흐름에 맞는 task-first Reference Center로 개편하기 위한 제품 audit, benchmark, UX/UI pattern, 단계별 개발 가이드 |
| `active/2026-06-why-it-moved-benchmark/` | Overview > Market Movers > Why It Moved를 prototype-level link / metadata panel에서 manual investigation board로 개선하기 위한 벤치마킹과 V1.6 UX 가이드 |
| `active/2026-05-overview-market-intelligence/` | Workspace > Overview를 market movers, sector / industry leadership, event calendar 중심으로 개편할 수 있는지 조사 |
| `active/2026-06-futures-market-monitoring/` | 선물장 OHLCV / 개장 전 급변 신호를 Overview에서 read-only로 모니터링하기 위한 데이터 소스, cadence, UX 방향 조사 |
| `active/2026-05-ui-platform-research/` | Streamlit UX/UI를 Python quant engine + API + React/Next.js product surface로 분리할지 조사 |
| `active/2026-05-backtest-report-productization/` | Backtest Result / Strategy Report를 제품화하기 위한 report artifact, UI pattern, 기능 후보 조사 |
| `active/2026-05-investable-workflow-gap-analysis/` | 현재 Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름의 실전 투자 판단 약점과 상용 제품 대비 개선 방향 조사 |
| `active/2026-06-operations-workspace-restructure/` | Operations 탭의 현재 기능, legacy 보조 화면, Selected Portfolio Dashboard 위치, 운영/모니터링 개편 방향 조사 |

## Rules

- 조사 중 사실, 추측, source notes, 비교표는 `researches/active/<research-id>/`에 둔다.
- 채택된 장기 방향만 `docs/PRODUCT_DIRECTION.md` 또는 `docs/ROADMAP.md`로 승격한다.
- 승인된 개발 단위만 `phases/active/` 또는 `tasks/active/`로 전환한다.
- 외부 서비스, 가격, 기능, UI는 변할 수 있으므로 `SOURCES.md`에 접근 날짜와 evidence label을 남긴다.
- registry, saved setup, run history, generated artifact를 research 정리 대상으로 섞지 않는다.
