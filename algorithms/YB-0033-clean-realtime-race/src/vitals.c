/* Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed. | SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE) | Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 */
/* YB-0015 core: summary features of a vital-sign time series (one episode, one channel).
 * out[0] mean, [1] std, [2] RMSSD (successive-difference variability, as in heart-rate variability),
 * [3] max, [4] min, [5] least-squares slope per step, [6] spike fraction (> mean + 2 std).
 * Returns 0 on success, 1 if n < 2. */
#include <math.h>

int series_features(const double *x, int n, double *out) {
    if (n < 2) return 1;
    double s = 0, mx = x[0], mn = x[0];
    for (int i = 0; i < n; i++) { s += x[i]; if (x[i] > mx) mx = x[i]; if (x[i] < mn) mn = x[i]; }
    double mean = s / n, v = 0, d2 = 0, sxy = 0, sxx = 0, tm = (n - 1) / 2.0;
    for (int i = 0; i < n; i++) {
        v += (x[i] - mean) * (x[i] - mean);
        sxy += (i - tm) * (x[i] - mean); sxx += (i - tm) * (i - tm);
        if (i) d2 += (x[i] - x[i - 1]) * (x[i] - x[i - 1]);
    }
    double sd = sqrt(v / n); int sp = 0;
    for (int i = 0; i < n; i++) if (x[i] > mean + 2 * sd) sp++;
    out[0] = mean; out[1] = sd; out[2] = sqrt(d2 / (n - 1)); out[3] = mx; out[4] = mn;
    out[5] = sxx > 0 ? sxy / sxx : 0; out[6] = (double)sp / n;
    return 0;
}
