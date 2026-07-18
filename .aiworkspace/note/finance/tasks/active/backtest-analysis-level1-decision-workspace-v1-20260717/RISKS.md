# Risks

## Current Risks

### Large Existing UI Surfaces

`backtest_result_display.py`와 `backtest_compare/page.py`가 크고 다수의 legacy
contract를 포함한다. one-shell이 기존 runtime을 직접 재작성하지 않도록 adapter
seam과 focused regression test를 먼저 만든다.

### Streamlit Rerun Lifecycle

script rerun 자체를 없앨 수는 없다. stable context와 mutable result projection을
분리하지 않으면 실행 시 전체 화면 reset처럼 보이는 문제가 재발할 수 있다.

### Persistence Side Effects

Run History, saved Mix, Level2 candidate registry가 서로 다른 경로에 기록된다.
테스트는 temp path를 사용하고 실제 registry / history / saved JSONL을 stage하지
않는다.

### Strategy Metadata Drift

purpose group과 maturity를 UI에서 중복 정의하면 React / fallback이 달라질 수 있다.
Python read model을 단일 source로 유지한다.

### Result Overclaim

높은 performance를 후보 적합성으로 잘못 해석할 위험이 있다. Level1 Gate는 실행,
data readiness, contract freshness만 소유하며 실제 투자 판단은 Level2 / Level3에
남긴다.

### Scope Expansion

Risk-On Momentum 5D runtime 완성, 신규 provider, DB / strategy runtime 재설계는
별도 승인 없이는 이번 task에 포함하지 않는다.

### Frontend Dependency Audit

신규 component의 기존 Vite / React pattern으로 `npm install`한 결과 audit 경고는
moderate 1건, high 1건이다. production build에는 성공했지만 breaking dependency
upgrade는 이번 UI workflow 범위를 벗어나므로 closeout의 남은 위험으로 기록한다.

## Closeout Assessment

- large UI surface 위험은 adapter / pure read model / focused boundary test로 완화했다.
- stable context / mutable decision mount와 callback nested rerun suppression을 실제
  Browser run으로 확인했다.
- persistence side effect는 distinct handler test로 검증했고 실제 QA 중 생성된 run
  history, protected registry, saved JSONL은 stage / commit하지 않는다.
- repository 전체 service contract에는 implementation 전부터 있던 11 failures가
  남아 있다: Sentiment React 1건, Practical Validation / Final Review legacy source
  contract 10건. 이번 Level1 focused / boundary는 모두 통과하며 새 Level1 회귀는 없다.
- Streamlit 로그에는 기존 `use_container_width` deprecation warning이 반복된다.
  current Level1 동작 / layout blocker는 아니며 broad compatibility cleanup 범위다.
- frontend dependency audit moderate 1 / high 1은 production build를 막지 않지만,
  breaking upgrade 전 별도 dependency compatibility task가 필요하다.

## 6차 Corrective Closeout Assessment

- 공통 shell은 UI 계층만 소유하고 strategy key / widget key / payload / runtime /
  Level2 Gate는 기존 Python owner를 유지한다.
- Browser QA actual run으로 Equal Weight와 strict multi-factor handler를 확인했고,
  760px outer overflow는 0이다.
- full service baseline 11 failures와 frontend audit moderate 1 / high 1은 그대로다.
  이번 corrective에서 새 failure나 dependency upgrade는 만들지 않았다.
- QA 중 보호 대상 registry / run history는 runtime side effect로 남아 있으며 commit하지
  않는다. saved JSONL, `.superpowers/`, generated screenshot도 stage 대상이 아니다.
- current regression은 source contract 비중이 높다. 후속으로 Streamlit AppTest 또는
  renderer fake를 추가해 variant 변경 -> family dispatch -> stale 판정을 한 경로로
  검증하면 UI runtime 회귀 방어를 더 강화할 수 있다.

## 7차 Unified React Settings Closeout Assessment

- current primary Single route는 strategy-specific native form을 호출하지 않지만 해당
  renderer 파일은 history/replay compatibility 때문에 남아 있다. 후속 삭제는 replay
  inventory와 migration 증거를 별도 task에서 확보한 뒤 판단해야 한다.
- legacy Quality Snapshot은 pure service compatibility key로 유지한다. current catalog
  allow-list와 primary picker test가 재노출을 막지만 saved/history replay 제거 근거는 없다.
- native multi-select modifier 부담은 adaptive checkbox-card / search-list / selected-chip으로
  해소했다. 다만 검색어가 빈 상태에서 `검색 결과 전체 선택`을 누르면 1,031개 selection
  chip이 생길 수 있어, 대량 전체 선택의 chip virtualization은 후속 성능 범위로 남는다.
- desktop/760px pointer interaction과 CSS `:focus-visible` contract는 확인했다. Browser QA
  runtime이 iframe 안 Tab focus를 이동시키지 못해 실제 keyboard traversal/focus-ring은
  수동 accessibility QA gap으로 남는다.
- repository-wide service contract 11 failures는 pre-7차와 동일하다: Sentiment React 1,
  Final Review 4, Practical Validation 6. 8차 Level1 focused 114 tests와 actual
  Quality/GTAA/large-option Browser QA는 통과했다.
- GTAA 전환 첫 시도에서 한 번 Quality로 복귀했지만 controlled 5-second persistence retry와
  이후 interaction에서는 재발하지 않았다. strategy selection은 app rerun을 계속 사용하므로
  multi-select local-edit와 별개인 이 transient를 후속 Browser 회귀에서 관찰한다.
