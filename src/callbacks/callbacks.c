#include <stdlib.h>
#include <printf.h>
#include <signal.h>
#include "callbacks.h"

NEW_ITERATION_CALLBACK newIterationCallback;
ITERATION_DATA_CALLBACK iterationCallback;
ITERATION_TIME_CALLBACK iterationTimeCallback;
INITIAL_DATA_CALLBACK initialDataCallback;

struct ITERATION_DATA currentIterationData;

API void setNewIterationCallback(NEW_ITERATION_CALLBACK cb) {
    newIterationCallback = cb;
}

API void setIterationCallback(ITERATION_DATA_CALLBACK cb) {
    iterationCallback = cb;
}

API void setIterationTimeCallback(ITERATION_TIME_CALLBACK cb) {
    iterationTimeCallback = cb;
}

API void setInitialDataCallback(INITIAL_DATA_CALLBACK cb) {
    initialDataCallback = cb;
}

void allocateIterationData(SPXLP *lp) {
    if (currentIterationData.basis.array != NULL ||
        currentIterationData.basisCols.array != NULL ||
        currentIterationData.basisRows.array != NULL ||
            currentIterationData.u.array != NULL) {
        freeIterationData();
    }
    initDoubleArray(&currentIterationData.basis, lp->m);
    initIntArray(&currentIterationData.basisRows, lp->m);
    initIntArray(&currentIterationData.basisCols, lp->m);
    initDoubleArray(&currentIterationData.u, lp->m);
}

void freeIterationData() {
    if (currentIterationData.basis.array == NULL ||
        currentIterationData.basisCols.array == NULL ||
        currentIterationData.basisRows.array == NULL ||
        currentIterationData.u.array == NULL) {
        printf("Current iteration data freed before it was filled.");
        exit(SIGABRT);
    }

    freeDoubleArray(&currentIterationData.basis);
    freeIntArray(&currentIterationData.basisRows);
    freeIntArray(&currentIterationData.basisCols);
    freeDoubleArray(&currentIterationData.u);
}
