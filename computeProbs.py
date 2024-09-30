from collections import Counter


# 计算每个点在所有轨迹中的出现次数(频繁模式)
def generate_occurrence_number(merged_list):
    node_dict = {}
    for i in range(len(merged_list)):
        if merged_list[i] not in node_dict:
            if i == 0:
                node_dict[merged_list[i]] = 1
            else:
                node_dict[merged_list[i]] = 0
    for i in range(1, len(merged_list)):
        if merged_list[i - 1] != merged_list[i]:
            node_dict[merged_list[i]] += 1
    return node_dict


def get_cell_probs(node_dict, syn_node_dict):
    """获取每个单元格的访问频率,扰动前与扰动后"""
    cell_probs = []
    sum = 0
    syn_cell_probs = []
    syn_sum = 0
    for node in node_dict:
        sum += node_dict[node]
    for node in syn_node_dict:
        syn_sum += syn_node_dict[node]
    for node in node_dict:
        cell_probs.append(node_dict[node] / sum)
        if node not in syn_node_dict:
            syn_cell_probs.append(0)
        else:
            syn_cell_probs.append(syn_node_dict[node] / syn_sum)
    return cell_probs, syn_cell_probs


def get_trans_counts(trans_mode, syn_trans_mode):
    """统计转移模式value"""
    trans_counts = []
    syn_trans_counts = []
    for item in trans_mode:
        trans_counts.append(trans_mode[item])
        if item not in syn_trans_mode:
            syn_trans_counts.append(0)
        else:
            syn_trans_counts.append(syn_trans_mode[item]/2)
    return trans_counts, syn_trans_counts


def get_stayTime_counts(stay_times,syn_stay_times):
    """统计停留时间value"""
    st_counts = []
    syn_st_counts = []
    for item in stay_times:
        st_counts.append(stay_times[item])
        if item not in syn_stay_times:
            syn_st_counts.append(0)
        else:
            syn_st_counts.append(syn_stay_times[item])
    return st_counts, syn_st_counts


#
# def compute_probs(merged_list, all_list, index):
#     counter_dict = Counter(merged_list)
#     freq_list = []
#     for l in all_list:
#         freq_in = []
#         for point in l:
#             freq_in.append(counter_dict[point] / len(merged_list))
#         freq_list.append(freq_in)
#     return freq_list[index]
#

# 平均轨迹长度
def Mean_Track_Len(merged_list, num):
    return len(merged_list) / num


# 转移模式
def Transfer_mode(all_list):
    transfer_mode = {}

    # 定义一个计算一张表中转移计数的方法
    def transfer(trajectory):
        for i in range(len(trajectory) - 1):
            current_state = trajectory[i]
            next_state = trajectory[i + 1]
            if current_state == next_state:
                continue
            transition = (current_state, next_state)
            if transition in transfer_mode:
                transfer_mode[transition] += 1
            else:
                transfer_mode[transition] = 1

    for list in all_list:
        transfer(list)
    # print(transfer_count)
    return transfer_mode



# 停留时间
def stay_time(all_list):
    stay = {}

    def staytime(trajectory):
        i = 0
        while i < len(trajectory):
            current_point = trajectory[i]
            count = 1
            while i + count < len(trajectory) and trajectory[i + count] == current_point:
                count += 1
            if current_point in stay:
                stay[current_point].append(count - 1)
            else:
                stay[current_point] = [count - 1]  # value使用列表存储每次停留时间
            i += count

    for list in all_list:
        staytime(list)
    # print(stay)
    for point, times in stay.items():
        counter = Counter(times)
        # print(counter)
        most_common = max(counter.values())
        # print("最大出现次数" + str(most_common))
        A = []
        for key, value in counter.items():
            if value == most_common:
                A.append(key)  # 将出现次数相同的停留时间存入A组,取其最大值作为停留时间
        # print(max(A))
        stay[point] = max(A)
    # print(stay)
    return stay



# 测试
if __name__ == "__main__":
    list1 = [(2, 1), (2, 1), (4, 1), (4, 1), (2, 1), (2, 1), (2, 1), (4, 1), (5, 1), (2, 1)]
    list2 = [(5, 2), (5, 2), (4, 3), (7, 1), (8, 8)]
    list3 = [(2, 1), (4, 1), (5, 6), (6, 6), (6, 6)]
    list4 = [(7, 1), (8, 8), (7, 1), (2, 1), (2, 1)]
    list5 = [(7, 1), (2, 2), (2, 2), (3, 3), (6, 6)]
    # all_lists = [list1, list2, list3, list4]
    all_list = []
    all_list.append(list1)
    all_list.append(list2)
    all_list.append(list3)
    all_list.append(list4)
    all_list.append(list5)
    # Merge all lists into one
    merged_list = list1 + list2 + list3 + list4 + list5

    node_dict = generate_occurrence_number(merged_list)
    print(node_dict)
    print(Mean_Track_Len(merged_list, 5))
    Transfer_mode(all_list)
    stay_time(all_list)

    # for i in range(len(all_list)):
    #     probs = compute_probs(merged_list, all_list, i)
    #     print(probs)

    node_dict = Counter(list1 + list2)
    syn_node_dict = Counter(list3 + list4)
    node_dict = {}
    for i in range(len(merged_list)):
        if merged_list[i] not in node_dict:
            if i == 0:
                node_dict[merged_list[i]] = 1
            else:
                node_dict[merged_list[i]] = 0
    for i in range(1, len(merged_list)):
        if merged_list[i - 1] != merged_list[i]:
            node_dict[merged_list[i]] += 1
    print(node_dict)