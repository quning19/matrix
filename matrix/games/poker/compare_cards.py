import itertools
import time
from collections import defaultdict

# 常量定义
RANKS = '23456789TJQKA'
SUITS = 'shdc'
RANK_CODE = {r: i for i, r in enumerate(RANKS)}  # 0=2, 1=3, ..., 12=A
SUIT_CODE = {s: i for i, s in enumerate(SUITS)}
CODE_TO_RANK = {v: k for k, v in RANK_CODE.items()}
CODE_TO_SUIT = {v: k for k, v in SUIT_CODE.items()}

# 牌型强度
HAND_STRENGTH = {
    '高牌': 1, '一对': 2, '两对': 3, '三条': 4,
    '顺子': 5, '同花': 6, '葫芦': 7, '四条': 8, '同花顺': 9
}

def encode_hand(hand):
    """将手牌字符串转换为编码格式"""
    encoded = []
    for card in hand:
        rank = card[:-1]
        suit = card[-1].lower()
        encoded.append((RANK_CODE[rank], SUIT_CODE[suit]))
    return encoded

def decode_card(card):
    """将编码牌转换为字符串"""
    return f"{CODE_TO_RANK[card[0]]}{CODE_TO_SUIT[card[1]].upper()}"

def has_straight_flush(suit_cards):
    """检查一组同花色牌中是否存在同花顺"""
    if len(suit_cards) < 5:
        return (False, [])
    
    unique_ranks = sorted({r for r, _ in suit_cards})
    rank_set = set(unique_ranks)
    
    # 检查常规顺子
    for i in range(len(unique_ranks) - 4):
        start = unique_ranks[i]
        if unique_ranks[i+4] - unique_ranks[i] == 4:
            target_ranks = set(range(start, start+5))
            selected = []
            for r in target_ranks:
                for card in suit_cards:
                    if card[0] == r and card not in selected:
                        selected.append(card)
                        break
            if len(selected) == 5:
                return (True, selected)
    
    # 检查A-2-3-4-5特殊顺子
    if {0, 1, 2, 3, 12}.issubset(rank_set):
        target_ranks = [12, 0, 1, 2, 3]
        selected = []
        for r in target_ranks:
            for card in suit_cards:
                if card[0] == r and card not in selected:
                    selected.append(card)
                    break
        if len(selected) == 5:
            return (True, selected)
    
    return (False, [])

def get_best_hand(seven_cards):
    """从7张牌中获取最佳牌型及强度值"""
    # 1. 检查同花顺
    suit_groups = defaultdict(list)
    for card in seven_cards:
        suit_groups[card[1]].append(card)
    
    for suit, cards in suit_groups.items():
        has_sf, sf_cards = has_straight_flush(cards)
        if has_sf:
            ranks = [r for r, _ in sf_cards]
            if set(ranks) == {0,1,2,3,12}:
                high_rank = 3  # A-2-3-4-5按5算
            else:
                high_rank = max(ranks)
            return ('同花顺', (high_rank,))
    
    # 2. 点数统计
    rank_counts = defaultdict(int)
    for r, _ in seven_cards:
        rank_counts[r] += 1
    sorted_ranks = sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0]))
    count_sorted = [cnt for _, cnt in sorted_ranks]
    if not count_sorted:
        return ('高牌', (0,))
    
    # 3. 四条
    if count_sorted[0] == 4:
        four_rank = sorted_ranks[0][0]
        kicker = sorted_ranks[1][0] if len(sorted_ranks) > 1 else 0
        return ('四条', (four_rank, kicker))
    
    # 4. 葫芦
    if count_sorted[0] >= 3 and len(count_sorted) >= 2 and count_sorted[1] >= 2:
        three_rank = sorted_ranks[0][0]
        pair_rank = sorted_ranks[1][0]
        return ('葫芦', (three_rank, pair_rank))
    
    # 5. 同花
    for suit, cards in suit_groups.items():
        if len(cards) >= 5:
            sorted_flush = sorted(cards, key=lambda x: (-x[0], -x[1]))[:5]
            flush_ranks = [r for r, _ in sorted_flush]
            return ('同花', tuple(flush_ranks))
    
    # 6. 顺子
    all_ranks = {r for r, _ in seven_cards}
    unique_ranks = sorted(all_ranks)
    has_straight = False
    straight_high = 0
    
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i+4] - unique_ranks[i] == 4:
            has_straight = True
            straight_high = unique_ranks[i+4]
            break
    
    if not has_straight and {0,1,2,3,12}.issubset(all_ranks):
        has_straight = True
        straight_high = 3
    
    if has_straight:
        return ('顺子', (straight_high,))
    
    # 7. 三条
    if count_sorted[0] == 3:
        three_rank = sorted_ranks[0][0]
        kickers = [r for r, _ in sorted_ranks[1:] if r != three_rank][:2]
        while len(kickers) < 2:
            kickers.append(0)
        return ('三条', (three_rank, kickers[0], kickers[1]))
    
    # 8. 两对
    if len(count_sorted) >= 2 and count_sorted[0] == 2 and count_sorted[1] == 2:
        pair1 = sorted_ranks[0][0]
        pair2 = sorted_ranks[1][0]
        if pair1 < pair2:
            pair1, pair2 = pair2, pair1
        kicker = sorted_ranks[2][0] if len(sorted_ranks) > 2 else 0
        return ('两对', (pair1, pair2, kicker))
    
    # 9. 一对
    if count_sorted[0] == 2:
        pair_rank = sorted_ranks[0][0]
        kickers = [r for r, _ in sorted_ranks[1:] if r != pair_rank][:3]
        while len(kickers) < 3:
            kickers.append(0)
        return ('一对', (pair_rank, kickers[0], kickers[1], kickers[2]))
    
    # 10. 高牌
    high_ranks = sorted([r for r, _ in seven_cards], reverse=True)[:5]
    return ('高牌', tuple(high_ranks))

