import numpy as np

G = 9.8
V_MISSILE = 300.0
V_SINK = 3.0
R_SMOKE = 10.0
T_SMOKE = 20.0

FAKE = np.array([0.0, 0.0, 0.0])
TRUE_CENTER = np.array([0.0, 200.0, 5.0])
M1 = np.array([20000.0, 0.0, 2000.0])
FY1 = np.array([17800.0, 0.0, 1800.0])


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
    return np.array([
        pd[0] + v[0] * t_fuse,
        pd[1] + v[1] * t_fuse,
        pd[2] - 0.5 * G * t_fuse ** 2,
    ])


def cloud_center(p_det, t_det, t):
    return np.array([p_det[0], p_det[1], p_det[2] - V_SINK * (t - t_det)])


def point_to_segment_dist(p, a, b):
    ab = b - a
    L2 = float(np.dot(ab, ab))
    if L2 < 1e-18:
        return float(np.linalg.norm(p - a))
    s = float(np.clip(np.dot(p - a, ab) / L2, 0.0, 1.0))
    return float(np.linalg.norm(p - (a + s * ab)))


def effective_duration(speed, heading, t_drop, t_fuse, dt=0.01):
    t_det = t_drop + t_fuse
    p_det = det_point(speed, heading, t_drop, t_fuse)
    t_hit = missile_hit_time()
    t0, t1 = t_det, min(t_det + T_SMOKE, t_hit)
    if t1 <= t0 or p_det[2] <= 0:
        return 0.0
    ts = np.arange(t0, t1 + 1e-12, dt)
    total = 0.0
    for t in ts:
        c = cloud_center(p_det, t_det, t)
        if point_to_segment_dist(c, missile_pos(t), TRUE_CENTER) <= R_SMOKE:
            total += dt
    return float(total)


def solve_problem1():
    speed, t_drop, t_fuse = 120.0, 1.5, 3.6
    heading = heading_to_fake()
    duration = effective_duration(speed, heading, t_drop, t_fuse, dt=0.01)
    return {
        "speed": speed,
        "heading": heading,
        "t_drop": t_drop,
        "t_fuse": t_fuse,
        "t_det": t_drop + t_fuse,
        "drop": drop_point(speed, heading, t_drop),
        "det": det_point(speed, heading, t_drop, t_fuse),
        "duration": duration,
    }


def optimize_problem2():
    best = (0.0, None)
    for theta in np.linspace(np.pi - 0.25, np.pi + 0.25, 11):
        for speed in [70, 85, 100, 115, 130, 140]:
            for t_drop in np.linspace(0.3, 10.0, 12):
                for t_fuse in np.linspace(1.0, 7.0, 11):
                    heading = heading_from_angle(theta)
                    if det_point(speed, heading, t_drop, t_fuse)[2] <= 2:
                        continue
                    J = effective_duration(speed, heading, t_drop, t_fuse, dt=0.05)
                    if J > best[0]:
                        best = (J, (theta, speed, t_drop, t_fuse))

    theta0, speed0, t_drop0, t_fuse0 = best[1]
    for theta in np.linspace(theta0 - 0.08, theta0 + 0.08, 9):
        for speed in np.linspace(max(70, speed0 - 12), min(140, speed0 + 12), 7):
            for t_drop in np.linspace(max(0.05, t_drop0 - 1.0), t_drop0 + 1.0, 9):
                for t_fuse in np.linspace(max(0.4, t_fuse0 - 1.0), t_fuse0 + 1.0, 9):
                    heading = heading_from_angle(theta)
                    if det_point(speed, heading, t_drop, t_fuse)[2] <= 2:
                        continue
                    J = effective_duration(speed, heading, t_drop, t_fuse, dt=0.03)
                    if J > best[0]:
                        best = (J, (theta, float(speed), float(t_drop), float(t_fuse)))

    theta, speed, t_drop, t_fuse = best[1]
    heading = heading_from_angle(theta)
    duration = effective_duration(speed, heading, t_drop, t_fuse, dt=0.01)
    return {
        "theta": theta,
        "speed": speed,
        "heading": heading,
        "t_drop": t_drop,
        "t_fuse": t_fuse,
        "t_det": t_drop + t_fuse,
        "drop": drop_point(speed, heading, t_drop),
        "det": det_point(speed, heading, t_drop, t_fuse),
        "duration": duration,
    }


if __name__ == "__main__":
    q1 = solve_problem1()
    print("Problem 1")
    print("drop =", q1["drop"])
    print("det  =", q1["det"])
    print("J1   = {:.2f} s".format(q1["duration"]))

    q2 = optimize_problem2()
    print("Problem 2")
    print("speed = {:.2f} m/s".format(q2["speed"]))
    print("theta = {:.6f} rad".format(q2["theta"]))
    print("drop  =", q2["drop"])
    print("det   =", q2["det"])
    print("J2    = {:.2f} s".format(q2["duration"]))
