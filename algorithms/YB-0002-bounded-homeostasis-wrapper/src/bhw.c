/* Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed. | SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE) | Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 */
/* YB-0002 core: Bounded Homeostatic Wrapper (BHW), streaming.
 * For a stream of feature vectors s_t (T x p, row-major) and a precision matrix P (p x p):
 *   d_t   = sqrt((s_t - mu)^T P (s_t - mu))            score vs current baseline
 *   flag  = d_t > tau
 *   if !flag && !frozen:  mu <- mu + eta (s_t - mu)     gated EWMA (homeostasis)
 *     D = sqrt((mu - mu0)^T P (mu - mu0));  if budget>0 && D > budget: frozen = 1
 * Outputs per step: score, flag, drift D, frozen. mode: 0 static, 1 unbounded, 2 budgeted. */
#include <math.h>
#include <stdlib.h>
#include <string.h>

static double qform(const double *v, const double *P, int p) {
    double s = 0.0;
    for (int i = 0; i < p; i++) {
        double r = 0.0;
        for (int j = 0; j < p; j++) r += P[i*p+j] * v[j];
        s += v[i] * r;
    }
    return sqrt(s > 0 ? s : 0);
}

int bhw_run(const double *S, int T, int p, const double *P, const double *mu0,
            double tau, double eta, double budget, int mode,
            double *score, int *flag, double *drift, int *frozen_out) {
    double *mu = malloc(p * sizeof(double)), *v = malloc(p * sizeof(double));
    if (!mu || !v) { free(mu); free(v); return 1; }
    memcpy(mu, mu0, p * sizeof(double));
    int frozen = 0;
    for (int t = 0; t < T; t++) {
        const double *s = S + (size_t)t * p;
        for (int i = 0; i < p; i++) v[i] = s[i] - mu[i];
        score[t] = qform(v, P, p);
        flag[t] = score[t] > tau;
        if (mode > 0 && !flag[t] && !frozen) {
            for (int i = 0; i < p; i++) mu[i] += eta * v[i];
            for (int i = 0; i < p; i++) v[i] = mu[i] - mu0[i];
            if (mode == 2 && qform(v, P, p) > budget) frozen = 1;
        }
        for (int i = 0; i < p; i++) v[i] = mu[i] - mu0[i];
        drift[t] = qform(v, P, p);
        frozen_out[t] = frozen;
    }
    free(mu); free(v);
    return 0;
}
