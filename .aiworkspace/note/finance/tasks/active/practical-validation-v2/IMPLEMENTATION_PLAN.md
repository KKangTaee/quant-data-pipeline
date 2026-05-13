# Practical Validation V2 Remaining Implementation Plan

## 목적

이 문서는 `DESIGN.md`에 흡수된 Practical Validation 진단 설계를 기준으로,
현재 구현이 끝난 범위와 아직 남은 개발 범위를 분리해 정리한다.

이번 문서의 목적은 개발 착수가 아니라, 사용자가 검토할 수 있는 남은 구현 계획을 만드는 것이다.
코드 변경은 이 문서 검토 후 별도 확인을 받고 진행한다.

## P2 전용 후속 문서

P2 개발은 아래 두 문서로 더 구체화한다.

| 문서 | 역할 |
|---|---|
| `CONNECTOR_AND_STRESS_PLAN.md` | P2 전체 실행 계획. Cost / Liquidity, ETF holdings, Macro / Sentiment, Stress Interpretation, sensitivity runtime 경계를 정리 |
| `PROVIDER_CONNECTORS.md` | provider / DB / loader connector 상세 설계. ETF operability snapshot, holdings snapshot, macro series loader 계약을 정리 |

## 쉽게 말하면

현재 Practical Validation V2는 이미 12개 진단 보드, 검증 프로필, profile-aware score,
compact curve / DB price proxy 기반 rolling / stress / baseline / sensitivity 계산까지 들어가 있다.

하지만 아직 모든 진단이 "실제 전략 runtime replay와 외부/DB provider 데이터"를 사용해 정밀 계산되는 상태는 아니다.
일부는 proxy 계산이고, 일부는 `NOT_RUN` 또는 `REVIEW`로 남아 있다.

따라서 P2의 핵심은 provider connector 자체가 아니라,
**12개 Practical Validation 진단 중 아직 정상 검증되지 않는 항목을 정상화하는 것**이다.

정상화의 의미:

- 데이터가 있으면 실제 provider / DB evidence로 검증한다.
- 데이터가 없으면 왜 `NOT_RUN`인지 명확히 표시한다.
- proxy만 가능하면 `proxy` 또는 `REVIEW`로 명확히 구분한다.
- Final Review에서 사용자가 "이 검증을 믿을 수 있는지 / 아직 부족한지" 판단할 수 있게 만든다.

다음 개발의 핵심은 아래 세 가지다.

1. proxy와 실제 replay / 실제 provider 데이터를 명확히 분리한다.
2. 실제 계산 가능한 진단은 전략 runtime 또는 DB provider로 고도화한다.
3. Final Review와 Selected Portfolio Dashboard가 이 evidence를 믿고 읽을 수 있게 저장 계약을 정리한다.

## 현재 작업 기준: P2는 12개 진단 정상화 트랙

P2는 별도 phase가 아니라 Practical Validation V2 내부의 개발 트랙이다.
현재 작업은 아래 순서로 진행한다.

```text
P2-0. 12개 진단 중 P2 대상 항목 확정
P2-1. 각 항목에 필요한 데이터 목록 확정
P2-2. ETF 운용성 / 비용 / 유동성 데이터 수집
P2-3. ETF holdings / exposure 데이터 수집
P2-4. macro / sentiment 데이터 수집
P2-5. Practical Validation 12개 진단에 연결
P2-6. stress / sensitivity 해석 보강
P2-7. QA: proxy / NOT_RUN 항목이 정상적으로 설명되는지 확인
```

P2에서 직접 정상화하는 주 대상은 아래와 같다.

| 검증 번호 | 검증 항목 | P2 정상화 방향 |
|---:|---|---|
| 2 | Asset Allocation Fit | ticker proxy 대신 ETF holdings / asset-class exposure 사용 |
| 3 | Concentration / Overlap / Exposure | holdings overlap, top holding concentration, exposure 중복 확인 |
| 5 | Regime / Macro Suitability | FRED 기반 VIX / yield curve / credit spread snapshot 사용 |
| 6 | Sentiment / Risk-On-Off Overlay | VIX / spread / yield curve 기반 risk-on/off market context 사용 |
| 7 | Stress / Scenario Diagnostics | stress 숫자에 원인 해석과 review trigger 추가 |
| 9 | Leveraged / Inverse ETF Suitability | provider 상품 정보로 leverage / inverse / daily objective 확인 |
| 10 | Operability / Cost / Liquidity | expense ratio, AUM, ADV, spread, premium/discount로 보강 |
| 11 | Robustness / Sensitivity / Overfit | sensitivity 결과와 해석을 더 명확히 표시 |

