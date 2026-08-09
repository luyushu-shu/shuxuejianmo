# -*- coding: utf-8 -*-
"""为问题3–5生成补充图表（与论文详细求解配套）。"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
IMG = ROOT / "图片"
TAB = ROOT / "表格"
for d in (FIG, IMG, TAB):
    d.mkdir(exist_ok=True)

# 从 notebook 逻辑复用：直接读 result 并重建关键量
G, V_MISSILE, V_SINK, R_SMOKE, T_SMOKE = 9.8, 300.0, 3.0, 10.0, 20.0
FAKE = np.array([0.0, 0.0, 0.0])
TRUE_CENTER = np.array([0.0, 200.0, 5.0])
MISSILES = {
    "M1": np.array([20000.0, 0.0, 2000.0]),
    "M2": np.array([19000.0, 600.0, 2100.0]),
    "M3": np.array([18000.0, -600.0, 1900.0]),
}
UAVS = {
    "FY1": np.array([17800.0, 0.0, 1800.0]),
    "FY2": np.array([12000.0, 1400.0, 1400.0]),
    "FY3": np.array([6000.0, -3000.0, 700.0]),
    "FY4": np.array([11000.0, 2000.0, 1800.0]),
    "FY5": np.array([13000.0, -2000.0, 1300.0]),
}


def unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else v


def missile_hit_time(p0):
    return float(np.linalg.norm(p0 - FAKE) / V_MISSILE)


def missile_pos(t, p0):
    e = unit(FAKE - p0)
    if np.isscalar(t):
        return p0 + V_MISSILE * float(t) * e
    t = np.asarray(t, dtype=float)
    return p0[None, :] + (V_MISSILE * t)[:, None] * e[None, :]


def point_to_segment_dist_batch(p, a, b):
    ab = b[None, :] - a
    L2 = np.sum(ab * ab, axis=1)
    s = np.zeros(len(p))
    ok = L2 > 1e-18
    ap = p - a
    s[ok] = np.clip(np.sum(ap[ok] * ab[ok], axis=1) / L2[ok], 0.0, 1.0)
    return np.linalg.norm(p - (a + s[:, None] * ab), axis=1)


def heading_from_deg(deg):
    th = np.deg2rad(deg)
    return np.array([np.cos(th), np.sin(th), 0.0])


def bombs_from_result_row(row, uav_col=None):
    uav = row[uav_col] if uav_col else "FY1"
    uav0 = UAVS[uav]
    h = heading_from_deg(row["无人机运动方向"])
    speed = float(row["无人机运动速度 (m/s)"])
    pd = np.array(
        [
            row["烟幕干扰弹投放点的x坐标 (m)"],
            row["烟幕干扰弹投放点的y坐标 (m)"],
            row["烟幕干扰弹投放点的z坐标 (m)"],
        ]
    )
    pe = np.array(
        [
            row["烟幕干扰弹起爆点的x坐标 (m)"],
            row["烟幕干扰弹起爆点的y坐标 (m)"],
            row["烟幕干扰弹起爆点的z坐标 (m)"],
        ]
    )
    # 反推 td, tf
    # pd = uav0 + speed*td*h  => td from horizontal
    disp = pd - uav0
    td = float(np.dot(disp[:2], h[:2]) / max(speed, 1e-9))
    td = max(0.0, td)
    # pe_xy = pd_xy + speed*tf*h_xy
    disp2 = pe[:2] - pd[:2]
    tf = float(np.dot(disp2, h[:2]) / max(speed, 1e-9))
    tf = max(0.05, tf)
    return {
        "id": int(row["烟幕干扰弹编号"]),
        "uav": uav,
        "speed": speed,
        "heading": h,
        "t_drop": td,
        "t_fuse": tf,
        "t_det": td + tf,
        "drop": pd,
        "det": pe,
        "missile": row.get("干扰的导弹编号", "M1"),
    }


def series_multi(bombs, p_missile, dt=0.01):
    t_hit = missile_hit_time(p_missile)
    t0 = min(b["t_det"] for b in bombs)
    t1 = min(max(b["t_det"] + T_SMOKE for b in bombs), t_hit)
    ts = np.arange(t0, t1 + 1e-12, dt)
    mpos = missile_pos(ts, p_missile)
    min_d = np.full(len(ts), np.inf)
    any_mask = np.zeros(len(ts), dtype=bool)
    per = []
    for b in bombs:
        te, pe = b["t_det"], b["det"]
        mask = (ts >= te) & (ts <= te + T_SMOKE)
        d_full = np.full(len(ts), np.nan)
        if np.any(mask):
            idx = np.where(mask)[0]
            c = np.column_stack(
                [
                    np.full(len(idx), pe[0]),
                    np.full(len(idx), pe[1]),
                    pe[2] - V_SINK * (ts[idx] - te),
                ]
            )
            d = point_to_segment_dist_batch(c, mpos[idx], TRUE_CENTER)
            d_full[idx] = d
            min_d[idx] = np.minimum(min_d[idx], d)
            any_mask[idx] |= d <= R_SMOKE
        per.append((b, d_full, (~np.isnan(d_full)) & (d_full <= R_SMOKE)))
    return ts, min_d, any_mask, per, float(any_mask.sum() * dt)


def savefig(fig, name_en, name_zh):
    fig.savefig(FIG / name_en, dpi=180, bbox_inches="tight")
    fig.savefig(IMG / name_zh, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_q3(df1):
    bombs = [bombs_from_result_row(r) for _, r in df1.iterrows()]
    for b in bombs:
        b["missile"] = "M1"
    ts, min_d, mask, per, J = series_multi(bombs, MISSILES["M1"], 0.01)

    # 分弹距离曲线
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    colors = ["#4C78A8", "#F58518", "#54A24B"]
    for (b, d_full, m), c in zip(per, colors):
        ax.plot(ts, d_full, color=c, lw=1.4, label=f"弹{b['id']} 距离")
        ax.axvline(b["t_det"], color=c, ls=":", alpha=0.7)
    ax.plot(ts, min_d, "k-", lw=1.8, label="多弹取最小距离")
    ax.axhline(10, color="crimson", ls="--", label="阈值 10 m")
    ax.fill_between(ts, 0, 10, where=mask, color="C2", alpha=0.2, label="并集有效区")
    ax.set_xlabel("时间 t / s")
    ax.set_ylabel("距离 / m")
    ax.set_title("问题3：各弹到视线距离与并集有效区间")
    ax.set_ylim(0, 80)
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    savefig(fig, "q3_per_bomb_distance.png", "问题3_各弹距离与并集.png")

    # 甘特式时序
    fig, ax = plt.subplots(figsize=(9, 3.2))
    for i, (b, _, m) in enumerate(per):
        # 有效段
        if m.any():
            # 找连续段
            idx = np.where(m)[0]
            starts = [idx[0]]
            for a, bb in zip(idx[:-1], idx[1:]):
                if bb != a + 1:
                    starts.append(bb)
            # simpler: plot scatter of effective
            ax.plot(ts[m], np.full(m.sum(), i + 1), "|", color=colors[i], ms=10)
        ax.scatter([b["t_det"]], [i + 1], marker="*", s=120, color=colors[i], zorder=5)
        ax.text(b["t_det"], i + 1.15, f"起爆{b['t_det']:.2f}s", color=colors[i], fontsize=8)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["弹1", "弹2", "弹3"])
    ax.set_xlabel("时间 t / s")
    ax.set_title(f"问题3：三弹有效遮蔽时序（并集 J={J:.2f}s）")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "q3_timeline.png", "问题3_有效遮蔽时序图.png")

    # 与问题1/2对比
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    names = ["问题1\n单弹给定", "问题2\n单弹优化", "问题3\n同机三弹"]
    vals = [1.43, 4.71, J]
    bars = ax.bar(names, vals, color=["#4C78A8", "#F58518", "#54A24B"], width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}s", ha="center")
    ax.set_ylabel("有效遮蔽时长 / s")
    ax.set_title("问题1–3 遮蔽时长对比")
    ax.set_ylim(0, max(vals) * 1.25)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "q1q2q3_duration_compare.png", "问题1至3_遮蔽时长对比图.png")

    # 导出明细
    rows = []
    for b in bombs:
        rows.append(
            {
                "弹号": b["id"],
                "投放时刻(s)": round(b["t_drop"], 3),
                "引信延时(s)": round(b["t_fuse"], 3),
                "起爆时刻(s)": round(b["t_det"], 3),
                "投放点": f"({b['drop'][0]:.2f},{b['drop'][1]:.2f},{b['drop'][2]:.2f})",
                "起爆点": f"({b['det'][0]:.2f},{b['det'][1]:.2f},{b['det'][2]:.2f})",
            }
        )
    pd.DataFrame(rows).to_excel(TAB / "问题3_三弹时序明细表.xlsx", index=False)
    return bombs, J


def plot_q4(df2):
    bombs = [bombs_from_result_row(r, "无人机编号") for _, r in df2.iterrows()]
    ts, min_d, mask, per, J = series_multi(bombs, MISSILES["M1"], 0.01)
    Ji = []
    for b, _, m in per:
        Ji.append(float(m.sum() * 0.01))

    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    colors = ["#4C78A8", "#F58518", "#54A24B"]
    for (b, d_full, m), c in zip(per, colors):
        ax.plot(ts, d_full, color=c, lw=1.3, label=f"{b['uav']} 距离")
        ax.axvline(b["t_det"], color=c, ls=":", alpha=0.75)
    ax.plot(ts, min_d, "k-", lw=1.7, label="三机取最小")
    ax.axhline(10, color="crimson", ls="--")
    ax.fill_between(ts, 0, 10, where=mask, color="C2", alpha=0.22, label="并集有效区")
    ax.set_ylim(0, 100)
    ax.set_xlabel("时间 t / s")
    ax.set_ylabel("距离 / m")
    ax.set_title("问题4：三机各自距离曲线与并集有效区")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    savefig(fig, "q4_per_uav_distance.png", "问题4_各机距离与并集.png")

    # 单弹 vs 并集
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    names = [b["uav"] + "单弹" for b in bombs] + ["三机并集"]
    vals = Ji + [J]
    colors = ["#4C78A8", "#F58518", "#54A24B", "#E45756"]
    bars = ax.bar(names, vals, color=colors, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.15, f"{v:.2f}s", ha="center")
    ax.set_ylabel("有效遮蔽时长 / s")
    ax.set_title("问题4：单机贡献与并集时长")
    ax.set_ylim(0, max(vals) * 1.2)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "q4_union_vs_single.png", "问题4_单机与并集对比图.png")

    # 时序带
    fig, ax = plt.subplots(figsize=(9, 3.0))
    for i, (b, _, m) in enumerate(per):
        ax.plot(ts[m], np.full(m.sum(), i + 1), "|", color=colors[i], ms=9)
        ax.scatter([b["t_det"]], [i + 1], marker="*", s=110, color=colors[i])
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels([b["uav"] for b in bombs])
    ax.set_xlabel("时间 t / s")
    ax.set_title(f"问题4：三机有效遮蔽时序（并集 J={J:.2f}s）")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "q4_timeline.png", "问题4_有效遮蔽时序图.png")

    rows = []
    for b, j in zip(bombs, Ji):
        rows.append(
            {
                "无人机": b["uav"],
                "速度(m/s)": round(b["speed"], 3),
                "投放时刻(s)": round(b["t_drop"], 3),
                "引信延时(s)": round(b["t_fuse"], 3),
                "起爆时刻(s)": round(b["t_det"], 3),
                "单弹遮蔽(s)": round(j, 3),
                "投放点": f"({b['drop'][0]:.2f},{b['drop'][1]:.2f},{b['drop'][2]:.2f})",
                "起爆点": f"({b['det'][0]:.2f},{b['det'][1]:.2f},{b['det'][2]:.2f})",
            }
        )
    pd.DataFrame(rows).to_excel(TAB / "问题4_三机策略明细表.xlsx", index=False)
    return bombs, Ji, J


def plot_q5(df3):
    by_m = {"M1": [], "M2": [], "M3": []}
    for _, r in df3.iterrows():
        b = bombs_from_result_row(r, "无人机编号")
        by_m[b["missile"]].append(b)

    durations = {}
    for m, bombs in by_m.items():
        ts, min_d, mask, per, J = series_multi(bombs, MISSILES[m], 0.02)
        durations[m] = J
        fig, ax = plt.subplots(figsize=(9, 3.6))
        ax.plot(ts, min_d, lw=1.6)
        ax.axhline(10, color="r", ls="--")
        ax.fill_between(ts, 0, 10, where=mask, color="C2", alpha=0.25)
        for b in bombs:
            ax.axvline(b["t_det"], ls=":", alpha=0.6)
        ax.set_title(f"问题5：{m} 遮蔽距离曲线（J={J:.2f}s，弹数{len(bombs)}）")
        ax.set_xlabel("时间 t / s")
        ax.set_ylabel("距离 / m")
        ax.set_ylim(0, 80)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        savefig(fig, f"q5_{m.lower()}_distance.png", f"问题5_{m}_遮蔽距离曲线.png")

    # 分配示意柱状
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    names = ["M1\n(FY1+FY4)", "M2\n(FY2)", "M3\n(FY3+FY5)", "合计"]
    vals = [durations["M1"], durations["M2"], durations["M3"], sum(durations.values())]
    bars = ax.bar(names, vals, color=["#4C78A8", "#F58518", "#54A24B", "#B279A2"], width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.2, f"{v:.2f}s", ha="center")
    ax.set_ylabel("有效遮蔽时长 / s")
    ax.set_title("问题5：任务分配与各导弹遮蔽时长")
    ax.set_ylim(0, max(vals) * 1.2)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "q5_assignment_bar.png", "问题5_任务分配与遮蔽时长.png")

    # 俯视：五机与三导弹
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for name, p0 in MISSILES.items():
        t_hit = missile_hit_time(p0)
        t = np.linspace(0, t_hit, 80)
        traj = missile_pos(t, p0)
        ax.plot(traj[:, 0], traj[:, 1], lw=1.2, label=f"{name}轨迹")
        ax.scatter(p0[0], p0[1], marker="x", s=50)
    ax.scatter(0, 0, c="k", marker="s", s=40, label="假目标")
    ax.add_patch(plt.Circle((0, 200), 7, fill=False, color="g", lw=1.5, label="真目标"))
    cmap = {"FY1": "C0", "FY2": "C1", "FY3": "C2", "FY4": "C3", "FY5": "C4"}
    for _, r in df3.iterrows():
        u = r["无人机编号"]
        ax.scatter(UAVS[u][0], UAVS[u][1], marker="^", c=cmap[u], s=55)
        ax.scatter(
            r["烟幕干扰弹起爆点的x坐标 (m)"],
            r["烟幕干扰弹起爆点的y坐标 (m)"],
            marker="*",
            c=cmap[u],
            s=70,
        )
    for u, c in cmap.items():
        ax.scatter([], [], marker="^", c=c, label=u)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("X / m")
    ax.set_ylabel("Y / m")
    ax.set_title("问题5：五机起点、起爆点与三导弹水平态势")
    ax.legend(fontsize=7, ncol=3, loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    savefig(fig, "q5_topview.png", "问题5_五机三导弹俯视图.png")

    pd.DataFrame(
        [
            {"导弹": m, "弹数": len(by_m[m]), "有效遮蔽时长(s)": round(durations[m], 2)}
            for m in ["M1", "M2", "M3"]
        ]
        + [{"导弹": "合计", "弹数": len(df3), "有效遮蔽时长(s)": round(sum(durations.values()), 2)}]
    ).to_excel(TAB / "问题5_各导弹结果汇总表.xlsx", index=False)
    return durations


def main():
    df1 = pd.read_excel(ROOT / "result1.xlsx")
    df2 = pd.read_excel(ROOT / "result2.xlsx")
    df3 = pd.read_excel(ROOT / "result3.xlsx")
    print("plot q3...")
    bombs3, J3 = plot_q3(df1)
    print("J3", J3)
    for b in bombs3:
        print(b["id"], b["t_drop"], b["t_fuse"], b["t_det"])
    print("plot q4...")
    bombs4, Ji, J4 = plot_q4(df2)
    print("J4", J4, Ji)
    for b in bombs4:
        print(b["uav"], b["t_drop"], b["t_fuse"], b["t_det"], b["speed"])
    print("plot q5...")
    d5 = plot_q5(df3)
    print(d5)
    print("done")


if __name__ == "__main__":
    main()
