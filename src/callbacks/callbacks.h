#ifndef CALLBACKS_H
#define CALLBACKS_H

#include "spxlp.h"

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API
#endif
typedef void (*NEW_ITERATION_CALLBACK)();
// m, A_B, A_B^-1, #candidateColumns, absMaxReducedCost
typedef void (*ITERATION_DATA_CALLBACK)(int, double **, double **, int, double);
typedef void (*ITERATION_TIME_CALLBACK)(unsigned int);

extern NEW_ITERATION_CALLBACK newIterationCallback;
extern ITERATION_DATA_CALLBACK iterationCallback;
extern ITERATION_TIME_CALLBACK iterationTimeCallback;

API void setNewIterationCallback(NEW_ITERATION_CALLBACK cb);
API void setIterationCallback(ITERATION_DATA_CALLBACK cb);
API void setIterationTimeCallback(ITERATION_TIME_CALLBACK cb);

double **createBasisMatrixShare(SPXLP *lp);

double **createInverseMatrixShare(SPXLP *lp);

#endif