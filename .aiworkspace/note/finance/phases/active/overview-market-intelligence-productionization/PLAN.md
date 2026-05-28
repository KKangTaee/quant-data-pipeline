# Overview Market Intelligence Productionization Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

1차 Overview Market Intelligence는 이미 Market Movers, Sector / Industry, FOMC, earnings prototype을 한 화면에서 보여준다. 하지만 이 상태는 “쓸 수 있는 prototype”에 가깝다.

정식 기능으로 부르려면 운영자가 매일 믿고 refresh할 수 있어야 하고, 데이터가 오래됐는지 / 부족한지 / provider estimate인지 즉시 판단할 수 있어야 한다. 특히 earnings calendar는 무료 source 특성상 날짜 변경, 누락, provider delay가 흔하기 때문에 lifecycle과 신뢰도 표시가 더 필요하다.

이 phase의 목적은 1차 prototype을 DB-first, 무료 데이터 원칙을 유지한 채 운영 가능한 정식 feature로 끌어올리는 것이다.

## 결론: 몇 차까지 필요한가?

권장 개발 흐름은 총 4차다.

| 차수 | 이름 | 목표 | 상태 |
|---|---|---|---|
| 1차 | Prototype / First Build | Overview tab, Market Movers, Sector / Industry, FOMC, earnings prototype | Complete |
| 2차 | Production Baseline | refresh 상태, stale 기준, diagnostics, event lifecycle의 운영 안정화 | Next |
| 3차 | Earnings / Events Production | earnings official-source 검증, stale estimate cleanup, wider low-frequency collection | Planned |
| 4차 | Product UX / Automation | heatmap/treemap, calendar usability, refresh cadence guide, operator acceptance polish | Planned |

최소 정식화 기준은 3차까지다. 다만 사용자가 매일 여는 product surface로 보기 좋게 만들려면 4차까지 진행하는 것이 좋다.

## Scope Lock

포함한다.

- Overview refresh 상태와 stale/partial/fail 표시 개선
- Market Movers / Events diagnostics를 운영자가 바로 읽을 수 있게 정리
- `market_event_calendar` event lifecycle 보강
- earnings free-source row의 estimate cleanup / source confidence / missing reason 개선
- low-frequency earnings collection cadence 설계와 구현
- Overview visual polish: heatmap/treemap 또는 dense ranking visual
- runbook / QA / acceptance checklist 정리

포함하지 않는다.

- 유료 API 도입
- broker order, live approval, auto rebalance
- Overview render 중 직접 웹 scraping
- full coverage earnings scan을 장중 버튼으로 실행
- Top movers를 자동 투자 후보로 승격

## Production Acceptance

정식화 완료 조건:

- 운영자가 `Refresh` 후 success / partial / fail과 다음 조치 reason을 볼 수 있다.
- Market Movers daily refresh는 stale 상태와 최신 snapshot 시간을 명확히 표시한다.
- Events는 FOMC와 earnings를 섞어 보되 source, confidence, collected time, stale estimate 여부를 구분한다.
- earnings 수집은 default가 bounded / low-frequency이며, full coverage heavy scan을 UI에서 우발적으로 실행하지 않는다.
- 서비스 계층은 Streamlit-free이고, Overview render는 DB만 읽는다.
- Browser smoke와 service contract tests로 주요 화면과 read model을 검증한다.

## Next Task

첫 개발 task는 `Task 2-01 Refresh State And Diagnostics Baseline`이다.
