
from collections import Counter
from matrix.games.poker.Cards import Card, Cards
from enum import Enum, auto


class TexasMatch(Enum):
    HIGH_CARD = auto()
    ONE_PAIR = auto()
    TWO_PAIRS = auto()
    THREE_OF_A_KIND = auto()
    STRAIGHT = auto()
    FLUSH = auto()
    FULL_HOUSE = auto()
    FOUR_OF_A_KIND = auto()
    STRAIGHT_FLUSH = auto()
    

class TexasRules():
    """ Texas Hold'em Poker Rules """

    def __init__(self):
        self.cards = Cards()

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
        # 按照牌型强度从高到低的顺序检查
        for match_type in reversed(list(TexasMatch)):  # 从 STRAIGHT_FLUSH 到 HIGH_CARD
            match, rank_idxs = self.rules[match_type](cards)
            if match:
                print(match, rank_idxs)
                return match_type, rank_idxs

    def check_high_card(self, cards, len = 5):
        cards.sort(key=lambda card: card.rank_idx, reverse=True)
        return True, cards[0:len]
    
    def check_one_pair(self, cards):

        counts = Counter([card.rank_idx for card in cards])
        pairs = [k for k, v in counts.items() if v == 2]

        if len(pairs) == 0:
            return False, []
        
        pairs.sort(reverse=True)
        pair_cards, left = self.split_match_rank_idx(cards, pairs[0])
        _, left = self.check_high_card(left, 3)

        return True, pair_cards + left
    
    def check_two_pairs(self, cards):
        counts = Counter([card.rank_idx for card in cards])
        pairs = [k for k, v in counts.items() if v == 2]

        if len(pairs) < 2:
            return False, []
        
        pairs.sort(reverse=True)
        pair_cards_1, left = self.split_match_rank_idx(cards, pairs[0])
        pair_cards_2, left = self.split_match_rank_idx(left, pairs[1])
        _, left = self.check_high_card(left, 1)

        return True, pair_cards_1 + pair_cards_2 + left
    
    def check_three_of_a_kind(self, cards):
        counts = Counter([card.rank_idx for card in cards])
        trips = [k for k, v in counts.items() if v == 3]

        if len(trips) < 1:
            return False, []
        
        trips.sort(reverse=True)
        trip_cards, left = self.split_match_rank_idx(cards, trips[0])
        _, left = self.check_high_card(left, 2)

        return True, trip_cards + left
    
    def check_straight(self, cards):
        counts = Counter([card.rank_idx for card in cards])
        counts[-1] = counts[12]
        straight_top = None

        for i in range(12, 0, -1):
            if counts[i] >= 1 and counts[i-1] >= 1 and counts[i-2] >= 1 and counts[i-3] >= 1 and counts[i-4] >= 1:
                straight_top = i
                break

        if straight_top == None:
            return False, []
        
        straights = []
        for i in range(straight_top, straight_top - 5, -1):
            i = i + 13 if i < 0 else i
            matches, cards = self.split_match_rank_idx(cards, i)
            straights.append(matches[0])

        return True, straights
    
    def check_flush(self, cards):
        counts = Counter([card.suit_idx for card in cards])
        flush = [k for k, v in counts.items() if v >= 5]
        if len(flush) < 1:
            return False, []
        flush.sort(reverse=True)
        flush_cards, left = self.split_match_suit_idx(cards, flush[0])

        return True, flush_cards[0:5]
    
    def check_full_house(self, cards):
        counts = Counter([card.rank_idx for card in cards])
        trips = [k for k, v in counts.items() if v == 3]

        if len(trips) < 1:
            return False, []
        
        trips.sort(reverse=True)
        trip_cards, left = self.split_match_rank_idx(cards, trips[0])

        counts = Counter([card.rank_idx for card in left])
        pairs = [k for k, v in counts.items() if v >= 2]

        if len(pairs) == 0:
            return False, []
        
        pairs.sort(reverse=True)
        pair_cards, left = self.split_match_rank_idx(cards, pairs[0])

        return True, trip_cards + pair_cards
    
    def check_four_of_a_kind(self, cards):
        counts = Counter([card.rank_idx for card in cards])
        quads = [k for k, v in counts.items() if v == 4]

        if len(quads) < 1:
            return False, []
        
        quads.sort(reverse=True)
        quads_cards, left = self.split_match_rank_idx(cards, quads[0])
        _, left = self.check_high_card(left, 1)

        return True, quads_cards + left
    
    def check_straight_flush(self, cards):
        counts = Counter([card.suit_idx for card in cards])
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
