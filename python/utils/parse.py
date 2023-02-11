
def parse_iteration_line(line, datatype):
    return [datatype(it) if it != "NULL" else None for it in reversed(list(line.split())[1:])]


def read_benchmark(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
        n = int(lines[0].split()[0])
        m = int(lines[1].split()[0])
        nonzeros = int(lines[2].split()[0])
        max_two_norm_in_colum_or_b = float(lines[3].split()[0])
        max_c = float(lines[4].split()[0])
        max_nonzeros_in_aj = int(lines[5].split()[0])
        solved_optimally = bool(int(lines[6].split()[0]))

        per_iteration_start_index = 7

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

        try:
            assert iterations == len(inverse_time_per_iteration)
            assert iterations == len(reduced_cost_times_per_iteration)
            assert iterations == len(pivot_time_per_iteration)
            assert iterations == len(abs_max_reduced_cost_iteration)
            assert iterations == len(nonzeros_in_basis)
            assert iterations == len(condition_numbers)
            assert iterations == len(inverse_one_norms)
            assert iterations == len(one_norms)
            assert iterations == len(max_nonzeros_in_basis_columns)

        except AssertionError:
            return None

        runtime_per_iteration = [inverse_time_per_iteration[i] +
                                 pivot_time_per_iteration[i] + reduced_cost_times_per_iteration[i] for
                                 i in range(len(basis_candidate_columns))]

    return {
        "n": n,
        "m": m,
        "solved_optimally": solved_optimally,
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

