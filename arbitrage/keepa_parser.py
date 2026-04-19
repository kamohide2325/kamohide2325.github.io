"""
Keepa CSVファイルのパーサー
Keepaからエクスポートした販売上位リストを読み込む
"""

import csv
import re
from dataclasses import dataclass
from typing import Optional


# Amazon FBA サイズ区分
SIZE_SMALL   = "小型"
SIZE_MEDIUM  = "標準"
SIZE_LARGE   = "大型"
SIZE_XLARGE  = "特大型"
SIZE_UNKNOWN = "不明"


@dataclass
class KeepaProduct:
    asin: str
    title: str
    jan: Optional[str]
    amazon_price: int
    sales_rank: Optional[int]
    category: Optional[str]
    bought_last_month: Optional[int]
    weight_g: Optional[float]    # 重量（グラム）
    length_cm: Optional[float]   # 最長辺（cm）
    width_cm: Optional[float]    # 次辺（cm）
    height_cm: Optional[float]   # 最短辺（cm）

    @property
    def size_tier(self) -> str:
        """Amazon FBA サイズ区分を返す（判定できない場合は不明）"""
        w = self.weight_g
        dims = sorted(
            [d for d in [self.length_cm, self.width_cm, self.height_cm] if d is not None],
            reverse=True,
        )
        if not dims:
            return SIZE_UNKNOWN

        l = dims[0]
        m = dims[1] if len(dims) > 1 else 0
        s = dims[2] if len(dims) > 2 else 0

        # 重量不明の場合は寸法のみで判定
        weight_ok_small  = (w is None or w <= 250)
        weight_ok_medium = (w is None or w <= 9000)
        weight_ok_large  = (w is None or w <= 25000)

        if weight_ok_small and l <= 25 and m <= 18 and s <= 2:
            return SIZE_SMALL
        if weight_ok_medium and l <= 35 and m <= 25 and s <= 12:
            return SIZE_MEDIUM
        if weight_ok_large and l <= 120 and m <= 60 and s <= 60:
            return SIZE_LARGE
        return SIZE_XLARGE


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
                weight_g=_parse_float(_get(row, col.get("weight"), "")),
                length_cm=_parse_float(_get(row, col.get("length"), "")),
                width_cm=_parse_float(_get(row, col.get("width"), "")),
                height_cm=_parse_float(_get(row, col.get("height"), "")),
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
        "weight":   ["package weight", "weight (g)", "weight(g)", "重量"],
        "length":   ["package length", "length (cm)", "length(cm)", "長さ"],
        "width":    ["package width", "width (cm)", "width(cm)", "幅"],
        "height":   ["package height", "height (cm)", "height(cm)", "高さ"],
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


def _parse_float(s: str) -> Optional[float]:
    """数値文字列をfloatに変換（変換不可はNone）"""
    digits = re.sub(r"[^\d.]", "", s)
    try:
        return float(digits) if digits else None
    except ValueError:
        return None
