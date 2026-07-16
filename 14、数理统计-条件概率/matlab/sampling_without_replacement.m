function prob = sampling_without_replacement(b, r, m, n)
    % 无放回抽样(超几何分布)
    % 计算从两种类型的总体中抽取指定数量的每种类型的概率
    %
    % 输入参数:
    %   b : int - 类型1的数量
    %   r : int - 类型2的数量
    %   m : int - 抽到的类型1数量 (必须满足 m < b)
    %   n : int - 抽到的类型2数量 (必须满足 n < r)
    %
    % 输出:
    %   prob : float - 计算得到的概率值
    %
    % 示例:
    %   sampling_without_replacement(5, 6, 2, 3) % 返回约 0.4329
    %   sampling_without_replacement(90, 10, 8, 2) % 返回约 0.2015
    
    % 参数验证
    if m >= b || n >= r
        error('sampling_without_replacement:InvalidArgument', ...
              '参数错误: 确保 m < b 且 n < r');
    end
    
    % 计算组合数并返回概率
    prob = nchoosek(b, m) * nchoosek(r, n) / nchoosek(b + r, m + n);
end