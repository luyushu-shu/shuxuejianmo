function [A,x] = Gauss(A,b)
    n = length(b);

    if size(A,2) == n
        A = [A, b(:)];
    elseif size(A,2) ~= n + 1
        error('A 的列数应为 n 或 n+1');
    end

    for k = 1:(n-1)
        [~, p] = max(abs(A(k:n, k)));
        p = p + k - 1;
        if p ~= k
            A([k, p], :) = A([p, k], :);
        end

        if A(k,k) == 0
            error('主元为 0，无法继续消元');
        end

        A((k+1):n, (k+1):(n+1)) = A((k+1):n, (k+1):(n+1)) ...
            - A((k+1):n, k) / A(k,k) * A(k, (k+1):(n+1));
        A((k+1):n, k) = 0;
    end

    x = zeros(n,1);
    x(n) = A(n,n+1) / A(n,n);
    for k = n-1:-1:1
        x(k) = (A(k,n+1) - A(k,(k+1):n) * x((k+1):n)) / A(k,k);
    end
end