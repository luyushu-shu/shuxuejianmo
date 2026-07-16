%% 清空环境
clc
clear


%% 遗传算法参数
maxgen=1000;                       %进化代数
sizepop=100;                       %种群规模
pcross=[0.7];                      %交叉概率
pmutation=[0.01];                  %变异概率
lenchrom=[1 1];                    %变量字串长度
bound=[-2 2;-2 2];                 %变量范围 参数维度为2：共2行数据,每行存储着各优化参数的下限和上限

% 初始化数组
individuals=struct('fitness',zeros(1,sizepop), 'chrom',[]);  %种群结构体
avgfitness=[];                                               %种群平均适应度
bestfitness=[];                                              %种群最佳适应度
bestchrom=[];                                                %适应度最好染色体

%% 初始化种群
for i=1:sizepop
    individuals.chrom(i,:)=Code(lenchrom,bound);             % 调用编码方法Code：随机产生个体
    x=individuals.chrom(i,:);                                % 传递个体数据：从individuals.chrom传递给x
    individuals.fitness(i)=fun(x);                           % 调用适应度函数fun：计算个体适应度
end

%% 找最优的染色体
[bestfitness bestindex]=max(individuals.fitness);      % 根据最优适应度值,提取出索引值index
bestchrom=individuals.chrom(bestindex,:);              % 根据索引值index,匹配出最优的染色体
avgfitness=sum(individuals.fitness)/sizepop;           % 计算染色体的平均适应度

% 初始化数组：记录每一代进化中最好的适应度和平均适应度
trace=[]; 
chrom = [];

%% 进化开始
for i=1:maxgen % 迭代循环

    %% 选择操作
    % individuals: 当前种群（包含染色体 chrom 和适应度 fitness）；sizepop: 种群大小（个体数量）
    individuals=Select(individuals,sizepop); 
    avgfitness=sum(individuals.fitness)/sizepop;   % 计算当前种群的平均适应度
     
    %% 交叉操作
    % pcross: 交叉概率；lenchrom: 染色体长度（变量维度）；bound: 变量的取值范围（约束条件）
    individuals.chrom=Cross(pcross,lenchrom,individuals.chrom,sizepop,bound); 
     
    %% 变异操作
    % pmutation: 变异概率
    % [i maxgen]: 当前代数 i + 最大代数 maxgen（可用于自适应变异）
    individuals.chrom=Mutation(pmutation,lenchrom,individuals.chrom,sizepop,[i maxgen],bound);
    
    %% 计算适应度 
    for j=1:sizepop
        x=individuals.chrom(j,:);
        individuals.fitness(j)=fun(x);   
    end
    
    %% 精英保留
    % 找到最小和最大适应度的染色体，提取出种群位置index
    [newbestfitness,newbestindex]=max(individuals.fitness);
    [worestfitness,worestindex]=min(individuals.fitness);

    % 如果当前代的最优适应度 newbestfitness 比历史最优 bestfitness 更好，则更新 bestfitness 和 bestchrom（最优染色体）
    if bestfitness<newbestfitness                     % 更新：最优适应度值
        bestfitness=newbestfitness;                   % 更新：最优适应度值
        bestchrom=individuals.chrom(newbestindex,:);  % 更新：最优染色体
    
    % 用历史最优解 bestchrom 替换当前代最差个体；保证最优解不会被交叉/变异破坏（精英保留策略）
    end
    individuals.chrom(worestindex,:)=bestchrom;
    individuals.fitness(worestindex)=bestfitness;
    
    %% 记录进化过程
    avgfitness=sum(individuals.fitness)/sizepop;
    chrom = [chrom;bestchrom];                        % 记录：最优染色体
    trace=[trace;avgfitness bestfitness];             % 记录：每一代进化中平均适应度和最好的适应度
end
%进化结束

%% 绘图显示
[r ~]=size(trace);  % 获取矩阵trace的行数（r）和列数（~表示忽略列数）

% 绘制收敛曲线：
figure(1)              % 创建一个新的图形窗口
plot([1:r]',trace(:,2),'b--');   
% [1:r]'：x轴数据（1到总代数r的列向量）
% trace(:,2)：y轴数据（trace矩阵第2列，通常记录每代的最优函数值）
% 'b--'：蓝色虚线样式

title(['函数值曲线  ' '终止代数＝' num2str(maxgen)],'fontsize',12);
xlabel('进化代数','fontsize',12);ylabel('函数值','fontsize',12);
disp('函数值                   变量');
grid on

% 窗口显示
disp([bestfitness x]);

figure(2);
lbx=-2;ubx=2; %函数自变量x范围【-2,2】
lby=-2;uby=2; %函数自变量y范围【-2,2】
ezmesh('y*sin(2*pi*x)+x*cos(2*pi*y)',[lbx,ubx,lby,uby],50);   % 画出函数曲线
hold on;
aa = individuals.chrom;
plot3(aa(:,1),aa(:,2),individuals.fitness','b^');             % 画出每代的最优点
grid on;

