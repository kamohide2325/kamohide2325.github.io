"""
楽天スクレイピングの動作確認スクリプト
使い方: python3 test_rakuten.py
"""
import requests
from bs4 import BeautifulSoup
from price_fetcher import RAKUTEN_HEADERS, _parse_price_text

TEST_JAN = "4521329346038"  # ポケモンカード

print(f"JAN {TEST_JAN} で楽天を検索中...")
url = f"https://search.rakuten.co.jp/search/mall/{TEST_JAN}/?s=4&p=1"
resp = requests.get(url, headers=RAKUTEN_HEADERS, timeout=15)
print(f"ステータスコード: {resp.status_code}")

soup = BeautifulSoup(resp.text, "html.parser")

# どのセレクタが機能するか確認
for selector in [
    "div.searchresultitem",
    "div.dui-card.searchresult",
    "li.product",
    "div[data-ratid]",
]:
    items = soup.select(selector)
    print(f"  セレクタ '{selector}': {len(items)} 件")

# 最初の商品を詳細表示
items = soup.select("div.searchresultitem") or soup.select("div.dui-card") or []
if items:
    print(f"\n最初の商品のHTML（先頭500文字）:")
    print(str(items[0])[:500])
else:
    print("\n商品リストが見つかりません。ページタイトル:")
    print(soup.title.string if soup.title else "不明")
