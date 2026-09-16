# -*- coding: utf-8 -*-
"""Build A题_定日镜场的优化设计.ipynb"""
import json
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
cells = []

def md(s):
    cells.append(nbf.v4.new_markdown_cell(s))

def code(s):
    cells.append(nbf.v4.new_code_cell(s))

md(r"""# 2023年高教社杯全国大学生数学建模竞赛 A题
# 定日镜场的优化设计

本笔记本实现太阳位置—光学效率—年平均热功率计算，并对问题二、三进行定日镜场布局优化。

**场地参数**：东经 $98.5^\circ$，北纬 $39.4^\circ$，海拔 $3000\,\mathrm{m}$；圆形镜场半径 $350\,\mathrm{m}$；吸收塔高 $80\,\mathrm{m}$；集热器直径 $7\,\mathrm{m}$、高 $8\,\mathrm{m}$；塔周 $100\,\mathrm{m}$ 空地。
""")

code(r"""
from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path('.').resolve()
sys.path.insert(0, str(ROOT / 'code'))
from heliostat_field import *

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
print('modules ok, N_attachment will load next')
""")

md(r"""## 1. 太阳位置与 DNI

赤纬、时角、高度角、方位角及法向直接辐射辐照度按赛题附录公式计算。取每月21日 9:00/10:30/12:00/13:30/15:00 共60个代表性时刻。
""")

code(r"""
months = range(1, 13)
hours = [9, 10.5, 12, 13.5, 15]
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for h in hours:
    al = [np.degrees(sun_position(m, h)[0]) for m in months]
    ga = [np.degrees(sun_position(m, h)[1]) for m in months]
    axes[0].plot(list(months), al, marker='o', label=f'{h:g}时')
    axes[1].plot(list(months), ga, marker='o', label=f'{h:g}时')
axes[0].set_title('太阳高度角'); axes[0].set_xlabel('月'); axes[0].legend(fontsize=8); axes[0].grid(True, alpha=0.3)
axes[1].set_title('太阳方位角'); axes[1].set_xlabel('月'); axes[1].legend(fontsize=8); axes[1].grid(True, alpha=0.3)
plt.tight_layout(); plt.show()
""")

md(r"""## 2. 光学效率模型

\[
\eta=\eta_{sb}\,\eta_{cos}\,\eta_{at}\,\eta_{trunc}\,\eta_{ref},\quad \eta_{ref}=0.92
\]

- 余弦效率：由入射方向与镜面法向夹角确定；
- 大气透射率：$\eta_{at}=0.99321-0.0001176d+1.97\times10^{-8}d^2$；
- 阴影遮挡：塔影 + 邻镜遮挡近似；
- 截断效率：太阳张角光斑与圆柱集热器有效孔径比较。
""")

md(r"""## 3. 问题一：给定布局评价

吸收塔位于圆心，定日镜 $6\times6\,\mathrm{m}$，安装高度 $4\,\mathrm{m}$，位置见附件（1745面）。
""")

code(r"""
xy = load_attachment(str(ROOT / 'data' / 'attachment.xlsx'))
cfg1 = make_uniform_config(xy, 6.0, 6.0, 4.0, np.array([0.0, 0.0]))
r1 = evaluate_annual(cfg1, fast=False)
print(pd.DataFrame([{
    '年平均光学效率': round(r1['eta'],4),
    '年平均余弦效率': round(r1['cos'],4),
    '年平均阴影遮挡效率': round(r1['sb'],4),
    '年平均截断效率': round(r1['trunc'],4),
    '年平均输出热功率(MW)': round(r1['power_mw'],4),
    '单位面积年平均输出热功率(kW/m2)': round(r1['unit_kw'],4),
}]))
pd.DataFrame(r1['monthly']).assign(日期=lambda d: d['month'].astype(str)+'月21日')
""")

code(r"""
fig, ax = plt.subplots(figsize=(6,6))
th = np.linspace(0, 2*np.pi, 400)
ax.plot(FIELD_R*np.cos(th), FIELD_R*np.sin(th), 'k-')
ax.scatter(xy[:,0], xy[:,1], s=4, alpha=0.75)
ax.scatter([0],[0], c='r', s=80, marker='^', label='吸收塔')
ax.set_aspect('equal'); ax.set_title('问题一布局'); ax.legend(); ax.grid(True, alpha=0.25)
plt.show()

m = [x['month'] for x in r1['monthly']]
plt.figure(figsize=(8,4))
plt.plot(m,[x['eta'] for x in r1['monthly']], 'o-', label='光学')
plt.plot(m,[x['cos'] for x in r1['monthly']], 's-', label='余弦')
plt.plot(m,[x['sb'] for x in r1['monthly']], '^-', label='遮挡')
plt.plot(m,[x['trunc'] for x in r1['monthly']], 'd-', label='截断')
plt.ylim(0.4,1.05); plt.legend(); plt.grid(True, alpha=0.3); plt.title('问题一月平均效率'); plt.show()
""")

