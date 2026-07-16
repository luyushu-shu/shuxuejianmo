import numpy as np
np.random.seed(1337)
import os
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from keras.layers import Dense, Dropout, LSTM,GRU
from keras.models import Sequential
import matplotlib.pyplot as plt

#显示中文
# 用来正常显示中文标签
plt.rcParams['font.sans-serif'] = ['SimHei']
# 用来正常显示符号
plt.rcParams['axes.unicode_minus'] = False
#忽略警告
import warnings
warnings.filterwarnings("ignore")
#如果没有这个目录，则创建这个目录
if not os.path.isdir('result'):
    os.mkdir('result')


#本案例参数只是初步调节，仅用于学习，自己的数带入后训练过程需要不断调参才能获得较好的效果

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


#####数据分析部分（如果不需要可直接删除#----->## ##<-----##中间部分）
#----->##
# 热力图相关性分析，需要预测的特征列与其他列颜色越深，相关性越大
plt.matshow(da.corr(method='spearman'), vmax=1, vmin=-1, cmap='PRGn')
plt.title('hot feature', size=15)
plt.colorbar()
plt.title('correlation analysis')
plt.show()
# 对于一个时间序列，通常可以从四个方面来考虑数据的特性：趋势性（Trend）、季节性（Seasonal ）、周期性（ Cyclical ）、随机性（Irregular）
from statsmodels.tsa.seasonal import seasonal_decompose

def decompose(timeseries):
    # 返回包含三个部分 trend（趋势部分） ， seasonal（季节性部分） 和residual (残留部分)
    decomposition = seasonal_decompose(timeseries,model='additive',extrapolate_trend='freq', period=1)

    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    fig = plt.figure(figsize=(15, 8), dpi=80)
    plt.subplot(411)
    plt.plot(timeseries, label='Original')
    plt.xticks(range(1, len(data), 100), rotation=45)  # 为了横坐标显示清楚，通过间隔50个显示一个值
    plt.legend(loc='best')
    plt.subplot(412)
    plt.plot(trend, label='Trend')
    plt.xticks(range(1, len(data), 100), rotation=45)  # 为了横坐标显示清楚，通过间隔50个显示一个值
    plt.legend(loc='best')
    plt.subplot(413)
    plt.plot(seasonal, label='Seasonality')
    plt.xticks(range(1, len(data), 100), rotation=45)  # 为了横坐标显示清楚，通过间隔50个显示一个值
    plt.legend(loc='best')
    plt.subplot(414)
    plt.plot(residual, label='Residuals')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.xticks(range(1, len(data), 100), rotation=45)  # 为了横坐标显示清楚，通过间隔50个显示一个值
    plt.legend()
    plt.savefig('result/decompose_data.png')  # 图片保存路径
    plt.show()
    return trend, seasonal, residual



#对要预测的特征close进行分析
close=df["close"]#获取close特征列数据
trend, seasonal, residual = decompose(close)
#对于数据趋势特征，季节性等特征比较明显时，如果lstm模型预测不好，可以通过调节模型参数，如果还不行就需要考虑一下数据预处理了，预处理方法比如分解算法等


#<-----##

####下面是lstm模型预测部分

#显示原数据
fig = plt.figure(figsize=(15, 8), dpi=80)#设置图大小
plt.plot(date, data[:,0], label="origin data", color='b',lw=2.5)  #若不需要日期或者数据没有日期可改成plt.plot(data[:,0], label=" ", color='b',lw=2.5),ata[:,0]表示取close列
plt.title("origin data")#图表题
plt.xticks(range(1,len(data),50),rotation=45) #为了横坐标显示清楚，通过间隔50个显示一个值
plt.legend()#显示图例
plt.savefig('result/origin_data.png')#图片保存路径
plt.show()#显示图像

#划分训练集和测试集长度
X=data[:,1:5]#取数据的其他特征部分,[行或行区间(:),列或列区间(:)],这里取open,high,low,vol列
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



