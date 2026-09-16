# -*- coding: utf-8 -*-
"""Full-eval only finalize for Q2/Q3 meeting 60 MW."""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from heliostat_field import *  # noqa
from solve_all import (  # noqa
    annual_table,
    compare_bar,
    monthly_table,
    plot_eta_map,
    plot_layout,
    plot_monthly,
    savefig,
    TAB,
)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def main():
    xy1 = load_attachment(str(ROOT / "data" / "attachment.xlsx"))
    cfg1 = make_uniform_config(xy1, 6, 6, 4, np.array([0.0, 0.0]))
    r1 = evaluate_annual(cfg1, fast=False)
    monthly_table(r1).to_excel(TAB / "表1_问题1月平均.xlsx", index=False)
    annual_table(r1).to_excel(TAB / "表2_问题1年平均.xlsx", index=False)

    best2 = None
    # full grid (compact)
    for ty in [-80, -60, -40, -20, 0, 20]:
        for tx in [0.0]:
            for w in [6.5, 7.0, 7.5, 8.0]:
                z = float(min(6.0, max(w / 2 + 0.4, 4.0)))
                tower = np.array([tx, float(ty)])
                if tx * tx + ty * ty > (FIELD_R - 5) ** 2:
                    continue
                xy = concentric_layout(tower, w, gap=5.0)
                cfg = make_uniform_config(xy, w, w, z, tower)
                res = evaluate_annual(cfg, fast=False)
                ok = res["power_mw"] >= 60
                # maximize unit among feasible; else maximize power
                key = (1, res["unit_kw"]) if ok else (0, res["power_mw"])
                print(f"Q2 w={w} ty={ty} n={res['n']} P={res['power_mw']:.2f} u={res['unit_kw']:.4f} ok={ok}")
                if best2 is None or key > best2[0]:
                    best2 = (key, cfg, res, dict(tx=tx, ty=ty, w=w, z=z))

    cfg2, r2, meta2 = best2[1], best2[2], best2[3]
    print("Q2 BEST", meta2, r2["power_mw"], r2["unit_kw"])

    # Q3 around same tower: try to beat q2 unit with P>=60
    tower = cfg2.tower_xy.copy()
    best3 = None
    for scale in [0.95, 1.0, 1.05, 1.1, 1.15]:
        for z0 in [4.0, 4.5, 5.0]:
            rings = []
            r = CLEAR_R + 2
            k = 0
            while r < FIELD_R - 2:
                wh = float(np.clip(meta2["w"] * scale * (1.06 - 0.012 * k), 3.0, 8.0))
                z = float(np.clip(max(z0, wh / 2 + 0.35), 2.0, 6.0))
                rings.append((r, wh, z))
                r += wh + 5.0
                k += 1
            cfg = make_ring_variable_config(tower, rings, gap=5.0)
            if len(cfg.xy) < 1000:
                continue
            res = evaluate_annual(cfg, fast=False)
            ok = res["power_mw"] >= 60
            key = (1, res["unit_kw"]) if ok else (0, res["power_mw"])
            print(f"Q3 scale={scale:.2f} z0={z0} n={res['n']} P={res['power_mw']:.2f} u={res['unit_kw']:.4f}")
            if best3 is None or key > best3[0]:
                best3 = (key, cfg, res)

    cfg3, r3 = best3[1], best3[2]
    print("Q3 BEST", r3["n"], r3["power_mw"], r3["unit_kw"])

    # exports
    monthly_table(r2).to_excel(TAB / "表1_问题2月平均.xlsx", index=False)
    annual_table(r2).to_excel(TAB / "表2_问题2年平均.xlsx", index=False)
    pd.DataFrame([{
        "吸收塔x坐标(m)": round(float(cfg2.tower_xy[0]), 3),
        "吸收塔y坐标(m)": round(float(cfg2.tower_xy[1]), 3),
        "定日镜尺寸(m)": round(float(cfg2.w[0]), 3),
        "安装高度(m)": round(float(cfg2.z[0]), 3),
        "定日镜数目": int(r2["n"]),
        "定日镜总面积(m2)": round(r2["area"], 2),
    }]).to_excel(TAB / "表3_问题2设计参数.xlsx", index=False)
    with pd.ExcelWriter(ROOT / "result2.xlsx", engine="openpyxl") as w:
        pd.DataFrame({
            "吸收塔x坐标(m)": [cfg2.tower_xy[0]],
            "吸收塔y坐标(m)": [cfg2.tower_xy[1]],
            "定日镜宽(m)": [cfg2.w[0]],
            "定日镜高(m)": [cfg2.h[0]],
            "安装高度(m)": [cfg2.z[0]],
            "数目": [len(cfg2.xy)],
        }).to_excel(w, sheet_name="参数", index=False)
        pd.DataFrame({"x坐标 (m)": cfg2.xy[:, 0], "y坐标 (m)": cfg2.xy[:, 1]}).to_excel(
            w, sheet_name="定日镜位置", index=False
        )

    monthly_table(r3).to_excel(TAB / "表1_问题3月平均.xlsx", index=False)
    annual_table(r3).to_excel(TAB / "表2_问题3年平均.xlsx", index=False)
    pd.DataFrame([{
        "吸收塔x坐标(m)": round(float(cfg3.tower_xy[0]), 3),
        "吸收塔y坐标(m)": round(float(cfg3.tower_xy[1]), 3),
        "定日镜数目": int(r3["n"]),
        "定日镜总面积(m2)": round(r3["area"], 2),
        "尺寸范围(m)": f"{cfg3.w.min():.2f}~{cfg3.w.max():.2f}",
        "高度范围(m)": f"{cfg3.z.min():.2f}~{cfg3.z.max():.2f}",
    }]).to_excel(TAB / "表3_问题3设计参数.xlsx", index=False)
    with pd.ExcelWriter(ROOT / "result3.xlsx", engine="openpyxl") as w:
        pd.DataFrame({
            "吸收塔x坐标(m)": [cfg3.tower_xy[0]],
            "吸收塔y坐标(m)": [cfg3.tower_xy[1]],
            "数目": [len(cfg3.xy)],
        }).to_excel(w, sheet_name="参数", index=False)
        pd.DataFrame({
            "x坐标 (m)": cfg3.xy[:, 0],
            "y坐标 (m)": cfg3.xy[:, 1],
            "定日镜尺寸 (m)": cfg3.w,
            "安装高度 (m)": cfg3.z,
        }).to_excel(w, sheet_name="定日镜", index=False)

    plot_layout(cfg2.xy, cfg2.tower_xy, "fig06_q2_layout.png", "问题二：优化后定日镜场布局")
    plot_monthly(r2, "fig07_q2_monthly.png", "问题二：各月平均效率")
    plot_eta_map(cfg2, "fig08_q2_eta_map.png", "问题二：春分正午光学效率分布")
    plot_layout(cfg3.xy, cfg3.tower_xy, "fig10_q3_layout.png", "问题三：变尺寸/高度优化布局")
    plot_monthly(r3, "fig11_q3_monthly.png", "问题三：各月平均效率")
    plot_eta_map(cfg3, "fig12_q3_eta_map.png", "问题三：春分正午光学效率分布")
    rr = np.linalg.norm(cfg3.xy - cfg3.tower_xy, axis=1)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.scatter(rr, cfg3.w, s=8, alpha=0.7)
    ax.set_xlabel("到吸收塔距离 / m")
    ax.set_ylabel("定日镜边长 / m")
    ax.set_title("问题三：定日镜尺寸随径向距离的变化")
    ax.grid(True, alpha=0.3)
    savefig("fig13_q3_size_radius.png")
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
        "monthly_q1": r1["monthly"],
        "monthly_q2": r2["monthly"],
        "monthly_q3": r3["monthly"],
    }
    with open(ROOT / "code" / "results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: summary[k] for k in ["q1", "q2", "q3"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
