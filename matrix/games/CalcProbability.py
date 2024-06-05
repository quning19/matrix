#coding=utf-8

from matrix.base.BaseJob import BaseJob

class CalcProbability(BaseJob):

    total_cards_num = 13
    all_cards = [1,2,3,4,5,6,7,8,9,10,11,12,13]

    def __init__(self, options):
        BaseJob.__init__(self, options)
        pass

    def run(self):
        self.logger.info('calc probability')
        self.calc_host_probability()

    def calc_host_probability(self):
        self.host_prob_sheet = {}
        for i in range(self.total_cards_num):
            card = self.all_cards[i]
            self._new_host_prob()
            self._calc_probability([card], 1)
            self.host_prob_sheet[card] = self._get_host_prob()
            # self.logger.info('%d %5.2f%% %5.2f%%'%(card, under * 100, over * 100))
        self.output_host_prob()

    def output_host_prob(self):
        for i in range(len(self.host_prob_sheet)):
            card = self.all_cards[i]
            prob_list = self.host_prob_sheet[card]
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

        for i in range(self.total_cards_num):
            card = self.all_cards[i]
            clist = card_list[:]
            clist.append(card)
            self._calc_probability(clist, probability / self.total_cards_num)

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
        
        