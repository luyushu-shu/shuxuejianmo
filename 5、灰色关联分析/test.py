# # 在python中，np.mean（）是用来计算平均值（算术平均数）的函数。
# # 基础语法：np.mean(a, axis=None, keepdims=False)
# # a：输入数组
# # axis：指定沿哪个轴计算平均值，默认对所有元素求平均值（axis=0，对列求均值；axis=1，对行求均值）
# # keepdims：是否保留原数组的维度（默认为 False，即不保留维度）
# import numpy as np
# a = np.array([[1, 2],
#               [3, 4]])
# print(np.mean(a))
# print(np.mean(a, axis=0))
# print(np.mean(a, axis=1))