- frontend dependency audit의 moderate 1 / high 1은 기존 위험으로 남는다. production
  build는 통과했으며 breaking dependency upgrade는 별도 compatibility task가 필요하다.
- QA가 append한 Run History와 기존 modified Practical Validation registry, saved JSONL,
  `.superpowers/`, generated screenshots는 closeout commit에서 제외한다.

## 9차 Deterministic Preset Application Closeout Assessment

- strategy-default profile은 명시적 tuning evidence가 없는 preset에 같은 strategy/variant
  기본 규칙을 적용한다. preset별 최적화 숫자가 새로 검증되면 Python evidence map과 테스트를
  함께 추가해야 하며 React에 직접 값을 넣지 않는다.
- ignored frontend build와 `fileWatcherType none` Python process를 따로 갱신하면 local dev에서
  신·구 contract가 섞일 수 있다. production과 QA는 Python process restart 뒤 같은 source/build
  pair로 확인해야 한다.
- repository-wide service contract 11 failures는 기존 Sentiment 1, Final Review 4,
  Practical Validation 6 source-contract debt다. focused Level1 134 tests는 통과했다.
- actual Browser QA는 GTAA evidence/base, Equal Weight, GRS, Quality+Value Annual을 대표로
  확인했고 모든 named preset family는 pure matrix test로 보완했다. Risk Parity / Dual Momentum
  개별 화면의 별도 screenshot은 만들지 않았다.
- frontend dependency audit moderate 1 / high 1과 actual keyboard traversal/focus-ring 수동 QA
  gap은 기존 위험으로 남는다.
- modified Practical Validation registry, Run History, saved JSONL, `.superpowers/`, generated
  screenshots는 closeout commit에서 제외한다.

## 10차 Result Workspace Planned Risks

- Streamlit component callback 안에서 직접 실행하면 이전 result가 중간 rerun에서 사라져 보일 수
  있다. validated payload를 fragment pending state에 queue하고 previous result/running state를 먼저
  그린 뒤 실행하는 순서를 Browser에서 확인해야 한다.
- strategy family마다 `End Ticker`, `End Balance`, `Next Weight`, `Next Balance` 제공 범위가 다르다.
  equal-weight 추정은 금지하고 explicit weight 또는 supported balance/total contract만 사용한다.
- Portfolio Mix underlying target은 component evidence가 모두 있을 때만 aggregate한다. 일부가
  없으면 component allocation과 partial 표시를 유지한다.
- 새 `run_result_id`는 current bundle, Run History, single/weighted handoff source에 함께 보존해야
  한다. 기존 append-only JSONL row는 migration 또는 rewrite하지 않는다.
- `_render_real_money_details_legacy` 외의 detail helper는 compare/history consumer 가능성이 있으므로
  reference test 없이 broad deletion하지 않는다.
- QA가 registry와 Run History를 append할 수 있지만 protected artifact이므로 stage/commit하지 않는다.

## 10차 Result Workspace Closeout Assessment

- repository-wide service contract에는 Sentiment 1, Final Review 4, liquidity copy 1,
  Practical Validation 6의 baseline 12 failures가 남아 있다. focused Level1 result / decision /
  boundary는 통과했고 신규 Level1 failure는 없다.
- actual Browser execution은 Equal Weight 대표 경로를 확인했다. GTAA, GRS, Risk Parity,
  Dual Momentum, factor variants는 all-family pure result-column matrix로 검증했지만 각 family의
  actual Browser rerun / screenshot은 후속 manual regression gap이다.
- frontend dependency audit moderate 1 / high 1은 production build를 막지 않는다. breaking
  dependency upgrade는 별도 compatibility task가 필요하다.
- CSS `:focus-visible`과 source contract는 있으나 iframe 안 실제 keyboard traversal / focus-ring은
  수동 accessibility QA gap으로 남는다.
- server restart 직후 console의 transient WebSocket / health 오류는 current page app error와
  구분했다. current source 재시작 뒤 component console error는 없었다.

## 11차 Result Interpretation Closeout Assessment

- sparse Benchmark는 없는 날짜를 hover에서 `-`로 보존하지만 SVG path는 제공된 point 사이를
  연결한다. gap 자체를 끊어 표시하는 시각화는 chart dependency를 넓히는 별도 범위다.
- 다음 리밸런싱은 explicit cadence와 마지막 실제 rebalance를 더한 월말 예상이다. 휴일과 거래일을
  보정한 exact execution date 또는 irregular signal schedule은 제공하지 않는다.
- point에는 native SVG title과 tab focus가 있지만 custom tooltip은 pointer 전용이다. keyboard
  tooltip/focus traversal의 실제 accessibility QA는 후속 수동 검증 gap으로 남는다.
- actual Equal Weight read-only 실행 결과로 result component를 검증했다. fresh full-app QA에서
  settings run intent가 새 result mount까지 이어지지 않은 세션이 있어, settings adapter부터 실행까지의
  Browser end-to-end 회귀는 별도 runtime 조사 대상으로 남긴다.
- source/build가 바뀐 뒤 long-running Streamlit process를 재시작하지 않으면 old Python과 new React
  schema가 섞일 수 있다. production QA는 같은 source/build pair로 process를 새로 띄워야 한다.
- repository-wide service contract 12 failures는 기존 Sentiment 1, Final Review 4, liquidity copy 1,
  Practical Validation 6 baseline이다. 이번 11차 focused result / decision / boundary 92개에는 failure가 없다.
