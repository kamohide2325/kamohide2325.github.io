# せどりリサーチツール — プロジェクト概要

このリポジトリは、KeepaのAmazon販売上位リスト（CSV）を元に、楽天市場・Yahoo!ショッピングで仕入れてAmazonで転売できる商品を自動で探し出すPythonツールを含む。

---

## ディレクトリ構成

```
arbitrage/
├── config.py             # APIキー・利益計算パラメータ（GitIgnore済み）
├── credentials.json      # Google OAuth認証情報（GitIgnore済み）
├── token.json            # Google認証トークン（自動生成・GitIgnore済み）
├── keepa_parser.py       # KeepaのCSVを読み込む
├── price_fetcher.py      # 楽天スクレイピング・Yahoo APIで仕入れ価格を取得
├── profit_calculator.py  # Amazon手数料を引いて純利益を計算
├── google_uploader.py    # GoogleスプレッドシートへExcelをアップロード
├── main.py               # 実行スクリプト（Excel保存→Googleシート自動アップロード）
├── requirements.txt      # 依存ライブラリ
└── test_rakuten.py       # 楽天スクレイピング動作確認用
```

---

## 通常の使用手順（毎回）

```bash
cd ~/kamohide2325.github.io && git pull origin claude/amazon-arbitrage-finder-ZlPpF
cd arbitrage && python3 main.py 0421
```

- `0421` の部分だけ実行する日付に変える（例: 5月3日 → `0503`）
- `~/Downloads/KeepaExport-2026-04-21.csv` を自動で参照する
- デスクトップに `せどりリサーチ結果_20260421.xlsx` が保存され、Googleスプレッドシートがブラウザで自動的に開く

---

## Googleスプレッドシート自動アップロード

### 初回のみ：ブラウザでGoogle認証が必要
1. ツール実行後、ブラウザが自動で開く
2. `kamohide2325@gmail.com` でログイン
3. 「このアプリはGoogleで確認されていません」→「**続行**」をクリック
4. 「許可」をクリック
5. 以降は `token.json` が保存されるため認証不要

### token.jsonを削除した場合（再認証が必要なとき）
```bash
rm -f ~/kamohide2325.github.io/arbitrage/token.json
python3 main.py 0421
```

### Google Cloud設定（初回セットアップ済み）
- プロジェクト: `sedori-list`
- 有効API: Google Drive API
- OAuthクライアント: デスクトップアプリ（`credentials.json`）
- テストユーザー: `kamohide2325@gmail.com`

---

## Excelの仕様

### シート構成
- **全商品**: ✅利益あり＋⚠️微利益のみ（❌赤字・データなしは除外）
- **利益あり商品**: ✅利益あり（粗利1000円以上）のみ

### 列順（17列）
| 列 | 内容 |
|----|------|
| A | 判定 |
| B | No.（1から連番） |
| C | 商品名 |
| D | Amazon現在価格 |
| E | 楽天最安値 |
| F | ヤフー最安値 |
| G | ショップ名 |
| H | ASIN |
| I | EAN |
| J | 最安仕入先 |
| K | 仕入最安値 |
| L | Amazon手数料 |
| M | FBA配送料 |
| N | 粗利(楽天仕入) |
| O | 粗利(ヤフー仕入) |
| P | 楽天最安値ページURL（クリックでリンク） |
| Q | ヤフー最安値ページURL（クリックでリンク） |

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
- 最安仕入値がAmazon価格の50%以下の商品（Amazon複数個販売の可能性）

楽天の検索はJANコードのみ（商品名での検索は行わない）。

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

## 環境セットアップ（新しいMacで最初から始める場合）

```bash
# リポジトリ取得
git clone https://github.com/kamohide2325/kamohide2325.github.io.git
cd kamohide2325.github.io
git checkout claude/amazon-arbitrage-finder-ZlPpF

# ライブラリインストール
cd arbitrage
pip3 install -r requirements.txt

# APIキー設定（config.pyを編集）
open -e config.py

# Google認証情報を配置
# Google Cloud Console（sedori-listプロジェクト）から
# credentials.jsonをダウンロードして arbitrage/ フォルダに置く
```
