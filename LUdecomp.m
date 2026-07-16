function [L, U, x] = LUsolve(A, b)
    [n, m] = size(A);
    if n ~= m
        error('A 必须是方阵');
    end
    if length(b) ~= n
        error('b 的长度必须等于 A 的阶数');
    end
    b = b(:);  % 转成列向量

    % ---------- LU 分解 (Doolittle) ----------
    L = eye(n);
    U = zeros(n);

    for k = 1:n
        % 计算 U 的第 k 行
        for j = k:n
            U(k,j) = A(k,j) - L(k,1:k-1) * U(1:k-1,j);
        end

        if U(k,k) == 0
            error('出现零主元，无法继续（可考虑加入选主元）');
        end

        % 计算 L 的第 k 列（对角线以下）
        for i = k+1:n
            L(i,k) = (A(i,k) - L(i,1:k-1) * U(1:k-1,k)) / U(k,k);
        end
    end

    % ---------- 先解 Ly = b（前代） ----------
    y = zeros(n,1);
    for i = 1:n
        y(i) = b(i) - L(i,1:i-1) * y(1:i-1);
        % L(i,i)=1，无需再除
    end

    % ---------- 再解 Ux = y（回代） ----------
    x = zeros(n,1);
    for i = n:-1:1
        x(i) = (y(i) - U(i,i+1:n) * x(i+1:n)) / U(i,i);
    end
end