# Finance Roadmap

Status: Active
Last Verified: 2026-08-12

## Current Snapshot

Finance Console은 `Research / Portfolio / Data / Help` 아래 7개 top-level surface를
제공하는 Evidence-first 퀀트 투자 리서치 워크스페이스다.

사용자 승인 `Inflation Policy Yield Path` 5단계 phase는 actual DB와 Browser 재감사를
통과해 완료됐다. 독립 Point-in-Time 데이터, Core PCE Q4/Q4, 정책·공동 금리 경로·
10년물 목표 역산, 조건부 S&P 500 스트레스와 독립 12개월 침체 위험이 기존 V1 workflow에
연결됐다.
기존 baseline과 남은 verification debt는 유지하며 다른 신규 product/data scope는
아래 Decision Queue에서 별도 승인 없이 함께 열지 않는다.

현재 판단 기준:

- Product baseline: Research → Portfolio Lab → Portfolio Monitoring 흐름 구현
- Data baseline: MySQL-backed ingestion / loader / service / UI 경계 구현
- Safety baseline: no live approval, broker order, auto rebalance
- Active phase: none
- Active product implementation: none
- Completed phase: `inflation-policy-yield-path` (5/5 actual DB/Browser verified)
- Inflation / Policy baseline: Core PCE·policy·joint rate·reverse·equity·independent recession materialization READY
- Paused work와 Verification-Only work는 별도 상태로 관리

## Implemented Baseline

| Track | Current Baseline | Boundary |
|---|---|---|
| Today | 시장 세션, 저장된 시장 근거, 일정과 대표 포트폴리오 EOD/live overlay | summary / navigation surface, trading signal 아님 |
| Market Research | 관측 기반 현재 국면·최근 변화·조건부 전환 감시 경제 사이클, 선물 매크로, 심리, 일정, S&P 500, Market Movers, 미국 개별 종목의 3-family / 7-view research | context-only, 미래 월별 국면 예측·validation / monitoring signal 아님 |
| Institutional Holdings | SEC Form 13F 기관 portfolio, holdings, sector, security detail와 identifier coverage | delayed long holdings research, recommendation 아님 |
| Data Operations | 네 consumer 목적별 data preparation, 공식 파일, bounded recovery, compact history와 active 30-action 고급 도구 | explicit click만 실행, UI direct fetch와 자동 연속 실행 없음 |
| Backtest Analysis | single strategy와 portfolio mix 실행·비교, result bundle, save / replay와 candidate source. Risk-On Momentum 5D는 Quick / Standard / Deep 분석 강도와 compact Daily Swing evidence를 제공 | 높은 수익률만으로 선정하지 않음 |
| Practical Validation | data trust, realism, provider, holdings, macro, stress, robustness와 construction evidence. Daily Swing은 거래·비용·회전율·PIT/survivorship 전용 module로 fail-closed | `NOT_RUN`은 pass가 아니며 보강 뒤 재검증 필요 |
| Final Review | gate-aware investment report, selected / hold / reject / re-review decision과 monitoring handoff | human decision record, live approval 아님 |
| Portfolio Monitoring | direct stock·ETF와 selected strategy의 group/item, cashflow-aware performance, contribution, diagnosis와 recheck | read-only monitoring, broker / auto rebalance 없음 |
| Reference Center | 7개 current surface의 개념·journey·failure state·deep link 검색 | product help owner |
| Architecture | Python domain / service / runtime, Streamlit command boundary와 React presentation 분리 | React가 DB / provider / canonical decision을 소유하지 않음 |
| Inflation / Policy Backend | 독립 27-series PIT 원장, Philadelphia Fed SPF 확률 bin, 공식 FOMC rate decision 86건·SEP 40 release, FactSet 두 CY 라벨 검증 annual EPS 80 release, strict as-of/vintage loader, 혼합형 Core PCE, 검증 정책 marginal·2,000개 joint rate path·equity stress·독립 침체, 동적 저항대 | 기존 경제 사이클 결과 재사용 없음; Core/Q4/policy/joint-rate/equity/recession actual chronological gate 통과 |
| Inflation / Policy Workbench | 기존 경기 국면 기본 선택기 아래 DB-backed 물가·정책·금리·역산·equity·12개월 침체 surface와 USER 기준 저장 | actual Q4 5상태·다음 발표·다음 회의·연말 정책·동적 4.79% 역산·EPS×multiple 스트레스·침체 5단계 공개와 Browser QA 완료 |

