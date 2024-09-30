def get_start_node_score(node_start, coords):
    """起始结点评分函数"""

    sum = 0
    start_node_score = {}
    for node in coords:
        if node in node_start:
            sum += node_start[node]

    for node in node_start:
        start_node_score[node] = round(node_start[node] / sum, 3)

    # print('* 开始节点评分函数：{}'.format(start_node_score))
    return start_node_score


def get_M1_transnumber(node_j, co_list, node_end):
    """获取 p(node_i,node_j) 的计数"""

    count_ij = {}

    if node_j == (-1, -1):
        # 终止计数
        endi = {}
        '''将结束节点在轨迹中的出现次数作为 (node_end,(-1,-1))的转移计数'''
        for node_i in node_end.keys():
            co_end = node_end[node_i]
            for i in range(len(co_end)):
                node_i = co_end[i][0][-1]
                if node_i in endi.keys():
                    endi[node_i] += co_end[i][1]
                else:
                    endi[node_i] = co_end[i][1]

        if endi:
            for node_i, count9 in endi.items():
                count_ij[(node_i, node_j)] = count9
    else:
        # 停留计数
        count0 = 0
        '''将中间节点的停留时间作为 (node_mid,node_mid)的转移计数'''
        if node_j in co_list.keys():
            co_mid = co_list[node_j]
            for i in range(len(co_mid)):
                if co_mid[i][2] >= 1:
                    count0 += co_mid[i][2]
        count_ij[(node_j, node_j)] = count0

        # 移动计数
        movei = {}
        '''将中间节点前缀末尾两个节点的的出现次数作为 (mid_prfx[-2],mid_prfx[-1])的转移计数'''
        if node_j in co_list.keys():
            co_mid = co_list[node_j]
            for i in range(len(co_mid)):
                try:
                    node_i = co_mid[i][0][-2]
                    if node_i in movei.keys():
                        movei[node_i] += 1
                    else:
                        movei[node_i] = 1
                except:
                    pass

        if movei:
            for node_i, count1 in movei.items():
                count_ij[(node_i, node_j)] = count1

    # if count_ij:
    #     for itoj in count_ij:
    #         pass
    #         print('{}：{}'.format(itoj, count_ij[itoj]))
    # else:
    #     print("nan")

    return count_ij


def get_M2_transnumber(node_k, co_list, node_end):
    """获取 p(node_i,node_j,node_k) 的计数"""

    count_ij = {}

    if node_k == (-1, -1):
        # node_k = (-1,-1)计数
        endij = {}
        '''遍历结束节点作为node_j'''
        for node_j in node_end.keys():
            co_end = node_end[node_j]
            try:
                '''遍历co_list中node_j的属性，查找与node_end中的node_j对应的信息'''
                co_mid = co_list[node_j]
                for i in range(len(co_end)):
                    prfx = co_end[i][0]
                    for j in range(len(co_mid)):
                        if co_mid[j][0] == prfx:
                            staytime = co_mid[j][2]
                            if staytime >= 1:
                                # node_i == node_j
                                try:
                                    '''将node_j作为结束节点停留的次数作为(node_j,node_j,(-1,-1))的转移计数'''
                                    node_i = co_end[j][0][-1]
                                    node_j = co_end[j][0][-1]
                                    if (node_i, node_j) in endij.keys():
                                        endij[(node_i, node_j)] += co_mid[j][1]
                                    else:
                                        endij[(node_i, node_j)] = co_mid[j][1]
                                except:
                                    pass

                            elif staytime == 0:
                                # node_i != node_j
                                '''将结束节点前缀末尾两个节点作为轨迹终止的次数作为(node_j,node_j,(-1,-1))的转移计数'''
                                node_i = co_end[i][0][-2]
                                node_j = co_end[i][0][-1]
                                if (node_i, node_j) in endij.keys():
                                    endij[(node_i, node_j)] += co_mid[j][1]
                                else:
                                    endij[(node_i, node_j)] = co_mid[j][1]

            except:
                pass

        if endij:
            for node_ij, count9 in endij.items():
                count_ij[(node_ij[0], node_ij[1], node_k)] = count9

    else:
        # node_j == node_k计数
        stayi = {}
        if node_k in co_list.keys():
            co_mid = co_list[node_k]
            for i in range(len(co_mid)):
                if co_mid[i][2] >= 1:
                    # node_i != node_j
                    try:
                        '''将停留的中间节点的前缀末尾节点(除本身)的出现次数作为(node_i,node_j,node_j)的转移计数'''
                        node_i = co_mid[i][0][-2]
                        if node_i in stayi.keys():
                            stayi[node_i] += co_mid[i][1]
                        else:
                            stayi[node_i] = co_mid[i][1]
                        if co_mid[i][2] >= 2:
                            # node_i == node_j
                            '''将停留的中间节点的停留时间减1作为(node_i,node_i,node_i)的转移计数'''
                            node_i = co_mid[i][0][-1]
                            if node_i in stayi.keys():
                                stayi[node_i] += co_mid[i][2] - 1
                            else:
                                stayi[node_i] = co_mid[i][2] - 1
                    except:
                        pass

        if stayi:
            for node_i, count0 in stayi.items():
                count_ij[(node_i, node_k, node_k)] = count0

        # node_j != node_k移动计数
        moveij = {}
        if node_k in co_list.keys():
            co_mid = co_list[node_k]
            for i in range(len(co_mid)):
                try:
                    _prfx =co_mid[i][0][:-1]
                    node_j = co_mid[i][0][-2]
                    co_move = co_list[node_j]
                    '''遍历co_list中node_k的前一个前缀节点node_j的属性，找到与node_k前缀(去掉本身)相同的信息'''
                    for j in range(len(co_move)):
                        if co_move[j][0] == _prfx:
                            if co_move[j][2] >= 1:
                                #node_i = node_j
                                node_i = node_j
                                '''将前缀匹配成功后node_j的停留次数作为(node_j,node_j,node_k)的转移计数'''
                                if (node_i, node_j) in moveij.keys():
                                    moveij[(node_i, node_j)] += co_move[j][1]
                                else:
                                    moveij[(node_i, node_j)] = co_move[j][1]
                            elif co_move[j][2] == 0:
                                #node_i ！= node_j
                                node_i = co_move[j][0][-2]
                                '''将前缀匹配成功后(node_i,node_j)的出现次数作为(node_i,node_j,node_k)的转移计数'''
                                if (node_i, node_j) in moveij.keys():
                                    moveij[(node_i, node_j)] += co_move[j][1]
                                else:
                                    moveij[(node_i, node_j)] = co_move[j][1]
                except:
                    pass

        if moveij:
            for node_ij, count1 in moveij.items():
                count_ij[(node_ij[0], node_ij[1], node_k)] = count1

    # if count_ij:
    #     for itoj in count_ij:
    #         print('{}：{}'.format(itoj, count_ij[itoj]))
    # else:
    #     print("nan")

    return count_ij
    pass

