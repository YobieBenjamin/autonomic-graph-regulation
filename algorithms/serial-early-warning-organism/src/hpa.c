/* Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed. | SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE) | Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 */
/* YB-0017 core: HPA-axis organism (hypothalamus -> pituitary -> adrenal) as a 3-node graph ODE.
 *   fb(C) = 1 / (1 + (C/Ki)^n)                          cortisol negative feedback (edge C -> H, C -> A)
 *   dH/dt = b + k1 * S(t) * fb(C) - w1 * H              CRH, driven by stress input S >= 0
 *   dA/dt = k2 * H * fb(C) - w2 * A                     ACTH
 *   dC/dt = k3 * A - w3 * C                             cortisol (slow: w3 small)
 * p = {b, k1, k2, k3, w1, w2, w3, Ki, n}. One step per input sample, RK4 with `sub` substeps.
 * If burn > 0 the state starts at the S=0 resting point (burn steps from zero). Returns 0 on success. */
#include <math.h>

static void rhs(const double *p, double S, const double *x, double *d) {
    double C = x[2] > 0 ? x[2] : 0, fb = 1.0 / (1.0 + pow(C / p[7], p[8]));
    d[0] = p[0] + p[1] * S * fb - p[4] * x[0];
    d[1] = p[2] * x[0] * fb - p[5] * x[1];
    d[2] = p[3] * x[1] - p[6] * x[2];
}

static void step(const double *p, double S, double *x, int sub) {
    double h = 1.0 / sub, k1[3], k2[3], k3[3], k4[3], t[3];
    for (int s = 0; s < sub; s++) {
        rhs(p, S, x, k1); for (int i = 0; i < 3; i++) t[i] = x[i] + 0.5 * h * k1[i];
        rhs(p, S, t, k2); for (int i = 0; i < 3; i++) t[i] = x[i] + 0.5 * h * k2[i];
        rhs(p, S, t, k3); for (int i = 0; i < 3; i++) t[i] = x[i] + h * k3[i];
        rhs(p, S, t, k4); for (int i = 0; i < 3; i++) x[i] += h / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    }
}

int hpa_simulate(const double *S, int T, const double *p, int sub, int burn, double *H, double *A, double *C) {
    if (T < 1 || sub < 1) return 1;
    double x[3] = {0, 0, 0};
    for (int t = 0; t < burn; t++) step(p, 0.0, x, sub);
    for (int t = 0; t < T; t++) {
        step(p, S[t] > 0 ? S[t] : 0, x, sub);
        H[t] = x[0]; A[t] = x[1]; C[t] = x[2];
    }
    return 0;
}
