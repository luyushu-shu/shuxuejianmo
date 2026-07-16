#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "rssi_position.h"
#include "InitialPosition.h"

double dist2d(double beacon[2], double pos[2])
{
    double dx = pos[0] - beacon[0];
    double dy = pos[1] - beacon[1];
    return sqrt(dx * dx + dy * dy);
}

void dist2dgrad(double beacon[2], double pos[2], double grad[2])
{
    double dx = pos[0] - beacon[0];
    double dy = pos[1] - beacon[1];
    double r = sqrt(dx * dx + dy * dy);
    if (r < 1.0e-8)
    {
        grad[0] = 0.0;
        grad[1] = 0.0;
        return;
    }
    grad[0] = dx / r;
    grad[1] = dy / r;
}

void dist2dhess(double beacon[2], double pos[2], double hess[2][2])
{
    double dx = pos[0] - beacon[0];
    double dy = pos[1] - beacon[1];
    double x2 = dx * dx;
    double y2 = dy * dy;
    double r2 = x2 + y2;
    double r = sqrt(r2);
    double r3 = r * r2;
    if (r < 1.0e-8)
    {
        hess[0][0] = 0.0;
        hess[0][1] = 0.0;
        hess[1][0] = 0.0;
        hess[1][1] = 0.0;
        return;
    }
    hess[0][0] = 1.0 / r - x2 / r3;
    hess[0][1] = -dx * dy / r3;
    hess[1][0] = hess[0][1];
    hess[1][1] = 1.0 / r - y2 / r3;
}

double rssi2dist(double rssi)
{
    return pow(10.0, (P0_RSSI - rssi) / (10.0 * N_PATH));
}

double huber_weight(double residual, double delta)
{
    double a = fabs(residual);
    if (a <= delta)
        return 1.0;
    return delta / a;
}

double objfun2d(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2])
{
    int i;
    double r = 0.0;
    double d, t;
    for (i = 0; i < n; i++)
    {
        d = dist2d(beacons[i], pos);
        t = d - dist_obs[i];
        r += weights[i] * t * t;
    }
    return r;
}

void gradfun2d(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2], double gf[2])
{
    int i, j;
    double d, t, g[2];
    gf[0] = 0.0;
    gf[1] = 0.0;
    for (i = 0; i < n; i++)
    {
        d = dist2d(beacons[i], pos);
        dist2dgrad(beacons[i], pos, g);
        t = d - dist_obs[i];
        for (j = 0; j < 2; j++)
            gf[j] += 2.0 * weights[i] * t * g[j];
    }
}

void hessfun2d(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2], double hf[2][2])
{
    int i, j, k;
    double d, t, g[2], h[2][2];
    for (i = 0; i < 2; i++)
        for (j = 0; j < 2; j++)
            hf[i][j] = 0.0;
    for (k = 0; k < n; k++)
    {
        d = dist2d(beacons[k], pos);
        dist2dgrad(beacons[k], pos, g);
        dist2dhess(beacons[k], pos, h);
        t = d - dist_obs[k];
        for (i = 0; i < 2; i++)
            for (j = 0; j < 2; j++)
                hf[i][j] += weights[k] * (2.0 * g[i] * g[j] + 2.0 * t * h[i][j]);
    }
}

void solve_linear2(double A[2][2], double B[2], double X[2])
{
    double D = A[0][0] * A[1][1] - A[0][1] * A[1][0];
    if (fabs(D) < 1.0e-14)
    {
        X[0] = 0.0;
        X[1] = 0.0;
        return;
    }
    X[0] = (B[0] * A[1][1] - B[1] * A[0][1]) / D;
    X[1] = (A[0][0] * B[1] - A[1][0] * B[0]) / D;
}

void matrix_inverse2(double a[2][2], double ainv[2][2])
{
    double det = a[0][0] * a[1][1] - a[0][1] * a[1][0];
    ainv[0][0] = a[1][1] / det;
    ainv[0][1] = -a[0][1] / det;
    ainv[1][0] = -a[1][0] / det;
    ainv[1][1] = a[0][0] / det;
}

