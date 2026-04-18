"""
Amazon転売リサーチツール メインスクリプト

使い方:
    python main.py keepa_export.csv

出力:
    results.xlsx  - 利益商品リスト（Excelファイル）
    results.csv   - 同上（CSV形式）
"""

import sys
import time
from pathlib import Path
from datetime import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from keepa_parser import parse_keepa_csv, KeepaProduct
from price_fetcher import fetch_purchase_options, PurchaseOption
from profit_calculator import calculate_profit, ProfitResult, JUDGMENT_PROFITABLE, JUDGMENT_MARGINAL, JUDGMENT_LOSS
import config


def main():
    if len(sys.argv) < 2:
        print("使い方: python main.py <keepa_export.csv>")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"ファイルが見つかりません: {csv_path}")
        sys.exit(1)

    print(f"Keepa CSVを読み込んでいます: {csv_path}")
    products = parse_keepa_csv(csv_path)
    print(f"  {len(products)} 商品を読み込みました")

    jan_products = [p for p in products if p.jan]
    print(f"  うちJANコードあり: {len(jan_products)} 商品\n")

    rows = []
    for i, product in enumerate(jan_products, 1):
        print(f"[{i}/{len(jan_products)}] {product.asin} / JAN:{product.jan}")
        print(f"  Amazon価格: ¥{product.amazon_price:,} | {product.title[:40]}")

        options = fetch_purchase_options(product.jan)
        if not options:
            print("  → 仕入れ候補なし（データなし）")
            rows.append({
                "product": product,
                "best_option": None,
                "all_options": [],
                "profit": None,
                "judgment": "データなし",
            })
            continue

        best = options[0]  # 最安値
        profit_result = calculate_profit(
            amazon_price=product.amazon_price,
            purchase_total=best.total,
            category=product.category or "",
        )

        print(f"  仕入れ最安: ¥{best.total:,} ({best.source} / {best.shop_name})")
        print(f"  利益: ¥{profit_result.profit:,} ({profit_result.profit_rate}%) {profit_result.judgment}")

        rows.append({
            "product": product,
            "best_option": best,
            "all_options": options,
            "profit": profit_result,
            "judgment": profit_result.judgment,
        })

    profitable = [r for r in rows if r.get("judgment") == JUDGMENT_PROFITABLE]
    print(f"\n=== 完了: {len(profitable)} / {len(rows)} 商品が利益あり（粗利1000円以上） ===\n")

    output_path = save_results(profitable, rows)
    print(f"結果を保存しました: {output_path}")


def save_results(profitable_rows: list, all_rows: list) -> str:
    """Excelファイルに結果を保存"""
    wb = openpyxl.Workbook()

    # シート1: 利益あり商品（粗利1000円以上）
    ws1 = wb.active
    ws1.title = "利益あり商品"
    _write_sheet(ws1, profitable_rows)

    # シート2: 全商品（判定別色分け）
    ws2 = wb.create_sheet("全商品")
    _write_sheet(ws2, all_rows)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = f"results_{timestamp}.xlsx"
    wb.save(output)
    return output


# 判定別の背景色
JUDGMENT_COLORS = {
    JUDGMENT_PROFITABLE: "E2EFDA",  # 緑
    JUDGMENT_MARGINAL:   "FFF2CC",  # 黄
    JUDGMENT_LOSS:       "FCE4D6",  # 赤
    "データなし":          "F2F2F2",  # グレー
}


def _write_sheet(ws, rows: list):
    headers = [
        "判定", "ASIN", "タイトル", "JAN", "カテゴリ", "月間購入数",
        "Amazon価格", "仕入れ価格(合計)", "仕入れ先", "ショップ名",
        "参照手数料", "FBA手数料", "利益", "利益率(%)",
        "仕入れURL", "Amazon URL",
    ]

    # ヘッダー行
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="2E75B6")
        cell.alignment = Alignment(horizontal="center")

    for r, row in enumerate(rows, 2):
        p: KeepaProduct = row["product"]
        opt: PurchaseOption = row.get("best_option")
        pr: ProfitResult = row.get("profit")
        judgment: str = row.get("judgment", "データなし")

        values = [
            judgment,
            p.asin,
            p.title,
            p.jan,
            p.category,
            p.bought_last_month,
            p.amazon_price,
            opt.total if opt else "",
            opt.source if opt else "",
            opt.shop_name if opt else "",
            pr.referral_fee if pr else "",
            pr.fba_fee if pr else "",
            pr.profit if pr else "",
            pr.profit_rate if pr else "",
            opt.url if opt else "",
            f"https://www.amazon.co.jp/dp/{p.asin}",
        ]

        bg_color = JUDGMENT_COLORS.get(judgment, "FFFFFF")
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=r, column=col, value=val)
            cell.alignment = Alignment(horizontal="left")
            cell.fill = PatternFill("solid", fgColor=bg_color)

    # 列幅調整
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    ws.column_dimensions["A"].width = 28  # 判定列
    ws.column_dimensions["C"].width = 40  # タイトル列
    ws.column_dimensions["O"].width = 50  # 仕入れURL列


if __name__ == "__main__":
    main()
