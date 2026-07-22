# Today Home And Navigation IA Recommendation

Status: Implemented; Follow-ups Deferred
Last Updated: 2026-07-22

## Recommended Direction

Finance Console의 새 기본 진입점으로 `Today`를 추가한다.

`Today`는 사용자가 첫 업무로 선택한 `오늘의 시장 판단`을 완결하는 read-only 화면이다. 기존 Overview, Institutional Portfolios, Backtest, Portfolio Monitoring, Ingestion, Reference 내부 화면은 그대로 유지하고, 첫 화면과 상위 navigation만 목적 중심으로 정리한다.

첫 화면은 시장 판단을 주인공으로 두고 대표 포트폴리오 한 개를 두 번째 영역으로 표시한다. 실행 job, raw status, 저장 row, 로그 같은 운영 진단값은 첫 화면의 주인공으로 올리지 않는다.

## Decision Scope

- Implemented: 신규 `Today` 기본 화면, 목적 중심 상위 navigation, 기존 화면으로 이동하는 CTA와 URL compatibility.
- Implementation record: `.aiworkspace/note/finance/tasks/active/today-home-purpose-navigation-v1-20260722/`.
- Longer roadmap option: Overview를 `Market Intelligence / Equity Research`로 실제 분리.
- Not approved / parking lot: 기존 탭 내부 전면 개편, Backtest stage 독립 페이지화, live trading·broker·auto rebalance, 운영 진단 dashboard.

## Approved Information Architecture

```text
Research
  Today                    # 신규, 기본 진입
  Market Research          # 기존 Overview, 내부 기능 유지
  Institutional Holdings   # 기존 Institutional Portfolios, 내부 기능 유지

Portfolio
  Portfolio Lab            # 기존 Backtest, 3-stage workflow 유지
  Portfolio Monitoring     # 기존 화면 유지

Data
  Data Operations          # 기존 Ingestion, 내부 기능 유지

Help
  Reference Center         # 기존 Reference, 내부 기능 유지
```

기존 URL path는 모두 유지한다.

- `/overview`
- `/institutional-portfolios`
- `/ingestion`
- `/backtest`
- `/selected-portfolio-dashboard`
- `/reference`

신규 기본 path만 `/today`로 추가한다. 기존 Reference destination key와 Backtest 내부 stage routing은 변경하지 않는다.

## Today Screen Design

### 1. Today Header

- 기준 날짜와 마지막 저장 자료 시각
- `오늘의 시장 판단`이라는 화면 목적
- 일부 source가 stale 또는 unavailable이면 짧은 제한 표시
- build marker, raw job status, registry count는 기본 화면에서 제외

### 2. 오늘의 시장 브리프

첫 영역은 하나의 결론과 그 결론을 구성하는 근거를 순서대로 보여준다.

- 한 줄 시장 상태: 기존 read model의 상태를 요약하되 공식 적정가, 확정 예측, 매매 신호로 표현하지 않는다.
- 경제 국면: Economic Cycle의 현재 판단과 publication 상태.
- 주식시장 가치평가: S&P 500 trailing multiple / earnings scenario의 현재 범위와 자료 제한.
- 단기 재가격화: Futures Macro의 observed regime와 공개 가능한 conditional outlook.
- 심리: CNN / AAII의 최신 저장 관측과 freshness.
- 오늘 일정: FOMC, macro release, earnings 등 현재 Events snapshot의 중요 일정.
- 주의할 점: 서로 충돌하는 신호, stale source, unavailable evidence를 최대 세 항목으로 정리.

브리프는 새로운 독립 시장 점수를 만들지 않는다. 기존 서비스 결과를 compact하게 설명하는 aggregation layer다.

### 3. 대표 포트폴리오 오늘

대표 포트폴리오는 `monitoring_portfolio_group.is_default = 1`인 기존 group 한 개다. 새로운 저장 파일이나 별도 portfolio registry를 만들지 않는다.

- 포트폴리오 이름
- 현재 평가액
- 오늘 수익률과 누적 수익률
- benchmark 대비 성과가 계산 가능한 경우 그 차이
- 상승 기여 종목과 하락 부담 종목
- 현재 review/주의 상태가 있는 종목 또는 전략
- 전체 상세를 여는 `Portfolio Monitoring` 이동

default group이 없으면 기존 default-group 생성 계약을 사용한다. group은 있지만 active item이 없으면 수익률을 만들지 않고 Portfolio Monitoring에서 종목이나 전략을 추가하도록 안내한다.

대표 포트폴리오 변경 UI가 필요하면 기존 `is_default` 필드를 전환하는 명시적 command를 Portfolio Monitoring에 추가한다. 이를 위해 새 DB column이나 JSONL registry를 만들지 않는다.

### 4. 다음 확인

최대 세 개의 행동만 둔다.

- 시장 근거 자세히 보기 → `Market Research`
- 영향이 큰 종목 조사 → 기존 Overview의 Market Movers 또는 미국 개별주식 경로
- 포트폴리오 전체 점검 → `Portfolio Monitoring`

Today에서 ingestion을 실행하거나 Final Review 결정을 저장하지 않는다. 데이터 보강이 필요한 경우 owning surface로만 안내한다.

## Component And Ownership Design

### App Shell

- `app/web/streamlit_app.py`: 신규 Today page 등록, default page 변경, group label과 display title 변경.
- 기존 page object와 URL path는 유지해 deep link 회귀를 피한다.

### Today Read Model

