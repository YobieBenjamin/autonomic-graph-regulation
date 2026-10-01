/* Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed. | SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE) | Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71 */
/* YB-0001 core: heat-trace spectral signature of a weighted undirected graph.
 * Given symmetric non-negative adjacency A (n x n, row-major), computes the
 * normalized Laplacian L = I - D^-1/2 A D^-1/2, its eigenvalues via cyclic
 * Jacobi rotation, and the heat trace h(t) = sum_k exp(-t * lambda_k).
 * Isolated nodes get a zero Laplacian row, so each contributes exp(0) = 1.
 * Build: gcc -O2 -shared -fPIC -o libheattrace.so heattrace.c -lm            */
#include <math.h>
#include <stdlib.h>
#include <string.h>

static void jacobi_eigvals(double *M, int n, double *out) {
    for (int sweep = 0; sweep < 100; sweep++) {
        double off = 0.0;
        for (int p = 0; p < n; p++)
            for (int q = p + 1; q < n; q++) off += M[p*n+q] * M[p*n+q];
        if (off < 1e-22) break;
        for (int p = 0; p < n; p++) {
            for (int q = p + 1; q < n; q++) {
                double apq = M[p*n+q];
                if (fabs(apq) < 1e-300) continue;
                double app = M[p*n+p], aqq = M[q*n+q];
                double theta = (aqq - app) / (2.0 * apq);
                double t = (theta >= 0 ? 1.0 : -1.0) / (fabs(theta) + sqrt(theta*theta + 1.0));
                double c = 1.0 / sqrt(t*t + 1.0), s = t * c;
                for (int k = 0; k < n; k++) {
                    double mkp = M[k*n+p], mkq = M[k*n+q];
                    M[k*n+p] = c*mkp - s*mkq;
                    M[k*n+q] = s*mkp + c*mkq;
                }
                for (int k = 0; k < n; k++) {
                    double mpk = M[p*n+k], mqk = M[q*n+k];
                    M[p*n+k] = c*mpk - s*mqk;
                    M[q*n+k] = s*mpk + c*mqk;
                }
            }
        }
    }
    for (int i = 0; i < n; i++) out[i] = M[i*n+i];
}

int heat_trace(const double *A, int n, const double *ts, int nt,
               double *trace_out, double *eig_out) {
    double *deg = calloc(n, sizeof(double));
    double *L = malloc((size_t)n * n * sizeof(double));
    double *ev = malloc(n * sizeof(double));
    if (!deg || !L || !ev) { free(deg); free(L); free(ev); return 1; }
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) deg[i] += A[i*n+j];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            double v = 0.0;
            if (deg[i] > 0 && deg[j] > 0) v = -A[i*n+j] / sqrt(deg[i] * deg[j]);
            if (i == j) v += (deg[i] > 0) ? 1.0 : 0.0;
            L[i*n+j] = v;
        }
    jacobi_eigvals(L, n, ev);
    for (int k = 0; k < nt; k++) {
        double s = 0.0;
        for (int i = 0; i < n; i++) s += exp(-ts[k] * ev[i]);
        trace_out[k] = s;
    }
    if (eig_out) memcpy(eig_out, ev, n * sizeof(double));
    free(deg); free(L); free(ev);
    return 0;
}