void solve_linear(int n, double A[MAX_DIM][MAX_DIM], double B[MAX_DIM], double X[MAX_DIM])
{
    int i, j, k, p, imax;
    double temp, factor, Am[MAX_DIM][MAX_DIM], Bm[MAX_DIM];
    for (i = 0; i < n; i++)
    {
        Bm[i] = B[i];
        for (j = 0; j < n; j++)
            Am[i][j] = A[i][j];
    }
    for (p = 0; p < n; p++)
    {
        imax = p;
        for (i = p + 1; i < n; i++)
            if (fabs(Am[i][p]) > fabs(Am[imax][p]))
                imax = i;
        if (fabs(Am[imax][p]) < 1.0e-14)
        {
            for (i = 0; i < n; i++)
                X[i] = 0.0;
            return;
        }
        if (imax != p)
        {
            for (j = 0; j < n; j++)
            {
                temp = Am[p][j];
                Am[p][j] = Am[imax][j];
                Am[imax][j] = temp;
            }
            temp = Bm[p];
            Bm[p] = Bm[imax];
            Bm[imax] = temp;
        }
        for (i = p + 1; i < n; i++)
        {
            factor = Am[i][p] / Am[p][p];
            for (j = p; j < n; j++)
                Am[i][j] -= factor * Am[p][j];
            Bm[i] -= factor * Bm[p];
        }
    }
    for (i = n - 1; i >= 0; i--)
    {
        X[i] = Bm[i];
        for (j = i + 1; j < n; j++)
            X[i] -= Am[i][j] * X[j];
        X[i] /= Am[i][i];
    }
}

void matrix_inverse(int n, double a[MAX_DIM][MAX_DIM], double ainv[MAX_DIM][MAX_DIM])
{
    int i, j, k;
    double aug[MAX_DIM][2 * MAX_DIM];
    double factor;
    for (i = 0; i < n; i++)
    {
        for (j = 0; j < n; j++)
        {
            aug[i][j] = a[i][j];
            aug[i][n + j] = (i == j) ? 1.0 : 0.0;
        }
    }
    for (k = 0; k < n; k++)
    {
        if (fabs(aug[k][k]) < 1.0e-14)
            return;
        for (j = 0; j < 2 * n; j++)
            aug[k][j] /= aug[k][k];
        for (i = 0; i < n; i++)
        {
            if (i == k)
                continue;
            factor = aug[i][k];
            for (j = 0; j < 2 * n; j++)
                aug[i][j] -= factor * aug[k][j];
        }
    }
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            ainv[i][j] = aug[i][n + j];
}

void rssi_position_newton_method(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2])
{
    int j, k;
    double gradient[2], hessian[2][2], dx[2];
    for (k = 0; k < MAX_ITER; k++)
    {
        gradfun2d(n, beacons, dist_obs, weights, pos, gradient);
        hessfun2d(n, beacons, dist_obs, weights, pos, hessian);
        solve_linear2(hessian, gradient, dx);
        pos[0] -= dx[0];
        pos[1] -= dx[1];
        if (sqrt(dx[0] * dx[0] + dx[1] * dx[1]) / (sqrt(pos[0] * pos[0] + pos[1] * pos[1]) + 1.0) < 1.0e-5)
            break;
    }
}

int rssi_position_newton_method_detailed(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2], double *objvalue, double gradient[2], double hessian[2][2])
{
    int j, k;
    double dx[2];
    for (k = 0; k < MAX_ITER; k++)
    {
        gradfun2d(n, beacons, dist_obs, weights, pos, gradient);
        hessfun2d(n, beacons, dist_obs, weights, pos, hessian);
        solve_linear2(hessian, gradient, dx);
        pos[0] -= dx[0];
        pos[1] -= dx[1];
        if (sqrt(dx[0] * dx[0] + dx[1] * dx[1]) / (sqrt(pos[0] * pos[0] + pos[1] * pos[1]) + 1.0) < 1.0e-5)
        {
            *objvalue = objfun2d(n, beacons, dist_obs, weights, pos);
            gradfun2d(n, beacons, dist_obs, weights, pos, gradient);
            hessfun2d(n, beacons, dist_obs, weights, pos, hessian);
            return 0;
        }
        if (k > MAX_ITER)
            return 1;
    }
    *objvalue = objfun2d(n, beacons, dist_obs, weights, pos);
    return 0;
}

