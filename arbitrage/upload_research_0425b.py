"""
千葉県築古戸建リサーチ結果（2026年4月25日 第2回）を
Excelに保存してGoogleスプレッドシートへアップロードする

実行方法:
    cd ~/kamohide2325.github.io/arbitrage
    python3 upload_research_0425b.py
"""

from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from google_uploader import upload_to_sheets, open_url


def build_excel(path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "千葉県築古戸建リサーチ第2回"

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    blue_fill    = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    green_fill   = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
    orange_fill  = PatternFill(start_color="FF8C00", end_color="FF8C00", fill_type="solid")
    red_fill     = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    lightgreen   = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    lightblue    = PatternFill(start_color="DEEAF1", end_color="DEEAF1", fill_type="solid")
    lightyellow  = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    lightorange  = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    lightred     = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")

    headers = [
        "No.", "所在地", "最寄り駅・アクセス", "価格(万円)", "表面利回り",
        "推定月額賃料", "土地面積", "建物面積", "築年（築年数）",
        "間取り", "駐車場", "構造", "ステータス", "URL", "短評・注意点",
    ]
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.fill = blue_fill
        c.font = Font(bold=True, color="FFFFFF", size=10)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border
    ws.row_dimensions[1].height = 30

    def section_row(row, label, fill):
        c = ws.cell(row=row, column=1, value=label)
        c.fill = fill
        c.font = Font(bold=True, color="FFFFFF", size=11)
        c.alignment = Alignment(horizontal="left", vertical="center")
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=15)
        ws.row_dimensions[row].height = 22
        for col in range(2, 16):
            ws.cell(row=row, column=col).fill = fill

    def data_row(row, cols_1_13, url, note, fill):
        for col, val in enumerate(cols_1_13, 1):
            c = ws.cell(row=row, column=col, value=val)
            c.fill = fill
            c.font = Font(size=10)
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            c.border = border
        # 14列目：URL（クリッカブルリンク）
        uc = ws.cell(row=row, column=14, value="🔗 開く" if url else "—")
        if url:
            uc.hyperlink = url
            uc.font = Font(color="0070C0", underline="single", size=10)
        else:
            uc.font = Font(size=10, color="999999")
        uc.fill = fill
        uc.alignment = Alignment(horizontal="center", vertical="center")
        uc.border = border
        # 15列目：短評
        nc = ws.cell(row=row, column=15, value=note)
        nc.fill = fill
        nc.font = Font(size=10)
        nc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        nc.border = border
        ws.row_dimensions[row].height = 55

    # ===== 候補物件（個別URL確認済みのみ掲載） =====
    section_row(2, "【候補物件】個別URLが確認できた物件のみ掲載", green_fill)

    # row_data: (no, address, station, price, yield, rent, land, bldg, built, layout, parking, structure, status, note, url, fill)
    candidates = [
        (1, "千葉県旭市二", "要確認",
         398, "要確認", "不明", "185㎡", "不明", "1994年（築32年）",
         "2DK", "要確認", "不明", "詳細要確認",
         "1994年築で比較的新しめ（築古の中では良好）。土地185㎡。OC・水道・下水・再建築可否・駐車場は問合せ必須。",
         "https://www.kenbiya.com/pp8/s/chiba/asahi-shi/re_4387203i7a/", lightyellow),
    ]

    r = 3
    for row_data in candidates:
        fill  = row_data[-1]
        url   = row_data[-2]
        note  = row_data[-3]
        cols  = list(row_data[:-3])  # no 〜 status（13列）
        data_row(r, cols, url, note, fill or PatternFill())
        r += 1

    # ===== URL未取得のため非掲載 =====
    r += 1
    section_row(r, "【URL未取得のため非掲載】個別ページURLが確認できなかった物件 → 健美家・イエステーション旭市店で手動確認してください", orange_fill)
    r += 1

    no_url_list = [
        ("—", "千葉県旭市（土地743㎡）", "要確認", "298万", "要確認", "不明", "743㎡", "不明", "1986年（築40年）", "2DK", "要確認", "不明", "URL未取得"),
        ("—", "千葉県旭市桜井（土地465㎡）", "旭駅 徒歩88分（車必須）", "320万", "要確認", "不明", "465㎡", "67㎡", "1968年（築58年）", "4K", "要確認", "不明", "URL未取得"),
        ("—", "千葉県旭市（土地438㎡）", "要確認", "328万", "要確認", "不明", "438㎡", "不明", "1979年（築47年）", "5DK", "要確認", "不明", "URL未取得"),
        ("—", "千葉県旭市（土地204㎡）", "要確認", "330万", "要確認", "不明", "204㎡", "不明", "1974年（築52年）", "5DK", "要確認", "不明", "URL未取得"),
        ("—", "千葉県旭市（土地198㎡）", "要確認", "350万", "要確認", "不明", "198㎡", "不明", "1974年（築52年）", "5DK", "要確認", "不明", "URL未取得"),
        ("—", "千葉県旭市（土地164㎡）", "要確認", "358万", "要確認", "不明", "164㎡", "不明", "1983年（築43年）", "5DK", "要確認", "不明", "URL未取得"),
        ("—", "千葉県旭市（土地140㎡）", "要確認", "400万", "要確認", "不明", "140㎡", "87㎡", "1989年（築37年）", "1LDK", "要確認", "不明", "URL未取得"),
        ("—", "千葉県山武市蓮沼イ（100坪超）", "要確認", "298万", "要確認", "不明", "330㎡超", "不明", "不明", "4DK", "あり（カーポート）", "平屋", "URL未取得"),
    ]
    for row_data in no_url_list:
        for col, val in enumerate(row_data, 1):
            c = ws.cell(row=r, column=col, value=val)
            c.fill = lightorange
            c.font = Font(size=10)
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            c.border = border
        uc = ws.cell(row=r, column=14, value="—")
        uc.fill = lightorange
        uc.font = Font(size=10, color="999999")
        uc.alignment = Alignment(horizontal="center", vertical="center")
        uc.border = border
        nc = ws.cell(row=r, column=15, value="個別URLが確認できなかったため非掲載。旭市物件はイエステーション旭市店（yes1.co.jp/asahi）にまとめて問合せ推奨。")
        nc.fill = lightorange
        nc.font = Font(size=10)
        nc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        nc.border = border
        ws.row_dimensions[r].height = 40
        r += 1

    # ===== 除外確定 =====
    r += 1
    section_row(r, "【除外確定】絶対除外条件に該当 / 予算超過", red_fill)
    r += 1

    excluded_list = [
        ("❌", "千葉県山武市埴谷", "JR東金線 日向駅 徒歩36分", "398万", "14.1%", "—", "78㎡", "76㎡", "1990年（築36年）", "4DK", "—", "木造", "上水が井戸", "上水が井戸のため絶対除外"),
        ("❌", "千葉県市原市（椎津）", "最寄り駅徒歩圏", "〜798万", "14.73%", "約9.8万円", "不明", "不明", "不明", "不明", "不明", "不明", "予算超過", "推定価格〜798万円で400万円予算超過のため除外（個別URL: re_43387982o9）"),
    ]
    for row_data in excluded_list:
        for col, val in enumerate(row_data, 1):
            c = ws.cell(row=r, column=col, value=val)
            c.fill = lightred
            c.font = Font(size=10)
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            c.border = border
        uc = ws.cell(row=r, column=14, value="—")
        uc.fill = lightred
        uc.font = Font(size=10, color="999999")
        uc.alignment = Alignment(horizontal="center", vertical="center")
        uc.border = border
        ws.row_dimensions[r].height = 30
        r += 1

    # 列幅
    col_widths = [5, 22, 20, 10, 11, 11, 10, 10, 17, 8, 10, 16, 14, 10, 50]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ===== シート2：調査メモ =====
    ws2 = wb.create_sheet("調査メモ・凡例")
    notes = [
        ("■ 調査情報", ""),
        ("調査日",     "2026年4月25日（第2回）"),
        ("調査サイト", "楽待・健美家・HOME'S投資（Google検索キャッシュ経由 / イエステーション旭市店も参照）"),
        ("備考",       "各サイトへの直接アクセスが403エラーのため検索キャッシュで収集。個別URLが確認できた物件のみ掲載（ポリシーに従い一覧ページURLは使用しない）。"),
        ("", ""),
        ("■ 今回の特徴", ""),
        ("",           "旭市に低価格・広大土地の物件が多数確認されましたが、個別URLを取得できなかったため非掲載。"),
        ("",           "旭市物件のURLはイエステーション旭市店（yes1.co.jp/asahi）から直接問合せることを強く推奨します。"),
        ("", ""),
        ("■ 検索条件", ""),
        ("予算",         "400万円以下"),
        ("利回り",       "10%以上"),
        ("駐車場",       "あり"),
        ("対象エリア",   "千葉県の「市」のみ（町・村は除外）"),
        ("除外市",       "野田市・館山市・銚子市・勝浦市・鴨川市・印西市・南房総市・匝瑳市・いすみ市"),
        ("絶対除外条件", "OC / 再建築不可 / 井戸水 / 汲み取り / 傾き / 白アリ"),
        ("", ""),
        ("■ 色の意味", ""),
        ("黄（薄）",    "候補物件（個別URL確認済み）"),
        ("橙（薄）",    "URL未取得のため非掲載 → 手動で要確認"),
        ("赤（薄）",    "除外確定（除外条件に該当 / 予算超過）"),
        ("", ""),
        ("■ 次のアクション（優先順）", ""),
        ("優先①", "物件1（旭市二 398万 1994年築）→ 健美家 re_4387203i7a で詳細確認・問合せ"),
        ("優先②", "旭市 298〜400万の7件（URL未取得）→ イエステーション旭市店にまとめて問合せ"),
        ("優先③", "山武市蓮沼 298万（URL未取得）→ 健美家の山武市ページを直接確認"),
        ("全物件共通", "OC非該当・水道公営・下水汲み取りでない・再建築可・駐車場あり を必ず問合せで確認"),
        ("", ""),
        ("■ 旭市 問合せ先", ""),
        ("イエステーション旭市店", "https://www.yes1.co.jp/asahi/office_search_result/house"),
        ("健美家 旭市", "https://www.kenbiya.com/pp0/s/chiba/asahi-shi/"),
    ]
    for i, (k, v) in enumerate(notes, 1):
        ck = ws2.cell(row=i, column=1, value=k)
        cv = ws2.cell(row=i, column=2, value=v)
        if k.startswith("■"):
            ck.fill = blue_fill
            cv.fill = blue_fill
            ck.font = Font(bold=True, color="FFFFFF", size=10)
            cv.font = Font(color="FFFFFF", size=10)
        elif k.startswith("優先") or k in ("全物件共通",):
            ck.font = Font(bold=True, size=10)
            cv.font = Font(size=10)
        else:
            ck.font = Font(size=10)
            cv.font = Font(size=10)
        cv.alignment = Alignment(wrap_text=True)
    ws2.column_dimensions["A"].width = 25
    ws2.column_dimensions["B"].width = 75

    wb.save(path)
    print(f"Excel保存: {path}")


def main():
    desktop = Path.home() / "Desktop" / "千葉県築古戸建リサーチ結果_20260425b.xlsx"
    build_excel(desktop)

    print("Googleスプレッドシートへアップロード中...")
    url = upload_to_sheets(str(desktop))
    print(f"アップロード完了: {url}")

    open_url(url)
    print("ブラウザで開きました。")


if __name__ == "__main__":
    main()
