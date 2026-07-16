import matplotlib.pyplot as plt
import numpy as np

POP_SIZE = 100  # 种群大小
DNA_SIZE = 1  # 实数编码，单变量
MAX_ITER = 200  # 迭代次数
CROSS_RATE = 0.8  # 交叉概率
MUTATION_RATE = 0.05  # 变异概率
MUTATION_STD = 0.01  # 变异幅度
LB, UB = -1, 3  # 变量范围
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

def f(x):
    return x * np.sin(10 * np.pi * x) + 2.0


# 3. 初始化种群（实数编码）
def init_pop():
    return np.random.uniform(LB, UB, size=(POP_SIZE, DNA_SIZE))


# 4. 适应度计算（最小化问题：适应度=1/(1+目标值)，避免负值影响选择）
def get_fitness(pop):
    values = np.array([f(x[0]) for x in pop])
    return 1 / (1 + values)  # 目标值越小，适应度越高


# 5. 选择算子
def select(pop, fitness, elite_size=2):
    # 精英保留
    elite_idx = np.argsort([f(x[0]) for x in pop])[:elite_size]  # 选目标值最小的2个
    elites = pop[elite_idx]

    # 锦标赛选择：随机选3个个体，取适应度最高的
    selected = []
    for _ in range(POP_SIZE - elite_size):
        candidates_idx = np.random.choice(POP_SIZE, size=3, replace=False)
        candidates = pop[candidates_idx]
        candidates_fitness = fitness[candidates_idx]
        selected.append(candidates[np.argmax(candidates_fitness)])  # 选适应度最高的

    return np.vstack([elites, np.array(selected)])


# 6. 交叉算子
def crossover(parent, pop):
    if np.random.rand() < CROSS_RATE:
        mate = pop[np.random.randint(POP_SIZE)]  # 随机选配偶
        alpha = np.random.rand()  # 混合系数
        parent = alpha * parent + (1 - alpha) * mate  # 线性组合
    return parent


# 7. 变异算子
def mutate(child):
    if np.random.rand() < MUTATION_RATE:
        child += np.random.normal(0, MUTATION_STD, size=DNA_SIZE)  # 加高斯噪声
        child = np.clip(child, LB, UB)  # 确保在范围内
    return child


# 8. 主循环
pop = init_pop()
best_manual = []  # 记录每代最优值

for _ in range(MAX_ITER):
    # 计算当前种群的目标值
    current_values = np.array([f(x[0]) for x in pop])
    best_manual.append(np.min(current_values))  # 记录最小目标值

    # 选择
    fitness = get_fitness(pop)
    pop = select(pop, fitness)
    pop_copy = pop.copy()  # 复制种群用于交叉

    # 交叉和变异（跳过精英个体）
    for i in range(2, POP_SIZE):  # 前2个是精英，不处理
        pop[i] = crossover(pop[i], pop_copy)
        pop[i] = mutate(pop[i])

final_values = np.array([f(x[0]) for x in pop])
best_x_manual = pop[np.argmin(final_values)][0]
best_f_manual = np.min(final_values)
print(f"手动GA最优解：x = {best_x_manual:.4f}, f(x) = {best_f_manual:.4f}")
plt.plot(best_manual, label="Manual GA")
plt.xlabel("Generation")
plt.ylabel("Best Fitness")
plt.show()