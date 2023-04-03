#include <stdlib.h>
#include <printf.h>
#include "callbacks.h"

NEW_ITERATION_CALLBACK newIterationCallback;
ITERATION_DATA_CALLBACK iterationCallback;
ITERATION_TIME_CALLBACK iterationTimeCallback;

API void setNewIterationCallback(NEW_ITERATION_CALLBACK cb) {
    newIterationCallback = cb;
}

API void setIterationCallback(ITERATION_DATA_CALLBACK cb) {
    iterationCallback = cb;
}

API void setIterationTimeCallback(ITERATION_TIME_CALLBACK cb) {
    iterationTimeCallback = cb;
}

void writeZeros(SPXLP *lp, double **M) {
    for (int i = 0; i < lp->m; i++) {
        for (int j = 0; j < lp->m; j++) {
            M[i][j] = 0; // row, column
        }
    }
}

void allocateMatrix(SPXLP *lp, double **M) {
    for (int i = 0; i < lp->m; i++) {
        M[i] = (double *) malloc(lp->m * sizeof(double *));
    }
}

double **createBasisMatrixShare(SPXLP *lp) {
    static double **basis = NULL;
    if (basis == NULL) {
        basis = malloc(sizeof(int *) * lp->m);
        allocateMatrix(lp, basis);
    }

    writeZeros(lp, basis);
    return basis;
}

double **createInverseMatrixShare(SPXLP *lp) {
    static double **inverse = NULL;
    if (inverse == NULL) {
        inverse = malloc(sizeof(int *) * lp->m);
        allocateMatrix(lp, inverse);
    }
    writeZeros(lp, inverse);
    return inverse;
}

