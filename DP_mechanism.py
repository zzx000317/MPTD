import numpy as np
import math

# loc=0, scale=sensitivity / epsilon
def laplace_mech(data, epsilon):
    """对数据添加拉普拉斯噪声,loc scale"""
    loc = 0
    scale = 1.0 / epsilon
    s = np.random.laplace(loc, scale)
    data += s
    return data


def exp_mech(scores, epsilon, sensitivity):
    """指数机制实现"""
    exponents_dict = {}
    sum = 0
    exponent_sum = 0

    for co in scores:
        expo = 0.5 * scores[co] * epsilon / sensitivity
        exponents_dict[co] = math.exp(expo)

    for co in exponents_dict:
        sum += exponents_dict[co]

    for co in exponents_dict:
        exponents_dict[co] = exponents_dict[co] / sum

    random = np.random.uniform(0, 1)  # 在0至sum之间随机取一个数
    for co in exponents_dict:
        exponent_sum += exponents_dict[co]
        if exponent_sum > random:
            # print(co)
            return co
