"""
    info 정보 (ex. SPY)
    ticker = yf.Ticker("SPY")
    ticker.info 의 정보
"""

info_format_by_etf = {
    "longBusinessSummary": "The trust seeks to achieve its investment objective by holding a portfolio of the common stocks that are included in the index (the “Portfolio”), with the weight of each stock in the Portfolio substantially corresponding to the weight of such stock in the index.", # 회사 개요(장기 사업 요약)
    "companyOfficers": [],                     # 임원 정보
    "executiveTeam": [],                       # 경영진 명단
    "maxAge": 86400,                           # 데이터 최대 연령(초)
    "priceHint": 2,                            # 가격 표시 자리수 힌트
    "previousClose": 689.53,                   # 전일 종가
    "open": 690.35,                            # 시가
    "dayLow": 681.76,                          # 당일 저가
    "dayHigh": 691.45,                         # 당일 고가
    "regularMarketPreviousClose": 689.53,      # 정규시장 전일 종가
    "regularMarketOpen": 690.35,               # 정규시장 시가
    "regularMarketDayLow": 681.76,             # 정규시장 저가
    "regularMarketDayHigh": 691.45,            # 정규시장 고가
    "trailingPE": 27.781937,                   # 주가수익비율(12개월 후행)
    "volume": 97603141,                        # 거래량
    "regularMarketVolume": 97603141,           # 정규시장 거래량
    "averageVolume": 81520026,                 # 평균 거래량
    "averageVolume10days": 83155850,           # 10일 평균 거래량
    "averageDailyVolume10Day": 83155850,       # 10일 일평균 거래량
    "bid": 686.05,                             # 매수 호가
    "ask": 686.13,                             # 매도 호가
    "bidSize": 320,                            # 매수 호가 수량
    "askSize": 360,                            # 매도 호가 수량
    "yield": 0.0107,                           # 분배율
    "totalAssets": 712072560640,               # 총 자산
    "fiftyTwoWeekLow": 481.8,                  # 52주 최저가
    "fiftyTwoWeekHigh": 697.84,                # 52주 최고가
    "allTimeHigh": 697.84,                     # 역대 최고가
    "allTimeLow": 42.8125,                     # 역대 최저가
    "fiftyDayAverage": 685.0494,               # 50일 평균가
    "twoHundredDayAverage": 642.7045,          # 200일 평균가
    "trailingAnnualDividendRate": 5.662,       # 최근 12개월 배당금
    "trailingAnnualDividendYield": 0.00821139, # 최근 12개월 배당수익률
    "navPrice": 689.56085,                     # 순자산가치(NAV)
    "currency": "USD",                         # 통화
    "tradeable": False,                        # 거래 가능 여부
    "category": "Large Blend",                 # 카테고리
    "ytdReturn": 17.7547,                      # 올해 수익률
    "beta3Year": 1.0,                          # 3년 베타값
    "fundFamily": "State Street Investment Management", # 운용사
    "fundInceptionDate": 727660800,            # 최초 설정일(Unix timestamp)
    "legalType": "Exchange Traded Fund",       # 법적 종류
    "threeYearAverageReturn": 0.2027,          # 3년 평균 수익률
    "fiveYearAverageReturn": 0.1411215,        # 5년 평균 수익률
    "quoteType": "ETF",                        # 종목 종류
    "symbol": "SPY",                           # 심벌
    "language": "en-US",                       # 언어
    "region": "US",                            # 지역
    "typeDisp": "ETF",                         # 타입 설명
    "quoteSourceName": "Nasdaq Real Time Price", # 시세 출처
    "triggerable": True,                       # 거래 트리거 가능
    "customPriceAlertConfidence": "HIGH",      # 가격 알림 신뢰도
    "regularMarketChangePercent": -0.484392,   # 정규시장 변동률(%)
    "regularMarketPrice": 686.19,              # 정규시장 현재가
    "hasPrePostMarketData": True,              # 장전/장후 데이터 지원 여부
    "firstTradeDateMilliseconds": 728317800000,# 최초 거래일(ms)
    "postMarketChangePercent": 0.20329931,     # 장후 변동률(%)
    "postMarketPrice": 687.585,                # 장후 가격
    "postMarketChange": 1.3950195,             # 장후 가격 변화
    "regularMarketChange": -3.34003,           # 정규시장 가격 변화
    "regularMarketDayRange": "681.76 - 691.45",# 정규시장 당일 범위
    "fullExchangeName": "NYSEArca",            # 전체 거래소 명칭
    "financialCurrency": "USD",                # 재무 통화
    "averageDailyVolume3Month": 81520026,      # 3개월 일평균 거래량
    "fiftyTwoWeekLowChange": 204.39001,        # 52주 최저가 대비 변동
    "fiftyTwoWeekLowChangePercent": 0.42422172,# 52주 최저가 대비 변동률
    "fiftyTwoWeekRange": "481.8 - 697.84",     # 52주 범위
    "fiftyTwoWeekHighChange": -11.650024,      # 52주 최고가 대비 변동
    "fiftyTwoWeekHighChangePercent": -0.016694406, # 52주 최고가 대비 변동률
    "fiftyTwoWeekChangePercent": 14.119029,    # 52주 수익률(%)
    "dividendYield": 1.07,                     # (연) 배당수익률(%)
    "trailingThreeMonthReturns": 2.6265,       # 3개월 후행 수익률
    "trailingThreeMonthNavReturns": 2.6265,    # 3개월 후행 NAV 수익률
    "netAssets": 712072560000.0,               # 순자산
    "epsTrailingTwelveMonths": 24.699142,      # 주당순이익(최근 12개월)
    "sharesOutstanding": 917782016,            # 유통주식수
    "bookValue": 429.22,                       # 장부가치(주당)
    "fiftyDayAverageChange": 1.140625,         # 50일 평균가 대비 변화
    "fiftyDayAverageChangePercent": 0.001665026,# 50일 평균가 대비 변화율
    "twoHundredDayAverageChange": 43.485474,   # 200일 평균가 대비 변화
    "twoHundredDayAverageChangePercent": 0.06766013, # 200일 평균가 대비 변화율
    "netExpenseRatio": 0.0945,                 # 총비용률(%)
    "marketCap": 629772845056,                 # 시가총액
    "priceToBook": 1.5986906,                  # 주가순자산비율(PBR)
    "sourceInterval": 15,                      # 데이터 갱신 간격(분)
    "exchangeDataDelayedBy": 0,                # 거래소 데이터 지연(분)
    "cryptoTradeable": False,                  # 암호화폐 거래 가능 여부
    "marketState": "POST",                     # 시장 상태
    "corporateActions": [],                    # 기업 액션(예: 분할, 병합 등)
    "postMarketTime": 1770244583,              # 장후 시간(Unix timestamp)
    "regularMarketTime": 1770238800,           # 정규시장 시간(Unix timestamp)
    "exchange": "PCX",                         # 거래소 코드
    "messageBoardId": "finmb_6160262",         # 토론방 ID
    "exchangeTimezoneName": "America/New_York",# 거래소 시간대
    "exchangeTimezoneShortName": "EST",        # 거래소 시간대(약)
    "gmtOffSetMilliseconds": -18000000,        # GMT 오프셋(ms)
    "market": "us_market",                     # 시장 구분
    "esgPopulated": False,                     # ESG 데이터 존재 여부
    "shortName": "State Street SPDR S&P 500 ETF T", # 짧은 이름
    "longName": "State Street SPDR S&P 500 ETF Trust", # 공식 이름
    "trailingPegRatio": None                   # 최근 PEG 비율
}


