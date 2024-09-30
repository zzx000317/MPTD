import pandas as pd
from GraphModel import graph_generate
from Transition import get_M1_transnumber
from Transition import get_M2_transnumber


def get_M1_Normalizator(node_i, node_j, co_list):
    """获取 M1模型的归一化因子"""
    normalizator = 0

    if node_i == 0:
        # move状态的归一化因子
        '''将co_list中node_j的属性个数作为(node_i,node_j)的归一化因子'''
        if node_j in co_list.keys():
            normalizator = len(co_list[node_j])
        else:
            pass

    elif node_j == 0:
        # stay状态的归一化因子
        '''将一条轨迹中node_i停留时间之和的最大值作为(node_i,node_i)的归一化因子'''
        if node_i in co_list.keys():
            co = co_list[node_i]
            prfx = co[0][0]
            nors = []
            nor = 0
            for i in range(len(co)):
                _prfx = co[i][0]
                if set(prfx).issubset(set(_prfx)) and co[i][2] > 0:
                    nor += co[i][2]
                elif not set(prfx).issubset(set(_prfx)):
                    nors.append(nor)
                    prfx = co[i][0]
                    nor = co[i][2]
            nors.append(nor)
            if max(nors):
                normalizator = max(nors)
            else:
                normalizator = 1
        else:
            pass

    else:
        # 终止状态的归一化因子
        normalizator = 1

    # '''避免归一化因子（做分母）为0'''
    # if normalizator == 0:
    #     normalizator = 1


    # print('normalizator = {}'.format(normalizator))
    # print("normalizator = ")
    # print(normalizator)
    return normalizator


def get_M2_Normalizator(node_i, node_j, node_k, co_list):
    """获取 M2模型的归一化因子"""
    normalizator = 0

    if node_j == 0 and node_k == 0:
        # (i,i,i)状态的归一化因子
        '''将一条轨迹中node_i停留时间之和减1的最大值作为(node_i,node_i，node_i)的归一化因子'''
        if node_i in co_list.keys():
            co = co_list[node_i]
            prfx = co[0][0]
            nors = []
            nor = 0
            for i in range(len(co)):
                #if prfx in co[i][0]:
                _prfx = co[i][0]
                if set(prfx).issubset(set(_prfx)) and co[i][2]-1 > 0:
                    nor += co[i][2]-1
                elif not set(prfx).issubset(set(_prfx)):
                    nors.append(nor)
                    prfx = co[i][0]
                    nor = co[i][2]-1
            nors.append(nor)
            if nors:
                normalizator = max(nors)
        else:
            pass

    elif node_j == 0 and node_k != 0:
        # (i,i,k)状态的归一化因子
        '''将co_list中node_k的属性个数作为(node_i,node_i,node_j)的归一化因子'''
        if node_k in co_list.keys():
            co = co_list[node_k]
            for i in range(len(co)):
                if co[i][0][-2] == node_i:
                    normalizator += 1
            #normalizator = len(co_list[node_k])
        else:
            pass

    elif node_j != 0 and node_k == 0:
        # (i,j,j)状态的归一化因子
        '''将co_list中node_j的属性个数作为(node_i,node_j,node_j)的归一化因子'''
        if node_j in co_list.keys():
            co = co_list[node_j]
            for i in range(len(co)):
                if co[i][0][-2] == node_i:
                    normalizator += 1
            #normalizator = len(co_list[node_j])
        else:
            pass

    elif node_j != 0 and node_k != 0:
        # (i,j,k)状态的归一化因子
        '''将co_list中(node_i,node_j,node_k)作为前缀末尾的出现次数作为(node_i,node_j,node_k)的归一化因子'''
        nor = 0
        if node_k in co_list.keys():
            co = co_list[node_k]
            for i in range(len(co)):
                if co[i][0][-2] == node_j and co[i][0][-3] == node_i:
                    nor += 1
            normalizator = nor
        else:
            pass

    else:
        # (i,j,(-1,-1))状态的归一化因子
        normalizator = 1

    # '''避免归一化因子（做分母）为0'''
    # if normalizator == 0:
    #     normalizator = 1

    # print('normalizator ={}'.format(normalizator))
    # print("normalizator = ")
    # print(normalizator)
    return normalizator


def make_Normcut(v):
    """对加噪后的转移计数进行后处理，使负值回归到 1"""

    N = sum([x for x in v if x < 1])
    P = sum([x for x in v if x > 1])

    n = len([x for x in v if x < 1])
    p = len([x for x in v if x > 1])

    while N != n and P != p:
        ps = min([x for x in v if x > 1])
        temp = ps + N
        if temp < n:
            N = temp
            P = P - ps
            for i in range(len(v)):
                if v[i] == ps:
                    v[i] =1
        else:
            N = n
            for i in range(len(v)):
                if v[i] == ps:
                    v[i] = temp - n
                    break

    for i in range(len(v)):
        if v[i] < 0.1:
            v[i] = 0.1

    return v


if __name__ == "__main__":

    """构建图模型"""
    csv_path = 'C:\WorkSpace\Accepted\griddata.csv'
    csv_file = pd.read_csv(csv_path, dtype=str)

    users = list(set(csv_file['user_id']))
    users.sort(key=list(csv_file['user_id']).index)

    for user_id in users:
        user_rows = csv_file[csv_file.user_id == user_id].index.tolist()
        node_start, node_end, co_list, coords = graph_generate(csv_file, user_rows)

        """确定状态空间"""
        states = list(coords) + [(-1, -1)]

        for sign in range(2):
            for j in states:
                if sign:
                    count_ij = get_M1_transnumber(j, co_list, node_end)
                else:
                    count_ij = get_M2_transnumber(j, co_list, node_end)

                '''获取转换对应的归一化因子'''
                for transtion in count_ij.keys():
                    transcount = count_ij[transtion]

                    if sign:
                        if transtion[1] == (-1, -1):
                            normalizator = get_M1_Normalizator(transtion[0], transtion[1], co_list)
                        elif transtion[0] == transtion[1]:
                            normalizator = get_M1_Normalizator(transtion[0], 0, co_list)
                        elif transtion[0] != transtion[1]:
                            normalizator = get_M1_Normalizator(0, transtion[1], co_list)
                    else:
                        try:
                            if transtion[2] == (-1, -1):
                                normalizator = get_M2_Normalizator(transtion[0], transtion[1], transtion[2], co_list)
                            elif transtion[0] == transtion[1] and transtion[1] == transtion[2]:
                                normalizator = get_M2_Normalizator(transtion[0], 0, 0, co_list)
                            elif transtion[0] == transtion[1] and transtion[1] != transtion[2]:
                                normalizator = get_M2_Normalizator(transtion[0], 0, transtion[2], co_list)
                            elif transtion[0] != transtion[1] and transtion[1] == transtion[2]:
                                normalizator = get_M2_Normalizator(transtion[0], transtion[1], 0, co_list)
                            elif transtion[0] != transtion[1] and transtion[1] != transtion[2]:
                                normalizator = get_M2_Normalizator(transtion[0], transtion[1], transtion[2], co_list)
                        except:
                            normalizator = 1




