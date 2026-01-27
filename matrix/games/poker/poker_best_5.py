import itertools
import time

# 常量定义（整数编码优化）
RANKS = '23456789TJQKA'
SUITS = 'shdc'
RANK_CODE = {r: i for i, r in enumerate(RANKS)}  # 点数编码（0-12）
SUIT_CODE = {s: i for i, s in enumerate(SUITS)}  # 花色编码（0-3）
CODE_TO_RANK = {v: k for k, v in RANK_CODE.items()}  # 编码转点数
CODE_TO_SUIT = {v: k for k, v in SUIT_CODE.items()}  # 编码转花色

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

def encode_card(rank, suit):
    """将点数和花色转换为编码"""
    return (RANK_CODE[rank], SUIT_CODE[suit])

def decode_card(card):
    """将编码转换为点数和花色字符串（如(12,0)→'Ah'）"""
    return f"{CODE_TO_RANK[card[0]]}{CODE_TO_SUIT[card[1]].upper()}"

def get_straight_cards(cards):
    """从牌组中提取组成顺子的5张牌"""
    unique_ranks = sorted({r for r, s in cards}, key=lambda x: x)
    n = len(unique_ranks)
    
    # 检查常规顺子
    for i in range(n - 4):
        if unique_ranks[i+4] - unique_ranks[i] == 4:
            # 提取这5个点数的牌（各取1张）
            selected = []
            for r in unique_ranks[i:i+5]:
                # 优先选点数匹配的任意牌
                for card in cards:
                    if card[0] == r and card not in selected:
                        selected.append(card)
                        break
            return selected[:5]
    
    # 检查A-2-3-4-5特殊顺子
    if {0,1,2,3,12}.issubset(unique_ranks):  # 0=2,1=3,2=4,3=5,12=A
        target_ranks = [12,0,1,2,3]  # A,2,3,4,5
        selected = []
        for r in target_ranks:
            for card in cards:
                if card[0] == r and card not in selected:
                    selected.append(card)
                    break
        return selected[:5]
    return None

def get_best_hand_from_7cards(seven_cards):
    """从7张牌中判断最佳牌型，并返回最佳5张牌"""
    # 1. 按花色分组
    suit_groups = {}
    for card in seven_cards:
        s = card[1]
        suit_groups.setdefault(s, []).append(card)
    
    # 2. 统计点数频次（并记录对应牌）
    rank_card_map = {}  # {点数: [牌列表]}
    for card in seven_cards:
        r = card[0]
        rank_card_map.setdefault(r, []).append(card)
    # 按点数大小排序（用于选最大牌）
    sorted_ranks = sorted(rank_card_map.keys(), reverse=True)
    # 按频次排序（用于判断牌型）
    count_sorted = sorted([(len(cards), r) for r, cards in rank_card_map.items()], 
                         key=lambda x: (-x[0], -x[1]))  # 先按频次，再按点数
    
    # 3. 检查同花顺
    flush_suit = None
    flush_cards = []
    for s, cards in suit_groups.items():
        if len(cards) >= 5:
            flush_suit = s
            flush_cards = cards
            break
    if flush_cards:
        straight_flush_cards = get_straight_cards(flush_cards)
        if straight_flush_cards:
            return '同花顺', straight_flush_cards
    
    # 4. 检查四条
    if count_sorted[0][0] == 4:
        four_rank = count_sorted[0][1]
        four_cards = rank_card_map[four_rank][:4]  # 4张四条
        # 找第5张牌（最大的非四条牌）
        kicker = None
        for r in sorted_ranks:
            if r != four_rank:
                kicker = rank_card_map[r][0]
                break
        return '四条', four_cards + [kicker]
    
    # 5. 检查葫芦（3+2或3+3）
    if count_sorted[0][0] >= 3 and len(count_sorted) >= 2 and count_sorted[1][0] >= 2:
        three_rank = count_sorted[0][1]
        three_cards = rank_card_map[three_rank][:3]  # 3张三条
        # 找对子（优先选次高频次的点数）
        pair_rank = count_sorted[1][1]
        pair_cards = rank_card_map[pair_rank][:2]  # 2张对子
        return '葫芦', three_cards + pair_cards
    
    # 6. 检查同花
    if flush_cards:
        # 选同花中最大的5张牌
        sorted_flush = sorted(flush_cards, key=lambda x: (-x[0], -x[1]))
        return '同花', sorted_flush[:5]
    
    # 7. 检查顺子
    straight_cards = get_straight_cards(seven_cards)
    if straight_cards:
        return '顺子', straight_cards
    
    # 8. 检查三条
    if count_sorted[0][0] == 3:
        three_rank = count_sorted[0][1]
        three_cards = rank_card_map[three_rank][:3]
        # 找最大的2张非三条牌
        kickers = []
        for r in sorted_ranks:
            if r != three_rank and len(kickers) < 2:
                kickers.append(rank_card_map[r][0])
        return '三条', three_cards + kickers
    
    # 9. 检查两对
    if len(count_sorted) >= 2 and count_sorted[0][0] == 2 and count_sorted[1][0] == 2:
        pair1_rank = count_sorted[0][1]
        pair1_cards = rank_card_map[pair1_rank][:2]
        pair2_rank = count_sorted[1][1]
        pair2_cards = rank_card_map[pair2_rank][:2]
        # 找最大的非对牌
        kicker = None
        for r in sorted_ranks:
            if r != pair1_rank and r != pair2_rank:
                kicker = rank_card_map[r][0]
                break
        return '两对', pair1_cards + pair2_cards + [kicker]
    
    # 10. 检查一对
    if count_sorted[0][0] == 2:
        pair_rank = count_sorted[0][1]
        pair_cards = rank_card_map[pair_rank][:2]
        # 找最大的3张非对牌
        kickers = []
        for r in sorted_ranks:
            if r != pair_rank and len(kickers) < 3:
                kickers.append(rank_card_map[r][0])
        return '一对', pair_cards + kickers
    
    # 11. 高牌（选最大的5张）
    sorted_high = sorted(seven_cards, key=lambda x: (-x[0], -x[1]))
    return '高牌', sorted_high[:5]

