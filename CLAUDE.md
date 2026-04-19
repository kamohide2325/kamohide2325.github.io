# せどりリサーチツール — プロジェクト概要

このリポジトリは、KeepaのAmazon販売上位リスト（CSV）を元に、楽天市場・Yahoo!ショッピングで仕入れてAmazonで転売できる商品を自動で探し出すPythonツールを含む。

---

## ディレクトリ構成

```
arbitrage/
├── config.py            # APIキー・利益計算パラメータ（GitIgnore済み）
├── keepa_parser.py      # KeepaのCSVを読み込む
├── price_fetcher.py     # 楽天・Yahoo APIで仕入れ価格を取得
├── profit_calculator.py # Amazon手数料を引いて純利益を計算
├── main.py              # 実行スクリプト（Excelをデスクトップに出力）
├── requirements.txt     # 依存ライブラリ
└── MANUAL.md            # 詳細な手順書
```

---

## ツールの実行方法

```bash
cd ~/kamohide2325.github.io/arbitrage
python3 main.py ~/Downloads/KeepaExport-YYYY-MM-DD.csv
```

出力: `~/Desktop/せどりリサーチ結果.xlsx`（実行のたびに上書き）

---

## Excelの仕様

### シート構成
- **全商品**: ✅利益あり＋⚠️微利益のみ（❌赤字・データなしは除外）
- **利益あり商品**: ✅利益あり（粗利1000円以上）のみ

### 列順（16列）
| 列 | 内容 |
|----|------|
| A | No.（1から連番） |
| B | 商品名 |
| C | 判定 |
| D | EAN |
| E | ASIN |
| F | Amazon現在価格 |
| G | 楽天最安値 |
| H | ヤフー最安値 |
| I | 最安仕入先 |
| J | 仕入最安値 |
| K | Amazon手数料 |
| L | FBA配送料 |
| M | 粗利(楽天仕入) |
| N | 粗利(ヤフー仕入) |
| O | 楽天最安値ページURL（クリックでリンク） |
| P | ヤフー最安値ページURL（クリックでリンク） |

### 判定と行の色
| 判定 | 色 | 条件 |
|------|----|------|
| ✅ 利益あり（粗利1000円以上） | 緑 | 粗利 ≥ 1000円 |
| ⚠️ 微利益 | 黄 | 0 < 粗利 < 1000円 |
| ❌ 赤字 | 赤 | 粗利 ≤ 0（出力から除外） |
| データなし | グレー | 仕入れ候補なし（出力から除外） |

### その他
- 1行目にオートフィルター設定済み
- URLはクリックで商品ページにリンク（青色下線）

---

## 仕入れフィルター仕様

楽天・Yahoo両方で以下を除外：
- タイトルに「中古」「未使用品」「ジャンク」「訳あり」「アウトレット」を含む商品
- 楽天の `auc-` 系ショップ（オークション）

---

## 利益計算式

```
純利益 = Amazon販売価格
       - 仕入れ価格（税込み＋送料）
       - Amazon参照手数料（カテゴリ別 8〜15%）
       - FBA配送手数料（デフォルト361円）
```

---

## APIキー設定（config.py）

```python
RAKUTEN_APP_ID = "..."   # 楽天Webサービス Application ID
YAHOO_CLIENT_ID = "..."  # Yahoo!ショッピング Client ID
KEEPA_API_KEY = "..."    # Keepa API（未使用・任意）
```

- `config.py` は `.gitignore` に登録済み（GitHubに公開されない）
- 楽天API取得先: https://webservice.rakuten.co.jp/
- Yahoo API取得先: https://e.developer.yahoo.co.jp/dashboard/

---

## 開発ブランチ

`claude/amazon-arbitrage-finder-ZlPpF`

新機能・修正はすべてこのブランチで開発し、push する。

---

## 環境セットアップ（初回のみ）

```bash
# リポジトリ取得
git clone https://github.com/kamohide2325/kamohide2325.github.io.git
cd kamohide2325.github.io
git checkout claude/amazon-arbitrage-finder-ZlPpF

# ライブラリインストール
cd arbitrage
pip3 install -r requirements.txt

# APIキー設定
open -e config.py
```
