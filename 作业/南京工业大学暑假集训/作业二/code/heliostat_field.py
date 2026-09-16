# -*- coding: utf-8 -*-
"""2023 CUMCM A: heliostat field optical/thermal model (vectorized)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

PHI = np.radians(39.4)  # latitude
ALT_KM = 3.0  # altitude / km
G0 = 1.366  # kW/m^2
ETA_REF = 0.92
SUN_HALF_ANGLE = 4.65e-3  # rad
TOWER_H = 80.0
RECV_H = 8.0
RECV_R = 3.5
FIELD_R = 350.0
CLEAR_R = 100.0
MONTHS = list(range(1, 13))
HOURS = [(9, 0), (10, 30), (12, 0), (13, 30), (15, 0)]


def day_from_equinox(month: int, day: int = 21) -> int:
    """Days from spring equinox (Mar 21), in [0, 364]."""
    # approximate day-of-year then offset
    mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    doy = sum(mdays[:month]) + day
    d = doy - (31 + 28 + 21)  # Mar 21
    return d % 365


def sun_position(month: int, hour: float) -> Tuple[float, float, float]:
    """Return (alpha, gamma, dni). gamma from north, clockwise; alpha altitude."""
    D = day_from_equinox(month)
    delta = math.asin(math.sin(2 * math.pi * D / 365) * math.sin(math.radians(23.45)))
    omega = math.pi / 12 * (hour - 12)
    sin_a = math.cos(delta) * math.cos(PHI) * math.cos(omega) + math.sin(delta) * math.sin(PHI)
    sin_a = float(np.clip(sin_a, -1, 1))
    alpha = math.asin(sin_a)
    # azimuth: from north, clockwise; sign by omega
    cos_g = (math.sin(delta) - math.sin(alpha) * math.sin(PHI)) / (
        math.cos(alpha) * math.cos(PHI) + 1e-15
    )
    cos_g = float(np.clip(cos_g, -1, 1))
    gamma = math.acos(cos_g)
    if omega > 0:
        gamma = 2 * math.pi - gamma
    # DNI (problem appendix), H in km
    a = 0.4237 - 0.00821 * (6 - ALT_KM) ** 2
    b = 0.5055 + 0.00595 * (6.5 - ALT_KM) ** 2
    c = 0.2711 + 0.01858 * (2.5 - ALT_KM) ** 2
    sa = max(math.sin(alpha), 1e-6)
    dni = G0 * (a + b * math.exp(-c / sa)) if alpha > 0 else 0.0
    return alpha, gamma, dni


def incident_unit(alpha: float, gamma: float) -> np.ndarray:
    """Unit vector from mirror toward the sun (incoming reverse)."""
    # problem coord: +x east, +y north, +z up
    # sun direction (from ground to sun):
    sx = math.cos(alpha) * math.sin(gamma)
    sy = math.cos(alpha) * math.cos(gamma)
    sz = math.sin(alpha)
    return np.array([sx, sy, sz], dtype=float)


@dataclass
class FieldConfig:
    xy: np.ndarray  # (N,2)
    w: np.ndarray  # width
    h: np.ndarray  # height of mirror
    z: np.ndarray  # install height of center
    tower_xy: np.ndarray  # (2,)


def load_attachment(path: str) -> np.ndarray:
    df = pd.read_excel(path)
    cols = list(df.columns)
    return df[[cols[0], cols[1]]].to_numpy(dtype=float)


def atmosphere_eta(dist: np.ndarray) -> np.ndarray:
    return 0.99321 - 0.0001176 * dist + 1.97e-8 * dist**2


def cosine_and_normals(
    xy: np.ndarray,
    z: np.ndarray,
    tower_xy: np.ndarray,
    s_hat: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return eta_cos, distance to receiver center, unit reflection vectors."""
    recv = np.array([tower_xy[0], tower_xy[1], TOWER_H], dtype=float)
    centers = np.column_stack([xy[:, 0], xy[:, 1], z])
    r_vec = recv - centers
    dist = np.linalg.norm(r_vec, axis=1)
    r_hat = r_vec / dist[:, None]
    # incident from sun: unit vector pointing to sun is s_hat
    # reflection law: n = normalize(s_hat + r_hat)
    n = s_hat + r_hat
    n = n / (np.linalg.norm(n, axis=1)[:, None] + 1e-15)
    eta_cos = np.clip(np.sum(n * s_hat, axis=1), 0.0, 1.0)
    return eta_cos, dist, r_hat