P2의 데이터 수집 / DB / loader 작업은 위 검증 항목을 정상화하기 위한 수단이다.
즉 P2는 "provider 플랫폼 구축"이 아니라 "미완성 검증 항목 정상화"가 목표다.

P2-0 현재 상태:

- `completed`
- 대상 진단은 2, 3, 5, 6, 7, 9, 10, 11로 확정했다.
- 각 대상 진단의 actual data, bridge / proxy fallback, `NOT_RUN` / `REVIEW` 조건은
  `CONNECTOR_AND_STRESS_PLAN.md`의 `P2-0 완료 산출물: 대상 진단 계약`을 기준으로 한다.

P2-1 현재 상태:

- `completed`
- P2-0 진단 계약을 구현하기 위한 schema / ingestion field contract를 확정했다.
- 신규 table 후보는 `etf_operability_snapshot`, `etf_holdings_snapshot`, `etf_exposure_snapshot`,
  `macro_series_observation` 4개다.
- 각 table의 business key, actual 판정 최소조건, bridge / proxy 경계, loader 반환 기준은
  `PROVIDER_CONNECTORS.md`의 `P2-1 Schema / Ingestion Field Contract`를 기준으로 한다.

P2-2 현재 상태:

- `partial_complete`
- P2-2A로 `etf_operability_snapshot` schema, 기존 DB 기반 `db_bridge` 수집, UPSERT 저장, loader read path를 구현했다.
- 현재 구현은 official issuer actual data 수집이 아니라 `nyse_price_history` / `nyse_asset_profile` 기반 bridge/proxy foundation이다.
- 다음 P2-2B는 iShares / SSGA / Invesco official source를 붙여 `source_type=official` actual / partial row를 저장하는 것이다.

## 현재 구현 상태

현재 Clean V2 흐름은 아래와 같다.

```text
Backtest Analysis
  -> PORTFOLIO_SELECTION_SOURCES.jsonl
  -> Practical Validation
  -> PRACTICAL_VALIDATION_RESULTS.jsonl
  -> Final Review
  -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl
  -> Operations > Selected Portfolio Dashboard
```

현재 구현된 주요 기능:

| 영역 | 현재 상태 |
|---|---|
| Validation Profile | 방어형 / 균형형 / 성장형 / 전술·헤지형 / 사용자 지정과 5개 질문을 저장하고 threshold / domain weight / rolling window / cost assumption에 반영 |
| 12개 Practical Diagnostics | Input Evidence부터 Monitoring Baseline Seed까지 domain별 `PASS / REVIEW / BLOCKED / NOT_RUN` 표시 |
| Profile-aware score | profile별 domain weight를 반영한 score breakdown 표시 |
| Curve evidence | Backtest Analysis handoff의 compact monthly curve snapshot 저장, 기존 source는 DB price proxy curve 계산 시도 |
| Rolling validation | portfolio curve가 있으면 profile별 rolling window 기준으로 계산 |
| Stress diagnostics | static stress calendar로 포함 구간을 찾고, curve가 있으면 return / MDD / benchmark spread 계산 |
| Alternative baseline | SPY, QQQ, 60/40 proxy, cash-aware baseline을 같은 기간 DB price proxy로 비교 |
| Correlation / risk contribution | component curve가 있으면 monthly return correlation과 volatility contribution proxy 계산 |
| Sensitivity | drop-one, mix weight +5%p, window perturbation 일부 계산 |
| Operability | 가격 / volume 기반 proxy로 최소 운용성 확인 |
| Macro / sentiment | FRED connector 전까지 benchmark price-action proxy context로 표시 |
| Final Review handoff | Practical Diagnostics 요약, score breakdown, curve evidence, rolling evidence를 Final Review snapshot으로 전달 |
| 최신 runtime 재검증 | 사용자가 명시적으로 실행할 때 기존 strategy runtime으로 source를 최신 DB 시장일까지 재검증하고, 보조 모드로 저장 기간 replay를 제공하며, curve provenance와 benchmark parity를 validation result에 저장 |

