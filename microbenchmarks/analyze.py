import boto3
import pandas as pd
import numpy as np
from scipy import stats
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from transform import transform_df


class DataAnalyzer:
    """A class to analyze and process performance data for Lambda functions."""

    @staticmethod
    def remove_top_percentile(data, col, percentile=10):
        """Remove the top percentile of data points based on execution time."""

        def remove_percentile(group):
            threshold = np.percentile(group["time_taken"], 100 - percentile)
            return group[group["time_taken"] <= threshold]

        return (
            data.groupby(["microbenchmark", col])
            .apply(remove_percentile)
            .reset_index(drop=True)
        )

    @staticmethod
    def remove_outliers_iqr(data):
        """Remove outliers using the Interquartile Range (IQR) method."""

        def remove_iqr_outliers(group):
            Q1 = group["time_taken"].quantile(0.25)
            Q3 = group["time_taken"].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = 0
            upper_bound = Q3 + 1.5 * IQR
            return group[
                (group["time_taken"] >= lower_bound)
                & (group["time_taken"] <= upper_bound)
            ]

        return (
            data.groupby(["microbenchmark", "width", "depth"])
            .apply(remove_iqr_outliers)
            .reset_index(drop=True)
        )

    @staticmethod
    def remove_outliers_mad(data, threshold=3.5):
        """Remove outliers using the Median Absolute Deviation (MAD) method."""

        def remove_mad_outliers(group):
            median = group["time_taken"].median()
            mad = np.median(np.abs(group["time_taken"] - median))
            modified_z_scores = 0.6745 * (group["time_taken"] - median) / mad
            return group[np.abs(modified_z_scores) < threshold]

        return (
            data.groupby(["microbenchmark", "width", "depth"])
            .apply(remove_mad_outliers)
            .reset_index(drop=True)
        )

    @staticmethod
    def calculate_statistics(data):
        """Calculate basic statistics for each group in the data."""
        return (
            data.groupby(["microbenchmark", "width", "depth"])["time_taken"]
            .agg(["mean", "median", "std", "count"])
            .reset_index()
        )

    @staticmethod
    def perform_t_tests(data, col):
        """Perform t-tests comparing baseline to other microbenchmarks."""
        t_test_results = []
        baseline_data = data[data["microbenchmark"] == "baseline"]
        other_microbenchmarks = [
            mb for mb in data["microbenchmark"].unique() if mb != "baseline"
        ]

        for size in data[col].unique():
            baseline_times = baseline_data[baseline_data[col] == size]["time_taken"]

            for mb in other_microbenchmarks:
                mb_data = data[data["microbenchmark"] == mb]
                mb_times = mb_data[mb_data[col] == size]["time_taken"]

                if len(baseline_times) > 1 and len(mb_times) > 1:
                    t_statistic, p_value = stats.ttest_ind(
                        baseline_times, mb_times, equal_var=False
                    )
                    t_test_results.append(
                        {
                            "size": size,
                            "comparison": f"baseline vs {mb}",
                            "t_statistic": t_statistic,
                            "p_value": p_value,
                            "<0.05": p_value < 0.05,
                        }
                    )
                else:
                    print(
                        f"Not enough data for t-test between baseline and {mb} for size {size}"
                    )

        return pd.DataFrame(t_test_results)


# Configuration
function_name = "fanout_microbenchmark"
col = "depth" if "chain" in function_name else "width"
ram = "1769-65"


def main():
    """Main function to run the analysis process."""
    results = pd.read_csv(f"{ram}/raw_results_{function_name}.csv")
    analyzer = DataAnalyzer()

    # Remove outliers
    cleaned_results = analyzer.remove_outliers_iqr(results)
    cleaned_results.to_csv(f"{ram}/cleaned_results_{function_name}.csv", index=False)

    # Ask user to manually verify
    input("Please verify the cleaned results and press Enter to continue...")
    cleaned_results = pd.read_csv(f"{ram}/cleaned_results_{function_name}.csv")

    # Calculate statistics and perform t-tests
    stats_results = analyzer.calculate_statistics(cleaned_results)
    t_test_results = analyzer.perform_t_tests(cleaned_results, col)

    # Save results
    stats_results.to_csv(f"{ram}/function_statistics_{function_name}.csv", index=False)
    t_test_results.to_csv(f"{ram}/t_test_results_{function_name}.csv", index=False)

    # Transform and save additional statistics
    transformed_df = transform_df(f"{ram}/function_statistics_{function_name}.csv")
    transformed_df.to_csv(
        f"{ram}/transformed_function_statistics_{function_name}.csv", index=False
    )

    print(f"All results saved for {function_name}")


if __name__ == "__main__":
    main()
