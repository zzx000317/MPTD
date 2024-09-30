import pandas as pd
from Data_process import data_process
from GraphModel import graph_generate
from DP_addnoise import get_privacy_degree
from DP_addnoise import addnoise_to_transnumber
from Transition import get_M1_transnumber
from GenerateExcel import Generateexcel
from Transition import get_M2_transnumber
from Transition import get_start_node_score
from MarkovModel import generate_transition_matrix
from MarkovModel import generate_syntrajectory
from DP_mechanism import exp_mech


if __name__ == "__main__":

    """参数赋值"""
    sample = 15
    min_stay_time = 60
    min_stay_speed = 1
    budget = 10
    sensitivity = 1
    epsilon_b = 1
    eplison2 = 1
    theta2 = 5
    Generalization_number = 10


    """网格映射"""
    data_process(sample, min_stay_time, min_stay_speed)

    """构建图模型"""
    csv_path = 'C:\WorkSpace\Accepted(v2)\griddata.csv'
    csv_file = pd.read_csv(csv_path, dtype=str)

    users = list(set(csv_file['user_id']))
    users.sort(key=list(csv_file['user_id']).index)

    for user_id in users:
        print("用户" + str(user_id) + "----------------------------")
        user_rows = csv_file[csv_file.user_id == user_id].index.tolist()
        node_start, node_end, co_list, coords = graph_generate(csv_file, user_rows)

        # """测试"""
        # Tnum = 0
        # for co in co_list.keys():
        #     co_mid = co_list[co]
        #     for i in range(len(co_mid)):
        #         if co == co_mid[i][0][-1]:
        #             Tnum += 1
        #         else:
        #             print(co)
        #             print(i)
        # print(Tnum)


        """确定状态空间"""
        states = list(coords) + [(-1, -1)]
        # print("{}的状态空间: {}".format(user_id, states))
        """计算模型选择的第一个阈值"""
        theta1 = pow(2, 0.5) * eplison2 * len(states)

        """计算转移计数"""
        transnumbers = {}
        for j in states:
            count_ij= get_M1_transnumber(j, co_list, node_end)
            for transtion in count_ij.keys():
                transnumbers[transtion] = count_ij[transtion]

        """计算转移概率矩阵(加噪后)"""
        transition_matrix = {}
        for sign in range(2):
            degrees, min_deg, max_deg = get_privacy_degree(sign, states, co_list, node_end)
            transcounts = addnoise_to_transnumber(sign, epsilon_b, states, co_list, node_end, degrees, min_deg, max_deg)
            transition_matrix[sign] = generate_transition_matrix(sign, states, transcounts)

        # print(transition_matrix)

        """计算开始节点的评分函数"""
        start_node_score = get_start_node_score(node_start, coords)

        """生成泛化轨迹"""
        for i in range(Generalization_number):
            start_state = exp_mech(start_node_score, 0.01, sensitivity)  # 选出起始结点
            generate_syntrajectory(states, transnumbers, transition_matrix, start_state, theta1, theta2)

