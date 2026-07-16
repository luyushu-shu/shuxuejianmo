function ret=Mutation(pmutation,lenchrom,chrom,sizepop,pop,bound)
% 本函数完成变异操作
% pmutation             input  : 变异概率
% lenchrom              input  : 染色体长度
% chrom                 input  : 染色体群
% sizepop               input  : 种群规模
% pop                   input  : 当前种群的进化代数和最大的进化代数信息
% ret                   output : 变异后的染色体

for i=1:sizepop
    % 随机选择一个染色体进行变异
    pick=rand;                       % 生成随机数 pick（范围 (0,1)
    while pick==0                    % 避免随机数为0
        pick=rand;
    end
    index=ceil(pick*sizepop);        % 通过 ceil(pick * sizepop) 随机选择一个个体索引 index
    
    % 变异概率决定该轮循环是否进行变异
    pick=rand;                       
    if pick>pmutation                % 如果随机数 pick > pmutation，跳过变异（continue）
        continue;
    end

    flag=0;                          % flag=0表示未完成变异操作循环
    while flag==0
        
        % 变异位置
        pick=rand;                   % 生成随机数 pick（范围 (0,1)% 
        while pick==0                % 避免随机数为0
            pick=rand;
        end
        pos=ceil(pick*sum(lenchrom)); % 随机选择第 pos 个变量进行变异
        v=chrom(i,pos);               % 当前基因值
        v1=v-bound(pos,1);            % 当前值到下界的距离
        v2=bound(pos,2)-v;            % 当前值到上界的距离
        
        % 变异开始
        pick=rand;                    % 变异方向系数：决定变异方向
        if pick>0.5                   % pop(1) 是当前代数，pop(2) 是最大代数
            % 随着进化代数的增加，pop(1)/pop(2) 从 0 趋近于 1，因此 (1 - pop(1)/pop(2))^2 从 1 趋近于 0
            % 这使得变异幅度 delta 随代数增加而减小（早期大范围探索，后期小范围微调）
            delta=v2*(1-pick^((1-pop(1)/pop(2))^2));  % 当 pick 接近 0 时，delta 接近最大值（v1 或 v2）
            chrom(i,pos)=v+delta;     % pick > 0.5: 向上变异（v + delta）
        else
            delta=v1*(1-pick^((1-pop(1)/pop(2))^2));
            chrom(i,pos)=v-delta;     % pick ≤ 0.5: 向下变异（v - delta）
        end   
        
        % 变异结束
        flag=test(lenchrom,bound,chrom(i,:));     % 检验染色体：确保变异后的个体仍在变量范围内
    end
end
% 返回变异后的种群
ret=chrom; 