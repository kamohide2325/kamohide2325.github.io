"""
Keepa CSVファイルのパーサー
Keepaからエクスポートした販売上位リストを読み込む
"""

import csv
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class KeepaProduct:
    asin: str
    title: str
    jan: Optional[str]        # JAN/EAN コード
    amazon_price: int         # Amazon現在価格（円）
    sales_rank: Optional[int]
    category: Optional[str]
    bought_last_month: Optional[int]


def normalize_jan(code: str) -> Optional[str]:
    """JAN/EANコードを正規化（数字のみ、13桁または8桁）"""
    if not code:
        return None
    digits = re.sub(r"\D", "", code)
    if len(digits) in (8, 12, 13):
        return digits.zfill(13) if len(digits) == 12 else digits
    return None


def parse_keepa_csv(filepath: str) -> list[KeepaProduct]:
    """
    KeepaのCSVエクスポートを読み込む。
    Keepa→エクスポート→CSVを前提とする。
    列名はKeepaのバージョンで変わる場合があるため柔軟にマッピングする。
    """
    products = []

    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = [h.strip() for h in reader.fieldnames or []]

        col = _detect_columns(headers)

        for row in reader:
            asin = _get(row, col.get("asin"), "").strip()
            if not asin:
                continue

            price_str = _get(row, col.get("price"), "0")
            price = _parse_price(price_str)
            if price <= 0:
                continue

            jan_raw = _get(row, col.get("jan"), "")
            jan = normalize_jan(jan_raw)

            rank_str = _get(row, col.get("rank"), "")
            rank = int(re.sub(r"\D", "", rank_str)) if rank_str else None

            bought_str = _get(row, col.get("bought"), "")
            bought = int(re.sub(r"\D", "", bought_str)) if bought_str else None

            products.append(KeepaProduct(
                asin=asin,
                title=_get(row, col.get("title"), ""),
                jan=jan,
                amazon_price=price,
                sales_rank=rank,
                category=_get(row, col.get("category"), ""),
                bought_last_month=bought,
            ))

    return products


def _detect_columns(headers: list[str]) -> dict:
    """ヘッダー名からカラムを自動検出"""
    mapping = {}
    lower = [h.lower() for h in headers]

    patterns = {
        "asin":     ["asin"],
        "title":    ["title", "product name", "商品名"],
        "jan":      ["jan", "ean", "upc", "barcode"],
        "price":    ["buy box price", "amazon price", "price", "価格"],
        "rank":     ["sales rank", "rank", "ランク"],
        "category": ["category", "カテゴリ"],
        "bought":   ["bought in past month", "bought last month", "月間購入数"],
    }

    for key, candidates in patterns.items():
        for cand in candidates:
            for i, h in enumerate(lower):
                if cand in h:
                    mapping[key] = headers[i]
                    break
            if key in mapping:
                break

    return mapping


def _get(row: dict, col: Optional[str], default: str) -> str:
    if col and col in row:
        return row[col].strip()
    return default


def _parse_price(s: str) -> int:
    """¥1,234 や 1234 を整数に変換"""
    digits = re.sub(r"[^\d.]", "", s)
    try:
        return int(float(digits))
    except ValueError:
        return 0
