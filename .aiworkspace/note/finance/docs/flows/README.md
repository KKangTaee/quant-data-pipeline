# Finance Flows

Status: Active
Last Verified: 2026-08-17

## Main User Flow

```text
Finance Console `/` 최초 진입
  -> Research > Today
     -> React `오늘의 시장 판단`과 텍스트 신호·위험 분류
     -> 대표 포트폴리오 확정 일봉 곡선과 정규장 중 장중 임시 평가 overlay
     -> Market Research / Portfolio Monitoring 현재 화면으로 이동

Research: Today / Market Research / Institutional Holdings
Portfolio: Portfolio Lab / Portfolio Monitoring
Data: Data Operations
Help: Reference Center
```

Streamlit의 `default=True` page는 등록된 `url_path="today"`와 무관하게 browser root `/`를 소유한다. 따라서 Today의 canonical 최초 진입 주소는 `/`이며 기존 상세 URL은 유지한다.
Today의 차트는 최신 최대 60개 실제 일별 관측을 주봉으로 변환하지 않고 실제 날짜 간격으로 표시한다. 정규장 중에는 확정 곡선을 바꾸지 않고 별도 점선·빈 marker 한 개로 장중 임시 값을 겹친다. 매매 신호가 아니며 React가 반환하는 세 navigation event만 Python Page router가 처리한다. 세부 흐름은 [Today Portfolio Intraday Flow](./TODAY_PORTFOLIO_INTRADAY_FLOW.md)를 본다.
`Research > Market Research`는 Portfolio Lab의 필수 선행 단계가 아니라 Today에서 발견한 질문을 깊게 조사하는 표면이다. `/overview` 안에서 `시장 환경 | 지수 가치평가 | 종목 리서치`를 먼저 고르고, 각각 `경기 국면·물가·정책·선물 매크로·심리·일정 | S&P 500 | 변동 종목·개별 종목`의 8개 canonical view로 이동한다.
`경기 국면`과 `물가·정책`은 시장 환경 아래 같은 깊이의 sibling view다. 물가·정책은 `연말 Core PCE 다섯 상태 -> 다음 발표 준비 -> FOMC 순이동 -> 10년물 동적 전고점 군집 -> 목표 금리 조건부 역산 -> S&P 500 EPS×multiple 조건부 스트레스` 순서로 읽는다. 자동 저항 기준은 읽기 전용이며 별도 USER 기준으로만 복사·저장한다. 측정된 차년도 EPS 수정과 사용자 AI EPS 가정은 분리하고, 사용자 지수 수준은 전역 목표가가 아니라 조건부 scenario다. `READY`가 아니면 저장 확률을 현재 판단으로 표시하지 않고 제한 사유·관측/발표/수집 시각·버전을 보여준다. 날짜가 검증된 annual EPS 빈티지나 공동 거시경로가 없으면 Shiller를 대신 쓰지 않고 equity만 `NOT_AVAILABLE`로 닫는다. 기존 경기 사이클 확률은 이 경로 또는 침체 fallback으로 재사용하지 않는다.
Market Research 상단은 eyebrow·실제 `<h1>`·설명을 full-width editorial header로 두고, family는 divider 위 text tab과 active underline, 선택 family의 local view는 외곽 surface 없는 compact active state로 렌더링한다. 모바일에서도 family와 local view는 desktop과 같은 왼쪽 정렬·underline·pill 디자인을 유지하며, view가 한 줄에 맞지 않으면 자연스럽게 줄바꿈한다. header만 좁은 화면에서 stacked layout으로 바뀌며 drawer, horizontal swipe, sticky navigation은 사용하지 않는다.
`Research > Institutional Holdings`도 Portfolio Lab의 필수 선행 단계가 아니라 delayed SEC 13F institutional holdings를 탐색하는 별도 research surface다.
Sentiment, futures macro, Why It Moved는 판단 보조 정보이며 validation gate, trade signal, monitoring signal을 만들지 않는다.
Sentiment의 1W·1M 카드는 CNN 최근 5/20개 관측 간격과 AAII Bull-Bear Spread 최근 1/4개 주간 관측 간격의 시작값·현재값·변화량·두 축 관계 전환을 source별 실제 날짜와 함께 표시한다. 이 카드는 미래 전망이 아니며 검증된 estimator가 없는 기존 확률 publication gate는 계속 닫혀 있다.
React는 allow-listed view event만 반환하고 Python이 canonical URL/session/legacy normalization과 lazy renderer를 소유한다. bundle이 없을 때는 기존 Streamlit header/navigation이 fallback이다. 상단은 summary cockpit, page-global market-session banner, contextual Reference, 운영 진단 패널을 반복하지 않으며 기준일·자료 상태·refresh action은 선택된 module이 소유한다.
S&P 500 view는 최근 60개월 후행 PER 상대 구간과 FOMC SEP 기반 EPS/SPX 시나리오를 두 React 그래프로 읽는다. 36개월은 민감도이며, actual As-Reported TTM EPS가 없으면 예상 지수 숫자를 표시하지 않는다.
Market Movers의 `개별 종목 분석`은 선택 symbol을 검증한 뒤 같은 page의 U.S. Stock Research로 넘기며 provider fetch나 write를 실행하지 않는다.
`Futures Monitor`와 `Sector / Industry` standalone tab은 current primary navigation이 아니며, 관련 데이터는 Futures Macro / Market Movers의 context evidence로 읽는다.

