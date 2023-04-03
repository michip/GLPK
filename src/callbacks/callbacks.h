#ifndef CALLBACKS_H
#define CALLBACKS_H

#include "spxlp.h"

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API
#endif
// m, A_B, A_B^-1, #candidateColumns, absMaxReducedCost
typedef void (*CALLBACK)(int, double **, double **, int, double);

extern CALLBACK iterationCallback;

API void setIterationCallback(CALLBACK cb);

double **createBasisMatrixShare(SPXLP *lp);

double **createInverseMatrixShare(SPXLP *lp);

#endif