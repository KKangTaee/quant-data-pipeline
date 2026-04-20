# Playwright Market Research Playbook (2026-03-31)

## 목적

이 문서는 `Playwright`를 활용해 공개 웹 소스에서 시장/기업 정보를 조사하고,
아래 사용자가 제시한 기관형 키워드를
**실행 가능한 공개정보 리서치 카테고리**로 재해석한 뒤,
각 카테고리에 대해
`3단계 수집 -> 해석 -> 정리` 흐름을 고정하는 플레이북이다.

다만 반복적으로 운영할 리서치라면
기존 3단계만으로는 부족할 수 있다.
특히 실제 운용에서는 아래가 자주 빠진다.

- 질문과 의사결정 범위의 사전 고정
- 시점 정합성 검증
- source provenance 관리
- 갱신 주기와 재현성 관리

그래서 이 문서는
기존 3단계를 **경량형 core flow**로 유지하되,
반복 조사에는 `사전 프레이밍 + 사후 검증/갱신`을 추가한
**운영형 5단계 보강안**도 함께 제시한다.

이번 문서의 핵심 전제는 명확하다.

- `골드만삭스급`, `모건스탠리`, `JP모건`, `블랙록`, `시타델`, `르네상스`, `맥킨지` 같은 표현은
  **실제 내부 proprietary 리서치 기법에 접근한다는 뜻이 아니다.**
- 대신
  - 종목 스크리닝
  - DCF 가치평가
  - 실적 분석
  - 포트폴리오 구성
  - 기술적 분석
  - 배당/현금흐름 전략
  - 경쟁사 분석
  - 패턴 탐지
  - 매크로 영향평가
  같은 **공개 소스로 재현 가능한 조사 테마**로 해석한다.
- 따라서 이 문서는
  **불법 우회, 유료 리포트 크롤링, 사설 단말기 데이터 재배포**
  를 다루지 않는다.

원 요청의 번호는 `8`번 항목이 없이
`1, 2, 3, 4, 5, 6, 7, 9, 10`
순서로 주어졌으므로,
아래도 그 번호 체계를 그대로 유지한다.

---

## Playwright가 적합한 이유

`Playwright`는 아래 같은 경우에 특히 유용하다.

1. 동적 페이지
   - IR 사이트의 `Earnings`, `Presentations`, `Filings` 탭
   - ETF holdings 테이블
   - 거래소 listing/filter UI
2. 반복 수집
   - 같은 구조의 페이지를 분기/월별로 반복 방문
   - PDF/CSV 다운로드 링크 추적
3. 증빙 확보
   - 어떤 URL에서 어떤 날짜의 자료를 봤는지
   - 스크린샷, HTML snapshot, 다운로드 파일 이름을 남길 수 있음

반대로 아래는 브라우저 자동화보다
API 또는 직접 다운로드가 더 낫다.

- SEC EDGAR raw filing retrieval
- 시계열 macro data bulk download
- 자사 DB에 이미 있는 OHLCV/factor 재사용

즉 실무적으로는:

- `공개 API/CSV가 있으면 API 우선`
- `동적 UI만 열려 있으면 Playwright`
- `둘 다 있으면 API를 원본, Playwright를 보조 증빙/메타 수집용`

으로 가는 편이 가장 안정적이다.

---

## 공통 3단계 조사 프레임

모든 카테고리는 아래 3단계로 통일하면 관리가 쉽다.
이 구조는 빠른 탐색과 1회성 메모에 적합하다.

### 1단계. Source Map / 수집 범위 고정

목표:
- 무엇을 어디서 가져올지 먼저 고정한다.

수집 대상:
- 공식 filings
- investor relations 발표 자료
- 거래소/ETF/fund holdings
- 거시지표
- 가격/거래량/변동성 시계열

이 단계 산출물:
- 조사 질문 1개
- 공식 소스 URL 목록
- 기간 범위
- 다운로드 파일 목록
- source 메타데이터
  - `url`
  - `accessed_at`
  - `document_date`
  - `ticker`
  - `form_type`
  - `period`

### 2단계. Structured Parse / 정형화

목표:
- 모은 자료를 비교 가능한 구조로 바꾼다.

