import pandas as pd
import os
from collections import Counter
from computeProbs import generate_occurrence_number


def graph_generate_ori(file, rows):
    """构建图模型"""

    '''定义变量（用于存储图模型信息）'''
    node_start = {}  # 图模型的起始节点
    node_end = {}  # 图模型的结束节点
    co_list = {}  # 图模型的中间节点
    user_coords = []  # 所有位置点坐标的去重集合(一个用户)

    '''读取数据'''
    user_points = file[rows[0]:rows[-1] + 1]
    # print('用户起始行：{} ；用户结束行：{}'.format(rows[0], rows[-1]))
    trajectorys = list(set(user_points['trajectory_id']))
    trajectorys.sort(key=list(user_points['trajectory_id']).index)

    '''遍历用户轨迹'''
    for id in trajectorys:
        trajectory_coords = []  # 一条轨迹位置点坐标的集合
        trajectory_rows = user_points[user_points.trajectory_id == id].index.tolist()

        # print('轨迹起始行：{} ；轨迹结束行：{}'.format(trajectory_rows[0], trajectory_rows[-1]))
        X, Y = list(file['loc_x'][trajectory_rows[0]:trajectory_rows[-1] + 1]), \
               list(file['loc_y'][trajectory_rows[0]:trajectory_rows[-1] + 1])  # 一条轨迹的坐标集合


        '''构建图模型'''
        prfx = []  # 轨迹前缀
        co_flag1 = 1
        '''遍历每个轨迹位置点'''
        for i in range(0, len(X)):
            x, y = float(X[i]), float(Y[i])
            trajectory_coords.append((x, y))
            user_coords.append((x, y))
            # 起始节点的前缀为空
            if prfx == []:
                '''开始节点点集'''
                if (x, y) not in node_start:
                    node_start[(x, y)] = 1
                else:
                    node_start[(x, y)] += 1
                prfx.append((x, y))
            elif i == len(X) - 1:
                '''结束节点点集'''
                if (x, y) not in node_end.keys():
                    end_prfx_add_co = prfx
                    # 结束节点与前一个点不同，前缀更新
                    if (x, y) != prfx[-1]:
                        end_prfx_add_co.append((x, y))
                    node_end[(x, y)] = [[end_prfx_add_co, 1, 0]]
                else:
                    # 当前节点与前一个结点相同，前缀不更新，停留时间加一
                    if (x, y) == prfx[-1]:
                        co = co_list[(x, y)][-1]
                        co[2] += 1
                        end_prfx_add_co = prfx
                    else:
                        # 当前节点与前一个结点不同
                        end_prfx_add_co = prfx
                        end_prfx_add_co.append((x, y))  # 将该坐标加入前缀信息
                    # 遍历此节点前缀信息
                    end_co_attribute_set = node_end[(x, y)]
                    end_flag = 1  # 前缀信息异同标志位
                    for co_attribute in end_co_attribute_set:
                        # 如果查到该前缀信息，co_flag = 0，前缀不更新，count加一
                        if co_attribute[0] == end_prfx_add_co:
                            co_attribute[1] += 1
                            end_flag = 0
                            break
                    # 如果没有查到该前缀信息，co_flag = 1，前缀更新
                    if end_flag:
                        node_end[(x, y)].append([end_prfx_add_co, 1, 0])

            else:
                '''中间点点集'''

                if (x, y) not in co_list.keys():
                    co_list[(x, y)] = [[prfx[:], 1, 0]]
                    # 第一个中间节点和开始节点相同时，停留时间加一，co_flag1保证只执行一次
                    if trajectory_coords[0] == trajectory_coords[1] and co_flag1:
                        #co_list[(x, y)] = [[prfx[:], 1, 1]]
                        co = co_list[trajectory_coords[0]][0]
                        co[2] = 1
                        co_flag1 = 0
                    else:
                        prfx.append((x, y))
                        prfx_add_co = prfx
                        co_list[(x, y)] = [[prfx_add_co[:], 1, 0]]
                else:
                    # 当前节点与前一个结点相同
                    if (x, y) == prfx[-1]:
                        co = co_list[(x, y)][-1]
                        co[2] += 1
                    else:
                        prfx.append((x, y))  # 将该坐标加入前缀信息
                        # 遍历此节点前缀信息
                        co_attribute_set = co_list[(x, y)]
                        co_flag = 1  # 前缀信息不同标志位
                        for co_attribute in co_attribute_set:
                            # 如果查到该前缀信息，co_flag = 0，前缀不更新，count加一
                            if co_attribute[0] == prfx:
                                co_attribute[1] += 1
                                co_flag = 0
                                break
                        # 如果没有查到该前缀信息，co_flag = 1，前缀更新
                        if co_flag:
                            reprfx_add_co = prfx
                            co_list[(x, y)].append([reprfx_add_co[:], 1, 0])

        #print('第{}条轨迹坐标：{}'.format(id, trajectory_coords))

    coords = set(user_coords)
    #GenerateExcel.Generateexcel(node_start, co_list, node_end, userid)


    print('* 开始节点点集：{}'.format(node_start))
    print('* 中间节点点集：')
    for keys, values in co_list.items():
        print(keys)
        print(values)
    # print('* 中间节点点集：{}'.format(co_list))
    print('* 结束节点点集：{}'.format(node_end))
    print('* 轨迹点坐标集：{}'.format(coords))
    # print('\n')

    return node_start, node_end, co_list, coords

