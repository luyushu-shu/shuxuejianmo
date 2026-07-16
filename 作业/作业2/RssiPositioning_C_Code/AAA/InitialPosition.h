#ifndef INITIAL_POSITION_H
#define INITIAL_POSITION_H

int GridSearchPosition2D(int n, double beacons[16][2], double dist_obs[16], double pos[2]);
int TriDistPosition2D(double B1[2], double d1, double B2[2], double d2, double B3[2], double d3, double pos[2]);

#endif