def calculate_aa_odds():
    start_time = time.time()
    # 固定AA底牌（红桃A和黑桃A，编码后）
    hole_cards = [encode_card('A', 'h'), encode_card('A', 's')]
    deck = create_deck()
    
    # 移除底牌
    for card in hole_cards:
        deck.remove(card)
    
    hand_counts = {hand: 0 for hand in HAND_STRENGTH.keys()}
    total = 0
    total_combinations = 2118760
    
    # 为了演示，只计算前1000组（全量计算请注释此行）
    # deck = deck[:55]  # 减少牌组大小以加速演示
    
    print(f"开始计算（共{total_combinations:,}种组合）")
    
    # 遍历所有公共牌组合
    for community in itertools.combinations(deck, 5):
        seven_cards = hole_cards + list(community)
        best_hand, best_5cards = get_best_hand_from_7cards(seven_cards)
        hand_counts[best_hand] += 1
        total += 1
        
        # 每10万组打印一次示例
        if total % 100000 == 0:
            # 解码5张牌为可读格式
            decoded = [decode_card(c) for c in best_5cards]
            elapsed = time.time() - start_time
            print(f"已计算{total:,} | 示例: {best_hand} → {decoded} | 耗时{elapsed:.1f}s")
    
    probabilities = {h: (c / total) * 100 for h, c in hand_counts.items()}
    elapsed_total = time.time() - start_time
    print(f"计算完成！总耗时：{elapsed_total:.1f}秒")
    
    return probabilities, hole_cards, elapsed_total

def print_results(probabilities, hole_cards, elapsed):
    print("\n" + "="*50)
    print(f"底牌：{decode_card(hole_cards[0])} + {decode_card(hole_cards[1])}（一对A）")
    print(f"计算耗时：{elapsed:.2f}秒 | 计算精度：100%")
    print("="*50)
    print(f"{'牌型':<8} {'概率':<10}")
    print("-"*50)
    
    for hand in sorted(HAND_STRENGTH.keys(), key=lambda x: HAND_STRENGTH[x], reverse=True):
        print(f"{hand:<8} {probabilities[hand]:.4f}%")

def main():
    print("德州扑克AA底牌概率计算器（记录最佳5张牌）")
    probabilities, hole_cards, elapsed = calculate_aa_odds()
    print_results(probabilities, hole_cards, elapsed)

if __name__ == "__main__":
    main()
