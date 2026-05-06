#!/bin/bash
cd "$(dirname "$0")"
python3 - <<'EOF'
import urllib.request, urllib.parse, json, os, time

APP_ID = "9b07f603-1b86-48ad-ab6b-d08005640ac6"
KEY    = "pk_GYZOQiIkgr4viwkEy43XE78LIPlm2dhw0bZ23VSePE7"

all_items = []

for page in range(1, 20):
    url = (
        "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"
        f"?format=json&keyword=%E3%82%AD%E3%83%A3%E3%83%B3%E3%83%97"
        f"&genreId=0&shopCode=himaraya&page={page}"
        f"&applicationId={APP_ID}&accessKey={KEY}"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read())
        items = data.get("Items", [])
        if not items:
            print("データなし。終了。")
            break
        for item in items:
            i = item["Item"]
            all_items.append({
                "name":      i["itemName"],
                "price":     i["itemPrice"],
                "code":      i["itemCode"],
                "pointRate": i.get("pointRate", 1)
            })
        print(f"{page}ページ完了（計 {len(all_items)} 件）")
        time.sleep(0.4)
    except Exception as e:
        print(f"エラー (page {page}): {e}")
        break

out_path = os.path.join(os.path.expanduser("~"), "Desktop", "rakuten_himaraya.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

print(f"\n完了！ {len(all_items)} 件をデスクトップに保存しました。")
print("ファイル名: rakuten_himaraya.json")
print("\nこのウィンドウは閉じないでください。")
print("デスクトップの rakuten_himaraya.json をテキストエディタで開き、")
print("中身を全選択してClaudeに貼り付けてください。")
EOF
echo ""
echo "Enterキーで閉じる"
read
