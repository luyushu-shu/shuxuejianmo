function ret=Select(individuals,sizepop)
% 本函数对每一代种群中的染色体进行选择，以进行后面的交叉和变异
% individuals input  : 种群信息
% sizepop     input  : 种群规模
% opts        input  : 选择方法的选择
% ret         output : 经过选择后的种群

% individuals.fitness= (individuals.fitness);
sumfitness=sum(individuals.fitness);    % 计算当前种群所有个体的适应度之和 sumfitness
sumf=individuals.fitness./sumfitness;   % 计算每个个体的 选择概率（适应度占比）[0.1, 0.3, 0.6]
index=[];
for i=1:sizepop   % 转sizepop次轮盘    想象一个轮盘，每个个体占据的面积与其适应度成正比
    pick=rand;                      % 随机扔一个球（pick=rand），球落在哪个区域，就选中对应的个体
    
    for j=1:sizepop
        pick=pick-sumf(j);          % 减去当前个体的概率
        if pick<0                   % 如果 pick < 0，说明落入了当前个体的区间
            index=[index j];        % 记录被选中的个体索引
            break;                  % 寻找落入的区间，此次转轮盘选中了染色体i
        end                         % 注意：适应度高的个体更可能被选中（但低适应度的个体也有机会）
    end                             % 注意：可能重复选择某些优质个体（符合“适者生存”原则）
end

% 据 index 从原种群中提取被选中的个体，形成新一代种群。
individuals.chrom=individuals.chrom(index,:);   
individuals.fitness=individuals.fitness(index); 
ret=individuals;