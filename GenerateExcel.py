import csv
import xlwt
import pandas as pd
def Generateexcel(node_start,co_list,node_end,userid):
    """
    生成数据为Excel表
    :param node_start: 开始节点点集
    :param co_list: 中间节点点集
    :param node_end: 结束节点点集
    :param userid: 用户的序号
    :return:
    """

    wb = xlwt.Workbook(encoding='utf-8', style_compression=0)  # 一个实例
    sheet1 = wb.add_sheet("开始节点", cell_overwrite_ok=True)  # 创建工作簿
    sheet2 = wb.add_sheet("中间节点", cell_overwrite_ok=True)  # 创建工作簿
    sheet3 = wb.add_sheet("结束节点", cell_overwrite_ok=True)  # 创建工作簿

    # 开始节点
    title1 = ('开始节点', '出现次数')  # 设置开始节点表头
    for i in range(0, len(title1)):
        sheet1.write(0, i, title1[i])
    i = 1
    for key in node_start:
        sheet1.write(i, 0, str(key))
        sheet1.write(i, 1, str(node_start[key]))
        i += 1

    # 中间节点
    title2 = ('中间节点', '前缀', '出现次数', '停留时间')  # 设置中间节点表头
    for i in range(0, len(title2)):
        sheet2.write(0, i, title2[i])
    a = 1
    for key in co_list:
        if len(co_list[key]) > 1:
            for element in co_list[key]:
                sheet2.write(a, 0, str(key))  # 中间节点
                sheet2.write(a, 1, str(element[0]))  # 前缀
                sheet2.write(a, 2, str(element[1]))  # 出现次数
                sheet2.write(a, 3, str(element[2]))  # 停留时间
                a += 1
        else:
            sheet2.write(a, 0, str(key))  # 中间节点
            sheet2.write(a, 1, str(co_list[key][0][0]))  # 前缀
            sheet2.write(a, 2, str(co_list[key][0][1]))  # 出现次数
            sheet2.write(a, 3, str(co_list[key][0][2]))  # 停留时间
            a += 1

    # 结束节点
    title3 = ('结束节点', '前缀', '出现次数', '停留时间')  # 设置结束节点表头
    for i in range(0, len(title3)):
        sheet3.write(0, i, title3[i])
    j = 1
    for key in node_end:
        if len(node_end[key]) > 1:
            for element in node_end[key]:
                sheet3.write(j, 0, str(key))  # 结束节点
                sheet3.write(j, 1, str(element[0]))  # 前缀
                sheet3.write(j, 2, str(element[1]))  # 出现次数
                sheet3.write(j, 3, str(element[2]))  # 停留时间
                j += 1
        else:
            sheet3.write(j, 0, str(key))  # 结束节点
            sheet3.write(j, 1, str(node_end[key][0][0]))  # 前缀
            sheet3.write(j, 2, str(node_end[key][0][1]))  # 出现次数
            sheet3.write(j, 3, str(node_end[key][0][2]))  # 停留时间
            j += 1

    wb.save("Users/user" + str(userid) + ".xls")