void rssi_position_LM_method_detailed(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], int maxtimes, double pos[2], double Ainv[2][2], double A[2][2], int info[1])
{
    int i, j, k, j1, j2;
    double d, dr, g[2], dx[2], B[2];
    info[0] = 0;
    for (k = 0; k < maxtimes; k++)
    {
        for (j = 0; j < 2; j++)
        {
            B[j] = 0.0;
            for (i = 0; i < 2; i++)
                A[j][i] = 0.0;
        }
        for (j = 0; j < n; j++)
        {
            d = dist2d(beacons[j], pos);
            dist2dgrad(beacons[j], pos, g);
            dr = dist_obs[j] - d;
            for (j1 = 0; j1 < 2; j1++)
            {
                B[j1] += weights[j] * dr * g[j1];
                for (j2 = 0; j2 < 2; j2++)
                    A[j1][j2] += weights[j] * g[j1] * g[j2];
            }
        }
        solve_linear2(A, B, dx);
        pos[0] += dx[0];
        pos[1] += dx[1];
        if (sqrt(dx[0] * dx[0] + dx[1] * dx[1]) / (sqrt(pos[0] * pos[0] + pos[1] * pos[1]) + 1.0) < 1.0e-5)
        {
            matrix_inverse2(A, Ainv);
            return;
        }
        if (k > maxtimes)
        {
            info[0] = 1;
            return;
        }
    }
}

void build_window_weights(int w, int nbeacons, double beacons[MAX_BEACONS][2], double dist_obs[MAX_WINDOW][MAX_BEACONS], double X[MAX_DIM], double weights[MAX_WINDOW][MAX_BEACONS])
{
    int t, i;
    double pos[2], d, r;
    for (t = 0; t < w; t++)
    {
        pos[0] = X[2 * t];
        pos[1] = X[2 * t + 1];
        for (i = 0; i < nbeacons; i++)
        {
            if (dist_obs[t][i] <= 0.0)
            {
                weights[t][i] = 0.0;
                continue;
            }
            d = dist2d(beacons[i], pos);
            r = d - dist_obs[t][i];
            weights[t][i] = huber_weight(r, HUBER_DELTA);
        }
    }
}

void window_obj_grad_hess(int w, int nbeacons, double beacons[MAX_BEACONS][2], double dist_obs[MAX_WINDOW][MAX_BEACONS], double weights[MAX_WINDOW][MAX_BEACONS], double X[MAX_DIM], double *objvalue, double grad[MAX_DIM], double hess[MAX_DIM][MAX_DIM])
{
    int t, i, j, p, q, idx;
    double pos[2], d, r, g[2], h[2][2], dx, dy, ds, th0, th1, dth;
    for (p = 0; p < 2 * w; p++)
    {
        grad[p] = 0.0;
        for (q = 0; q < 2 * w; q++)
            hess[p][q] = 0.0;
    }
    *objvalue = 0.0;
    for (t = 0; t < w; t++)
    {
        pos[0] = X[2 * t];
        pos[1] = X[2 * t + 1];
        for (i = 0; i < nbeacons; i++)
        {
            if (dist_obs[t][i] <= 0.0)
                continue;
            d = dist2d(beacons[i], pos);
            r = d - dist_obs[t][i];
            *objvalue += weights[t][i] * r * r;
            dist2dgrad(beacons[i], pos, g);
            dist2dhess(beacons[i], pos, h);
            for (p = 0; p < 2; p++)
            {
                grad[2 * t + p] += 2.0 * weights[t][i] * r * g[p];
                for (q = 0; q < 2; q++)
                    hess[2 * t + p][2 * t + q] += weights[t][i] * (2.0 * g[p] * g[q] + 2.0 * r * h[p][q]);
            }
        }
    }
    for (t = 1; t < w; t++)
    {
        dx = X[2 * t] - X[2 * t - 2];
        dy = X[2 * t + 1] - X[2 * t - 1];
        *objvalue += LAMBDA_S * (dx * dx + dy * dy);
        for (p = 0; p < 2; p++)
        {
            idx = 2 * t + p;
            grad[idx] += 2.0 * LAMBDA_S * (X[idx] - X[idx - 2]);
            grad[idx - 2] -= 2.0 * LAMBDA_S * (X[idx] - X[idx - 2]);
            hess[idx][idx] += 2.0 * LAMBDA_S;
            hess[idx - 2][idx - 2] += 2.0 * LAMBDA_S;
            hess[idx][idx - 2] -= 2.0 * LAMBDA_S;
            hess[idx - 2][idx] -= 2.0 * LAMBDA_S;
        }
    }
    for (t = 2; t < w; t++)
    {
        th0 = atan2(X[2 * t - 1] - X[2 * t - 3], X[2 * t - 2] - X[2 * t - 4]);
        th1 = atan2(X[2 * t + 1] - X[2 * t - 1], X[2 * t] - X[2 * t - 2]);
        dth = th1 - th0;
        if (dth > 3.141592653589793)
            dth -= 6.283185307179586;
        if (dth < -3.141592653589793)
            dth += 6.283185307179586;
        *objvalue += LAMBDA_H * dth * dth;
    }
}

