%%% 定义编码函数，生成染色体编码

function ret=Code(lenchrom,bound)
%本函数将变量编码成染色体，用于随机初始化一个种群
% lenchrom   input : 染色体长度
% bound      input : 变量的取值范围
% ret        output: 染色体的编码值

flag=0;
while flag==0                                       % 开始while循环，直到生成有效的染色体(flag=1)才会退出
    pick=rand(1,length(lenchrom));                  % 生成一个随机数向量pick，长度与lenchrom相同，元素值在[0,1)区间均匀分布
    ret=bound(:,1)'+(bound(:,2)-bound(:,1))'.*pick; % 通过线性插值，将随机数映射到变量的取值范围内：
    flag=test(lenchrom,bound,ret);                  % 检验染色体的可行性：调用子函数test检查生成的染色体是否在允许范围内
end