"""
    info 정보포멧 (ex. AAPL)
    ticker = yf.Ticker("AAPL")
    ticker.info 의 정보
"""
info_format_by_stock = {
    "address1": "One Apple Park Way",             # 본사 주소
    "city": "Cupertino",                          # 도시
    "state": "CA",                                # 주
    "zip": "95014",                               # 우편번호
    "country": "United States",                   # 국가
    "phone": "(408) 996-1010",                    # 전화번호
    "website": "https://www.apple.com",           # 홈페이지
    "industry": "Consumer Electronics",           # 업종
    "industryKey": "consumer-electronics",        # 업종 키
    "industryDisp": "Consumer Electronics",       # 업종(표시)
    "sector": "Technology",                       # 섹터
    "sectorKey": "technology",                    # 섹터 키
    "sectorDisp": "Technology",                   # 섹터(표시)
    "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; and wearables, home, and accessories comprising AirPods, Apple Vision Pro, Apple TV, Apple Watch, Beats products, and HomePod, as well as Apple branded and third-party accessories. It also provides AppleCare support and cloud services; and operates various platforms, including the App Store that allow customers to discover and download applications and digital content, such as books, music, video, games, and podcasts, as well as advertising services include third-party licensing arrangements and its own advertising platforms. In addition, the company offers various subscription-based services, such as Apple Arcade, a game subscription service; Apple Fitness+, a personalized fitness service; Apple Music, which offers users a curated listening experience with on-demand radio stations; Apple News+, a subscription news and magazine service; Apple TV, which offers exclusive original content and live sports; Apple Card, a co-branded credit card; and Apple Pay, a cashless payment service, as well as licenses its intellectual property. The company serves consumers, and small and mid-sized businesses; and the education, enterprise, and government markets. It distributes third-party applications for its products through the App Store. The company also sells its products through its retail and online stores, and direct sales force; and third-party cellular network carriers and resellers. The company was formerly known as Apple Computer, Inc. and changed its name to Apple Inc. in January 2007. Apple Inc. was founded in 1976 and is headquartered in Cupertino, California.",   # 회사 설명
    "fullTimeEmployees": 150000,                  # 전체 직원수
    "companyOfficers": [                          # 임원 목록
        {
            "maxAge": 1,                          # 최대 유효 기간
            "name": "Mr. Timothy D. Cook",        # 이름
            "age": 64,                            # 나이
            "title": "CEO & Director",            # 직책
            "yearBorn": 1961,                     # 출생연도
            "fiscalYear": 2025,                   # 재무연도
            "totalPay": 16759518,                 # 총보수
            "exercisedValue": 0,                  # 행사 가치
            "unexercisedValue": 0                 # 미행사 가치
        },
        {
            "maxAge": 1,
            "name": "Mr. Kevan  Parekh",
            "age": 53,
            "title": "Senior VP & CFO",
            "yearBorn": 1972,
            "fiscalYear": 2025,
            "totalPay": 4034174,
            "exercisedValue": 0,
            "unexercisedValue": 0
        },
        {
            "maxAge": 1,
            "name": "Mr. Sabih  Khan",
            "age": 58,
            "title": "Senior VP & Chief Operating Officer",
            "yearBorn": 1967,
            "fiscalYear": 2025,
            "totalPay": 5021905,
            "exercisedValue": 0,
            "unexercisedValue": 0
        },
        {
            "maxAge": 1,
            "name": "Ms. Katherine L. Adams",
            "age": 61,
            "title": "Senior VP, General Counsel & Secretary",
            "yearBorn": 1964,
            "fiscalYear": 2025,
            "totalPay": 5022482,
            "exercisedValue": 0,
            "unexercisedValue": 0
        },
        {
            "maxAge": 1,
            "name": "Ms. Deirdre  O'Brien",
            "age": 58,
            "title": "Senior Vice President of Retail & People",
            "yearBorn": 1967,
            "fiscalYear": 2025,
            "totalPay": 5037867,
            "exercisedValue": 0,
            "unexercisedValue": 0
        },
        {
            "maxAge": 1,
            "name": "Mr. Ben  Borders",
            "age": 44,
            "title": "Principal Accounting Officer",
            "yearBorn": 1981,
            "fiscalYear": 2025,
            "exercisedValue": 0,
            "unexercisedValue": 0
        },
        {
            "maxAge": 1,
            "name": "Suhasini  Chandramouli",
            "title": "Director of Investor Relations",
            "fiscalYear": 2025,
            "exercisedValue": 0,
            "unexercisedValue": 0
        },
        {
            "maxAge": 1,
            "name": "Ms. Kristin Huguet Quayle",
            "title": "Vice President of Worldwide Communications",
            "fiscalYear": 2025,
            "exercisedValue": 0,
            "unexercisedValue": 0
        },
        {
            "maxAge": 1,
            "name": "Mr. Greg  Joswiak",
            "title": "Senior Vice President of Worldwide Marketing",
            "fiscalYear": 2025,
            "exercisedValue": 0,
            "unexercisedValue": 0
        },
        {
            "maxAge": 1,
            "name": "Mr. Adrian  Perica",
            "age": 51,
            "title": "Vice President of Corporate Development",
            "yearBorn": 1974,
            "fiscalYear": 2025,
            "exercisedValue": 0,
            "unexercisedValue": 0
        }
    ],
    "auditRisk": 7,                               # 감사 위험
    "boardRisk": 1,                               # 이사회 위험
    "compensationRisk": 3,                        # 보상 위험
    "shareHolderRightsRisk": 1,                   # 주주권 위험
    "overallRisk": 1,                             # 전체 위험
    "governanceEpochDate": 1769904000,            # 지배구조 Epoch 날짜(Unix)
    "compensationAsOfEpochDate": 1767139200,      # 보상 기준 Epoch
    "irWebsite": "http://investor.apple.com/",    # IR 홈페이지
    "executiveTeam": [],                          # 경영진 리스트
    "maxAge": 86400,                              # 최대 유효 시간(초)
    "priceHint": 2,                               # 가격 힌트(소수점)
    "previousClose": 269.48,                      # 전일 종가
    "open": 272.31,                               # 시가
    "dayLow": 272.285,                            # 당일 저가
    "dayHigh": 278.95,                            # 당일 고가
    "regularMarketPreviousClose": 269.48,         # 정규시장 전일종가
    "regularMarketOpen": 272.31,                  # 정규시장 시가
    "regularMarketDayLow": 272.285,               # 정규시장 저가
    "regularMarketDayHigh": 278.95,               # 정규시장 고가
    "dividendRate": 1.04,                         # 연간 배당금
    "dividendYield": 0.39,                        # 배당수익률(%)
    "exDividendDate": 1770595200,                 # 배당락일(Unix)
    "payoutRatio": 0.1304,                        # 배당성향
    "fiveYearAvgDividendYield": 0.52,             # 5년 평균 배당수익률(%)
    "beta": 1.107,                                # 베타(변동성)
    "trailingPE": 34.998734,                      # 과거 P/E 비율(TTM)
    "forwardPE": 29.799831,                       # 예상 P/E 비율(포워드)
    "volume": 90320670,                           # 거래량
    "regularMarketVolume": 90320670,              # 정규시장 거래량
    "averageVolume": 47227998,                    # 평균 거래량(3개월)
    "averageVolume10days": 58089390,              # 최근 10일간 평균 거래량
    "averageDailyVolume10Day": 58089390,          # 최근 10일 일평균 거래량
    "bid": 275.95,                                # 매수호가
    "ask": 277.05,                                # 매도호가
    "bidSize": 2,                                 # 매수호가 수량
    "askSize": 3,                                 # 매도호가 수량
    "marketCap": 4063829426176,                   # 시가총액
    "fiftyTwoWeekLow": 169.21,                    # 52주 최저가
    "fiftyTwoWeekHigh": 288.62,                   # 52주 최고가
    "allTimeHigh": 288.62,                        # 역대 최고가
    "allTimeLow": 0.049107,                       # 역대 최저가
    "priceToSalesTrailing12Months": 9.328904,     # 주가매출비율(TTM)
    "fiftyDayAverage": 268.365,                   # 50일 평균가
    "twoHundredDayAverage": 237.36736,            # 200일 평균가
    "trailingAnnualDividendRate": 1.03,           # 과거 연간 배당금(TTM)
    "trailingAnnualDividendYield": 0.0038221758,  # 과거 연 배당률(TTM)
    "currency": "USD",                            # 통화
    "tradeable": False,                           # 거래 가능 여부
    "enterpriseValue": 3979875713024,             # EV(기업가치)
    "profitMargins": 0.27037,                     # 순이익률
    "floatShares": 14655594816,                   # 유동주식수
    "sharesOutstanding": 14681140000,             # 발행주식수
    "sharesShort": 113576032,                     # 공매도 잔고
    "sharesShortPriorMonth": 122035714,           # 전월 공매도 잔고
    "sharesShortPreviousMonthDate": 1765756800,   # 전월 공매도 잔고 기준일자(Unix)
    "dateShortInterest": 1768435200,              # 공매도 집계 기준일(Unix)
    "sharesPercentSharesOut": 0.0077,             # 공매도 잔고/발행주식수
    "heldPercentInsiders": 0.01702,               # 내부자 지분율
    "heldPercentInstitutions": 0.64992994,        # 기관 지분율
    "shortRatio": 2.61,                           # 공매도 비율
    "shortPercentOfFloat": 0.0077,                # 유동주식 대비 공매도 잔고 비율
    "impliedSharesOutstanding": 14697926000,      # 암묵적 발행주식수
    "bookValue": 5.998,                           # 장부가치(주당)
    "priceToBook": 46.09703,                      # 주가순자산비율(PBR)
    "lastFiscalYearEnd": 1758931200,              # 직전 회계연도말(Unix)
    "nextFiscalYearEnd": 1790467200,              # 다음 회계연도말(Unix)
    "mostRecentQuarter": 1766793600,              # 최근 분기(Unix)
    "earningsQuarterlyGrowth": 0.159,             # 분기별 이익 증가율
    "netIncomeToCommon": 117776998400,            # 귀속 순이익
    "trailingEps": 7.9,                           # 최근 12개월 EPS
    "forwardEps": 9.27824,                        # 예상 EPS
    "lastSplitFactor": "4:1",                     # 최근 액면분할 비율
    "lastSplitDate": 1598832000,                  # 최근 액면분할일(Unix)
    "enterpriseToRevenue": 9.136,                 # EV/매출
    "enterpriseToEbitda": 26.029,                 # EV/EBITDA
    "52WeekChange": 0.15920329,                   # 52주 변화율
    "SandP52WeekChange": 0.1412741,               # S&P500 52주 변화율
    "lastDividendValue": 0.26,                    # 직전 배당금액
    "lastDividendDate": 1762732800,               # 직전 배당일(Unix)
    "quoteType": "EQUITY",                        # 종목 타입
    "currentPrice": 276.49,                       # 현재가
    "targetHighPrice": 350.0,                     # 목표가(상단)
    "targetLowPrice": 205.0,                      # 목표가(하단)
    "targetMeanPrice": 292.45975,                 # 목표가(평균)
    "targetMedianPrice": 300.0,                   # 목표가(중간)
    "recommendationMean": 1.97826,                # 추천 점수(평균)
    "recommendationKey": "buy",                   # 추천(키)
    "numberOfAnalystOpinions": 41,                # 애널리스트 추천 의견 수
    "totalCash": 66907000832,                     # 전체 현금
    "totalCashPerShare": 4.557,                   # 주당 현금
    "ebitda": 152901992448,                       # EBITDA
    "totalDebt": 90509000704,                     # 총부채
    "quickRatio": 0.845,                          # 당좌비율
    "currentRatio": 0.974,                        # 유동비율
    "totalRevenue": 435617005568,                 # 총매출
    "debtToEquity": 102.63,                       # 부채비율(%)
    "revenuePerShare": 29.305,                    # 주당 매출액
    "returnOnAssets": 0.24377,                    # 총자산이익률
    "returnOnEquity": 1.5202099,                  # 자기자본이익률
    "grossProfits": 206157004800,                 # 총이익
    "freeCashflow": 106312753152,                 # 잉여현금흐름
    "operatingCashflow": 135471996928,            # 영업현금흐름
    "earningsGrowth": 0.183,                      # 이익 증가율
    "revenueGrowth": 0.157,                       # 매출 증가율
    "grossMargins": 0.47325,                      # 매출총이익률
    "ebitdaMargins": 0.35099998,                  # EBITDA 마진
    "operatingMargins": 0.35374,                  # 영업이익률
    "financialCurrency": "USD",                   # 재무 통화
    "symbol": "AAPL",                             # 티커(symbol)
    "language": "en-US",                          # 언어
    "region": "US",                               # 국가/지역
    "typeDisp": "Equity",                         # 타입(표시)
    "quoteSourceName": "Nasdaq Real Time Price",  # 가격 출처
    "triggerable": True,                          # 트리거 가능 여부
    "customPriceAlertConfidence": "HIGH",         # 커스텀 경고 신뢰도
    "corporateActions": [],                       # 기업 액션(예: 분할, 병합 등)
    "postMarketTime": 1770244997,                 # 장후 시간(Unix)
    "regularMarketTime": 1770238802,              # 정규시장 시간(Unix)
    "exchange": "NMS",                            # 거래소 코드
    "messageBoardId": "finmb_24937",              # 토론방 ID
    "exchangeTimezoneName": "America/New_York",   # 거래소 시간대
    "exchangeTimezoneShortName": "EST",           # 거래소 시간대(약칭)
    "gmtOffSetMilliseconds": -18000000,           # GMT 오프셋(ms)
    "market": "us_market",                        # 시장 구분
    "esgPopulated": False,                        # ESG 데이터 존재 여부
    "marketState": "POST",                        # 시장 상태
    "shortName": "Apple Inc.",                    # 간단 이름
    "longName": "Apple Inc.",                     # 공식 이름
    "dividendDate": 1762992000,                   # 배당일(Unix)
    "earningsTimestamp": 1769720400,              # 실적 발표 시점(Unix)
    "earningsTimestampStart": 1777582800,         # 실적 발표 시작(Unix)
    "earningsTimestampEnd": 1777582800,           # 실적 발표 종료(Unix)
    "earningsCallTimestampStart": 1769724000,     # 실적 콜 시작(Unix)
    "earningsCallTimestampEnd": 1769724000,       # 실적 콜 종료(Unix)
    "isEarningsDateEstimate": True,               # 실적발표 추정여부
    "epsTrailingTwelveMonths": 7.9,               # 최근 12개월 EPS
    "epsForward": 9.27824,                        # 예상 EPS
    "epsCurrentYear": 8.4729,                     # 올해 예상 EPS
    "priceEpsCurrentYear": 32.63227,              # 올해 PER
    "fiftyDayAverageChange": 8.125,               # 50일 평균가 대비 변화
    "fiftyDayAverageChangePercent": 0.030275932,  # 50일 평균가 대비 변화율
    "twoHundredDayAverageChange": 39.122635,      # 200일 평균가 대비 변화
    "twoHundredDayAverageChangePercent": 0.16481894, # 200일 평균가 대비 변화율
    "sourceInterval": 15,                         # 데이터 갱신 간격(분)
    "exchangeDataDelayedBy": 0,                   # 거래소 데이터 지연(분)
    "averageAnalystRating": "2.0 - Buy",          # 애널리스트 평가(평균)
    "cryptoTradeable": False,                     # 암호화폐 거래 가능 여부
    "hasPrePostMarketData": True,                 # 프리/포스트마켓 데이터 제공 여부
    "firstTradeDateMilliseconds": 345479400000,   # 최초 거래 일자(ms)
    "postMarketChangePercent": -0.53889483,       # 장후 가격 변화율(%)
    "postMarketPrice": 275.0,                     # 장후 가격
    "postMarketChange": -1.4899902,               # 장후 가격 변화
    "regularMarketChange": 7.0099792,             # 정규시장 가격 변화
    "regularMarketDayRange": "272.285 - 278.95",  # 정규시장 당일 범위
    "fullExchangeName": "NasdaqGS",               # 전체 거래소 명칭
    "averageDailyVolume3Month": 47227998,         # 3개월 일평균 거래량
    "fiftyTwoWeekLowChange": 107.27998,           # 52주 최저가 대비 변동
    "fiftyTwoWeekLowChangePercent": 0.63400495,   # 52주 최저가 대비 변동률
    "fiftyTwoWeekRange": "169.21 - 288.62",       # 52주 범위
    "fiftyTwoWeekHighChange": -12.130005,         # 52주 최고가 대비 변동
    "fiftyTwoWeekHighChangePercent": -0.042027596,# 52주 최고가 대비 변동률
    "fiftyTwoWeekChangePercent": 15.920329,       # 52주 수익률(%)
    "regularMarketChangePercent": 2.6012986,      # 정규시장 가격 변화율(%)
    "regularMarketPrice": 276.49,                 # 정규시장 가격
    "displayName": "Apple",                       # 표기 이름
    "trailingPegRatio": 2.5005                    # 최근 PEG 비율
}


