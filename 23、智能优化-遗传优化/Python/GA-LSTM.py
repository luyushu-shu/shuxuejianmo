import numpy as np
import pandas as pd
import os
from datetime import datetime
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from deap import base, creator, tools, algorithms
from scipy.stats import bernoulli
from bitstring import BitArray
from sklearn.preprocessing import MinMaxScaler
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.layers import Dropout
from keras import optimizers
np.random.seed(1120)
import math

#显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示符号

#忽略警告
import warnings
warnings.filterwarnings("ignore")

#如果没有这个目录，则创建这个目录
if not os.path.isdir('result'):
    os.mkdir('result')


#创建网络运行需要的样本格式
def create_data(seq_len):

    # 转换成网络训练所需格式，（样本数，步长，特征数）
    X_train = np.array([data_train[i: i + seq_len, :] for i in range(data_train.shape[0] - seq_len)])  # 数据构建为（样本数，步长，特征数）形式
    y_train = np.array([data_train[i + seq_len, 0] for i in range(data_train.shape[0] - seq_len)])
    X_test = np.array([data_test[i: i + seq_len, :] for i in range(data_test.shape[0] - seq_len)])
    y_test = np.array([data_test[i + seq_len, 0] for i in range(data_test.shape[0] - seq_len)])

    return X_train, y_train, X_test, y_test

#适应度函数定义
def train_evaluate(ga_individual_solution):
    # 编码lstm参数二进制表示
    num_neurons_bits = BitArray(ga_individual_solution[0:8])   #0-256#神经元个数
    num_seq_bits = BitArray(ga_individual_solution[8:13])      #0-32 时间步长
    epoch_bits = BitArray(ga_individual_solution[13:20])       #0-128训练次数
    batch_size_bits = BitArray(ga_individual_solution[20:27])  #0-128批次大小
    learning_rate_bits = BitArray(ga_individual_solution[27:]) #0-8学习率

    # 将二进制位串（BitArray）解析为无符号整数  根据需求进行缩放
    num_neurons = num_neurons_bits.uint
    num_seq = num_seq_bits.uint
    epoch = epoch_bits.uint
    Batch_size = batch_size_bits.uint
    learning_rate = learning_rate_bits.uint *(math.exp(-9))

    print('\nNum of neurons: ', num_neurons ,'\nNum of seq' ,num_seq, '\nEpoch:', epoch ,'\nBatch size:',Batch_size ,'\nLearning rate:' ,learning_rate)

    # 如果这些参数在迭代寻参过程出现以下情况则返回0
    # 返回 0 意味着当前参数组合的适应度为0（理论最优值），但实际上这是一个无效解的惩罚标记
    # 立即终止当前个体的评估：避免在无效参数（如 num_neurons=0）上浪费计算资源
    if num_neurons < 2 or num_seq < 2 or epoch < 2 or Batch_size < 2  or learning_rate < 0:
        return 0,

    X_train, y_train, X_test, y_test=create_data(num_seq)

    #设计LSTM模型
    optimizer =optimizers.Adam(lr=learning_rate, beta_1=0.9, beta_2=0.999, amsgrad=False)#指定优化器
    model = Sequential()
    model.add(LSTM(units=num_neurons, return_sequences=False, input_shape=(X_train.shape[1], X_train.shape[2])))  # 第一层lstm，神经元数64，激活函数relu，return_sequences=True表示后面还要添加lstm则用True，否则为False
    # model.add(LSTM(units=256,activation='tanh'))#第二层lstm，神经元数64，激活函数tanh
    model.add(Dropout(0.2))  # dropout层，防止过拟合
    model.add(Dense(1))  # 全连接层
    model.compile(loss='mean_squared_error', optimizer=optimizer)  # 指定loss函数和优化器类型
    history = model.fit(X_train, y_train, epochs=epoch, batch_size=Batch_size, validation_data=(X_test, y_test), verbose=0,shuffle=False)
    # model.summary()
    # 利用训练好的模型进行预测预测
    yhat = model.predict(X_test)
    # 反归一化预测值
    yhat = scY.inverse_transform(yhat)
    # 反归一化真实值
    ytrue = scY.inverse_transform(y_test.reshape(-1, 1))
    #计算适应度函数值
    rmse = np.sqrt(mean_squared_error(ytrue, yhat))
    print('Validation Rmse: ', rmse ,'\n')

    return rmse,



#读取数据datam.csv
df=pd.read_csv('datam.csv')
date=df['datetime'] #获取date列日期数据
df=df.set_index(df['datetime'],drop=True)#把时间列作为索引
da = df.drop(columns=['datetime'])  # 去除时间列，df中还剩open,close,high,low,vol列
da = da.fillna(method='pad')#若有空值，则用上一个值填充
#把close即收盘价放到第一列,若自己的数据没有调整列，则删除下面两行
col=da.columns[[1,0,2,3,4]]
da=da[col]#调整数据列由open,close,high,low,vol列变成close,open,high,low,vol列
#获取处理后的数据
data=da.values

#显示原数据
fig = plt.figure(figsize=(15, 8), dpi=80)
plt.plot(date, data[:,0], label="origin data", color='b',lw=2.5)  #若不需要日期或者数据没有日期可改成plt.plot(data[:,0], label=" ", color='b',lw=2.5),ata[:,0]表示取close列
plt.title("origin data")
plt.xticks(range(1,len(data),50),rotation=45) #为了横坐标显示清楚，通过间隔50个显示一个值
plt.legend()
plt.savefig('result/origin_data.png')#图片保存路径
plt.show()

#划分训练集和测试集长度
X=data[:,1:]#取数据的其他特征部分,[行或行区间(:),列或列区间(:)],这里取open,high,low,vol列
Y=data[:,0].reshape(-1,1)#取需要预测的特征close列并转置
data_len=len(data)#获取数据长度
train_len=int(data_len*0.8)#取80%作为训练数据
test_len=data_len-train_len #测试集数据长度