화면 경계가 code layer / storage boundary와 섞일 때는 [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md)를 먼저 확인한다.

## Market Research Futures Macro Flow

`Research > Market Research > 시장 환경 > 선물 매크로`는 저장된 완료 5분봉으로 선택 구간의 가격 반응과 주식시장에 대한 지지·부담을 읽는다. 경제자료의 월간 경기국면과 기준이 다르며 예측 확률·가격 목표·매매 신호를 제공하지 않는다.

- 비교 구간: `미국장 마감 이후`는 마지막 공통 관측 이전의 공식 미국 현물 정규장 마감부터, `최근 1시간`은 마지막 공통 관측 전 60분부터 비교한다. 모든 값은 같은 시작·종료 시각의 완료봉 가격 변화율이다. 한국시간의 비교 시작·마지막 관측·조회 시각과 조회 당시 관측 지연을 명시한다. 실시간 현재가 등락률이나 현물 일간 수익률이 아니다.
- 가격: S&P 500·나스닥 100·10년 국채·금·WTI 원유 선물과 고정 5개 통화선물의 역방향 동일 가중 평균인 자체 달러 대용지표를 표시한다. 국채선물은 금리 bp가 아니고 자체 달러 지표는 DXY가 아니다.
- 두 확인 결과: 실제 ES/NQ 값으로 동반 상승·동반 하락·엇갈림·한쪽 보합·동반 보합을 구분하고, 실제 국채·달러의 9가지 방향 조합별 지지·부담·상충 근거를 설명한다. 색상과 판정 문구를 함께 사용한다. 주가 방향과 국채·달러 조합의 관계를 상단에서 요약한다.
- 이전 관측 비교: 종료 시각 T의 1시간 전 자료를 직접 사용한다. 마감 이후는 같은 마감 기준점에서 T−60분까지, 최근 1시간은 T−120분→T−60분의 겹치지 않는 이전 구간이다. 해당 구간의 값과 판정을 펼쳐 확인할 수 있다. 두 관측에서 같은 조합이어도 중간 모든 시점의 지속이나 다음 시간의 방향을 뜻하지 않는다.
- 누락·지연: 정확한 끝점이 없으면 보간하지 않는다. 이전 구간 공백은 변화 비교만 보류한다. 통화 누락은 달러 바스켓 비중을 바꾸지 않고, 유효한 주가지수 동행은 따로 표시한다. 현재 관측이 오래되면 저장된 수치와 과거 구간을 보존하되 현재 판정을 보류한다.
- 동작: `최신 데이터 반영` 하나로 수집 후 DB 관측을 읽는다. 별도 저장자료 다시 읽기 버튼은 없다. 화면 진입·구간 전환은 provider를 호출하지 않는다. React와 Streamlit fallback은 동일 read model의 시각·가격·판정·근거를 사용한다.
- 근거: 구성 지표·수식·roll 위험·부호 해석 한계는 `지표 구성과 계산 기준`, 다른 지수·가격 관측은 `추가 관측 근거`에 둔다. 기존 daily family·forecast history는 backend 연구/호환용이며 현재 화면의 장중 확률로 사용하지 않는다.

## Backtest Selection Flow

