# 数学建模

课程算法练习、课程作业，以及南京工业大学相关赛训 / 校赛模板。这是代码与讲义仓库，不是 2026 国赛 A 题仓库。

- GitHub：https://github.com/luyushu-shu/shuxuejianmo （Private）
- **默认分支和工作分支都是 `stu`**（仓库首页的 README 也在这条分支上）
- SSH：`git@github.com:luyushu-shu/shuxuejianmo.git`

另外两个仓库：

| 仓库 | 作用 |
| --- | --- |
| [cumcm-2026-a](https://github.com/luyushu-shu/cumcm-2026-a) | 2026 国赛 A 题药材烘干（论文、求解器、支撑材料） |
| [obsidian-vault](https://github.com/luyushu-shu/obsidian-vault) | 知识库；课程目录用 Windows 联接挂进去，不把本库文件再提交一遍 |

---

## 1. 克隆

本机 HTTPS 访问 `github.com` 容易在代理 / TLS 上失败，请用 SSH：

```bash
git clone -b stu git@github.com:luyushu-shu/shuxuejianmo.git
cd shuxuejianmo
```

如果已经克隆过但远程还是 HTTPS，改成：

```bash
git remote set-url origin git@github.com:luyushu-shu/shuxuejianmo.git
git checkout stu
git pull
```

不需要 Git LFS。体积主要来自作业 PDF、zip 和图片，比国赛仓库小得多。

---

## 2. 仓库分成两块

1. **`作业/`**：要交的报告、代码、数据、笔记本。一份作业一个子目录，论文入口几乎都是该目录下的 `main.tex`。
2. **根目录带顿号编号的文件夹**（`2、Topsis法` 等）：课程讲义、MATLAB / Python 示例、大纲 Markdown。用来练算法，不是某次作业的提交包。

此外：

- `作业/南京工业大学数学建模校赛论文/`：校赛 `njtechmcmthesis` 模板。
- `作业/答题模版latex和word版各一份。/`：答题用 tex / Word 模板。
- `ECNU2NJTECH/`：从华东师大模板迁到南京工业大学时的字体与编译说明。按其中 `ReadMeFirstStep.txt`：先安装 `STZHONGS` 字库，再用 **XeLaTeX** 编译 `main.tex`。

---

## 3. 作业一览

论文类作业默认 XeLaTeX。有的目录同时有分章 `ch*.tex` 和合订稿。

### 3.1 课程作业

| 目录 | 题目 | 主要入口 |
| --- | --- | --- |
| `作业/作业1/` | 融合测角、测距观测的空间目标定位（牛顿法 / 法方程迭代） | `main.tex` |
| `作业/作业2/` | 地下停车场应急人员定位（蓝牙 RSSI + 步行约束） | `main.tex`；C 代码在 `RssiPositioning_C_Code/`；答辩 `defense_ppt.tex` |
| `作业/作业3/` | 自动化车床刀具检查与换刀策略 | `main.tex`；合订稿 `作业3_刀具问题建模.tex` |
| `作业/作业4/` | FAST 主动反射面形状调节 | `main.tex`；合订稿 `作业4_FAST主动反射面建模.tex` |
| `作业/作业5/` | 高阶泰勒级数法与牛顿类迭代（`CTaylorSeriesSecond20250324`） | `main.tex` |
| `作业/作业6/` | 常微分方程系统的高精度参数辨识 | `main.tex` |

作业 2 起部分文档类文件会 `\documentclass{../作业1/MathematicalModelCaseStudyReport}`，编译工作目录必须是该作业自己的文件夹，并保证作业 1 里的类文件还在。

### 3.2 南京工业大学暑假集训

| 目录 | 题目 | 主要入口 |
| --- | --- | --- |
| `作业/南京工业大学暑假集训/作业一/` | 烟幕干扰弹投放策略 | `main.tex`，`A题_烟幕干扰弹投放策略.ipynb`，`code/` |
| `作业/南京工业大学暑假集训/作业二/` | 定日镜场优化设计 | `main.tex`，`A题_定日镜场的优化设计.ipynb`，`code/heliostat_field.py` 等 |

作业二还带 `data/`（镜场表、附件 xlsx）、`figures/` / `图片/`、`表格/` 以及 `result2.xlsx` / `result3.xlsx`。`cumcmthesis.cls` 在作业一、作业二目录各有一份，编译时用**当前作业目录**里的那份。

集训目录里另有题目 zip、`_ref2023.txt`、`_build_notebook.py`（由计算结果生成笔记本）。不要把 `code/__pycache__/` 再提交上来。

---

## 4. 课程算法目录

这些文件夹名称以「数字、顿号」开头。大纲已是 Markdown 的，可以在编辑器或 Obsidian 联接里直接打开。

| 目录 | 内容 | 常见文件 |
| --- | --- | --- |
| `2、Topsis法` | TOPSIS | Python / MATLAB |
| `3、熵权法` | 熵权 | Python / MATLAB |
| `4、模糊综合评价` | 模糊综合 | Python / MATLAB |
| `5、灰色关联分析` | 灰色关联、正向化 | `.py` / `.m` |
| `8、多元线性回归分析` | 多元线性回归 | `大纲_multiple_regression.md`、notebook、csv |
| `9、非线性回归分析` | 非线性回归 | `非线性回归分析.md`、人口 / 咖啡降温 notebook |
| `10、灰色预测分析` | GM 预测 | 大纲 md、GDP / 销售额 notebook |
| `11、时间序列模型ARIMA` | ARIMA | 大纲 md、两个案例 notebook |
| `12、蒙特卡洛算法` | 蒙特卡洛 | 大纲 md（文件名带 `#`，用资源管理器或文件列表打开更稳）、练习 py / ipynb |
| `13、马尔科夫预测算法` | 马尔可夫 | `case1.ipynb`、`case2.ipynb` |
| `23、智能优化-遗传优化` | 遗传算法 | MATLAB，含 Sheffield `gatbx` 工具箱 |

讲义来源混有课程材料和公开示例代码，引用或改写进作业时自己核对许可与是否需要重写。

---

## 5. 编译与运行习惯

- **LaTeX**：XeLaTeX。中文模板依赖本机字体；校赛模板按 `ECNU2NJTECH` 说明装字。
- **Python**：作业一 / 集训脚本直接跑对应 `code/`。不要提交 `__pycache__/`。
- **MATLAB**：算法目录和遗传工具箱用 MATLAB 打开该文件夹。`gatbx` 是旧版工具箱，文档在其 `doc/`。
- **C**：作业 2 的 RSSI 定位在 `RssiPositioning_C_Code/AAA/`，可用目录里的 `gccbianyi.bat`。

改作业结论时，把数字留在该作业的 `main.tex` 或 result 表里；可复用的方法再提炼到知识库 `01 领域`，不要把整份讲义复制进 Obsidian。

---

## 6. 和 Obsidian 的关系

知识库可以把本目录联接为 `06 工作区/数学建模`，两边改的是同一份文件。因此：

- 在 Obsidian 文件列表里删联接下面的作业 = 删本仓库文件；
- 知识库的 `.gitignore` 已经排除该联接，`obsidian-vault` 里不会出现本库的 `.git` 或代码；
- 本库继续在这里用 Git，不要在知识库根目录对联接做 `git add`。

---

## 7. 提交约定

- 工作都往 **`stu`** 推：`git push origin stu`。
- 不要把默认分支改回空的 `main`，否则 GitHub 首页又看不到这份 README。
- 新增大 zip / PDF 前看单文件是否超过 100 MiB；本库目前未开 LFS。
- 编译产生的 `.aux`、`.log`、`.toc` 等可以留在本地；能不推就不推。
