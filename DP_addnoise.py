from Transition import get_M1_transnumber
from Transition import get_M2_transnumber
from Normalization import get_M1_Normalizator
from Normalization import get_M2_Normalizator
from Normalization import make_Normcut
from DP_mechanism import laplace_mech


def get_privacy_degree(sign, states, co_list, node_end):
    """获取状态空间中每个转换的隐私级别"""
    degrees = {}

    '''遍历状态空间的转换组合，获取其转换计数'''
    for state in states:
        if sign:
            count_ij = get_M1_transnumber(state, co_list, node_end)
        else:
            count_ij = get_M2_transnumber(state, co_list, node_end)

        '''计算转换的隐私级别'''
        for transtion in count_ij.keys():
            sumstay = 0
            sumcount = 0
            sumtrans = count_ij[transtion]

            for node in transtion:
                if node in co_list.keys():
                    co = co_list[node]
                    for i in range(len(co)):
                        sumcount += co[i][1]
                        sumstay += co[i][2]
            degrees[transtion] = round((0.9 * sumcount + 0.1 * sumstay) * 0.5 + sumtrans * 0.5, 2)

    '''获取隐私级别的边界值(一个用户)'''
    min_deg = min(degrees.values())
    max_deg = max(degrees.values())

    #print('min = {},max = {}'.format(min_deg, max_deg))
    #print('degrees = {}'.format(degrees))

    return degrees, min_deg, max_deg


def privacy_budget_allocate(epsilon_b, transtion, degrees, min_deg, max_deg):
    """根据转换的隐私级别为其分配隐私预算"""

    '''归一化处理'''
    if transtion in degrees.keys():
        temp1 = (degrees[transtion] - min_deg)/(max_deg - min_deg)
        co_deg = round((degrees[transtion] - min_deg)/(max_deg - min_deg), 2)
    else:
        co_deg = 0

    #epsilon_b = 1
    impactor = 0.5  # 隐私级别对预算的影响程度
    epsilon = round(epsilon_b * (1 - impactor * co_deg), 3)

    #print('{} de epsilon = {}'.format(transtion, epsilon))

    return epsilon


def addnoise_to_transnumber(sign, epsilon_b, states, co_list, node_end, degrees, min_deg, max_deg):
    """对获取的转换计数进行个性化加噪"""
    transcounts = {}

    '''遍历状态空间的转换组合，获取其转换计数'''
    for j in states:
        if sign:
            count_ij = get_M1_transnumber(j, co_list, node_end)
        else:
            count_ij = get_M2_transnumber(j, co_list, node_end)

        '''获取为转换分配的预算'''
        for transtion in count_ij.keys():
            # transcounts[transtion] = count_ij[transtion]
            transcount = count_ij[transtion]
            epsilon = privacy_budget_allocate(epsilon_b, transtion, degrees, min_deg, max_deg)

            '''获取转换对应的归一化因子'''
            if sign:
                if transtion[0] == transtion[1]:
                    normalizator = get_M1_Normalizator(transtion[0], 0, co_list)
                else:
                    normalizator = get_M1_Normalizator(0, transtion[-1], co_list)
            else:
                try:
                    if transtion[0] == transtion[1] and transtion[1] == transtion[2]:
                        normalizator = get_M2_Normalizator(transtion[0], 0, 0, co_list)
                    elif transtion[0] == transtion[1] and transtion[1] != transtion[2]:
                        normalizator = get_M2_Normalizator(transtion[0], 0, transtion[2], co_list)
                    elif transtion[0] != transtion[1] and transtion[1] == transtion[2]:
                        normalizator = get_M2_Normalizator(transtion[0], transtion[1], 0, co_list)
                    elif transtion[0] != transtion[1] and transtion[1] != transtion[2]:
                        normalizator = get_M2_Normalizator(transtion[0],transtion[1], transtion[2], co_list)
                except:
                    normalizator = 1

            #print('{}的归一化因子：{}'.format(transtion, normalizator))

            '''归一化处理'''
            if normalizator:
                nor_transcount = transcount / normalizator
            else:
                nor_transcount = transcount

            '''拉普拉斯机制进行个性化加噪'''
            addnoise_transcount = laplace_mech(nor_transcount, epsilon)
            transcounts[transtion] = round(addnoise_transcount * normalizator, 4)

    # print('transcounts : {}'.format(transcounts))

    n = list(transcounts.values())
    '''对加噪后的转换计数进行Normcut后处理'''
    norm = make_Normcut(n)
    for i, k in enumerate(transcounts.keys()):
        transcounts[k] = norm[i]

    return transcounts



