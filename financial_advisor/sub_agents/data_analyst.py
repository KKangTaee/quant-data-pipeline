import yfinance as yf
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm("openai/gpt-5")

def get_company_info(ticker: str) -> str:
    """
    주어진 주식 티커에 대한 기본적인 회사 정보를 제공합니다.

    이 도구는 Yahoo Finance로부터 공식 회사명, 산업, 섹터 등 주요 기업 정보를 조회합니다.

    매개변수:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 애플)

    반환값:
        dict: 다음 정보를 담은 딕셔너리 반환
            - ticker (str): 입력한 티커 심볼
            - success (bool): 성공 여부
            - company_name (str): 회사의 공식명(Full legal name)
            - industry (str): 산업 분류
            - sector (str): 섹터(더 넓은 산업군)

    예시:
        >>> get_company_info('MSFT')
        {
            'ticker': 'MSFT',
            'success': True,
            'company_name': 'Microsoft Corporation',
            'industry': 'Software - Infrastructure',
            'sector': 'Technology'
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "success": True,
        "company_name": info.get("longName", "NA"),
        "industry": info.get("industry", "NA"),
        "sector": info.get("sector", "NA"),
    }

def get_stock_price(ticker:str, period:str) -> str:
    """
    지정한 주식 티커에 대한 과거 주가 데이터와 현재 거래 가격을 조회합니다.

    이 도구는 입력한 기간 동안의 과거 가격 데이터(시가, 고가, 저가, 종가, 거래량)와 현재 시장 가격을 모두 제공합니다.

    매개변수:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 애플)
        period (str): 과거 데이터 조회 기간. 사용 가능한 옵션:
            - '1d': 1일
            - '5d': 5일
            - '1mo': 1개월 (기본값)
            - '3mo': 3개월
            - '6mo': 6개월
            - '1y': 1년
            - '2y': 2년
            - '5y': 5년
            - '10y': 10년
            - 'ytd': 연초 이후
            - 'max': 제공되는 최대 기간

    반환값:
        dict: 다음 정보를 담은 딕셔너리
            - ticker (str): 입력한 티커 심볼
            - success (bool): 작업 성공 여부
            - history (str): OHLCV(시가, 고가, 저가, 종가, 거래량)가 포함된 JSON 포맷의 과거 가격 데이터
            - current_price (float): 해당 시점의 현재 주가

    예시:
        >>> get_stock_price('TSLA', '3mo')
        {
            'ticker': 'TSLA',
            'success': True,
            'history': '{"Open": {...}, "High": {...}, ...}',
            'current_price': 245.67
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period=period)
    return {
        "ticker": ticker,
        "success": True,
        "history": history.to_json(),
        "current_price": info.get("currentPrice"),
    }


def get_financial_metrics(ticker: str) -> str:
    """
    주식 분석을 위한 주요 재무 지표 및 밸류에이션 비율을 조회합니다.

    이 도구는 기업 가치평가, 수익성, 배당정책, 시장 리스크 특성을 파악할 수 있는 핵심 재무 지표를 제공합니다.

    매개변수:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 애플)

    반환값:
        dict: 다음 정보를 담은 딕셔너리
            - ticker (str): 입력한 티커 심볼
            - success (bool): 작업 성공 여부
            - market_cap (float): 시가총액 (미 달러 기준)
            - pe_ratio (float): 주가수익비율 (P/E, 주가/주당순이익)
            - dividend_yield (float): 연간 배당 수익률 (0.02 = 2%)
            - beta (float): 베타계수 (시장 대비 변동성)

    참고:
        - 시가총액(Market Cap): 회사의 총 가치 (발행주식수 * 주가)
        - P/E 비율: 낮을수록 저평가, 높을수록 성장 기대 반영
        - 배당수익률: 연간 배당을 주가로 나눈 비율
        - 베타: 1 미만이면 시장보다 변동성 낮음, 1 초과면 변동성 큼

    예시:
        >>> get_financial_metrics('JNJ')
        {
            'ticker': 'JNJ',
            'success': True,
            'market_cap': 385000000000,
            'pe_ratio': 15.2,
            'dividend_yield': 0.031,
            'beta': 0.65
        }
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "success": True,
        "market_cap": info.get("marketCap", "NA"),
        "pe_ratio": info.get("trailingPE", "NA"),
        "dividend_yield": info.get("dividendYield", "NA"),
        "beta": info.get("beta", "NA"),
    }   

data_analyst = LlmAgent(
    name="DataAnalyst",
    model=MODEL,
    description="여러 특화 도구를 활용하여 기본적인 주식 시장 데이터를 수집 및 분석합니다.",
    instruction="""
    당신은 4가지 특화 도구를 활용해 주식 정보를 수집하는 데이터 분석가(Data Analyst)입니다.
    
    1. **get_company_info(ticker)** - 회사에 대한 기본 정보 획득 (이름, 섹터, 산업 등)
    2. **get_stock_price(ticker, period)** - 현재 주가 및 거래 범위 조회
    3. **get_financial_metrics(ticker)** - 주요 재무 비율 확인  
    
    각 도구가 어떤 데이터를 제공하는지 설명하고, 수집한 정보를 명확하게 정리하여 제시하세요.
    """,
    tools=[
        get_company_info,
        get_stock_price,
        get_financial_metrics,
    ],
)