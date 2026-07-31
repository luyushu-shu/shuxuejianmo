"""生成问题1、问题2的图片与表格（中文文件名）。"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

G = 9.8
V_MISSILE = 300.0
V_SINK = 3.0
R_SMOKE = 10.0
T_SMOKE = 20.0

FAKE = np.array([0.0, 0.0, 0.0])
TRUE_CENTER = np.array([0.0, 200.0, 5.0])
TRUE_BOTTOM = np.array([0.0, 200.0, 0.0])
TRUE_R, TRUE_H = 7.0, 10.0
M1 = np.array([20000.0, 0.0, 2000.0])
FY1 = np.array([17800.0, 0.0, 1800.0])

IMG_DIR = Path("图片")
TAB_DIR = Path("表格")
IMG_DIR.mkdir(exist_ok=True)
TAB_DIR.mkdir(exist_ok=True)


def unit(v):
    return v / np.linalg.norm(v)


def missile_hit_time(p0=M1):
    return float(np.linalg.norm(p0 - FAKE) / V_MISSILE)


def missile_pos(t, p0=M1):
    return p0 + V_MISSILE * t * unit(FAKE - p0)


def heading_to_fake(p=FY1):
    d = FAKE[:2] - p[:2]
    return unit(np.array([d[0], d[1], 0.0]))


def heading_from_angle(theta):
    return np.array([np.cos(theta), np.sin(theta), 0.0])


def drop_point(speed, heading, t_drop, p0=FY1):
    h = unit(np.array([heading[0], heading[1], 0.0]))
    return p0 + speed * t_drop * h


def det_point(speed, heading, t_drop, t_fuse, p0=FY1):
    pd = drop_point(speed, heading, t_drop, p0)
    h = unit(np.array([heading[0], heading[1], 0.0]))
    v = speed * h
    return np.array(
        [pd[0] + v[0] * t_fuse, pd[1] + v[1] * t_fuse, pd[2] - 0.5 * G * t_fuse**2]
    )


def cloud_center(p_det, t_det, t):
    return np.array([p_det[0], p_det[1], p_det[2] - V_SINK * (t - t_det)])


def point_to_segment_dist(p, a, b):
    ab = b - a
    L2 = float(np.dot(ab, ab))
    if L2 < 1e-18:
        return float(np.linalg.norm(p - a))
    s = float(np.clip(np.dot(p - a, ab) / L2, 0.0, 1.0))
    return float(np.linalg.norm(p - (a + s * ab)))


def shielding_series(speed, heading, t_drop, t_fuse, dt=0.01):
    t_det = t_drop + t_fuse
    p_det = det_point(speed, heading, t_drop, t_fuse)
    t_hit = missile_hit_time()
    t0, t1 = t_det, min(t_det + T_SMOKE, t_hit)
    if t1 <= t0 or p_det[2] <= 0:
        return np.array([]), np.array([]), np.array([]), 0.0
    ts = np.arange(t0, t1 + 1e-12, dt)
    dists = np.zeros(len(ts))
    mask = np.zeros(len(ts), dtype=bool)
    for i, t in enumerate(ts):
        d = point_to_segment_dist(cloud_center(p_det, t_det, t), missile_pos(t), TRUE_CENTER)
        dists[i] = d
        mask[i] = d <= R_SMOKE
    return ts, dists, mask, float(mask.sum() * dt)


def effective_duration(speed, heading, t_drop, t_fuse, dt=0.01):
    return shielding_series(speed, heading, t_drop, t_fuse, dt)[3]


def optimize_q2():
    best = (0.0, None)
    for theta in np.linspace(np.pi - 0.25, np.pi + 0.25, 11):
        for v in [70, 85, 100, 115, 130, 140]:
            for td in np.linspace(0.3, 10.0, 12):
                for tf in np.linspace(1.0, 7.0, 11):
                    pe = det_point(v, heading_from_angle(theta), td, tf)
                    if pe[2] <= 2:
                        continue
                    J = effective_duration(v, heading_from_angle(theta), td, tf, dt=0.05)
                    if J > best[0]:
                        best = (J, (theta, v, td, tf))
    theta0, v0, td0, tf0 = best[1]
    for theta in np.linspace(theta0 - 0.08, theta0 + 0.08, 9):
        for v in np.linspace(max(70, v0 - 12), min(140, v0 + 12), 7):
            for td in np.linspace(max(0.05, td0 - 1.0), td0 + 1.0, 9):
                for tf in np.linspace(max(0.4, tf0 - 1.0), tf0 + 1.0, 9):
                    pe = det_point(v, heading_from_angle(theta), td, tf)
                    if pe[2] <= 2:
                        continue
                    J = effective_duration(v, heading_from_angle(theta), td, tf, dt=0.03)
                    if J > best[0]:
                        best = (J, (theta, float(v), float(td), float(tf)))
    return best


def draw_cylinder(ax, color="tab:green", alpha=0.25):
    theta = np.linspace(0, 2 * np.pi, 40)
    z = np.linspace(0, TRUE_H, 12)
    th, zz = np.meshgrid(theta, z)
    x = TRUE_BOTTOM[0] + TRUE_R * np.cos(th)
    y = TRUE_BOTTOM[1] + TRUE_R * np.sin(th)
    ax.plot_surface(x, y, zz, color=color, alpha=alpha, linewidth=0)


def draw_sphere(ax, center, radius=R_SMOKE, color="gray", alpha=0.35):
    u = np.linspace(0, 2 * np.pi, 24)
    v = np.linspace(0, np.pi, 16)
    uu, vv = np.meshgrid(u, v)
    x = center[0] + radius * np.cos(uu) * np.sin(vv)
    y = center[1] + radius * np.sin(uu) * np.sin(vv)
    z = center[2] + radius * np.cos(vv)
    ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0)


def plot_distance(ts, dists, mask, title, path):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(ts, dists, color="C0", lw=1.8, label="烟幕球心到导弹—真目标视线距离")
    ax.axhline(R_SMOKE, color="crimson", ls="--", lw=1.5, label="有效半径 10 m")
    if len(ts):
        ax.fill_between(ts, 0, R_SMOKE, where=mask, color="C2", alpha=0.28, label="有效遮蔽区间")
    ax.set_xlabel("时间 t / s", fontsize=12)
    ax.set_ylabel("距离 / m", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_situation_3d(speed, heading, t_drop, t_fuse, title, path, sample_t=None):
    t_det = t_drop + t_fuse
    pd = drop_point(speed, heading, t_drop)
    pe = det_point(speed, heading, t_drop, t_fuse)
    t_hit = missile_hit_time()
    if sample_t is None:
        ts, _, mask, _ = shielding_series(speed, heading, t_drop, t_fuse, dt=0.02)
        sample_t = float(ts[mask][len(ts[mask]) // 2]) if mask.any() else float(t_det + 0.5)

    t_uav = np.linspace(0, max(t_drop, 0.1), 40)
    uav_traj = np.array([FY1 + speed * t * unit(np.array([heading[0], heading[1], 0.0])) for t in t_uav])
    t_mis = np.linspace(0, min(t_hit, 60), 80)
    mis_traj = np.array([missile_pos(t) for t in t_mis])
    m_now = missile_pos(sample_t)
    c_now = cloud_center(pe, t_det, sample_t)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(mis_traj[:, 0], mis_traj[:, 1], mis_traj[:, 2], "r-", lw=1.6, label="导弹 M1 轨迹")
    ax.plot(uav_traj[:, 0], uav_traj[:, 1], uav_traj[:, 2], "b-", lw=1.6, label="无人机 FY1 轨迹")
    ax.scatter(*FAKE, c="k", s=40, marker="x", label="假目标")
    ax.scatter(*TRUE_CENTER, c="g", s=40, marker="o", label="真目标中心")
    draw_cylinder(ax)
    ax.scatter(*pd, c="C1", s=50, marker="^", label="投放点")
    ax.scatter(*pe, c="purple", s=50, marker="*", label="起爆点")
    draw_sphere(ax, c_now)
    ax.plot(
        [m_now[0], TRUE_CENTER[0]],
        [m_now[1], TRUE_CENTER[1]],
        [m_now[2], TRUE_CENTER[2]],
        "g--",
        lw=1.2,
        label="导弹—真目标视线",
    )
    ax.set_xlabel("X / m")
    ax.set_ylabel("Y / m")
    ax.set_zlabel("Z / m")
    ax.set_title(title + f"（示意时刻 t={sample_t:.2f}s）")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_topview(cases, title, path):
    fig, ax = plt.subplots(figsize=(9, 5))
    t_hit = missile_hit_time()
    t_mis = np.linspace(0, min(t_hit, 65), 100)
    mis = np.array([missile_pos(t) for t in t_mis])
    ax.plot(mis[:, 0], mis[:, 1], "r-", lw=1.5, label="导弹 M1 水平投影")
    ax.scatter(0, 0, c="k", marker="x", s=60, label="假目标")
    circ = plt.Circle((0, 200), TRUE_R, color="g", fill=False, lw=1.5, label="真目标底面")
    ax.add_patch(circ)
    colors = ["C0", "C1"]
    for (name, speed, heading, td, tf), color in zip(cases, colors):
        pe = det_point(speed, heading, td, tf)
        pd = drop_point(speed, heading, td)
        tu = np.linspace(0, max(td, 0.1), 30)
        h = unit(np.array([heading[0], heading[1], 0.0]))
        ut = np.array([FY1 + speed * t * h for t in tu])
        ax.plot(ut[:, 0], ut[:, 1], color=color, lw=1.5, label=f"{name} 无人机轨迹")
        ax.scatter(pd[0], pd[1], color=color, marker="^", s=55)
        ax.scatter(pe[0], pe[1], color=color, marker="*", s=90)
        smoke = plt.Circle((pe[0], pe[1]), R_SMOKE, color=color, alpha=0.15)
        ax.add_patch(smoke)
    ax.set_xlabel("X / m")
    ax.set_ylabel("Y / m")
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_compare_bar(J1, J2, path):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    names = ["问题1\n给定策略", "问题2\n优化策略"]
    vals = [J1, J2]
    bars = ax.bar(names, vals, color=["#4C78A8", "#F58518"], width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f} s", ha="center", va="bottom", fontsize=12)
    ax.set_ylabel("有效遮蔽时长 / s")
    ax.set_title("问题1与问题2有效遮蔽时长对比")
    ax.set_ylim(0, max(vals) * 1.25)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    print("计算问题1…")
    v1, td1, tf1 = 120.0, 1.5, 3.6
    h1 = heading_to_fake()
    ts1, d1, m1, J1 = shielding_series(v1, h1, td1, tf1, dt=0.01)
    pd1 = drop_point(v1, h1, td1)
    pe1 = det_point(v1, h1, td1, tf1)

    print("优化问题2…")
    _, params = optimize_q2()
    theta2, v2, td2, tf2 = params
    h2 = heading_from_angle(theta2)
    ts2, d2, m2, J2 = shielding_series(v2, h2, td2, tf2, dt=0.01)
    pd2 = drop_point(v2, h2, td2)
    pe2 = det_point(v2, h2, td2, tf2)
    print(f"J1={J1:.2f}s, J2={J2:.2f}s")

    print("绘制图片…")
    plot_distance(ts1, d1, m1, "问题1：烟幕球心到视线距离随时间变化", IMG_DIR / "问题1_遮蔽距离随时间变化.png")
    plot_distance(ts2, d2, m2, "问题2：烟幕球心到视线距离随时间变化", IMG_DIR / "问题2_遮蔽距离随时间变化.png")
    plot_situation_3d(v1, h1, td1, tf1, "问题1 三维空间态势", IMG_DIR / "问题1_三维空间态势图.png")
    plot_situation_3d(v2, h2, td2, tf2, "问题2 三维空间态势", IMG_DIR / "问题2_三维空间态势图.png")
    plot_topview(
        [("问题1", v1, h1, td1, tf1), ("问题2", v2, h2, td2, tf2)],
        "问题1与问题2投放/起爆位置俯视图",
        IMG_DIR / "问题1与问题2_水平俯视图.png",
    )
    plot_compare_bar(J1, J2, IMG_DIR / "问题1与问题2_遮蔽时长对比图.png")

    print("导出表格…")
    df_param = pd.DataFrame(
        [
            {"参数名称": "导弹速度 (m/s)", "取值": V_MISSILE},
            {"参数名称": "烟幕下沉速度 (m/s)", "取值": V_SINK},
            {"参数名称": "有效遮蔽半径 (m)", "取值": R_SMOKE},
            {"参数名称": "有效遮蔽时长上限 (s)", "取值": T_SMOKE},
            {"参数名称": "重力加速度 g (m/s^2)", "取值": G},
            {"参数名称": "真目标几何中心", "取值": str(tuple(TRUE_CENTER))},
            {"参数名称": "假目标位置", "取值": str(tuple(FAKE))},
            {"参数名称": "M1 初始位置", "取值": str(tuple(M1))},
            {"参数名称": "FY1 初始位置", "取值": str(tuple(FY1))},
        ]
    )
    df_param.to_excel(TAB_DIR / "模型基本参数表.xlsx", index=False)

    df_q1 = pd.DataFrame(
        [
            {"项目": "飞行速度 (m/s)", "数值": v1},
            {"项目": "航向单位向量", "数值": str(tuple(np.round(h1, 6)))},
            {"项目": "投放时刻 (s)", "数值": td1},
            {"项目": "引信延时 (s)", "数值": tf1},
            {"项目": "起爆时刻 (s)", "数值": td1 + tf1},
            {"项目": "投放点 X (m)", "数值": pd1[0]},
            {"项目": "投放点 Y (m)", "数值": pd1[1]},
            {"项目": "投放点 Z (m)", "数值": pd1[2]},
            {"项目": "起爆点 X (m)", "数值": pe1[0]},
            {"项目": "起爆点 Y (m)", "数值": pe1[1]},
            {"项目": "起爆点 Z (m)", "数值": pe1[2]},
            {"项目": "有效遮蔽时长 (s)", "数值": round(J1, 2)},
        ]
    )
    df_q1.to_excel(TAB_DIR / "问题1_计算结果表.xlsx", index=False)

    df_q2 = pd.DataFrame(
        [
            {"项目": "飞行速度 (m/s)", "数值": round(v2, 4)},
            {"项目": "航向角 (rad)", "数值": round(theta2, 6)},
            {"项目": "航向单位向量", "数值": str(tuple(np.round(h2, 6)))},
            {"项目": "投放时刻 (s)", "数值": round(td2, 4)},
            {"项目": "引信延时 (s)", "数值": round(tf2, 4)},
            {"项目": "起爆时刻 (s)", "数值": round(td2 + tf2, 4)},
            {"项目": "投放点 X (m)", "数值": round(pd2[0], 4)},
            {"项目": "投放点 Y (m)", "数值": round(pd2[1], 4)},
            {"项目": "投放点 Z (m)", "数值": round(pd2[2], 4)},
            {"项目": "起爆点 X (m)", "数值": round(pe2[0], 4)},
            {"项目": "起爆点 Y (m)", "数值": round(pe2[1], 4)},
            {"项目": "起爆点 Z (m)", "数值": round(pe2[2], 4)},
            {"项目": "有效遮蔽时长 (s)", "数值": round(J2, 2)},
        ]
    )
    df_q2.to_excel(TAB_DIR / "问题2_优化结果表.xlsx", index=False)

    df_cmp = pd.DataFrame(
        [
            {
                "问题": "问题1",
                "速度(m/s)": v1,
                "投放时刻(s)": td1,
                "起爆时刻(s)": td1 + tf1,
                "投放点": f"({pd1[0]:.2f},{pd1[1]:.2f},{pd1[2]:.2f})",
                "起爆点": f"({pe1[0]:.2f},{pe1[1]:.2f},{pe1[2]:.2f})",
                "有效遮蔽时长(s)": round(J1, 2),
            },
            {
                "问题": "问题2",
                "速度(m/s)": round(v2, 2),
                "投放时刻(s)": round(td2, 3),
                "起爆时刻(s)": round(td2 + tf2, 3),
                "投放点": f"({pd2[0]:.2f},{pd2[1]:.2f},{pd2[2]:.2f})",
                "起爆点": f"({pe2[0]:.2f},{pe2[1]:.2f},{pe2[2]:.2f})",
                "有效遮蔽时长(s)": round(J2, 2),
            },
        ]
    )
    df_cmp.to_excel(TAB_DIR / "问题1与问题2_结果对比表.xlsx", index=False)

    if len(ts1):
        pd.DataFrame({"时间(s)": ts1, "球心到视线距离(m)": d1, "是否有效遮蔽": m1.astype(int)}).to_excel(
            TAB_DIR / "问题1_遮蔽过程明细表.xlsx", index=False
        )
    if len(ts2):
        pd.DataFrame({"时间(s)": ts2, "球心到视线距离(m)": d2, "是否有效遮蔽": m2.astype(int)}).to_excel(
            TAB_DIR / "问题2_遮蔽过程明细表.xlsx", index=False
        )

    print("图片目录:", list(IMG_DIR.glob("*.png")))
    print("表格目录:", list(TAB_DIR.glob("*.xlsx")))
    print("完成")


if __name__ == "__main__":
    main()
