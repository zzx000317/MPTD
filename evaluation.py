import math
import numpy as np
import scipy.stats as sp
from dtw import dtw
from sklearn.metrics.pairwise import euclidean_distances
from numpy import inf
from scipy.spatial.distance import euclidean


def hausdorff_distance(raw_loc, syn_loc):
    """计算豪斯多夫距离"""
    max_distance1 = 0
    for loc1 in raw_loc:
        # lon1, lat1 = loc1.get_loc()
        lon1, lat1 = loc1[0], loc1[1]
        min_distance = 10000000
        for loc2 in syn_loc:
            # lon2, lat2 = loc2.get_loc()
            lon2, lat2 = loc2[0], loc2[1]
            distance = math.hypot(abs(lon1 - lon2) / 0.0000115, abs(lat1 - lat2) / 0.00001)
            if distance < min_distance:
                min_distance = distance
        if min_distance > max_distance1:
            max_distance1 = min_distance
    max_distance2 = 0
    for loc1 in syn_loc:
        # lon1, lat1 = loc1.get_loc()
        lon1, lat1 = loc1[0], loc1[1]
        min_distance = 1000000
        for loc2 in raw_loc:
            # lon2, lat2 = loc2.get_loc()
            lon2, lat2 = loc2[0], loc2[1]
            distance = math.hypot(abs(lon1 - lon2) / 0.0000115, abs(lat1 - lat2) / 0.00001)
            if distance < min_distance:
                min_distance = distance
        if min_distance > max_distance2:
            max_distance2 = min_distance
    hausdorff_distance = max(max_distance1, max_distance2)
    return round(hausdorff_distance, 4)


# js散度
def JS_divergence(cell_probs, syn_cell_probs):
    p = np.asarray(cell_probs)
    q = np.asarray(syn_cell_probs)
    M = (p + q) / 2
    js = 0.5 * sp.entropy(p, M) + 0.5 * sp.entropy(q, M)

    return round(js, 4)


# 肯德尔系数
def Kendall(cell_probs, syn_cell_probs):
    tau, p_value = sp.kendalltau(cell_probs, syn_cell_probs)
    return round(tau, 4), round(p_value, 4)


def DTW_value(raw_trace, private_new_trace, beta):
    """
    检测抵御去匿名攻击的能力
    使用DTW作为指标，beta为相似度阈值，大于该阈值则判定为相似轨迹 k+=1
    beta的值为0.00001*米
    k越大表示安全程度越高（与扰动轨迹相似的轨迹多）
    取所有扰动轨迹中的最小k值作为最后的指标
    """
    min_k = 10000
    for new_user in private_new_trace:
        print('计算轨迹' + str(new_user) + 'DTW')
        new_pos_list = private_new_trace[new_user]  # 取得该用户轨迹列表
        trace_x = []
        k = 0
        for i in range(len(new_pos_list)):
            x, y = new_pos_list[i].get_lon(), new_pos_list[i].get_lat()
            co = [x, y]
            co_np = np.array(co).reshape(-1, 2)
            trace_x.append(co_np)

        for old_user in raw_trace:
            raw_pos_list = raw_trace[old_user]
            trace_y = []
            for j in range(len(raw_pos_list)):
                x, y = raw_pos_list[j].get_lon(), raw_pos_list[j].get_lat()
                co = [x, y]
                co_np = np.array(co).reshape(-1, 2)
                trace_y.append(co_np)
            dist, cost, acc, path = dtw(trace_x, trace_y, euclidean_distances, w=inf, s=1.0)
            if dist >= beta:
                k += 1

        if k < min_k:
            min_k = k

    return min_k


# 计算序列组成单元之间的欧式距离(手写)
def Euclid_Distance(w1, w2):
    d = np.sqrt(np.square(w1[0]-w2[0])+np.square(w1[1]-w2[1]))
    return d
# 欧氏距离（自带类库）
def distance_func(a, b):
    return euclidean(a, b)

