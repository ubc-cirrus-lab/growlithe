import os, re, json
import unittest
from growlithe.cli.apply import apply
from growlithe.config import get_config


def match_pattern(value, pattern):
    # Create a regex pattern that matches any number followed by the rest of the string
    return value.partition(":")[2].strip() == pattern
    # return re.match(regex_pattern, value) is not None


def add_policy(policy_file_path, policy_str):
    # Read the JSON file
    with open(policy_file_path, "r") as file:
        data = json.load(file)

    # Find the specific entry and update it
    for entry in data:
        if match_pattern(entry["source"], "tempfs:$tempFile") and match_pattern(
            entry["sink"], "sample-test-bucket:$output_key"
        ):
            # Update the read policy
            entry["write"] = policy_str
            print(f"Updated policy in : {entry}")
            break
    else:
        print("Edge not found.")

    # Write the updated data back to the JSON file
    with open(policy_file_path, "w") as file:
        json.dump(data, file, indent=4)


class TestPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the sample_app directory
        self.sample_app_dir = os.path.join(current_dir, "sample_app")

        # Construct the path to growlithe_config.yaml
        self.custom_config_path = os.path.join(
            self.sample_app_dir, "growlithe_config.yaml"
        )

        self.config = get_config(os.path.abspath(self.custom_config_path))
        self.policy_file_path = os.path.join(
            self.sample_app_dir, "growlithe_SampleApp", "policy_spec.json"
        )

    def tearDown(self):
        pass

    def test_policy(self):
        policy = "eq(ResourceRegion, 'us-west-1')"
        add_policy(self.policy_file_path, policy)
        apply(self.config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
