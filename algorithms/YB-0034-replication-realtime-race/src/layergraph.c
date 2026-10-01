/* Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed. | SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE) | Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 */
/* YB-0019 core: layer coupling graph (k nodes, e.g. 24 transformer layers) over sliding windows.
 * Edge weight W_ij = max over lags 0..L of |Pearson corr| (either direction) within the window.
 * Per window out[6]: [0] algebraic connectivity lambda_2 of the normalized Laplacian, [1] spectral entropy,
 * [2] total coupling sum_{i<j} W_ij, [3] largest Laplacian eigenvalue,
 * [4] spectral-bipartition modularity Q = s^T B s / (4m), B = W - d d^T / (2m), s = sign of B's leading eigenvector
 *     (Q = 0 when the leading eigenvalue of B is <= 0: no division improves on the whole graph),
 * [5] number of nodes in the smaller community. Returns number of windows, -1 on bad input. */
#include <math.h>
#include <stdlib.h>
#include <string.h>

static void jacobi(double *M, int n, double *ev) {
    for (int sw = 0; sw < 100; sw++) {
        double off = 0; for (int p = 0; p < n; p++) for (int q = p + 1; q < n; q++) off += M[p*n+q] * M[p*n+q];
        if (off < 1e-24) break;
        for (int p = 0; p < n; p++) for (int q = p + 1; q < n; q++) {
            double apq = M[p*n+q]; if (fabs(apq) < 1e-300) continue;
            double th = (M[q*n+q] - M[p*n+p]) / (2 * apq), t = (th >= 0 ? 1 : -1) / (fabs(th) + sqrt(th*th + 1)), c = 1 / sqrt(t*t + 1), s = t * c;
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

/* modularity of the leading-eigenvector bipartition (power iteration on B + c I, c = max row abs sum) */
static void modularity(const double *W, int k, double *Q, double *small) {
    double *d = calloc(k, sizeof(double)), *B = malloc(k*k*sizeof(double)), *v = malloc(k*sizeof(double)), *u = malloc(k*sizeof(double));
    double m2 = 0; for (int i = 0; i < k; i++) { for (int j = 0; j < k; j++) d[i] += W[i*k+j]; m2 += d[i]; }
    *Q = 0; *small = 0;
    if (m2 > 1e-12) {
        double c = 0;
        for (int i = 0; i < k; i++) { double r = 0; for (int j = 0; j < k; j++) { B[i*k+j] = W[i*k+j] - d[i]*d[j]/m2; r += fabs(B[i*k+j]); } if (r > c) c = r; }
        for (int i = 0; i < k; i++) v[i] = 1.0 + 0.01 * i;
        for (int it = 0; it < 500; it++) {
            double nrm = 0;
            for (int i = 0; i < k; i++) { u[i] = c * v[i]; for (int j = 0; j < k; j++) u[i] += B[i*k+j] * v[j]; nrm += u[i]*u[i]; }
            nrm = sqrt(nrm); for (int i = 0; i < k; i++) v[i] = u[i] / nrm;
        }
        double lam = 0; for (int i = 0; i < k; i++) { double r = 0; for (int j = 0; j < k; j++) r += B[i*k+j] * v[j]; lam += v[i] * r; }
        if (lam > 1e-12) {
            int np = 0; double q = 0;
            for (int i = 0; i < k; i++) { double si = v[i] >= 0 ? 1 : -1; if (si > 0) np++; for (int j = 0; j < k; j++) q += si * B[i*k+j] * (v[j] >= 0 ? 1 : -1); }
            *Q = q / (2 * m2); *small = np < k - np ? np : k - np;   /* s^T B s / (4m) with 2m = m2 */
        }
    }
    free(d); free(B); free(v); free(u);
}

int layer_graph_windows(const double *X, int T, int k, int w, int s, int L, double *out, int maxw) {
    if (k < 2 || w < L + 3 || T < w) return -1;
    double *W = malloc(k*k*sizeof(double)), *Lp = malloc(k*k*sizeof(double)), *ev = malloc(k*sizeof(double)), *d = malloc(k*sizeof(double));
    int nw = 0;
    for (int t0 = 0; t0 + w <= T && nw < maxw; t0 += s, nw++) {
        double tot = 0;
        for (int i = 0; i < k; i++) { W[i*k+i] = 0; for (int j = i + 1; j < k; j++) {
            double best = 0; for (int g = 0; g <= L; g++) { double a = fabs(corr(X, k, i, j, t0, w, g)), b = fabs(corr(X, k, j, i, t0, w, g)); if (a > best) best = a; if (b > best) best = b; }
            W[i*k+j] = W[j*k+i] = best; tot += best; } }
        for (int i = 0; i < k; i++) { d[i] = 0; for (int j = 0; j < k; j++) d[i] += W[i*k+j]; }
        for (int i = 0; i < k; i++) for (int j = 0; j < k; j++)
            Lp[i*k+j] = (i == j ? (d[i] > 0 ? 1.0 : 0.0) : 0.0) - ((d[i] > 0 && d[j] > 0) ? W[i*k+j] / sqrt(d[i]*d[j]) : 0.0);
        jacobi(Lp, k, ev);
        double l2 = 1e9, lmax = 0, sum = 0, H = 0; int zi = 0;
        for (int i = 0; i < k; i++) { if (ev[i] < ev[zi]) zi = i; if (ev[i] > lmax) lmax = ev[i]; sum += ev[i] > 0 ? ev[i] : 0; }
        for (int i = 0; i < k; i++) if (i != zi && ev[i] < l2) l2 = ev[i];
        for (int i = 0; i < k; i++) { double p = ev[i] > 0 && sum > 0 ? ev[i] / sum : 0; if (p > 0) H -= p * log(p); }
        double Q, sm; modularity(W, k, &Q, &sm);
        double *o = out + nw * 6; o[0] = l2; o[1] = H; o[2] = tot; o[3] = lmax; o[4] = Q; o[5] = sm;
    }
    free(W); free(Lp); free(ev); free(d);
    return nw;
}
