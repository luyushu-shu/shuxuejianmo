% 又称为罐子模型，可以引出放回抽样、无放回抽样、传染病模型以及安全模型。
% 设罐中有b个蓝球、r个红球，每次随机取出一个球，取出后将原球放回，还加进c个同色球和d个异色球
% 无放回抽样：c=-1，d=0
% 放回抽样：  c=0，d=0
% 传染病模型： c>0，d=0
% 安全模型：  c=0，d>0

% 90个样本1，10个样本2，抽到8个样本1，2个样本2的概率
disp('放回抽样: ')
disp(sampling_with_replacement(90, 10, 8, 2))
disp('不放回抽样: ')
disp(sampling_without_replacement(90, 10, 8, 2))

% 5个样本1，6个样本2，抽到1个样本1，2个样本2，分别放入3个同类型和3个不同类型的概率
disp('传染病模型: ')
disp(infection(5, 6, 1, 2, 3))
disp('安全模型: ')
result = security(5, 6, 1, 2, 3, 0, 1, true);
keys = result.keys;
value = result.values;
for i = 1: length(keys)
    disp(keys{i})
    disp(value{i})
end
disp(security(5, 6, 1, 2, 3, 0, 1, false));