void window_irwls(int w, int nbeacons, double beacons[MAX_BEACONS][2], double dist_obs[MAX_WINDOW][MAX_BEACONS], double X0[MAX_DIM], double Xout[MAX_DIM], int maxiter, double huber_delta)
{
    int k, p, q, t;
    double X[MAX_DIM], grad[MAX_DIM], hess[MAX_DIM][MAX_DIM], dx[MAX_DIM];
    double weights[MAX_WINDOW][MAX_BEACONS], objvalue;
    for (p = 0; p < 2 * w; p++)
        X[p] = X0[p];
    for (k = 0; k < maxiter; k++)
    {
        build_window_weights(w, nbeacons, beacons, dist_obs, X, weights);
        window_obj_grad_hess(w, nbeacons, beacons, dist_obs, weights, X, &objvalue, grad, hess);
        solve_linear(2 * w, hess, grad, dx);
        for (p = 0; p < 2 * w; p++)
            X[p] -= dx[p];
        for (t = 0; t < w; t++)
        {
            if (X[2 * t] < 0.0)
                X[2 * t] = 0.0;
            if (X[2 * t] > PARK_W)
                X[2 * t] = PARK_W;
            if (X[2 * t + 1] < 0.0)
                X[2 * t + 1] = 0.0;
            if (X[2 * t + 1] > PARK_H)
                X[2 * t + 1] = PARK_H;
        }
        if (sqrt(dx[0] * dx[0] + dx[1] * dx[1]) / (sqrt(X[0] * X[0] + X[1] * X[1]) + 1.0) < 1.0e-5)
            break;
    }
    for (p = 0; p < 2 * w; p++)
        Xout[p] = X[p];
}

int NewtonMethodInitialPositionByObsData(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double pos[2], double *ObjectiveFunctionValue, double Gradient[2], double Hessian[2][2])
{
    int i;
    double weights[MAX_BEACONS];
    TriDistPosition2D(beacons[0], dist_obs[0], beacons[1], dist_obs[1], beacons[2], dist_obs[2], pos);
    for (i = 0; i < n; i++)
        weights[i] = 1.0;
    printf("Newton result:\n");
    rssi_position_newton_method_detailed(n, beacons, dist_obs, weights, pos, ObjectiveFunctionValue, Gradient, Hessian);
    printf("pos = %12.6f %12.6f\n", pos[0], pos[1]);
    printf("objective = %12.6f\n", *ObjectiveFunctionValue);
    printf("grad = %12.6e %12.6e\n", Gradient[0], Gradient[1]);
    printf("hess = %12.6f %12.6f\n", Hessian[0][0], Hessian[0][1]);
    printf("hess = %12.6f %12.6f\n", Hessian[1][0], Hessian[1][1]);
    return 0;
}

int LMMethodInitialPositionByObsData(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double pos[2], double Ainv[2][2], double A[2][2])
{
    int i, info[1];
    double weights[MAX_BEACONS];
    TriDistPosition2D(beacons[0], dist_obs[0], beacons[1], dist_obs[1], beacons[2], dist_obs[2], pos);
    for (i = 0; i < n; i++)
        weights[i] = 1.0;
    rssi_position_LM_method_detailed(n, beacons, dist_obs, weights, MAX_ITER, pos, Ainv, A, info);
    printf("LM result:\n");
    printf("pos = %12.6f %12.6f\n", pos[0], pos[1]);
    printf("A = %12.6f %12.6f\n", A[0][0], A[0][1]);
    printf("A = %12.6f %12.6f\n", A[1][0], A[1][1]);
    printf("Ainv = %12.6f %12.6f\n", Ainv[0][0], Ainv[0][1]);
    printf("Ainv = %12.6f %12.6f\n", Ainv[1][0], Ainv[1][1]);
    return info[0];
}

void evaluate_trajectory(int T, double gt[MAX_FRAMES][2], double est[MAX_FRAMES][2], double *mae, double *rmse)
{
    int t;
    double err, sum = 0.0, sum2 = 0.0;
    for (t = 0; t < T; t++)
    {
        err = sqrt((gt[t][0] - est[t][0]) * (gt[t][0] - est[t][0]) + (gt[t][1] - est[t][1]) * (gt[t][1] - est[t][1]));
        sum += err;
        sum2 += err * err;
    }
    *mae = sum / T;
    *rmse = sqrt(sum2 / T);
}