핵심 작업:
- 표 추출
- 실적/가이던스/세그먼트 문장 분리
- holdings/weights/sector/region 정리
- price/macro/event 시계열 정렬
- 기업/기간/문서유형 기준 정규화

이 단계 산출물:
- 정형 테이블
- 핵심 KPI 요약
- category별 체크리스트 결과
- 불확실성 / 누락 항목

### 3단계. Synthesis / 판단 메모

목표:
- 자료를 읽는 데서 멈추지 않고
  실제 판단 가능한 메모로 바꾼다.

핵심 작업:
- peer 비교
- 과거 대비 변화율 비교
- bull/base/bear 시나리오 작성
- 신호와 반례 동시 기록
- 시점 정합성 검증
  - filing 시점 이전 정보 사용 금지
  - look-ahead bias 방지

이 단계 산출물:
- 1페이지 summary
- longlist / shortlist / reject list
- valuation band
- earnings takeaways
- portfolio proposal
- macro watchpoints

---

## 반복 리서치용 운영형 5단계 보강안

같은 주제를 여러 번 조사하거나,
향후 자동화/비교/백테스트 연결까지 염두에 둔다면
아래 5단계가 더 안전하다.

### 0단계. Research Brief / 질문과 판단계약 고정

목표:
- 무엇을 결정하려는 조사인지 먼저 고정한다.

왜 필요한가:
- 같은 자료를 봐도
  `종목 발굴`, `실적 해석`, `가치평가`, `자산배분`
  는 질문이 다르다.
- 질문이 안 고정되면
  자료는 많이 모으고 판단은 흐려진다.

최소 고정 항목:
- 조사 질문 1문장
- 최종 산출물 유형
  - screening shortlist
  - DCF memo
  - earnings review
  - portfolio proposal
  - macro impact map
- 대상 universe
- 기준 시점
  - `as_of_date`
  - `accessed_at`
- 제외 범위
  - 유료 리포트 제외 여부
  - 비공식 2차 요약 제외 여부
  - 특정 자산군 제외 여부

권장 산출물:
- `research_brief.md`

### 1단계. Source Map / 수집 범위 고정

기존 3단계의 1단계와 동일하다.

추가 보강:
- source tier를 같이 적는다.
  - `tier1`: 규제기관 / 발행사 / 거래소 원문
  - `tier2`: 운용사 methodology / holdings / factsheet
  - `tier3`: 2차 가공 데이터
- 공식 원문이 있으면
  2차 가공본만으로 끝내지 않는다.

### 2단계. Structured Parse / 정형화

기존 3단계의 2단계와 동일하다.

추가 보강:
- entity key를 ticker만 쓰지 않는다.
- 아래 canonical key를 함께 남긴다.
  - `ticker`
  - `cik`
  - `accession_no`
  - `filing_date`
  - `accepted_at`

### 3단계. Synthesis / 판단 메모

기존 3단계의 3단계와 동일하다.

추가 보강:
- 결론과 함께 반대 시나리오를 반드시 남긴다.
- 즉
  `왜 좋아 보이는가`와
  `무엇이 이 판단을 깨는가`
  를 같이 적는다.

### 4단계. Validation / 반증 검토 / 갱신 계획

목표:
- 만든 메모가 시점상 맞는지,
  출처상 방어 가능한지,
  다음 조사에서도 재사용 가능한지 확인한다.

핵심 점검:
- source provenance 확인
- 숫자 상충 여부 확인
- filing acceptance 시각 확인
- macro series revision 여부 확인
- 결론 반증 포인트 정리
- 다음 refresh cadence 결정

권장 산출물:
- `validation.md`
- `run_manifest.json`

---

## 왜 0단계와 4단계가 필요한가

아래 이유 때문에
반복 리서치에는 3단계만으로 부족할 수 있다.

### 1. 질문이 안 고정되면 과수집이 발생한다

시장조사는 자료가 부족해서 망하기보다
질문이 흐려져서 망하는 경우가 많다.

따라서
`무슨 결정을 위한 조사인가`
를 먼저 고정하는 0단계가 있으면
후속 자동화와 note 재사용성이 올라간다.

### 2. 금융 데이터는 시점과 개정 이력이 중요하다

