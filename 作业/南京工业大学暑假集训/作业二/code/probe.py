import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from heliostat_field import *
import numpy as np

xy = load_attachment(str(Path(__file__).parents[1] / "data" / "attachment.xlsx"))
cfg = make_uniform_config(xy, 6, 6, 4, np.array([0.0, 0.0]))
r = evaluate_annual(cfg, fast=False)
print("q1", r["eta"], r["cos"], r["sb"], r["trunc"], r["power_mw"], r["unit_kw"])
for w, ty in [(6, -40), (7, -40), (8, -20), (8, 0), (7, 20), (8, -60)]:
    tower = np.array([0.0, float(ty)])
    xy2 = concentric_layout(tower, w, gap=5)
    cfg2 = make_uniform_config(xy2, w, w, min(6, w / 2 + 0.5), tower)
    r2 = evaluate_annual(cfg2, fast=True)
    print(
        "w", w, "ty", ty, "n", len(xy2),
        "P", round(r2["power_mw"], 2),
        "u", round(r2["unit_kw"], 4),
        "eta", round(r2["eta"], 3),
        "tr", round(r2["trunc"], 3),
    )
