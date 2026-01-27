
import itertools
import math
import sys
import time
from loguru import logger
from colorama import Fore, Style, init
from matrix.games.poker.Cards import Card, Cards
from matrix.games.poker.TexasRules import TexasMatch, TexasRules


class TexasStatistics():
    def __init__(self):
        self.cards = Cards()
        self.rules = TexasRules()

        logger.remove()  # 移除默认的日志处理器
        logger.add(
            sys.stdout,
            format="<green>{time:MM-DD HH:mm:ss.SSS}</green> | <level>{level: ^8}</level> | <level>{message}</level>",
            level="DEBUG",  # 最低输出级别
            colorize=True   # 启用彩色输出
        )

    def calc_property_by_hand(self, hand_cards):
        self.init_property_dict()

        logger.info(hand_cards)

        full_cards = Cards()
        full_cards.deal_card(hand_cards[0].rank_char, hand_cards[0].suit_char)
        full_cards.deal_card(hand_cards[1].rank_char, hand_cards[1].suit_char)

        start_time = time.time()  # 记录开始时间
        total = 0
        total_combinations = math.comb(50, 5)  # 固定总组合数（C(50,5)）

        for combo in itertools.combinations(full_cards.cards, 5):
            match_type, rank_idxs = self.rules.get_best_match(list(combo) + hand_cards)
            self.property_dict[match_type] += 1
            total += 1
            # 进度提示（每20万次更新一次，减少打印开销）
            if total % 200000 == 0:
                elapsed = time.time() - start_time
                remaining = elapsed * (total_combinations - total) / total
                print(f"已计算{total:,}/{total_combinations:,} | 已耗时{elapsed:.1f}s | 预计剩余{remaining:.1f}s")


        self.print_property()

    def print_property(self):
        total = sum(self.property_dict.values())
        for key in self.property_dict:
            logger.info(f'{TexasMatch.get_type_name(key)}: {self.property_dict[key] / total:.4%}')

    def add_property(self, match):
        self.property_dict[match] += 1

    def init_property_dict(self):
        self.property_dict = {}

        self.property_dict[TexasMatch.HIGH_CARD] = 0
        self.property_dict[TexasMatch.ONE_PAIR] = 0
        self.property_dict[TexasMatch.TWO_PAIRS] = 0
        self.property_dict[TexasMatch.THREE_OF_A_KIND] = 0
        self.property_dict[TexasMatch.STRAIGHT] = 0
        self.property_dict[TexasMatch.FLUSH] = 0
        self.property_dict[TexasMatch.FULL_HOUSE] = 0
        self.property_dict[TexasMatch.FOUR_OF_A_KIND] = 0
        self.property_dict[TexasMatch.STRAIGHT_FLUSH] = 0

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
    hand_cards = ts.input_hand_cards()

    # import cProfile
    # import pstats
    # profiler = cProfile.Profile()
    # profiler.enable()  # 开始记录

    cards = ts.calc_property_by_hand(hand_cards)

    # profiler.disable()  # 停止记录

    # # 分析结果（按总耗时排序，显示前10行）
    # stats = pstats.Stats(profiler)
    # # stats.sort_stats('cumulative').print_stats(10) 
    # stats.sort_stats('tottime').print_stats(10) 