"""
ETF에만 있는 키 (15개)
    beta3Year                   # 3년 베타값
    category                    # 카테고리 (펀드유형)
    fiveYearAverageReturn       # 5년 평균 수익률
    fundFamily                  # 펀드 회사
    fundInceptionDate           # 펀드 설정일
    legalType                   # 법적 유형
    navPrice                    # 기준가(NAV)
    netAssets                   # 순자산
    netExpenseRatio             # 총비용률(%)
    threeYearAverageReturn      # 3년 평균 수익률
    totalAssets                 # 총자산
    trailingThreeMonthNavReturns# 최근 3개월 NAV 수익률
    trailingThreeMonthReturns   # 최근 3개월 후행 수익률
    yield                       # 배당수익률(%)
    ytdReturn                   # 연초대비 수익률
"""

"""
Stock에만 있는 키 (96개)
    52WeekChange                    # 52주 수익률(%)
    SandP52WeekChange               # S&P 52주 수익률(%)
    address1                        # 본사 주소
    auditRisk                       # 감사 위험
    averageAnalystRating            # 애널리스트 평가(평균)
    beta                            # 주식 베타(변동성)
    boardRisk                       # 이사회 위험
    city                            # 도시
    compensationAsOfEpochDate       # 보상 기준일(epoch)
    compensationRisk                # 보상 위험
    country                         # 국가
    currentPrice                    # 현재 가격
    currentRatio                    # 유동비율
    dateShortInterest               # 공매도 이자 기준일
    debtToEquity                    # 부채/자기자본 비율
    displayName                     # 표기 이름
    dividendDate                    # 배당 기준일
    dividendRate                    # 배당률
    earningsCallTimestampEnd        # 실적 컨퍼런스콜 종료시각
    earningsCallTimestampStart      # 실적 컨퍼런스콜 시작시각
    earningsGrowth                  # 순이익 성장률
    earningsQuarterlyGrowth         # 분기별 순이익 성장률
    earningsTimestamp               # 실적 발표 타임스탬프
    earningsTimestampEnd            # 실적 발표 종료 타임스탬프
    earningsTimestampStart          # 실적 발표 시작 타임스탬프
    ebitda                          # EBITDA(상각전영업이익)
    ebitdaMargins                   # EBITDA 마진(%)
    enterpriseToEbitda              # EV/EBITDA 비율
    enterpriseToRevenue             # EV/매출 비율
    enterpriseValue                 # EV(기업가치)
    exDividendDate                  # 배당락일
    fiveYearAvgDividendYield        # 5년 평균 배당수익률(%)
    floatShares                     # 유통주식수
    forwardEps                      # 예측 EPS
    forwardPE                       # 예측 PER
    freeCashflow                    # 프리캐시플로우
    fullTimeEmployees               # 전체 직원수
    governanceEpochDate             # 지배구조 기준일(epoch)
    grossMargins                    # 총마진율(%)
    grossProfits                    # 총이익
    hasPrePostMarketData            # 프리/포스트마켓 데이터 제공 여부
    heldPercentInsiders             # 내부자 지분율
    heldPercentInstitutions         # 기관투자자 지분율
    impliedSharesOutstanding        # 암시적 유통주식수
    industry                        # 업종
    industryDisp                    # 업종(표시)
    industryKey                     # 업종 키
    irWebsite                       # IR 웹사이트
    isEarningsDateEstimate          # 실적발표일 추정 여부
    lastDividendDate                # 최종 배당일
    lastDividendValue               # 최종 배당금액
    lastFiscalYearEnd               # 최근 결산년도 종료일
    lastSplitDate                   # 마지막 액면분할일
    lastSplitFactor                 # 마지막 액면분할 비율
    marketCap                       # 시가총액
    mostRecentQuarter               # 최근 분기
    netIncomeToCommon               # 당기순이익
    nextFiscalYearEnd               # 다음 결산년도 종료일
    numberOfAnalystOpinions         # 애널리스트 의견 수
    operatingCashflow               # 영업활동현금흐름
    operatingMargins                # 영업이익률
    overallRisk                     # 전반적 위험
    payoutRatio                     # 배당성향
    phone                           # 전화번호
    priceEpsCurrentYear             # 올해 PER
    priceToSalesTrailing12Months    # 주가매출비율(최근12개월)
    profitMargins                   # 순이익률
    quickRatio                      # 당좌비율
    recommendationKey               # 추천 등급 키
    recommendationMean              # 추천 등급 평균
    returnOnAssets                  # 총자산수익률(ROA)
    returnOnEquity                  # 자기자본이익률(ROE)
    revenueGrowth                   # 매출성장률
    revenuePerShare                 # 주당매출액
    sector                          # 섹터
    sectorDisp                      # 섹터(표시)
    sectorKey                       # 섹터 키
    shareHolderRightsRisk           # 주주권 위험
    sharesOutstanding               # 유통주식수
    sharesPercentSharesOut          # 공매도 비율(%)
    sharesShort                     # 공매도 잔고
    sharesShortPriorMonth           # 전월 공매도 잔고
    sharesShortPreviousMonthDate    # 전월 공매도 잔고 날짜
    shortName                       # 짧은 이름
    shortPercentOfFloat             # 유동주식 공매도 비율
    shortRatio                      # 공매도 비율
    state                           # 주(지역)
    targetHighPrice                 # 목표주가(최고)
    targetLowPrice                  # 목표주가(최저)
    targetMeanPrice                 # 목표주가(평균)
    targetMedianPrice               # 목표주가(중간값)
    totalCash                       # 총현금
    totalCashPerShare               # 주당 총현금
    totalDebt                       # 총부채
    totalRevenue                    # 총매출
    tradeable                       # 거래가능 여부
    trailingEps                     # 최근 EPS
    trailingPegRatio                # 최근 PEG 비율
    website                         # 홈페이지
    zip                             # 우편번호
"""

