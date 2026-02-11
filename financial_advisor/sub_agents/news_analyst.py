from google.adk.agents import Agent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from tools import web_search_tool


MODEL = LiteLlm(model="openai/gpt-4o")


news_analyst = LlmAgent(
    name="NewsAnalyst",
    model=MODEL,
    description="웹 검색 도구를 활용해 실제 웹에서 최신 뉴스를 찾아 요약합니다.",
    instruction="""
    당신은 웹 도구를 사용해 최신 뉴스와 정보를 찾는 뉴스 분석 전문가(News Analyst)입니다. 주요 업무는 다음과 같습니다:
    
    1. **웹 검색**: web_search_tool()을 사용해 특정 기업에 대한 최근 뉴스를 찾으세요.
    2. **요약 및 설명**: 찾은 뉴스의 핵심 내용과 관련성을 요약해서 설명하세요.
    
    **사용 가능한 웹 도구:**
    - **web_search_tool()**: 기업 뉴스 검색 및 크롤링
    
    외부 API/툴을 적극 활용하여 현재 시점의 최신 뉴스, 정보를 웹에서 수집하고 요약해 분석하세요.
    """,
    tools=[
        web_search_tool,
    ],
)