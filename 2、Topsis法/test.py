# 如果你想从用户输入中获取值，可以使用内置函数输入input()。这个函数允许用户在程序执行时提供输入。
# input()返回一个字符串，你可能需要根数据需要将其转换为其他数据类型。
# 如果你需要将转换为其他数据类型，例如总数，你可以使用int()函数，如果想转换成零点数，可以使用float()
# 如果输入的是表达式，可以使用eval()
# n = eval(input('n ='))
# m=n+n+n
# print(type(n))
# print(m)


# # split('分隔符',分割次数)方法用于将字符串分割成子字符串，并返回一个包含这些子字符串的列表。
# kind=input('请输入内容:')
# newkind = kind.split()
# print(kind)
# print(newkind)


# # numpy.zeros函数用于创建一个指定形状（shape）的数组，并将所有元素初始化为零。它的语法如下：
# # numpy.zeros(shape, dtype=float, order='C")
# # 参数说明：
# # shape：数组的形状，可以是一个整数，例如（3）表示一维数组，或者是一个整数元组，例如(2，3）表示二维数组。必须指定。
# # dtype：数组的数据类型，可选参数，默认为float。可以设置为其他数据类型，例如int、complex 等。
# # order：数组在内存中的存储顺序，可选参数，取值为'C'（按行存储）或'F'（按列存储）。默认为'C'。
# import numpy as np
# A = np.zeros((2,3))
# print(A)


# # 在Python中，for循环用于迭代（遍历）序列（如列表、元组、字符串）或其他可迭代对象的元素。for循环的基本语法如下。
# # for 变量 in 可迭代对象:
# #     在这里执行循环体的代码
# # 在每次选代中，变量都会取可迭代对象中的下一个值。当可迭代对象中的所有值都被取出后，循环终止。
# fruits = ['apple', 'orange', 'banana']
# for fruit in fruits:
#     print(fruit)

# for i in [0,1,2,3,4]:
#     print(i)


# # 在Python中，range()函数用于生成一个包合指定范围内数字的不可变序列。它的基本语法如下：
# # range(start, stop, step)
# # 参数说明：
# # start（可选）：序列起始值，默认为0。
# # stop：序列终止值（不包含在序列中）。
# # step（可选）：步长，默认为 1。
# for i in range(5):
#     print(i)

# for i in range(0,10,2):
#     print(i)


# # 在Python中，map(function, iterable)函数用于将指定函数应用于给定可迭代对象（如列表、元组等）的每个元素，并返回一个新的迭代器
# # 参数说明：
# # function：一个函数，用来对 iterable 中的每个元素进行操作。
# # iterable：一个可迭代对象（如列表、元组、集合等）。
# # 假设A[i]是一个包含字符串的列表
# A_i_str = ['1.0','2.0','3.0']
# print(A_i_str)
#
# # 使用 map 和 float 进行转换
# A_i_float = list(map(float, A_i_str))
# # 打印转换后的结果
# print(A_i_float)


# # A[行范围,列范围]用于从数组中提取指定的行和列
# import numpy as np
# A = np.array([(1,2,3),
#               (4,5,6),
#               (7,8,9)])
# print(A[0])
# print(A[1])
# print(A[1,:])
# print(A[:,1])


# # 在print()中，{}可用作占位符，搭配.format() 方法插入变量
# fruit = '苹果'
# price = 3.4
# print('商品名称：fruit，单价price元/斤')



# # 在 Python中，函数的基本语法如下：
# # def function_name(parameters):
# #     函数体，包含一系列操作
# #     可选：return语句，用于返回一个值
# # 参数说明：
# # def：是定义函数的关键字。
# # function_name：是函数的名称，遵循标识符的命名规则。
# # parameters：是函数的参数，可以是零个或多个。多个参数之间用逗号分隔。
# # 函数体：包含一系列操作的代码块。Python使用缩进来表示代码块。
# # return：是一个可选的关键字，用于在函数执行结束时返回一个值给调用方。
# # 下面是一个简单的函数示例，它接受两个参数并返回它们的和：
# def add_numbers(a, b):
#     result =a+b
#     return result
# # 你可以调用这个函数并获取结果：
# sum_result = add_numbers(3,5)
# print(sum_result) # 输出 8