"""
공통키 (86개) / Common Keys (86)
    allTimeHigh                       # 사상 최고가 / All-time high
    allTimeLow                        # 사상 최저가 / All-time low
    ask                               # 매도호가 / Ask price
    askSize                           # 매도호가 수량 / Ask size
    averageDailyVolume10Day           # 10일 일평균 거래량 / 10-day average daily volume
    averageDailyVolume3Month          # 3개월 일평균 거래량 / 3-month average daily volume
    averageVolume                     # 평균 거래량 / Average volume
    averageVolume10days               # 10일 평균 거래량 / 10-day average volume
    bid                               # 매수호가 / Bid price
    bidSize                           # 매수호가 수량 / Bid size
    bookValue                         # 주당 장부가치 / Book value per share
    companyOfficers                   # 임원 정보 / Company officers
    corporateActions                  # 기업행동(분할 등) / Corporate actions (e.g., splits)
    cryptoTradeable                   # 암호화폐 거래 가능 여부 / Crypto tradeable
    currency                          # 통화 / Currency
    customPriceAlertConfidence        # 맞춤 가격 알림 신뢰도 / Custom price alert confidence
    dayHigh                           # 일중 최고가 / Day high
    dayLow                            # 일중 최저가 / Day low
    dividendYield                     # 배당수익률 / Dividend yield
    epsTrailingTwelveMonths           # 최근 12개월 주당순이익 / EPS trailing twelve months
    esgPopulated                      # ESG 데이터 존재 여부 / ESG populated
    exchange                          # 거래소 코드 / Exchange code
    exchangeDataDelayedBy             # 거래소 데이터 지연(분) / Exchange data delayed by (min)
    exchangeTimezoneName              # 거래소 시간대 이름 / Exchange timezone name
    exchangeTimezoneShortName         # 거래소 시간대 약칭 / Exchange timezone short name
    executiveTeam                     # 임원진 정보 / Executive team
    fiftyDayAverage                   # 50일 평균가 / 50-day average price
    fiftyDayAverageChange             # 50일 평균가 대비 변화 / 50-day average change
    fiftyDayAverageChangePercent      # 50일 평균가 대비 변화율 / 50-day average change percent
    fiftyTwoWeekChangePercent         # 52주 최고/최저 변동률 / 52-week change percent
    fiftyTwoWeekHigh                  # 52주 최고가 / 52-week high
    fiftyTwoWeekHighChange            # 52주 최고가 대비 변화 / 52-week high change
    fiftyTwoWeekHighChangePercent     # 52주 최고가 대비 변화율 / 52-week high change percent
    fiftyTwoWeekLow                   # 52주 최저가 / 52-week low
    fiftyTwoWeekLowChange             # 52주 최저가 대비 변화 / 52-week low change
    fiftyTwoWeekLowChangePercent      # 52주 최저가 대비 변화율 / 52-week low change percent
    fiftyTwoWeekRange                 # 52주 가격범위 / 52-week range
    financialCurrency                 # 재무 기준 통화 / Financial currency
    firstTradeDateMilliseconds        # 첫 거래 일시(ms) / First trade date (ms)
    fullExchangeName                  # 전체 거래소 이름 / Full exchange name
    gmtOffSetMilliseconds             # GMT 오프셋(ms) / GMT offset (ms)
    hasPrePostMarketData              # 장전/장후 데이터 포함 여부 / Has pre/post-market data
    language                          # 언어 / Language
    longBusinessSummary               # 기업 설명 / Long business summary
    longName                          # 공식 이름 / Long name
    market                            # 시장 구분 / Market
    marketCap                         # 시가총액 / Market cap
    marketState                       # 시장 상태 / Market state
    maxAge                            # 데이터 최대 유효 기간 / Max data age
    messageBoardId                    # 토론방 ID / Message board ID
    open                              # 시가 / Open price
    postMarketChange                  # 장후 변동 / Post-market change
    postMarketChangePercent           # 장후 변동률 / Post-market change percent
    postMarketPrice                   # 장후 가격 / Post-market price
    postMarketTime                    # 장후 시간 / Post-market time
    previousClose                     # 전일 종가 / Previous close
    priceHint                         # 가격 단위 힌트 / Price hint
    priceToBook                       # 주가순자산비율(PBR) / Price to book
    quoteSourceName                   # 시세 제공원 / Quote source name
    quoteType                         # 시세 타입 / Quote type
    regularMarketChange               # 정규장 변동 / Regular market change
    regularMarketChangePercent        # 정규장 변동률 / Regular market change percent
    regularMarketDayHigh              # 정규장 고가 / Regular market day high
    regularMarketDayLow               # 정규장 저가 / Regular market day low
    regularMarketDayRange             # 정규장 가격 범위 / Regular market day range
    regularMarketOpen                 # 정규장 시가 / Regular market open
    regularMarketPreviousClose        # 정규장 전일 종가 / Regular market previous close
    regularMarketPrice                # 정규장 현재가 / Regular market price
    regularMarketTime                 # 정규장 기준 시각 / Regular market time
    regularMarketVolume               # 정규장 거래량 / Regular market volume
    region                            # 지역 / Region
    sharesOutstanding                 # 유통주식수 / Shares outstanding
    shortName                         # 짧은 이름 / Short name
    sourceInterval                    # 데이터 갱신 간격(분) / Source interval (min)
    symbol                            # 종목코드 / Symbol
    tradeable                         # 거래가능 여부 / Tradeable
    trailingAnnualDividendRate        # 연간 배당금 / Trailing annual dividend rate
    trailingAnnualDividendYield       # 연간 배당수익률 / Trailing annual dividend yield
    trailingPE                        # 후행 PER / Trailing PE
    trailingPegRatio                  # 최근 PEG 비율 / Trailing PEG ratio
    triggerable                       # 트리거 가능 여부 / Triggerable
    twoHundredDayAverage              # 200일 평균가 / 200-day average
    twoHundredDayAverageChange        # 200일 평균가 대비 변화 / 200-day average change
    twoHundredDayAverageChangePercent # 200일 평균가 대비 변화율 / 200-day average change percent
    typeDisp                          # 타입 표시 / Type display
    volume                            # 거래량 / Volume
"""



