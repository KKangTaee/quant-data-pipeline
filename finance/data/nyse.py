import json
import time
import pandas as pd
from pathlib import Path
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


NYSE_URLS = {
    "stock": "https://www.nyse.com/listings_directory/stock",
    "etf": "https://www.nyse.com/listings_directory/etf",
}
NYSE_API_URL = "https://www.nyse.com/api/quotes/filter"
NYSE_INSTRUMENT_TYPES = {
    "stock": "EQUITY",
    "etf": "EXCHANGE_TRADED_FUND",
}


def _fetch_api_rows(kind: str, max_results_per_page: int = 10000) -> list[dict]:
    payload = json.dumps(
        {
            "instrumentType": NYSE_INSTRUMENT_TYPES[kind],
            "pageNumber": 1,
            "sortColumn": "NORMALIZED_TICKER",
            "sortOrder": "ASC",
            "maxResultsPerPage": max_results_per_page,
            "filterToken": "",
        }
    ).encode("utf-8")
    request = Request(
        NYSE_API_URL,
        data=payload,
        headers={
            "content-type": "application/json",
            "origin": "https://www.nyse.com",
            "referer": NYSE_URLS[kind],
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Chrome/120 Safari/537.36"
            ),
        },
        method="POST",
    )
    with urlopen(request, timeout=40) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, list):
        raise RuntimeError(f"NYSE listing API returned unexpected payload for {kind}.")
    return data


def _parse_api_rows(rows: list[dict]) -> tuple[pd.DataFrame, dict]:
    parsed = []
    for row in rows:
        symbol = str(row.get("normalizedTicker") or row.get("symbolExchangeTicker") or "").strip()
        name = str(row.get("instrumentName") or "").strip()
        url = str(row.get("url") or "").strip()
        if not symbol or not name:
            continue
        parsed.append({"symbol": symbol, "name": name, "url": url})

    df = pd.DataFrame(parsed)
    if df.empty:
        return pd.DataFrame(columns=["symbol", "name", "url"]), {
            "api_total": 0,
            "api_rows": len(rows),
            "usable_rows": 0,
            "deduped_rows": 0,
            "duplicate_symbol_rows": 0,
        }

    api_total = int(rows[0].get("total") or len(rows)) if rows else 0
    df["_symbol_key"] = df["symbol"].str.lower()
    df["_uppercase_rank"] = df["symbol"].map(lambda value: 0 if value == value.upper() else 1)
    deduped = (
        df.sort_values(["_symbol_key", "_uppercase_rank"])
        .drop_duplicates("_symbol_key", keep="first")
        .drop(columns=["_symbol_key", "_uppercase_rank"])
        .sort_values("symbol")
        .reset_index(drop=True)
    )
    return deduped, {
        "api_total": api_total,
        "api_rows": len(rows),
        "usable_rows": len(df),
        "deduped_rows": len(deduped),
        "duplicate_symbol_rows": len(df) - len(deduped),
    }


def _create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver


def _accept_cookies(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(text(), "Accept All Cookies")]')
            )
        ).click()
    except TimeoutException:
        pass


def _parse_table(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")

    table = soup.select_one("table.table-data")
    if table is None:
        return []

    rows = table.select("tbody tr")
    data = []

    for row in rows:
        tds = row.find_all("td")

        # ✅ 구조가 깨진 row 제거
        if len(tds) < 2:
            continue

        a = tds[0].find("a")
        if a is None:
            continue

        symbol = a.text.strip()
        url = a.get("href", "").strip()
        name = tds[1].text.strip()

        if not symbol or not name:
            continue

        data.append({
            "symbol": symbol,
            "name": name,
            "url": url
        })

    return data

def _click_next(driver) -> bool:
    """
    Next 버튼 클릭
    성공하면 True, 없으면 False
    """
    try:
        next_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[rel="next"]')
            )
        )

        # disabled 상태 체크
        parent_li = next_btn.find_element(By.XPATH, "..")
        if "text-gray-500" in parent_li.get_attribute("class"):
            return False

        driver.execute_script("arguments[0].click();", next_btn)
        return True

    except TimeoutException:
        return False


def load_nyse_listings(
    kind: str = "stock",
    save_csv: bool = True,
    sleep: float = 1.5
) -> pd.DataFrame:
    """
    NYSE 상장 종목 / ETF 리스트 수집

    kind : "stock" | "etf"
    """
    if kind not in NYSE_URLS:
        raise ValueError(f"kind는 {list(NYSE_URLS.keys())} 중 하나여야 합니다.")

    rows = _fetch_api_rows(kind)
    df, stats = _parse_api_rows(rows)
    if df.empty:
        raise RuntimeError(f"NYSE listing API returned no usable {kind} rows.")

    print(f"[{kind.upper()}] API 수집 완료: {stats}")

    if save_csv:
        out_dir = Path("csv")
        out_dir.mkdir(exist_ok=True)
        path = out_dir / f"nyse_{kind}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"✅ CSV 저장 완료 → {path}")

    return df
