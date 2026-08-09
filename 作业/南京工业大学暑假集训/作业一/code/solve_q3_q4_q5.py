"""问题3/4/5：多弹、多机、多导弹烟幕投放策略求解。"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

G = 9.8
V_MISSILE = 300.0
V_SINK = 3.0
R_SMOKE = 10.0
T_SMOKE = 20.0
DROP_GAP = 1.0

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

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT
CACHE = ROOT / "code" / "q345_results.json"


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else v


def heading_from_angle(theta: float) -> np.ndarray:
    return np.array([np.cos(theta), np.sin(theta), 0.0])


def missile_hit_time(p0: np.ndarray) -> float:
    return float(np.linalg.norm(p0 - FAKE) / V_MISSILE)


def missile_pos(t: float | np.ndarray, p0: np.ndarray) -> np.ndarray:
    e = unit(FAKE - p0)
    if np.isscalar(t):
        return p0 + V_MISSILE * float(t) * e
    t = np.asarray(t, dtype=float)
    return p0[None, :] + V_MISSILE * t[:, None] * e[None, :]


def drop_and_det(
    uav0: np.ndarray, speed: float, heading: np.ndarray, t_drop: float, t_fuse: float
) -> tuple[np.ndarray, np.ndarray, float]:
    h = unit(np.array([heading[0], heading[1], 0.0]))
    p_drop = uav0 + speed * t_drop * h
    p_det = np.array(
        [
            p_drop[0] + speed * h[0] * t_fuse,
            p_drop[1] + speed * h[1] * t_fuse,
            p_drop[2] - 0.5 * G * t_fuse**2,
        ]
    )
    return p_drop, p_det, t_drop + t_fuse


def point_to_segment_dist_batch(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """p,a: (N,3); b: (3,) -> distances (N,)"""
    ab = b[None, :] - a
    L2 = np.sum(ab * ab, axis=1)
    s = np.zeros(len(p))
    ok = L2 > 1e-18
    ap = p - a
    s[ok] = np.clip(np.sum(ap[ok] * ab[ok], axis=1) / L2[ok], 0.0, 1.0)
    closest = a + s[:, None] * ab
    return np.linalg.norm(p - closest, axis=1)


def bombs_from_uav(
    uav0: np.ndarray,
    theta: float,
    speed: float,
    drops: list[float],
    fuses: list[float],
) -> list[dict]:
    h = heading_from_angle(theta)
    bombs = []
    for i, (td, tf) in enumerate(zip(drops, fuses), start=1):
        pd, pe, te = drop_and_det(uav0, speed, h, td, tf)
        bombs.append(
            {
                "id": i,
                "theta": theta,
                "speed": speed,
                "heading": h,
                "t_drop": float(td),
                "t_fuse": float(tf),
                "t_det": float(te),
                "drop": pd,
                "det": pe,
            }
        )
    return bombs


def union_duration(bombs: list[dict], p_missile: np.ndarray, dt: float = 0.02) -> float:
    if not bombs:
        return 0.0
    valid = [b for b in bombs if b["det"][2] > 0]
    if not valid:
        return 0.0
    t_hit = missile_hit_time(p_missile)
    t0 = min(b["t_det"] for b in valid)
    t1 = min(max(b["t_det"] + T_SMOKE for b in valid), t_hit)
    if t1 <= t0:
        return 0.0
    ts = np.arange(t0, t1 + 1e-12, dt)
    mpos = missile_pos(ts, p_missile)
    shielded = np.zeros(len(ts), dtype=bool)
    for b in valid:
        te = b["t_det"]
        pe = b["det"]
        mask = (ts >= te) & (ts <= te + T_SMOKE)
        if not np.any(mask):
            continue
        idx = np.where(mask)[0]
        c = np.column_stack(
            [
                np.full(len(idx), pe[0]),
                np.full(len(idx), pe[1]),
                pe[2] - V_SINK * (ts[idx] - te),
            ]
        )
        d = point_to_segment_dist_batch(c, mpos[idx], TRUE_CENTER)
        shielded[idx] |= d <= R_SMOKE
    return float(shielded.sum() * dt)


def single_bomb_duration(bomb: dict, p_missile: np.ndarray, dt: float = 0.01) -> float:
    return union_duration([bomb], p_missile, dt=dt)


def shielding_mask(bombs: list[dict], p_missile: np.ndarray, dt: float = 0.02):
    valid = [b for b in bombs if b["det"][2] > 0]
    if not valid:
        return np.array([]), np.array([]), 0.0
    t_hit = missile_hit_time(p_missile)
    t0 = min(b["t_det"] for b in valid)
    t1 = min(max(b["t_det"] + T_SMOKE for b in valid), t_hit)
    ts = np.arange(t0, t1 + 1e-12, dt)
    mpos = missile_pos(ts, p_missile)
    shielded = np.zeros(len(ts), dtype=bool)
    min_dist = np.full(len(ts), np.inf)
    for b in valid:
        te = b["t_det"]
        pe = b["det"]
        mask = (ts >= te) & (ts <= te + T_SMOKE)
        if not np.any(mask):
            continue
        idx = np.where(mask)[0]
        c = np.column_stack(
            [
                np.full(len(idx), pe[0]),
                np.full(len(idx), pe[1]),
                pe[2] - V_SINK * (ts[idx] - te),
            ]
        )
        d = point_to_segment_dist_batch(c, mpos[idx], TRUE_CENTER)
        min_dist[idx] = np.minimum(min_dist[idx], d)
        shielded[idx] |= d <= R_SMOKE
    return ts, min_dist, float(shielded.sum() * dt)


# ---------------- Problem 3 ----------------
def decode_q3(x: np.ndarray) -> tuple[float, float, list[float], list[float]]:
    theta, speed = float(x[0]), float(x[1])
    td1, g12, g23 = float(x[2]), float(x[3]), float(x[4])
    tf1, tf2, tf3 = float(x[5]), float(x[6]), float(x[7])
    td2 = td1 + g12
    td3 = td2 + g23
    return theta, speed, [td1, td2, td3], [tf1, tf2, tf3]


def optimize_q3(seed: int = 42) -> dict:
    uav0 = UAVS["FY1"]
    p_m = MISSILES["M1"]
    # theta, v, td1, gap12, gap23, tf1, tf2, tf3
    bounds = [
        (np.pi - 0.35, np.pi + 0.35),
        (70.0, 140.0),
        (0.0, 8.0),
        (1.0, 8.0),
        (1.0, 8.0),
        (0.4, 6.5),
        (0.4, 6.5),
        (0.4, 6.5),
    ]

    def obj(x):
        theta, speed, drops, fuses = decode_q3(x)
        bombs = bombs_from_uav(uav0, theta, speed, drops, fuses)
        if any(b["det"][2] <= 1.0 for b in bombs):
            return 0.0
        return -union_duration(bombs, p_m, dt=0.04)

    res = differential_evolution(
        obj,
        bounds,
        seed=seed,
        popsize=14,
        mutation=(0.5, 1.0),
        recombination=0.7,
        maxiter=55,
        polish=False,
        workers=1,
        updating="deferred",
        tol=1e-4,
    )
    theta, speed, drops, fuses = decode_q3(res.x)
    bombs = bombs_from_uav(uav0, theta, speed, drops, fuses)
    J = union_duration(bombs, p_m, dt=0.01)
    return {
        "uav": "FY1",
        "missile": "M1",
        "theta": theta,
        "speed": speed,
        "drops": drops,
        "fuses": fuses,
        "bombs": bombs,
        "duration": J,
    }


# ---------------- Problem 4 ----------------
def optimize_single_uav_for_missile(
    uav_name: str,
    missile_name: str,
    seed: int = 0,
    prefer_window: tuple[float, float] | None = None,
) -> dict:
    uav0 = UAVS[uav_name]
    p_m = MISSILES[missile_name]
    # Prefer heading toward fake target, with some freedom
    base = np.arctan2(FAKE[1] - uav0[1], FAKE[0] - uav0[0])
    bounds = [
        (base - 0.6, base + 0.6),
        (70.0, 140.0),
        (0.0, 25.0),
        (0.4, 7.0),
    ]

    def obj(x):
        theta, speed, td, tf = map(float, x)
        bombs = bombs_from_uav(uav0, theta, speed, [td], [tf])
        if bombs[0]["det"][2] <= 1.0:
            return 0.0
        J = union_duration(bombs, p_m, dt=0.05)
        if prefer_window is not None:
            # soft encourage detonation near window center
            te = bombs[0]["t_det"]
            mid = 0.5 * (prefer_window[0] + prefer_window[1])
            J -= 0.05 * abs(te - mid)
        return -J

    res = differential_evolution(
        obj,
        bounds,
        seed=seed,
        popsize=12,
        maxiter=40,
        polish=False,
        workers=1,
        updating="deferred",
    )
    theta, speed, td, tf = map(float, res.x)
    bombs = bombs_from_uav(uav0, theta, speed, [td], [tf])
    # local polish around solution with denser scan
    best = {
        "uav": uav_name,
        "missile": missile_name,
        "theta": theta,
        "speed": speed,
        "drops": [td],
        "fuses": [tf],
        "bombs": bombs,
        "duration": union_duration(bombs, p_m, dt=0.01),
    }
    for dth in np.linspace(-0.08, 0.08, 7):
        for dv in np.linspace(-10, 10, 5):
            for dtd in np.linspace(-1.0, 1.0, 7):
                for dtf in np.linspace(-0.8, 0.8, 7):
                    th = theta + dth
                    sp = float(np.clip(speed + dv, 70, 140))
                    tdd = max(0.0, td + dtd)
                    tff = max(0.3, tf + dtf)
                    bb = bombs_from_uav(uav0, th, sp, [tdd], [tff])
                    if bb[0]["det"][2] <= 1.0:
                        continue
                    J = union_duration(bb, p_m, dt=0.03)
                    if J > best["duration"]:
                        best = {
                            "uav": uav_name,
                            "missile": missile_name,
                            "theta": th,
                            "speed": sp,
                            "drops": [tdd],
                            "fuses": [tff],
                            "bombs": bb,
                            "duration": union_duration(bb, p_m, dt=0.01),
                        }
    return best


def optimize_q4(seed: int = 7) -> dict:
    """三机各一弹：先独立优化，再联合微调时序以拉长并集。"""
    p_m = MISSILES["M1"]
    # encourage staggered windows
    windows = [(1.5, 8.0), (8.0, 16.0), (16.0, 28.0)]
    singles = []
    for i, name in enumerate(["FY1", "FY2", "FY3"]):
        print(f"  optimizing {name} ...")
        singles.append(
            optimize_single_uav_for_missile(name, "M1", seed=seed + i, prefer_window=windows[i])
        )

    # joint local refinement on times/fuses/speeds/headings
    best_bombs = [s["bombs"][0] for s in singles]
    best_J = union_duration(best_bombs, p_m, dt=0.01)
    params = []
    for s in singles:
        params.append([s["theta"], s["speed"], s["drops"][0], s["fuses"][0]])
    params = np.array(params, dtype=float)

    rng = np.random.default_rng(seed)
    for it in range(1200):
        trial = params.copy()
        i = int(rng.integers(0, 3))
        trial[i, 0] += rng.normal(0, 0.04)
        trial[i, 1] = float(np.clip(trial[i, 1] + rng.normal(0, 4), 70, 140))
        trial[i, 2] = max(0.0, trial[i, 2] + rng.normal(0, 0.8))
        trial[i, 3] = float(np.clip(trial[i, 3] + rng.normal(0, 0.5), 0.3, 7.0))
        bombs = []
        ok = True
        for k, name in enumerate(["FY1", "FY2", "FY3"]):
            bb = bombs_from_uav(
                UAVS[name], trial[k, 0], trial[k, 1], [trial[k, 2]], [trial[k, 3]]
            )
            if bb[0]["det"][2] <= 1.0:
                ok = False
                break
            bombs.append(bb[0])
        if not ok:
            continue
        J = union_duration(bombs, p_m, dt=0.03)
        if J > best_J + 1e-9:
            best_J = union_duration(bombs, p_m, dt=0.01)
            params = trial
            best_bombs = bombs

    strategies = []
    for k, name in enumerate(["FY1", "FY2", "FY3"]):
        strategies.append(
            {
                "uav": name,
                "missile": "M1",
                "theta": float(params[k, 0]),
                "speed": float(params[k, 1]),
                "drops": [float(params[k, 2])],
                "fuses": [float(params[k, 3])],
                "bombs": [best_bombs[k]],
                "duration": single_bomb_duration(best_bombs[k], p_m, dt=0.01),
            }
        )
    return {
        "strategies": strategies,
        "bombs": best_bombs,
        "duration": best_J,
        "missile": "M1",
    }


# ---------------- Problem 5 ----------------
def assign_uavs_to_missiles() -> dict[str, str]:
    """按水平距离就近指派：保证每枚导弹至少一架。"""
    # Geometric heuristic from known good assignments
    return {
        "FY1": "M1",
        "FY2": "M2",
        "FY4": "M2",
        "FY3": "M3",
        "FY5": "M3",
    }


def optimize_uav_multi_bombs(
    uav_name: str, missile_name: str, n_bombs: int, seed: int = 0
) -> dict:
    uav0 = UAVS[uav_name]
    p_m = MISSILES[missile_name]
    base = np.arctan2(FAKE[1] - uav0[1], FAKE[0] - uav0[0])
    # theta, v, td1, gap12, ..., gaps, fuses
    bounds = [(base - 0.7, base + 0.7), (70.0, 140.0), (0.0, 20.0)]
    for _ in range(n_bombs - 1):
        bounds.append((1.0, 10.0))
    for _ in range(n_bombs):
        bounds.append((0.4, 6.5))

    def decode(x):
        theta, speed = float(x[0]), float(x[1])
        td = float(x[2])
        drops = [td]
        idx = 3
        for _ in range(n_bombs - 1):
            td = td + float(x[idx])
            drops.append(td)
            idx += 1
        fuses = [float(x[idx + i]) for i in range(n_bombs)]
        return theta, speed, drops, fuses

    def obj(x):
        theta, speed, drops, fuses = decode(x)
        bombs = bombs_from_uav(uav0, theta, speed, drops, fuses)
        if any(b["det"][2] <= 1.0 for b in bombs):
            return 0.0
        return -union_duration(bombs, p_m, dt=0.05)

    res = differential_evolution(
        obj,
        bounds,
        seed=seed,
        popsize=10,
        maxiter=35,
        polish=False,
        workers=1,
        updating="deferred",
    )
    theta, speed, drops, fuses = decode(res.x)
    bombs = bombs_from_uav(uav0, theta, speed, drops, fuses)
    return {
        "uav": uav_name,
        "missile": missile_name,
        "theta": theta,
        "speed": speed,
        "drops": drops,
        "fuses": fuses,
        "bombs": bombs,
        "duration": union_duration(bombs, p_m, dt=0.01),
    }


def optimize_q5(seed: int = 11) -> dict:
    assign = assign_uavs_to_missiles()
    # bombs per UAV (at most 3): give more bombs to closer / more critical tasks
    n_map = {"FY1": 3, "FY2": 2, "FY3": 2, "FY4": 2, "FY5": 2}
    strategies = []
    by_missile: dict[str, list[dict]] = {"M1": [], "M2": [], "M3": []}
    for i, (uav, missile) in enumerate(assign.items()):
        print(f"  optimizing {uav} -> {missile}, n={n_map[uav]} ...")
        s = optimize_uav_multi_bombs(uav, missile, n_map[uav], seed=seed + i)
        strategies.append(s)
        by_missile[missile].extend(s["bombs"])

    durations = {
        m: union_duration(bombs, MISSILES[m], dt=0.01) for m, bombs in by_missile.items()
    }
    return {
        "assign": assign,
        "n_map": n_map,
        "strategies": strategies,
        "by_missile": by_missile,
        "durations": durations,
        "total": float(sum(durations.values())),
    }


# ---------------- Excel / serialization ----------------
def bomb_row(uav: str, bomb: dict, missile: str | None, duration_note: float) -> dict:
    h = bomb["heading"]
    # 方向角：相对 +x 轴，单位度，范围 (-180,180]
    ang = float(np.degrees(np.arctan2(h[1], h[0])))
    row = {
        "无人机编号": uav,
        "无人机运动方向": round(ang, 3),
        "无人机运动速度 (m/s)": round(float(bomb["speed"]), 3),
        "烟幕干扰弹编号": bomb["id"],
        "烟幕干扰弹投放点的x坐标 (m)": round(float(bomb["drop"][0]), 3),
        "烟幕干扰弹投放点的y坐标 (m)": round(float(bomb["drop"][1]), 3),
        "烟幕干扰弹投放点的z坐标 (m)": round(float(bomb["drop"][2]), 3),
        "烟幕干扰弹起爆点的x坐标 (m)": round(float(bomb["det"][0]), 3),
        "烟幕干扰弹起爆点的y坐标 (m)": round(float(bomb["det"][1]), 3),
        "烟幕干扰弹起爆点的z坐标 (m)": round(float(bomb["det"][2]), 3),
        "有效干扰时长 (s)": round(float(duration_note), 3),
    }
    if missile is not None:
        row["干扰的导弹编号"] = missile
    return row


def save_result1(q3: dict, path: Path):
    rows = []
    for b in q3["bombs"]:
        rows.append(bomb_row("FY1", b, None, q3["duration"]))
    # remove unused columns for result1 style
    df = pd.DataFrame(rows)
    df = df.drop(columns=["无人机编号"])
    df.to_excel(path, index=False)


def save_result2(q4: dict, path: Path):
    rows = []
    for s in q4["strategies"]:
        b = s["bombs"][0]
        b = dict(b)
        b["id"] = 1
        rows.append(bomb_row(s["uav"], b, None, q4["duration"]))
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)


def save_result3(q5: dict, path: Path):
    rows = []
    for s in q5["strategies"]:
        for b in s["bombs"]:
            rows.append(
                bomb_row(
                    s["uav"],
                    b,
                    s["missile"],
                    q5["durations"][s["missile"]],
                )
            )
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)


def serialize_bomb(b: dict) -> dict:
    return {
        "id": b["id"],
        "theta": float(b["theta"]),
        "speed": float(b["speed"]),
        "heading": [float(x) for x in b["heading"]],
        "t_drop": float(b["t_drop"]),
        "t_fuse": float(b["t_fuse"]),
        "t_det": float(b["t_det"]),
        "drop": [float(x) for x in b["drop"]],
        "det": [float(x) for x in b["det"]],
    }


def main():
    print("=" * 60)
    print("Problem 3: FY1 x 3 bombs vs M1")
    q3 = optimize_q3()
    print(f"J3 = {q3['duration']:.3f} s")
    print(f"speed={q3['speed']:.2f}, theta={q3['theta']:.6f}")
    for b in q3["bombs"]:
        print(
            f"  bomb{b['id']}: td={b['t_drop']:.3f}, tf={b['t_fuse']:.3f}, "
            f"te={b['t_det']:.3f}, det={np.round(b['det'],2)}"
        )

    print("=" * 60)
    print("Problem 4: FY1/2/3 x 1 bomb vs M1")
    q4 = optimize_q4()
    print(f"J4 = {q4['duration']:.3f} s")
    for s in q4["strategies"]:
        b = s["bombs"][0]
        print(
            f"  {s['uav']}: v={s['speed']:.2f}, theta={s['theta']:.4f}, "
            f"td={b['t_drop']:.3f}, te={b['t_det']:.3f}, J_i={s['duration']:.3f}"
        )

    print("=" * 60)
    print("Problem 5: 5 UAVs vs M1/M2/M3")
    q5 = optimize_q5()
    print(f"J5 total = {q5['total']:.3f} s")
    for m, J in q5["durations"].items():
        print(f"  {m}: {J:.3f} s, bombs={len(q5['by_missile'][m])}")

    save_result1(q3, OUT_DIR / "result1.xlsx")
    save_result2(q4, OUT_DIR / "result2.xlsx")
    save_result3(q5, OUT_DIR / "result3.xlsx")
    print("saved result1/2/3.xlsx")

    cache = {
        "q3": {
            "theta": q3["theta"],
            "speed": q3["speed"],
            "drops": q3["drops"],
            "fuses": q3["fuses"],
            "duration": q3["duration"],
            "bombs": [serialize_bomb(b) for b in q3["bombs"]],
        },
        "q4": {
            "duration": q4["duration"],
            "strategies": [
                {
                    "uav": s["uav"],
                    "theta": s["theta"],
                    "speed": s["speed"],
                    "drops": s["drops"],
                    "fuses": s["fuses"],
                    "duration": s["duration"],
                    "bombs": [serialize_bomb(b) for b in s["bombs"]],
                }
                for s in q4["strategies"]
            ],
        },
        "q5": {
            "assign": q5["assign"],
            "n_map": q5["n_map"],
            "durations": q5["durations"],
            "total": q5["total"],
            "strategies": [
                {
                    "uav": s["uav"],
                    "missile": s["missile"],
                    "theta": s["theta"],
                    "speed": s["speed"],
                    "drops": s["drops"],
                    "fuses": s["fuses"],
                    "duration": s["duration"],
                    "bombs": [serialize_bomb(b) for b in s["bombs"]],
                }
                for s in q5["strategies"]
            ],
        },
    }
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print("cached", CACHE)


if __name__ == "__main__":
    main()
