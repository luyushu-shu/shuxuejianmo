# -*- coding: utf-8 -*-
"""Solve 2023 CUMCM A problems 1-3, export tables/figures/xlsx."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from heliostat_field import (  # noqa: E402
    CLEAR_R,
    FIELD_R,
    concentric_layout,
    evaluate_annual,
    load_attachment,
    make_ring_variable_config,
    make_uniform_config,
    sun_position,
)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

FIG = ROOT / "figures"
PIC = ROOT / "图片"
TAB = ROOT / "表格"
for d in (FIG, PIC, TAB, ROOT / "data"):
    d.mkdir(exist_ok=True)


def savefig(name: str):
    p1 = FIG / name
    p2 = PIC / name
    plt.tight_layout()
    plt.savefig(p1, dpi=160, bbox_inches="tight")
    plt.savefig(p2, dpi=160, bbox_inches="tight")
    plt.close()
    print("fig:", p1)


def monthly_table(res: dict) -> pd.DataFrame:
    rows = []
    for r in res["monthly"]:
        rows.append(
            {
                "日期": f"{r['month']}月21日",
                "平均光学效率": round(r["eta"], 4),
                "平均余弦效率": round(r["cos"], 4),
                "平均阴影遮挡效率": round(r["sb"], 4),
                "平均截断效率": round(r["trunc"], 4),
                "单位面积镜面平均输出热功率(kW/m2)": round(r["unit_kw"], 4),
            }
        )
    return pd.DataFrame(rows)


def annual_table(res: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "年平均光学效率": round(res["eta"], 4),
                "年平均余弦效率": round(res["cos"], 4),
                "年平均阴影遮挡效率": round(res["sb"], 4),
                "年平均截断效率": round(res["trunc"], 4),
                "年平均输出热功率(MW)": round(res["power_mw"], 4),
                "单位面积镜面年平均输出热功率(kW/m2)": round(res["unit_kw"], 4),
            }
        ]
    )


def plot_sun():
    months = range(1, 13)
    hours = [9, 10.5, 12, 13.5, 15]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for h in hours:
        al, ga = [], []
        for m in months:
            a, g, _ = sun_position(m, h)
            al.append(np.degrees(a))
            ga.append(np.degrees(g))
        axes[0].plot(list(months), al, marker="o", label=f"{h:g}时")
        axes[1].plot(list(months), ga, marker="o", label=f"{h:g}时")
    axes[0].set_xlabel("月份")
    axes[0].set_ylabel("太阳高度角 (°)")
    axes[0].set_title("太阳高度角年变化")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)
    axes[1].set_xlabel("月份")
    axes[1].set_ylabel("太阳方位角 (°)")
    axes[1].set_title("太阳方位角年变化")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    savefig("fig01_sun_angles.png")


def plot_layout(xy, tower, name, title):
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(FIELD_R * np.cos(th), FIELD_R * np.sin(th), "k-", lw=1.2)
    ax.plot(CLEAR_R * np.cos(th) + tower[0], CLEAR_R * np.sin(th) + tower[1], "k--", lw=0.8, alpha=0.6)
    ax.scatter(xy[:, 0], xy[:, 1], s=4, c="#1f77b4", alpha=0.75)
    ax.scatter([tower[0]], [tower[1]], s=80, c="crimson", marker="^", label="吸收塔", zorder=5)
    ax.set_aspect("equal")
    ax.set_xlim(-370, 370)
    ax.set_ylim(-370, 370)
    ax.set_xlabel("x / m（东）")
    ax.set_ylabel("y / m（北）")
    ax.set_title(title)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.25)
    savefig(name)


def plot_monthly(res, name, title):
    m = [r["month"] for r in res["monthly"]]
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.plot(m, [r["eta"] for r in res["monthly"]], "o-", label="光学效率")
    ax.plot(m, [r["cos"] for r in res["monthly"]], "s-", label="余弦效率")
    ax.plot(m, [r["sb"] for r in res["monthly"]], "^-", label="阴影遮挡效率")
    ax.plot(m, [r["trunc"] for r in res["monthly"]], "d-", label="截断效率")
    ax.set_xlabel("月份")
    ax.set_ylabel("效率")
    ax.set_ylim(0.4, 1.05)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    savefig(name)


def plot_eta_map(cfg, name, title):
    # use spring equinox noon as representative optical efficiency map
    from heliostat_field import evaluate_instant

    a, g, dni = sun_position(3, 12)
    r = evaluate_instant(cfg, a, g, dni)
    eta = r["eta_i"]
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    sc = ax.scatter(cfg.xy[:, 0], cfg.xy[:, 1], c=eta, s=8, cmap="viridis")
    ax.scatter([cfg.tower_xy[0]], [cfg.tower_xy[1]], c="r", s=70, marker="^")
    th = np.linspace(0, 2 * np.pi, 300)
    ax.plot(FIELD_R * np.cos(th), FIELD_R * np.sin(th), "k-", lw=1)
    plt.colorbar(sc, ax=ax, label="光学效率")
    ax.set_aspect("equal")
    ax.set_title(title)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    savefig(name)


def solve_q1():
    print("=== Q1 ===")
    xy = load_attachment(str(ROOT / "data" / "attachment.xlsx"))
    cfg = make_uniform_config(xy, 6.0, 6.0, 4.0, np.array([0.0, 0.0]))
    res = evaluate_annual(cfg)
    print(annual_table(res))
    monthly_table(res).to_excel(TAB / "表1_问题1月平均.xlsx", index=False)
    annual_table(res).to_excel(TAB / "表2_问题1年平均.xlsx", index=False)
    plot_layout(xy, cfg.tower_xy, "fig02_q1_layout.png", "问题一：定日镜场初始布局（塔在圆心）")
    plot_monthly(res, "fig03_q1_monthly.png", "问题一：各月平均效率")
    plot_eta_map(cfg, "fig04_q1_eta_map.png", "问题一：春分正午光学效率分布")
    # per-mirror annual rough: average of 12 noon snapshots
    from heliostat_field import evaluate_instant

    acc = np.zeros(len(xy))
    for m in range(1, 13):
        a, g, dni = sun_position(m, 12)
        acc += evaluate_instant(cfg, a, g, dni)["eta_i"]
    acc /= 12
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(acc, lw=0.8)
    ax.set_xlabel("定日镜序号（由内层起）")
    ax.set_ylabel("近似年平均光学效率")
    ax.set_title("问题一：各定日镜年平均光学效率")
    ax.grid(True, alpha=0.3)
    savefig("fig05_q1_eta_series.png")
    return cfg, res


def _q2_score(power: float, unit: float) -> float:
    """Prefer feasible (>=60 MW), then maximize unit power."""
    if power >= 60:
        return 1000.0 + unit
    return power + 0.01 * unit  # climb toward rated power first


def search_q2():
    print("=== Q2 search ===")
    best = None
    candidates = []
    for ty in np.linspace(-140, 0, 8):
        for tx in np.linspace(-20, 20, 3):
            for w in [4.0, 5.0, 6.0, 7.0, 8.0]:
                for z in [4.0, 5.0, 6.0]:
                    if z <= w / 2 + 0.05:
                        continue
                    candidates.append((tx, ty, w, z))
    print("candidates", len(candidates))
    results = []
    for i, (tx, ty, w, z) in enumerate(candidates):
        if tx**2 + ty**2 > (FIELD_R - 5) ** 2:
            continue
        tower = np.array([tx, ty])
        xy = concentric_layout(tower, w, r_min=CLEAR_R, r_max=FIELD_R, gap=5.0)
        if len(xy) < 200:
            continue
        cfg = make_uniform_config(xy, w, w, z, tower)
        res = evaluate_annual(cfg, fast=True)
        score = _q2_score(res["power_mw"], res["unit_kw"])
        item = dict(tx=tx, ty=ty, w=w, z=z, n=res["n"], power=res["power_mw"], unit=res["unit_kw"], score=score)
        results.append(item)
        if best is None or item["score"] > best["score"]:
            best = item
            print(f"  best@{i}: n={item['n']} P={item['power']:.2f} unit={item['unit']:.4f} w={w} z={z} tower=({tx:.1f},{ty:.1f})")

    # among top power candidates, refine for unit power under power constraint
    results.sort(key=lambda d: d["score"], reverse=True)
    pool = results[:20]
    best_full = None
    for item in pool:
        for dtx in (-10, 0, 10):
            for dty in (-15, 0, 15):
                for dw in (-0.5, 0, 0.5, 1.0):
                    tx, ty = item["tx"] + dtx, item["ty"] + dty
                    w = float(np.clip(item["w"] + dw, 2.0, 8.0))
                    z = float(np.clip(max(item["z"], w / 2 + 0.3), 2.0, 6.0))
                    if tx**2 + ty**2 > (FIELD_R - 5) ** 2:
                        continue
                    tower = np.array([tx, ty])
                    for gap in [5.0, 5.5]:
                        xy = concentric_layout(tower, w, gap=gap)
                        if len(xy) < 200:
                            continue
                        res = evaluate_annual(make_uniform_config(xy, w, w, z, tower), fast=True)
                        score = _q2_score(res["power_mw"], res["unit_kw"])
                        cand = dict(tx=tx, ty=ty, w=w, z=z, gap=gap, n=res["n"], power=res["power_mw"], unit=res["unit_kw"], score=score)
                        if best_full is None or cand["score"] > best_full["score"]:
                            best_full = cand
    print("  refine-fast", best_full)
    # full evaluation around best_full
    seeds = [best_full, best]
    best = None
    for seed in seeds:
        if seed is None:
            continue
        for w in np.linspace(max(3.0, seed["w"] - 1), min(8.0, seed["w"] + 1), 5):
            for ty in np.linspace(seed["ty"] - 20, seed["ty"] + 20, 5):
                tx = seed["tx"]
                z = float(np.clip(max(seed.get("z", 4), w / 2 + 0.3), 2.0, 6.0))
                if tx**2 + ty**2 > (FIELD_R - 5) ** 2:
                    continue
                tower = np.array([tx, ty])
                xy = concentric_layout(tower, w, gap=5.0)
                cfg = make_uniform_config(xy, w, w, z, tower)
                res = evaluate_annual(cfg, fast=False)
                score = _q2_score(res["power_mw"], res["unit_kw"])
                cand = dict(tx=tx, ty=ty, w=float(w), z=z, gap=5.0, n=res["n"], power=res["power_mw"], unit=res["unit_kw"], score=score)
                if best is None or cand["score"] > best["score"]:
                    best = cand
                    print(f"  full: n={cand['n']} P={cand['power']:.2f} unit={cand['unit']:.4f} w={cand['w']:.2f}")

    # last resort: maximize area with w=8
    if best is None or best["power"] < 60:
        for ty in np.linspace(-80, 40, 7):
            for w in [7.0, 7.5, 8.0]:
                z = min(6.0, w / 2 + 0.5)
                tower = np.array([0.0, ty])
                if tower[0] ** 2 + tower[1] ** 2 > (FIELD_R - 5) ** 2:
                    continue
                xy = concentric_layout(tower, w, gap=5.0)
                cfg = make_uniform_config(xy, w, w, z, tower)
                res = evaluate_annual(cfg, fast=False)
                score = _q2_score(res["power_mw"], res["unit_kw"])
                cand = dict(tx=0.0, ty=float(ty), w=float(w), z=float(z), gap=5.0, n=res["n"], power=res["power_mw"], unit=res["unit_kw"], score=score)
                if best is None or cand["score"] > best["score"]:
                    best = cand
                    print(f"  rescue: n={cand['n']} P={cand['power']:.2f} unit={cand['unit']:.4f}")

    print("Q2 best", best)
    tower = np.array([best["tx"], best["ty"]])
    xy = concentric_layout(tower, best["w"], gap=best.get("gap", 5.0))
    cfg = make_uniform_config(xy, best["w"], best["w"], best["z"], tower)
    res = evaluate_annual(cfg, fast=False)
    return cfg, res, best, results


def solve_q2():
    cfg, res, best, hist = search_q2()
    monthly_table(res).to_excel(TAB / "表1_问题2月平均.xlsx", index=False)
    annual_table(res).to_excel(TAB / "表2_问题2年平均.xlsx", index=False)
    pd.DataFrame(
        [
            {
                "吸收塔x坐标(m)": round(best["tx"], 3),
                "吸收塔y坐标(m)": round(best["ty"], 3),
                "定日镜尺寸(m)": round(best["w"], 3),
                "安装高度(m)": round(best["z"], 3),
                "定日镜数目": int(res["n"]),
                "定日镜总面积(m2)": round(res["area"], 2),
            }
        ]
    ).to_excel(TAB / "表3_问题2设计参数.xlsx", index=False)

    # result2.xlsx
    df_pos = pd.DataFrame(
        {
            "吸收塔x坐标 (m)": [cfg.tower_xy[0]] + [np.nan] * (len(cfg.xy) - 1),
            "吸收塔y坐标 (m)": [cfg.tower_xy[1]] + [np.nan] * (len(cfg.xy) - 1),
            "定日镜尺寸 (m)": [cfg.w[0]] + [np.nan] * (len(cfg.xy) - 1) if False else cfg.w,
        }
    )
    out = pd.DataFrame(
        {
            "吸收塔x坐标 (m)": [float(cfg.tower_xy[0])] + [None] * (len(cfg.xy) - 1),
            "吸收塔y坐标 (m)": [float(cfg.tower_xy[1])] + [None] * (len(cfg.xy) - 1),
            "定日镜尺寸 (m)": [float(cfg.w[0])] + [None] * (len(cfg.xy) - 1),
            "定日镜高度 (m)": [float(cfg.h[0])] + [None] * (len(cfg.xy) - 1),
            "安装高度 (m)": [float(cfg.z[0])] + [None] * (len(cfg.xy) - 1),
            "定日镜x坐标 (m)": cfg.xy[:, 0],
            "定日镜y坐标 (m)": cfg.xy[:, 1],
        }
    )
    # simpler standard template
    out2 = pd.DataFrame(
        {
            "x坐标 (m)": cfg.xy[:, 0],
            "y坐标 (m)": cfg.xy[:, 1],
        }
    )
    with pd.ExcelWriter(ROOT / "result2.xlsx", engine="openpyxl") as writer:
        pd.DataFrame(
            {
                "吸收塔x坐标(m)": [cfg.tower_xy[0]],
                "吸收塔y坐标(m)": [cfg.tower_xy[1]],
                "定日镜宽(m)": [cfg.w[0]],
                "定日镜高(m)": [cfg.h[0]],
                "安装高度(m)": [cfg.z[0]],
                "数目": [len(cfg.xy)],
            }
        ).to_excel(writer, sheet_name="参数", index=False)
        out2.to_excel(writer, sheet_name="定日镜位置", index=False)

    plot_layout(cfg.xy, cfg.tower_xy, "fig06_q2_layout.png", "问题二：优化后定日镜场布局")
    plot_monthly(res, "fig07_q2_monthly.png", "问题二：各月平均效率")
    plot_eta_map(cfg, "fig08_q2_eta_map.png", "问题二：春分正午光学效率分布")

    # random feasible comparison
    rng = np.random.default_rng(42)
    units = []
    for _ in range(40):
        tx = float(rng.uniform(-80, 80))
        ty = float(rng.uniform(-200, -20))
        w = float(rng.uniform(3, 6))
        z = float(rng.uniform(max(w / 2 + 0.3, 2.5), 6))
        if tx**2 + ty**2 > (FIELD_R - 5) ** 2:
            continue
        xy = concentric_layout(np.array([tx, ty]), w, gap=5.0)
        if len(xy) < 300:
            continue
        r = evaluate_annual(make_uniform_config(xy, w, w, z, np.array([tx, ty])), fast=True)
        if r["power_mw"] >= 50:
            units.append(r["unit_kw"])
    fig, ax = plt.subplots(figsize=(8, 3.8))
    if units:
        ax.stem(range(len(units)), units, linefmt="C0-", markerfmt="C0o", basefmt=" ")
    ax.axhline(res["unit_kw"], color="r", ls="--", label=f"最优 {res['unit_kw']:.4f}")
    ax.set_xlabel("随机可行解序号")
    ax.set_ylabel("单位面积年平均输出热功率")
    ax.set_title("问题二：随机可行解与最优解比较")
    ax.legend()
    savefig("fig09_q2_random.png")
    return cfg, res, best


def solve_q3(q2_cfg, q2_best):
    print("=== Q3 ===")
    tower = q2_cfg.tower_xy.copy()
    # rings with variable size: inner smaller? actually outer often larger gap; use decreasing size outward for intercept
    best = None
    best_cfg = None
    best_res = None
    for scale in [0.85, 0.9, 0.95, 1.0, 1.05]:
        for z0 in [3.2, 3.8, 4.2, 4.8]:
            rings = []
            r = CLEAR_R + 2.0
            k = 0
            while r < FIELD_R - 2:
                # size grows slightly then shrinks
                wh = float(np.clip(q2_best["w"] * scale * (1.05 - 0.012 * k), 2.0, 8.0))
                z = float(np.clip(max(z0, wh / 2 + 0.25) + 0.03 * k, 2.0, 6.0))
                rings.append((r, wh, z))
                r += wh + 5.0
                k += 1
            cfg = make_ring_variable_config(tower, rings, gap=5.0)
            if len(cfg.xy) < 300:
                continue
            res = evaluate_annual(cfg, fast=True)
            ok = res["power_mw"] >= 58
            score = res["unit_kw"] if ok else res["unit_kw"] - 10 * (60 - res["power_mw"])
            if best is None or score > best:
                best = score
                best_cfg, best_res = cfg, res
                print(f"  Q3-fast: n={res['n']} P={res['power_mw']:.2f} unit={res['unit_kw']:.4f}")

    best_res = evaluate_annual(best_cfg, fast=False)
    # if still < 60, densify
    if best_res["power_mw"] < 60:
        rings = []
        r = CLEAR_R + 1.5
        k = 0
        while r < FIELD_R - 1:
            wh = float(np.clip(q2_best["w"] * 1.1 * (1.02 - 0.008 * k), 2.5, 8.0))
            z = float(np.clip(max(4.0, wh / 2 + 0.3), 2.0, 6.0))
            rings.append((r, wh, z))
            r += wh + 4.8
            k += 1
        best_cfg = make_ring_variable_config(tower, rings, gap=4.8)
        best_res = evaluate_annual(best_cfg, fast=False)

    monthly_table(best_res).to_excel(TAB / "表1_问题3月平均.xlsx", index=False)
    annual_table(best_res).to_excel(TAB / "表2_问题3年平均.xlsx", index=False)
    pd.DataFrame(
        [
            {
                "吸收塔x坐标(m)": round(float(tower[0]), 3),
                "吸收塔y坐标(m)": round(float(tower[1]), 3),
                "定日镜数目": int(best_res["n"]),
                "定日镜总面积(m2)": round(best_res["area"], 2),
                "尺寸范围(m)": f"{best_cfg.w.min():.2f}~{best_cfg.w.max():.2f}",
                "高度范围(m)": f"{best_cfg.z.min():.2f}~{best_cfg.z.max():.2f}",
            }
        ]
    ).to_excel(TAB / "表3_问题3设计参数.xlsx", index=False)

    with pd.ExcelWriter(ROOT / "result3.xlsx", engine="openpyxl") as writer:
        pd.DataFrame(
            {
                "吸收塔x坐标(m)": [tower[0]],
                "吸收塔y坐标(m)": [tower[1]],
                "数目": [len(best_cfg.xy)],
            }
        ).to_excel(writer, sheet_name="参数", index=False)
        pd.DataFrame(
            {
                "x坐标 (m)": best_cfg.xy[:, 0],
                "y坐标 (m)": best_cfg.xy[:, 1],
                "定日镜尺寸 (m)": best_cfg.w,
                "安装高度 (m)": best_cfg.z,
            }
        ).to_excel(writer, sheet_name="定日镜", index=False)

    plot_layout(best_cfg.xy, tower, "fig10_q3_layout.png", "问题三：变尺寸/高度优化布局")
    plot_monthly(best_res, "fig11_q3_monthly.png", "问题三：各月平均效率")
    plot_eta_map(best_cfg, "fig12_q3_eta_map.png", "问题三：春分正午光学效率分布")

    # size vs radius
    rr = np.linalg.norm(best_cfg.xy - tower, axis=1)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.scatter(rr, best_cfg.w, s=8, alpha=0.7)
    ax.set_xlabel("到吸收塔距离 / m")
    ax.set_ylabel("定日镜边长 / m")
    ax.set_title("问题三：定日镜尺寸随径向距离的变化")
    ax.grid(True, alpha=0.3)
    savefig("fig13_q3_size_radius.png")
    return best_cfg, best_res


def compare_bar(r1, r2, r3):
    labels = ["光学效率", "余弦效率", "遮挡效率", "截断效率", "单位功率"]
    v1 = [r1["eta"], r1["cos"], r1["sb"], r1["trunc"], r1["unit_kw"] / max(r1["unit_kw"], 1e-9)]
    # normalize unit to relative for plot; also separate power plot
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    x = np.arange(4)
    w = 0.25
    axes[0].bar(x - w, [r1["eta"], r1["cos"], r1["sb"], r1["trunc"]], w, label="问题一")
    axes[0].bar(x, [r2["eta"], r2["cos"], r2["sb"], r2["trunc"]], w, label="问题二")
    axes[0].bar(x + w, [r3["eta"], r3["cos"], r3["sb"], r3["trunc"]], w, label="问题三")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(["光学", "余弦", "遮挡", "截断"])
    axes[0].set_ylim(0, 1.05)
    axes[0].legend()
    axes[0].set_title("年均效率对比")
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].bar(
        ["问题一", "问题二", "问题三"],
        [r1["unit_kw"], r2["unit_kw"], r3["unit_kw"]],
        color=["#4c72b0", "#55a868", "#c44e52"],
    )
    axes[1].set_ylabel("kW/m²")
    axes[1].set_title("单位镜面面积年平均输出热功率")
    axes[1].grid(True, axis="y", alpha=0.3)
    savefig("fig14_compare.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(
        ["问题一", "问题二", "问题三"],
        [r1["power_mw"], r2["power_mw"], r3["power_mw"]],
        color=["#4c72b0", "#55a868", "#c44e52"],
    )
    ax.axhline(60, color="k", ls="--", label="额定60 MW")
    ax.set_ylabel("MW")
    ax.set_title("年平均输出热功率对比")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    savefig("fig15_power_compare.png")


def main():
    plot_sun()
    cfg1, r1 = solve_q1()
    cfg2, r2, best2 = solve_q2()
    cfg3, r3 = solve_q3(cfg2, best2)
    compare_bar(r1, r2, r3)

    summary = {
        "q1": {k: r1[k] for k in ["eta", "cos", "sb", "trunc", "power_mw", "unit_kw", "n", "area"]},
        "q2": {
            **{k: r2[k] for k in ["eta", "cos", "sb", "trunc", "power_mw", "unit_kw", "n", "area"]},
            "tower": [float(cfg2.tower_xy[0]), float(cfg2.tower_xy[1])],
            "w": float(cfg2.w[0]),
            "z": float(cfg2.z[0]),
        },
        "q3": {
            **{k: r3[k] for k in ["eta", "cos", "sb", "trunc", "power_mw", "unit_kw", "n", "area"]},
            "tower": [float(cfg3.tower_xy[0]), float(cfg3.tower_xy[1])],
            "w_min": float(cfg3.w.min()),
            "w_max": float(cfg3.w.max()),
            "z_min": float(cfg3.z.min()),
            "z_max": float(cfg3.z.max()),
        },
    }
    with open(ROOT / "code" / "results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("=== SUMMARY ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
