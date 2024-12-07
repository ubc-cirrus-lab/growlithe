import os
import subprocess
import re
import csv
from statistics import mean, stdev
import sys
from Microbenchmarks.generate_app import generate_app_n_copies
import json

# Get the path to the current Python interpreter
python_executable = sys.executable


def generate_app(n):
    generate_app_n_copies(n)


def run_command(command):
    # Set up the environment to use the current Python
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        os.path.dirname(python_executable) + os.pathsep + env.get("PYTHONPATH", "")
    )

    # Run the command
    subprocess.run(command, shell=True, check=True, env=env)


def parse_log_file(file_path):
    times = {
        "analyze": [],
        "run_codeql_queries": [],
        "create_codeql_database": [],
        "parse_sam_template": [],
        "generate_adg": [],
    }

    with open(file_path, "r") as f:
        for line in f:
            match = re.search(r"\[INFO\] (\w+) took (\d+\.\d+) seconds", line)
            if match:
                func_name, time = match.groups()
                time = float(time)
                times[func_name].append(time)

    return times


def aggregate_stats(times):
    if not times:
        return 0, 0, 0
    return mean(times), min(times), max(times)


def run_performance_test(n, iterations=10, policy_type=None):
    if os.path.exists("growlithe/growlithe_profiler.log"):
        os.remove("growlithe/growlithe_profiler.log")

    generate_app(n)

    for _ in range(iterations):
        print("Iteration", _ + 1)
        run_command("growlithe analyze")
        update_policies("growlithe/policy_spec.json", policy_type)
        run_command("growlithe apply")

    times = parse_log_file("growlithe/growlithe_profiler.log")

    return times


def update_policies(policy_json_path, policy_type):
    if policy_type is None:
        return

    # Read the JSON file
    with open(policy_json_path, "r") as file:
        data = json.load(file)

        # Iterate through the array and update matching objects
        for item in data:
            if isinstance(item, dict) and "sink" in item:
                if item["sink"].endswith(":sensitivity-test-gr:$output_key"):
                    if policy_type == "LocalCheck" or policy_type == "RemoteCheck":
                        # Run Growlithe apply without hybrid enforcement for REMOTE_CHECK
                        item["write"] = "eq(ResourceRegion, InstRegion)"
                    elif policy_type == "TaintCheck":
                        BUCKET_NAME = "sensitivity-test-gr"
                        item["write"] = f"taintSetIncludes(PredNode, '{BUCKET_NAME}:*')"


    # Write the updated data back to the file
    with open(policy_json_path, "w") as file:
        json.dump(data, file, indent=4)
    print(f"File {policy_json_path} has been updated with {policy_type}.")


def main():
    NUM_FUNCS_CONFIG = [1, 2, 4, 8, 16, 32, 64, 128]
    NUM_ITERATIONS = 5

    csvfile = open("static_perf.csv", "w", newline="")
    writer = csv.writer(csvfile)
    writer.writerow(["n", "metric", "value"])

    for NUM_FUNCS in NUM_FUNCS_CONFIG:
        print(f"Running performance test for n={NUM_FUNCS}")
        times = run_performance_test(NUM_FUNCS, NUM_ITERATIONS, "LOCAL_CHECK")
        for k, v in times.items():
            for value in v:
                writer.writerow([NUM_FUNCS, k, value])

    csvfile.close()

    print("Performance test completed. Results written to static_perf.csv")


if __name__ == "__main__":
    main()