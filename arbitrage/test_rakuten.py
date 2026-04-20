"""
楽天スクレイピングの動作確認スクリプト
使い方: python3 test_rakuten.py
"""
import requests
from bs4 import BeautifulSoup
from price_fetcher import RAKUTEN_HEADERS

TEST_JAN = "4521329346038"

print(f"JAN {TEST_JAN} で楽天を検索中...")
url = f"https://search.rakuten.co.jp/search/mall/{TEST_JAN}/?s=4&p=1"
resp = requests.get(url, headers=RAKUTEN_HEADERS, timeout=15)
print(f"ステータスコード: {resp.status_code}\n")

soup = BeautifulSoup(resp.text, "html.parser")
items = soup.select("div.searchresultitem")
print(f"商品数: {len(items)} 件\n")

if items:
    item = items[0]
    print("=== 最初の商品のHTML全文 ===")
    print(str(item))