상세 구현과 과거 QA는 개별 task / phase 기록에 남아 있다. 현재 제품 의미는
[Product Direction](./PRODUCT_DIRECTION.md), code ownership은
[Project Map](./PROJECT_MAP.md)에서 확인한다.

## Current Work State

### Active

현재 user-approved product implementation 또는 active phase는 없다.
새 제품 범위는 목적, 완료 조건과 data/safety boundary를 합의한 뒤 task 또는
명시적으로 요청된 phase로 연다.

### Paused

| Work | Current State | Resume Condition |
|---|---|---|
| [CNN / AAII Sentiment expansion](../tasks/active/overview-sentiment-cnn-aaii-v1-20260719/STATUS.md) | 전체 잠정 `2/4차`. current evidence, immutable collection-time snapshot과 common-period history 구현 완료. 3차 독립 데이터 후보 검토는 사용자 요청으로 보류 | 신규 source 후보와 저장 경계를 승인하고, 1W / 1M 공개 전 chronological Point-in-Time validation을 별도 승인 |

Paused는 실패나 미완성 product baseline을 뜻하지 않는다. 현재 공개 가능한 범위는
유지하고, 다음 확장은 새 승인 전까지 시작하지 않는 상태다.

### Verification-Only

| Work | Implementation State | Remaining Verification |
|---|---|---|
| [Portfolio Monitoring chart zoom / pan](../tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/STATUS.md) | interaction helper, React UI, regression과 build 완료 | in-app Browser에서 desktop / 900px / 420px wheel, drag, reset, overflow QA |
| [Market Movers chart navigation polish](../tasks/active/market-movers-chart-navigation-polish-v1-20260721/STATUS.md) | hover / drag / readout 구현, regression과 production build 완료 | 최신 local app에서 hover / drag / responsive / console QA |

Verification-Only는 새 기능 설계가 아니다. 제품 의미를 바꾸지 않고 실제 interaction과
layout evidence를 닫은 뒤 해당 task status를 complete로 정렬한다.

## Next Decision Queue

| Priority | Candidate | Why It Matters | Approval Needed Before |
|---|---|---|---|
| P0 | Economic-cycle RTDSM / ADS realtime history expansion | next-transition target은 승인됐지만 current PIT history가 148개월·32 events이고 holdout expansion/slowdown support가 0이라 probability model이 `NO_GO_DATA` 상태 | Philadelphia Fed provider/file contract, storage mapping, current-state common-period parity와 gate rerun 범위 승인 |
| P0 | Historical universe / delisting Point-in-Time evidence | strict factor와 historical validation의 survivorship risk를 낮추는 핵심 correctness gap | source/provider, historical membership schema, delisting evidence와 fail-closed policy 결정 |
| P1 | Existing Browser verification debt closeout | 구현 완료 task의 실제 interaction evidence와 status drift를 작은 범위로 닫을 수 있음 | 대상 task별 QA-only 범위 확인 |
| P1 | Market Movers sector conditional outlook | 현재 broader roadmap의 다음 단계지만 확률·분포를 공개하려면 독립 episode와 OOS publication gate가 필요 | target, sample independence, chronological validation과 공개 기준 승인 |
| P1 | Sentiment independent evidence / PIT validation | CNN·AAII의 현재 맥락을 장기 검증 가능한 evidence로 확장할 수 있음 | paused 해제, 신규 source와 chronological PIT validation scope 승인 |
| P2 | Overview scheduler hardening | browser-session 수동 흐름을 넘어 unattended collection을 운영할 때 필요 | launchd / scheduler 운영권한, retry, alert와 runbook 승인 |
| P3 | Data Operations durable execution / dependency hardening | 운영 근거가 생기면 queue·cancel·resume 또는 collapsed-body 초기 평가와 dynamic dependency 위험을 줄일 수 있음 | 실제 unattended / multi-user 필요, authorization, history scope와 한 번에 하나의 refactor boundary 승인 |
| P3 | Focused code refactor follow-up | transitional Backtest helper와 일부 large surface의 ownership을 더 명확히 할 수 있음 | 한 번에 하나의 owner boundary와 public call-path 변경 승인 |
| P3 | UI platform split research | Streamlit이 복잡한 UX의 장기 제약이 될 경우 API + standalone React를 검토 | migration target, API boundary, deployment / auth scope 승인 |
| P3 | Physical task / phase archive migration | retained completed board 때문에 active 폴더 탐색이 무거움 | 대량 이동, historical link repair와 archive policy 승인 |

## Recommended Order

1. **Economic-cycle data decision** — RTDSM/ADS 공식 realtime history로 usable origin과
   independent transition support를 확장할지 승인하거나 forecast 개발을 중단한다.
