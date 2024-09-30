import numpy as np
import pandas as pd


def get_transtion_denominator(i, j, transcounts):
    '''为计算转换概率获取转换计数的分母'''
    deno = 0
    if not j:
        for transtion in transcounts.keys():
            if transtion[0] == i:
                deno += transcounts[transtion]
    else:
        for transtion in transcounts.keys():
            if transtion[0] == i and transtion[1] == j:
                deno += transcounts[transtion]

    if deno:
        denominator = deno
    else:
        denominator = 1

    # print(denominator)
    return denominator


def generate_transition_matrix(sign, states, transcounts):
    '''生成概率转换矩阵'''

    transtion = [i for i in list(transcounts.keys())]

    if sign:
        # M1概率矩阵
        P = np.zeros((len(states), len(states)))

        for i, last_point in enumerate(states):
            for j, next_point in enumerate(states):
                points = (last_point, next_point)
                if points in transtion:
                    P[i, j] = transcounts[points] / get_transtion_denominator(last_point, 0, transcounts)
                else:
                    P[i, j] = 0

    else:
        # M2概率矩阵
        P = np.zeros((len(states), len(states), len(states)))

        for i, last_point in enumerate(states):
            for j, current_point in enumerate(states):
                for k, next_point in enumerate(states):
                    points = (last_point, current_point, next_point)
                    if points in transtion:
                        P[i, j, k] = transcounts[points] / get_transtion_denominator(last_point, current_point, transcounts)
                    else:
                        P[i, j, k] = 0



    form_header = [i for i in states]
    if sign:
        df = pd.DataFrame(P, form_header, form_header)
    else:
        for i in range(len(P)):
            df = pd.DataFrame(P[i, ...], form_header, form_header)
    # print(df)

    # print('transmatrix : {}'.format(P))
    return P


def get_initial_state_prob(current_point, states):
    """设置初始状态概率分布"""

    P = np.zeros(len(states))
    for i, point in enumerate(states):
        if point == current_point:
            P[i] = 1

    form_header = [i for i in states]
    df = pd.DataFrame(P, form_header)
    # print(df)

    # print(P)
    return P


def generate_M1_syntrajectory(states,transition_matrix,start_state):
    """随机生成观察序列"""

    Tstates = []
    k = 1
    current_state = start_state

    while current_state != (-1, -1) and k <= 100:

        Tstates.append(current_state)
        #print("current_state: {}".format(current_state))
        initial_state_prob = get_initial_state_prob(current_state, states)

        prob = initial_state_prob.dot(np.linalg.matrix_power(transition_matrix, k))
        sumprob = np.sum(prob, axis=0)
        #print("sumprob: {}".format(sumprob))
        # print("P: {}".format(prob))
        # print(type(transition_matrix))
        #print("k: {}".format(k))

        current_index = np.random.choice([states.index(i) for i in states], p=[i/np.sum(prob) for i in prob])
        current_state = states[current_index]
        k = k + 1

    #print("Tstates: {}".format(Tstates))

    return Tstates




def generate_syntrajectory(states, transnumbers, transition_matrix, start_state, theta1, theta2, limit):
    """泛化生成合成轨迹"""
    # print(" theta1: {}, theta2:{}".format(theta1, theta2))

    Tstates = []
    k = 1
    current_state = start_state

    '''设置终止条件'''
    while current_state != (-1, -1) and k <= limit:

        '''更新当前节点和前一个节点'''
        if Tstates:
            previous_state = Tstates[-1]
        Tstates.append(current_state)
        # print("current_state: {}".format(current_state))

        '''计算选择模型的比较参数'''
        ni = []
        for transtion in transnumbers.keys():
            if transtion[0] == current_state:
                ni.append(transnumbers[transtion])

        sumni = sum(ni)
        if ni:
            ni1 = max(ni)
            ni.remove(ni1)
            if ni:
                ni2 = max(ni)
            else:
                ni2 = 0
        else:
            ni1 = 0
        # print("ni1: {}, ni2: {}, sumni: {}".format(ni1, ni2, sumni))

        if sumni < theta1 or ni1/ni2 >= theta2:
            # print("M1")
            '''选择M1模型预测下一个节点'''
            initial_state_prob = get_initial_state_prob(current_state, states)
            prob = initial_state_prob.dot(np.linalg.matrix_power(transition_matrix[1], k))
            #sumprob = np.sum(prob, axis=0)
            # print("sumprob: {}".format(sumprob))
            # print("P: {}".format(prob))
            # print(type(transition_matrix))
            # print("k: {}".format(k))

            current_index = np.random.choice([states.index(i) for i in states], p=[i/np.sum(prob) for i in prob])

        else:
            '''选择M2模型预测下一个节点'''
            # print("M2!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            previous_index = states.index(previous_state)
            current_index = states.index(current_state)
            prob = np.linalg.matrix_power(transition_matrix[0], k)[previous_index][current_index]

            # print("k: {}".format(k))
            current_index = np.random.choice([states.index(i) for i in states], p=[i / np.sum(prob) for i in prob])


        current_state = states[current_index]
        k = k + 1

    # print("Tstates: {}".format(Tstates))
    return Tstates





