"""
楽天スクレイピングの動作確認スクリプト
使い方: python3 test_rakuten.py
"""
import re
import requests
from bs4 import BeautifulSoup

RAKUTEN_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

TEST_JAN = "4521329346038"

print(f"JAN {TEST_JAN} で楽天を検索中...")
url = f"https://search.rakuten.co.jp/search/mall/{TEST_JAN}/?s=4&p=1"
resp = requests.get(url, headers=RAKUTEN_HEADERS, timeout=15)
print(f"ステータスコード: {resp.status_code}\n")

soup = BeautifulSoup(resp.text, "html.parser")
items = soup.select("div.searchresultitem")
print(f"商品数: {len(items)} 件\n")

if not items:
    print("商品が見つかりません。HTMLの先頭500文字:")
    print(resp.text[:500])
else:
    item = items[0]

    name_el = (
        item.select_one("a[class*='title-link']")
        or item.select_one("h2 a[data-link='item']")
        or item.select_one("h2 a")
        or item.select_one("a[data-link='item']")
    )
    shop_el = (
        item.select_one("div.content.merchant a")
        or item.select_one(".merchant a")
        or item.select_one(".merchant_name")
    )
    price_el = (
        item.select_one("div[class*='price--']")
        or item.select_one(".price .important")
        or item.select_one("span.important")
        or item.select_one(".price")
    )
    free_ship = item.select_one("span[class*='free-shipping-label']")

    print("=== セレクタ確認（1件目）===")
    print(f"商品名: {name_el.get_text(strip=True)[:60] if name_el else 'NOT FOUND'}")
    print(f"URL: {(name_el.get('href') or '')[:80] if name_el else 'NOT FOUND'}")
    print(f"ショップ: {shop_el.get_text(strip=True) if shop_el else 'NOT FOUND'}")
    price_text = price_el.get_text(strip=True) if price_el else ""
    price_num = re.sub(r"[^\d]", "", price_text)
    print(f"価格テキスト: {price_text}  →  ¥{price_num}")
    print(f"送料無料: {'あり' if free_ship else 'なし'}")

    print(f"\n=== 全{len(items)}件の価格 ===")
    for i, it in enumerate(items):
        n = it.select_one("a[class*='title-link']") or it.select_one("h2 a")
        p = it.select_one("div[class*='price--']") or it.select_one(".price")
        name = n.get_text(strip=True)[:40] if n else "???"
        price = re.sub(r"[^\d]", "", p.get_text(strip=True)) if p else "???"
        print(f"  {i+1}. {name} → ¥{price}")
