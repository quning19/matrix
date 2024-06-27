#coding=utf-8

import time
from matrix.base.BaseJob import BaseJob

black_jack = 21
total_cards_num = 13
all_cards = [1,2,3,4,5,6,7,8,9,10,11,12,13]
class CalcProbability(BaseJob):

    player_base_prob = {}   # 玩家 胜平负概率
    host_prob_sheet = {}    # 庄家 各点数概率

    def __init__(self, options):
        BaseJob.__init__(self, options)
        pass

    def run(self):
        self.logger.info('start')
        self.calc_host_probability()
        self.calc_player_base_prob()
        self.calc_player_hit_prob()

        self.logger.info('finished')

    def calc_player_hit_prob(self):
        self.logger.info('calc player hit prob')
        for i in range(total_cards_num):
            host_card = all_cards[i]
            host_prob = self.host_prob_sheet[host_card]
        

            

    def calc_player_base_prob(self):
        self.logger.info('calc player base prob')
        for i in range(2, black_jack + 2):
            base_prob = {}
            self.player_base_prob[i] = base_prob
            for j in self.host_prob_sheet:
                win = 0
                tie = 0
                lose = 0
                prob_sheet = self.host_prob_sheet[j]
                if i > black_jack:
                    lose = 1
                else:
                    for k in prob_sheet:
                        p = prob_sheet[k]
                        if k > black_jack:
                            win += p
                            continue
                        if i < k:
                            lose += p
                            continue
                        if i == k:
                            tie += p
                            continue
                        if i > k:
                            win += p
                            continue
                base_prob[j] = {'win': win, 'tie': tie, 'lose': lose}
        self.output_player_base_prob()

    def output_player_base_prob(self):
        for i in range(10, black_jack + 1):
            line = str(i) + ','
            for j in self.host_prob_sheet:
                prob = self.player_base_prob[i][j]
                line = line + '%5.2f%%,%5.2f%%,%05.2f%%,'%(prob['win'] * 100, prob['tie'] * 100, prob['lose'] * 100)
            time.sleep(0.1)

    def calc_host_probability(self):
        self.logger.info('calc host point prob')
        for i in range(total_cards_num):
            card = all_cards[i]
            self._new_host_prob()
            self._calc_probability([card], 1)
            self.host_prob_sheet[card] = self._get_host_prob()
            # self.logger.info('%d %5.2f%% %5.2f%%'%(card, under * 100, over * 100))
        self.output_host_prob()

    def output_host_prob(self):
        for i in range(len(self.host_prob_sheet)):
            card = all_cards[i]
            prob_list = self.host_prob_sheet[card]
            time.sleep(0.1)
            self.logger.info('%s %5.2f%% %5.2f%% %5.2f%% %5.2f%% %5.2f%% ! %5.2f%%'%
                (self._get_card_string(card), prob_list[17]*100, prob_list[18]*100, prob_list[19]*100, prob_list[20]*100, prob_list[21]*100, prob_list[22]*100))

    def _add_host_prob(self, point, prob):
        if point not in self._current_host_prob:
            self._current_host_prob[point] = 0
        self._current_host_prob[point] += prob

    def _get_host_prob(self):
        return self._current_host_prob

    def _new_host_prob(self):
        self._current_host_prob = {}

    def _calc_probability(self, card_list, probability):

        point, _ = self._get_point(card_list)

        if point > 21:
            # self.logger.debug(card_list)
            # self.logger.debug('%d, %5.2f%%'%(22, probability * 100))
            self._add_host_prob(22, probability)
            return
        
        if point > 16:
            # self.logger.debug(card_list)
            # self.logger.debug('%d, %5.2f%%'%(point, probability * 100))
            self._add_host_prob(point, probability)
            return

        for i in range(total_cards_num):
            card = all_cards[i]
            clist = card_list[:]
            clist.append(card)
            self._calc_probability(clist, probability / total_cards_num)

    def _get_card_string(self, card):
        if card == 1:
            return 'A'
        if card == 10:
            return 'T'
        if card == 11:
            return 'J'
        if card == 12:
            return 'Q'
        if card == 13:
            return 'K'
        return str(card)

    def _get_point(self, card_list):
        res = 0
        for i in range(len(card_list)):
            card = card_list[i]
            res = res + min(card, 10)
        if 1 in card_list and res <= 11:
            return res + 10, res
        return res, res
        
        