# [손익계산서 항목] Income Statement Fields
income_statement_fields = [
    ("Tax Effect Of Unusual Items", "특이 항목의 세금 효과"),  # 예외 항목에 대한 세금 효과
    ("Tax Rate For Calcs", "계산에 사용된 세율"),  # 세율
    ("Normalized EBITDA", "정상화된 EBITDA"),  # 표준화 EBITDA
    ("Net Income From Continuing Operation Net Minority Interest", "지배주주 귀속 지속 영업순이익"),  # 지속사업 순이익(비지배지분 차감 후)
    ("Reconciled Depreciation", "조정된 감가상각비"),  # 조정 감가상각
    ("Reconciled Cost Of Revenue", "조정된 매출원가"),  # 조정 매출원가
    ("EBITDA", "상각전 영업이익 (EBITDA)"),  # 상각전 영업이익
    ("EBIT", "영업이익 (EBIT)"),  # 영업이익
    ("Net Interest Income", "순이자수익"),  # 순이자 수익
    ("Interest Expense", "이자비용"),  # 이자 비용
    ("Interest Income", "이자수익"),  # 이자 수익
    ("Normalized Income", "정상화된 순이익"),  # 표준화 순이익
    ("Net Income From Continuing And Discontinued Operation", "지속 및 중단사업 순이익"),  # 전체 순이익
    ("Total Expenses", "총 비용"),  # 총비용
    ("Total Operating Income As Reported", "보고된 영업수익"),  # 보고 영업이익
    ("Diluted Average Shares", "희석주식수(평균)"),  # 희석주식수
    ("Basic Average Shares", "기본주식수(평균)"),  # 기본주식수
    ("Diluted EPS", "희석주당순이익"),  # 희석 EPS
    ("Basic EPS", "기본주당순이익"),  # 기본 EPS
    ("Diluted NI Availto Com Stockholders", "희석주식기준 순이익(보통주주귀속)"),  # 희석 주식 기준 순이익
    ("Net Income Common Stockholders", "보통주주귀속 순이익"),  # 보통주주 순이익
    ("Net Income", "당기순이익"),  # 순이익
    ("Net Income Including Noncontrolling Interests", "비지배지분 포함 순이익"),  # 비지배지분 포함 순이익
    ("Net Income Continuous Operations", "지속사업순이익"),  # 지속사업 순이익
    ("Tax Provision", "법인세 계상액"),  # 세금 계상
    ("Pretax Income", "세전 순이익"),  # 세전이익
    ("Other Income Expense", "기타 수익/비용"),  # 기타수익/비용
    ("Other Non Operating Income Expenses", "기타영업외수익/비용"),  # 기타 영업외 수익/비용
    ("Net Non Operating Interest Income Expense", "순영업외이자수익/비용"),  # 영업외 순이자
    ("Interest Expense Non Operating", "영업외 이자비용"),  # 영업외 이자비용
    ("Interest Income Non Operating", "영업외 이자수익"),  # 영업외 이자수익
    ("Operating Income", "영업이익"),  # 영업이익
    ("Operating Expense", "영업비용"),  # 영업비용
    ("Research And Development", "연구개발비"),  # 연구개발비
    ("Selling General And Administration", "판매관리비"),  # 판매/일반관리비
    ("Gross Profit", "매출총이익"),  # 매출총이익
    ("Cost Of Revenue", "매출원가"),  # 매출원가
    ("Total Revenue", "총매출액"),  # 총매출
    ("Operating Revenue", "영업수익")  # 영업수익
]

