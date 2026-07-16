%% 清空环境
clc
clear

%% 参数初始化
% 粒子群算法中的两个参数
c1 = 1.49445;
c2 = 1.49445;
maxgen=300;   % 进化次数T  
sizepop=20;   % 种群规模N

% 粒子速度上下限 
Vmax=0.5;
Vmin=-0.5;

% 粒子位置上下限（位置即x,y变量取值）
popmax=2;
popmin=-2;

% 线性递减惯性权重
ws=0.9;
we=0.4;

%% 产生初始粒子和速度
for i=1:sizepop
    % 随机产生一个种群
    pop(i,:)=2*rands(1,2);  % 初始种群  （生成1个1行2列随机向量，元素数值在[-2,2]之间）
    V(i,:)=0.5*rands(1,2);  % 初始化速度（生成1个1行2列随机向量，元素数值在[-0.5,0.5]之间）
    
    % 计算适应度
    fitness(i)=fun(pop(i,:));   % 粒子的适应度
end

%% 个体极值和群体极值
[bestfitness bestindex]=max(fitness);
zbest=pop(bestindex,:);   %全局最佳
gbest=pop;    %个体最佳
fitnessgbest=fitness;   %个体最佳适应度值
fitnesszbest=bestfitness;   %全局最佳适应度值

%% 迭代寻优
for i=1:maxgen
    for j=1:sizepop
        % 线性递减
         w=ws-(ws-we)*i/maxgen;
        %速度更新
        V(j,:) = w*V(j,:) + c1*rand*(gbest(j,:) - pop(j,:)) + c2*rand*(zbest - pop(j,:));
        V(j,find(V(j,:)>Vmax))=Vmax;
        V(j,find(V(j,:)<Vmin))=Vmin;
        %位置更新
        pop(j,:)=pop(j,:)+V(j,:);
        pop(j,find(pop(j,:)>popmax))=popmax;
        pop(j,find(pop(j,:)<popmin))=popmin;
        %适应度值
        fitness(j)=fun(pop(j,:)); 
    end
    
    for j=1:sizepop
        
        %个体最优更新
        if fitness(j) > fitnessgbest(j)
            gbest(j,:) = pop(j,:);
            fitnessgbest(j) = fitness(j);
        end
        
        %群体最优更新
        if fitness(j) > fitnesszbest
            zbest = pop(j,:);
            fitnesszbest = fitness(j);
        end
    end 
    yy(i)=fitnesszbest;    
end

%% 结果分析
plot(yy,'Color',[021 151 165]/255,'LineWidth',3)
title('最优个体适应度','fontsize',12);
xlabel('进化代数','fontsize',12);ylabel('适应度','fontsize',12);

