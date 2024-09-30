import os
import math
import csv


def data_process(sample, min_stay_time, min_stay_speed):
    """数据处理：将真实轨迹数据转换为网格轨迹数据"""

    '''创建存储网格数据的csv文件'''
    f = open('C:\WorkSpace\Accepted(v2)\griddata.csv', "w", newline="", encoding='utf-8')
    csv_writer = csv.writer(f)
    csv_writer.writerow(["user_id", "trajectory_id", "loc_x", "loc_y"])

    root_path = r"C:\WorkSpace\dataset\Geolife Trajectories 1.3\Data"
    users = os.listdir(root_path)  # 用户目录

    '''遍历所有用户'''
    for user_id in users[0:5]:
        print('用户{}的轨迹信息：'.format(user_id))
        trajectory_path = os.path.join(root_path, user_id, "Trajectory")
        trajectorys = os.listdir(trajectory_path)  # 轨迹目录(一个用户)

        boundary = get_boundary(trajectory_path, sample)   # 用户轨迹边界值
        grid_info = get_grid_info(boundary, min_stay_time, min_stay_speed)   # 用户网格图信息
        print('* boundary={}'.format(boundary))
        print('* grid_info={}'.format(grid_info))

        '''遍历一个用户的所有轨迹'''
        print(len(trajectorys))
        for item in trajectorys[2:int(len(trajectorys)/7):3]:
            item_title = item.split('.')
            item_path = os.path.join(trajectory_path, item)  # 轨迹路径（将处理单位设为一条轨迹）
            with open(item_path, 'r+') as fp:
                '''遍历一条轨迹的所有位置点'''
                for point in fp.readlines()[8::int(sample / 5 - 1)]:
                    context_list = point.split(',')
                    lat = float(context_list[0])  # 纬度
                    lon = float(context_list[1])  # 经度
                    '''经纬度映射坐标'''
                    x, y = loc_map(lat, lon, grid_info, boundary)
                    # print('lat={}'.format(lat) + ', lon={}'.format(lon))
                    # print('x={}'.format(x) + ', y={}'.format(y))
                    csv_writer.writerow([user_id, item_title[0], x, y])

    f.close()


def get_boundary(trajectory_path, sample):
    """获取用户轨迹的边界值"""

    min_lat, max_lat, min_lon, max_lon = 90, 0, 180, 0  # 初始化最值
    trajectorys = os.listdir(trajectory_path)  # 轨迹目录（一个用户）

    '''遍历一个用户的所有轨迹（可指定轨迹数）'''
    for item in trajectorys[2:int(len(trajectorys)/7):3]:
        item_path = os.path.join(trajectory_path, item)  # 轨迹路径（将处理单位设为一条轨迹）
        with open(item_path, 'r+') as fp:
            for point in fp.readlines()[8::int(sample / 5 - 1)]:
                context_list = point.split(',')
                lat = float(context_list[0])
                lon = float(context_list[1])
                if lat < min_lat:
                    min_lat = lat
                if lat > max_lat:
                    max_lat = lat
                if lon < min_lon:
                    min_lon = lon
                if lon > max_lon:
                    max_lon = lon

    boundary = [min_lat, max_lat, min_lon, max_lon]

    return boundary


def get_grid_info(boundary, min_stay_time, min_stay_speed):
    """获得网格的基本信息"""

    '''每个单元格的长度'''
    cell_length = min_stay_time * min_stay_speed

    '''经纬度对应的总长度m'''
    lat_length = math.ceil((boundary[1] - boundary[0]) / 0.000001)
    lon_length = math.ceil((boundary[3] - boundary[2]) / 0.000001)

    '''x轴与y轴方向上的单元格数量(在原有基础上加4个)'''
    x_axis_cell_count = lat_length // cell_length
    y_axis_cell_count = lon_length // cell_length

    '''网格信息元组保存网格信息'''
    grid_info = [cell_length, lat_length, lon_length, x_axis_cell_count, y_axis_cell_count]

    return grid_info


def loc_map(lat, lon, grid_info, boundary):
    """将符合时间判断的轨迹点映射到单元格中心"""

    cell_length = grid_info[0]

    x = (lat - boundary[0]) / 0.000001 // cell_length + 1
    y = (lon - boundary[2]) / 0.000001 // cell_length + 1

    return x, y


if __name__ == "__main__":

    """参数赋值"""
    sample = 40
    min_stay_time = 60
    min_stay_speed = 30
    """网格映射"""
    data_process(sample, min_stay_time, min_stay_speed)