seq_len = 5  #时间步长 ,意思是通过历史数据t-5,t-4,t-3,t-2,t-1 预测 t时刻值,该值为超参数，需要调节使模型预测变好
#转换成LSTM所需格式，（样本数，步长，特征数）
X_train = np.array([data_train[i : i + seq_len, :] for i in range(data_train.shape[0] - seq_len)]) #数据构建为（样本数，步长，特征数）形式
y_train = np.array([data_train[i + seq_len, 0] for i in range(data_train.shape[0]- seq_len)])
X_test = np.array([data_test[i : i + seq_len, :] for i in range(data_test.shape[0]- seq_len)])
y_test = np.array([data_test[i + seq_len, 0] for i in range(data_test.shape[0] - seq_len)])

print(X_train.shape,y_train.shape,X_test.shape,y_test.shape)


#模型超参数（可调节参数）
#1.神经元units以及lstm层数
#2.激活函数activation
#3.loss函数，优化器optimizer
#4.训练次数epochs和batch_size大小
#网络模型keras
model = Sequential() #声明模型
#第一层lstm，神经元数64，激活函数relu，return_sequences=True表示后面还要添加lstm则用True，否则为False，input_shape为声明网络输入的形状（第一层需要声明），X_train.shape[1]为获取数据的步长，X_train.shape[2]为数据的特征
model.add(GRU(units=128,activation='relu',return_sequences=False,input_shape=(X_train.shape[1], X_train.shape[2])))
# model.add(LSTM(units=256,activation='tanh'))#第二层lstm，神经元数64，激活函数tanh，注意第一层设置return_sequences=True
model.add(Dropout(0.2))#dropout层，防止过拟合
model.add(Dense(1))#全连接层
model.compile(loss='mean_squared_error', optimizer='adam')#指定loss函数和优化器类型
# 训练网络，训练次数100次，batch_size大小为128，验证数据不参与训练，所以可以直接用测试数据不用单独划分验证集，shuffle为是否打乱数据
history = model.fit(X_train, y_train, epochs=100, batch_size=128, validation_data=(X_test, y_test), verbose=2, shuffle=False)


# 显示训练的loss值和验证数据的loss情况
fig = plt.figure(figsize=(15, 8), dpi=80)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.savefig('result/train_loss.png')#图片保存路径
plt.show()


# 利用训练好的模型进行预测预测
yhat = model.predict(X_test)
#反归一化预测值
yhat = scY.inverse_transform(yhat)
# 反归一化真实值
ytrue = scY.inverse_transform(y_test.reshape(-1,1))

#计算评价指标（其他指标可以自己添加哦）
mse = mean_squared_error(ytrue, yhat)
mae = mean_absolute_error(ytrue, yhat)
rmse = np.sqrt(mse)
r2 = r2_score(ytrue,yhat)
# 保存评价指标数据
df_eval = pd.DataFrame([[mae, rmse, mse, r2]], columns=['mae', 'rmse', 'mse', 'r2'])
df_eval.to_csv('result/eval.csv')
print('mse: %.3f' % mse)
print('mae: %.3f' % mae)
print('rmse: %.3f' % rmse)
print('r2: %.3f' % r2)

#显示测试集预测结果
fig = plt.figure(figsize=(15, 8), dpi=80)
plt.plot(date[-len(yhat):], yhat, label="predict data", color='b',lw=2.5)  #若不需要日期或者数据没有日期可改成plt.plot(yhat, label=" ", color='b',lw=2.5)
plt.plot(date[-len(yhat):], ytrue, label="Actual data", color='r',lw=2.5)  #若不需要日期或者数据没有日期可改成plt.plot(ytrue, label=" ", color='b',lw=2.5)
plt.title("test data predict")
plt.xticks(range(1,len(yhat),50),rotation=45) #为了横坐标显示清楚，通过间隔50个显示一个值
plt.legend()
plt.savefig('result/test_predict_data.png')#图片保存路径
plt.show()

#保存LSTM预测结果到本地
new_result=np.concatenate((yhat,ytrue),axis=1)
dg=pd.DataFrame(new_result,columns=['predict','true'])
dg.to_csv('result/lstm_result.csv')

