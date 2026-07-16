import numpy as np
import matplotlib.pyplot as plt
from sko.GA import GA
# scikit-opt

def f(x):
    return x[0] * np.sin(10 * np.pi * x[0]) + 2.0


ga_sko = GA(
    func=f,  # 最小化目标函数
    n_dim=1,  # 变量维度
    size_pop=100,  # 种群大小
    max_iter=200,  # 迭代次数
    prob_mut=0.05,  # 变异概率
    lb=[-1],  # 下界
    ub=[3],  # 上界
    precision=1e-5,  # 精度
)


# 3. 运行并记录每代最优值
best_sko = []
for _ in range(ga_sko.max_iter):
    ga_sko.run(1)
    best_sko.append(ga_sko.best_y)  # 记录每代最优适应度


# 4. 输出结果
best_x_sko = ga_sko.best_x[0]
best_f_sko = ga_sko.best_y
print(f"sko-GA最优解：x = {best_x_sko:.4f}, f(x) = {best_f_sko[0]:.4f}")

plt.plot(best_sko, label="sko-GA")
plt.xlabel("Generation")
plt.ylabel("Best Fitness")
plt.show()