# # ans = [[(maxx-e)] for e in x]这是一个列表推导式（List Comprehension)的语法。
# # 列表推导式是一种简洁的方式来创建列表，它允许你通过一行代码生成一个新的列表。
# # for e in x：这是一个迭代语句，表示对于列表x中的每个元素，用变量e表示当前元素。
# # (maxx-e)：这是一个表达式，表示对每个元素e计算maxx-e的值。
# # [...]：这是列表推导式的语法，表示将括号内的表达式的结果添加到列表中。
# # 整体上，这个列表推导式的作用是遍历列表x中的每个元素，对每个元素计算maxx－e，并将结果构建成一个新的列表 ans。
# # 举个例子，如果 x 是[1，2，3]而 maxx 是 5，那么执行这个列表推导式后，ans将成为[[4]，[3]，[2]]。
# x=[1, 2, 3]
# maxx = 5
# ans = [[maxx - e] for e in x]
# print(ans)


# # append是Python列表对象的一个方法，用于在列表的末尾添加一个元素。它的语法如下：
# # list.append(element)
# # list：是你要修改的列表，可以是一个已经存在的列表。
# # append：是列表对象的方法，用于在列表末尾添加元素。
# # element：是要添加的元素，可以是任何合法的Python数据类型，包括数字、字符串、列表等。示例如下
# my_list = [1, 2, 3]
# my_list.append(4)
# print(my_list)


# # Reshape函数是用于改变数组形状的函数。它允许你将数组重新组织成不同的形状，而不改变数组中的数据。
# # 当一个数字为-1时，表示该维度的大小由系统自动推导，以匹配总元素数量与另一个维度共同确定的新形状。
# # 所以reshape（-1，1)其实就代表着把数组转换成列向量的意思
# import numpy as np
# #创建一个一维数组
# arr = np.array([1, 2, 3, 4, 5, 6])
# # 将一维数组reshape成二维数组
# reshaped_arr = arr.reshape(2, -1)
# print("原始数组:")
# print(arr)
# print("\n转换后的数组:")
# print(reshaped_arr)


# # np.hstack是 NumPy 库中的一个函数
# # 用于在水平方向（沿着列）将多个数组堆叠在→起。hstack是"horizontal stack"（水平堆叠）的缩写。
# import numpy as np
# # 创建两个一维数组
# arr1 = np.array([[1], [2], [3]])
# arr2 = np.array([[4], [5], [6]])
# #将两个数组水平堆叠
# stacked_arr = np.hstack((arr1, arr2))
# print("数组1:")
# print(arr1)
# print("\n数组2:")
# print(arr2)
# print("\n水平堆叠后的数组:")
# print(stacked_arr)


# # astype(dtype)函数是将数组的元素类型转换为指定类型，并返回一个新的数组。
# # dtype是指定转换的类型。
# import numpy as np
# arr1 = np.array([[1], [2], [3]])
# print(arr1)
# arr2 = arr1.astype('float')
# print(arr2)


# # sqrt()用于计算平方根的函数。
# import numpy as np
# a = 9
# print(np.sqrt(a))


# # np.max(array, axis)是numpy库中的函数，用于数组的最大值计算。
# # np.max(array, axis=0)  表示沿列方向求最大值。
# # np.max(array, axis=1)  表示沿行方向求最大值。
# import numpy as np
# arr = np.array([[1, 5], [3, 2]])
# print(arr)
# print(np.max(arr,axis=0))
# print(np.max(arr))


# # np.sum(arr, axis=None, keepdims=False)用于对数组中的元素求和，可以对整个数组或指定轴（axis）进行求和。
# # arr：要进行求和的数组。
# # axis：指定求和的轴。（默认None：所有元素总和。0：按列求和。1：按行求和）
# # keepdims：是否保留求和后的维度。（默认False：压缩被求和的维度。True：保留被求和的维度，但把它的长度变为1）
# import numpy as np
# arr = np.array([[1, 2],
#                 [3, 4]])
# print(np.sum(arr))
# print(np.sum(arr,axis=0))
# print(np.sum(arr,axis=0,keepdims=True))


# # w为一个一维数组[n,1]
# # X为一个多为数组[n,m]
# # w * X的表达式会通过 NumPy 的广播机制自动扩展 w，让它的形状和另一边匹配，从而可以做逐元素运算。
# import numpy as np
# w = np.array([3, 4, 3])
# X = np.array([
#     [1, 2, 3],
#     [4, 5, 6]])
# print(X * w)


# # np.tile(A, reps) 将数组 A 沿指定方向 复制 reps 次，生成一个新的更大的数组。
# # A：原始数组（可以是一维或多维数组）
# # reps：重复次数，可以是整数或元组，控制沿各个维度的重复次数
# import numpy as np
# a = np.array([[1, 2],
#               [3, 4]])
# print(np.tile(a, (2, 3)))