공식 소스만 써도
시점 이슈는 남는다.

- SEC API는 실시간에 가깝게 갱신되지만
  처리 지연이 있을 수 있다.
- SEC는 filing time / acceptance time을 구분한다.
- FRED는 같은 series라도 vintage별 개정 이력이 존재한다.

즉
`무엇을 봤는가`뿐 아니라
`언제 기준으로 봤는가`
가 남아야 한다.

### 3. 자동화는 재현성과 운영제약을 함께 다뤄야 한다

Playwright를 쓰면 동적 페이지 수집은 쉬워지지만,
동시에 아래도 같이 관리해야 한다.

- 다운로드 파일 보존
- trace / screenshot 보존
- 사이트별 fair access
- unsupported browser / 동적 렌더링 실패 fallback

그래서 마지막 검증/운영 단계가 필요하다.

---

## 카테고리별 적용

### 1. 골드만삭스급 종목 스크리닝

해석:
- 다수 종목을 빠르게 걸러내는
  `universe -> factor/screen -> ranked shortlist`
  흐름으로 본다.

주요 공개 소스:
- [NYSE Listings Directory](https://www.nyse.com/listings_directory/stock)
- [SEC Search Filings](https://www.sec.gov/search-filings)
- 회사별 IR/Annual Report/10-K/10-Q

1단계:
- 유니버스 고정
  - 예: NYSE 상장주, 특정 섹터, 시가총액 하한
- 최소 수집 필드 고정
  - 시총
  - 매출 성장
  - 영업이익률
  - 부채비율
  - 밸류에이션 배수
- 제외 규칙 고정
  - 금융/바이오 제외 여부
  - 적자 기업 제외 여부
  - 유동성 하한

2단계:
- 기업별 스크리닝 테이블 생성
- 최근 filings와 IR 자료에서
  숫자와 구조적 리스크를 같이 태깅
- 단순 점수화보다
  `왜 통과/탈락했는지` 이유 컬럼을 남김

3단계:
- `longlist -> shortlist -> final watchlist`
  3단 구조로 메모 작성
- 상위 후보는
  valuation / catalyst / risk를 한 줄씩 붙임

### 2. 모건스탠리 DCF 가치평가

해석:
- 기업 1개 또는 peer set에 대해
  `현금흐름 가정 -> 할인율 -> 가치 범위`
  를 만드는 valuation workflow로 본다.

주요 공개 소스:
- [SEC Search Filings](https://www.sec.gov/search-filings)
- [SEC EDGAR APIs](https://www.sec.gov/submit-filings/filer-support-resources/how-do-i-guides/understand-edgar-application-programming-interfaces-apis)
- 회사 IR 발표자료 / guidance
- [FRED](https://fred.stlouisfed.org/)
- [BLS](https://www.bls.gov/)
- [BEA](https://www.bea.gov/)

1단계:
- 최신 10-K / 10-Q / investor presentation 수집
- 매출 driver, margin, capex, working capital driver를 고정
- 거시 입력값 후보 수집
  - 무위험금리
  - inflation
  - GDP/소비

2단계:
- historical FCF bridge 작성
  - EBIT
  - tax
  - D&A
  - capex
  - working capital
- base/bull/bear 가정 분리
- terminal growth와 WACC 가정의 근거를 기록

3단계:
- 내재가치 단일 숫자 대신
  `가치 밴드`로 정리
- 민감도 표를 포함
  - WACC
  - terminal growth
  - margin
- 최종 메모에는
  `무엇이 가치 훼손 포인트인지`
  를 함께 적음

### 3. JP모건 실적분석

해석:
- 실적 발표 직후
  `무엇이 좋아졌고 나빠졌는지`
  를 빠르게 읽는 earnings review workflow로 본다.

주요 공개 소스:
- [JPMorganChase Quarterly Earnings](https://www.jpmorganchase.com/latest-earnings)
- 회사별 earnings release / slide deck / webcast transcript
- [SEC Search Filings](https://www.sec.gov/search-filings)

1단계:
- 실적 발표 페이지에서
  release, slide deck, supplemental 자료 수집
- 같은 분기의 10-Q 또는 8-K도 확보
- 이전 분기 / 전년동기 자료도 함께 묶음

2단계:
- headline beat/miss보다 아래를 분리
  - segment 매출
  - 마진
  - guidance 변화
  - 재고/대손/주주환원
- 경영진 코멘트에서
  수요, 가격, 비용, capex, 지역별 톤을 태깅

3단계:
- 결과를
  `좋은 실적`이 아니라
  `quality of earnings`
  관점으로 정리
- 메모는 최소 아래 4줄로 끝낼 수 있어야 한다.
  - 이번 분기 핵심 변화
  - 지속 가능한가
  - 다음 분기 확인 포인트
  - valuation에 주는 영향

### 4. 블랙록 포트폴리오 구성

해석:
- 자산배분과 exposure 설계를 중심으로 한
  portfolio construction workflow로 본다.

주요 공개 소스:
- [iShares Core S&P 500 ETF (IVV)](https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf)
- iShares methodology / holdings / factsheet
- [SEC Form 13F FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f)
- price/volatility/correlation 시계열

1단계:
- 목적 먼저 고정
  - 성장
  - 방어
  - 인컴
  - 혼합
- 사용 가능한 building block 수집
  - ETF
  - 전략 sleeve
  - 현금/T-bills

2단계:
- holdings와 methodology를 읽어
  겉 이름이 아니라 실제 노출을 정리
  - sector
  - top holdings concentration
  - country
  - duration
  - factor tilt
- 자산 간 상관/변동성/드로다운 비교

3단계:
- 목적별 model portfolio 제안
  - core
  - satellite
  - hedge
- 비중 표와 함께
  `왜 이 조합인지`
  를 설명
- 리밸런싱 규칙과 최대 편차 허용범위를 같이 적음

### 5. 시타델 기술적 분석

해석:
- 순수 차트 읽기가 아니라
  `price + volume + volatility + regime`
  결합형 technical workflow로 본다.

주요 공개 소스:
- 내부 OHLCV DB 또는 공공 가격 시계열
- [Cboe VIX](https://www.cboe.com/tradable_products/vix/vix_futures/)
- [FRED](https://fred.stlouisfed.org/)

1단계:
- 종목/ETF/지수의 가격 시계열 수집
- 시장 상태 보조지표 수집
  - VIX
  - 금리
  - 신용스프레드
  - 달러 인덱스

2단계:
- 기술적 상태를 정형화
  - 추세
  - 모멘텀
  - 거래량 급증
  - 변동성 확대/축소
  - 지지/저항 근처 여부
- 종목 단독 차트보다
  benchmark relative strength도 같이 봄

3단계:
- 각 종목을
  `trend intact / breakout candidate / failure risk / avoid`
  로 분류
- entry보다
  invalidation 조건과 손상 신호를 먼저 적음

### 6. 하버드 기금 배당 전략

해석:
- `배당수익률 chasing`이 아니라
  endowment처럼
  현금흐름 지속성과 분산을 중시하는
  income strategy로 본다.

주요 공개 소스:
- [Harvard Management Company FY24 Annual Report](https://www.hmc.harvard.edu/wp-content/uploads/2024/10/FY24_HMC_Annual_Report.pdf)
- 회사별 dividend history / annual report / 10-K
- company payout commentary

1단계:
- 배당주 후보군 수집
- 단순 고배당보다 아래 필드 우선 수집
  - payout ratio
  - FCF coverage
  - leverage
  - dividend growth streak
  - sector concentration

2단계:
- 배당 지속 가능성 검토
  - 현금흐름이 배당을 커버하는가
  - 경기둔화 시 방어력이 있는가
  - 배당이 CAPEX를 잠식하지 않는가
- endowment-style 관점에서
  인출 안정성과 drawdown도 함께 봄

3단계:
- 결과를
  `고배당 리스트`
  로 끝내지 않고
  `분산된 인컴 바스켓`
  으로 제안
- 종목별 기대 역할을 적음
  - 방어 인컴
  - 배당 성장
  - 경기민감 고수익

### 7. 베인 경쟁사 분석

해석:
- 컨설팅식 competitor mapping을
  공개 filings와 IR 자료로 재현하는 workflow로 본다.

주요 공개 소스:
- 10-K의 business / competition / risk factor / segment note
- investor day deck
- earnings presentation
- 업계 협회/규제기관 공개 문서

1단계:
- focal company와 top competitors 선정
- 비교 축 고정
  - 제품
  - 가격
  - 유통
  - 지역
  - margin
  - 성장률

2단계:
- 각 기업의 공개 문서에서
  경쟁 포지션 문장을 추출
- segment reporting과 KPI를 맞춰 비교표 생성
- 표현만이 아니라
  실제 숫자 차이로 매핑

3단계:
- competitor matrix 작성
  - leader
  - challenger
  - niche
  - structurally weak
- 마지막에
  `누가 누구의 점유율을 뺏고 있는가`
  를 한 문장으로 요약

### 9. 르네상스 테크놀로지스 패턴 탐지

해석:
- 비밀 신호를 흉내 내는 것이 아니라
  공개 시계열과 이벤트 데이터에서
  반복 패턴을 찾는 systematic research로 본다.

주요 공개 소스:
- 내부 OHLCV / factor DB
- [SEC Search Filings](https://www.sec.gov/search-filings)
- earnings/event dates
- macro calendar

1단계:
- 패턴 후보를 먼저 명시
  - earnings drift
  - month-end effect
  - gap fade/continuation
  - sector rotation
  - volatility compression breakout
- 테스트 기간과 universe를 고정

2단계:
- 패턴을 룰로 바꿔 backtest 가능한 형태로 정형화
- 평균 수익률보다 아래를 같이 측정
  - hit ratio
  - turnover
  - tail loss
  - regime dependency
- outlier 한두 건에 속지 않도록
  기간 분할 검증

3단계:
- 결과를
  `있다/없다`
  가 아니라
  `재현성 / 비용 감안 후 유효성 / 붕괴 조건`
  으로 정리
- 실전 전환 후보는
  실패 구간 설명이 가능해야 한다

### 10. 맥킨지 매크로 영향평가

해석:
- 거시 변수 변화가
  섹터/기업의 실적과 valuation에
  어떻게 연결되는지 평가하는 workflow로 본다.

주요 공개 소스:
- [FRED](https://fred.stlouisfed.org/)
- [BLS](https://www.bls.gov/)
- [BEA](https://www.bea.gov/)
- [Federal Reserve Beige Book](https://www.federalreserve.gov/monetarypolicy/publications/beige-book-default.htm)
- company filings의 macro sensitivity 언급

1단계:
- macro 변수 고정
  - 금리
  - 인플레이션
  - 소비
  - 고용
  - 제조업/서비스 업황
  - 달러
- 업종별 민감도 가설 수립

2단계:
- macro series와 sector/company 지표를 정렬
- 정량과 정성을 분리
  - 정량: 시계열 변화
  - 정성: Beige Book, management commentary
- 단기/중기/장기 영향 채널을 구분

3단계:
- 결과를
  `macro view`
  가 아니라
  `sector impact map`
  으로 요약
- 예:
  - 금리 하락 수혜
  - 원가 압박 완화 수혜
  - 소비 둔화 취약
  - 달러 강세 역풍

---

## 권장 소스 우선순위

실제 운용에서는 아래 우선순위가 가장 안전하다.

1. 규제기관 / 거래소 / 발행사 공식 문서
   - SEC
   - NYSE
   - 회사 IR
2. 운용사/ETF official holdings/methodology
   - iShares
3. 거시 공공기관 데이터
   - FRED
   - BLS
   - BEA
   - Federal Reserve
4. 내부 DB 재가공
   - OHLCV
   - factors
   - backtest artifacts

주의:
- 유료 sell-side report 제목만 보고 내부 논리를 추정하면 품질이 떨어진다.
- 반드시 공개 원문과 숫자부터 확보해야 한다.

---

## 추가적으로 반드시 고려할 사항

### 1. Point-In-Time / 공시 수용 시각

SEC 기준으로
전자 제출의 filing time과 acceptance time은 구분된다.
또한 일부 제출은 늦은 시각에 접수되면
다음 영업일 index에 반영될 수 있다.

실무 규칙:
- `filing_date`
- `accepted_at`
- `accessed_at`
를 분리 저장한다.
- IR 발표자료를 먼저 봤더라도
  공식 filing이 늦게 올라오면 그 시차를 메모에 남긴다.

### 2. Entity Mapping / ticker-only 금지

SEC는 `company_tickers*.json`을 제공하지만
정확성이나 scope를 보장하지 않는다고 밝힌다.

실무 규칙:
- ticker는 화면 표시용
- 식별은 `CIK + accession_no` 우선
- share class / preferred / ETF / ADR는 별도 태그

### 3. Macro Revision / vintage 관리

FRED는 `series/vintagedates`를 제공하고,
macro 수치는 이후 개정될 수 있다.

실무 규칙:
- macro 영향평가에는
  `series_id`, `release_date`, `vintage_date`
  를 남긴다.
- backtest용 macro factor와
  narrative용 최신 macro 수치를 섞지 않는다.

### 4. 2차 데이터는 원문 대체재가 아니다

SEC의 Financial Statement Data Sets도
원 filing을 돕기 위한 분석용 자료이지
원문 대체재가 아니라고 명시한다.

실무 규칙:
- flat dataset은 탐색/스캔용
- 투자 판단 직전 숫자는 원 filing 재확인

### 5. Qual + Quant 분리

Federal Reserve Beige Book은
정량 데이터로 바로 보이지 않는 변화를 보완하는
질적 정보 요약이다.

실무 규칙:
- macro 영향평가는
  정량 데이터와 정성 코멘터리를 분리 기록
- 서로 충돌하면
  `왜 충돌하는지`를 적고 둘 중 하나를 지우지 않는다

### 6. API 우선, Browser는 증빙/동적 테이블 보조

BLS와 BEA는 공식 API와 다운로드 경로를 제공한다.
SEC 역시 `data.sec.gov` API와 bulk ZIP을 제공한다.

실무 규칙:
- 시계열 / filing 메타 / bulk data는 API 우선
- Playwright는
  - 동적 테이블
  - IR 자료 링크 발견
  - 다운로드 유도
  - 증빙 캡처
  용도로 제한

### 7. Fair Access / rate limit 준수

SEC는 fair access 정책에서
현재 최대 요청률과 user-agent 선언을 명시한다.

실무 규칙:
- 공식 소스별 throttle profile 사용
- user-agent 명시
- 필요한 것만 다운로드
- 대량 수집은 bulk archive 우선

### 8. Evidence Package / trace 보존

Playwright trace viewer는
각 단계의 page state, DOM snapshot, network/log를 볼 수 있다.
다운로드 파일도 명시적으로 저장하지 않으면
browser context 종료 시 사라질 수 있다.

실무 규칙:
- `trace.zip`
- screenshot
- 다운로드 원본 파일
- parse 결과
- summary note
를 한 run 폴더 안에 같이 남긴다.

### 9. Contradiction Log / 반대증거 보존

좋아 보이는 근거만 모으면
시장조사가 아니라 확증편향 정리가 된다.

실무 규칙:
- `supporting_evidence`
- `contradicting_evidence`
를 분리
- 최종 메모에는
  `이 판단이 틀릴 수 있는 이유`
  를 한 문단 이상 남긴다.

### 10. Refresh Policy / 조사 수명 관리

실적, macro, holdings는 수명이 다르다.

실무 규칙:
- earnings memo: 다음 실적 전까지 유효
- DCF memo: 가정 변화 시 즉시 재검토
- portfolio note: 월별 또는 리밸런싱 시점 재검토
- macro impact map: 주요 release 후 갱신

---

## 보강 근거가 된 공식 문서

- [SEC EDGAR API Documentation](https://www.sec.gov/edgar/sec-api-documentation)
  - `data.sec.gov` API, bulk ZIP, 업데이트 지연, calendar-frame 해석 주의
- [SEC Developer Resources](https://www.sec.gov/about/developer-resources)
  - scripted access, developer entrypoint, fair-access 관련 안내
- [SEC Webmaster FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions)
  - user-agent 선언, 현재 최대 요청률, sec.gov 반영 지연 안내
- [SEC Privacy and Security Policy](https://www.sec.gov/privacy.htm)
  - automated access와 request-rate 제한 정책
- [SEC Accessing EDGAR Data](https://www.sec.gov/os/accessing-edgar-data)
  - `company_tickers*.json` 정확성/scope 비보장, EDGAR file-system 접근 방식
- [SEC Financial Statement Data Sets Guide](https://www.sec.gov/file/financial-statement-data-sets)
  - 분석 보조용 flat data이며 원 filing 대체재가 아니라는 점
- [FRED Real-Time Periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html)
  - `realtime_start`, `realtime_end`, ALFRED 관점 설명
- [FRED Series Vintage Dates](https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html)
  - revision / release vintage 추적
- [BLS Developers API Getting Started](https://www.bls.gov/developers/)
  - BLS 공식 API 경로와 버전 차이
- [BEA Open Data](https://www.bea.gov/open-data)
  - BEA API와 다운로드 경로
- [Federal Reserve Beige Book](https://www.federalreserve.gov/monetarypolicy/publications/beige-book-default.htm)
  - 정성 경기 코멘터리의 성격과 발간 주기
- [Playwright Trace Viewer](https://playwright.dev/docs/trace-viewer-intro)
  - `trace.zip`, DOM snapshot, step-level inspection
- [Playwright Downloads](https://playwright.dev/docs/next/downloads)
  - 다운로드 파일의 저장과 context 종료 시 삭제 주의
- [Playwright Tracing API](https://playwright.dev/docs/api/class-tracing)
  - tracing start/stop와 trace artifact 저장 방식

---

## Playwright 작업 단위 예시

브라우저 자동화는 아래 단위로 설계하면 된다.

1. URL discovery
   - IR 페이지에서 `Earnings`, `Presentations`, `Annual Report` 링크 수집
2. table capture
   - holdings / listing / filings result table 추출
3. artifact download
   - PDF
   - XLSX
   - CSV
4. evidence logging
   - 페이지 제목
   - 접근 시각
   - 원본 URL
   - 다운로드 파일명
5. markdown synthesis
   - 위 1~4 결과를 바탕으로 summary note 생성
6. trace capture
   - `trace.zip`
   - screenshot
   - raw HTML/metadata

가능하면 run 단위로 아래를 같이 남긴다.

- `research_brief.md`
- `sources.md`
- `validation.md`
- `run_manifest.json`

---

## 권장 산출물 구조

한 번의 조사 결과는 최소 아래처럼 남기면 재사용성이 높다.

```text
.note/finance/research_runs/
  2026-03-31_screening_aapl_peers/
    research_brief.md
    sources.md
    raw/
    parsed/
    validation.md
    run_manifest.json
    summary.md
```

`summary.md`에는 최소 아래 5개 블록을 고정한다.

1. 질문
2. 사용한 공개 소스
3. 핵심 숫자 / 표
4. 해석
5. 다음 액션

`run_manifest.json`에는 아래 필드를 권장한다.

- `run_id`
- `topic`
- `as_of_date`
- `accessed_at`
- `source_urls`
- `downloaded_files`
- `entity_keys`
- `validation_status`
- `refresh_rule`

---

## 이 문서의 결론

정리하면,
`Playwright`를 이용한 시장/기업 정보 조사는 충분히 가능하다.

다만 가장 중요한 포인트는
**기관 이름을 그대로 따라 하는 것**이 아니라,
그 이름 뒤에 있는 공개 재현 가능한 조사 테마를 분리하는 것이다.

실전형 흐름은 아래로 요약된다.

1. 반복 조사라면 먼저 질문과 판단계약을 고정한다.
2. 공식 소스를 먼저 고정한다.
3. Playwright는 동적 페이지와 증빙 수집에 제한적으로 쓴다.
4. 숫자와 서술을 정형화한다.
5. 마지막에는 반드시
   - shortlist
   - valuation band
   - earnings memo
   - portfolio proposal
   - macro impact map
   중 하나의 판단 산출물로 끝낸다.
6. 끝나기 전에
   - 시점 정합성
   - source provenance
   - contradiction log
   - refresh cadence
   를 검증한다.

이 방식이면
향후 `finance` 패키지의
데이터 수집,
백테스트,
리서치 메모 작성
흐름과도 자연스럽게 연결할 수 있다.
