#include <stdlib.h>
#include "dynamic_array.h"

void initDoubleArray(DoubleArray *a, int initialSize) {
    a->array = malloc(initialSize * sizeof(double));
    a->used = 0;
    a->size = initialSize;
}

void insertIntoDoubleArray(DoubleArray *a, double element) {
    if (a->used == a->size) {
        a->size *= 2;
        a->array = realloc(a->array, a->size * sizeof(double));
    }
    a->array[a->used++] = element;
}

void freeDoubleArray(DoubleArray *a) {
    free(a->array);
    a->array = NULL;
    a->used = a->size = 0;
}

void initIntArray(IntArray *a, int initialSize) {
    a->array = malloc(initialSize * sizeof(int));
    a->used = 0;
    a->size = initialSize;
}

void insertIntoIntArray(IntArray *a, int element) {
    if (a->used == a->size) {
        a->size *= 2;
        a->array = realloc(a->array, a->size * sizeof(int));
    }
    a->array[a->used++] = element;
}

void freeIntArray(IntArray *a) {
    free(a->array);
    a->array = NULL;
    a->used = a->size = 0;
}