function ret=Cross(pcross,lenchrom,chrom,sizepop,bound)
%本函数完成交叉操作
% pcorss                input  : 交叉概率
% lenchrom              input  : 染色体的长度
% chrom                 input  : 染色体群
% sizepop               input  : 种群规模
% ret                   output : 交叉后的染色体

for i=1:sizepop 
    
    % 随机选择两个染色体进行交叉
    pick=rand(1,2);      % 生成两个随机数 pick=[r1, r2]（范围 [0,1)）
    while prod(pick)==0  % 如果 r1 或 r2 为 0，则重新生成（避免索引为 0）
        pick=rand(1,2);  
    end
    % 通过 ceil(pick.*sizepop) 将随机数映射到 [1, sizepop]，得到两个个体的索引 index=[idx1, idx2]
    index=ceil(pick.*sizepop);  

    % 交叉概率决定是否进行交叉
    pick=rand;         % 生成一个随机数 pick（范围 [0,1)）
    while pick==0      % 如果 r1 或 r2 为 0，则重新生成（避免索引为 0）
        pick=rand;
    end
    if pick>pcross     % 如果 pick > pcross，跳过交叉（不执行后续操作）
        continue;
    end

    flag=0;            
    % flag=0 表示尚未生成有效的交叉结果
    while flag==0      
        % 随机选择交叉位置
        pick=rand;
        while pick==0
            pick=rand;   % 如果 r1 或 r2 为 0，则重新生成（避免索引为 0）
        end
        pos=ceil(pick.*sum(lenchrom));                 % 随机选择进行交叉的位置，即选择第几个基因位置进行交叉
        % 注意：两个染色体交叉的位置相同
        % 注意：ceil函数是向上取整数  pick.*sum(lenchrom)是将随机数 pick 映射到 (0, sum(lenchrom)) 范围
        
        pick=rand; % 交叉开始 更新随机数 交叉系数0.3
        
        %% 算术交叉生成子代
        v1=chrom(index(1),pos);                        % 父代 1 (index(1)): [1.0, 3.0, 5.0]
        v2=chrom(index(2),pos);                        % 父代 2 (index(2)): [2.0, 4.0, 6.0]
        chrom(index(1),pos)=pick*v2+(1-pick)*v1;       % 子代 1 的值 = pick * v2 + (1-pick) * v1
        chrom(index(2),pos)=pick*v1+(1-pick)*v2;       % 子代 2 的值 = pick * v1 + (1-pick) * v2 
        flag1=test(lenchrom,bound,chrom(index(1),:));  % 检验染色体1的可行性
        flag2=test(lenchrom,bound,chrom(index(2),:));  % 检验染色体2的可行性
        if   flag1*flag2==0                            % 规避0值
            flag=0;
        else flag=1;
        end    %如果两个染色体不是都可行，则重新交叉
    end
end
ret=chrom;
