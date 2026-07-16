function R = parallel(num, p)
%PARALLEL 计算并联系统的可靠性
%
%   R = PARALLEL(NUM, P) 返回由 NUM 个元件组成的并联系统的可靠性。
%   P 可以是一个标量（所有元件故障率相同）或一个向量（分别指定每个元件的故障率）。
%
%   输入参数：
%       num - 元件数量（正整数）
%       p   - 故障率（标量或长度为 num 的向量，范围在 [0, 1]）
%
%   输出参数：
%       R   - 系统可靠性（保留5位小数）
%
%   示例：
%       R1 = parallel(3, 0.9);                 % 三个元件故障率均为 0.9，可靠性为 1 - 0.9^3 = 0.271
%       R2 = parallel(3, [0.9, 0.8, 0.7]);     % 三个元件分别设定不同故障率，可靠性为 1 - (0.9*0.8*0.7)

    % 输入合法性检查
    if ~isscalar(num) || num ~= floor(num) || num <= 0
        error('num 必须为正整数。');
    end

    if isscalar(p)
        if p < 0 || p > 1
            error('标量 p 的取值必须在 [0, 1] 范围内。');
        end
        p = repmat(p, 1, num);  % 扩展为等长向量
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

    % 计算并联系统可靠性：1 减去 全部元件都故障的概率
    R = round(1 - prod(p), 5);

end
