import matplotlib.pyplot as plt
import numpy as np
import json
import sys
import os
from collections import defaultdict

# For the 20 samples of broadcast failure, maybe extract the max and the medium. For this plot, if might be helpful for each project (and use the same CDF graph)


def extract_function_runtimes(data):
    runtime_map = {}
    smt_run_module_times = data.get(
        "times-ms", {}).get("smt", {}).get("smt-run-module-times", [])
    for entry in smt_run_module_times:
        module_name = entry.get("module", "")
        function_breakdown = entry.get("function-breakdown", {})
        for func_entry in function_breakdown:
            func_name = func_entry.get("function", "")
            runtime = func_entry.get("time-micros", 0)
            success = func_entry.get("success", True)
            full_func_name = f"{module_name}::{func_name}"
            if full_func_name in runtime_map:
                runtime_map[full_func_name][0] = runtime_map[full_func_name][0] and bool(success) 
                runtime_map[full_func_name][1] += int(runtime)
            else:
                runtime_map[full_func_name] = [bool(success), int(runtime)]
    return runtime_map


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



def extract_one_experiment(project, path):
    print(project)
    files = os.listdir(path)
    # filter the files to only include json files, which should have pattern
    # "runtime_<number>.json"
    files = [(f, int(f.split("_")[1].split(".")[0])) for f in files if f.startswith(
        "runtime_") and f.endswith(".json")]
    files.sort(key=lambda x: x[1])

    # get the original runtime file
    orig_runtime_map = {}
    orig_runtime_file = os.path.join(path, "orig_runtime.json")
    if not os.path.exists(orig_runtime_file):
        print(f"Error: {orig_runtime_file} does not exist.")
        sys.exit(1)
    with open(orig_runtime_file, 'r') as f:
        orig_runtime_data = json.load(f)

    orig_runtime_map = extract_function_runtimes(orig_runtime_data)

    # create a list of runtime maps
    runtime_maps = []
    for file, num in files:
        with open(os.path.join(path, file), 'r') as f:
            data = json.load(f)
            runtime_map = {}
            runtime_map = extract_function_runtimes(data)
            runtime_maps.append(runtime_map)
    
    compound_map = {}
    for func_name, (success, runtime) in orig_runtime_map.items():
        compound_map[func_name] = defaultdict(dict)
        compound_map[func_name]['orig'] = runtime
        compound_map[func_name]['failure'] = []
        compound_map[func_name]['failed'] = []
    for i, runtime_map in enumerate(runtime_maps):
        for func_name, (success, runtime) in runtime_map.items():
            if func_name not in compound_map:
                compound_map[func_name] = {}
                compound_map[func_name]['failure'] = []
                compound_map[func_name]['failed'] = []
            compound_map[func_name]['failure'].append((i, success, runtime, runtime / compound_map[func_name]['orig']))
            if not success:
                compound_map[func_name]['failed'].append(i)

    all = [(x, compound_map[x]) for x in compound_map]
    all = [item for sublist in [[(x[0], y) for y in x[1]['failure']] for x in all] for item in sublist]
    print([x for x in all if x[1][3] > 4.0])
    # Print the runtime for the max ratio
    max_ratio_entry = max(all, key=lambda x: x[1][3])
    print(f"Max ratio entry: {max_ratio_entry}")
    print(f"Runtime for max ratio: {max_ratio_entry[1][2]}")

    failed = [(x, compound_map[x]) for x in compound_map if len(compound_map[x]['failed']) > 0]
    failed = [item for sublist in [[(x[0], y) for y in x[1]['failure'] if not y[1]] for x in failed] for item in sublist]
    print([x for x in failed if x[1][3] > 4.0])
    failed_percent = [x[1][3] * 100 for x in failed]
    median = np.median(failed_percent)
    sorted_failed_percent = np.sort(failed_percent)
    return sorted_failed_percent, median

if __name__ == "__main__":

    path = sys.argv[1]
    mode = sys.argv[2]
    if mode not in ["broadcast", "all_triggers"]:
        print(f"Error: Invalid mode '{mode}'.")
        sys.exit(1)
    if mode == "broadcast":
        projects = [("anvil", "Anvil"), ("splinter", "Splinter"), ("capybara", "CapybaraKV"), ("ironkv", "IronKV")]
    else:
        projects = [("ironkv_at", "IronKV")]
    output_name = sys.argv[3]

    data = [(project, extract_one_experiment(project, os.path.join(path, rel_path))) for rel_path, project in projects]

    plt.figure(figsize=(10, 2))

    plt.rcParams.update({
        # "pgf.rcfonts": False,  # Do not override LaTeX settings
        "font.size": 16,
        "font.weight": "bold",
        "axes.labelweight": "bold",
        "axes.titleweight": "bold",
    })
    
    # adjust data for plotting
    data_x = []
    data_y = []
    for project, (percent, median) in data:
        data_x.extend(percent)
        data_y.extend([project] * len(percent))

    plt.scatter(data_x, data_y, alpha=0.7)
    
    median_x = [median for _, (_, median) in data]
    median_y = [project for project, _ in data]
    # plt.barh(median_y, [1] * len(median_y), left=[x - 0.5 for x in median_x], height=0.8, color='red', alpha=0.3, label='Median')
    plt.scatter(median_x, median_y, color='red', marker='|', s=200, linewidth=3, label='Median')
    plt.legend(fontsize=16, loc='upper right')

    # Labels and title
    plt.xlabel('Verification Time Ratio (%)', fontsize=16)
    plt.ylim(-0.2 if mode == "all_triggers" else -0.5, len(set(data_y)) - 0.5)

    # Layout
    plt.tight_layout()
    # Save the plot as a high-resolution image
    plt.savefig(f"{output_name}.pgf")
    plt.savefig(f"{output_name}.png", dpi=300)
    # plt.show()