# [대차대조표 항목] Balance Sheet Fields
balance_sheet_fields = [
    ("Treasury Shares Number", "자기주식 수"),  # 자기주식수
    ("Ordinary Shares Number", "보통주 수"),  # 보통주식수
    ("Share Issued", "발행주식 수"),  # 발행주식수
    ("Net Debt", "순부채"),  # 순부채
    ("Total Debt", "총부채"),  # 총부채
    ("Tangible Book Value", "유형장부가치"),  # 유형장부가치
    ("Invested Capital", "투하자본"),  # 투자자본
    ("Working Capital", "운전자본"),  # 운전자본
    ("Net Tangible Assets", "순유형자산"),  # 순유형자산
    ("Capital Lease Obligations", "자본리스채무"),  # 자본리스채무
    ("Common Stock Equity", "보통주지분"),  # 보통주자본
    ("Total Capitalization", "총자본"),  # 총자본(자본금+부채)
    ("Total Equity Gross Minority Interest", "총지분(비지배지분포함)"),  # 총지분
    ("Stockholders Equity", "주주지분"),  # 주주지분
    ("Gains Losses Not Affecting Retained Earnings", "이익잉여금 미반영 손익"),  # 이익잉여금에 반영되지 않은 손익
    ("Other Equity Adjustments", "기타 자본조정"),  # 기타 자본조정
    ("Retained Earnings", "이익잉여금"),  # 이익잉여금
    ("Capital Stock", "자본금"),  # 자본금
    ("Common Stock", "보통주"),  # 보통주
    ("Total Liabilities Net Minority Interest", "총부채(비지배지분 제외)"),  # 총부채(비지배지분 제외)
    ("Total Non Current Liabilities Net Minority Interest", "총비유동부채(비지배지분 제외)"),  # 총비유동부채
    ("Other Non Current Liabilities", "기타 비유동부채"),  # 기타 장기부채
    ("Tradeand Other Payables Non Current", "장기 매입 및 기타 채무"),  # 장기 매입채무 등
    ("Long Term Debt And Capital Lease Obligation", "장기부채 및 자본리스채무"),  # 장기부채+리스
    ("Long Term Capital Lease Obligation", "장기 자본리스채무"),  # 장기리스채무
    ("Long Term Debt", "장기부채"),  # 장기채무
    ("Current Liabilities", "유동부채"),  # 유동부채
    ("Other Current Liabilities", "기타유동부채"),  # 기타유동부채
    ("Current Deferred Liabilities", "유동이연부채"),  # 유동이연부채
    ("Current Deferred Revenue", "유동이연수익"),  # 유동이연수익
    ("Current Debt And Capital Lease Obligation", "유동부채 및 자본리스채무"),  # 유동부채+리스
    ("Current Capital Lease Obligation", "유동 자본리스채무"),  # 유동리스채무
    ("Current Debt", "유동부채"),  # 유동부채
    ("Other Current Borrowings", "기타 단기차입금"),  # 기타단기차입금
    ("Commercial Paper", "상업어음"),  # 상업어음
    ("Payables And Accrued Expenses", "미지급금 및 미지급비용"),  # 미지급금/비용
    ("Current Accrued Expenses", "유동 미지급비용"),  # 유동미지급비용
    ("Payables", "지불채무"),  # 지불채무
    ("Total Tax Payable", "총납부세액"),  # 총납부세액
    ("Income Tax Payable", "법인세 납부금"),  # 법인세 납부금
    ("Accounts Payable", "매입채무"),  # 외상매입금
    ("Total Assets", "총자산"),  # 총자산
    ("Total Non Current Assets", "총비유동자산"),  # 총비유동자산
    ("Other Non Current Assets", "기타비유동자산"),  # 기타비유동자산
    ("Non Current Deferred Assets", "비유동이연자산"),  # 비유동이연자산
    ("Non Current Deferred Taxes Assets", "비유동이연법인세자산"),  # 비유동이연법인세자산
    ("Investments And Advances", "투자 및 선급금"),  # 투자 및 선급금
    ("Other Investments", "기타 투자"),  # 기타투자
    ("Investmentin Financial Assets", "금융자산 투자"),  # 금융자산 투자
    ("Available For Sale Securities", "매도가능증권"),  # 매도가능증권
    ("Net PPE", "유형자산 순액"),  # 유형자산 순액
    ("Accumulated Depreciation", "누적감가상각"),  # 누적감가상각
    ("Gross PPE", "총유형자산"),  # 총유형자산(감가상각 전)
    ("Leases", "리스"),  # 리스
    ("Other Properties", "기타 부동산"),  # 기타부동산
    ("Machinery Furniture Equipment", "기계, 가구, 장비"),  # 기계·가구·장비
    ("Land And Improvements", "토지 및 부속시설"),  # 토지 및 개량시설
    ("Properties", "부동산"),  # 부동산
    ("Current Assets", "유동자산"),  # 유동자산
    ("Other Current Assets", "기타유동자산"),  # 기타유동자산
    ("Inventory", "재고자산"),  # 재고
    ("Receivables", "받을어음,외상매출금"),  # 받을어음 등
    ("Other Receivables", "기타 수취채권"),  # 기타 받으실 금액
    ("Accounts Receivable", "매출채권"),  # 외상매출금
    ("Cash Cash Equivalents And Short Term Investments", "현금 및 현금성자산 및 단기투자자산"),  # 현금 등
    ("Other Short Term Investments", "기타 단기 투자자산"),  # 기타 단기투자
    ("Cash And Cash Equivalents", "현금 및 현금성자산"),  # 현금 및 현금성자산
    ("Cash Equivalents", "현금성자산"),  # 현금성자산
    ("Cash Financial", "금융성 현금"),  # 금융성 현금
]

