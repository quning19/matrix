#coding=utf-8

import time
from matrix.base.BaseJob import BaseJob

black_jack = 21
total_cards_num = 13
all_cards = [1,2,3,4,5,6,7,8,9,10,11,12,13]

action_hit = 1
action_pass = 2
action_double = 3
action_split = 4
class CalcProbability(BaseJob):

    host_card = 0

    host_prob_sheet = {}    # 庄家 各点数概率
    player_base_prob = {}   # 玩家 胜平负概率
    player_base_expect = {} # 玩家 基础期望
    player_best_expect = {} # 玩家 最好期望
    player_best_action = {} # 玩家 最好动作

    def __init__(self, options):
        BaseJob.__init__(self, options)
        pass

    def run(self):
        self.logger.info('start')

        self.calc_black_jack()

        # self.calc_player_hit_prob()

        self.logger.info('finished')

    def calc_black_jack(self):
        self.logger.info('start')
        for i in range(total_cards_num):
            self.host_card = all_cards[i]
            self.calc_host_prob()
            self.reset_player_prob()
            for j in range(black_jack + 1, 1, -1):
                self.calc_player_base_prob(j)
                self.calc_player_base_expect(j)
                self.calc_player_best_expect(j)
            self.output_player_base_prob()

        self.output_host_prob()
        self.output_player_base_expect()

    def calc_host_prob(self):
        card = self.host_card
        self._new_host_prob()
        self._calc_probability([card], 1)
        self.host_prob_sheet[card] = self._get_host_prob()

    def reset_player_prob(self):
        self.player_base_prob[self.host_card] = {}
        self.player_base_expect[self.host_card] = {}
        self.player_best_expect[self.host_card] = {}
        self.player_best_action[self.host_card] = {}

    def _calc_player_expection(host_card, player_point, action):
        if action == action_pass:
            pass
        if action == action_hit:
            pass
        if action == action_double:
            pass
        if action == action_split:
            pass

    def _calc_hit_expect(self, player_point):
        expect = 0

        for i in range(total_cards_num):
            card = all_cards[i]
            point = self._get_point([card], player_point)
            if point > black_jack:
                expect = expect - 1
            else:
                expect = expect + self.player_best_expect[self.host_card][point]

        expect = expect / total_cards_num

        return expect


    def calc_player_best_expect(self, player_point):
        host_card = self.host_card
        pass_expect = self.player_base_expect[host_card][player_point]
        hit_expect = self._calc_hit_expect(player_point)

        # best_expect = max(pass_expect, hit_expect)

        pass

    def calc_player_base_expect(self, player_point):
        probs = self.player_base_prob[self.host_card][player_point]
        expect = probs['win'] - probs['lose']
        self.player_base_expect[self.host_card][player_point] = expect
        return expect
    
        
    def output_player_base_expect(self):
        self.logger.debug('player base expect:')

        for i in range(10, black_jack + 2):
            line = str(i) + ': '
            for j in range(total_cards_num):
                prob = self.player_base_expect[all_cards[j]][i]
                line = line + '%5.2f '%prob
            self.logger.debug(line)

    def calc_player_base_prob(self, player_point):
        win = 0
        tie = 0
        lose = 0
        prob_sheet = self.host_prob_sheet[self.host_card]
        if player_point > black_jack:
            lose = 1
        else:
            for host_point in prob_sheet:
                p = prob_sheet[host_point]
                if host_point > black_jack:
                    win += p
                    continue
                if player_point < host_point:
                    lose += p
                    continue
                if player_point == host_point:
                    tie += p
                    continue
                if player_point > host_point:
                    win += p
                    continue
        base_prob = {'win': win, 'tie': tie, 'lose': lose}
        self.player_base_prob[self.host_card][player_point] = base_prob

    def output_player_base_prob(self):
        self.logger.debug('Host Card = %s, player base prob:'%self._get_card_string(self.host_card))
        for i in range(10, black_jack + 1):
            line = str(i) + ','
            prob = self.player_base_prob[self.host_card][i]
            line = line + '%5.2f%%,%5.2f%%,%05.2f%%,'%(prob['win'] * 100, prob['tie'] * 100, prob['lose'] * 100)
            self.logger.debug(line)

    def output_host_prob(self):
        for card in self.host_prob_sheet:
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
        self._current_host_prob = {17:0,18:0,19:0,20:0,21:0,22:0}

    def _calc_probability(self, card_list, probability):

        point, _ = self._get_point(card_list)

        if point > 21:
            # self.logger.debug('%d, %5.4f%%  '%(22, probability * 100) + str(card_list))
            self._add_host_prob(22, probability)
            return
        
        if point > 16:
            # self.logger.debug('%d, %5.4f%%  '%(point, probability * 100) + str(card_list))
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

    def _get_point(self, card_list, point = 0):
        res = point
        for i in range(len(card_list)):
            card = card_list[i]
            res = res + min(card, 10)
        if 1 in card_list and res <= 11:
            return res + 10, res
        return res, res
        
        