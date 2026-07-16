function x = GaussPivot(A, b)
    n = length(b);
    Ab = [A, b(:)];

    for k = 1:n-1
        [~, p] = max(abs(Ab(k:n, k)));
        p = p + k - 1;
        if p ~= k
            Ab([k,p], :) = Ab([p,k], :);
        end

        if Ab(k,k) == 0
            error('列主元法遇到零主元');
        end

        Ab(k+1:n, k+1:n+1) = Ab(k+1:n, k+1:n+1) ...
            - Ab(k+1:n,k)/Ab(k,k) * Ab(k,k+1:n+1);
        Ab(k+1:n,k) = 0;
    end

    x = zeros(n,1);
    x(n) = Ab(n,n+1)/Ab(n,n);
    for k = n-1:-1:1
        x(k) = (Ab(k,n+1) - Ab(k,k+1:n)*x(k+1:n)) / Ab(k,k);
    end
end