# Amazon転売リサーチツール 手順書

Keepaの販売上位リスト（JAN/EAN付き）から、楽天市場・Yahoo!ショッピングで仕入れてAmazonで転売できる商品を自動で探し出すツールです。

---

## 全体フロー

```
Keepa → CSV出力 → 本ツール → 楽天/Yahoo API検索 → 利益計算 → Excelレポート
```

---

## ステップ1: APIキーの取得

### 1-1. 楽天市場 API
1. https://webservice.rakuten.co.jp/ にアクセス
2. 楽天会員でログイン → 「アプリID発行」
3. 取得した **Application ID** を `config.py` の `RAKUTEN_APP_ID` に設定

### 1-2. Yahoo!ショッピング API
1. https://developer.yahoo.co.jp/webapi/shopping/ にアクセス
2. Yahoo! JAPAN IDでログイン → アプリ登録
3. 取得した **Client ID（アプリケーションID）** を `config.py` の `YAHOO_CLIENT_ID` に設定

> **楽天・Yahooは無料で利用可能**。月間リクエスト上限あり（楽天: 50,000回/日）

### 1-3. Keepa API（任意）
- Amazon価格の詳細な履歴が必要な場合のみ
- https://keepa.com/#!api で取得（月額$19〜）

---

## ステップ2: Keepaからデータをエクスポート

1. Keepaにログイン → 「Product Finder」または「Category Viewer」
2. 対象カテゴリ・条件を設定（例: Sales Rank Top 1000, 月間購入数 > 50）
3. 右上の **「Export」→「CSV」** をクリック
4. ダウンロードしたCSVに **ASIN, Title, EAN/JAN, Price** が含まれていることを確認

> **重要**: JAN/EANコード列が含まれているエクスポート設定にすること

---

## ステップ3: 環境セットアップ

```bash
# Python 3.10以上が必要
python --version

# 依存ライブラリのインストール
pip install -r requirements.txt
```

---

## ステップ4: 設定ファイルの編集

`config.py` を開いて以下を設定：

```python
RAKUTEN_APP_ID = "YOUR_RAKUTEN_APP_ID"   # 楽天APIキー
YAHOO_CLIENT_ID = "YOUR_YAHOO_CLIENT_ID" # YahooAPIキー

MIN_PROFIT_RATE = 15.0    # 最低利益率（%）- 目安は10〜20%
MIN_PROFIT_AMOUNT = 300   # 最低利益額（円）- 目安は300〜500円
DEFAULT_FBA_FEE = 361     # FBA配送手数料（標準サイズ）
```

---

## ステップ5: ツールの実行

```bash
cd arbitrage
python main.py /path/to/keepa_export.csv
```

実行中の出力例：
```
Keepa CSVを読み込んでいます: keepa_export.csv
  1200 商品を読み込みました
  うちJANコードあり: 980 商品

[1/980] B08XYZ1234 / JAN:4901234567890
  Amazon価格: ¥3,980 | ロジクール ワイヤレスマウス...
  仕入れ最安: ¥2,480 (rakuten / 〇〇家電)
  利益: ¥898 (22.6%) ✓ 利益あり
...
=== 完了: 87 / 980 商品が利益あり ===

結果を保存しました: results_20260418_143022.xlsx
```

---

## ステップ6: 結果Excelの確認

出力ファイル `results_YYYYMMDD_HHMMSS.xlsx` には2シートあります：

| シート | 内容 |
|--------|------|
| **利益あり商品** | 利益率・利益額が基準を超えた商品（緑ハイライト） |
| **全商品** | 検索できたすべての商品（参考） |

### 各列の説明

| 列名 | 説明 |
|------|------|
| ASIN | AmazonのASIN |
| タイトル | 商品名 |
| JAN | バーコード番号 |
| Amazon価格 | 現在のAmazon最安値 |
| 仕入れ価格(合計) | 楽天/Yahoo最安値＋送料 |
| 参照手数料 | Amazonカテゴリ別手数料（8〜15%） |
| FBA手数料 | FBA配送・保管手数料 |
| **利益** | **純利益（円）** |
| **利益率(%)** | **利益÷Amazon販売価格** |
| 仕入れURL | 楽天/YahooショップのURL |
| Amazon URL | Amazon商品ページURL |

---

## 利益計算の仕組み

```
純利益 = Amazon販売価格
       - 仕入れ価格
       - 仕入れ送料
       - Amazon参照手数料（販売価格の8〜15%）
       - FBA配送手数料（約268〜534円）
```

---

## よくある注意事項

### JANコードのない商品
- KeepaにJANが登録されていない商品は検索対象外
- Amazon専売品（Amazon Basics等）は通常JANなし

### Amazon価格変動リスク
- Keepaエクスポート時の価格と実際の販売価格は異なる場合がある
- 出品前に必ずSellerCentralで最新価格を確認すること

### FBA手数料
- `config.py` の `DEFAULT_FBA_FEE` はデフォルト値
- 正確な手数料はSellerCentral「FBA料金シミュレーター」で確認すること
- URL: https://sellercentral.amazon.co.jp/hz/fba/profitabilitycalculator/index

### カート取得競争
- 他のFBA出品者が既にいる場合、カートを取れない可能性がある
- Keepaで競合出品者数も確認すること（FBA出品者が少ない商品を優先）

### 規制商品
- 酒類、医薬品、食品等は出品申請が必要な場合がある
- Amazon「出品制限商品」リストを必ず確認すること

---

## カスタマイズ

### 利益基準を変更
```python
# config.py
MIN_PROFIT_RATE = 20.0    # より厳しく（20%以上のみ）
MIN_PROFIT_AMOUNT = 500   # 最低500円利益
```

### 特定カテゴリの手数料率を修正
```python
# profit_calculator.py の CATEGORY_FEE_RATES
"おもちゃ": 0.10,  # 10%
```

### リクエスト速度の調整
```python
# config.py
REQUEST_INTERVAL = 1.0  # APIへの負荷を減らす場合
```

---

## トラブルシューティング

| エラー | 原因・対処 |
|--------|-----------|
| `[Rakuten ERROR]` | APIキーが間違っている or リクエスト上限超過 |
| `[Yahoo ERROR]` | Client IDが間違っている |
| JAN検索でヒットなし | 商品が楽天/Yahooに出品されていない |
| 利益商品が0件 | 利益基準が厳しすぎる→`MIN_PROFIT_RATE`を下げる |
| openpyxlエラー | `pip install openpyxl` を再実行 |
