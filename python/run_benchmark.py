import subprocess
import os
from aemeasure import MeasurementSeries, Database, read_as_pandas_table
import timeit
from tqdm import tqdm
import slurminade
import argparse
from utils.config import PivotRule, RatioTest, BenchmarkConfig
from utils.parse import read_benchmark

slurminade.update_default_configuration(partition="alg",
                                        nodelist="algry03")  # nodelist="algpc01", constraint="alggen02"
slurminade.set_dispatch_limit(50)


@slurminade.slurmify
def run_benchmark(executable: str, out_dir: str, benchmark_dir: str):
    benchmarks = [BenchmarkConfig(PivotRule.STEEPEST_EDGE, RatioTest.HARRIS_TWO_PASS_RATIO),
                  BenchmarkConfig(PivotRule.DANZIG, RatioTest.HARRIS_TWO_PASS_RATIO)]

    current_results = read_as_pandas_table(out_dir)
    benchmark_file = os.path.join(out_dir, "benchmark.out")

    with MeasurementSeries(out_dir) as ms:
        for file in tqdm(os.listdir(benchmark_dir)):
            if not file.endswith(".mps") and not file.endswith(".mps.gz"):
                continue

            instance_name = file.rstrip(".gz")
            instance_name = instance_name.rstrip(".mps")

            if not instance_name:
                continue

            if "instance" in current_results and len(current_results[current_results["instance"] == instance_name]) > 0:
                continue

            file_path = os.path.join(benchmark_dir, file)

            for i, benchmark_config in enumerate(benchmarks):

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
                        [os.path.abspath(executable), os.path.abspath(file_path), "--freemps", "--simplex", "--primal"] + options,
                        timeout=300, capture_output=True, text=True,
                        cwd=os.path.abspath(os.path.join(os.getcwd(), out_dir)))
                    stop = timeit.default_timer()

                except subprocess.TimeoutExpired:
                    continue

                if os.path.exists(benchmark_file):
                    result = read_benchmark(benchmark_file)

                    if result is None:
                        continue

                    with ms.measurement() as m:
                        print("Reading results")

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

                        print("Compressing and saving")
                        print("Cleanup")
                        os.remove(benchmark_file)

    if os.path.exists(benchmark_file):
        os.remove(benchmark_file)

    Database(out_dir).compress()
    os.system("echo 'FINISHED' | mail -s 'Slurm' mperk@ibr.cs.tu-bs.de")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--executable", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    benchmark_dir = args.benchmark_dir
    out_dir = args.out_dir

    if args.debug:
        slurminade.set_dispatcher(slurminade.SubprocessDispatcher())

    run_benchmark.distribute(args.executable, out_dir, benchmark_dir)
