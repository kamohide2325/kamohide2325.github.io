"""
楽天市場・Yahoo!ショッピングのAPIで仕入れ価格を取得する
"""

import time
import requests
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


def _is_used_item(item_name: str, shop_name: str = "") -> bool:
    """中古・難あり商品かどうか判定"""
    for kw in EXCLUDE_KEYWORDS:
        if kw in item_name:
            return True
    if shop_name.startswith("auc-"):
        return True
    return False


# ─────────────────────────────────────────────
# 楽天市場
# ─────────────────────────────────────────────

def search_rakuten(jan: str) -> list[PurchaseOption]:
    """
    楽天 Product Search APIでJANコード検索。
    IchibaItem APIよりJAN精度が高く、楽天内最安値を取得できる。
    """
    url = "https://app.rakuten.co.jp/services/api/Product/Search/20170426"
    params = {
        "applicationId": config.RAKUTEN_APP_ID,
        "keyword": jan,
        "hits": config.MAX_PURCHASE_CANDIDATES,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [Rakuten ERROR] JAN={jan}: {e}")
        return []

    results = []
    for item in data.get("Items", []):
        it = item.get("Item", item)
        product_name = it.get("productName", "")
        if _is_used_item(product_name):
            continue
        min_price = int(it.get("minPrice", 0))
        if min_price <= 0:
            continue
        product_url = it.get("productUrlPc") or it.get("productUrl", "")
        results.append(PurchaseOption(
            source="rakuten",
            shop_name="楽天市場",
            item_name=product_name,
            price=min_price,
            shipping=0,
            total=min_price,
            url=product_url,
            jan=jan,
        ))
    return results


def _rakuten_shipping(item: dict) -> int:
    """楽天の送料を推定（postageFlag=0が送料無料）"""
    if item.get("postageFlag") == 0:
        return 0
    # 送料不明の場合はデフォルト送料を設定
    return 550


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
    # "CONDITION_FREE" or "FREE" = 送料無料
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
