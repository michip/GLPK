#ifndef CALLBACKS_H
#define CALLBACKS_H

#include "spxlp.h"
#include "dynamic_array.h"

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API
#endif
typedef void (*NEW_ITERATION_CALLBACK)();
// m, A_B, A_B^-1, #candidateColumns, absMaxReducedCost
typedef void (*ITERATION_DATA_CALLBACK)(
        int,
        double *, int *, int *, int, // basis
        //double *, int *, int *, int, //inverse
        int, // candidate columns
        double, // max reduced cost
        double // condition number (under 1-norm)
        );
typedef void (*ITERATION_TIME_CALLBACK)(unsigned int);
typedef void (*INITIAL_DATA_CALLBACK)(
        int, int, // n, m
        double *, // c
        double *, int *, int *, int, // A
        double * // b
        );

extern INITIAL_DATA_CALLBACK initialDataCallback;
extern NEW_ITERATION_CALLBACK newIterationCallback;
extern ITERATION_DATA_CALLBACK iterationCallback;
extern ITERATION_TIME_CALLBACK iterationTimeCallback;

API void setInitialDataCallback(INITIAL_DATA_CALLBACK cb);
API void setNewIterationCallback(NEW_ITERATION_CALLBACK cb);
API void setIterationCallback(ITERATION_DATA_CALLBACK cb);
API void setIterationTimeCallback(ITERATION_TIME_CALLBACK cb);

void allocateIterationData(SPXLP *lp);
void freeIterationData();

struct ITERATION_DATA {
    int m;
    unsigned int callbackTimes;
    IntArray basisCols;
    IntArray basisRows;
    DoubleArray basis;
    double maxReducedCost;
    double conditionNumberOneNorm;
    int candidateColumns;
};

extern struct ITERATION_DATA currentIterationData;

#endif