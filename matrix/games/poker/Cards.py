import itertools
import random

class Card():
    def __init__(self, rank, suit):
        self.rank_idx = Card.get_rank_idx_by_char(rank)
        self.suit_idx = Card.get_suit_idx_by_char(suit)
        self.rank_char = rank
        self.suit_char = suit

    @classmethod
    def from_idx(cls, idx):
        return cls(Card.get_card_rank_char(idx), Card.get_card_suit_char(idx))
   
    @staticmethod
    def get_card_rank_idx(idx):
        return idx % 13

    @staticmethod
    def get_card_suit_idx(idx):
        return idx // 13
    
    @staticmethod
    def get_card_rank_char(idx):
        rank = Card.get_card_rank_idx(idx)
        return ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'][rank]
    
    @staticmethod
    def get_card_suit_char(idx):
        suit = Card.get_card_suit_idx(idx)
        return ['S', 'H', 'C', 'D'][suit]
    @staticmethod
    def get_rank_idx_by_char(char):
        return ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'].index(char)    
    @staticmethod
    def get_suit_idx_by_char(char):
        return ['S', 'H', 'C', 'D'].index(char)
    

    def __str__(self):
        return self.rank_char + self.suit_char
    
    def __repr__(self):
        return self.__str__()

class Cards():
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = [Card.from_idx(i) for i in range(0, 52)]

    def deal_random_card(self):
        return self.cards.pop(random.randint(0, len(self.cards) - 1))
    
    def get_cards_combinations(self, count):
        return itertools.combinations(self.cards, count)

        