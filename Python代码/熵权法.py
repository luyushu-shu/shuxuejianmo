import numpy as np
def mylog(p):
    n = len(p) #获取向量p的长度
    lnp = np.zeros(n) #创建一个长度为n的零向量
    for i in range(n):
        if p[i] == 0:
            lnp[i] = 0
        else:
            #log(),求对数
            #log（），log2(),log10()
            lnp[i] = np.log(p[i])
    return lnp

# 定义一个指标矩阵X
X = np.array([[5/7, 1/3, 2/3], [0, 1, 1/3], [1, 0, 1], [3/7, 2/3, 0]])

Z = X/np.sqrt(np.sum(X**2, axis=0))

print("标准化矩阵 Z = ")
print(Z)  # 打印标准化矩阵Z

#计算熵权所需的变量和矩阵初始化
n,m = X.shape
D = np.zeros(m) # 初始化一个长度为m的数组D，用于保存每个指标的信息效用值

#计算每个指标的信息效用值
for i in range(m):
    x = Z[:,i]
    p = x/np.sum(x) #对每个指标进行归一化处理
    print(p)
    e = -np.sum(p * mylog(p))/np.log(n) #计算信息熵
    D[i] = 1 - e #计算信息效用值

W = D/np.sum(D)
print(W)