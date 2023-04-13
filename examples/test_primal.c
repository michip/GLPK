#include "primalsimplex.c"
#include "callbacks/callbacks.h"

void iteration_data_cb(int a,
                        double * b, int * c, int * d, int e, // basis
                        //double * f, int * g, int * h, int i, //inverse
                        int j, double k, double l) {
    xprintf("CALLBACK REACHED");
}

void initial_data_cb(int a, int b,
                     double * c,
                     double * d, int * e, int * f, int g,
                     double * h){
    xprintf("INITIAL");
}

void new_iteration(){
    xprintf("NEW IT");
}
int main(int argc, char *argv[]) {
    setInitialDataCallback(initialDataCallback);
    setNewIterationCallback(new_iteration);
    setIterationCallback(iteration_data_cb);
    runPrimalSimplex("../../../simplex-benchmarks/out/mps/random_graphs/min/erdos_renyi_90_0.4.dimac_vc.mps", 60,
                     1, 2, 2);
}