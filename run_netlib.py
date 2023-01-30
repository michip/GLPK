import subprocess
import os
from aemeasure import MeasurementSeries, Database, read_as_pandas_table
import timeit

benchmark_dir = "benchmark/netlib/netlib"
out_dir = "./results"

full_benchmark = [
    ["--steep", "--relax"],
    ["--nosteep", "--relax"],
    ["--steep", "--norelax"],
    ["--nosteep", "--norelax"],
    ["--steep", "--flip"],
    # ["--nosteep", "--flip"],
]

single_benchmark = [["--steep", "--relax"]]


def parse_iteration_line(line, datatype):
    return [datatype(it) for it in reversed(list(line.split())[1:])]


def read_benchmark():
    """
    10524 # n
    25 # m
    129042 # nonzeros
    1000.000000 # max c
    candidateColumns: 0 0 0
    nonZerosInBasisColumn:
    basis-1-norm: 8.225984
    basis-inverse-1-norm: 5
    conditionNumber: 472.38
    inverseTime: 0 0 0 0 0
    inverseTime2: 0 0 0 574
    reducedCostTime: 0 0 0
    pivotTime: 0 0 0 368 36
    :return:
    """
    with open("benchmark.out", "r") as f:
        lines = f.readlines()
        n = int(lines[0].split()[0])
        m = int(lines[1].split()[0])
        nonzeros = int(lines[2].split()[0])
        max_c = float(lines[3].split()[0])

        # per iterations
        basis_candidate_columns = parse_iteration_line(lines[4], int)
        max_nonzeros_in_basis_columns = parse_iteration_line(lines[5], int)
        one_norms = parse_iteration_line(lines[6], float)
        inverse_one_norms = parse_iteration_line(lines[7], float)
        condition_numbers = parse_iteration_line(lines[8], float)

        inverse_time_per_iteration = parse_iteration_line(lines[9], int)
        inverse_time_2_per_iteration = parse_iteration_line(lines[10], int)

        inverse_time_per_iteration = [v + inverse_time_2_per_iteration[i] for i, v in
                                      enumerate(inverse_time_per_iteration)]

        reduced_cost_times_per_iteration = parse_iteration_line(lines[11], int)
        pivot_time_per_iteration = parse_iteration_line(lines[12], int)

        assert len(basis_candidate_columns) == len(inverse_time_per_iteration)
        assert len(basis_candidate_columns) == len(reduced_cost_times_per_iteration)
        assert len(basis_candidate_columns) == len(pivot_time_per_iteration)

        runtime_per_iteration = [inverse_time_per_iteration[i] +
                                 pivot_time_per_iteration[i] + reduced_cost_times_per_iteration[i] for
                                 i in range(len(basis_candidate_columns))]

    return {
        "n": n,
        "m": m,
        "nonzeros": nonzeros,
        "max_c": max_c,
        "d_basis": max_nonzeros_in_basis_columns,
        "basis_norm": one_norms,
        "inverse_basis_norm": inverse_one_norms,
        "condition_numbers": condition_numbers,
        "no_candidate_basis": basis_candidate_columns,
        "inverse_time_per_iteration": inverse_time_per_iteration,
        "reduced_cost_time_per_iteration": reduced_cost_times_per_iteration,
        "pivot_time_per_iteration": pivot_time_per_iteration,
        "time_per_iteration": runtime_per_iteration,
    }

current_results = read_as_pandas_table(out_dir)

with MeasurementSeries(out_dir) as ms:
    for file in os.listdir(benchmark_dir):
        if not file.endswith(".mps"):
            continue

        instance_name = file.rstrip(".mps")

        if len(current_results[current_results["instance"] == instance_name]) > 0:
            continue

        with ms.measurement() as m:
            file_path = os.path.join(benchmark_dir, file)

            for i, options in enumerate(single_benchmark):
                try:
                    start = timeit.default_timer()
                    subprocess.run(
                        ["cmake-build-release/bin/glpsol", file_path, "--mps", "--simplex", "--primal"] + options,
                        timeout=300)
                    stop = timeit.default_timer()
                except subprocess.TimeoutExpired:
                    continue

                if os.path.exists("benchmark.out"):
                    print("Reading results")
                    result = read_benchmark()

                    for key, val in result.items():
                        m[key] = val

                    m["runtime"] = stop - start
                    m["instance"] = instance_name

                    print("Compressing ans saving")
                    print("Cleanup")
                    os.remove("benchmark.out")

Database(out_dir).compress()
