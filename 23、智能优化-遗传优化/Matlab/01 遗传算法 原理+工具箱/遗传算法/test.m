%%% 定义测试函数，检查染色体是否有效

function flag=test(lenchrom,bound,code)
% lenchrom   input : 染色体长度
% bound      input : 变量的取值范围
% code       output: 染色体的编码值

flag=1;             % 初始化flag为1 假设染色体有效
[n,m]=size(code);   % 获取染色体编码的尺寸

for i=1:n
    if code(i)<bound(i,1) || code(i)>bound(i,2)  % bound(i,1)是下限，bound(i,2)是上限
        flag=0;     % 如果变量值超出其对应的取值范围，则将flag设为0(无效)
    end
end