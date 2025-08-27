
import itertools
from loguru import logger
from colorama import Fore, Style, init
from matrix.games.poker.Cards import Card, Cards
from matrix.games.poker.TexasRules import TexasMatch, TexasRules


class TexasStatistics():
    def __init__(self):
        self.cards = Cards()
        self.rules = TexasRules()

    def calc_property_by_hand(self):
        self.init_property_dict()

        hand_cards = self.input_hand_cards()

        full_cards = Cards()
        full_cards.deal_card(hand_cards[0].rank_char, hand_cards[0].suit_char)
        full_cards.deal_card(hand_cards[1].rank_char, hand_cards[1].suit_char)

        for combo in itertools.combinations(full_cards.cards, 5):
            match_type, rank_idxs = self.rules.get_best_match(list(combo) + hand_cards)
            self.add_property(match_type)
            # self.add_property(TexasMatch.FULL_HOUSE)

        self.print_property()

    def print_property(self):
        total = sum(self.property_dict.values())
        for key in self.property_dict:
            logger.info(f'{key}: {self.property_dict[key] / total:.2%}')

    def add_property(self, match):
        self.property_dict[match] += 1

    def init_property_dict(self):
        self.property_dict = {}
        for match in TexasMatch:  # 假设存在此方法
            self.property_dict[match] = 0


    def input_hand_cards(self):

        while True:
            user_input = input(Fore.GREEN + "请输入手牌：")
            user_input = user_input.strip()
            user_input = user_input.upper()

            if len(user_input) == 2:
                if user_input[0] == user_input[1] :
                    return [Card(user_input[0],'S'), Card(user_input[0],'H')]
                else:
                    logger.error("请输入正确的牌:")
                    continue
            if len(user_input) == 3:
                last_char = user_input[2]
                if last_char == 'S':
                    return [Card(user_input[0],'S'), Card(user_input[1],'S')]
                elif last_char == 'O':
                    return [Card(user_input[0],'S'), Card(user_input[1],'H')]
                else:
                    logger.error("请输入正确的牌:")
                    continue

            if len(user_input) >= 4:
                return [Card(user_input[0],user_input[1]), Card(user_input[-2],user_input[-1])]
            

if __name__ == '__main__':
    ts = TexasStatistics()
    import cProfile
    import pstats
    profiler = cProfile.Profile()
    profiler.enable()  # 开始记录

    cards = ts.calc_property_by_hand()

    profiler.disable()  # 停止记录

    # 分析结果（按总耗时排序，显示前10行）
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(20) 
    stats.sort_stats('tottime').print_stats(20) 