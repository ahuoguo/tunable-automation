import matplotlib.pyplot as plt
import numpy as np
import json
import sys

# Create a hashmap of type <String, int> that stores the run time for each function
runtime_map1 = {}
runtime_map2 = {}

runtime_map3 = {}
runtime_map4 = {}

runtime_map5 = {}
runtime_map6 = {}

runtime_map7 = {}
runtime_map8 = {}


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


def main():

    if len(sys.argv) != 9:
        print("Usage: python plot.py <path_to_file1.json> <path_to_file2.json> <path_to_file3.json> <path_to_file4.json> <path_to_file5.json> <path_to_file6.json> <path_to_file7.json> <path_to_file8.json>")
        sys.exit(1)

    file_paths = sys.argv[1:9]
    with open(file_paths[0], 'r') as file1, open(file_paths[1], 'r') as file2, \
            open(file_paths[2], 'r') as file3, open(file_paths[3], 'r') as file4, \
            open(file_paths[4], 'r') as file5, open(file_paths[5], 'r') as file6, \
            open(file_paths[6], 'r') as file7, open(file_paths[7], 'r') as file8:
        data1 = json.load(file1)
        data2 = json.load(file2)
        data3 = json.load(file3)
        data4 = json.load(file4)
        data5 = json.load(file5)
        data6 = json.load(file6)
        data7 = json.load(file7)
        data8 = json.load(file8)

    # Extract runtimes from both JSON files
    extract_function_runtimes(data1, runtime_map1)
    extract_function_runtimes(data2, runtime_map2)
    extract_function_runtimes(data3, runtime_map3)
    extract_function_runtimes(data4, runtime_map4)
    extract_function_runtimes(data5, runtime_map5)
    extract_function_runtimes(data6, runtime_map6)
    extract_function_runtimes(data7, runtime_map7)
    extract_function_runtimes(data8, runtime_map8)

    # Calculate the ratios of runtime_map1 to runtime_map2 for all functions
    ironkv_ratios = [
        (runtime_map1[func_name] / runtime_map2[func_name]) * 100
        for func_name in runtime_map1
        if func_name in runtime_map2 and runtime_map2[func_name] != 0
    ]

    splinter_ratios = [
        (runtime_map3[func_name] / runtime_map4[func_name]) * 100
        for func_name in runtime_map3
        if func_name in runtime_map4 and runtime_map4[func_name] != 0
    ]

    anvil_ratios = [
        (runtime_map5[func_name] / runtime_map6[func_name]) * 100
        for func_name in runtime_map5
        if func_name in runtime_map6 and runtime_map6[func_name] != 0
    ]

    capybara_ratios = [
        (runtime_map7[func_name] / runtime_map8[func_name]) * 100
        for func_name in runtime_map7
        if func_name in runtime_map8 and runtime_map8[func_name] != 0
    ]

    # Sort the ratios and calculate the cumulative distribution for each
    sorted_ironkv_ratios = np.sort(ironkv_ratios)
    cumulative_ironkv = np.linspace(0, 1, len(sorted_ironkv_ratios))

    sorted_splinter_ratios = np.sort(splinter_ratios)
    # REVIEW: We reomved the largest splinter ratio
    sorted_splinter_ratios = sorted_splinter_ratios[:-1]
    cumulative_splinter = np.linspace(0, 1, len(sorted_splinter_ratios))

    sorted_anvil_ratios = np.sort(anvil_ratios)
    # REVIEW: We reomved the largest anvil ratio
    sorted_anvil_ratios = sorted_anvil_ratios[:-1]
    cumulative_anvil = np.linspace(0, 1, len(sorted_anvil_ratios))

    sorted_capybara_ratios = np.sort(capybara_ratios)
    cumulative_capybara = np.linspace(0, 1, len(sorted_capybara_ratios))

    max_ratio = max(max(sorted_ironkv_ratios), max(sorted_splinter_ratios),
                    max(sorted_anvil_ratios), max(sorted_capybara_ratios))

    # Plotting the cumulative distributions
    plt.figure(figsize=(10, 3.6))
    plt.rcParams.update({
        # "pgf.rcfonts": False,  # Do not override LaTeX settings
        "font.weight": "bold",
        "axes.labelweight": "bold",
        "axes.titleweight": "bold",
    })

    plt.plot(sorted_ironkv_ratios, cumulative_ironkv,
             label='IronKV')
    plt.plot(sorted_splinter_ratios, cumulative_splinter,
             label='Splinter')
    plt.plot(sorted_anvil_ratios, cumulative_anvil,
             label='Anvil')
    plt.plot(sorted_capybara_ratios, cumulative_capybara,
             label='Capybara')

    # Add lines at 200% for ironkv_ratios
    threshold = 200
    percentage_below_threshold = np.sum(
        sorted_capybara_ratios <= threshold) / len(sorted_capybara_ratios)
    plt.plot([threshold, threshold], [
        0, percentage_below_threshold], color='black', linestyle='--')
    plt.plot([0, threshold], [percentage_below_threshold,
                              percentage_below_threshold], color='black', linestyle='--')

    # Add text indicating percentage_below_threshold for ironkv_ratios
    plt.text(
        threshold + 5,
        percentage_below_threshold - 0.17,
        f"{percentage_below_threshold * 100:.2f}% of IronKV functions take at most \n 2x of their original verification time",
        color='black',
        fontsize=16,
        wrap=True
    )

    # Labels and title
    plt.xlabel('Verification Time Ratio', fontsize=16)
    plt.ylabel('\% of functions', fontsize=16)
    plt.ylim(0, 1.05)
    plt.xlim(0, max_ratio * 1.1)
    plt.xticks(np.arange(0, max_ratio * 1.1, 100),
               [f"{int(i)}%" for i in np.arange(0, max_ratio * 1.1, 100)],
               fontsize=16)
    plt.yticks(np.arange(0, 1.1, 0.2), [
        f"{int(i * 100)}%" for i in np.arange(0, 1.1, 0.2)], fontsize=16)

    plt.legend(fontsize=16)

    # Layout
    plt.tight_layout()
    # Save the plot as a high-resolution image

    plt.rcParams.update({
        "pgf.texsystem": "pdflatex",  # or "lualatex"/"xelatex"
        "text.usetex": True,
        "font.family": "serif",
        "pgf.rcfonts": False,
    })

    plt.savefig("plot_all.pgf")
    plt.savefig("plot_all.png", dpi=300)
    # plt.show()


if __name__ == "__main__":
    main()