현재 구현은 실전 후보 진단의 1차 골격과 일부 정량 계산이 완료된 상태다.
다만 아래 영역은 아직 정밀 구현이 남아 있다.

## 12개 진단별 남은 범위

| 번호 | 진단 module | 현재 상태 | 남은 구현 |
|---:|---|---|---|
| 1 | Input Evidence Layer | source runtime recheck attempt와 benchmark parity 저장까지 구현 | source replay contract completeness와 unsupported strategy 설명을 더 보강 |
| 2 | Asset Allocation Fit | ticker proxy classification 기반 | ETF holdings / sector / asset-class provider가 붙으면 look-through exposure로 보강 |
| 3 | Concentration / Overlap / Exposure | ticker / weight / sector ticker proxy 기반 | holdings-level overlap, top holding concentration, issuer / theme 중복 계산 |
| 4 | Correlation / Diversification / Risk Contribution | component curve 기반 proxy, runtime recheck curve 우선 사용 | contribution-to-drawdown 보강 |
| 5 | Regime / Macro Suitability | benchmark price-action proxy | FRED 기반 yield curve / credit spread / VIX snapshot connector 추가 |
| 6 | Sentiment / Risk-On-Off Overlay | proxy context | VIX / credit spread / yield curve 우선, Fear & Greed는 안정 source 확정 후 optional |
| 7 | Stress / Scenario Diagnostics | static event calendar + curve 기반 계산, runtime recheck curve 우선 사용 | stress별 interpretation 보강 |
| 8 | Alternative Portfolio Challenge | SPY / QQQ / 60/40 / cash-aware proxy | same-period parity, profile별 성공 기준, All Weather-like proxy 후속 추가 |
| 9 | Leveraged / Inverse ETF Suitability | ticker set / 목적 / 기간 proxy | 상품별 leverage multiple, daily objective, holding-period mismatch 근거 보강 |
| 10 | Operability / Cost / Liquidity | DB price / volume proxy, one-way cost assumption | expense ratio, AUM, ADV, bid-ask spread, premium/discount, turnover connector |
| 11 | Robustness / Sensitivity / Overfit | drop-one / weight +5%p / local trial count 일부 | strategy-specific perturbation runtime, multi-run 결과 저장 요약 |
| 12 | Monitoring Baseline Seed | component / benchmark / trigger seed 구현 | Selected Dashboard monitoring log 저장, alert trigger persistence, recheck evidence 비교 |

## 개발 원칙

남은 개발은 아래 원칙을 지킨다.

| 원칙 | 내용 |
|---|---|
| 투자 추천 아님 | Practical Validation은 live approval, 주문 지시, 미래 수익 보장이 아니다 |
| 새 전략 구현 아님 | GTAA / EW / GRS / Mix 등 기존 runtime을 replay하거나 조합한다. 새 전략 로직을 `finance/strategy.py`에 추가하지 않는다 |
| proxy와 actual 분리 | 모든 진단은 `actual_runtime`, `db_price_proxy`, `embedded_snapshot`, `provider_snapshot`, `not_run` 같은 출처를 남긴다 |
| `NOT_RUN`은 통과가 아님 | 데이터나 connector가 없어 실행하지 못한 domain은 Final Review에서 확인해야 하는 gap으로 남긴다 |
| 기존 JSONL 강제 의존 금지 | 기존 archive성 JSONL을 억지로 살리는 대신 Clean V2 row를 기준으로 한다. 필요한 경우 compatibility loader만 유지한다 |
| 대형 result 저장 금지 | full dataframe을 JSONL에 남기지 않고 compact curve / summary / evidence rows만 남긴다 |
| run_history commit 금지 | local run history는 audit summary만 선택적으로 읽고, 원본 JSONL은 커밋하지 않는다 |
| stage ownership 유지 | Backtest Analysis는 후보 생성, Practical Validation은 실전 진단, Final Review는 최종 판단, Selected Dashboard는 사후 monitoring을 담당한다 |

## 저장 계약 보강안

현재 기본 저장 파일은 유지한다.

