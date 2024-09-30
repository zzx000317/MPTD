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
import evaluation as el
from computeProbs import *
from sklearn import metrics as mt
from collections import Counter
import time


t1 = time.time()

"""参数赋值"""
sensitivity = 1
epsilon_budget = [1.6]
# epsilon_budget = [0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2, 0.2]
#eplison2 = 0.2



theta2 = 5
Generalization_number = 100

data = pd.read_csv("griddata.csv")
users = list(set(data['user_id']))
users.sort(key=list(data['user_id']).index)
# loc_x=np.array(data[["loc_x","loc_y"]])
# print(users)
for user_id in users:
    print("用户" + str(user_id) + "----------------------------")
    user_rows = data[data.user_id == user_id].index.tolist()
    node_start, node_end, co_list, coords, RawList, merged_RawList, node_dict = graph_generate(data, user_rows)  # 原始轨迹访问频率
    trans_mode = Transfer_mode(RawList)  # 原始轨迹转移模式
    Stay_Times = stay_time(RawList)  # 原始轨迹停留时间
    # print(RawList)
    # print(node_dict)
    # Transfer_mode(RawList)
    # stay_time(RawList)

    for epsilon_b in epsilon_budget:
        eplison2 = epsilon_b
        print(epsilon_b)

        """确定状态空间"""
        states = list(coords) + [(-1, -1)]
        """计算模型选择的第一个阈值"""
        theta1 = pow(2, 0.5) * eplison2 * len(states)

        """计算转移计数"""
        transnumbers = {}
        for j in states:
            count_ij = get_M1_transnumber(j, co_list, node_end)
            for transtion in count_ij.keys():
                transnumbers[transtion] = count_ij[transtion]

        """计算转移概率矩阵(加噪后)"""
        transition_matrix = {}
        for sign in range(2):
            degrees, min_deg, max_deg = get_privacy_degree(sign, states, co_list, node_end)
            transcounts = addnoise_to_transnumber(sign, epsilon_b, states, co_list, node_end, degrees, min_deg, max_deg)
            transition_matrix[sign] = generate_transition_matrix(sign, states, transcounts)
        """计算开始节点的评分函数"""
        start_node_score = get_start_node_score(node_start, coords)

        """轨迹合成"""
        merged_SynList = []  # 将所有合成轨迹合成为一个表
        SynList = []  # 此表中每个元素都是单次轨迹
        for i in range(Generalization_number):
            start_state = exp_mech(start_node_score, 0.01, sensitivity)  # 选出起始结点
            # 生成合成轨迹
            limit = el.Mean_Track_Len(merged_RawList, len(RawList)) * 1.1
            syn_list = generate_syntrajectory(states, transnumbers, transition_matrix, start_state, theta1, theta2, limit)  # 合成轨迹
            SynList.append(syn_list)
            merged_SynList += syn_list

        syn_node_dict = generate_occurrence_number(merged_SynList)  # 合成轨迹访问频率
        syn_trans_mode = Transfer_mode(SynList)  # 合成轨迹转移模式
        syn_Stay_Times = stay_time(SynList)  # 合成轨迹停留时间
        # print(SynList)
        # print(syn_node_dict)

        cell_probs, syn_cell_probs = get_cell_probs(node_dict, syn_node_dict)
        trans_counts, syn_trans_counts = get_trans_counts(trans_mode, syn_trans_mode)
        st_counts, syn_st_counts = get_stayTime_counts(Stay_Times, syn_Stay_Times)
        # print(st_counts)
        # print(syn_st_counts)
        # print('* cell_probs：{}'.format(cell_probs))
        # print('* syn_cell_probs：{}'.format(syn_cell_probs))

        """轨迹对比"""
        # # 计算豪斯多夫距离
        # H = []
        # for Slist in SynList:
        #     a=[]
        #     for Rlist in RawList:
        #         HD=el.hausdorff_distance(Rlist,Slist)
        #         a.append(HD)
        #     m=min(a) # 求每组的最小值
        #     H.append(m) # 将每组的最小值存入列表再求其平均值作为最终结果
        # average_HD = round(sum(H)/len(SynList),4)
        # print("豪斯多夫距离"+str(average_HD))

        #计算DTW距离
        D=[]
        for Slist in SynList:
            a=[]
            for Rlist in RawList:
                DTW=el.DTW_distance(Rlist,Slist)
                a.append(DTW)
            m=min(a)
            D.append(m)

        average_DTW = round(sum(D)/len(SynList),4)
        print("DTW距离"+str(average_DTW))

        # 计算弗雷歇距离
        F=[]
        for Slist in SynList:
            a=[]
            for Rlist in RawList:
                Frechet =el.frechet_distance(Rlist,Slist)
                a.append(Frechet)
            m=min(a)
            F.append(m)
        average_Frechet = round(sum(F)/len(SynList),4)
        print("弗雷歇距离"+str(average_Frechet))



        # 频繁模式
        # print("原始轨迹频繁模式" + str(node_dict))
        # print("合成轨迹频繁模式" + str(syn_node_dict))
        # 频繁模式的指标计算：
        js = el.JS_divergence(cell_probs, syn_cell_probs)  # js散度
        print("频繁模式js散度："+str(js))
        # tau, p_value = el.Kendall(cell_probs, syn_cell_probs) # 肯德尔系数
        # print("频繁模式tau："+str(tau))
        # print("频繁模式p_value:"+str(p_value))
        # NMI = round(mt.normalized_mutual_info_score(cell_probs, syn_cell_probs), 4)  # 互信息系数
        # print("频繁模式NMI:"+str(NMI))

        # 转移模式
        # print("原始轨迹转移模式"+str(trans_mode))
        # print("合成轨迹转移模式"+str(syn_trans_mode))
        # 转移模式指标计算
        trans_js=el.JS_divergence(trans_counts,syn_trans_counts)
        print("转移模式js散度：" + str(trans_js))
        # trans_tau,trans_pvalue=el.Kendall(trans_counts,syn_trans_counts)
        # print("转移模式tau："+str(trans_tau))
        # trans_NMI = round(mt.normalized_mutual_info_score(trans_counts,syn_trans_counts), 4)
        # print("转移模式NMI:"+str(trans_NMI))

        # 停留时间
        # print("原始轨迹停留时间"+str(Stay_Times))
        # print("合成轨迹停留时间"+str(syn_Stay_Times))
        # 停留时间指标计算
        st_js=el.JS_divergence(st_counts, syn_st_counts)
        print("停留时间js散度：" + str(st_js))
        # st_tau,st_pvaule=el.Kendall(st_counts, syn_st_counts)
        # print("停留时间tau：" + str(st_tau))
        # st_NMI = round(mt.normalized_mutual_info_score(st_counts, syn_st_counts),4)
        # print("停留时间NMI：" + str(st_NMI))


        # 轨迹平均长度
        print('原始轨迹平均长度' + format(el.Mean_Track_Len(merged_RawList, len(RawList))))
        print('合成轨迹平均长度' + format(el.Mean_Track_Len(merged_SynList, len(SynList))))

t2 = time.time()
print(t2-t1)