def truncation_eta(
    dist: np.ndarray,
    r_hat: np.ndarray,
    w: np.ndarray,
    h: np.ndarray,
) -> np.ndarray:
    """Approximate intercept efficiency via sun-shape + mirror size spot vs receiver."""
    diag = 0.5 * np.sqrt(w**2 + h**2)
    mu = np.clip(np.abs(r_hat[:, 2]), 0.2, 1.0)
    spot_r = dist * SUN_HALF_ANGLE + 0.12 * diag / mu
    # cylindrical receiver equivalent aperture radius
    recv_eff_r = 0.55 * math.sqrt((2 * RECV_R) * RECV_H)
    sigma = spot_r / 1.2
    eta = 1.0 - np.exp(-((recv_eff_r / (sigma + 1e-9)) ** 2))
    eta *= 0.96 + 0.04 * np.exp(-dist / 450.0)
    return np.clip(eta, 0.45, 0.99)


def shading_eta(
    xy: np.ndarray,
    w: np.ndarray,
    h: np.ndarray,
    z: np.ndarray,
    tower_xy: np.ndarray,
    s_hat: np.ndarray,
    detailed: bool = True,
) -> np.ndarray:
    """Fast approximate shading/blocking efficiency."""
    N = len(xy)
    eta = np.ones(N)
    if N == 0:
        return eta
    alpha_approx = math.asin(float(np.clip(s_hat[2], -1, 1)))
    if alpha_approx <= 0.05:
        return eta * 0.85
    shadow_len = (TOWER_H + RECV_H / 2) / math.tan(alpha_approx)
    sun_g = s_hat[:2]
    sun_g = sun_g / (np.linalg.norm(sun_g) + 1e-15)
    rel = xy - tower_xy
    proj = rel @ (-sun_g)
    perp = np.abs(rel[:, 0] * (-sun_g[1]) - rel[:, 1] * (-sun_g[0]))
    in_tower = (proj > 0) & (proj < shadow_len) & (perp < RECV_R + 0.5 * w)
    eta[in_tower] *= 0.55

    # packing density proxy (vectorized)
    dens = float(np.mean(w) ** 2 / max((np.mean(w) + 5.0) ** 2, 1e-9))
    eta *= max(0.88, 1.0 - 0.08 * dens)
    if not detailed or N > 4500:
        return eta

    # subsample neighbor check on every 3rd mirror, interpolate-ish
    cell = float(np.median(w) + 5.0)
    buckets: Dict[Tuple[int, int], List[int]] = {}
    for i, (x, y) in enumerate(xy):
        key = (int(math.floor(x / cell)), int(math.floor(y / cell)))
        buckets.setdefault(key, []).append(i)

    step = 2 if N > 1200 else 1
    for i in range(0, N, step):
        key = (int(math.floor(xy[i, 0] / cell)), int(math.floor(xy[i, 1] / cell)))
        cand = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                cand.extend(buckets.get((key[0] + dx, key[1] + dy), []))
        loss = 0.0
        for j in cand:
            if j == i:
                continue
            dxy = xy[j] - xy[i]
            along = dxy @ sun_g
            if along <= 0.2 or along > (w[i] + w[j] + 12):
                continue
            cross = abs(dxy[0] * sun_g[1] - dxy[1] * sun_g[0])
            if cross > 0.55 * (w[i] + w[j]):
                continue
            overlap = max(0.0, 1.0 - cross / (0.5 * (w[i] + w[j]) + 1e-9))
            loss = max(loss, 0.18 * overlap)
        eta[i] *= max(0.6, 1.0 - loss)
        if step > 1 and i + 1 < N:
            eta[i + 1] *= max(0.6, 1.0 - 0.85 * loss)
    return eta


def evaluate_instant(
    cfg: FieldConfig,
    alpha: float,
    gamma: float,
    dni: float,
    detailed_shade: bool = True,
) -> Dict[str, float]:
    n = len(cfg.xy)
    if alpha <= 0 or dni <= 0:
        z = np.zeros(n)
        return dict(eta=0, cos=0, sb=0, trunc=0, at=0, power=0, eta_i=z)
    s_hat = incident_unit(alpha, gamma)
    eta_cos, dist, r_hat = cosine_and_normals(cfg.xy, cfg.z, cfg.tower_xy, s_hat)
    eta_at = atmosphere_eta(dist)
    eta_tr = truncation_eta(dist, r_hat, cfg.w, cfg.h)
    eta_sb = shading_eta(cfg.xy, cfg.w, cfg.h, cfg.z, cfg.tower_xy, s_hat, detailed=detailed_shade)
    eta = eta_sb * eta_cos * eta_at * eta_tr * ETA_REF
    area = cfg.w * cfg.h
    power = float(dni * np.sum(area * eta))  # kW
    return dict(
        eta=float(np.mean(eta)),
        cos=float(np.mean(eta_cos)),
        sb=float(np.mean(eta_sb)),
        trunc=float(np.mean(eta_tr)),
        at=float(np.mean(eta_at)),
        power=power,
        eta_i=eta,
    )