- 신규 Streamlit-free service가 existing Overview / Portfolio Monitoring service output을 compact Today payload로 조합한다.
- Today page는 기존 대형 React component나 tab renderer를 직접 중첩하지 않는다.
- source별 계산과 저장 책임은 기존 service/loader에 남기고 Today service는 projection과 fallback만 소유한다.

### Today Presentation

- 신규 page renderer와 compact React component 또는 동일 payload의 Streamlit fallback을 둔다.
- 화면은 `시장 브리프 → 대표 포트폴리오 → 다음 확인` 순서의 한 shell로 렌더링한다.
- desktop과 mobile에서 같은 정보 우선순위를 유지한다.

### Representative Portfolio

- Portfolio Monitoring read model은 `active_group_id=None`일 때 기존 default group을 선택한다.
- Today는 동일 계약을 사용해 별도 portfolio 계산 경로를 만들지 않는다.
- Today의 read path는 portfolio group, item, valuation, diagnosis source를 수정하지 않는다.

## Data Flow And Boundaries

```text
Existing ingestion jobs
  -> MySQL
  -> existing loaders / Overview services
  -> Today aggregation service
  -> Today read-only UI

MySQL monitoring_portfolio_group(is_default)
  -> existing Portfolio Monitoring repository / read model
  -> Today representative portfolio projection
  -> Today read-only UI
```

- UI render 중 provider, FRED, SEC 또는 외부 page를 직접 fetch하지 않는다.
- Today 화면 진입만으로 ingestion job, registry write, monitoring log write를 실행하지 않는다.
- macro, sentiment, futures, market mover 정보는 context이며 validation gate나 monitoring signal이 아니다.
- `NOT_RUN`, stale, unavailable 상태를 정상 또는 pass로 바꾸지 않는다.
- live approval, broker order, auto rebalance 경계를 유지한다.

## Error And Empty States

- 일부 시장 source만 실패하면 사용 가능한 영역은 유지하고 해당 근거만 `자료 없음/오래됨`으로 표시한다.
- 핵심 시장 근거가 부족하면 합성 결론을 만들지 않고 `현재 자료로 종합 판단 보류`를 표시한다.
- 대표 포트폴리오가 비어 있으면 0% 수익률을 만들지 않고 설정 안내와 Portfolio Monitoring 이동만 보여준다.
- portfolio valuation 일부 종목이 missing/stale이면 평가 범위와 누락을 숨기지 않는다.
- component load가 실패하면 같은 section order의 compact read-only fallback을 제공한다.

## Verification Contract

### Automated

- Today aggregation pure-service tests
- complete / partial / unavailable market evidence cases
- default portfolio / empty group / partial valuation cases
- no remote fetch and no write-on-render boundary tests
- existing route and Reference destination regression tests
- `git diff --check` and relevant Python compile/import checks

### Browser QA

- actual DB-backed desktop view
- 760px and 420px responsive view
- Today default landing and all three next-action links
- Market Research, Institutional Holdings, Portfolio Lab, Portfolio Monitoring, Data Operations, Reference Center route continuity
- stale/unavailable and empty-portfolio states
- 최종 응답에 QA screenshot 한 장 첨부

## What To Build First

1. Today read-model contract와 fixture tests
2. Today page shell / compact presentation
3. representative default portfolio projection
4. top navigation regroup / rename while preserving URL paths
5. Reference copy / docs alignment and Browser QA

## What To Defer

- Overview 내부 5개 탭 재디자인
- Market Context 안의 경제 사이클 / S&P 500 / 미국 개별주식 재배치
- Market Research와 Equity Research의 실제 page split
- Institutional Portfolios, Backtest, Portfolio Monitoring, Ingestion 내부 UI 변경
- Today에서 데이터 수집 실행
- multi-portfolio aggregate view

## Decision Checkpoint

사용자 승인 뒤 written spec과 implementation plan을 거쳐 전체 `4/4차` 구현·actual Browser QA를 완료했다. 다음 선택지는 실제 사용 후 Overview의 Market / Equity Research 분리가 여전히 필요한지 재평가하는 것이다.

## Evidence Summary

- 현재 navigation code는 `Workspace`에 Overview, Institutional Portfolios, Ingestion, Backtest를 함께 두고 `Operations`에는 Portfolio Monitoring 하나만 둔다.
- Overview는 Market Context, Market Movers, Futures Macro, Sentiment, Events를 소유하며 Market Context 안에 경제 사이클, S&P 500, 미국 개별주식이 다시 들어 있다.
- Backtest는 이미 후보 분석, 실전 검증, 최종 검토의 3-stage workflow다.
- Ingestion은 자체 설명과 코드상 외부 자료를 DB에 저장하는 운영 콘솔이다.
- Portfolio Monitoring group schema에는 대표 선택에 재사용할 수 있는 `is_default`가 이미 있다.
- 사용자는 기본 업무를 `오늘의 시장 판단`, 첫 화면 portfolio 범위를 대표 포트폴리오 한 개로 확정했고, 기존 각 탭 내부의 전면 개편은 원하지 않았다.

## Risks And Unknowns

- source별 freshness/as-of 형식 차이는 compact projection에서 정규화했고 future event 날짜는 header as-of에서 제외했다.
- Today는 기존 cached loader를 직렬로 읽는다. actual Browser에서 완료를 확인했지만 별도 latency budget과 장기 성능 측정은 후속이다.
- default group을 사용자가 변경하는 현재 command가 없으므로 대표 변경 UX가 필요하면 기존 DB field를 안전하게 전환하는 command/test가 필요하다.
- 시장 브리프 문구가 지나치게 강하면 context를 매매 신호로 오해할 수 있으므로 상태와 근거를 분리해야 한다.
