typedef struct {
    double *array;
    int used;
    int size;
} DoubleArray;

typedef struct {
    int *array;
    int used;
    int size;
} IntArray;

void initDoubleArray(DoubleArray *a, int initialSize);
void insertIntoDoubleArray(DoubleArray *a, double element);
void freeDoubleArray(DoubleArray *a);

void initIntArray(IntArray *a, int initialSize);
void insertIntoIntArray(IntArray *a, int element);
void freeIntArray(IntArray *a);