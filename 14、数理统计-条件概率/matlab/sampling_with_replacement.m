function prob = sampling_with_replacement(b, r, m, n)
    % 放回抽样（二项分布）
    % 计算公式为：C_{m+n}^m * (b^m * r^n) / (b+r)^(m+n)
    %
    % 输入参数:
    %   b : int - 类型1的数量
    %   r : int - 类型2的数量
    %   m : int - 抽到的类型1数量
    %   n : int - 抽到的类型2数量
    %
    % 输出:
    %   prob : float - 计算得到的概率值
    %
    % 示例:
    %   sampling_with_replacement(5, 6, 2, 3) % 返回约 0.33529
    %   sampling_with_replacement(90, 10, 8, 2) % 返回约 0.1937102
    
    % 直接计算公式
    prob = nchoosek(m + n, m) * (b^m * r^n) / (b + r)^(m + n);
end

