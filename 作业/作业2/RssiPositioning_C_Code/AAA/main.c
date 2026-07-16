#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "rssi_position.h"
#include "InitialPosition.h"

int main(void)
{
    int nbeacons, t, w, i, j, T = 120;
    double beacons[MAX_BEACONS][2];
    double true_pos[2] = {55.0, 38.0};
    double rssi_obs[MAX_BEACONS], dist_obs[MAX_BEACONS], weights[MAX_BEACONS];
    double pos_newton[2], pos_lm[2], pos_frame[2];
    double fv, gf[2], hf[2][2], A[2][2], Ainv[2][2];
    double gt[MAX_FRAMES][2], rssi_series[MAX_FRAMES][MAX_BEACONS];
    double est_newton[MAX_FRAMES][2], est_window[MAX_FRAMES][2];
    double window_dist[MAX_WINDOW][MAX_BEACONS];
    double X0[MAX_DIM], Xout[MAX_DIM];
    double mae1, rmse1, mae2, rmse2;
    double sigma_rssi = 2.5;

    simudata(beacons, &nbeacons, true_pos, rssi_obs, dist_obs, sigma_rssi);
    for (i = 0; i < nbeacons; i++)
        weights[i] = 1.0;

    NewtonMethodInitialPositionByObsData(nbeacons, beacons, dist_obs, pos_newton, &fv, gf, hf);
    LMMethodInitialPositionByObsData(nbeacons, beacons, dist_obs, pos_lm, Ainv, A);

    simulate_trajectory(T, gt, rssi_series, beacons, nbeacons, sigma_rssi);

    for (t = 0; t < T; t++)
    {
        for (i = 0; i < nbeacons; i++)
            dist_obs[i] = rssi2dist(rssi_series[t][i]);
        TriDistPosition2D(beacons[0], dist_obs[0], beacons[1], dist_obs[1], beacons[2], dist_obs[2], pos_newton);
        rssi_position_newton_method(nbeacons, beacons, dist_obs, weights, pos_newton);
        est_newton[t][0] = pos_newton[0];
        est_newton[t][1] = pos_newton[1];
    }

    w = WINDOW_SIZE;
    for (t = 0; t < T; t++)
    {
        if (t < w - 1)
        {
            for (i = 0; i < nbeacons; i++)
                dist_obs[i] = rssi2dist(rssi_series[t][i]);
            GridSearchPosition2D(nbeacons, beacons, dist_obs, pos_frame);
            est_window[t][0] = pos_frame[0];
            est_window[t][1] = pos_frame[1];
            continue;
        }
        for (i = 0; i < w; i++)
        {
            for (j = 0; j < nbeacons; j++)
                window_dist[i][j] = rssi2dist(rssi_series[t - w + 1 + i][j]);
            GridSearchPosition2D(nbeacons, beacons, window_dist[i], pos_frame);
            X0[2 * i] = pos_frame[0];
            X0[2 * i + 1] = pos_frame[1];
        }
        window_irwls(w, nbeacons, beacons, window_dist, X0, Xout, MAX_ITER, HUBER_DELTA);
        est_window[t][0] = Xout[2 * w - 2];
        est_window[t][1] = Xout[2 * w - 1];
    }

    evaluate_trajectory(T, gt, est_newton, &mae1, &rmse1);
    evaluate_trajectory(T, gt, est_window, &mae2, &rmse2);

    printf("RSSI-Only Newton MAE = %8.4f RMSE = %8.4f\n", mae1, rmse1);
    printf("Proposed Window IRWLS MAE = %8.4f RMSE = %8.4f\n", mae2, rmse2);

    return 0;
}