# [현금흐름표 항목] Cashflow Statement Fields
cashflow_fields = [
    ("Free Cash Flow", "자유현금흐름"),  # 자유현금흐름(FCF)
    ("Repurchase Of Capital Stock", "자기주식 매입"),  # 자사주 매입
    ("Repayment Of Debt", "부채 상환"),  # 부채 상환
    ("Issuance Of Debt", "부채 발행"),  # 부채 발행
    ("Issuance Of Capital Stock", "자본금 발행"),  # 자본금 발행
    ("Capital Expenditure", "자본적지출"),  # 자본적지출(CAPEX)
    ("Interest Paid Supplemental Data", "지급이자(지원자료)"),  # 지급이자(추가자료)
    ("Income Tax Paid Supplemental Data", "납부법인세(지원자료)"),  # 납부법인세(추가자료)
    ("End Cash Position", "기말현금"),  # 기말현금
    ("Beginning Cash Position", "기초현금"),  # 기초현금
    ("Changes In Cash", "현금의 변동"),  # 현금변동
    ("Financing Cash Flow", "재무활동으로 인한 현금흐름"),  # 재무활동CF
    ("Cash Flow From Continuing Financing Activities", "지속적 재무활동 현금흐름"),  # 지속적 재무활동
    ("Net Other Financing Charges", "순기타재무비용"),  # 기타 재무비용 순액
    ("Cash Dividends Paid", "현금배당 지급"),  # 현금배당
    ("Common Stock Dividend Paid", "보통주 현금배당 지급"),  # 보통주 배당지급
    ("Net Common Stock Issuance", "보통주 순발행"),  # 보통주 순발행
    ("Common Stock Payments", "보통주 지급금"),  # 보통주 지급액
    ("Common Stock Issuance", "보통주 발행"),  # 보통주 발행
    ("Net Issuance Payments Of Debt", "부채 순발행/상환"),  # 부채 순발행·상환
    ("Net Short Term Debt Issuance", "단기부채 순발행"),  # 단기부채 순발행
    ("Net Long Term Debt Issuance", "장기부채 순발행"),  # 장기부채 순발행
    ("Long Term Debt Payments", "장기부채 상환"),  # 장기부채 상환
    ("Long Term Debt Issuance", "장기부채 발행"),  # 장기부채 발행
    ("Investing Cash Flow", "투자활동 현금흐름"),  # 투자CF
    ("Cash Flow From Continuing Investing Activities", "지속적 투자활동 현금흐름"),  # 지속적 투자현금흐름
    ("Net Other Investing Changes", "순기타투자변동"),  # 기타 투자변동 순액
    ("Net Investment Purchase And Sale", "순투자매입/매각"),  # 순투자매입매각
    ("Sale Of Investment", "투자매각"),  # 투자매각
    ("Purchase Of Investment", "투자매입"),  # 투자매입
    ("Net Business Purchase And Sale", "사업 순매입/매각"),  # 사업 순매입·매각
    ("Purchase Of Business", "사업매입"),  # 사업 매입
    ("Net PPE Purchase And Sale", "순유형자산매입/매각"),  # 유형자산 순매입·매각
    ("Purchase Of PPE", "유형자산매입"),  # 유형자산 매입
    ("Operating Cash Flow", "영업활동 현금흐름"),  # 영업CF
    ("Cash Flow From Continuing Operating Activities", "지속적 영업활동 현금흐름"),  # 지속적 영업현금흐름
    ("Change In Working Capital", "운전자본의 변동"),  # 운전자본 변동
    ("Change In Other Working Capital", "기타 운전자본 변동"),  # 기타 운전자본 변동
    ("Change In Other Current Liabilities", "기타 유동부채 변동"),  # 기타유동부채 변동
    ("Change In Other Current Assets", "기타 유동자산 변동"),  # 기타유동자산 변동
    ("Change In Payables And Accrued Expense", "지불채무 및 미지급비용 변동"),  # 지불채무·미지급비용 변동
    ("Change In Payable", "지불채무 변동"),  # 지불채무 변동
    ("Change In Account Payable", "매입채무 변동"),  # 매입채무 변동
    ("Change In Inventory", "재고자산 변동"),  # 재고 변동
    ("Change In Receivables", "매출채권 변동"),  # 매출채권 변동
    ("Changes In Account Receivables", "매출채권 변동(복수)"),  # 매출채권 변동(복수)
    ("Other Non Cash Items", "기타 비현금항목"),  # 기타 비현금 항목
    ("Stock Based Compensation", "주식기준보상비용"),  # 주식기준보상비용
    ("Deferred Tax", "이연법인세"),  # 이연법인세
    ("Deferred Income Tax", "이연소득세"),  # 이연소득세
    ("Depreciation Amortization Depletion", "감가상각/무형자산상각/고갈"),  # 감가상각/상각/고갈
    ("Depreciation And Amortization", "감가상각 및 무형자산상각비"),  # 감가상각 및 상각비
    ("Net Income From Continuing Operations", "지속사업 순이익")  # 지속사업 순이익
]
