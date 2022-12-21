import subprocess
import os
import compress_json
import timeit

benchmark_dir = "benchmark/netlib/netlib"

full_benchmark = [
    ["--steep", "--relax"],
    ["--nosteep", "--relax"],
    ["--steep", "--norelax"],
    ["--nosteep", "--norelax"],
    ["--steep", "--flip"],
    # ["--nosteep", "--flip"],
]

single_benchmark = [["--steep", "--relax"]]


def read_benchmark():
    with open("benchmark.out", "r") as f:
        lines = f.readlines()
        n = int(lines[0].split()[0])
        m = int(lines[1].split()[0])
        nonzeros = int(lines[2].split()[0])
        no_candidate_basis = [int(it) for it in reversed(lines[3].split())]

        inverse_time_per_iteration = [int(it) for it in reversed(lines[4].split())]
        inverse_time_2_per_iteration = [int(it) for it in reversed(lines[5].split())]

        inverse_time_per_iteration = [v + inverse_time_2_per_iteration[i] for i, v in
                                      enumerate(inverse_time_per_iteration)]

        reduced_cost_times_per_iteration = [int(it) for it in reversed(lines[6].split())]
        pivot_time_per_iteration = [int(it) for it in reversed(lines[7].split())]

        assert len(no_candidate_basis) == len(inverse_time_per_iteration)
        assert len(no_candidate_basis) == len(reduced_cost_times_per_iteration)
        assert len(no_candidate_basis) == len(pivot_time_per_iteration)

        runtime_per_iteration = [inverse_time_per_iteration[i] +
                                 pivot_time_per_iteration[i] + reduced_cost_times_per_iteration[i] for
                                 i in range(len(no_candidate_basis))]


    return {
        "n": n,
        "m": m,
        "nonzeros": nonzeros,
        "no_candidate_basis": no_candidate_basis,
        "inverse_time_per_iteration": inverse_time_per_iteration,
        "reduced_cost_time_per_iteration": reduced_cost_times_per_iteration,
        "pivot_time_per_iteration": pivot_time_per_iteration,
        "time_per_iteration": runtime_per_iteration,
    }


for file in os.listdir(benchmark_dir):
    if not file.endswith(".mps"):
        continue

    file_path = os.path.join(benchmark_dir, file)

    for i, options in enumerate(single_benchmark):
        out_file = f"out/{file.rstrip('.mps')}.gz"

        if os.path.isfile(out_file):
            continue

        try:
            start = timeit.default_timer()
            subprocess.run(
                ["cmake-build-release/bin/glpsol", file_path, "--mps", "--simplex", "--primal"] + options, timeout=300)
            stop = timeit.default_timer()
        except subprocess.TimeoutExpired:
            continue

        if os.path.exists("benchmark.out"):
            print("Reading results")
            result = read_benchmark()
            result["runtime"] = stop - start
            result["instance"] = file.rstrip(".mps")

            print("Compressing ans saving")
            # os.makedirs(f"out/{result['instance']}", exist_ok=True)
            compress_json.dump(result, out_file)

            print("Cleanup")
            os.remove("benchmark.out")