# DTW距离
def DTW_distance(s1, s2):
    m = len(s1)
    n = len(s2)

    # 构建二维dp矩阵,存储对应每个子问题的最小距离
    dp = [[0] * n for _ in range(m)]

    # 起始条件,计算单个字符与一个序列的距离
    for i in range(m):
        dp[i][0] = Euclid_Distance(s1[i], s2[0])
    for j in range(n):
        dp[0][j] = Euclid_Distance(s1[0], s2[j])

    # 利用递推公式,计算每个子问题的最小距离,矩阵最右下角的元素即位最终两个序列的最小值
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = round(min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + Euclid_Distance(s1[i], s2[j]),4)
    return round(dp[-1][-1],4)

# # 递归计算计算两个曲线之间的Fréchet距离
# def frechet_distance(P, Q):
#     n = len(P)
#     m = len(Q)
#
#     # 创建一个二维数组来保存距离矩阵
#     distance_matrix = [[-1] * m for _ in range(n)]
#
#     # 递归计算Fréchet距离
#     def recursive_frechet_distance(i, j):
#         if distance_matrix[i][j] > -1:
#             return distance_matrix[i][j]
#
#         elif i == 0 and j == 0:
#             distance_matrix[i][j] = Euclid_Distance(P[0], Q[0])
#
#         elif i > 0 and j == 0:
#             distance_matrix[i][j] = max(recursive_frechet_distance(i - 1, 0), Euclid_Distance(P[i], Q[0]))
#
#         elif i == 0 and j > 0:
#             distance_matrix[i][j] = max(recursive_frechet_distance(0, j - 1), Euclid_Distance(P[0], Q[j]))
#
#         elif i > 0 and j > 0:
#             distance_matrix[i][j] = max(
#                 min(
#                     recursive_frechet_distance(i - 1, j),
#                     recursive_frechet_distance(i - 1, j - 1),
#                     recursive_frechet_distance(i, j - 1)
#                 ),
#                 Euclid_Distance(P[i], Q[j])
#             )
#
#         return distance_matrix[i][j]
#
#     # 调用递归函数计算Fréchet距离
#     return recursive_frechet_distance(n - 1, m - 1)
# 动态规划计算Frechet距离
def frechet_distance(A, B):
    n = len(A)
    m = len(B)
    distance_matrix = np.zeros((n, m))

    # 初始化距离矩阵
    for i in range(n):
        for j in range(m):
            distance_matrix[i][j] = Euclid_Distance(A[i], B[j])
    # 动态规划计算弗雷歇距离
    dp = np.zeros((n, m))
    dp[0][0] = distance_matrix[0][0]

    for i in range(1, n):
        dp[i][0] = max(dp[i-1][0], distance_matrix[i][0])

    for j in range(1, m):
        dp[0][j] = max(dp[0][j-1], distance_matrix[0][j])

    for i in range(1, n):
        for j in range(1, m):
            dp[i][j] = max(min(dp[i-1][j], dp[i-1][j-1], dp[i][j-1]), distance_matrix[i][j])

    return round(dp[n-1][m-1], 4)
#平均轨迹长度
def Mean_Track_Len(merged_list,num):

    return round(len(merged_list)/num,2)

if __name__ == "__main__":
    a=[1,3,2,4,2]
    b=[0,3,4,2,2]
    vec1 = np.array(a)
    vec2 = np.array(b)
    # x1=(1,1)
    # x2=(2,2)
    # print(euclidean(x1,x2))

    l1 = [(2, 1), (2, 1), (4, 1), (4, 1), (2, 1)]
    l2 = [(5, 2), (5, 2), (4, 3), (7, 1), (8, 8)]
    A = [(0, 0), (1, 2), (2, 1), (3, 3)]
    B = [(0, 1), (1, 0), (2, 2), (3, 3)]
    # dtw = DTW_distance(l1, l2)
    # print(dtw)
    frechet = frechet_distance(A, B)
    print(frechet)