| Step | What Happens | Main Files |
|---|---|---|
| Backtest Analysis | 단일 전략, compare, saved mix로 후보 source 생성 | `app/web/backtest_analysis.py`, `app/web/backtest_single_*.py`, `app/web/backtest_compare/` |
| Practical Validation | 후보 source를 12개 진단과 module gate로 검증하고, Gate 미통과 저장-only row는 audit trail로만 남긴다 | `app/web/backtest_practical_validation/` |
| Final Review | Practical Validation Gate를 통과한 후보만 source picker에 표시하고 최종 select / hold / reject / re-review 판단 | `app/web/backtest_final_review/` |
| Portfolio Monitoring | 선정 이후 성과 재확인과 read-only monitoring / recheck signal 확인 | `app/web/final_selected_portfolio_dashboard*.py` |

## Practical Validation Provider Flow

```text
Data > Data Operations
  -> ETF provider source map discovery
  -> ETF operability / holdings / exposure snapshot
  -> FRED macro market-context snapshot
  -> symbol lifecycle evidence
     (SEC Form 25 actual delisting evidence,
      Nasdaq current listing snapshot,
      SEC CIK / ticker cross-check,
      computed repeated-observation summary)
  -> MySQL
  -> finance/loaders/provider.py / macro.py / universe.py
  -> Practical Validation diagnostics
```

## Data Operations Flow

```text
Data > Data Operations
  -> 데이터 준비
     -> Market Research / Portfolio Lab / Institutional Holdings / Practical Validation
     -> 필요한 action의 목적·순서·주의사항 확인
     -> 설정 열기
  -> 고급 도구
     -> 선택 action의 기존 form / preflight 자동 확장
     -> 사용자 명시 클릭
     -> 기존 Ingestion -> DB -> Loader -> UI 경계
  -> 실행 이력
     -> 시각 / 작업 / 목적 / 상태 / 범위 / 결과 / 다음 행동
     -> partial / failed이면 같은 설정으로 복귀
```

공식 XLSX/ICS는 `공식 파일`, 읽기 전용 진단과 bounded 수동 보강은 `문제 복구`에서 시작한다.
모든 active action은 기존 registry/form/dispatcher를 한 벌만 유지하며 consumer workflow가 action을 복제하지 않는다.
Runtime/Build, raw log, failure CSV, absolute artifact path, full payload는 기본 user flow가 아니다.

## Flow Rules

- Practical Validation result는 최종 투자 승인 기록이 아니다.
- Practical Validation의 `검증 결과 저장(기록용)`은 Final Review 후보 등록이 아니다. Final Review에는 Gate를 통과한 result만 표시한다.
- Practical Validation의 최신 runtime replay 결과는 현재 세션에서 사용자가 직접 실행한 뒤에만 표시한다.
- Final Review decision도 broker order나 auto rebalance가 아니다.
- Portfolio > Portfolio Monitoring은 read-only monitoring surface이며 monitoring log 자동 저장, live approval, broker order, auto rebalance를 하지 않는다.
- Market Research의 Sentiment, Futures Macro, Why It Moved는 시장 배경 / 조사 단서이며 Practical Validation PASS / BLOCKER가 아니다.
- 부족 provider data는 Practical Validation Provider Gaps에서 확인하고, 수집 가능한 항목은 ingestion job을 통해 보강한다.
- Data Operations의 current listing snapshot, SEC identity cross-check, computed snapshot lifecycle row는 survivorship PASS 근거가 아니다. Form 25 delisting row도 delisting evidence이며, Form 25 부재를 active listing proof로 해석하지 않는다.

## Detailed Flow Docs

| Need | Document |
|---|---|
| 화면 stage와 code / storage boundary가 섞일 때 | [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md) |
| 투자 대가 / 기관별 delayed SEC Form 13F portfolio 탐색 | [INSTITUTIONAL_PORTFOLIOS_FLOW.md](./INSTITUTIONAL_PORTFOLIOS_FLOW.md) |
| Backtest UI, history, saved replay, Practical Validation, Final Review 화면 흐름 | [BACKTEST_UI_FLOW.md](./BACKTEST_UI_FLOW.md) |
| Backtest Analysis 1단계 closeout 현재 상태 | [BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md](./BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md) |
| 후보 생성부터 최종 선정 후 dashboard까지의 Portfolio Selection 흐름 | [PORTFOLIO_SELECTION_FLOW.md](./PORTFOLIO_SELECTION_FLOW.md) |
| Final Review selected-route waiver 허용 조건 | [STRUCTURED_WAIVER_POLICY.md](./STRUCTURED_WAIVER_POLICY.md) |
