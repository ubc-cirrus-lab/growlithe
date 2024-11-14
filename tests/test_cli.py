import os
import unittest
from click.testing import CliRunner
from growlithe.cli.cli import cli

DEBUG = True


def print_runner_logs(result):
    if DEBUG:
        print(f"Exit code: {result.exit_code}")
        print(f"Output: {result.output}")
        print(f"Exception: {result.exception}")


class TestCli(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.runner = CliRunner()
        self.original_dir = os.getcwd()

        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the sample_app directory
        self.sample_app_dir = os.path.join(current_dir, "sample_app")
        # Construct the path to growlithe_config.yaml
        self.custom_config_path = os.path.join(
            self.sample_app_dir, "growlithe_config.yaml"
        )

        print(f"Current working directory: {os.getcwd()}")
        print(f"Using config path: {self.custom_config_path}")
        print(f"Config file exists: {os.path.exists(self.custom_config_path)}")
        print(
            "----------------------------------------------------------------------\n"
        )
        # Change the current working directory to sample_app
        os.chdir(self.sample_app_dir)

    def tearDown(self):
        os.chdir(self.original_dir)

    def test_analyze_with_custom_config(self):
        # Run the CLI command with the custom config option
        result = self.runner.invoke(
            cli, ["--config", self.custom_config_path, "analyze"]
        )
        print_runner_logs(result)

        # Check that the command executed successfully
        self.assertEqual(result.exit_code, 0)

    def test_apply_with_custom_config(self):
        # Run the CLI command with the custom config option
        result = self.runner.invoke(cli, ["--config", self.custom_config_path, "apply"])
        print_runner_logs(result)

        # Check that the command executed successfully
        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
