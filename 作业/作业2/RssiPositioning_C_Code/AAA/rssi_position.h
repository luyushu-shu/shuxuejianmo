#ifndef RSSI_POSITION_H
#define RSSI_POSITION_H

#define MAX_BEACONS 16
#define MAX_WINDOW 8
#define MAX_DIM (2 * MAX_WINDOW)
#define MAX_FRAMES 300
#define PARK_W 120.0
#define PARK_H 80.0
#define P0_RSSI -59.0
#define N_PATH 2.5
#define HUBER_DELTA 2.0
#define LAMBDA_S 0.5
#define LAMBDA_H 0.1
#define WINDOW_SIZE 8
#define MAX_ITER 50
#define V_MIN 0.8
#define V_MAX 2.0
#define DT 1.0

double dist2d(double beacon[2], double pos[2]);
void dist2dgrad(double beacon[2], double pos[2], double grad[2]);
void dist2dhess(double beacon[2], double pos[2], double hess[2][2]);
double rssi2dist(double rssi);
double huber_weight(double residual, double delta);

double objfun2d(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2]);
void gradfun2d(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2], double gf[2]);
void hessfun2d(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2], double hf[2][2]);

void solve_linear(int n, double A[MAX_DIM][MAX_DIM], double B[MAX_DIM], double X[MAX_DIM]);
void matrix_inverse(int n, double a[MAX_DIM][MAX_DIM], double ainv[MAX_DIM][MAX_DIM]);
void solve_linear2(double A[2][2], double B[2], double X[2]);
void matrix_inverse2(double a[2][2], double ainv[2][2]);

void rssi_position_newton_method(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2]);
int rssi_position_newton_method_detailed(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], double pos[2], double *objvalue, double gradient[2], double hessian[2][2]);

void rssi_position_LM_method_detailed(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double weights[MAX_BEACONS], int maxtimes, double pos[2], double Ainv[2][2], double A[2][2], int info[1]);

int GridSearchPosition2D(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double pos[2]);
int TriDistPosition2D(double B1[2], double d1, double B2[2], double d2, double B3[2], double d3, double pos[2]);

void setup_beacons(double beacons[MAX_BEACONS][2], int *nbeacons);
void simudata(double beacons[MAX_BEACONS][2], int *nbeacons, double true_pos[2], double rssi_obs[MAX_BEACONS], double dist_obs[MAX_BEACONS], double sigma_rssi);
double gaussrand(void);

void build_window_weights(int w, int nbeacons, double beacons[MAX_BEACONS][2], double dist_obs[MAX_WINDOW][MAX_BEACONS], double X[MAX_DIM], double weights[MAX_WINDOW][MAX_BEACONS]);
void window_obj_grad_hess(int w, int nbeacons, double beacons[MAX_BEACONS][2], double dist_obs[MAX_WINDOW][MAX_BEACONS], double weights[MAX_WINDOW][MAX_BEACONS], double X[MAX_DIM], double *objvalue, double grad[MAX_DIM], double hess[MAX_DIM][MAX_DIM]);
void window_irwls(int w, int nbeacons, double beacons[MAX_BEACONS][2], double dist_obs[MAX_WINDOW][MAX_BEACONS], double X0[MAX_DIM], double Xout[MAX_DIM], int maxiter, double huber_delta);

int NewtonMethodInitialPositionByObsData(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double pos[2], double *ObjectiveFunctionValue, double Gradient[2], double Hessian[2][2]);
int LMMethodInitialPositionByObsData(int n, double beacons[MAX_BEACONS][2], double dist_obs[MAX_BEACONS], double pos[2], double Ainv[2][2], double A[2][2]);

void simulate_trajectory(int T, double gt[MAX_FRAMES][2], double rssi_series[MAX_FRAMES][MAX_BEACONS], double beacons[MAX_BEACONS][2], int nbeacons, double sigma_rssi);
void evaluate_trajectory(int T, double gt[MAX_FRAMES][2], double est[MAX_FRAMES][2], double *mae, double *rmse);

#endif