def graph_generate(file, rows):

    """构建图模型"""

    '''定义变量（用于存储图模型信息）'''
    node_start = {}  # 图模型的起始节点
    node_end = {}  # 图模型的结束节点
    co_list = {}  # 图模型的中间节点
    user_coords = []  # 所有位置点坐标的集合(一个用户)
    rawlist = [] # 用于存储轨迹集


    '''读取数据'''
    user_points = file[rows[0]:rows[-1] + 1]
    # print('用户起始行：{} ；用户结束行：{}'.format(rows[0], rows[-1]))
    trajectorys = list(set(user_points['trajectory_id']))
    trajectorys.sort(key=list(user_points['trajectory_id']).index)

    '''遍历用户轨迹'''
    for id in trajectorys:
        trajectory_coords = []  # 一条轨迹位置点坐标的集合
        trajectory_rows = user_points[user_points.trajectory_id == id].index.tolist()

        # print('轨迹起始行：{} ；轨迹结束行：{}'.format(trajectory_rows[0], trajectory_rows[-1]))
        X, Y = list(file['loc_x'][trajectory_rows[0]:trajectory_rows[-1] + 1]), \
               list(file['loc_y'][trajectory_rows[0]:trajectory_rows[-1] + 1])  # 一条轨迹的坐标集合

        '''构建图模型'''
        prfx = []  # 轨迹前缀
        co_flag1 = 1
        '''遍历每个轨迹位置点'''
        for i in range(0, len(X)):
            x, y = float(X[i]), float(Y[i])
            trajectory_coords.append((x, y))
            user_coords.append((x, y))
            # 起始节点的前缀为空
            if prfx == []:
                '''开始节点点集'''
                if (x, y) not in node_start:
                    node_start[(x, y)] = 1
                else:
                    node_start[(x, y)] += 1
                prfx.append((x, y))
            elif i == len(X) - 1:
                '''结束节点点集'''
                if (x, y) not in node_end.keys():
                    end_prfx_add_co = prfx
                    # 结束节点与前一个点不同，前缀更新
                    if (x, y) != prfx[-1]:
                        end_prfx_add_co.append((x, y))
                    node_end[(x, y)] = [[end_prfx_add_co, 1, 0]]
                else:
                    # 当前节点与前一个结点相同，前缀不更新，停留时间加一
                    if (x, y) == prfx[-1]:
                        co = co_list[(x, y)][-1]
                        co[2] += 1
                        end_prfx_add_co = prfx
                    else:
                        # 当前节点与前一个结点不同
                        end_prfx_add_co = prfx
                        end_prfx_add_co.append((x, y))  # 将该坐标加入前缀信息
                    # 遍历此节点前缀信息
                    end_co_attribute_set = node_end[(x, y)]
                    end_flag = 1  # 前缀信息异同标志位
                    for co_attribute in end_co_attribute_set:
                        # 如果查到该前缀信息，co_flag = 0，前缀不更新，count加一
                        if co_attribute[0] == end_prfx_add_co:
                            co_attribute[1] += 1
                            end_flag = 0
                            break
                    # 如果没有查到该前缀信息，co_flag = 1，前缀更新
                    if end_flag:
                        node_end[(x, y)].append([end_prfx_add_co, 1, 0])

            else:
                '''中间点点集'''

                if (x, y) not in co_list.keys():
                    co_list[(x, y)] = [[prfx[:], 1, 0]]
                    # 第一个中间节点和开始节点相同时，停留时间加一，co_flag1保证只执行一次
                    if trajectory_coords[0] == trajectory_coords[1] and co_flag1:
                        #co_list[(x, y)] = [[prfx[:], 1, 1]]
                        co = co_list[trajectory_coords[0]][0]
                        co[2] = 1
                        co_flag1 = 0
                    else:
                        prfx.append((x, y))
                        prfx_add_co = prfx
                        co_list[(x, y)] = [[prfx_add_co[:], 1, 0]]
                else:
                    # 当前节点与前一个结点相同
                    if (x, y) == prfx[-1]:
                        co = co_list[(x, y)][-1]
                        co[2] += 1
                    else:
                        prfx.append((x, y))  # 将该坐标加入前缀信息
                        # 遍历此节点前缀信息
                        co_attribute_set = co_list[(x, y)]
                        co_flag = 1  # 前缀信息不同标志位
                        for co_attribute in co_attribute_set:
                            # 如果查到该前缀信息，co_flag = 0，前缀不更新，count加一
                            if co_attribute[0] == prfx:
                                co_attribute[1] += 1
                                co_flag = 0
                                break
                        # 如果没有查到该前缀信息，co_flag = 1，前缀更新
                        if co_flag:
                            reprfx_add_co = prfx
                            co_list[(x, y)].append([reprfx_add_co[:], 1, 0])
        # print('第{}条轨迹坐标：{}'.format(id, trajectory_coords))
        rawlist.append(trajectory_coords)
    # print(rawlist)


    merged_rawlist = user_coords
    node_dict = generate_occurrence_number(merged_rawlist)  # 用于存储每个点以及其出现次数
    # print(node_dict)

    coords = set(user_coords)
    # print(coords)

    #GenerateExcel.Generateexcel(node_start, co_list, node_end, userid)

    # print('* 开始节点点集：{}'.format(node_start))
    # print('* 中间节点点集：')
    # for keys, values in co_list.items():
    #     print(keys)
    #     print(values)
    # # print('* 中间节点点集：{}'.format(co_list))
    # print('* 结束节点点集：{}'.format(node_end))
    #print('* 轨迹点坐标集：{}'.format(coords))
    # # print('\n')

    return node_start, node_end, co_list, coords
    #return node_start, node_end, co_list, coords

if __name__ == "__main__":
    """构建图模型"""
    csv_path = 'C:\WorkSpace\Accepted\griddata.csv'
    csv_file = pd.read_csv(csv_path, dtype=str)

    users = list(set(csv_file['user_id']))
    users.sort(key=list(csv_file['user_id']).index)

    # 创建文件夹
    if not os.path.exists('Users'):
        print('no users')
        os.mkdir('Users')
    # 创建Excel表
    for user_id in users:
        user_rows = csv_file[csv_file.user_id == user_id].index.tolist()
        graph_generate(csv_file, user_rows)


