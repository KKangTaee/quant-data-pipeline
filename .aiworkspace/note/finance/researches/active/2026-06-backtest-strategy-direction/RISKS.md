# Risks

Status: Active
Last Verified: 2026-06-08

## Open Questions

- 3차 첫 구현을 `Strategy Evidence Inventory / Direction Panel`로 할지, 바로 `Strict Annual + GTAA/EW Portfolio Bridge`로 할지 사용자 결정이 필요하다.
- Risk-On Momentum 5D governance를 이번 cycle에 포함할지 별도 cycle로 뺄지 아직 확정하지 않았다.
- Global Relative Strength / Risk Parity / Dual Momentum의 current candidate search를 어느 순서로 볼지 미정이다.

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| 성과 수치가 투자 준비 상태처럼 읽힘 | 사용자가 CAGR / MDD만 보고 후보를 과대평가할 수 있다 | maturity / validation / monitoring readiness를 성과보다 먼저 보여준다 |
| Risk-On Momentum을 너무 빨리 governance에 연결 | daily swing 전략이 기존 monthly / annual gate와 섞여 의미가 흐려질 수 있다 | 별도 Daily Swing governance design을 먼저 열고, monitoring signal이 아니라 review evidence로 시작한다 |
| Quarterly prototype 과대해석 | runtime smoke를 investment evidence로 착각할 수 있다 | prototype label과 missing replay / validation evidence를 명확히 표시한다 |
| Research output is mistaken for approved roadmap | 확정되지 않은 방향이 committed roadmap처럼 보일 수 있다 | recommendation은 user approval 전까지 evidence로만 둔다 |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Strategy report path drift | 과거 report 링크가 다른 worktree 경로를 가리킬 수 있다 | 현재 bundle은 현재 worktree local source와 relative path를 우선한다 |
| 구현 세션이 scope를 넓힘 | inventory, bridge, governance가 한 번에 섞일 수 있다 | 3차는 3A / 3B / 3C로 분리하고 첫 task는 read-only로 좁힌다 |
| Streamlit UI 변경이 커짐 | Backtest Analysis 화면이 더 복잡해질 수 있다 | read model을 먼저 만들고 UI는 compact table / expander로 시작한다 |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| External benchmark 부재 | 상용 제품 대비 위치 판단은 아직 약하다 | 필요 시 `finance-benchmark-research`로 별도 research를 연다 |
| ETF non-GTAA 후보 탐색 부족 | GRS / Risk Parity / Dual Momentum이 product catalog에 비해 evidence가 약하다 | ETF evidence expansion task |
| Risk-On governance 미설계 | daily swing 결과가 workflow에 들어갈 기준이 없다 | Daily Swing governance research / design |
| Quarterly investment evidence 부족 | prototype을 annual strict와 혼동할 수 있다 | quarterly replay / PIT / filing lag validation |

## Follow-Up

- 3차 새 세션에서 `NEXT_SESSION_HANDOFF.md`를 먼저 읽는다.
- 구현 전 `PROJECT_MAP.md`, `BACKTEST_RUNTIME_FLOW.md`, `BACKTEST_UI_FLOW.md`를 다시 확인한다.
- Backtest UI 변경이 있으면 Browser QA를 수행한다.
- 구현 후에는 `finance-doc-sync`로 durable docs alignment를 별도 처리한다.
