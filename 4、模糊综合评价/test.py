# 在Python中，np.dot 是 NumPy 库中的一个函数，主要用于计算两个数组的点积。
# 基础语法：np.dot(a, b)
# # 1. 向量的点积
# import numpy as np
# a = np.array([1, 2, 3])
# b = np.array([4, 5, 6])
# print(np.dot(a, b))

# # 2. 矩阵与向量的乘积
# import numpy as np
# a = np.array([[1, 2], [3, 4]])
# b = np.array([5, 6])
# print(np.dot(a, b))

# 3. 矩阵的乘积
import numpy as np
a = np.array([[1, 2],
              [3, 4]])
b = np.array([[5, 6],
              [7, 8]])
print(np.dot(a, b))