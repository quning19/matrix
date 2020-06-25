#coding=utf-8

import os
import math 
import time
import random


names = ['曲宁','曹鑫','穆建辰','王登博','徐昊','关峰','黄睿','郭黎阳','袁芳瑞','闫伟','闫雪丰','刘秋梅']

totalPos = 16

result = {}
temp = []

for i in range(totalPos):
    temp.append(i + 1)

for i in range(len(names)):
    index = int(math.floor(random.random() * len(temp)))
    result[temp[index]] = names[i]
    temp.remove(temp[index])

for i in range(totalPos):
    p = i + 1
    time.sleep(0.6)
    if p in result:
        print('%02d : %s'%(p, result[p]))
    else:
        print('%02d : ----'%(p))