| 파일 | 역할 |
|---|---|
| `.aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl` | Backtest Analysis에서 Practical Validation으로 보낸 source |
| `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` | Practical Validation 결과 |
| `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | Final Review 최종 판단 |
| `.aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | Selected Dashboard에서 사용자가 명시 저장한 monitoring snapshot |
| `.aiworkspace/note/finance/saved/SAVED_PORTFOLIO_MIXES.jsonl` | reusable saved mix setup |

다음 개발에서 Practical Validation result는 schema version을 올릴 수 있다.
권장 추가 필드는 아래와 같다.

```json
{
  "schema_version": 3,
  "curve_provenance": {
    "portfolio_curve_source": "actual_runtime | embedded_snapshot | db_price_proxy | unavailable",
    "benchmark_curve_source": "actual_runtime | embedded_snapshot | db_price_proxy | unavailable",
    "component_curve_sources": []
  },
  "replay_contract": {
    "source_kind": "single_strategy | compare_strategy | weighted_mix | saved_mix",
    "strategy_keys": [],
    "period": {},
    "settings_snapshot": {},
    "benchmark_ticker": "SPY"
  },
  "replay_attempts": [
    {
      "attempted_at": "ISO-8601",
      "status": "PASS | REVIEW | BLOCKED",
      "runtime_path": "existing_runtime",
      "error": null
    }
  ],
  "benchmark_parity": {
    "same_period": true,
    "same_frequency": true,
    "same_cost_basis": "known | assumed | not_run",
    "missingness_note": null
  },
  "provider_coverage": {
    "holdings": "actual | proxy | not_run",
    "liquidity": "actual | proxy | not_run",
    "macro_sentiment": "actual | proxy | not_run"
  }
}
```

주의:

- 위 구조는 방향성이다. 개발 시 기존 row와 호환되도록 optional field로 시작한다.
- full daily result dataframe을 그대로 저장하지 않는다.
- 실제 replay가 오래 걸릴 수 있으므로 Practical Validation 화면에서 자동 실행보다 명시 버튼을 우선한다.

## 코드 분리 계획

현재 `app/web/backtest_practical_validation_helpers.py`가 source 생성, profile, curve proxy,
diagnostics 계산, persistence handoff까지 많은 책임을 갖고 있다.
다음 개발은 기능을 확장하기 전에 helper를 너무 거대하게 만들지 않는 방향이 좋다.

권장 분리:

| 새 helper 후보 | 책임 |
|---|---|
| `app/web/backtest_practical_validation_profiles.py` | profile option, 5개 질문, threshold / domain weight 계산 |
| `app/web/backtest_practical_validation_curve.py` | compact curve normalize, DB price proxy, benchmark parity, curve provenance |
| `app/web/backtest_practical_validation_replay.py` | 기존 strategy runtime replay contract 생성과 실행 wrapper |
| `app/web/backtest_practical_validation_diagnostics.py` | 12개 domain result 생성, score, display row 생성 |
| `app/web/backtest_practical_validation_connectors.py` | holdings / liquidity / macro-sentiment provider adapter boundary |

분리 방식:

1. 먼저 behavior를 바꾸지 않고 순수 함수 이동만 한다.
2. `backtest_practical_validation_helpers.py`는 기존 import 호환을 위해 public wrapper를 유지한다.
3. 새 파일이 생기면 `SCRIPT_STRUCTURE_MAP.md`와 `BACKTEST_UI_FLOW.md`를 같이 갱신한다.
4. 분리 후 `py_compile`과 Streamlit smoke를 먼저 돌리고, 기능 고도화는 그 다음 commit에서 진행한다.

## 우선순위별 구현 단위

### P0. 최신 Runtime 재검증과 Curve Provenance

목표:

- Practical Validation에서 후보 source를 실제 기존 runtime으로 다시 실행할 수 있게 한다.
- 기본 검증은 저장 당시 종료일을 그대로 재현하는 것이 아니라, DB에 더 최신 가격 데이터가 있으면 최신 시장일까지 기간을 확장해 다시 확인한다.
- compact / proxy curve와 최신 runtime recheck curve, 저장 기간 replay curve를 구분해 표시한다.

현재 상태:

