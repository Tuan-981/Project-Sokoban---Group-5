
import argparse
import cProfile
import pstats

import solution
from sokoban import PROBLEMS
from validation import validate_solution


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=int, default=5)
    parser.add_argument("--timebound", type=float, default=10)
    args = parser.parse_args()

    if not 0 <= args.map < len(PROBLEMS):
        parser.error("Map index is out of range.")

    initial_state = PROBLEMS[args.map]

    profiler = cProfile.Profile()
    result = profiler.runcall(
        solution.solve, initial_state, args.timebound
    )

    print("Map:", args.map)
    print("LAST_STATS:", solution.LAST_STATS)

    if result is False:
        print("Result: no solution found within the time limit.")
    else:
        print("Steps:", result.gval)
        print("Validation:", validate_solution(initial_state, result))

    print("\nTop 20 functions by cumulative time:")
    pstats.Stats(profiler).strip_dirs().sort_stats(
        "cumtime"
    ).print_stats(20)


if __name__ == "__main__":
    main()
