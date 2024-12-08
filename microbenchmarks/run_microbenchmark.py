import boto3
import pandas as pd
import numpy as np
from scipy import stats
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from transform import transform_df


class LambdaRunner:
    """A class to manage the execution of AWS Lambda functions and collect performance data."""

    def __init__(self, aws_profile="default", region="ca-west-1"):
        """Initialize AWS session and Lambda client."""
        self.session = boto3.Session(profile_name=aws_profile, region_name=region)
        self.lambda_client = self.session.client("lambda")

    def invoke_function(self, function_name, microbenchmark, num_funcs):
        """Invoke a Lambda function with specified parameters."""
        payload = json.dumps(
            {"microbenchmark": microbenchmark, "start": num_funcs, "end": 2 * num_funcs}
        )
        response = self.lambda_client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=payload,
        )
        return json.loads(response["Payload"].read().decode("utf-8"))

    def run_function_iterations(
        self, function_name, microbenchmark, num_funcs, num_iterations, time_gap
    ):
        """Run a Lambda function multiple times and collect execution times."""
        results = []
        with tqdm(
            total=num_iterations,
            desc=f"{microbenchmark:<15} {num_funcs:>3}",
            leave=True,
        ) as pbar:
            for iter in range(num_iterations):
                try:
                    response = self.invoke_function(
                        function_name, microbenchmark, num_funcs
                    )
                    time_taken = response.get("time_taken", None)
                    if time_taken is not None:
                        results.append(time_taken)
                    else:
                        print(f"Error invoking {function_name}: {response}")
                    time_gap = time_gap + num_funcs / 50.0
                    if iter < 3:
                        time.sleep(time_gap * 2)
                    else:
                        time.sleep(time_gap)
                    pbar.update(1)
                except Exception as e:
                    print(f"Error invoking {function_name}: {str(e)}")
        return results

    def run_functions(
        self,
        function_name,
        microbenchmarks,
        num_funcs_list,
        num_iterations,
        microbenchmark_type,
        time_gap,
    ):
        """Run multiple Lambda functions concurrently and collect results."""
        all_results = []
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    self.run_function_iterations,
                    function_name,
                    mb,
                    num_funcs,
                    num_iterations,
                    time_gap,
                ): (mb, num_funcs)
                for mb in microbenchmarks
                for num_funcs in num_funcs_list
            }
            for future in as_completed(futures):
                mb, num_funcs = futures[future]
                results = future.result()
                if "chain" in microbenchmark_type:
                    all_results.extend(
                        [
                            {
                                "microbenchmark": mb,
                                "width": 1,
                                "depth": num_funcs,
                                "time_taken": r,
                            }
                            for r in results
                        ]
                    )
                else:
                    all_results.extend(
                        [
                            {
                                "microbenchmark": mb,
                                "width": num_funcs,
                                "depth": 1,
                                "time_taken": r,
                            }
                            for r in results
                        ]
                    )
        return pd.DataFrame(all_results)


# Configuration
# function_name = "linear_chain_microbenchmark"
function_name = "fanout_microbenchmark"

col = "depth" if "chain" in function_name else "width"
microbenchmarks = ["baseline", "local_check", "remote_check", "taint_check"]
num_funcs_list = [1, 2, 4, 8, 16, 32, 64, 128]
region = "ca-west-1"
num_iterations = 50
time_gap = 1.2


def main():
    """Main function to run the benchmarking process."""
    runner = LambdaRunner(region=region)
    results = runner.run_functions(
        function_name,
        microbenchmarks,
        num_funcs_list,
        num_iterations,
        function_name,
        time_gap,
    )
    results.to_csv(f"raw_results_{function_name}.csv", index=False)


if __name__ == "__main__":
    main()