- 2026-05-10 2차 구현 완료.
- Practical Validation 화면의 3번 구간을 `최신 데이터 기준 전략 재검증`으로 정리했다.
- 기본 모드는 `최신 DB 데이터까지 확장 검증`이며, DB 최신 시장일이 저장 종료일보다 뒤면 그 날짜까지 기존 strategy runtime을 다시 실행한다.
- 보조 모드로 `저장 기간 그대로 재현`을 제공한다. 이 모드는 동일 기간 재현 / 디버깅 성격이며, 실전 후보 최신성 확인의 기본값은 아니다.
- 재검증은 자동 실행하지 않고 사용자가 명시적으로 `전략 재검증 실행`을 누를 때만 실행한다.
- 결과는 `actual_runtime_latest_recheck`, `actual_runtime_replay`, `embedded_source_curve`, `component_curve_weighted_proxy`, `db_price_proxy` provenance와 함께 validation result에 남긴다.
- 요청 종료일과 실제 portfolio curve 종료일이 7일 이상 벌어지면 `period_coverage`를 `REVIEW`로 남긴다. 예를 들어 mix 안의 GTAA component가 cadence상 최신 월까지 오지 못하면 runtime 실행은 성공해도 최신성 coverage는 검토 대상으로 표시한다.
- unsupported strategy나 contract 부족은 재검증 실패로 처리하되, snapshot / proxy 기반 diagnostics는 계속 표시한다.

작업:

- source kind별 replay contract 생성
- single strategy / compare-selected / weighted mix / saved mix replay 경로 정리
- `전략 재검증 실행` 버튼 추가
- 재검증 mode, 저장 기간, 요청 기간, 실제 기간, DB 최신 시장일, 확장 일수, period coverage, 성공 / 실패 / runtime error / elapsed time 저장
- curve provenance와 result parity 표시

수정 예상 파일:

- `app/web/backtest_practical_validation.py`
- `app/web/backtest_practical_validation_helpers.py`
- 새 replay helper 파일
- `app/web/runtime/portfolio_selection_v2.py`
- code analysis 문서

검증:

- 기존 source는 재검증 없이도 이전처럼 board 표시
- 재검증 버튼을 눌렀을 때만 actual runtime 실행
- 기본 모드에서 저장 종료일보다 최신 DB 시장일이 있으면 runtime payload의 종료일이 최신 시장일로 확장됨
- 실패 시 validation row를 망가뜨리지 않고 `REVIEW` 또는 `NOT_RUN` evidence로 남김

### P0. Benchmark Parity Hardening

목표:

- 후보와 benchmark가 같은 기간 / 같은 frequency / 같은 cost basis로 비교됐는지 확인한다.

현재 상태:

- 2026-05-10 1차 구현 완료.
- portfolio curve와 benchmark curve의 기간, 월별 coverage, frequency 차이를 `benchmark_parity`로 계산한다.
- parity가 `REVIEW`이면 Input Evidence review gap과 Curve / Replay Evidence에 표시한다.

작업:

- portfolio curve와 benchmark curve의 start / end / row count / monthly coverage 비교
- benchmark missing month, stale date, period mismatch 표시
- stress / baseline / rolling domain이 parity 상태를 재사용

검증:

- benchmark curve가 없으면 `NOT_RUN`
- 기간이 다르면 `REVIEW`
- Data Trust hard blocker와 중복 감점하지 않고 benchmark parity domain으로만 표시

### P1. Validation Inspector와 Profile Comparison UX

목표:

- 사용자가 같은 source를 방어형 / 균형형 / 성장형 등으로 바꿨을 때 무엇이 달라지는지 볼 수 있게 한다.

작업:

- 저장된 Practical Validation result 목록 inspect
- 같은 `selection_source_id` 기준 profile별 score / blocker / review gap 비교
- profile 변경으로 score가 달라지지 않는 경우, 원인이 hard blocker인지 profile-insensitive domain인지 설명

검증:

- 기존 result row를 깨지 않고 읽음
- score breakdown과 domain weight를 UI에서 확인 가능

### P1. Strategy-specific Sensitivity Runtime

목표:

- 단순 weight perturbation을 넘어 기존 runtime이 허용하는 설정 범위에서 작은 흔들림을 테스트한다.

작업 예시:

