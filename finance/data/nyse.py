import time
import pandas as pd
from pathlib import Path
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

    driver = _create_driver()
    driver.get(NYSE_URLS[kind])
    _accept_cookies(driver)

    all_rows = []

    while True:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".table-data.w-full.table-border-rows tbody tr")
            )
        )

        all_rows.extend(_parse_table(driver.page_source))
        print(f"[{kind.upper()}] 수집중... {len(all_rows):,} rows")

        # 🔁 다음 페이지 이동
        if not _click_next(driver):
            break

        time.sleep(sleep)


    driver.quit()

    df = pd.DataFrame(all_rows).drop_duplicates("symbol").reset_index(drop=True)

    if save_csv:
        out_dir = Path("csv")
        out_dir.mkdir(exist_ok=True)
        path = out_dir / f"nyse_{kind}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"✅ CSV 저장 완료 → {path}")

    return df