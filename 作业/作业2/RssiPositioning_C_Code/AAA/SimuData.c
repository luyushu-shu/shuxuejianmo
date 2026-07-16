#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include "rssi_position.h"

void setup_beacons(double beacons[MAX_BEACONS][2], int *nbeacons)
{
    int i, j, k = 0;
    double xs[4] = {15.0, 45.0, 75.0, 105.0};
    double ys[4] = {10.0, 30.0, 50.0, 70.0};
    for (i = 0; i < 4; i++)
        for (j = 0; j < 4; j++)
        {
            beacons[k][0] = xs[i];
            beacons[k][1] = ys[j];
            k++;
        }
    *nbeacons = 16;
}

void simudata(double beacons[MAX_BEACONS][2], int *nbeacons, double true_pos[2], double rssi_obs[MAX_BEACONS], double dist_obs[MAX_BEACONS], double sigma_rssi)
{
    int i;
    double d, noise;
    setup_beacons(beacons, nbeacons);
    srand((unsigned int)time(NULL));
    for (i = 0; i < *nbeacons; i++)
    {
        d = dist2d(beacons[i], true_pos);
        noise = gaussrand() * sigma_rssi;
        rssi_obs[i] = P0_RSSI - 10.0 * N_PATH * log10(d) + noise;
        dist_obs[i] = rssi2dist(rssi_obs[i]);
    }
}

void simulate_trajectory(int T, double gt[MAX_FRAMES][2], double rssi_series[MAX_FRAMES][MAX_BEACONS], double beacons[MAX_BEACONS][2], int nbeacons, double sigma_rssi)
{
    int t, i;
    double x = 10.0, y = 40.0, vx = 1.2, vy = 0.0, d, noise, th;
    setup_beacons(beacons, &nbeacons);
    srand(20260303u);
    for (t = 0; t < T; t++)
    {
        if (t == 100)
        {
            th = 3.141592653589793 / 2.0;
            vx = 1.0 * cos(th);
            vy = 1.0 * sin(th);
        }
        if (t == 200)
        {
            vx = 1.2;
            vy = 0.0;
        }
        x += vx * DT;
        y += vy * DT;
        if (x < 2.0)
            x = 2.0;
        if (x > 118.0)
            x = 118.0;
        if (y < 2.0)
            y = 2.0;
        if (y > 78.0)
            y = 78.0;
        gt[t][0] = x;
        gt[t][1] = y;
        for (i = 0; i < nbeacons; i++)
        {
            d = dist2d(beacons[i], gt[t]);
            noise = gaussrand() * sigma_rssi;
            if (rand() % 100 < 15)
                noise += 8.0 * gaussrand();
            rssi_series[t][i] = P0_RSSI - 10.0 * N_PATH * log10(d) + noise;
        }
    }
}

double gaussrand(void)
{
    static double U, V;
    static int phase = 0;
    double Z;
    if (phase == 0)
    {
        U = rand() / (RAND_MAX + 1.0);
        V = rand() / (RAND_MAX + 1.0);
        Z = sqrt(-2.0 * log(U)) * sin(6.283185307179586 * V);
    }
    else
    {
        Z = sqrt(-2.0 * log(U)) * cos(6.283185307179586 * V);
    }
    phase = 1 - phase;
    return Z;
}