2. **Verification debt closeout** — 이미 구현된 interaction을 작은 QA-only 작업으로 닫아
   active-state 신뢰도를 높인다.
3. **Correctness decision** — historical universe / delisting PIT source와 storage policy를
   승인하거나 명시적으로 defer한다.
4. **One product research lane** — Market Movers outlook 또는 Sentiment validation 중
   하나만 선택해 target과 publication gate를 먼저 설계한다.
5. **Maintenance / platform work** — Data Operations hardening, refactor, scheduler,
   UI split과 archive migration은 제품 가치나 운영 병목이 확인된 범위로만 연다.

동시에 여러 broad track을 열지 않는다. 각 후보는 source correctness, 사용자 완료
작업, 구현 범위와 검증 비용을 비교한 뒤 하나의 task 또는 명시적으로 승인된 phase로
전환한다.

## Completion And Approval Rules

### State Meanings

| State | Meaning |
|---|---|
| Active | 사용자가 범위와 완료 조건을 승인했고 현재 구현·조사·문서 작업이 진행 중 |
| Paused | 구현된 현재 범위는 유지하지만 다음 확장은 명시적 재개 전까지 진행하지 않음 |
| Verification-Only | behavior implementation은 끝났고 실제 환경 QA와 closeout 기록만 남음 |
| Candidate | 아직 승인되지 않은 다음 결정 후보 |
| Complete | 요구된 구현, 관련 검증, durable docs와 필요한 handoff가 모두 정렬됨 |

여기서 handoff는 우선 task/phase `STATUS.md`, `RUNS.md`, `RISKS.md`의 다음 행동과 검증 기록을 뜻한다.
root handoff log는 다음 작업자가 반드시 알아야 할 고신호 milestone이나 decision이 있을 때만 갱신한다.

### Product Completion

- 화면이나 지표를 추가한 것만으로 완료하지 않는다. 사용자가 실제 workflow에서
  무엇을 끝낼 수 있는지 확인한다.
- DB / provider / validation 변화는 Point-in-Time, look-ahead, survivorship와
  source coverage를 검토한다.
- `NOT_RUN`, missing, stale와 partial을 pass 또는 fully ready로 표현하지 않는다.
- UI 변경은 관련 automated contract와 가능한 actual Browser QA를 함께 닫는다.
- generated artifact와 local runtime state를 product source-of-truth로 승격하지 않는다.

### Approval Boundary

다음 변경은 구현 전에 사용자 승인을 받는다.

- product journey, stage 책임과 navigation 의미 변경
- 새로운 provider, DB schema 또는 historical source-of-truth
- validation gate, Final Review eligibility와 Monitoring handoff 의미 변경
- background scheduler, external deployment 또는 account / broker integration
- 대량 task / phase 이동과 historical link rewrite

## Work Model

| Unit | Location | Responsibility |
|---|---|---|
| Task | `.aiworkspace/note/finance/tasks/active/<task>/` | focused implementation, docs, QA 또는 investigation |
| Phase | `.aiworkspace/note/finance/phases/active/<phase>/` | 명시적으로 승인된 multi-task direction과 integration |
| Research | `.aiworkspace/note/finance/researches/active/<research-id>/` | product direction, benchmark와 feature opportunity evidence |
| Durable Docs | `.aiworkspace/note/finance/docs/` | 구현 후 오래 유지될 current knowledge |
| Root Handoff | `.aiworkspace/note/finance/WORK_PROGRESS.md`, `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | milestone / decision pointer |

folder가 `active/` 아래 있다는 이유만으로 현재 active라고 판단하지 않는다. Roadmap,
state manifest와 해당 `STATUS.md`를 함께 확인한다.

## Update Rules

- Roadmap 첫 화면에는 Current Snapshot, 실제 open state와 Decision Queue를 둔다.
- 완료 task별 상세 changelog를 Roadmap에 추가하지 않는다.
- 구현된 baseline이 바뀌면 해당 product track 한 줄과 owning durable doc을 갱신한다.
- task가 paused 또는 verification-only가 되면 active와 분리하고 resume / close 조건을 쓴다.
- product purpose와 non-goal은 Product Direction, code ownership은 Project Map,
  algorithm·storage·user flow는 focused architecture / data / flow 문서가 소유한다.
- milestone detail은 task / phase 기록, 최근 handoff는 root log에서 찾는다.
- 새 active phase는 사용자가 phase-managed execution을 명시적으로 승인할 때만 연다.
