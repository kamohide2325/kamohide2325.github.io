"""
千葉県築古戸建リサーチ結果（2026年4月25日）を
Excelに保存してGoogleスプレッドシートへアップロードする

実行方法:
    cd ~/kamohide2325.github.io/arbitrage
    python3 upload_research_0425.py
"""

from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from google_uploader import upload_to_sheets, open_url


def build_excel(path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "千葉県築古戸建リサーチ"

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    blue_fill    = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    green_fill   = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
    orange_fill  = PatternFill(start_color="FF8C00", end_color="FF8C00", fill_type="solid")
    red_fill     = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    lightgreen   = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    lightblue    = PatternFill(start_color="DEEAF1", end_color="DEEAF1", fill_type="solid")
    lightyellow  = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    lightgray    = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
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

    def data_row(row, vals, fill, url=None):
        for col, val in enumerate(vals, 1):
            c = ws.cell(row=row, column=col, value=val)
            c.fill = fill
            c.font = Font(size=10)
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            c.border = border
        if url:
            uc = ws.cell(row=row, column=14, value="🔗 開く")
            uc.hyperlink = url
            uc.font = Font(color="0070C0", underline="single", size=10)
            uc.fill = fill
            uc.alignment = Alignment(horizontal="center", vertical="center")
            uc.border = border
        ws.row_dimensions[row].height = 55

    # 候補物件
    section_row(2, "【候補物件】条件合致の可能性あり", green_fill)

    candidates = [
        (1, "千葉県市原市金剛地", "JR外房線 土気駅\nバス+徒歩 約90分",
         171, "35.08%", "5.0万円", "205.91㎡", "67.36㎡", "1968年（築58年）",
         "3DK", "あり（2台）", "木造平屋", "空室・即引渡し可",
         "超格安・超高利回り。土気駅90分超と交通極悪で賃付け難易度高。土地200㎡超は強み。水道・下水・再建築可否は問合せ必須。",
         "https://www.kenbiya.com/pp8/s/chiba/ichihara-shi/re_4283103wpt/", lightblue),
        (2, "千葉県茂原市高師", "JR外房線 茂原駅\n徒歩 約21〜22分",
         400, "13.50%", "4.5万円", "165.28㎡", "64.43㎡", "1968年（築57年）",
         "3DK", "要確認", "木造平屋", "空室（要確認）",
         "茂原駅から徒歩圏で立地は悪くない。木造平屋1968年築。土地165㎡で土地値期待。駐車場・再建築可否・水道下水は要確認。",
         "https://www.kenbiya.com/pp8/s/chiba/mobara-shi/re_4434813nmi/", None),
        (3, "千葉県大網白里市上谷新田", "JR東金線 福俵駅\n約3.9km（車必須）",
         398, "18.99%", "6.3万円", "129.94㎡", "94.28㎡", "1984年（築41年）",
         "5DK", "要確認", "S造（軽量鉄骨）2階", "空室（要確認）",
         "★最注目★ 鉄骨造で耐久性高め・高利回り・5DK大型間取り。車社会エリア。再建築可否・水道・下水・駐車場は要問合せ。",
         "https://www.kenbiya.com/pp8/s/chiba/oamishirasato-shi/re_39623525ze/", lightgreen),
        (4, "千葉県大網白里市", "要問合せ",
         390, "15.38%", "5.0万円", "不明", "不明", "不明",
         "不明", "不明", "不明", "詳細不明",
         "楽待・健美家の複数サイトに掲載あり。詳細取得困難。サイト直接確認・問合せ必要。",
         "https://www.kenbiya.com/pp8/s/chiba/oamishirasato-shi/re_3421676myx/", lightgray),
        (5, "千葉県山武市（成東エリア）", "JR総武線 成東駅\n徒歩約44分（車必須）",
         350, "18.85%", "5.5万円", "157㎡", "82.21㎡", "1990年（築36年）",
         "4DK", "あり（1台）", "木造2階", "⚠ OC確認必須",
         "1990年築で比較的新しめ。成東駅徒歩44分は非現実的。農村エリアでニーズ限定。OCの可能性あり→問合せ必須。水道・下水・再建築可否も要確認。",
         "https://www.kenbiya.com/pp8/s/chiba/sammu-shi/re_43649517nt/", lightyellow),
    ]

    r = 3
    for row_data in candidates:
        fill = row_data[-1]
        vals = list(row_data[:-2])
        url  = row_data[-2]
        data_row(r, vals + ["", ""], fill or PatternFill(), url)
        r += 1

    # 調査中断
    r += 1
    section_row(r, "【調査中断】APIレート制限により途中で打ち切り → 手動確認が必要", orange_fill)
    r += 1

    interrupted = [
        ("A", "千葉県旭市", "調査中断のため不明",
         180, "約30%（要確認）", "不明", "不明", "不明", "不明",
         "不明", "不明", "不明", "⚠ 調査中断",
         "APIレート制限で調査打ち切り。180万・利回り30%の可能性あり。条件合致なら最有力候補。健美家の旭市ページを直接確認してください。",
         "https://www.kenbiya.com/pp0/s/chiba/asahi-shi/"),
        ("B", "千葉県茂原市", "不明",
         190, "不明", "不明", "不明", "不明", "不明",
         "不明", "あり", "不明", "⚠ 詳細要確認",
         "190万円・駐車場あり・水道公営・下水浄化槽（汲み取りでないため除外対象外の可能性あり）。利回り・間取り詳細は要確認。",
         "https://www.kenbiya.com/pp8/s/chiba/mobara-shi/re_43697371kk/"),
    ]
    for row_data in interrupted:
        data_row(r, list(row_data[:-1]) + [""], lightorange, row_data[-1])
        r += 1

    # 除外確定
    r += 1
    section_row(r, "【除外確定】絶対除外条件に該当", red_fill)
    r += 1

    excluded_list = [
        ("❌", "東金市",          "—", "398万", "—","—","—","—","—","—","—","—","OC・下水浄化槽",  "—", "OC＋下水浄化槽のため除外"),
        ("❌", "大網白里市",      "—", "不明",  "—","—","—","—","—","—","—","—","満室OC",          "—", "満室（OC）のため除外"),
        ("❌", "八街市",          "—", "650万", "—","—","—","—","—","—","—","—","OC・予算超過",    "—", "OC＋予算400万超のため除外"),
        ("❌", "八街市",          "—", "180万", "—","—","—","—","—","—","—","—","再建築不可",      "—", "再建築不可のため絶対除外"),
        ("❌", "茂原市",          "—", "360万", "—","—","—","—","—","—","—","—","賃貸中OC",        "—", "賃貸中（OC）のため除外"),
        ("❌", "横芝光町ほか町村","—", "各種",  "—","—","—","—","—","—","—","—","町のため対象外",  "—", "「市のみ対象」条件に不該当"),
    ]
    for row_data in excluded_list:
        for col, val in enumerate(row_data, 1):
            c = ws.cell(row=r, column=col, value=val)
            c.fill = lightred
            c.font = Font(size=10)
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            c.border = border
        ws.row_dimensions[r].height = 25
        r += 1

    # 列幅
    col_widths = [5, 22, 20, 10, 11, 11, 10, 10, 17, 8, 10, 16, 14, 10, 50]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # シート2
    ws2 = wb.create_sheet("調査メモ・凡例")
    notes = [
        ("■ 調査情報", ""),
        ("調査日",       "2026年4月25日"),
        ("調査サイト",   "健美家・楽待・HOME'S投資（各サイト403のためGoogle検索キャッシュ経由）"),
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
        ("緑（薄）",     "★最注目候補（物件3：S造・利回り19%・条件良好）"),
        ("青（薄）",     "候補物件"),
        ("黄（薄）",     "OC確認など保留中の物件"),
        ("グレー",       "詳細不明・要問合せ"),
        ("橙（薄）",     "調査中断・手動確認が必要"),
        ("赤（薄）",     "除外確定"),
        ("", ""),
        ("■ 次のアクション（優先順）", ""),
        ("優先①", "物件3（大網白里市 398万 S造 18.99%）→ 健美家で詳細確認・問合せ"),
        ("優先②", "旭市 180万・30%（調査中断A）→ 健美家の旭市ページを直接確認"),
        ("優先③", "物件5（山武市 350万）→ OC非該当を確認後に問合せ"),
        ("全物件共通", "水道（公営か）・下水（汲み取りでないか）・再建築可否・駐車場有無を必ず問合せで確認"),
    ]
    for i, (k, v) in enumerate(notes, 1):
        ck = ws2.cell(row=i, column=1, value=k)
        cv = ws2.cell(row=i, column=2, value=v)
        if k.startswith("■"):
            ck.fill = blue_fill
            cv.fill = blue_fill
            ck.font = Font(bold=True, color="FFFFFF", size=10)
            cv.font = Font(color="FFFFFF", size=10)
        elif k.startswith("優先") or k == "全物件共通":
            ck.font = Font(bold=True, size=10)
            cv.font = Font(size=10)
        else:
            ck.font = Font(size=10)
            cv.font = Font(size=10)
        cv.alignment = Alignment(wrap_text=True)
    ws2.column_dimensions["A"].width = 20
    ws2.column_dimensions["B"].width = 75

    wb.save(path)
    print(f"Excel保存: {path}")


def main():
    desktop = Path.home() / "Desktop" / "千葉県築古戸建リサーチ結果_20260425.xlsx"
    build_excel(desktop)

    print("Googleスプレッドシートへアップロード中...")
    url = upload_to_sheets(str(desktop))
    print(f"アップロード完了: {url}")

    open_url(url)
    print("ブラウザで開きました。")


if __name__ == "__main__":
    main()