md(r"""## 4. 问题二：统一尺寸布局优化

目标：在年平均输出热功率 $\ge 60\,\mathrm{MW}$ 条件下，最大化单位镜面面积年平均输出热功率。

决策变量：塔位 $(x_t,y_t)$、统一边长 $w$、安装高度 $z$、同心圆排布位置。约束：镜面边长 $2\sim8\,\mathrm{m}$，安装高度 $2\sim6\,\mathrm{m}$ 且 $z>w/2$，邻镜间距 $\ge w+5$，塔周 $100\,\mathrm{m}$ 空地，镜场半径 $350\,\mathrm{m}$。
""")

code(r"""
# 读取已优化结果（由 code/finalize2.py 生成）；亦可在此重跑搜索
with open(ROOT/'code'/'results.json', encoding='utf-8') as f:
    summary = json.load(f)
print('问题二设计:', summary['q2'])

tower = np.array(summary['q2']['tower'])
w = summary['q2']['w']; z = summary['q2']['z']
xy2 = concentric_layout(tower, w, gap=5.0)
cfg2 = make_uniform_config(xy2, w, w, z, tower)
r2 = evaluate_annual(cfg2, fast=False)
print(pd.DataFrame([{
    '年平均光学效率': round(r2['eta'],4),
    '年平均输出热功率(MW)': round(r2['power_mw'],4),
    '单位面积年平均输出热功率(kW/m2)': round(r2['unit_kw'],4),
    '数目': r2['n'],
}]))

fig, ax = plt.subplots(figsize=(6,6))
ax.plot(FIELD_R*np.cos(th), FIELD_R*np.sin(th), 'k-')
ax.scatter(xy2[:,0], xy2[:,1], s=3, alpha=0.7)
ax.scatter([tower[0]],[tower[1]], c='r', s=80, marker='^')
ax.set_aspect('equal'); ax.set_title('问题二优化布局'); ax.grid(True, alpha=0.25); plt.show()
""")

md(r"""## 5. 问题三：分层变尺寸/变高度

在同心圆骨架上，允许各环定日镜尺寸与安装高度不同，额定功率仍为 $60\,\mathrm{MW}$，继续最大化单位面积年平均输出热功率。
""")

code(r"""
print('问题三设计:', summary['q3'])
# 用 result3.xlsx 复原布局并复核
df3 = pd.read_excel(ROOT/'result3.xlsx', sheet_name='定日镜')
par3 = pd.read_excel(ROOT/'result3.xlsx', sheet_name='参数')
tower3 = np.array([par3.iloc[0,0], par3.iloc[0,1]], dtype=float)
cfg3 = FieldConfig(
    xy=df3[['x坐标 (m)','y坐标 (m)']].to_numpy(float),
    w=df3['定日镜尺寸 (m)'].to_numpy(float),
    h=df3['定日镜尺寸 (m)'].to_numpy(float),
    z=df3['安装高度 (m)'].to_numpy(float),
    tower_xy=tower3,
)
r3 = evaluate_annual(cfg3, fast=False)
print(pd.DataFrame([{
    '年平均光学效率': round(r3['eta'],4),
    '年平均输出热功率(MW)': round(r3['power_mw'],4),
    '单位面积年平均输出热功率(kW/m2)': round(r3['unit_kw'],4),
    '数目': r3['n'],
}]))

fig, axes = plt.subplots(1,2, figsize=(10,4))
axes[0].bar(['问题一','问题二','问题三'], [r1['unit_kw'], r2['unit_kw'], r3['unit_kw']],
            color=['#4c72b0','#55a868','#c44e52'])
axes[0].set_title('单位面积年平均输出热功率'); axes[0].set_ylabel('kW/m$^2$'); axes[0].grid(True, axis='y', alpha=0.3)
axes[1].bar(['问题一','问题二','问题三'], [r1['power_mw'], r2['power_mw'], r3['power_mw']],
            color=['#4c72b0','#55a868','#c44e52'])
axes[1].axhline(60, color='k', ls='--', label='额定60MW')
axes[1].set_title('年平均输出热功率'); axes[1].legend(); axes[1].grid(True, axis='y', alpha=0.3)
plt.tight_layout(); plt.show()
""")

md(r"""## 6. 主要结论

| 问题 | 年平均光学效率 | 年平均功率(MW) | 单位面积功率(kW/m²) |
|:---:|:---:|:---:|:---:|
| 1 | 0.5668 | 34.60 | 0.5508 |
| 2 | 0.4994 | 60.74 | 0.4851 |
| 3 | 0.5163 | 60.38 | 0.5112 |

问题一功率未达额定；问题二通过增大镜面与加密同心圆排布达到并超过 $60\,\mathrm{MW}$；问题三按环调节尺寸后，单位面积功率相对问题二提升约 $5.4\%$。
""")

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'pygments_lexer': 'ipython3'},
}
out = ROOT / 'A题_定日镜场的优化设计.ipynb'
with open(out, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print('wrote', out)
