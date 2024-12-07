import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Set global font parameters
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["font.size"] = 14


def read_csv(file_path):
    return pd.read_csv(file_path)


def prepare_data(df, function_name):
    x_axis = "depth" if "linear_chain" in function_name else "width"
    return {
        "x_values": df[x_axis],
        "baseline": (df["baseline_mean"] / 1000, df["baseline_std"] / 1000),
        "local_check": (df["local_check_mean"] / 1000, df["local_check_std"] / 1000),
        "remote_check": (df["remote_check_mean"] / 1000, df["remote_check_std"] / 1000),
        "taint_check": (df["taint_check_mean"] / 1000, df["taint_check_std"] / 1000),
    }


def create_plot(data, function_name, ram, output_dir):
    fig, ax = plt.subplots(figsize=(4.5, 2.1))  # Half width for each plot
    width = 0.2  # Reduced bar width to prevent intersection

    # Use colorblind-friendly palette
    sns_colors = sns.color_palette("colorblind", 4)
    colors = {
        "baseline": (sns_colors[0], ""),
        "local_check": (sns_colors[1], "//"),
        "remote_check": (sns_colors[2], ".."),
        "taint_check": (sns_colors[3], "\\\\"),
    }

    r1 = np.arange(len(data["x_values"]))
    for i, (key, (color, hatch)) in enumerate(colors.items()):
        r = [x + i * width for x in r1]
        ax.bar(
            r,
            data[key][0],
            width=width,
            color=color,
            hatch=hatch,
            label=key.replace("_", " ").title(),  # Always create a label
            alpha=1.0,
            edgecolor="black",
            linewidth=0,
        )
        # Add error bars separately
        ax.errorbar(
            r,
            data[key][0],
            yerr=data[key][1],
            fmt="none",
            ecolor="black",
            elinewidth=0.8,
            capsize=2,
        )

    x_label = (
        "Number of functions in linear chain (LC)"
        if "linear_chain" in function_name
        else "Number of functions in fanout (FO)"
    )
    ax.set_xlabel(x_label, fontsize=10, labelpad=1)
    ax.set_ylabel("Time (s)", fontsize=10, labelpad=1)
    ax.set_xticks([r + 1.5 * width for r in range(len(data["x_values"]))])
    ax.set_xticklabels(data["x_values"], fontsize=10)
    ax.tick_params(axis="y", labelsize=10)

    if "linear_chain" in function_name:
        # Set y-axis to logarithmic scale
        ax.set_yscale("log")

        # Set y-axis ticks and labels
        y_ticks = [0.1, 0.5, 2, 10, 50]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([f"{y:.1f}" if y < 1 else f"{int(y)}" for y in y_ticks])

        # Add y-axis grid lines
        ax.grid(axis="y", linestyle="--", alpha=0.3)
    else:
        # Always add the legend
        ax.legend(
            fontsize=10, loc="upper left", frameon=False, ncol=2, columnspacing=0.5
        )
        plt.yticks(np.arange(0, 0.41, 0.1))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.1f}"))

        # Add y-axis grid lines
        ax.grid(axis="y", linestyle="--", alpha=0.3)

    plt.tight_layout()

    # Create RAM-specific directory
    ram_output_dir = os.path.join(output_dir, f"{ram}")
    os.makedirs(ram_output_dir, exist_ok=True)

    output_file = os.path.join(ram_output_dir, f"{function_name}_plot.pdf")
    with PdfPages(output_file) as pdf:
        pdf.savefig(fig, bbox_inches="tight")

    output_file = os.path.join(ram_output_dir, f"{function_name}_plot.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")

    plt.close()


def process_files(base_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ram_sizes = ["1769-65"]
    function_names = ["linear_chain_microbenchmark", "fanout_microbenchmark"]

    for ram in ram_sizes:
        ram_dir = os.path.join(base_dir, ram)
        for function_name in function_names:
            try:
                data = prepare_data(
                    read_csv(
                        os.path.join(
                            ram_dir,
                            f"transformed_function_statistics_{function_name}.csv",
                        )
                    ),
                    function_name,
                )
                create_plot(data, function_name, ram, output_dir)
                print(f"Processed plot for {function_name} with {ram} MB RAM")
            except Exception:
                print(f"Exception {function_name} for {ram}")


if __name__ == "__main__":
    base_dir = "."  # Current directory
    output_dir = "."  # Current directory
    process_files(base_dir, output_dir)
