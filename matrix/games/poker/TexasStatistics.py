
from matrix.games.poker.Cards import Cards
from matrix.games.poker.TexasRules import TexasRules


class TexasStatistics():
    def __init__(self):
        self.cards = Cards()

    def get_property_by_hand(self):
        pass

    def input_two_cards(self):
        user_input = input("请输入内容：")
        user_input = user_input.lower()
        card1 = None
        card2 = None
        if len(user_input) == 2:
            if user_input[0] == user_input[1] :
                pass
                