def evaluate_annual(cfg: FieldConfig, fast: bool = False) -> Dict:
    """If fast=True, sample 4 months × 3 hours for optimization screening."""
    months = [3, 6, 9, 12] if fast else MONTHS
    hours = [(9, 0), (12, 0), (15, 0)] if fast else HOURS
    rows = []
    powers = []
    etas = []
    coss, sbs, trs = [], [], []
    month_acc = {m: {"eta": [], "cos": [], "sb": [], "trunc": [], "p": []} for m in MONTHS}
    for m in months:
        for hh, mm in hours:
            hour = hh + mm / 60
            alpha, gamma, dni = sun_position(m, hour)
            r = evaluate_instant(cfg, alpha, gamma, dni, detailed_shade=not fast)
            etas.append(r["eta"])
            coss.append(r["cos"])
            sbs.append(r["sb"])
            trs.append(r["trunc"])
            powers.append(r["power"])
            if not fast:
                month_acc[m]["eta"].append(r["eta"])
                month_acc[m]["cos"].append(r["cos"])
                month_acc[m]["sb"].append(r["sb"])
                month_acc[m]["trunc"].append(r["trunc"])
                month_acc[m]["p"].append(r["power"])
    area = float(np.sum(cfg.w * cfg.h) + 1e-15)
    p_avg_kw = float(np.mean(powers))
    if not fast:
        for m in MONTHS:
            rows.append(
                dict(
                    month=m,
                    eta=float(np.mean(month_acc[m]["eta"])),
                    cos=float(np.mean(month_acc[m]["cos"])),
                    sb=float(np.mean(month_acc[m]["sb"])),
                    trunc=float(np.mean(month_acc[m]["trunc"])),
                    unit_kw=float(np.mean(month_acc[m]["p"]) / area),
                )
            )
    return dict(
        monthly=rows,
        eta=float(np.mean(etas)),
        cos=float(np.mean(coss)),
        sb=float(np.mean(sbs)),
        trunc=float(np.mean(trs)),
        power_mw=p_avg_kw / 1000.0,
        unit_kw=p_avg_kw / area,
        area=area,
        n=len(cfg.xy),
    )


def concentric_layout(
    tower_xy: np.ndarray,
    w: float,
    r_min: float = CLEAR_R,
    r_max: float = FIELD_R,
    gap: float = 5.0,
) -> np.ndarray:
    """Generate concentric-circle heliostat positions around tower, clipped to field disk."""
    # field center at origin; tower may be offset
    dr = w + gap
    rs = np.arange(r_min + 0.5 * w, r_max - 0.5 * w + 1e-9, dr)
    pts = []
    for r in rs:
        n = max(6, int(math.floor(2 * math.pi * r / dr)))
        for k in range(n):
            th = 2 * math.pi * k / n + (0.0 if int(r / dr) % 2 == 0 else math.pi / n)
            x = tower_xy[0] + r * math.cos(th)
            y = tower_xy[1] + r * math.sin(th)
            if x**2 + y**2 <= FIELD_R**2 - 1e-6:
                # keep clear zone around tower
                if (x - tower_xy[0]) ** 2 + (y - tower_xy[1]) ** 2 >= r_min**2:
                    pts.append([x, y])
    if not pts:
        return np.zeros((0, 2))
    return np.asarray(pts, dtype=float)


def make_uniform_config(
    xy: np.ndarray,
    w: float,
    h: float,
    z: float,
    tower_xy: np.ndarray,
) -> FieldConfig:
    n = len(xy)
    return FieldConfig(
        xy=xy,
        w=np.full(n, w),
        h=np.full(n, h),
        z=np.full(n, z),
        tower_xy=np.asarray(tower_xy, dtype=float),
    )


def make_ring_variable_config(
    tower_xy: np.ndarray,
    ring_params: List[Tuple[float, float, float]],
    gap: float = 5.0,
) -> FieldConfig:
    """ring_params: list of (radius, width(=height), install_z)."""
    pts, ws, hs, zs = [], [], [], []
    for r, wh, z in ring_params:
        if r < CLEAR_R or r > FIELD_R:
            continue
        dr = wh + gap
        n = max(6, int(math.floor(2 * math.pi * r / dr)))
        for k in range(n):
            th = 2 * math.pi * k / n
            x = tower_xy[0] + r * math.cos(th)
            y = tower_xy[1] + r * math.sin(th)
            if x**2 + y**2 <= FIELD_R**2 and (x - tower_xy[0]) ** 2 + (y - tower_xy[1]) ** 2 >= CLEAR_R**2:
                pts.append([x, y])
                ws.append(wh)
                hs.append(wh)
                zs.append(z)
    xy = np.asarray(pts, dtype=float) if pts else np.zeros((0, 2))
    return FieldConfig(
        xy=xy,
        w=np.asarray(ws, dtype=float),
        h=np.asarray(hs, dtype=float),
        z=np.asarray(zs, dtype=float),
        tower_xy=np.asarray(tower_xy, dtype=float),
    )
