import matplotlib.pyplot as plt
import numpy as np
import json
import sys
import os
from collections import defaultdict

# For the 20 samples of broadcast failure, maybe extract the max and the medium. For this plot, if might be helpful for each project (and use the same CDF graph)


def extract_function_runtimes(data, runtime_map):
    smt_run_module_times = data.get(
        "times-ms", {}).get("smt", {}).get("smt-run-module-times", [])
    for entry in smt_run_module_times:
        module_name = entry.get("module", "")
        function_breakdown = entry.get("function-breakdown", {})
        for func_entry in function_breakdown:
            func_name = func_entry.get("function", "")
            runtime = func_entry.get("time-micros", 0)
            full_func_name = f"{module_name}::{func_name}"
            if full_func_name in runtime_map:
                runtime_map[full_func_name] += int(runtime)
            else:
                runtime_map[full_func_name] = int(runtime)


def ratio_info(runtime_map1, runtime_map2):
    # Create one runtime map, make the value a tuple containing the ratio of runtime_map1 to runtime_map2
    # and the original values from both maps
    runtime_map_ratio = {}
    for func_name in runtime_map1:
        if func_name in runtime_map2 and runtime_map2[func_name] != 0:
            ratio = runtime_map1[func_name] / runtime_map2[func_name]
            runtime_map_ratio[func_name] = (
                ratio, runtime_map1[func_name], runtime_map2[func_name])
        else:
            runtime_map_ratio[func_name] = (
                None, runtime_map1[func_name], runtime_map2.get(func_name, 0))

    # Find and print the highest ratio along with the corresponding time values
    highest_ratio_entry = max(
        ((func_name, v)
         for func_name, v in runtime_map_ratio.items() if v[0] is not None),
        key=lambda x: x[1][0],
        default=None
    )

    if highest_ratio_entry:
        func_name, (highest_ratio, time1, time2) = highest_ratio_entry
        print(
            f"Highest ratio of runtime_map1 to runtime_map2: {highest_ratio}")
        print(f"Function: {func_name}")
        print(f"Time in runtime_map1: {time1}")
        print(f"Time in runtime_map2: {time2}")
    else:
        print("No valid ratio found.")

    # also take the highest runtime from map 1 and its ratio
    highest_runtime_entry = max(
        ((func_name, v) for func_name, v in runtime_map1.items()),
        key=lambda x: x[1],
        default=None
    )
    if highest_runtime_entry:
        func_name, highest_runtime = highest_runtime_entry
        ratio = highest_runtime / runtime_map2.get(func_name, 1)
        print(f"Highest runtime in runtime_map1: {highest_runtime}")
        print(f"Function: {func_name}")
        print(f"Ratio: {ratio}")


if __name__ == "__main__":
    # read in the path for json files, it should be a directory

    path = sys.argv[1]
    output_name = sys.argv[2]
    files = os.listdir(path)
    # filter the files to only include json files, which should have pattern
    # "runtime_<number>.json"
    files = [f for f in files if f.startswith(
        "runtime_") and f.endswith(".json")]

    # get the original runtime file
    orig_runtime_map = {}
    orig_runtime_file = os.path.join(path, "orig_runtime.json")
    if not os.path.exists(orig_runtime_file):
        print(f"Error: {orig_runtime_file} does not exist.")
        sys.exit(1)
    with open(orig_runtime_file, 'r') as f:
        orig_runtime_data = json.load(f)

    extract_function_runtimes(orig_runtime_data, orig_runtime_map)

    # create a list of runtime maps
    runtime_maps = []
    for file in files:
        with open(os.path.join(path, file), 'r') as f:
            data = json.load(f)
            runtime_map = {}
            extract_function_runtimes(data, runtime_map)
            runtime_maps.append(runtime_map)

    # for each function in the runtime maps, take the max runtime
    max_runtimes = defaultdict(int)
    for runtime_map in runtime_maps:
        for func_name, runtime in runtime_map.items():
            max_runtimes[func_name] = max(max_runtimes[func_name], runtime)

    # ratio_info(max_runtimes, orig_runtime_map)

    # for each function in the runtime maps, take the median runtime
    median_runtimes = {}
    for func_name in max_runtimes.keys():
        runtimes = [runtime_map.get(func_name, 0)
                    for runtime_map in runtime_maps]
        median_runtimes[func_name] = np.median(runtimes)

    max_ratio_map = [
        (max_runtimes[func_name] / orig_runtime_map[func_name]) * 100
        for func_name in max_runtimes
        if func_name in orig_runtime_map and orig_runtime_map[func_name] != 0
    ]

    median_ratio_map = [
        (median_runtimes[func_name] / orig_runtime_map[func_name]) * 100
        for func_name in median_runtimes
        if func_name in orig_runtime_map and orig_runtime_map[func_name] != 0
    ]

    # Sort the max ratios and calculate the cumulative distribution
    sorted_max_ratios = np.sort(max_ratio_map)
    cumulative_max = np.linspace(0, 1, len(sorted_max_ratios))

    # Sort the median ratios and calculate the cumulative distribution
    sorted_median_ratios = np.sort(median_ratio_map)
    cumulative_median = np.linspace(0, 1, len(sorted_median_ratios))

    # Plotting the cumulative distribution for max and median ratios
    plt.figure(figsize=(10, 5))

    plt.rcParams.update({
        # "pgf.rcfonts": False,  # Do not override LaTeX settings
        "font.weight": "bold",
        "axes.labelweight": "bold",
        "axes.titleweight": "bold",
    })

    plt.plot(sorted_max_ratios, cumulative_max,
             label='Max Verification Time Ratios')
    plt.plot(sorted_median_ratios, cumulative_median,
             label='Median Verification Time Ratios')

    # Labels and title
    plt.xlabel('Verification Time Ratio (\%)', fontsize=24)
    plt.ylabel('Percentage of Functions', fontsize=24)
    plt.ylim(0, 1.05)
    plt.xlim(0, max(max(sorted_max_ratios), max(sorted_median_ratios)) * 1.1)
    plt.xticks(
        np.arange(0, max(max(sorted_max_ratios), max(
            sorted_median_ratios)) * 1.1, 100),
        [f"{int(i)}%" for i in np.arange(
            0, max(max(sorted_max_ratios), max(sorted_median_ratios)) * 1.1, 100)],
        fontsize=24
    )
    plt.yticks(
        np.arange(0, 1.1, 0.2),
        [f"{int(i * 100)}%" for i in np.arange(0, 1.1, 0.2)],
        fontsize=24
    )
    plt.legend(fontsize=20, loc="lower right")

    # Layout
    plt.tight_layout()
    # Save the plot as a high-resolution image
    plt.savefig(f"{output_name}.pgf")
    plt.savefig(f"{output_name}.png", dpi=300)
    # plt.show()
