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