| strategy family | perturbation 예시 |
|---|---|
| GTAA | interval, moving average window, month-end / rebalance cadence의 작은 변경 |
| Equal Weight | rebalance frequency, ticker subset drop-one, sector/gold 포함 여부 |
| GRS | lookback, top_n, skip-month 여부 |
| Mix | component weight +/-5%p, drop-one, component role 변경 |

주의:

- 새 전략을 만들지 않는다.
- 기존 runtime의 입력으로 안전하게 표현 가능한 perturbation만 실행한다.
- 많은 실험을 자동으로 돌리는 optimizer로 만들지 않는다.

검증:

- perturbation 수와 결과 요약을 `overfit_audit`에 남김
- trial count가 많아질수록 overfit review gap을 표시

### P1. Final Review Gate V2.1

목표:

- Practical Validation 결과를 Final Review에서 더 명확히 해석하게 한다.

작업:

- `BLOCKED`는 Final Review 이동 차단 유지
- critical `NOT_RUN`은 이동은 허용하되 Final Review 선택 사유에서 명시 확인
- profile mismatch, alternative baseline 열세, stress 취약성, liquidity gap을 final decision reason template에 노출
- `SELECT / HOLD / RE_REVIEW / REJECT` 추천 문구는 투자 추천이 아니라 evidence-based route suggestion으로만 표시

검증:

- Final Review가 사용자의 최종 판단 저장 위치라는 stage ownership 유지
- Practical Validation에서 최종 메모를 받지 않음

### P2. ETF Holdings / Sector Look-through Provider

목표:

- proxy classification에서 ETF 내부 holdings 기반 exposure / overlap 계산으로 보강한다.

작업:

- provider 후보 결정
- ticker별 top holdings, sector, country, asset class coverage 저장 boundary 결정
- coverage가 없으면 `NOT_RUN`, proxy만 있으면 `REVIEW`로 표시
- holdings overlap matrix와 top holding concentration 표시

주의:

- provider source와 업데이트 시점을 row에 남긴다.
- ETF holdings는 시점에 따라 변하므로 point-in-time 한계를 disclosure한다.

### P2. Cost / Liquidity / ETF Operability Connector

목표:

- 가격 / volume proxy를 넘어 실제 ETF 운용 비용과 거래 가능성을 확인한다.

필요 데이터:

- expense ratio
- AUM
- average daily volume 또는 dollar volume
- bid-ask spread 또는 median spread
- premium / discount
- turnover 또는 rebalance cadence proxy

작업:

- `finance/data/asset_profile.py`와 기존 DB schema를 먼저 확인
- 이미 저장 가능한 field가 있으면 loader만 연결
- field가 부족하면 data architecture 문서와 schema 변경 계획을 먼저 만든다

검증:

- 비용 데이터가 없으면 `NOT_RUN` 또는 `REVIEW`
- 저유동성 / 고비용 ETF는 profile과 무관하게 hard blocker 후보

### P2. Macro / Sentiment Connector

목표:

- market-context evidence를 DB/API snapshot으로 붙인다.

1차 범위:

- VIX
- credit spread
- yield curve spread

후속 optional:

- CNN Fear & Greed

원칙:

- sentiment는 trade signal이 아니다.
- hard blocker로 쓰지 않고 market-context evidence로 둔다.
- 데이터 부재 시 `NOT_RUN`으로 표시한다.

작업:

- FRED 기반 connector 또는 DB cache boundary 결정
- API key / rate limit / caching 정책 결정
- snapshot date와 source를 validation row에 저장

### P2. Stress Interpretation 고도화

목표:

- static event window 계산 결과를 사용자가 해석 가능한 문장과 route suggestion으로 만든다.

작업:

- stress별 return, MDD, benchmark spread, recovery 여부 표시
- profile별 stress 중요도 조정
- 특정 stress에서 반복적으로 취약하면 Final Review review gap 생성

검증:

- stress calendar는 deterministic static data를 계속 사용
- 후보 기간 밖 stress는 `NOT_RUN`이지 통과가 아님

### P3. Selected Portfolio Monitoring Persistence

목표:

- Final Review에서 선정된 포트폴리오가 Selected Dashboard에서 사후관리 기준을 계속 남길 수 있게 한다.

작업:

