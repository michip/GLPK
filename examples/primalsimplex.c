#include <stdlib.h>
#include "glpsol.c"
#include <limits.h>
#include <stdio.h>

#include <glpk.h>

int runPrimalSimplex(const char *file_path, int tm_lim, int pivot_rule, int ratio_test) {
    xprintf("Solving %s \n", file_path);
    xprintf("Time limit: %d \n", tm_lim);
    struct csa _csa, *csa = &_csa;
    int ret;

    double start;
    /* perform initialization */

    csa->prob = glp_create_prob();
    glp_get_bfcp(csa->prob, &csa->bfcp);
    glp_init_smcp(&csa->smcp);
    csa->smcp.presolve = GLP_ON;
    glp_init_iptcp(&csa->iptcp);
    glp_init_iocp(&csa->iocp);
    csa->iocp.presolve = GLP_ON;
    csa->tran = NULL;
    csa->graph = NULL;
    csa->format = FMT_MPS_FILE;
    csa->in_file = NULL;
    csa->ndf = 0;
    csa->out_dpy = NULL;
    csa->seed = 1;
    csa->solution = SOL_BASIC;
    csa->in_res = NULL;
    csa->dir = 0;
    csa->scale = 1;
    csa->out_sol = NULL;
    csa->out_res = NULL;
    csa->out_ranges = NULL;
    csa->check = 0;
    csa->new_name = NULL;
    csa->hide = 0;
    csa->out_mps = NULL;
    csa->out_freemps = NULL;
    csa->out_cpxlp = NULL;
    csa->out_glp = NULL;

    csa->out_cnf = NULL;
    csa->log_file = NULL;
    csa->crash = USE_ADV_BASIS;
    csa->ini_file = NULL;
    csa->exact = 0;
    csa->xcheck = 0;
    csa->nomip = 0;
    csa->minisat = 0;
    csa->use_bnd = 0;
    csa->obj_bnd = 0;

    csa->use_sol = NULL;

    /* Set params */
    csa->in_file = file_path;

    csa->format = FMT_MPS_FILE;
    csa->solution = SOL_BASIC;

    if (tm_lim <= INT_MAX / 1000)
        csa->smcp.tm_lim = csa->iocp.tm_lim = 1000 * tm_lim;
    else
        csa->smcp.tm_lim = csa->iocp.tm_lim = INT_MAX;

    csa->smcp.meth = GLP_PRIMAL;

    if (pivot_rule == 1) {
        csa->smcp.pricing = GLP_PT_PSE; // Steepest Edge
        xprintf("Using steepest edge pivot.\n");
    } else if(pivot_rule == 2) {
        csa->smcp.pricing = GLP_PT_STD; // Danzig
        xprintf("Using Danzig pivot.\n");
    } else xassert(csa != csa);

    if (ratio_test == 1) {
        csa->smcp.r_test = GLP_RT_HAR; // Harris' two-pass ratio test
        xprintf("Using Harris two-pass ratio test.\n");
    } else if(ratio_test == 2) {
        csa->smcp.r_test = GLP_RT_STD;; // Standard ratio test
        xprintf("Using standard ratio test.\n");
    } else xassert(csa != csa);

    /* end set parameters */

    /*--------------------------------------------------------------*/
    /* remove all output files specified in the command line */
    if (csa->out_dpy != NULL) remove(csa->out_dpy);
    if (csa->out_sol != NULL) remove(csa->out_sol);
    if (csa->out_res != NULL) remove(csa->out_res);
    if (csa->out_ranges != NULL) remove(csa->out_ranges);
    if (csa->out_mps != NULL) remove(csa->out_mps);
    if (csa->out_freemps != NULL) remove(csa->out_freemps);
    if (csa->out_cpxlp != NULL) remove(csa->out_cpxlp);
    if (csa->out_glp != NULL) remove(csa->out_glp);
    if (csa->out_cnf != NULL) remove(csa->out_cnf);
    if (csa->log_file != NULL) remove(csa->log_file);

    /*--------------------------------------------------------------*/
    /* print version information */
    print_version(1);

    /*--------------------------------------------------------------*/
    /* read problem data from the input file */
    if (csa->format == FMT_MPS_FILE) {
        ret = glp_read_mps(csa->prob, GLP_MPS_FILE, NULL,
                           csa->in_file);
        if (ret != 0) {
            xprintf("MPS file processing error\n");
            ret = EXIT_FAILURE;
            goto done;
        }
    } else
                xassert (csa != csa);
    /*--------------------------------------------------------------*/
    /* change problem name, if required */
    if (csa->new_name != NULL)
        glp_set_prob_name(csa->prob, csa->new_name);
    /* change optimization direction, if required */
    if (csa->dir != 0)
        glp_set_obj_dir(csa->prob, csa->dir);
    /* sort elements of the constraint matrix */
    glp_sort_matrix(csa->prob);
    /*--------------------------------------------------------------*/
    /* remove all symbolic names from problem object, if required */
    if (csa->hide) {
        int i, j;
        glp_set_obj_name(csa->prob, NULL);
        glp_delete_index(csa->prob);
        for (i = glp_get_num_rows(csa->prob); i >= 1; i--)
            glp_set_row_name(csa->prob, i, NULL);
        for (j = glp_get_num_cols(csa->prob); j >= 1; j--)
            glp_set_col_name(csa->prob, j, NULL);
    }

    /*--------------------------------------------------------------*/
    /* scale the problem data, if required */
    if (csa->scale) {
        if (csa->solution == SOL_BASIC && !csa->smcp.presolve ||
            csa->solution == SOL_INTERIOR ||
            csa->solution == SOL_INTEGER && !csa->iocp.presolve)
            glp_scale_prob(csa->prob, GLP_SF_AUTO);
    }
    /*--------------------------------------------------------------*/
    /* construct starting LP basis */
    if (csa->solution == SOL_BASIC && !csa->smcp.presolve ||
        csa->solution == SOL_INTEGER && !csa->iocp.presolve) {
        if (csa->crash == USE_STD_BASIS)
            glp_std_basis(csa->prob);
        else if (csa->crash == USE_ADV_BASIS)
            glp_adv_basis(csa->prob, 0);
        else if (csa->crash == USE_CPX_BASIS)
            glp_cpx_basis(csa->prob);
        else if (csa->crash == USE_INI_BASIS) {
            ret = glp_read_sol(csa->prob, csa->ini_file);
            if (ret != 0) {
                xprintf("Unable to read initial basis\n");
                ret = EXIT_FAILURE;
                goto done;
            }
        } else
                    xassert (csa != csa);
    }
    /*--------------------------------------------------------------*/
    /* solve the problem */
    start = glp_time();
    if (csa->solution == SOL_BASIC) {
        if (!csa->exact) {
            glp_set_bfcp(csa->prob, &csa->bfcp);
            glp_simplex(csa->prob, &csa->smcp);
            if (csa->xcheck) {
                if (csa->smcp.presolve &&
                    glp_get_status(csa->prob) != GLP_OPT)
                    xprintf("If you need to check final basis for non-opt"
                            "imal solution, use --nopresol\n");
                else
                    glp_exact(csa->prob, &csa->smcp);
            }
            if (csa->out_sol != NULL || csa->out_res != NULL) {
                if (csa->smcp.presolve &&
                    glp_get_status(csa->prob) != GLP_OPT)
                    xprintf("If you need actual output for non-optimal solut"
                            "ion, use --nopresol\n");
            }
        } else
            glp_exact(csa->prob, &csa->smcp);
    } else
                xassert (csa != csa);

    /*--------------------------------------------------------------*/
    /* display statistics */
    xprintf("Time used:   %.1f secs\n", glp_difftime(glp_time(),
                                                     start));
    {
        size_t tpeak;
        glp_mem_usage(NULL, NULL, NULL, &tpeak);
        xprintf("Memory used: %.1f Mb (%.0f bytes)\n",
                (double) tpeak / 1048576.0, (double) tpeak);
    }
    done: /* delete the LP/MIP problem object */
    if (csa->prob != NULL)
        glp_delete_prob(csa->prob);
    /* close log file, if necessary */
    /* free the GLPK environment */
    glp_free_env();
    /* return to the control program */
    return ret;
}