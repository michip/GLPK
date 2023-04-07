#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <ctype.h>
#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <glpk.h>

#define xassert glp_assert
#define xerror  glp_error
#define xprintf glp_printf

struct csa {     /* common storage area */
    glp_prob *prob;
    /* LP/MIP problem object */
    glp_bfcp bfcp;
    /* basis factorization control parameters */
    glp_smcp smcp;
    /* simplex method control parameters */
    glp_iptcp iptcp;
    /* interior-point method control parameters */
    glp_iocp iocp;
    /* integer optimizer control parameters */
    glp_tran *tran;
    /* model translator workspace */
    glp_graph *graph;
    /* network problem object */
    int format;
    /* problem file format: */
#define FMT_MPS_DECK    1  /* fixed MPS */
#define FMT_MPS_FILE    2  /* free MPS */
#define FMT_LP          3  /* CPLEX LP */
#define FMT_GLP         4  /* GLPK LP/MIP */
#define FMT_MATHPROG    5  /* MathProg */
#define FMT_MIN_COST    6  /* DIMACS min-cost flow */
#define FMT_MAX_FLOW    7  /* DIMACS maximum flow */
#define FMT_CNF         8  /* DIMACS CNF-SAT */
    const char *in_file;
    /* name of input problem file */
#define DATA_MAX 10
    /* maximal number of input data files */
    int ndf;
    /* number of input data files specified */
    const char *in_data[1 + DATA_MAX];
    /* name(s) of input data file(s) */
    const char *out_dpy;
    /* name of output file to send display output; NULL means the
       display output is sent to the terminal */
    int seed;
    /* seed value to be passed to the MathProg translator; initially
       set to 1; 0x80000000 means the value is omitted */
    int solution;
    /* solution type flag: */
#define SOL_BASIC       1  /* basic */
#define SOL_INTERIOR    2  /* interior-point */
#define SOL_INTEGER     3  /* mixed integer */
    const char *in_res;
    /* name of input solution file in raw format */
    int dir;
    /* optimization direction flag:
       0       - not specified
       GLP_MIN - minimization
       GLP_MAX - maximization */
    int scale;
    /* automatic problem scaling flag */
    const char *out_sol;
    /* name of output solution file in printable format */
    const char *out_res;
    /* name of output solution file in raw format */
    const char *out_ranges;
    /* name of output file to write sensitivity analysis report */
    int check;
    /* input data checking flag; no solution is performed */
    const char *new_name;
    /* new name to be assigned to the problem */
    int hide;
    /* clear all symbolic names in the problem object */
    const char *out_mps;
    /* name of output problem file in fixed MPS format */
    const char *out_freemps;
    /* name of output problem file in free MPS format */
    const char *out_cpxlp;
    /* name of output problem file in CPLEX LP format */
    const char *out_glp;
    /* name of output problem file in GLPK format */
    const char *out_cnf;
    /* name of output problem file in DIMACS CNF-SAT format */
    const char *log_file;
    /* name of output file to hardcopy terminal output */
    int crash;
    /* initial basis option: */
#define USE_STD_BASIS   1  /* use standard basis */
#define USE_ADV_BASIS   2  /* use advanced basis */
#define USE_CPX_BASIS   3  /* use Bixby's basis */
#define USE_INI_BASIS   4  /* use initial basis from ini_file */
    const char *ini_file;
    /* name of input file containing initial basis */
    int exact;
    /* flag to use glp_exact rather than glp_simplex */
    int xcheck;
    /* flag to check final basis with glp_exact */
    int nomip;
    /* flag to consider MIP as pure LP */
    int minisat;
    /* option to solve feasibility problem with MiniSat solver */
    int use_bnd;
    /* option to bound objective function */
    int obj_bnd;
    /* upper (minization) or lower (maximization) objective bound */
    const char *use_sol;
    /* name of input mip solution file in GLPK format */
};

static void print_version(int briefly) {     /* print version information */
    xprintf("GLPSOL--GLPK LP/MIP Solver %s\n", glp_version());
    if (briefly) goto done;
    xprintf("Copyright (C) 2000-2020 Free Software Foundation, Inc.\n"
    );
    xprintf("\n");
    xprintf("This program has ABSOLUTELY NO WARRANTY.\n");
    xprintf("\n");
    xprintf("This program is free software; you may re-distribute it "
            "under the terms\n");
    xprintf("of the GNU General Public License version 3 or later.\n");
    done:
    return;
}