#显示预测的特征Y的训练数据
fig = plt.figure(figsize=(15, 8), dpi=80)
plt.plot(date[:train_len], Y[:train_len], label="train data", color='b',lw=2.5)  #若不需要日期或者数据没有日期可改成plt.plot(Y[:train_len], label=" ", color='b',lw=2.5)
plt.title("origin train data")
plt.xticks(range(1,len(Y[:train_len]),50),rotation=45) #为了横坐标显示清楚，通过间隔50个显示一个值
plt.legend()
plt.savefig('result/origin_train_data.png')#图片保存路径
plt.show()

#显示预测的特征Y的测试集的数据
fig = plt.figure(figsize=(15, 8), dpi=80)
plt.plot(date[train_len:], Y[train_len:], label="test data", color='b',lw=2.5)  #若不需要日期或者数据没有日期可改成plt.plot(Y[train_len:], label=" ", color='b',lw=2.5)
plt.title("origin test data")
plt.xticks(range(1,len(Y[train_len:]),50),rotation=45) #为了横坐标显示清楚，通过间隔50个显示一个值
plt.legend()
plt.savefig('result/origin_test_data.png')#图片保存路径
plt.show()

#对te特征X和y分别进行归一化
from sklearn.preprocessing import MinMaxScaler
#声明两个归一化变量
scX = MinMaxScaler(feature_range=(0, 1))
scY = MinMaxScaler(feature_range=(0, 1))
#利用归一化变量进行归一化
scx = scX.fit_transform(X)
scy = scY.fit_transform(Y)
#把数据合并起来（前面对数据分开成X和Y了）
data=np.concatenate((scy, scx), axis=1)
#取训练数据和测试数据
data_train=data[:train_len,:]
data_test=data[train_len:,:]



##### 遗传优化算法参数设定
population_size = 6#群体大小
num_generations = 2#迭代次数
gene_length = 30 #基因长度

# 以 RMSE score做适应度函数则选择 -1.0.
creator.create('FitnessMax', base.Fitness, weights = (-1.0,))     #01. 创建适应度类：设置优化目标为最小化RMSE（通过weights=-1.0实现）
creator.create('Individual', list , fitness = creator.FitnessMax) #02. 创建个体类：每个个体是一个二进制列表，关联适应度函数

# ==================== 遗传算子配置 ====================
toolbox = base.Toolbox()#工具箱：注册参数信息:交叉,变异,保留个体,评价函数
toolbox.register('binary', bernoulli.rvs, 0.5)                #03. 编码设置：定义二进制基因生成方式（每个基因50%概率为0/1）
toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.binary, n = gene_length)   #04. 个体初始化：创建长度为gene_length的二进制个体
toolbox.register('population', tools.initRepeat, list , toolbox.individual)                             #05. 种群初始化：创建包含population_size个个体的种群

toolbox.register('mate', tools.cxOrdered)                           #06. 交叉算子：有序交叉（适合顺序敏感的参数如时间步长）
toolbox.register('mutate', tools.mutShuffleIndexes, indpb = 0.6)    #07. 变异算子：索引乱序变异（indpb=0.6表示每个基因60%概率被扰动）
toolbox.register('select', tools.selRoulette)                       #08. 选择算子：轮盘赌选择（可能因适应度差异大导致早熟）
toolbox.register('evaluate', train_evaluate)                        #09. 评价函数：绑定自定义的LSTM评估函数

population = toolbox.population(n = population_size)                      #10. 初始化种群
start_time = datetime.now()                                               #11. 记录算法开始时间
print("Start time:", start_time)

#12. 执行遗传算法主流程
# 参数说明：
# cxpb=0.4  - 交叉概率40%
# mutpb=0.1 - 变异概率10%
# ngen      - 迭代代数
# verbose=2 - 显示进化进度（2=每代统计，1=简要进度，0=不输出）
r = algorithms.eaSimple(population, toolbox, cxpb = 0.4, mutpb = 0.1, ngen = num_generations, verbose = 2)
#返回值类型：list (final_population, logbook)
#1.final_population：进化完成后的最终种群（包含所有Individual对象）
#2.logbook:记录每代统计信息的字典，可用于绘制进化曲线：
# gen：代数；
# nevals：被评估的个体数；
# avg/std/min/max：适应度的统计值


#13. 记录算法结束时间并计算耗时
end_time = datetime.now()
print('End time:',end_time)
time_elapsed = end_time-start_time
print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

#14. 选择最好个体
best_individuals = tools.selBest(population, k=1)
best_num_neurons = None
best_num_seq = None
best_epoch = None
best_batch_size = None
best_learning_rate = None
#根据得到的个体编码进行转码得到lstm参数
for bi in best_individuals:
    # 解码
    num_neurons_bits = BitArray(bi[0:8])
    num_seq_bits = BitArray(bi[8:13])
    epoch_bits = BitArray(bi[13:20])
    batch_size_bits = BitArray(bi[20:27])
    learning_rate_bits = BitArray(bi[27:])

    # 参数传递
    best_num_neurons = num_neurons_bits.uint
    best_num_seq = num_seq_bits.uint
    best_epoch = epoch_bits.uint
    best_batch_size = batch_size_bits.uint
    temp = learning_rate_bits.uint
    best_learning_rate = temp * (math.exp(-9))

    print('\n Num of neurons best: ', best_num_neurons,
          '\n Num of seq best: ', best_num_seq,
          '\n best Epoch:', best_epoch,
          '\n best Batch_size:', best_batch_size,
          '\n best Learning_rate:', best_learning_rate,)




