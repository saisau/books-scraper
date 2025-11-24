from bs4 import BeautifulSoup
import requests
import pandas as pd
from urllib.parse import urljoin
import re

BASE_URL = "https://books.toscrape.com/catalogue/"
CSV_Title="books_detail_minimal.csv"
records = []


def fetch_book_detail(book_url: str) -> dict:
    """1冊分の詳細ページにアクセスして、タイトル・価格・通貨・URLを返す"""
    try:
        resp = requests.get(book_url, timeout=10)
        resp.encoding = "utf-8"
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"詳細ページの取得に失敗しました: {e}")

    soup = BeautifulSoup(resp.text, "html.parser")
    product_main = soup.find("div", class_="product_main")
    if product_main is None:
        raise ValueError("product_main が見つかりません")

    # タイトル
    title = product_main.find("h1").get_text(strip=True)

    # 価格
    price_tag = product_main.find("p", class_="price_color")
    if price_tag is None:
        raise ValueError("price_tag が見つかりません")

    raw_price = price_tag.get_text(strip=True)
    price_str = re.sub(r"[^\d.]", "", raw_price)
    if not price_str:
        raise ValueError(f"価格文字列のパースに失敗しました: {raw_price!r}")

    price_value = float(price_str)

    # 通貨はこのサイトでは GBP 固定
    currency = "GBP"

    return {
        "title": title,
        "url": book_url,
        "price": price_value,
        "currency": currency,
    }


# --- 一覧ページを next ボタンで最後まで辿る ---
url = urljoin(BASE_URL, "page-1.html")

while True:
    print(f"[INFO] 一覧ページ取得中: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[WARN] 一覧ページの取得に失敗しました: {e}")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    if not products:
        print("[INFO] 商品が見つからなかったため終了します。")
        break

    for idx, product in enumerate(products, start=1):
        try:
            # 詳細URLを取る
            a_tag = product.find("h3").find("a")
            if a_tag is None:
                raise ValueError("a_tag が見つかりませんでした")

            detail_url = urljoin(BASE_URL, a_tag["href"])

            # 詳細ページにアクセスして4項目を取得
            book_data = fetch_book_detail(detail_url)

            records.append(book_data)

        except Exception as e:
            print(f"[WARN] 一覧ページ内の商品 {idx} の処理中にエラー: {e}")
            continue

    # next ボタンを探して次ページへ
    pager_next = soup.find("li", class_="next")
    if not pager_next:
        print("[INFO] next ボタンがないため、最終ページと判断して終了します。")
        break

    next_href = pager_next.find("a")["href"]
    url = urljoin(BASE_URL, next_href)

# --- CSV 出力（タイトル・価格・通貨・URL のみ）---
df = pd.DataFrame(records, columns=["title", "price", "currency", "url"])
df.to_csv(CSV_Title, index=False, encoding="utf-8-sig")
print(f"[INFO] 取得件数: {len(records)} 件")
