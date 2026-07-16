function R = series(num, p)
%SERIES 计算串联系统的可靠性
%
%   R = SERIES(NUM, P) 返回由 NUM 个元件组成的串联系统的可靠性。
%   P 可以是一个标量（所有元件故障率相同）或一个向量（各元件分别指定故障率）。
%
%   输入参数：
%       num - 元件数量（正整数）
%       p   - 故障率（标量或长度为 num 的向量，范围在 [0, 1]）
%
%   输出参数：
%       R   - 系统可靠性（保留5位小数）
%
%   示例：
%       R1 = series(3, 0.1)                % 所有元件故障率均为0.1
%       R2 = series(3, [0.1 0.2 0.3])    % 分别指定每个元件故障率

    % 输入合法性检查
    if ~isscalar(num) || num ~= floor(num) || num <= 0
        error('num 必须为正整数。');
    end

    if isscalar(p)
        if p < 0 || p > 1
            error('标量 p 的取值必须在 [0, 1] 范围内。');
        end
        p = repmat(p, 1, num);  % 构造等故障率向量
    elseif isvector(p)
        if length(p) ~= num
            error('向量 p 的长度必须等于 num。');
        end
        if any(p < 0 | p > 1)
            error('向量 p 中的所有元素必须在 [0, 1] 范围内。');
        end
    else
        error('p 必须为标量或向量。');
    end

    % 故障率转为可靠率
    r = 1 - p;

    % 计算串联系统可靠性（所有可靠率相乘）
    R = round(prod(r), 5);

end
