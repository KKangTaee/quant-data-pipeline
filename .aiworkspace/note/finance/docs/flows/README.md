# Finance Flows

Status: Active
Last Verified: 2026-08-11

## Main User Flow

```text
Finance Console `/` 최초 진입
  -> Research > Today
     -> React `오늘의 시장 판단`과 텍스트 신호·위험 분류
     -> 대표 포트폴리오 확정 일봉 곡선과 정규장 중 장중 임시 평가 overlay
     -> Market Context / Market Movers / Portfolio Monitoring 기존 화면으로 이동

Research: Today / Market Research / Institutional Holdings
Portfolio: Portfolio Lab / Portfolio Monitoring
Data: Data Operations
Help: Reference Center
```

Streamlit의 `default=True` page는 등록된 `url_path="today"`와 무관하게 browser root `/`를 소유한다. 따라서 Today의 canonical 최초 진입 주소는 `/`이며 기존 상세 URL은 유지한다.
Today의 차트는 최신 최대 60개 실제 일별 관측을 주봉으로 변환하지 않고 실제 날짜 간격으로 표시한다. 정규장 중에는 확정 곡선을 바꾸지 않고 별도 점선·빈 marker 한 개로 장중 임시 값을 겹친다. 매매 신호가 아니며 React가 반환하는 세 navigation event만 Python Page router가 처리한다. 세부 흐름은 [Today Portfolio Intraday Flow](./TODAY_PORTFOLIO_INTRADAY_FLOW.md)를 본다.
`Research > Market Research`는 Portfolio Lab의 필수 선행 단계가 아니라 Today에서 발견한 질문을 깊게 조사하는 표면이다. `/overview` 안에서 `시장 환경 | 지수 가치평가 | 종목 리서치`를 먼저 고르고, 각각 `경제 사이클·선물 매크로·심리·일정 | S&P 500 | 변동 종목·개별 종목`의 7개 canonical view로 이동한다.
경제 사이클 view 안의 `경기 국면 | 물가·정책 경로` 선택기는 기존 경기 국면을 기본값으로 유지한다. 신규 경로는 `연말 Core PCE 다섯 상태 -> 다음 발표 준비 -> FOMC 순이동 -> 10년물 동적 전고점 군집 -> 목표 금리 조건부 역산 -> S&P 500 EPS×multiple 조건부 스트레스` 순서로 읽는다. 자동 저항 기준은 읽기 전용이며 별도 USER 기준으로만 복사·저장한다. 측정된 차년도 EPS 수정과 사용자 AI EPS 가정은 분리하고, 사용자 지수 수준은 전역 목표가가 아니라 조건부 scenario다. `READY`가 아니면 저장 확률을 현재 판단으로 표시하지 않고 제한 사유·관측/발표/수집 시각·버전을 보여준다. 날짜가 검증된 annual EPS 빈티지나 공동 거시경로가 없으면 Shiller를 대신 쓰지 않고 equity만 `NOT_AVAILABLE`로 닫는다. 기존 경기 사이클 확률은 이 경로 또는 침체 fallback으로 재사용하지 않는다.
Market Research 상단은 eyebrow·실제 `<h1>`·설명을 full-width editorial header로 두고, family는 divider 위 text tab과 active underline, 선택 family의 local view는 외곽 surface 없는 compact active pill로 렌더링한다. desktop에서는 module 본문과 같은 축을 쓰고 420px에서는 stacked header·family 3열·view 2열로 접히며, drawer와 sticky navigation은 사용하지 않는다.
`Research > Institutional Holdings`도 Portfolio Lab의 필수 선행 단계가 아니라 delayed SEC 13F institutional holdings를 탐색하는 별도 research surface다.
Sentiment, futures macro, Why It Moved는 판단 보조 정보이며 validation gate, trade signal, monitoring signal을 만들지 않는다.
React는 allow-listed view event만 반환하고 Python이 canonical URL/session/legacy normalization과 lazy renderer를 소유한다. bundle이 없을 때는 기존 Streamlit header/navigation이 fallback이다. 상단은 summary cockpit, page-global market-session banner, contextual Reference, 운영 진단 패널을 반복하지 않으며 기준일·자료 상태·refresh action은 선택된 module이 소유한다.
S&P 500 view는 최근 60개월 후행 PER 상대 구간과 FOMC SEP 기반 EPS/SPX 시나리오를 두 React 그래프로 읽는다. 36개월은 민감도이며, actual As-Reported TTM EPS가 없으면 예상 지수 숫자를 표시하지 않는다.
Market Movers의 `개별 종목 분석`은 선택 symbol을 검증한 뒤 같은 page의 U.S. Stock Research로 넘기며 provider fetch나 write를 실행하지 않는다.
`Futures Monitor`와 `Sector / Industry` standalone tab은 current primary navigation이 아니며, 관련 데이터는 Futures Macro / Market Movers의 context evidence로 읽는다.

화면 경계가 code layer / storage boundary와 섞일 때는 [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md)를 먼저 확인한다.

## Overview Futures Macro Flow

`Research > Market Research > Futures Macro`는 완료 futures daily OHLCV와 활성 세션의 저장된 latest closed 5m OHLCV를 읽어 현재 1D / 5D / 20D 변화, 교차자산 재가격화와 조건부 시나리오를 확인하는 단기 매크로 레이더다. 장기 경제사이클, provider run 진단, 확정 예측, trading signal 화면이 아니다.

기본 화면의 정보 소유권은 다음처럼 유지한다.

- Current regime: `1D·지금 새로 생긴 변화`, `5D·현재 단기 방향`, `20D·기존 배경과의 관계`로 읽는다. 거래 중이면 latest closed 5m로 임시 재계산하고, 비거래 구간이거나 freshness/coverage gate를 통과하지 못하면 마지막 완료 세션으로 fallback한다. 이 세 카드는 관측이며 미래 확률이 아니다.
- Market repricing: 위험선호·금리 부담·달러 압력·물가 압력 네 핵심축 가운데 평소 변동 범위를 벗어난 가장 강한 5D 축을 중심 해석으로 선택한다. 다른 핵심축은 정규화된 위험 방향에 따라 뒷받침·반대 근거로 나누고, 성장 기대와 방어 수요는 구성 종목 중복 때문에 독립 신뢰도 개수가 아닌 맥락 근거로만 쓴다. 5D 핵심축이 중립이어도 1D 핵심축이 뚜렷하면 `1D 새 충격`으로 보존한다.
- Conditional scenario: 중심 해석이 이어질 조건, 무효화될 조건과 민감 자산을 제공한다. 이는 확률, 5D 가격 목표, 매수·매도 신호가 아니다. 기존 completed-daily forecast validation과 immutable history는 호환성·shadow research용 backend artifact로 보존하지만 primary UI나 제품 약속으로 사용하지 않는다.
- Pattern evidence: 선물군별 1D·5D·20D 방향 정렬과 최근 체제 이력을 현재 해석의 근거로 제공한다. 과거 유사 구면과 미래 terminal/range 계산은 backend 호환성·연구용으로 보존하며 기본 화면의 미래 경로 또는 확률로 노출하지 않는다.
- Asset pathways: 주식 위험선호, 금리 부담, 달러 압력, 안전자산, 원자재·물가는 전체 시장 체제의 보조 근거이며 독립 추천으로 승격하지 않는다.
- Disclosure: React 방법론에는 관측 원천, 1D·5D·20D 범위, family coverage와 continuous futures roll 한계를 둔다. 하단 `원본 데이터 / 계산 추적`은 원시 점수와 daily candle 검산용 appendix로 남긴다.

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
