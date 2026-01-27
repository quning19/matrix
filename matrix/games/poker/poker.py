import itertools
import time

# 常量定义（整数编码优化）
RANKS = '23456789TJQKA'
SUITS = 'shdc'
RANK_CODE = {r: i for i, r in enumerate(RANKS)}  # 点数编码（0-12）
SUIT_CODE = {s: i for i, s in enumerate(SUITS)}  # 花色编码（0-3）

# 牌型强度
HAND_STRENGTH = {
    '同花顺': 9, '四条': 8, '葫芦': 7,
    '同花': 6, '顺子': 5, '三条': 4, '两对': 3,
    '一对': 2, '高牌': 1
}

# 预计算所有顺子的位掩码
STRAIGHT_MASKS = set()
for i in range(9):  # 2-6到10-A的常规顺子
    mask = 0
    for j in range(i, i+5):
        mask |= 1 << j
    STRAIGHT_MASKS.add(mask)
STRAIGHT_MASKS.add(0b1000000000001 | 0b1110)  # A-2-3-4-5

def create_deck():
    """创建编码后的牌组"""
    return [(RANK_CODE[r], SUIT_CODE[s]) for r in RANKS for s in SUITS]

def has_straight_in_cards(cards):
    """检查一组牌中是否存在顺子"""
    if len(cards) < 5:
        return False

    unique_ranks = {r for r, s in cards}
    rank_mask = 0
    for r in unique_ranks:
        rank_mask |= 1 << r
    return rank_mask in STRAIGHT_MASKS

def get_best_hand_from_7cards(seven_cards):
    """从7张牌中判断最佳牌型（修正葫芦判断）"""
    ranks = [c[0] for c in seven_cards]
    suits = [c[1] for c in seven_cards]
    
    # 1. 统计点数频次（数组优化）
    rank_counts = [0] * 13
    for r in ranks:
        rank_counts[r] += 1
    # 按频次降序排列（只保留>0的频次）
    count_sorted = sorted((cnt for cnt in rank_counts if cnt > 0), reverse=True)
    if not count_sorted:
        return '高牌'
    
    # 2. 检查同花并提取同花色牌
    suit_groups = {}
    for card in seven_cards:
        s = card[1]
        suit_groups.setdefault(s, []).append(card)
    has_flush = False
    flush_cards = []
    for s, cards in suit_groups.items():
        if len(cards) >= 5:
            has_flush = True
            flush_cards = cards
            break
    
    # 3. 检查全局顺子（非同花的顺子）
    all_unique_ranks = {r for r in ranks}
    all_rank_mask = 0
    for r in all_unique_ranks:
        all_rank_mask |= 1 << r
    has_global_straight = all_rank_mask in STRAIGHT_MASKS
    
    # 4. 检查同花顺（同花牌中必须有顺子）
    has_straight_flush = has_flush and has_straight_in_cards(flush_cards)
    
    # 5. 牌型判断（核心修正：葫芦的判断）
    if has_straight_flush:
        print(flush_cards)
        return '同花顺'
    if count_sorted[0] == 4:
        return '四条'
    # 葫芦修正：只要最高频次是3，且次高频次≥2（包括3，如3+3的情况）
    if count_sorted[0] == 3 and len(count_sorted) >= 2 and count_sorted[1] >= 2:
        return '葫芦'
    if has_flush:
        return '同花'
    if has_global_straight:
        return '顺子'
    if count_sorted[0] == 3:
        return '三条'
    if len(count_sorted) >= 2 and count_sorted[0] == 2 and count_sorted[1] == 2:
        return '两对'
    if count_sorted[0] == 2:
        return '一对'
    return '高牌'

def calculate_aa_odds():
    start_time = time.time()
    hole_cards = [(12, SUIT_CODE['h']), (12, SUIT_CODE['s'])]  # AA底牌
    deck = create_deck()
    
    # 移除底牌
    for card in hole_cards:
        deck.remove(card)
    
    hand_counts = {hand: 0 for hand in HAND_STRENGTH.keys()}
    total = 0
    total_combinations = 2118760
    
    print(f"开始计算（共{total_combinations:,}种组合）")
    
    # 遍历所有公共牌组合
    for community in itertools.combinations(deck, 5):
        seven_cards = hole_cards + list(community)
        best_hand = get_best_hand_from_7cards(seven_cards)
        hand_counts[best_hand] += 1
        total += 1
        
        if total % 500000 == 0:
            elapsed = time.time() - start_time
            print(f"已计算{total:,}/{total_combinations:,} | 耗时{elapsed:.1f}s")
    
    probabilities = {h: (c / total) * 100 for h, c in hand_counts.items()}
    elapsed_total = time.time() - start_time
    print(f"计算完成！总耗时：{elapsed_total:.1f}秒")
    
    return probabilities, hole_cards, elapsed_total

def print_results(probabilities, hole_cards, elapsed):
    print("\n" + "="*50)
    print(f"底牌：AA（红桃A + 黑桃A）")
    print(f"计算耗时：{elapsed:.2f}秒 | 计算精度：100%")
    print("="*50)
    print(f"{'牌型':<8} {'概率':<10} {'出现次数':<10}")
    print("-"*50)
    
    for hand in sorted(HAND_STRENGTH.keys(), key=lambda x: HAND_STRENGTH[x], reverse=True):
        prob = probabilities[hand]
        count = int(prob * 2118760 / 100)
        print(f"{hand:<8} {prob:.4f}%      {count:,}")

def main():
    print("德州扑克AA底牌概率计算器（修正葫芦判断）")
    probabilities, hole_cards, elapsed = calculate_aa_odds()
    print_results(probabilities, hole_cards, elapsed)

if __name__ == "__main__":
    main()
