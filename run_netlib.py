import subprocess
import os
from dataclasses import dataclass

from aemeasure import MeasurementSeries, Database, read_as_pandas_table
import timeit
from enum import Enum


benchmark_dir = "benchmark/netlib/netlib"
out_dir = "./results"


class RatioTest(Enum):
    HARRIS_TWO_PASS_RATIO = 1
    NO_HARRIS_TWO_PASS_RATIO = 2


class PivotRule(Enum):
    STEEPEST_EDGE = 1
    DANZIG = 2


@dataclass
class BenchmarkConfig:
    pivot_rule: PivotRule
    ratio_test: RatioTest

full_benchmark = [
    ["--steep", "--relax"],
    ["--nosteep", "--relax"],
    ["--steep", "--norelax"],
    ["--nosteep", "--norelax"],
    ["--steep", "--flip"],
    # ["--nosteep", "--flip"],
]

single_benchmark = [BenchmarkConfig(PivotRule.STEEPEST_EDGE, RatioTest.HARRIS_TWO_PASS_RATIO)]


def parse_iteration_line(line, datatype):
    return [datatype(it) if it != "NULL" else None for it in reversed(list(line.split())[1:])]


def read_benchmark():
    with open("benchmark.out", "r") as f:
        lines = f.readlines()
        n = int(lines[0].split()[0])
        m = int(lines[1].split()[0])
        nonzeros = int(lines[2].split()[0])
        max_two_norm_in_colum_or_b = float(lines[3].split()[0])
        max_c = float(lines[4].split()[0])
        max_nonzeros_in_aj = int(lines[5].split()[0])

        per_iteration_start_index = 6

        # per iterations
        basis_candidate_columns = parse_iteration_line(lines[per_iteration_start_index], int)
        max_nonzeros_in_basis_columns = parse_iteration_line(lines[per_iteration_start_index+1], int)
        one_norms = parse_iteration_line(lines[per_iteration_start_index+2], float)
        inverse_one_norms = parse_iteration_line(lines[per_iteration_start_index+3], float)
        condition_numbers = parse_iteration_line(lines[per_iteration_start_index+4], float)

        inverse_time_per_iteration = parse_iteration_line(lines[per_iteration_start_index+5], int)
        inverse_time_2_per_iteration = parse_iteration_line(lines[per_iteration_start_index+6], int)

        inverse_time_per_iteration = [v + inverse_time_2_per_iteration[i] for i, v in
                                      enumerate(inverse_time_per_iteration)]

        reduced_cost_times_per_iteration = parse_iteration_line(lines[per_iteration_start_index+7], int)
        pivot_time_per_iteration = parse_iteration_line(lines[per_iteration_start_index+8], int)
        abs_max_reduced_cost_iteration = parse_iteration_line(lines[per_iteration_start_index+9], float)
        nonzeros_in_basis = parse_iteration_line(lines[per_iteration_start_index+10], int)

        iterations = len(basis_candidate_columns)

        assert iterations == len(inverse_time_per_iteration)
        assert iterations == len(reduced_cost_times_per_iteration)
        assert iterations == len(pivot_time_per_iteration)
        assert iterations == len(abs_max_reduced_cost_iteration)
        assert iterations == len(nonzeros_in_basis)
        assert iterations == len(condition_numbers)
        assert iterations == len(inverse_one_norms)
        assert iterations == len(one_norms)
        assert iterations == len(max_nonzeros_in_basis_columns)

        runtime_per_iteration = [inverse_time_per_iteration[i] +
                                 pivot_time_per_iteration[i] + reduced_cost_times_per_iteration[i] for
                                 i in range(len(basis_candidate_columns))]

    return {
        "n": n,
        "m": m,
        "iterations": iterations,
        "nonzeros": nonzeros,
        "max_c": max_c,
        "d_max": max_nonzeros_in_aj,
        "d_max_basis_per_iteration": max_nonzeros_in_basis_columns,
        "basis_norm_per_iteration": one_norms,
        "inverse_basis_norm_per_iteration": inverse_one_norms,
        "condition_number_per_iteration": condition_numbers,
        "no_candidate_basis_per_iteration": basis_candidate_columns,
        "inverse_time_per_iteration": inverse_time_per_iteration,
        "reduced_cost_time_per_iteration": reduced_cost_times_per_iteration,
        "pivot_time_per_iteration": pivot_time_per_iteration,
        "runtime_per_iteration": runtime_per_iteration,
        "abs_max_reduced_cost_per_iteration": abs_max_reduced_cost_iteration,
        "nonzeros_in_basis_per_iteration": nonzeros_in_basis,
        "max_two_norm_in_colum_or_b": max_two_norm_in_colum_or_b,
    }


current_results = read_as_pandas_table(out_dir)

with MeasurementSeries(out_dir) as ms:
    for file in os.listdir(benchmark_dir):
        if not file.endswith(".mps"):
            continue

        instance_name = file.rstrip(".mps")

        if not instance_name:
            continue

        if "instance" in current_results and len(current_results[current_results["instance"] == instance_name]) > 0:
            continue

        file_path = os.path.join(benchmark_dir, file)

        for i, benchmark_config in enumerate(single_benchmark):

            options = []

            if benchmark_config.pivot_rule == PivotRule.STEEPEST_EDGE:
                options.append("--steep")
            elif benchmark_config.pivot_rule == PivotRule.DANZIG:
                options.append("--nosteep")
            else:
                raise ValueError()

            if benchmark_config.ratio_test == RatioTest.HARRIS_TWO_PASS_RATIO:
                options.append("--relax")
            elif benchmark_config.ratio_test == RatioTest.NO_HARRIS_TWO_PASS_RATIO:
                options.append("--norelax")
            else:
                raise ValueError()

            try:
                start = timeit.default_timer()
                process = subprocess.run(
                    ["cmake-build-release/bin/glpsol", file_path, "--mps", "--simplex", "--primal"] + options,
                    timeout=300, capture_output=True, text=True)
                stop = timeit.default_timer()
            except subprocess.TimeoutExpired:
                continue

            if os.path.exists("benchmark.out"):
                with ms.measurement() as m:
                    print("Reading results")
                    result = read_benchmark()
                    for key, val in result.items():
                        m[key] = val

                    m["solver_stdout"] = process.stdout
                    m["solver_stderr"] = process.stderr

                    m["runtime"] = stop - start
                    m["instance"] = instance_name

                    if benchmark_config.pivot_rule == PivotRule.DANZIG:
                        m["pivot_rule"] = "dantzig"
                    elif benchmark_config.pivot_rule == PivotRule.STEEPEST_EDGE:
                        m["pivot_rule"] = "steepest"

                    if benchmark_config.ratio_test == RatioTest.HARRIS_TWO_PASS_RATIO:
                        m["ratio_test"] = "harris"
                    elif benchmark_config.ratio_test == RatioTest.NO_HARRIS_TWO_PASS_RATIO:
                        m["ratio_test"] = "default"

                    print("Compressing ans saving")
                    print("Cleanup")
                    os.remove("benchmark.out")

Database(out_dir).compress()
