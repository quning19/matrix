import itertools
import random

class Card():
    def __init__(self, idx):
        self.idx = idx
        self.rank = Card.get_card_rank(idx)
        self.suit = Card.get_card_suit(idx)
        self.disp_rank = Card.get_card_disp_rank(idx)
        self.disp_suit = Card.get_card_disp_suit(idx)
   
    @staticmethod
    def get_card_rank(idx):
        return idx % 13

    @staticmethod
    def get_card_suit(idx):
        return idx // 13
    
    @staticmethod
    def get_card_disp_rank(idx):
        rank = Card.get_card_rank(idx)
        return ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'][rank]
    
    @staticmethod
    def get_card_disp_suit(idx):
        suit = Card.get_card_suit(idx)
        return ['S', 'H', 'C', 'D'][suit]
    
    def __str__(self):
        return self.disp_rank + self.disp_suit
    
    def __repr__(self):
        return self.__str__()

class Cards():
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = [Card(i) for i in range(0, 52)]

    def deal_random_card(self):
        return self.cards.pop(random.randint(0, len(self.cards) - 1))
    
    def get_cards_combinations(self, count):
        return itertools.combinations(self.cards, count)

        