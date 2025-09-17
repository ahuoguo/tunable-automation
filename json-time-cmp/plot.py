import matplotlib.pyplot as plt
import numpy as np
import json
import sys

# Create a hashmap of type <String, int> that stores the run time for each function
runtime_map1 = {}
runtime_map2 = {}


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

    # print the number of functions that takes more than .1s
    # functions_above_1s = sum(1 for time in runtime_map1.values() if time == 100)
    # print(
    #     f"Number of functions taking more than .1 second: {functions_above_1s} out of {len(runtime_map1)} functions")


def main():
    # Read in two JSON files from command line arguments
    if len(sys.argv) != 3:
        print("Usage: python plot.py <path_to_first_file.json> <path_to_second_file.json>")
        sys.exit(1)

    first_file_path = sys.argv[1]
    second_file_path = sys.argv[2]

    with open(first_file_path, 'r') as file1, open(second_file_path, 'r') as file2:
        data1 = json.load(file1)
        data2 = json.load(file2)

    # Extract runtimes from both JSON files
    extract_function_runtimes(data1, runtime_map1)
    extract_function_runtimes(data2, runtime_map2)

    ratio_info(runtime_map1, runtime_map2)
    # Calculate the ratios of runtime_map1 to runtime_map2 for all functions

    # TODO: we ignored functions with runtime 0 in the denominator
    ratios = [
        (runtime_map1[func_name] / runtime_map2[func_name]) * 100
        for func_name in runtime_map1
        if func_name in runtime_map2 and runtime_map2[func_name] != 0
    ]

    # Sort the ratios and calculate the cumulative distribution
    sorted_ratios = np.sort(ratios)
    sorted_ratios = sorted_ratios[:-1]
    cumulative = np.linspace(0, 1, len(sorted_ratios))

    # Calculate the percentage of functions taking at most 200% of verification time
    threshold = 200
    percentage_below_threshold = np.sum(
        sorted_ratios <= threshold) / len(sorted_ratios)

    # Plotting the cumulative distribution
    plt.figure(figsize=(10, 5))
    
    plt.rcParams.update({
        # "pgf.rcfonts": False,  # Do not override LaTeX settings
        "font.weight": "bold",
        "axes.labelweight": "bold",
        "axes.titleweight": "bold",
    })
    
    plt.plot(sorted_ratios, cumulative, label='IronKV All Triggers')

    # Add lines at 200% stopping at percentage_below_threshold
    plt.plot([threshold, threshold], [0, percentage_below_threshold],
             color='black', linestyle='--')
    plt.plot([0, threshold], [percentage_below_threshold,
             percentage_below_threshold], color='black', linestyle='--')

    # Add text indicating percentage_below_threshold
    plt.text(
        threshold + 5,
        percentage_below_threshold - 0.3,
        f"{percentage_below_threshold * 100:.2f}% of IronKV functions \n take at most 2x of their \n original verification time",
        color='black',
        fontsize=20,
        wrap=True
    )

    # Labels and title
    plt.xlabel('Verification Time Ratio (%)', fontsize=24)
    plt.ylabel('Percentage of Functions', fontsize=24)
    plt.ylim(0, 1.05)
    plt.xlim(0, max(sorted_ratios) * 1.1)
    plt.xticks(np.arange(0, max(sorted_ratios) * 1.1, 100),
               [f"{int(i)}%" for i in np.arange(0, max(sorted_ratios) * 1.1, 100)],
               fontsize=20)
    plt.yticks(np.arange(0, 1.1, 0.2), [
               f"{int(i * 100)}%" for i in np.arange(0, 1.1, 0.2)],
               fontsize=20)
    plt.legend(loc="lower right", fontsize=20)

    # layout
    plt.tight_layout()
    # Save the plot as a high-resolution image
    plt.savefig("plot.pgf")
    plt.savefig("a.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
