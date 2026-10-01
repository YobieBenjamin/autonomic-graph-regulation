/* Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed. | SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE) | Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 */
/* YB-0009 core: physiological coupling graph over sliding windows (network-physiology style).
 * X: T x k multichannel vitals (row-major). For each window of length w (stride s), edge weight between channels
 * i,j = max over lags 0..L of |Pearson corr(x_i(t), x_j(t+lag))| (lag in either direction). Graph -> normalized
 * Laplacian; per window we output: [0] algebraic connectivity lambda_2, [1] spectral entropy of the Laplacian
 * eigenvalues, [2] total coupling (sum of edge weights), [3] largest eigenvalue. Returns number of windows (or -1).
 * The eigensolver is the cyclic Jacobi method reused from YB-0001. */
#include <math.h>
#include <stdlib.h>

static void jacobi(double *M, int n, double *ev) {
    for (int sw = 0; sw < 100; sw++) {
        double off = 0; for (int p = 0; p < n; p++) for (int q = p + 1; q < n; q++) off += M[p*n+q] * M[p*n+q];
        if (off < 1e-24) break;
        for (int p = 0; p < n; p++) for (int q = p + 1; q < n; q++) {
            double apq = M[p*n+q]; if (fabs(apq) < 1e-300) continue;
            double th = (M[q*n+q] - M[p*n+p]) / (2 * apq), t = (th >= 0 ? 1 : -1) / (fabs(th) + sqrt(th * th + 1)), c = 1 / sqrt(t * t + 1), s = t * c;
            for (int k = 0; k < n; k++) { double a = M[k*n+p], b = M[k*n+q]; M[k*n+p] = c*a - s*b; M[k*n+q] = s*a + c*b; }
            for (int k = 0; k < n; k++) { double a = M[p*n+k], b = M[q*n+k]; M[p*n+k] = c*a - s*b; M[q*n+k] = s*a + c*b; }
        }
    }
    for (int i = 0; i < n; i++) ev[i] = M[i*n+i];
}

static double corr(const double *X, int k, int i, int j, int t0, int w, int lag) {
    double sa = 0, sb = 0, saa = 0, sbb = 0, sab = 0; int m = w - lag;
    for (int t = 0; t < m; t++) { double a = X[(t0+t)*k+i], b = X[(t0+t+lag)*k+j]; sa += a; sb += b; saa += a*a; sbb += b*b; sab += a*b; }
    double va = saa - sa*sa/m, vb = sbb - sb*sb/m; if (va <= 1e-15 || vb <= 1e-15) return 0;
    return (sab - sa*sb/m) / sqrt(va * vb);
}

int coupling_windows(const double *X, int T, int k, int w, int s, int L, double *out, int maxw) {
    if (k < 2 || w < L + 3 || T < w) return -1;
    double *W = malloc(k*k*sizeof(double)), *Lp = malloc(k*k*sizeof(double)), *ev = malloc(k*sizeof(double)), *d = malloc(k*sizeof(double));
    int nw = 0;
    for (int t0 = 0; t0 + w <= T && nw < maxw; t0 += s, nw++) {
        double tot = 0;
        for (int i = 0; i < k; i++) { W[i*k+i] = 0; for (int j = i + 1; j < k; j++) {
            double best = 0; for (int lag = 0; lag <= L; lag++) { double a = fabs(corr(X, k, i, j, t0, w, lag)), b = fabs(corr(X, k, j, i, t0, w, lag)); if (a > best) best = a; if (b > best) best = b; }
            W[i*k+j] = W[j*k+i] = best; tot += best; } }
        for (int i = 0; i < k; i++) { d[i] = 0; for (int j = 0; j < k; j++) d[i] += W[i*k+j]; }
        for (int i = 0; i < k; i++) for (int j = 0; j < k; j++)
            Lp[i*k+j] = (i == j ? (d[i] > 0 ? 1.0 : 0.0) : 0.0) - ((d[i] > 0 && d[j] > 0) ? W[i*k+j] / sqrt(d[i]*d[j]) : 0.0);
        jacobi(Lp, k, ev);
        double l2 = 1e9, lmax = 0, sum = 0, H = 0; int zi = 0;
        for (int i = 0; i < k; i++) { if (ev[i] < ev[zi]) zi = i; if (ev[i] > lmax) lmax = ev[i]; sum += ev[i] > 0 ? ev[i] : 0; }
        for (int i = 0; i < k; i++) if (i != zi && ev[i] < l2) l2 = ev[i];
        for (int i = 0; i < k; i++) { double p = ev[i] > 0 && sum > 0 ? ev[i] / sum : 0; if (p > 0) H -= p * log(p); }
        out[nw*4+0] = l2; out[nw*4+1] = H; out[nw*4+2] = tot; out[nw*4+3] = lmax;
    }
    free(W); free(Lp); free(ev); free(d);
    return nw;
}
