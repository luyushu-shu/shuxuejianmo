clear,clc;
%% 1.对正向化后的矩阵进行标准化
% X=[5/7 1/3 2/3; 0 1 1/3; 1 0 1; 3/7 2/3 0]
X = input("指标矩阵X=")
[n,m] = size(X);
Z = X./repmat(sum(X.*X).^0.5,n,1);
disp("标准化矩阵:");
disp(X);
%计算熵权
D = zeros(1,m);
for i = 1:m
    x = Z(:,i);%取出第i列元素
    p = x/sum(x);
    e = -sum(p.*mylog(p))/log(n);
    D(i) = 1-e;
end
W = D./sum(D);
disp("权重为：");
disp(W);
