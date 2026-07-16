function result = infection(b, r, m, n, c)
    % 波利亚模型中的传染病模型
    % 每次发现一个传染病都会增加再感染的概率，每次发现一个正常则会减少再感染的概率
    %
    % 输入参数:
    %   b : int - 类型1的数量（正常）
    %   r : int - 类型2的数量（感染）
    %   m : int - 抽到m个类型1（正常）
    %   n : int - 抽到n个类型2（感染）
    %   c : int - 每次抽完之后，增加的同类型数量
    %
    % 输出:
    %   result : float - 计算得到的概率值
    %
    % 示例:
    %   infection(5, 6, 1, 2, 3) % 返回约 0.309396
    
    % 初始化结果为组合数
    result = nchoosek(m + n, m);
    
    % 计算抽到m个正常类型的概率乘积
    for i = 0:(m-1)
        % 分子：当前正常类型数量 + i * c
        up = b + i * c;
        
        % 分母：总体数量 + i * c
        down = b + r + i * c;
        
        % 累乘概率因子
        result = result * (up / down);
    end
    
    % 计算抽到n个感染类型的概率乘积
    for j = 0:(n-1)
        % 分子：当前感染类型数量 + j * c
        up = r + j * c;
        
        % 分母：总体数量 + (m + j) * c
        down = b + r + (m + j) * c;
        
        % 累乘概率因子
        result = result * (up / down);
    end
end