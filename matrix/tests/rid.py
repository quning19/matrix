import math
import random
import math

encode_num = 21415926

max_num = 0

for i in range(3):
    num = random.randint(0, 67000000)
    num_encode = num ^ encode_num

    print(num_encode)
    right5 = num_encode % 100000
    left3 = math.floor(num_encode/100000)
    left2 = left3 % 26
    left1 = math.floor(left3/26)
    left1 = chr(65 + left1)
    left2 = chr(65 + left2)
    print(left1 + left2 + str(right5))

    print('======')
