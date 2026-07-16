function result = security(b, r, m, n, d, name1, name2, verbose)
    % 安全抽样模型（波利亚模型变体）
    % 每次抽样后，增加d个不同类型的样本
    %
    % 输入参数:
    %   b : int - 类型1的数量
    %   r : int - 类型2的数量
    %   m : int - 抽到m个类型1
    %   n : int - 抽到n个类型2
    %   d : int - 每次抽完后增加d个不同类型的数量
    %   name1 : str | int - 类型1的名称 (默认为'0')
    %   name2 : str | int - 类型2的名称 (默认为'1')
    %   verbose : bool - 是否打印运算过程 (默认为false)
    %
    % 输出:
    %   result : containers.Map - 包含不同序列及其概率的映射对象
    %
    % 示例:
    %   security(5, 6, 1, 2, 3) % 返回算得的概率和
    if(~exist('name1', 'var'))
        name1 = "0";
    end
    if(~exist('name2', 'var'))
        name2 = "1";
    end
    if(~exist('verbose', 'var'))
        verbose = false;
    end
    
    % 确保名称参数为字符串
    name1 = char(string(name1));
    name2 = char(string(name2));
    
    % 递归生成唯一序列（避免生成冗余排列）
    sequences = generate_unique_sequences(m, n, name1, name2);
    
    % 初始化结果容器
    result = containers.Map('KeyType', 'char', 'ValueType', 'double');
    
    % 遍历所有唯一序列
    for i = 1:length(sequences)
        seq = sequences{i};
        current_b = b;
        current_r = r;
        p = 1;
        
        % 计算当前序列的概率
        for j = 1:length(seq)
            if seq(j) == name1
                % 抽到类型1
                p = p * (current_b / (current_b + current_r));
                current_r = current_r + d;  % 增加类型2
            elseif seq(j) == name2
                % 抽到类型2
                p = p * (current_r / (current_b + current_r));
                current_b = current_b + d;  % 增加类型1
            end
        end
        
        % 创建序列字符串标识
        seq_str = strrep(seq, ' ', '');
        
        % 存储结果
        result(seq_str) = p;
    end
    if ~verbose
        value_array = values(result);
        result = sum(cell2mat(value_array));
    end
    

    %% 递归生成唯一序列的子函数
    function sequences = generate_unique_sequences(m, n, name1, name2)
        % 递归生成所有唯一序列（避免冗余排列）
        sequences = {};
        
        % 基准情况：没有可抽取的元素
        if m == 0 && n == 0
            sequences = {''};
            return;
        end
        
        % 如果有类型1可抽取
        if m > 0
            sub_seqs = generate_unique_sequences(m-1, n, name1, name2);
            for i = 1:length(sub_seqs)
                % 添加类型1前缀
                seq = [name1, sub_seqs{i}];
                sequences{end+1} = seq;
            end
        end
        
        % 如果有类型2可抽取
        if n > 0
            sub_seqs = generate_unique_sequences(m, n-1, name1, name2);
            for i = 1:length(sub_seqs)
                % 添加类型2前缀
                seq = [name2, sub_seqs{i}];
                sequences{end+1} = seq;
            end
        end
    end
end