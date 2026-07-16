function R = vote(num, p, r)
%VOTE 计算表决系统的可靠性
%
%   R = VOTE(NUM, P, RATIO) 返回由 NUM 个元件组成的表决系统的可靠性。
%   P 为各元件相同的故障率，RATIO 为最少需要正常的元件数量或比例。
%
%   输入参数：
%       num   - 元件数量（正整数）
%       p     - 故障率（0 到 1 之间的标量）
%       r     - 正常元件阈值（整数或小数，小数表示占比，将向上取整）
%
%   输出参数：
%       R     - 系统可靠性（保留5位小数）
%
%   示例：
%       R1 = vote(3, 0.1, 1);       % 至少1个元件正常即可
%       R2 = vote(3, 0.1, 2);       % 至少2个元件正常
%       R3 = vote(5, 0.2, 0.6);     % 至少60%的元件正常，即至少3个

    % 参数检查
    if ~isscalar(num) || num ~= floor(num) || num <= 0
        error('num 必须为正整数。');
    end

    if ~isscalar(p) || p < 0 || p > 1
        error('p 必须为 [0, 1] 之间的标量。');
    end

    % 故障率向量展开
    p_vec = repmat(p, 1, num);

    % 若 r 为占比形式，向上取整
    if isfloat(r) && r > 0 && r < 1
        r = ceil(num * r);
    end

    % 二项概率函数
    function prob = binom(k, n, prob_success)
        prob = nchoosek(n, k) * prob_success^k * (1 - prob_success)^(n - k);
    end

    % 累加器初始化
    result = 0;

    % 计算可靠性
    if r > num / 2
        % 需要多数元件正常，直接累加从 r 到 num 的成功概率
        for i = r:num
            result = result + binom(i, num, 1 - p_vec(i));
        end
    else
        % 反向计算不可靠概率，再取 1 减去
        for i = 0:(r - 1)
            result = result + binom(i, num, 1 - p_vec(i + 1));
        end
        result = 1 - result;
    end

    % 保留5位小数
    R = round(result, 5);
end