- recheck result snapshot을 `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`에 사용자가 명시 저장
- drift alert preview를 monitoring row로 저장
- 이전 monitoring snapshot과 latest recheck 비교

주의:

- broker account 연결, 주문 초안, 자동 리밸런싱은 하지 않는다.
- monitoring log는 사후 관찰 기록이지 live approval이 아니다.

## 개발 순서 제안

현재 P2 작업의 권장 순서는 아래다.

1. 12개 진단 중 P2 대상 항목을 확정한다. (`completed`)
2. 각 검증 항목에 필요한 데이터와 fallback 상태를 정의한다. (`completed`)
3. ETF 운용성 / 비용 / 유동성 데이터를 수집하고 DB에 저장한다. (`partial_complete`: DB bridge/proxy foundation 완료, official provider actual 수집 남음)
4. ETF holdings / exposure 데이터를 수집하고 DB에 저장한다.
5. macro / sentiment 데이터를 수집하고 DB에 저장한다.
6. loader / provider context를 통해 Practical Validation 진단에 연결한다.
7. stress / sensitivity 해석을 보강한다.
8. proxy / actual / bridge / `NOT_RUN` 표시가 사용자가 이해할 수 있는지 QA한다.

이 순서가 좋은 이유:

- P0의 runtime replay와 benchmark parity는 이미 구현되어 있으므로, 지금은 남은 proxy / `NOT_RUN` 진단을 정상화하는 것이 다음 병목이다.
- provider connector는 독립 목적이 아니라 ETF / holdings / macro 관련 진단을 정상 검증하기 위한 데이터 경계다.
- 데이터가 없더라도 실패가 아니라 명확한 `NOT_RUN` / `REVIEW` reason을 남겨 Final Review 판단 가능성을 높인다.

## 테스트 / 검증 기준

각 구현 단위마다 최소 아래를 확인한다.

| 검증 | 기준 |
|---|---|
| py_compile | `app/web/pages/backtest.py`, `app/web/backtest_*.py`, `app/web/runtime/*.py` 컴파일 통과 |
| Streamlit smoke | Backtest Analysis -> Practical Validation -> Final Review 기본 흐름 접근 가능 |
| 기존 source 호환 | 기존 `PORTFOLIO_SELECTION_SOURCES.jsonl` row가 새 필드 없이도 읽힘 |
| result 저장 | validation result 저장 시 schema version과 optional field가 정상 저장 |
| generated artifact hygiene | run_history, web run history, temp CSV, local artifact는 commit 제외 |
| stage ownership | Practical Validation은 최종 메모를 받지 않고 Final Review로 넘김 |
| disclosure | proxy / actual / not_run 출처가 UI와 JSON에 남음 |

## 열려 있는 결정

개발 전 또는 개발 중 결정이 필요한 항목:

| 항목 | 기본 제안 |
|---|---|
| ETF holdings provider | 먼저 기존 `finance/data/asset_profile.py`와 DB schema를 확인하고, 없으면 별도 provider 설계 문서 작성 |
| FRED connector 저장 위치 | 초기에는 snapshot adapter + optional cache로 시작하고, 지속 수집이 필요해지면 data pipeline phase로 분리 |
| 최신 runtime 재검증 자동 실행 여부 | 자동 실행하지 않고 버튼 기반 명시 실행 |
| validation schema version | 최신 runtime 재검증 period / provenance 필드가 들어가며 v4로 올림 |
| Fear & Greed | 안정적 source와 재현성 확인 전에는 optional / 후속 |
| All Weather-like baseline | ETF / weight assumption 확정 후 후속 |

## 이번 문서의 결론

현재 Practical Validation V2는 core board와 1차 정량 진단이 구현되어 있다.
남은 핵심은 "더 많은 검증명을 추가하는 것"이 아니라,
최신 runtime 재검증과 실제 provider 데이터를 붙여 proxy domain을 actual evidence로 승격하는 것이다.

첫 구현 단위인 `P0. 최신 Runtime 재검증과 Curve Provenance`는 2026-05-10에 2차 구현까지 완료되었다.
따라서 현재 다음 개발은 P2로 보고,
12개 진단 중 provider / holdings / macro / stress / sensitivity 데이터가 부족해 정상 검증되지 않는 항목을 정상화한다.
