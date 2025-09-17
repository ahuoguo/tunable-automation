import matplotlib.pyplot as plt
import numpy as np
import json
import sys
import os
from collections import defaultdict


def extract_runtime(data):
    verification_success = data["verification-results"]["success"]
    total_runtime_ms = data["times-ms"]["total"]
    return verification_success, total_runtime_ms


if __name__ == "__main__":
    # read in the path for json files, it should be a directory

    path = sys.argv[1]
    files = os.listdir(path)
    # filter the files to only include json files, which should have pattern
    # "runtime_<number>.json"
    files = [f for f in files if f.startswith(
        "runtime_") and f.endswith(".json")]
      # Get the original total runtime
    orig_runtime_file = os.path.join(path, "orig_runtime.json")
    if not os.path.exists(orig_runtime_file):
        print(f"Error: {orig_runtime_file} does not exist.")
        sys.exit(1)
    with open(orig_runtime_file, 'r') as f:
        orig_runtime_data = json.load(f)
    _, orig_total_runtime = extract_runtime(orig_runtime_data)

    # Collect total runtimes from all files
    total_runtimes = []
    for file in files:
        with open(os.path.join(path, file), 'r') as f:
            data = json.load(f)
            _, total_runtime = extract_runtime(data)
            total_runtimes.append(total_runtime)

    # Calculate max and median total runtime ratios
    if orig_total_runtime == 0:
        print("Error: Original total runtime is zero.")
        sys.exit(1)

    print(f"Original total runtime: {orig_total_runtime} ms")
    print(f"Total runtimes from files: {total_runtimes}")
    
    max_runtime = max(total_runtimes)
    max_index = total_runtimes.index(max_runtime)
    max_file = files[max_index]
    print(f"Max total runtime ratio: {max_runtime / orig_total_runtime:.2f} (File: {max_file})")