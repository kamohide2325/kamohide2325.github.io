"""
楽天市場・Yahoo!ショッピングの価格を取得する
楽天: 検索ページをスクレイピング（JANコードで直接検索）
Yahoo: ショッピングAPIを使用
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
import config


@dataclass
class PurchaseOption:
    source: str          # "rakuten" or "yahoo"
    shop_name: str
    item_name: str
    price: int           # 税込み価格（円）
    shipping: int        # 送料（円）
    total: int           # price + shipping
    url: str
    jan: str


# 除外キーワード（タイトルに含まれる場合はスキップ）
EXCLUDE_KEYWORDS = ["中古", "未使用品", "ジャンク", "訳あり", "アウトレット"]

# 楽天スクレイピング用ブラウザヘッダー
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


def _is_used_item(item_name: str, shop_name: str = "") -> bool:
    """中古・難あり商品かどうか判定"""
    for kw in EXCLUDE_KEYWORDS:
        if kw in item_name:
            return True
    if shop_name.startswith("auc-"):
        return True
    return False


def _parse_price_text(text: str) -> int:
    """価格テキストから数値を抽出（例: '¥1,234' → 1234）"""
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


# ─────────────────────────────────────────────
# 楽天市場（スクレイピング）
# ─────────────────────────────────────────────

def search_rakuten(jan: str) -> list[PurchaseOption]:
    """楽天検索ページをスクレイピングしてJANコードで価格取得"""
    url = f"https://search.rakuten.co.jp/search/mall/{jan}/?s=4&p=1"

    try:
        resp = requests.get(url, headers=RAKUTEN_HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [Rakuten ERROR] JAN={jan}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # 商品リストを取得（複数のセレクタを試みる）
    items = (
        soup.select("div.searchresultitem")
        or soup.select("div.dui-card.searchresult")
        or soup.select("li.product")
        or []
    )

    for item in items[:config.MAX_PURCHASE_CANDIDATES]:
        # 商品名・URL（実際のHTML構造に合わせたセレクタ）
        name_el = (
            item.select_one("a.title-link--3Yuev")
            or item.select_one("h2 a[data-link='item']")
            or item.select_one("h2 a")
            or item.select_one("a[data-link='item']")
        )
        if not name_el:
            continue
        item_name = name_el.get_text(strip=True)
        item_url = name_el.get("href", "")

        # ショップ名
        shop_el = (
            item.select_one("div.content.merchant a")
            or item.select_one(".merchant a")
            or item.select_one(".merchant_name")
            or item.select_one(".shop_name")
            or item.select_one(".dui-shopname")
        )
        shop_name = shop_el.get_text(strip=True) if shop_el else "楽天"

        # 価格
        price_el = (
            item.select_one("div[class*='price--']")
            or item.select_one(".price--3zUvK")
            or item.select_one(".price .important")
            or item.select_one("span.important")
            or item.select_one(".dui-price-main")
            or item.select_one(".price")
        )
        price_text = price_el.get_text(strip=True) if price_el else ""
        price = _parse_price_text(price_text)

        # 送料
        free_ship_el = item.select_one("span[class*='free-shipping-label']")
        shipping = 0 if free_ship_el else 0  # 送料込みで表示される場合が多い

        if not item_name or price <= 0:
            continue
        if _is_used_item(item_name, shop_name):
            continue

        results.append(PurchaseOption(
            source="rakuten",
            shop_name=shop_name,
            item_name=item_name,
            price=price,
            shipping=shipping,
            total=price + shipping,
            url=item_url,
            jan=jan,
        ))

    if not results:
        print(f"  [Rakuten] ヒットなし JAN={jan} (items={len(items)})")

    return results


# ─────────────────────────────────────────────
# Yahoo!ショッピング
# ─────────────────────────────────────────────

def search_yahoo(jan: str) -> list[PurchaseOption]:
    """Yahoo!ショッピング商品検索APIでJANコード検索"""
    url = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
    params = {
        "appid": config.YAHOO_CLIENT_ID,
        "jan_code": jan,
        "results": config.MAX_PURCHASE_CANDIDATES,
        "sort": "+price",
        "in_stock": True,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [Yahoo ERROR] JAN={jan}: {e}")
        return []

    results = []
    for hit in data.get("hits", []):
        item_name = hit.get("name", "")
        if _is_used_item(item_name):
            continue
        price = int(hit.get("price", 0))
        shipping = _yahoo_shipping(hit)
        results.append(PurchaseOption(
            source="yahoo",
            shop_name=hit.get("seller", {}).get("name", ""),
            item_name=item_name,
            price=price,
            shipping=shipping,
            total=price + shipping,
            url=hit.get("url", ""),
            jan=jan,
        ))
    return results


def _yahoo_shipping(hit: dict) -> int:
    """Yahoo!の送料を推定"""
    shipping = hit.get("shipping", {})
    if shipping.get("code") in ("CONDITION_FREE", "FREE") or shipping.get("name") == "送料無料":
        return 0
    charge = shipping.get("charge", 0)
    return int(charge) if charge else 550


# ─────────────────────────────────────────────
# まとめて検索
# ─────────────────────────────────────────────

def fetch_purchase_options(jan: str) -> list[PurchaseOption]:
    """楽天・Yahooを検索して最安値順に返す"""
    results = []
    results.extend(search_rakuten(jan))
    time.sleep(config.REQUEST_INTERVAL)
    results.extend(search_yahoo(jan))
    time.sleep(config.REQUEST_INTERVAL)
    results.sort(key=lambda x: x.total)
    return results


def fetch_purchase_options_split(jan: str) -> tuple[list[PurchaseOption], list[PurchaseOption]]:
    """楽天・Yahooを個別のリストで返す (rakuten_results, yahoo_results)"""
    rakuten = search_rakuten(jan)
    time.sleep(config.REQUEST_INTERVAL)
    yahoo = search_yahoo(jan)
    time.sleep(config.REQUEST_INTERVAL)
    return rakuten, yahoo
