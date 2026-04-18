"""
設定ファイル - APIキーとパラメータ
"""

# === 楽天市場 API ===
# https://webservice.rakuten.co.jp/ で取得
RAKUTEN_APP_ID = "YOUR_RAKUTEN_APP_ID"

# === Yahoo!ショッピング API ===
# https://developer.yahoo.co.jp/webapi/shopping/ で取得
YAHOO_CLIENT_ID = "YOUR_YAHOO_CLIENT_ID"

# === Keepa API ===
# https://keepa.com/#!api で取得（有料プラン必須）
KEEPA_API_KEY = "YOUR_KEEPA_API_KEY"

# === 利益計算パラメータ ===
# Amazon FBA小口出品の参照手数料率（カテゴリ別）
# 正確な値はSellerCentralで確認すること
AMAZON_REFERRAL_FEE_RATE = 0.10   # 10% (デフォルト)

# FBA配送手数料（円）- 商品サイズによって異なる
FBA_SHIPPING_FEE = {
    "small":  268,   # 小型（250g以下）
    "medium": 361,   # 標準（1kg以下）
    "large":  534,   # 大型（5kg以下）
}
DEFAULT_FBA_FEE = FBA_SHIPPING_FEE["medium"]

# 仕入れ先から自宅・FBA倉庫への送料（円）
INBOUND_SHIPPING = 0  # 楽天・Yahooは送料無料商品も多い

# 最低利益率（%） - これ以上の商品のみ出力
MIN_PROFIT_RATE = 15.0

# 最低利益額（円） - これ以上の商品のみ出力
MIN_PROFIT_AMOUNT = 300

# APIリクエスト間隔（秒）- レート制限対策
REQUEST_INTERVAL = 0.5

# 1商品あたりの仕入れ候補最大件数
MAX_PURCHASE_CANDIDATES = 5
