
from collections import Counter
from matrix.games.poker.Cards import Card, Cards
from enum import Enum, IntEnum, auto


class TexasMatch(IntEnum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIRS = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8

    # 实现反向查找：通过值获取名称
    @staticmethod
    def get_type_name(value):
        # 遍历类的所有属性
        for name, val in TexasMatch.__dict__.items():
            # 过滤掉类的特殊属性（如__module__、__doc__等）
            if not name.startswith('__') and val == value:
                return name
        return None  # 未找到对应值时返回None

# TexasMatch = {
#     'HIGH_CARD' : 0,
#     'ONE_PAIR' : 1,
#     'TWO_PAIRS' : 2,
#     'THREE_OF_A_KIND' : 3,
#     'STRAIGHT' : 4,
#     'FLUSH' : 5,
#     'FULL_HOUSE' : 6,
#     'FOUR_OF_A_KIND' : 7,
#     'STRAIGHT_FLUSH' : 8
# }
    

class TexasRules():
    """ Texas Hold'em Poker Rules """

    def __init__(self):
        self.cards = Cards()
        self.init_rules()

    def init_rules(self):
        self.rules = {}
        self.rules[TexasMatch.HIGH_CARD] = self.check_high_card
        self.rules[TexasMatch.ONE_PAIR] = self.check_one_pair
        self.rules[TexasMatch.TWO_PAIRS] = self.check_two_pairs
        self.rules[TexasMatch.THREE_OF_A_KIND] = self.check_three_of_a_kind
        self.rules[TexasMatch.STRAIGHT] = self.check_straight
        self.rules[TexasMatch.FLUSH] = self.check_flush
        self.rules[TexasMatch.FULL_HOUSE] = self.check_full_house
        self.rules[TexasMatch.FOUR_OF_A_KIND] = self.check_four_of_a_kind
        self.rules[TexasMatch.STRAIGHT_FLUSH] = self.check_straight_flush

    def get_best_match(self, cards):
        self.calc_card_counts(cards)

        # 按照牌型强度从高到低的顺序检查
        for match_type in range(TexasMatch.STRAIGHT_FLUSH, TexasMatch.HIGH_CARD - 1, -1):  # 从 STRAIGHT_FLUSH 到 HIGH_CARD
            match, rank_idxs = self.rules[match_type](cards)
            if match:
                # print(match, rank_idxs)
                return match_type, rank_idxs
            
    def calc_card_counts(self, cards):
        pass
        # self.rank_counts = self._get_count_dict(cards, use_rank_idx = True)
        # self.suit_counts = self._get_count_dict(cards, use_rank_idx = False)

        # print(self.rank_counts)
        # print(self.suit_counts)

    def check_high_card(self, cards, len = 5):
        cards.sort(key=lambda card: card.rank_idx, reverse=True)
        return True, cards[0:len]
    
    def check_one_pair(self, cards):

        # counts = Counter(card.rank_idx for card in cards)
        counts = self._get_count_dict(cards, use_rank_idx = True)
        pairs = [k for k, v in counts.items() if v == 2]

        if len(pairs) == 0:
            return False, []
        
        pairs.sort(reverse=True)
        pair_cards, left = self.split_match_rank_idx(cards, pairs[0])
        _, left = self.check_high_card(left, 3)

        return True, pair_cards + left
    
    def check_two_pairs(self, cards):
        # counts = Counter(card.rank_idx for card in cards)
        counts = self._get_count_dict(cards, use_rank_idx = True)
        pairs = [k for k, v in counts.items() if v == 2]

        if len(pairs) < 2:
            return False, []
        
        pairs.sort(reverse=True)
        pair_cards_1, left = self.split_match_rank_idx(cards, pairs[0])
        pair_cards_2, left = self.split_match_rank_idx(left, pairs[1])
        _, left = self.check_high_card(left, 1)

        return True, pair_cards_1 + pair_cards_2 + left
    
    def check_three_of_a_kind(self, cards):
        # counts = Counter(card.rank_idx for card in cards)
        counts = self._get_count_dict(cards, use_rank_idx = True)
        trips = [k for k, v in counts.items() if v == 3]

        if len(trips) < 1:
            return False, []
        
        trips.sort(reverse=True)
        trip_cards, left = self.split_match_rank_idx(cards, trips[0])
        _, left = self.check_high_card(left, 2)

        return True, trip_cards + left
    
    def check_straight(self, cards):
        # counts = Counter(card.rank_idx for card in cards)
        counts = self._get_count_dict(cards, use_rank_idx = True)
        if 12 in counts:
            counts[-1] = counts[12]
        straight_top = None

        for i in range(12, 2, -1):
            if i in counts and i-1 in counts and i-2 in counts and i-3 in counts and i-4 in counts:
                straight_top = i
                break

        if straight_top == None:
            return False, []
        
        straights = []
        tmp_cards = cards.copy()
        for i in range(straight_top, straight_top - 5, -1):
            idx = i + 13 if i < 0 else i
            matches, tmp_cards = self.split_match_rank_idx(tmp_cards, idx)
            if (len(matches) == 0):
                print(cards)
                print(straight_top)
                print(i)
                print(idx)
                for i in range(12, 2, -1):
                    if i in counts and i-1 in counts and i-2 in counts and i-3 in counts and i-4 in counts:
                        print(i)
                        print(counts)
            straights.append(matches[0])

        return True, straights
    
    def check_flush(self, cards):
        # counts = Counter(card.suit_idx for card in cards)
        counts = self._get_count_dict(cards, use_rank_idx = False)
        flush = [k for k, v in counts.items() if v >= 5]
        if len(flush) < 1:
            return False, []
        flush.sort(reverse=True)
        flush_cards, left = self.split_match_suit_idx(cards, flush[0])

        return True, flush_cards[0:5]
    
    def check_full_house(self, cards):
        # counts = Counter(card.rank_idx for card in cards)
        counts = self._get_count_dict(cards, use_rank_idx = True)
        trips = [k for k, v in counts.items() if v == 3]

        if len(trips) < 1:
            return False, []
        
        trips.sort(reverse=True)
        trip_cards, left = self.split_match_rank_idx(cards, trips[0])

        # counts = Counter(card.rank_idx for card in left)
        counts = self._get_count_dict(left, use_rank_idx = True)
        pairs = [k for k, v in counts.items() if v >= 2]

        if len(pairs) == 0:
            return False, []
        
        pairs.sort(reverse=True)
        pair_cards, left = self.split_match_rank_idx(cards, pairs[0])

        return True, trip_cards + pair_cards
    
    def check_four_of_a_kind(self, cards):
        # counts = Counter(card.rank_idx for card in cards)
        counts = self._get_count_dict(cards, use_rank_idx = True)
        quads = [k for k, v in counts.items() if v == 4]

        if len(quads) < 1:
            return False, []
        
        quads.sort(reverse=True)
        quads_cards, left = self.split_match_rank_idx(cards, quads[0])
        _, left = self.check_high_card(left, 1)

        return True, quads_cards + left
    
    def check_straight_flush(self, cards):
        # counts = Counter(card.suit_idx for card in cards)
        counts = self._get_count_dict(cards, use_rank_idx = False)
        flush = [k for k, v in counts.items() if v >= 5]
        
        if len(flush) < 1:
            return False, []
        flush.sort(reverse=True)
        flush_cards, left = self.split_match_suit_idx(cards, flush[0])

        straight_flush, straight_flush_cards = self.check_straight(flush_cards)        

        if straight_flush:
            return True, straight_flush_cards
        else:
            return False, []
    
    def split_match_rank_idx(self, cards, rank_idx):
        matches = [card for card in cards if card.rank_idx == rank_idx]
        left = [card for card in cards if card.rank_idx != rank_idx]
        left.sort(key=lambda card: card.rank_idx, reverse=True)
        return matches, left
    
    def split_match_suit_idx(self, cards, suit_idx):
        matches = [card for card in cards if card.suit_idx == suit_idx]
        matches.sort(key=lambda card: card.rank_idx, reverse=True)
        left = [card for card in cards if card.suit_idx != suit_idx]
        left.sort(key=lambda card: card.rank_idx, reverse=True)
        return matches, left
    
    def _get_count_dict(self, cards, use_rank_idx = True):
        if use_rank_idx:
            counts = {}
            for card in cards:
                i = card.rank_idx
                counts[i] = counts[i] + 1 if i in counts else 1
        else:
            counts = {}
            for card in cards:
                i = card.suit_idx
                counts[i] = counts[i] + 1 if i in counts else 1
        return counts
    

if __name__ == '__main__':
    rules = TexasRules()
    rules.init_rules()
    cards = Cards()
    hand = []
    # high card
    hand.append(Card.from_idx(0))
    hand.append(Card.from_idx(2))
    hand.append(Card.from_idx(3))
    hand.append(Card.from_idx(4))
    hand.append(Card.from_idx(5))
    hand.append(Card.from_idx(6))
    hand.append(Card.from_idx(8))
    hand.append(Card.from_idx(12))

    print(hand)
    print(rules.get_best_match(hand))
