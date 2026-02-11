import yfinance as yf
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm("openai/gpt-5")

def get_income_statement(ticker: str):
    """
    손익계산서를 조회하여 매출 및 수익성에 대한 포괄적 분석을 제공합니다.

    이 도구는 최근 보고 기간(분기/연간)의 회사 손익계산서 데이터를 상세하게 가져와
    수익(매출), 비용, 각종 이익률(마진) 등을 다층적으로 보여줍니다.

    매개변수:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 애플)

    반환값:
        dict: 다음 정보를 포함하는 딕셔너리
            - ticker (str): 입력한 티커 심볼
            - success (bool): 성공 시 True
            - income_statement (str): JSON 형식의 손익계산서 데이터.
                * 총매출(Total Revenue)
                * 매출원가(Cost of Revenue)
                * 총이익(Gross Profit)
                * 영업비용(Operating Expenses)
                * 영업이익(Operating Income)
                * EBITDA
                * 순이익(Net Income)
                * 주당순이익(EPS, Earnings Per Share)

    참고:
        - 일반적으로 최근 4개 분기 및 연간 데이터 제공
        - 모든 재무 수치는 회사의 공시 통화 기준
        - 매출 성장, 이익률 추세, 수익성 분석에 유용

    예시:
        >>> get_income_statement('GOOGL')
        {
            'ticker': 'GOOGL',
            'success': True,
            'income_statement': '{"Total Revenue": {...}, "Net Income": {...}}'
        }
    """
    stock = yf.Ticker(ticker)
    # return stock.income_stmt.to_json()
    return {
        "ticker": ticker,
        "success": True,
        "income_statement": stock.income_stmt.to_json(),
    }


def get_balance_sheet(ticker: str):
    """
    재무상태표(대차대조표)를 조회하여 기업의 재무 건전성과 자본 구조를 분석합니다.

    이 도구는 특정 시점(분기/연말)의 자산, 부채, 자본 등 폭넓은 대차대조표 데이터를 제공하며,
    기업의 재무 건전성 및 자본 효율성을 평가하는 데 활용됩니다.

    매개변수:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 애플)

    반환값:
        dict: 다음 정보를 담은 딕셔너리
            - ticker (str): 입력한 티커 심볼
            - success (bool): 성공 시 True
            - balance_sheet (str): JSON 형식의 대차대조표 데이터. 포함 항목:
                * 유동자산(현금, 매출채권, 재고자산 등)
                * 비유동자산(유형자산, 무형자산, 투자 등)
                * 유동부채(매입채무, 단기부채 등)
                * 비유동부채(장기부채, 이연항목 등)
                * 총 자본(자본총계)
                * 운전자본 관련 항목

    참고:
        - 분기/연말 기준의 재무 상태 스냅샷 제공
        - 유동비율, 당좌비율 등 유동성 비율 산출에 필수
        - 부채 수준, 자산 효율성, 장부가치 평가에 활용
        - 모든 수치는 회사의 공시 통화 기준

    예시:
        >>> get_balance_sheet('AMZN')
        {
            'ticker': 'AMZN',
            'success': True,
            'balance_sheet': '{"Total Assets": {...}, "Total Liabilities": {...}}'
        }
    """
    stock = yf.Ticker(ticker)
    # return stock.balance_sheet.to_json()
    return {
        "ticker": ticker,
        "success": True,
        "balance_sheet": stock.balance_sheet.to_json(),
    }


def get_cash_flow(ticker: str):
    """
    기업의 현금창출력과 자본배분 구조를 분석할 수 있도록 현금흐름표(Cash Flow Statement)를 조회합니다.

    이 도구는 영업활동, 투자활동, 재무활동 등 다양한 영역에서 기업이 어떻게 현금을 창출하고 사용하는지에 대한 상세 데이터(현금흐름표)를 제공합니다. 기업의 재무적 지속 가능성과 성장 잠재력을 평가하는 데 필수적입니다.

    매개변수:
        ticker (str): 주식 티커 심볼 (예: 'AAPL'은 애플)

    반환값:
        dict: 다음 정보를 담은 딕셔너리
            - ticker (str): 입력한 티커 심볼
            - success (bool): 작업 성공 시 True
            - cash_flow (str): JSON 포맷의 현금흐름표 데이터, 주요 항목 포함:
                * 영업활동현금흐름(핵심 사업에서 발생한 현금, Operating Cash Flow)
                * 자본적지출(CapEx, 설비·유형자산 투자, Capital Expenditures)
                * 잉여현금흐름(영업 CF - 자본적지출, Free Cash Flow)
                * 투자활동현금흐름(인수, 투자 등, Investing Activities)
                * 재무활동현금흐름(부채, 배당, 자사주 등, Financing Activities)
                * 현금변동액(Net Change in Cash)

    참고:
        - 영업활동현금흐름: 주사업의 현금창출력 지표
        - 잉여현금흐름: 주주환원·성장 투자 여력
        - 투자 현금흐름이 마이너스면, 적극적 투자 진행 중일 수 있음
        - 재무활동 현금흐름: 자본구조(부채·배당 등) 결정 반영
        - 배당지급 및 성장 투자 여력 판단의 핵심 지표

    Example:
        >>> get_cash_flow('META')
        {
            'ticker': 'META',
            'success': True,
            'cash_flow': '{"Operating Cash Flow": {...}, "Free Cash Flow": {...}}'
        }
    """
    stock = yf.Ticker(ticker)
    # return stock.balance_sheet.to_json()
    return {
        "ticker": ticker,
        "success": True,
        "cash_flow": stock.cash_flow.to_json(),
    }


financial_analyst = Agent(
    name="FinancialAnalyst",
    model=MODEL,
    description="손익계산서, 재무상태표, 현금흐름표 등 기업 재무제표를 종합적으로 분석합니다.",
    instruction="""
    당신은 심층적인 재무제표 분석을 수행하는 재무 애널리스트입니다. 
    
    주요 업무:
    1. **손익 분석(Income Analysis)**: get_income_statement()를 활용해 매출, 수익성, 이익률을 분석하세요.
    2. **재무상태 분석(Balance Sheet Analysis)**: get_balance_sheet()로 자산, 부채, 자본구조 등 재무 구성을 파악하세요.
    3. **현금흐름 분석(Cash Flow Analysis)**: get_cash_flow()로 기업의 현금 창출력과 자본배분 구조를 평가하세요.
    
    **사용 가능한 재무 도구:**
    - **get_income_statement(ticker)**: 매출, 이익률, 수익성 분석
    - **get_balance_sheet(ticker)**: 자산, 부채, 자기자본, 재무안정성 지표
    - **get_cash_flow(ticker)**: 영업활동현금흐름, 잉여현금흐름, 자본적지출

    재무제표 데이터를 바탕으로 기업의 재무 건전성과 실적을 분석하세요.
    중요한 재무 비율, 추세(트렌드), 그리고 건전성을 보여주는 주요 지표에 주목하세요.
    """,
    tools=[
        get_income_statement,
        get_balance_sheet,
        get_cash_flow,
    ],
)