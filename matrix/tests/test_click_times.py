
import os
import math 
import random
import click
import json
import logging
from ..utils import common_utils


import logging

class ClickSimulator:

    def __init__(self):
        self._boxes = []
        self._count_1 = 0
        self._count_2 = 0
        self._count_3 = 0

    def run(self, times):
        for i in range(times):
            self.generate_new_box()
            self.try_click_box()

        print(self._count_1, self._count_2, self._count_3)

    def try_click_box(self):
        if self._boxes[-1] > 1:
            pass


    def generate_new_box(self):
        box = 1
        num = random.random()
        if num < 1/7:
            box = 2
        elif num < 2/7:
            box = 3
        
        self._boxes.append(box)