def compare_hands(hand1, hand2):
    """比较两组最佳牌型"""
    type1, strength1 = hand1
    type2, strength2 = hand2
    
    if HAND_STRENGTH[type1] > HAND_STRENGTH[type2]:
        return 1
    elif HAND_STRENGTH[type1] < HAND_STRENGTH[type2]:
        return -1
    else:
        for s1, s2 in zip(strength1, strength2):
            if s1 > s2:
                return 1
            elif s1 < s2:
                return -1
        return 0

def exact_calculate_odds(hand1, hand2):
    """精确计算两组手牌的胜率（遍历所有可能的公共牌组合）"""
    start_time = time.time()
    
    # 编码手牌
    h1_encoded = encode_hand(hand1)
    h2_encoded = encode_hand(hand2)
    
    # 检查手牌是否有重复
    all_cards = set(h1_encoded + h2_encoded)
    if len(all_cards) != 4:
        raise ValueError("两组手牌不能有重复牌")
    
    # 创建剩余牌组（52-4=48张）
    full_deck = [(r, s) for r in RANK_CODE.values() for s in SUIT_CODE.values()]
    remaining_deck = [c for c in full_deck if c not in all_cards]
    total_combinations = len(list(itertools.combinations(remaining_deck, 5)))  # C(48,5) = 1,712,304
    
    # 初始化统计
    stats = defaultdict(int)
    total = 0
    
    print(f"开始精确计算：{hand1} vs {hand2}（共{total_combinations:,}种组合）")
    
    # 遍历所有可能的公共牌组合（核心：全量计算）
    for community in itertools.combinations(remaining_deck, 5):
        # 计算两组的最佳牌型
        h1_seven = h1_encoded + list(community)
        h2_seven = h2_encoded + list(community)
        h1_best = get_best_hand(h1_seven)
        h2_best = get_best_hand(h2_seven)
        
        # 比较结果
        result = compare_hands(h1_best, h2_best)
        if result == 1:
            stats['hand1_win'] += 1
        elif result == -1:
            stats['hand2_win'] += 1
        else:
            stats['tie'] += 1
        
        total += 1
        
        # 进度提示（每10万组更新一次）
        if total % 100000 == 0:
            elapsed = time.time() - start_time
            progress = (total / total_combinations) * 100
            print(f"进度：{progress:.1f}% | 已计算{total:,}/{total_combinations:,} | 耗时{elapsed:.1f}s")
    
    # 计算精确胜率
    h1_odds = (stats['hand1_win'] / total) * 100
    h2_odds = (stats['hand2_win'] / total) * 100
    tie_odds = (stats['tie'] / total) * 100
    
    elapsed_total = time.time() - start_time
    return {
        'hand1': hand1,
        'hand2': hand2,
        'hand1_win_rate': h1_odds,
        'hand2_win_rate': h2_odds,
        'tie_rate': tie_odds,
        'total_combinations': total_combinations,
        'time_elapsed': elapsed_total
    }

def print_results(results):
    """打印精确计算结果"""
    print("\n" + "="*60)
    print(f"手牌对比：{results['hand1']} vs {results['hand2']}")
    print(f"总组合数：{results['total_combinations']:,} | 计算时间：{results['time_elapsed']:.2f}秒")
    print("="*60)
    print(f"{results['hand1']} 胜率：{results['hand1_win_rate']:.6f}%")  # 更高精度
    print(f"{results['hand2']} 胜率：{results['hand2_win_rate']:.6f}%")
    print(f"平局概率：{results['tie_rate']:.6f}%")
    print("="*60)
    
    if results['hand1_win_rate'] > results['hand2_win_rate']:
        print(f"结论：{results['hand1']} 胜率更高")
    elif results['hand1_win_rate'] < results['hand2_win_rate']:
        print(f"结论：{results['hand2']} 胜率更高")
    else:
        print("结论：两组手牌胜率相同（理论上极罕见）")

def main():
    print("德州扑克手牌胜率精确计算器")
    print("="*50)
    
    # 示例：精确比较一对A和一对K
    hand1 = ['Ah', 'As']  # 一对A
    hand2 = ['Kd', 'Kh']  # 一对K
    
    # 执行精确计算（约170万种组合，耗时5-10分钟，取决于CPU）
    results = exact_calculate_odds(hand1, hand2)
    print_results(results)

if __name__ == "__main__":
    main()
