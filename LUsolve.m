function [L, U, x] = LUsolve(A, b)
    [n, m] = size(A);
    if n ~= m
        error('A 必须是方阵');
    end
    if length(b) ~= n
        error('b 的长度必须等于 A 的阶数');
    end
    b = b(:);  
    L = eye(n);
    U = zeros(n);

    for k = 1:n
        for j = k:n
            U(k,j) = A(k,j) - L(k,1:k-1) * U(1:k-1,j);
        end

        if U(k,k) == 0
            error('出现零主元，无法继续（可考虑加入选主元）');
        end

        for i = k+1:n
            L(i,k) = (A(i,k) - L(i,1:k-1) * U(1:k-1,k)) / U(k,k);
        end
    end
    y = zeros(n,1);
    for i = 1:n
        y(i) = b(i) - L(i,1:i-1) * y(1:i-1);
    end

    x = zeros(n,1);
    for i = n:-1:1
        x(i) = (y(i) - U(i,i+1:n) * x(i+1:n)) / U(i,i);
    end
end