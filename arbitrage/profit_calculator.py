"""
Amazon FBA利益計算モジュール
Amazon手数料構造を考慮して正確な利益を算出する
"""

from dataclasses import dataclass
import config


JUDGMENT_PROFITABLE = "✅ 利益あり（粗利1000円以上）"
JUDGMENT_MARGINAL   = "⚠️ 微利益"
JUDGMENT_LOSS       = "❌ 赤字"


@dataclass
class ProfitResult:
    amazon_price: int          # Amazon販売価格
    purchase_total: int        # 仕入れ合計（税込み+送料）
    referral_fee: int          # Amazonカテゴリ別参照手数料
    fba_fee: int               # FBA配送手数料
    total_cost: int            # 仕入れ + Amazon手数料
    profit: int                # 純利益
    profit_rate: float         # 利益率（%）
    is_profitable: bool        # 最低基準を満たすか
    judgment: str              # 判定ラベル


# カテゴリ別参照手数料率（2024年度基準）
# 正確な最新値はSellerCentralで必ず確認すること
CATEGORY_FEE_RATES = {
    "家電":          0.08,
    "パソコン":       0.08,
    "おもちゃ":       0.10,
    "ゲーム":         0.08,
    "食品":          0.08,
    "ヘルス":         0.08,
    "ビューティー":    0.08,
    "スポーツ":       0.10,
    "本":            0.15,
    "音楽":          0.15,
    "DVD":           0.15,
    "ホーム":         0.10,
    "ファッション":    0.10,
}


def get_referral_fee_rate(category: str) -> float:
    """カテゴリ名から参照手数料率を取得"""
    if not category:
        return config.AMAZON_REFERRAL_FEE_RATE
    for key, rate in CATEGORY_FEE_RATES.items():
        if key in category:
            return rate
    return config.AMAZON_REFERRAL_FEE_RATE


def calculate_profit(
    amazon_price: int,
    purchase_total: int,
    category: str = "",
    fba_fee: int = None,
) -> ProfitResult:
    """
    利益を計算する。

    amazon_price   : Amazon出品価格（円）
    purchase_total : 仕入れ価格 + 送料（円）
    category       : Amazonカテゴリ（手数料率の決定に使用）
    fba_fee        : FBA手数料（Noneの場合はデフォルト値を使用）
    """
    if fba_fee is None:
        fba_fee = config.DEFAULT_FBA_FEE

    fee_rate = get_referral_fee_rate(category)
    referral_fee = int(amazon_price * fee_rate)

    # Amazonは最低参照手数料30円を設定している
    referral_fee = max(referral_fee, 30)

    total_cost = purchase_total + referral_fee + fba_fee
    profit = amazon_price - total_cost
    profit_rate = (profit / amazon_price * 100) if amazon_price > 0 else 0.0

    if profit >= 1000:
        judgment = JUDGMENT_PROFITABLE
    elif profit > 0:
        judgment = JUDGMENT_MARGINAL
    else:
        judgment = JUDGMENT_LOSS

    is_profitable = (judgment == JUDGMENT_PROFITABLE)

    return ProfitResult(
        amazon_price=amazon_price,
        purchase_total=purchase_total,
        referral_fee=referral_fee,
        fba_fee=fba_fee,
        total_cost=total_cost,
        profit=profit,
        profit_rate=round(profit_rate, 1),
        is_profitable=is_profitable,
        judgment=judgment,
    )
