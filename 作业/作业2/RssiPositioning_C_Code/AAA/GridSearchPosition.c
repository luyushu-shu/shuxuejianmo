#include <stdio.h>
#include <math.h>
#include "InitialPosition.h"

int GridSearchPosition2D(int n, double beacons[16][2], double dist_obs[16], double pos[2])
{
    int i;
    double x, y, best = 1.0e30, val, d, t;
    for (x = 0.0; x <= 120.0; x += 2.0)
    {
        for (y = 0.0; y <= 80.0; y += 2.0)
        {
            val = 0.0;
            for (i = 0; i < n; i++)
            {
                d = sqrt((x - beacons[i][0]) * (x - beacons[i][0]) + (y - beacons[i][1]) * (y - beacons[i][1]));
                t = d - dist_obs[i];
                val += t * t;
            }
            if (val < best)
            {
                best = val;
                pos[0] = x;
                pos[1] = y;
            }
        }
    }
    return 0;
}

int TriDistPosition2D(double B1[2], double d1, double B2[2], double d2, double B3[2], double d3, double pos[2])
{
    double x1 = B1[0], y1 = B1[1];
    double x2 = B2[0], y2 = B2[1];
    double x3 = B3[0], y3 = B3[1];
    double A, B, C, D, E, F, G, H, I;
    double det;
    A = 2.0 * (x2 - x1);
    B = 2.0 * (y2 - y1);
    C = d1 * d1 - d2 * d2 - x1 * x1 + x2 * x2 - y1 * y1 + y2 * y2;
    D = 2.0 * (x3 - x1);
    E = 2.0 * (y3 - y1);
    F = d1 * d1 - d3 * d3 - x1 * x1 + x3 * x3 - y1 * y1 + y3 * y3;
    det = A * E - B * D;
    if (fabs(det) < 1.0e-10)
    {
        pos[0] = 60.0;
        pos[1] = 40.0;
        return -1;
    }
    pos[0] = (C * E - B * F) / det;
    pos[1] = (A * F - C * D) / det;
    return 0;
}
